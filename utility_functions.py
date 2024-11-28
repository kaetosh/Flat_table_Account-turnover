# A function for determining whether a value is an accounting
import os
import shutil
import sys
import functools

import config
from logger import logger

def is_accounting_code(value):
    if value:
        # Проверка на значение "000"
        if str(value) == "000":
            return True
        try:
            parts = str(value).split('.')
            has_digit = any(part.isdigit() for part in parts)
            # Проверка, состоит ли каждая часть только из цифр (длиной 1 или 2) или (если длина меньше 3) только из букв
            return has_digit and all(
                (part.isdigit() and len(part) <= 2) or (len(part) < 3 and part.isalpha()) for part in parts)
        except TypeError:
            return False
    else:
        return False

# в случае ошибки - удаление временных папок и файлов
def terminate_script(error_message: str):
    """
    Terminates the script with an error message and deletes temporary folders.
    """
    logger.error(error_message)
    delete_folders()
    logger.info("Скрипт завершен безуспешно. Можно закрыть программу. ")
    input()
    sys.exit()

# удаление временных папок
def delete_folders():
    """
    Deletes temporary folders.
    """
    for dir_ in [config.folder_path_preprocessing, config.folder_path_converted]:
        if os.path.exists(dir_):
            try:
                shutil.rmtree(dir_)
                logger.info(f"Папка и ее содержимое {os.path.basename(dir_)} были успешно удалены.")
            except OSError as e:
                pass
                logger.warning(f"Error: {e.filename} - {e.strerror}")
        else:
            pass
            logger.warning(f"Папка {os.path.basename(dir_)} не существует.")

# декоратор к функциям обработки файлов Excel (на каждом этапе A, B, C, ...)
# отлавливающий ошибку, чтобы корректно завершить программу и удалить временные папки
def catch_errors():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                terminate_script(f'{e}')
        return wrapper
    return decorator


