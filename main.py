from DapsEX import PosterRenamerr, YamlConfig, Settings


if __name__ == "__main__":
    config = YamlConfig(Settings.POSTER_RENAMERR.value)
    payload = config.create_poster_renamer_payload()
    print(f"{payload}")
    renamerr = PosterRenamerr(payload.target_path, payload.source_dirs, payload.asset_folders)
    renamerr.run(payload)