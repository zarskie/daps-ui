from DapsEX import Payload
from DapsEX.poster_renamerr import Radarr, Server, Sonarr


def get_combined_media_lists(
    radarr_instances: dict[str, Radarr], sonarr_instances: dict[str, Sonarr]
) -> tuple[list, list]:
    all_movies = []
    all_series = []
    for radarr in radarr_instances.values():
        all_movies.extend(radarr.movies)
    for sonarr in sonarr_instances.values():
        all_series.extend(sonarr.series)
    return all_movies, all_series


def get_combined_collections_lists(
    plex_instances: dict[str, Server]
) -> tuple[list, list]:
    all_movie_collections = []
    all_series_collections = []
    for plex in plex_instances.values():
        all_movie_collections.extend(plex.movie_collections)
        all_series_collections.extend(plex.series_collections)
    return all_movie_collections, all_series_collections


def create_arr_instances(
    payload_class: Payload, radarr_class: type[Radarr], sonarr_class: type[Sonarr]
) -> tuple[dict[str, Radarr], dict[str, Sonarr]]:
    radarr_instances: dict[str, Radarr] = {}
    sonarr_instances: dict[str, Sonarr] = {}

    for key, value in payload_class.radarr.items():
        if key in payload_class.instances:
            radarr_name = f"{key}"
            radarr_instances[radarr_name] = radarr_class(
                base_url=value["url"], api=value["api"]
            )
    for key, value in payload_class.sonarr.items():
        if key in payload_class.instances:
            sonarr_name = f"{key}"
            sonarr_instances[sonarr_name] = sonarr_class(
                base_url=value["url"], api=value["api"]
            )
    return radarr_instances, sonarr_instances


def create_plex_instances(
    payload: Payload, plex_class: type[Server]
) -> dict[str, Server]:
    plex_instances = {}
    for key, value in payload.plex.items():
        if key in payload.instances:
            plex_name = f"{key}"
            plex_instances[plex_name] = plex_class(
                plex_url=value["url"],
                plex_token=value["api"],
                library_names=payload.library_names,
            )
    return plex_instances
