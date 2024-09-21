import os
import shutil
from pathlib import Path


class Config:
    # check if we're in a docker and configure directories based on that
    # if str(Path.cwd()) == "/code":
    flask_static = Path(Path(Path.cwd()).parent / "config")
    # temp_db_working_dir = Path(flask_static / "temp_dir")
    logs = Path(flask_static / "logs")
    database = Path(flask_static / "db")
    database.mkdir(exist_ok=True, parents=True)
    # file_uploads = Path(flask_static / "uploads")
    # shutil.copytree(
    #     Path(Path.cwd()) / "bhdstudio" / "static", flask_static, dirs_exist_ok=True
    # )
    # bhdstudio_mount = Path("/bhdstudio_mount")

    # # create needed directories
    # temp_db_working_dir.mkdir(exist_ok=True)
    # logs.mkdir(exist_ok=True)
    # file_uploads.mkdir(exist_ok=True)

    # uploads
    # BHDSTUDIO_TITLE_TXT = Path(file_uploads / "bhdstudio_releases.txt")
    # BHDSTUDIO_IMDB_IDS_TXT = Path(file_uploads / "bhdstudio_releases_imdb_ids.txt")

    # environment
    FLASK_ENV = os.environ.get("FLASK_ENV")

    # version
    VERSION = os.environ.get("VERSION")

    # # cache
    # CACHE_TYPE = "redis"
    # CACHE_REDIS_URL = os.environ.get("BROKER_URL")
    # EMAIL_CACHE_DEFAULT_TIMEOUT = os.environ.get("EMAIL_CACHE_DEFAULT_TIMEOUT")
    # ALL_RELEASE_CACHE_TIMEOUT = os.environ.get("ALL_RELEASE_CACHE_TIMEOUT")

    # # configure the databases
    # DB_USER = os.environ.get("POSTGRES_USER")
    # DB_PW = os.environ.get("POSTGRES_PASSWORD")
    # DB_HOST = os.environ.get("DB_HOST")
    # DB_PORT = os.environ.get("DB_PORT")
    # DB_NAME = os.environ.get("POSTGRES_DB")
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{Path(database / "database.db")}'

    # # mail
    # MAIL_SERVER = "smtp.gmail.com"
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get("EMAIL_USER")
    # MAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

    # # secret key
    # SECRET_KEY = os.environ.get("SECRET_KEY")

    # # celery config
    # CELERY_CONFIG = {
    #     "broker_url": os.environ.get("BROKER_URL"),
    #     "result_backend": os.environ.get("RESULT_BACKEND"),
    # }

    # # beyondhd keys
    # BHD_API_KEY = os.environ.get("BHD_API_KEY")
    # BHD_RSS_KEY = os.environ.get("BHD_RSS_KEY")
    # BHD_RSS_URL = os.environ.get("BHD_RSS_URL")

    # # beyondhd irc
    # BHD_IRC_SERVER = os.environ.get("BHD_IRC_SERVER")
    # BHD_IRC_PORT = os.environ.get("BHD_IRC_PORT")
    # BHD_IRC_NICKNAME = os.environ.get("BHD_IRC_NICKNAME")
    # BHD_IRC_CHANNEL = os.environ.get("BHD_IRC_CHANNEL")
    # BHD_IRC_TARGET = os.environ.get("BHD_IRC_TARGET")
    # BHD_IRC_COMMAND = os.environ.get("BHD_IRC_COMMAND")

    # # tmdb
    # TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
    # TMDB_BATCH_SIZE = os.environ.get("TMDB_BATCH_SIZE")

    # # discord hooks
    # DISCORD_HOOK = os.environ.get("DISCORD_HOOK")
    # DISCORD_UPLOAD_POINTS_HOOK = os.environ.get("DISCORD_UPLOAD_POINTS_HOOK")
    # DISCORD_EXCEPTIONS_HOOK = os.environ.get("DISCORD_EXCEPTIONS_HOOK")

    # # api key
    # UPDATE_API_KEY = os.environ.get("UPDATE_API_KEY")