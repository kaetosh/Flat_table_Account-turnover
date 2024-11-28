import os
import time
from tqdm import tqdm
import pandas as pd
from pyfiglet import Figlet
from terminaltexteffects.effects import effect_rain

import config
from dialog_user import select_folder
from logger import logger

from preprocessing_openpyxl import preprocessing_file_excel
from resaving_files import save_as_xlsx_not_alert
from analysis_deviations import revolutions_before_processing, revolutions_after_processing

from processing.A_table_header import table_header
from processing.B_handle_missing_values_in_account import handle_missing_values_in_account
from processing.C_horizontal_structure import horizontal_structure
from processing.F_lines_delete import lines_delete
from processing.G_shiftable_level import shiftable_level
from utility_functions import terminate_script, delete_folders
from winreg_count import increment_run_count

# текст заставки
f1 = Figlet(font='ansi_shadow', justify="center")

if increment_run_count():
    # вывод заставки и описания программы
    effect = effect_rain.Rain(f1.renderText("Flat account turnover"))
    with effect.terminal_output() as terminal:
        for frame in effect:
            terminal.print(frame)
    time.sleep(2)
    print(config.start_message)
    input('Для продолжения нажмите Enter')

    # выбор пользователем папки с обрабатываемыми файлами
    logger.info(f"Сейчас будет предложено выбрать папку с файлами Excel - оборотами счетов.")
    time.sleep(2)
    select_folder()

    logger.info(f"Выбрана папка {os.path.basename(config.folder_path)}. Ожидайте завершения программы.")

    # выгрузки из 1С УПП не загружаются в openpyxl без пересохранения Excel-ем
    # пересохраняем файлы
    save_as_xlsx_not_alert()
    files = os.listdir(config.folder_path_converted)
    excel_files = [file for file in files if (file.endswith('.xlsx') or file.endswith('.xls'))
                   and file != '_СВОД_обороты_счетов.xlsx']
    if not excel_files:
        terminate_script(f'Не найдены файлы Excel в папке {config.folder_path_converted}. Скрипт завершен неудачно')

    # Инициализируем пустой словарь, куда мы добавим обработанные таблицы каждой компании, затем объединим эти файлы в один.
    dict_df = {} # для обрабатываемых таблиц
    dict_df_check = {} # для таблиц сверки оборотов до и после обработки

    def main_process():
        empty_files = []
        for file_excel in tqdm(excel_files, desc="Обработка файлов", ncols=100):
            folder_path_converted_file = os.path.normpath(os.path.join(config.folder_path_converted, file_excel))
            file_excel_treatment = preprocessing_file_excel(folder_path_converted_file)

            # загрузка в pandas
            df = pd.read_excel(file_excel_treatment)

            # устанавливаем шапку таблицы
            result_table_header = table_header(df)
            # признак версии 1С
            # или Конфигурации "Бухгалтерия предприятия", "1С:ERP Агропромышленный комплекс", "1С:ERP Управление предприятием 2"
            # или Конфигурация "Управление производственным предприятием",
            sign_1c = result_table_header[0]
            if not sign_1c:
                empty_files.append(f'{file_excel}')
                continue

            # если есть незаполненные поля группировки (вид номенклатуры например), ставим "не_заполнено"
            df = handle_missing_values_in_account(result_table_header[1], sign_1c)
            if df is None:
                empty_files.append(f'{file_excel}')
                continue

            # разносим иерархию в горизонтальную плоскость
            # если иерархии нет, то файл пустой, пропускаем его
            result_horizontal_structure = horizontal_structure(df, sign_1c)
            if result_horizontal_structure[0]:
                empty_files.append(f'{file_excel}')
                continue
            else:
                df = result_horizontal_structure[1]

            # формируем вспомогательную таблицу с оборотами до обработки
            # потом сравним данные с итоговой таблицей, чтобы убедиться в правильности результата
            df_for_check = revolutions_before_processing(df, sign_1c)

            if df_for_check.empty:
                  empty_files.append(f'{file_excel}')
                  continue

            # удаляем дублирующие строки (родительские счета, счета по которым есть аналитика, обороты, сальдо и т.д.)
            df = lines_delete(df, sign_1c, file_excel)

            # Сдвиг столбцов, чтобы субсчета располагались в одном столбце
            df = shiftable_level(df, True)
            if df is None:
                empty_files.append(f'{file_excel}')
                continue

            # формируем вспомогательную таблицу с оборотами после обработки
            # записываем данные по отклонениям до/после обработки
            df_check = revolutions_after_processing(df, df_for_check, file_excel)
            dict_df_check[file_excel] = df_check

            # запишем таблицу в словарь
            dict_df[file_excel] = df

        # объединяем все таблицы в одну
        result, result_check = None, None
        try:
            # result = pd.concat(list(dict_df.values()))
            result = pd.concat(tqdm(list(dict_df.values()), desc="Идет объединение таблиц", ncols=100))

            # Сдвиг столбцов, чтобы субсчета располагались в одном столбце
            result = shiftable_level(result)
            # объединяем все таблицы со сверками в одну
            result_check = pd.concat(list(dict_df_check.values()))

            deviation_rpm = (result_check['Разница_сальдо_нач'] + result_check['Разница_оборот'] + result_check['Разница_сальдо_кон']).sum()
            if deviation_rpm < 1:
                logger.info('Отклонения до и после обработки менее 1')
            else:
                logger.warning('Обнаружены существенные отклонения до и после обработки. См "СВОД_ОТКЛ_Обороты_счетов.xlsx"', warning_log=True)

            logger.info('Объединение завершено, пытаемся выгрузить файл в excel...')
        except Exception as e:
            terminate_script(f'Ошибка при объединении файлов {e}')

        # выгружаем в excel
        try:
            folder_path_summary_files = os.path.join(config.folder_path, "_СВОД_обороты_счетов.xlsx")
            with pd.ExcelWriter(folder_path_summary_files) as writer:
                # Запись данных чанками с прогрессом
                for i in tqdm(range(0, len(result), 100), desc="Идет запись в .xlsx", ncols=100):
                    result.iloc[i:i + 100].to_excel(writer, sheet_name='Свод', index=False)


                #result.to_excel(writer, sheet_name='Свод', index=False)
                result_check.to_excel(writer, sheet_name='Сверка', index=False)
            logger.info('Файл успешно выгружен в excel')

        except Exception as e:
            terminate_script(f'Ошибка при сохранении файла в excel: {e}')

        # удаляем папки с временными файлами
        delete_folders()

        if empty_files:
            logger.warning(f'Пустые или проблемные файлы: ({len(empty_files)} шт.): {empty_files}', warning_log=True)

        logger.info('Скрипт завершен успешно. Можно закрыть программу.')

    if __name__ == "__main__":
        main_process()
        input()

else:
    logger.info('Попытки запуска исчерпаны. Можно закрыть программу.')
    input()
