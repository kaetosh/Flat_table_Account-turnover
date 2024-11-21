import logging
import datetime

# Создаем путь к лог-файлу с текущей датой
log_path = f"logs/logs_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

# Создаем логгер
logger = logging.getLogger()

# Устанавливаем уровень логирования
logger.setLevel(logging.INFO)

# Создаем обработчик логов
handler = logging.FileHandler(log_path, mode='w')

# Создаем формат логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Добавляем формат логов в обработчик логов
handler.setFormatter(formatter)

# Добавляем обработчик логов в логгер
logger.addHandler(handler)

