from dataclasses import dataclass
from enum import Enum


@dataclass(slots=True)
class Payload:
    source_dirs: list[str]
    target_path: str
    asset_folders: bool
    library_names: list[str]
    instances: list[str]
    radarr: dict[str, dict[str, str]]
    sonarr: dict[str, dict[str, str]]
    plex: dict[str, dict[str, str]]


class Settings(Enum):
    CONFIG_PATH = r"./dev_config/config.yaml"
    POSTER_RENAMERR = "poster_renamerr"
    DB_PATH = r"./dev_config/db/database.db"

