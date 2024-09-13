from daps_ui import PosterRenamerr, Media, Radarr, Sonarr, Server, Config, utils


def main():
    script_name = "poster_renamerr"
    cache_file = r".\\cache.json"
    config = Config(script_name, config_path=r".\\config\\config.yaml")
    media = Media()
    source_directory = config.script_config.get("source_directories")
    target_directory = config.script_config.get("target_directory")
    asset_folders = config.script_config.get("asset_folders")
    renamer = PosterRenamerr(
        target_directory, source_directory, asset_folders, cache_file
    )
    radarr_instances, sonarr_instances = config.create_arr_instances(Radarr, Sonarr)
    plex_instances = config.create_plex_instances(Server)
    all_movies, all_series = utils.get_combined_media_lists(
        radarr_instances, sonarr_instances
    )
    all_movie_collections, all_series_collections = (
        utils.get_combined_collections_lists(plex_instances)
    )
    media_dict, collections_dict = media.get_dicts(
        all_movies, all_series, all_movie_collections, all_series_collections
    )
    source_files = renamer.get_source_files()
    matched_files = renamer.match_files_with_media(
        source_files, media_dict, collections_dict
    )
    # print()
    if asset_folders:
        asset_folder_names = renamer.create_asset_directories(
            collections_dict, media_dict
        )
        renamer.copy_rename_files_asset_folders(matched_files, asset_folder_names)
        renamer.remove_deleted_files_from_cache(source_files)
    else:
        renamer.copy_rename_files(matched_files, collections_dict)
        renamer.remove_deleted_files_from_cache(source_files)
