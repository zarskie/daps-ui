def get_combined_media_lists(radarr_instances: dict[str, list[object]], sonarr_instances: dict[str, list[object]]) -> tuple[list, list]:
    all_movies = []
    all_series = []
    for radarr in radarr_instances.values():
        all_movies.extend(radarr.movies)
    for sonarr in sonarr_instances.values():
        all_series.extend(sonarr.series)
    return all_movies, all_series

def get_combined_collections_lists(plex_instances: dict[str, list[object]]) -> tuple[list, list]:
    all_movie_collections = []
    all_series_collections = []
    for plex in plex_instances.values():
        all_movie_collections.extend(plex.movie_collections)
        all_series_collections.extend(plex.series_collections)
    return all_movie_collections, all_series_collections