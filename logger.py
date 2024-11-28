from loguru import logger
import sys

# Настройка логирования
logger.remove()  # Удаляем стандартный обработчик
logger.add(sys.stderr, level="INFO", colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> - <level>{message}</level>")