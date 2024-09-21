import datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def init_logger(
    lgr: logging.Logger, log_dir: Path, file_name: str, log_level: int = 20
):
    """
    Levels: (lvl)
    CRITICAL 50
    ERROR 40
    WARNING 30
    INFO 20
    DEBUG 10
    NOTSET 0
    """
    # ensure all parents exist
    log_dir.mkdir(parents=True, exist_ok=True)

    # set log level
    lgr.setLevel(log_level)

    # format the logger
    formatter = logging.Formatter("%(name)s:%(asctime)s:%(levelname)s = %(message)s")

    # add date time to file name
    path_file_name = Path(file_name)
    date_time_now = datetime.datetime.now(datetime.timezone.utc).strftime('%d-%m-%y %H:%M:%S')
    file_name = f"{date_time_now}_{path_file_name.stem}{path_file_name.suffix}"

    # Configure RotatingFileHandler for the logger
    file_handler = RotatingFileHandler(log_dir / file_name, mode="a", maxBytes=10000000, backupCount=5)
    file_handler.setFormatter(formatter)
    lgr.addHandler(file_handler)

    # Configure a stream handler for console output
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    lgr.addHandler(stream_handler)

    return lgr
