import sys

import openpyxl
from logger import logger


def preprocessing_file_excel(path_file_excel):
    file_excel = path_file_excel.split('/')[-1]
    file_excel_treatment = f'preprocessing_files/preprocessing_{file_excel}'
    try:
        workbook = openpyxl.load_workbook(path_file_excel)
    except Exception as e:
        logger.error(f'''\n{file_excel}: Косячный файл-выгрузка из 1с, пересохраните этот файл и снова запустите скрипт.
                      Или открыт обрабатываемый файл. Закройте этот файл и снова запустите скрипт.
                      Ошибка: {e}''')
        sys.exit()

    sheet = workbook.active

    # Снимаем объединение ячеек
    merged_cells_ranges = list(sheet.merged_cells.ranges)
    for merged_cell_range in merged_cells_ranges:
        sheet.unmerge_cells(str(merged_cell_range))

    # Столбец с уровнями группировок
    sheet.insert_cols(idx=1)
    for row_index in range(1, sheet.max_row + 1):
        cell = sheet.cell(row=row_index, column=1)
        cell.value = sheet.row_dimensions[row_index].outline_level
    # Указываем наименование столбца с уровнями группировки
    sheet['A1'] = "Уровень"

    # Вставляем новый столбец после столбца "Уровень"
    sheet.insert_cols(idx=2)
    
   
    
    # Сохраняем файл под новым названием
    #file_excel_treatment = f'Обработка_{file_excel}'
    workbook.save(file_excel_treatment)
    workbook.close()
    print(f'\n{file_excel}: сняли объединение ячеек, проставли уровни группировок')
    logger.info(f'\n{file_excel}: сняли объединение ячеек, проставли уровни группировок и признак курсив в ячейках')
    return file_excel_treatment
