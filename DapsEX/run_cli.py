from DapsEX import Settings, PosterRenamerr, Media, Radarr, Sonarr, Server, YamlConfig, utils


def main():
    config = YamlConfig(Settings.POSTER_RENAMERR.value)
    payload = config.create_poster_renamer_payload()
    media = Media()
    renamer = PosterRenamerr(
        payload.target_path, payload.source_dirs, payload.asset_folders, Settings.CACHE_FILE.value
    )
    radarr_instances, sonarr_instances = utils.create_arr_instances(payload, Radarr, Sonarr)
    plex_instances = utils.create_plex_instances(payload, Server)
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
    if payload.asset_folders:
        asset_folder_names = renamer.create_asset_directories(
            collections_dict, media_dict
        )
        renamer.copy_rename_files_asset_folders(matched_files, asset_folder_names)
        renamer.remove_deleted_files_from_cache(source_files)
    else:
        renamer.copy_rename_files(matched_files, collections_dict)
        renamer.remove_deleted_files_from_cache(source_files)