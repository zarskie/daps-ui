from DapsEX.payload import Payload

def get_instances(model) -> dict[str, dict[str, str]]: 
    instances = model.query.all()
    model_dict = {
        item.instance_name: {"url": item.url, "api": item.api_key} for item in instances
    }
    return model_dict

def create_poster_renamer_payload(radarr, sonarr, plex) -> Payload:
    from daps_webui.models.settings import Settings
    settings = Settings.query.first()

    return Payload(
        source_dirs=getattr(settings, 'source_dirs', '').split(",") if getattr(settings, 'source_dirs', None) else [],
        target_path=getattr(settings, 'target_path', ''),
        asset_folders=getattr(settings, 'asset_folders', False),
        library_names=getattr(settings, 'library_names', '').split(",") if getattr(settings, 'library_names', None) else [],
        instances=getattr(settings, 'instances', '').split(",") if getattr(settings, 'instances', None) else [],
        radarr=radarr,
        sonarr=sonarr,
        plex=plex,
    )
