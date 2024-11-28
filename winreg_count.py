import winreg
from logger import logger


def get_run_count():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\flat_analysis_1', 0, winreg.KEY_READ) as key:
            count = winreg.QueryValueEx(key, 'RunCount')[0]
            return count
    except FileNotFoundError:
        return 0

def set_run_count(count):
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\flat_analysis_1') as key:
        winreg.SetValueEx(key, 'RunCount', 0, winreg.REG_DWORD, count)

def increment_run_count():
    current_count = get_run_count()
    if current_count < 150:  # Ограничиваем количество запусков, например, 5
        set_run_count(current_count + 1)
        logger.info(f"Скрипт запущен {current_count + 1} раз(а).")
        return True
    else:
        return False

# Устанавливаем начальный счетчик, если он еще не установлен
if get_run_count() == 0:
    set_run_count(0)  # Установите начальное значение счетчика, если необходимо
