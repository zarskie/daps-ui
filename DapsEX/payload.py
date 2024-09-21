from dataclasses import dataclass
from enum import Enum

@dataclass(slots=True)
class Payload():
    source_dirs: list[str]
    target_path: str
    asset_folders: bool
    library_names: list[str]
    instances: list[str]
    radarr: dict[str, list[str]]
    sonarr: dict[str, list[str]]
    plex: dict[list[str]]

class Settings(Enum):
    CONFIG_PATH = r"./config/config_dev.yaml"
    POSTER_RENAMERR = "poster_renamerr"
    CACHE_FILE = "cache.json"