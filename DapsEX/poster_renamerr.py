# TODO: add logging
from pathlib import Path
from arrapi.apis.sonarr import Series
from arrapi.objs.reload import Movie
from plexapi.collection import LibrarySection
from DapsEX.payload import Payload
from DapsEX.database_cache import Database
from plexapi.server import PlexServer
from arrapi import SonarrAPI, RadarrAPI
import re
from tqdm import tqdm
import shutil
from pathvalidate import sanitize_filename
import hashlib
from progress import *


# TODO: remove media class convert to functions in utils module
class Media:
    @staticmethod
    def _get_paths(all_media_objects: list[Movie] | list[Series]) -> list[Path]:
        """
        Method to get paths from media objects (movies or series).
        """
        return [Path(item.path) for item in all_media_objects]  # type: ignore

    def get_dicts(
        self,
        movies_list: list[Path],
        series_list: list[Path],
        movies_collection_list: list[str],
        series_collection_list: list[str],
    ) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
        """
        Combines all unique movies, series and collections into dictionaries.
        """
        media_dict = {"movies": [], "shows": []}
        collections_dict = {"movies": [], "shows": []}
        movie_name_list = [item.name for item in movies_list]
        series_name_list = [item.name for item in series_list]
        unique_movies = set()
        unique_shows = set()
        unique_movie_collections = set()
        unique_show_collections = set()

        for movie in movie_name_list:
            self._process_list(movie, unique_movies, media_dict, key="movies")
        for show in series_name_list:
            self._process_list(show, unique_shows, media_dict, key="shows")
        for collection in movies_collection_list:
            self._process_list(
                collection, unique_movie_collections, collections_dict, key="movies"
            )
        for collection in series_collection_list:
            self._process_list(
                collection, unique_show_collections, collections_dict, key="shows"
            )
        return media_dict, collections_dict

    @staticmethod
    def _process_list(
        item: object, unique_set: set, final_dict: dict, key: str
    ) -> None:
        if item not in unique_set:
            unique_set.add(item)
            final_dict[key].append(item)


# TODO: move Radarr, Sonarr, Server to seperate modules
class Radarr(Media):
    def __init__(self, base_url: str, api: str):
        super().__init__()
        self.radarr = RadarrAPI(base_url, api)
        self.get_all_movies()

    def get_all_movies(self) -> None:
        all_movie_objects = self.radarr.all_movies()
        self.movies = self._get_paths(all_movie_objects)


class Sonarr(Media):
    def __init__(self, base_url: str, api: str):
        super().__init__()
        self.sonarr = SonarrAPI(base_url, api)
        self.get_all_series()

    def get_all_series(self) -> None:
        all_series_objects = self.sonarr.all_series()
        self.series = self._get_paths(all_series_objects)


class Server:
    def __init__(self, plex_url: str, plex_token: str, library_names: list[str]):
        self.plex = PlexServer(plex_url, plex_token)
        self.library_names = library_names
        self.get_collections()

    def get_collections(self) -> None:
        movie_collections_list = []
        show_collections_list = []
        unique_collections = set()

        for library_name in self.library_names:
            try:
                library = self.plex.library.section(library_name)
            except Exception as e:
                print(f"Library '{library_name}' not found: {e}")
                continue

            if library.type == "movie":
                self._movie_collection(
                    library, library_name, unique_collections, movie_collections_list
                )
            if library.type == "show":
                self._show_collection(
                    library, library_name, unique_collections, show_collections_list
                )
        self.movie_collections = movie_collections_list
        self.series_collections = show_collections_list

    def _movie_collection(
        self,
        library: LibrarySection,
        library_name: str,
        unique_collections: set,
        movie_collections_list: list[str],
    ) -> None:
        collections = library.collections()
        print(f"Processing collections from {library_name}")
        for collection in collections:
            if collection.title not in unique_collections:
                unique_collections.add(collection.title)
                movie_collections_list.append(collection.title)

    def _show_collection(
        self,
        library: LibrarySection,
        library_name: str,
        unique_collections: set,
        show_collections_list: list[str],
    ) -> None:
        collections = library.collections()
        print(f"Processing collections from {library_name}")
        for collection in collections:
            if collection.title not in unique_collections:
                unique_collections.add(collection.title)
                show_collections_list.append(collection.title)


