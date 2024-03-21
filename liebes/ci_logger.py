import logging
import os
from datetime import datetime

from config import settings

curr_time = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
file_name = os.path.join(settings.LOG.PATH, f'main-{curr_time}.txt')
# define file logger format
logging.basicConfig(
    format=settings.LOG.FORMAT,
    datefmt=settings.LOG.DATE_FORMAT,
    level=settings.LOG.LEVEL,
    filename=file_name,
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
    logger.info(f"start to record log in {file_name}")
    return logger


logger = get_logger()
