import sys

import art
from loguru import logger

logger_format = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "{message}"
)
logger.remove()
logger.add(sys.stderr, format=logger_format)

print(art.text2art("Capybara", font="big"))