class PosterRenamerr:
    def __init__(
        self,
        target_path: str,
        source_directories: list,
        asset_folders: bool,
    ):
        self.target_path = Path(target_path)
        self.source_directories = source_directories
        self.asset_folders = asset_folders
        self.db = Database()

    image_exts = {".png", ".jpg", ".jpeg"}

    def hash_file(self, file_path: Path) -> str:
        sha256_hash = hashlib.sha256()
        with file_path.open("rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def clean_cache(self) -> None:
        asset_files = [str(item) for item in Path(self.target_path).rglob('*')]
        cached_file_data = self.db.return_all_files()
        cached_file_paths = list(cached_file_data.keys())

        for item in cached_file_paths:
            if not item in asset_files:
                self.db.delete_cached_file(item)
                print(f"Removed deleted {item} from database")

    def get_source_files(self) -> dict[str, list[Path]]:
        source_directories = [Path(item) for item in self.source_directories]
        source_files = {}
        unique_files = set()
        for source_dir in source_directories:
            print(f"Processing source files from {source_dir}")
            for poster in source_dir.glob("*"):
                if not poster.is_file():
                    continue
                if poster.suffix.lower() in self.image_exts:
                    if source_dir not in source_files:
                        source_files[source_dir] = []
                    if poster not in unique_files:
                        unique_files.add(poster.name)
                        source_files[source_dir].append(poster)
        return source_files

    def match_files_with_media(
        self,
        source_files: dict[str, list[Path]],
        media_dict: dict[str, list[str]],
        collections_dict: dict[str, list[str]],
        cb: Callable[[str, int, ProgressState], None] | None = None,
        job_id: str | None = None,
    ) -> dict[str, list[Path]]:

        matched_files = {
            "collections": [],
            "movies": [],
            "shows": [],
        }

        flattened_col_list = [
            item for sublist in collections_dict.values() for item in sublist
        ]
        append_str = " Collection"
        modified_col_list = [item + append_str for item in flattened_col_list]

        total_files = sum(len(files) for files in source_files.values())
        processed_files = 0

        for directory, files in source_files.items():
            for file in tqdm(files, desc=f"Matching files in {directory}"):
                name_without_extension = file.stem
                matched = False

                for matched_list in matched_files.values():
                    if any(
                        name_without_extension == matched_file.stem
                        for matched_file in matched_list
                    ):
                        matched = True
                        break

                if not matched:
                    for collection_name in modified_col_list:
                        if name_without_extension in collection_name:
                            matched_files["collections"].append(file)
                            matched = True
                            break

                if not matched:
                    for movie_names in media_dict["movies"]:
                        if name_without_extension in movie_names:
                            matched_files["movies"].append(file)
                            matched = True
                            break

                if not matched:
                    for show_name in media_dict["shows"]:

                        stripped_name = self._strip_id(show_name)
                        if (
                            name_without_extension == stripped_name
                            or self._match_show_season(
                                name_without_extension, stripped_name
                            )
                            or self._match_show_special(
                                name_without_extension, stripped_name
                            )
                        ):
                            matched_files["shows"].append(file)
                            matched = True
                            break
                processed_files += 1
                if job_id and cb:
                    progress = int((processed_files / total_files) * 70)
                    cb(job_id, progress + 10, ProgressState.IN_PROGRESS)
        return matched_files

    @staticmethod
    def _match_show_season(file_name: str, show_name: str) -> bool:
        season_pattern = re.compile(
            rf"{re.escape(show_name)} - Season \d+", re.IGNORECASE
        )
        if season_pattern.match(file_name):
            return True

        return False

    @staticmethod
    def _match_show_special(file_name: str, show_name: str) -> bool:
        specials_pattern = re.compile(
            rf"{re.escape(show_name)} - Specials", re.IGNORECASE
        )
        if specials_pattern.match(file_name):
            return True

        return False

    @staticmethod
    def _strip_id(name: str) -> str:
        """
        Strip tvdb/imdb/tmdb ID from movie title.
        """
        return re.sub(r"\s*\{.*\}$", "", name)

    def create_asset_directories(
        self, collections_dict: dict[str, list[str]], media_dict: dict[str, list[str]]
    ) -> dict[str, list[str]]:
        asset_folder_names = {"collections": [], "movies": [], "shows": []}
        self.target_path.mkdir(parents=True, exist_ok=True)
        for key, items in collections_dict.items():
            for name in items:
                sanitized_name = sanitize_filename(name)
                sub_dir = self.target_path / sanitized_name
                if not sub_dir.exists():
                    sub_dir.mkdir(exist_ok=True)
                    print(f"Directory created: {sub_dir}")
                asset_folder_names["collections"].append(sub_dir.name)

        for key, items in media_dict.items():
            for name in items:
                sanitized_name = sanitize_filename(name)
                sub_dir = self.target_path / sanitized_name
                if not sub_dir.exists():
                    sub_dir.mkdir(exist_ok=True)
                    print(f"Directory created: {sub_dir}")
                if key == "movies":
                    asset_folder_names["movies"].append(sanitized_name)
                if key == "shows":
                    asset_folder_names["shows"].append(sanitized_name)

        return asset_folder_names

    def copy_rename_files_asset_folders(
        self,
        matched_files: dict[str, list[Path]],
        asset_folder_names: dict[str, list[str]],
    ) -> None:
        for key, items in matched_files.items():
            if key == "movies":
                for item in items:
                    result = self._handle_movie_asset_folders(asset_folder_names, item)
                    if result:
                        target_dir, file_name_format = result
                        self._copy_file(item, target_dir, file_name_format)

            elif key == "collections":
                for item in items:
                    result = self._handle_collection_asset_folders(
                        asset_folder_names, item
                    )
                    if result:
                        target_dir, file_name_format = result
                        self._copy_file(item, target_dir, file_name_format)

            elif key == "shows":
                for item in items:
                    result = self._handle_series_asset_folders(asset_folder_names, item)
                    if result:
                        target_dir, file_name_format = result
                        self._copy_file(item, target_dir, file_name_format)

    def _handle_movie_asset_folders(
        self, asset_folder_names: dict[str, list[str]], file_path: Path
    ) -> tuple[Path, str] | None:
        for name in asset_folder_names["movies"]:
            if file_path.exists() and file_path.is_file() and file_path.stem == name:
                movie_file_name_format = f"Poster{file_path.suffix}"
                target_dir = self.target_path / name
                return target_dir, movie_file_name_format
        return None

    def _handle_collection_asset_folders(
        self, asset_folder_names: dict[str, list[str]], file_path: Path
    ) -> tuple[Path, str] | None:
        for name in asset_folder_names["collections"]:
            stripped_file_name = file_path.stem.removesuffix(" Collection")
            if (
                file_path.exists()
                and file_path.is_file()
                and stripped_file_name == name
            ):
                collection_file_name_format = f"Poster{file_path.suffix}"
                target_dir = self.target_path / name
                return target_dir, collection_file_name_format
        return None

    def _handle_series_asset_folders(
        self, asset_folder_names: dict[str, list[str]], file_path: Path
    ) -> tuple[Path, str] | None:
        match_season = re.match(r"(.+?) - Season (\d+)", file_path.stem)
        match_specials = re.match(r"(.+?) - Specials", file_path.stem)
        if match_season:
            show_name_season = match_season.group(1)
            season_num = int(match_season.group(2))
            formatted_season_num = f"Season{season_num:02}"
            for name in asset_folder_names["shows"]:
                stripped_name = self._strip_id(name)
                if (
                    file_path.exists()
                    and file_path.is_file()
                    and show_name_season == stripped_name
                ):
                    target_dir = self.target_path / name
                    show_file_name_season_format = (
                        f"{formatted_season_num}{file_path.suffix}"
                    )
                    return target_dir, show_file_name_season_format
            return None

        elif match_specials:
            show_name_specials = match_specials.group(1)
            for name in asset_folder_names["shows"]:
                stripped_name = self._strip_id(name)
                if (
                    file_path.exists()
                    and file_path.is_file()
                    and show_name_specials == stripped_name
                ):
                    target_dir = self.target_path / name
                    show_file_name_special_format = f"Season00{file_path.suffix}"
                    return target_dir, show_file_name_special_format
            return None

        else:
            for name in asset_folder_names["shows"]:
                stripped_name = self._strip_id(name)
                if (
                    file_path.exists()
                    and file_path.is_file()
                    and file_path.stem == stripped_name
                ):
                    target_dir = self.target_path / name
                    show_file_name_format = f"Poster{file_path.suffix}"
                    return target_dir, show_file_name_format
            return None

    def _copy_file(self, file_path: Path, target_dir: Path, new_file_name: str) -> None:
        try:
            target_path = target_dir / new_file_name
            file_hash = self.hash_file(file_path)
            cached_file = self.db.get_cached_file(str(target_path))
            current_source = str(file_path)

            if target_path.exists() and cached_file:
                cached_hash = cached_file["file_hash"]
                cached_source = cached_file["source_path"]

                if file_hash != cached_hash or cached_source != current_source:
                    print(
                        f"Replacing file from {cached_source}: {current_source}\nCopied and renamed: {file_path.name} -> {target_path}"
                    )
                    shutil.copy2(file_path, target_path)
                    self.db.update_file(file_hash, current_source, str(target_path))
                else:
                    print(f"Skipping unchanged file: {file_path}")
                    return

            else:
                shutil.copy2(file_path, target_path)
                print(f"Copied and renamed: {file_path.name} -> {target_path}")
                self.db.add_file(str(target_path), file_hash, current_source)

        except Exception as e:
            print(f"Error copying file {file_path}: {e}")

    def copy_rename_files(
        self,
        matched_files: dict[str, list[Path]],
        collections_dict: dict[str, list[str]],
    ) -> None:
        for key, items in matched_files.items():
            if key == "movies":
                for item in items:
                    result = self._handle_movie(item)
                    if result:
                        file_name_format = result
                        self._copy_file(item, self.target_path, file_name_format)

            if key == "collections":
                for item in items:
                    result = self._handle_collections(collections_dict, item)
                    if result:
                        file_name_format = result
                        self._copy_file(item, self.target_path, file_name_format)

            if key == "shows":
                for item in items:
                    result = self._handle_series(item)
                    if result:
                        file_name_format = result
                        self._copy_file(item, self.target_path, file_name_format)

    @staticmethod
    def _handle_movie(item: Path) -> str | None:
        if item.exists() and item.is_file():
            file_name_format = f"{item.name}"
            return file_name_format
        return None

    @staticmethod
    def _handle_collections(
        collections_dict: dict[str, list[str]], item: Path
    ) -> str | None:
        collections_list = [
            item for sublist in collections_dict.values() for item in sublist
        ]
        stripped_name = item.stem.removesuffix(" Collection")
        for collection_name in collections_list:
            if collection_name == stripped_name:
                if item.exists() and item.is_file():
                    file_name_format = f"{collection_name}{item.suffix}"
                    return file_name_format
        return None

    @staticmethod
    def _handle_series(item: Path) -> str | None:
        match_season = re.match(r"(.+?) - Season (\d+)", item.stem)
        match_specials = re.match(r"(.+?) - Specials", item.stem)

        if match_season:
            show_name_season = match_season.group(1)
            season_num = int(match_season.group(2))
            formatted_season_num = f"Season{season_num:02}"
            if item.exists() and item.is_file():
                file_name_format = (
                    f"{show_name_season}_{formatted_season_num}{item.suffix}"
                )
                return file_name_format
            return None
        elif match_specials:
            show_name_specials = match_specials.group(1)
            if item.exists() and item.is_file():
                file_name_format = f"{show_name_specials}_Season00{item.suffix}"
                return file_name_format
            return None
        else:
            if item.exists() and item.is_file():
                file_name_format = f"{item.name}"
                return file_name_format
        return None

    def run(
        self,
        payload: Payload,
        cb: Callable[[str, int, ProgressState], None] | None = None,
        job_id: str | None = None,
    ) -> None:

        from DapsEX import utils

        try:
            media = Media()
            radarr_instances, sonarr_instances = utils.create_arr_instances(
                payload, Radarr, Sonarr
            )
            plex_instances = utils.create_plex_instances(payload, Server)
            all_movies, all_series = utils.get_combined_media_lists(
                radarr_instances, sonarr_instances
            )
            all_movie_collections, all_series_collections = (
                utils.get_combined_collections_lists(plex_instances)
            )
            media_dict, collections_dict = media.get_dicts(
                all_movies,
                all_series,
                all_movie_collections,
                all_series_collections,
            )
            if job_id and cb:
                cb(job_id, 10, ProgressState.IN_PROGRESS)
            source_files = self.get_source_files()
            matched_files = self.match_files_with_media(
                source_files, media_dict, collections_dict, cb, job_id
            )
            if self.asset_folders:
                asset_folder_names = self.create_asset_directories(
                    collections_dict, media_dict
                )
                self.copy_rename_files_asset_folders(matched_files, asset_folder_names)
            else:
                self.copy_rename_files(matched_files, collections_dict)

            if job_id and cb:
                cb(job_id, 100, ProgressState.COMPLETED)

            self.clean_cache()
        except Exception as e:
            print(f"Something went wrong: {e}", flush=True)

