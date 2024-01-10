import logging
import os
from datetime import datetime

from dynaconf import Dynaconf

curr_time = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

settings = Dynaconf(
    settings_files=['settings.toml', '.secrets.toml'],
)

# define file logger format
logging.basicConfig(
    format=settings.LOG.FORMAT,
    datefmt=settings.LOG.DATE_FORMAT,
    level=settings.LOG.LEVEL,
    filename=os.path.join(settings.LOG.PATH, f'main-{curr_time}.txt'),
    filemode='a'
)


def get_logger():
    console = logging.StreamHandler()
    console.setLevel(settings.LOG.LEVEL)
    formatter = logging.Formatter(settings.LOG.FORMAT)
    console.setFormatter(formatter)
    # Create an instance
    logger = logging.getLogger('main')
    logger.addHandler(console)
    return logger


logger = get_logger()
