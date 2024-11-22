"""
Обновляем наименования столбцов на корректные
"""

from settings import name_account_balance_movements
from logger import logger

sign_1c_upp = 'Субконто'
sign_1c_not_upp = 'Счет'
# Функция для обновления элементов списка


def table_header(df, file_excel):
    
    # получаем индекс строки, содержащей target_value (значение)
    index_for_columns = 0
    for i in name_account_balance_movements:
        nalue_dict = name_account_balance_movements[i]
        for j in nalue_dict:
            indices = df.index[df.apply(lambda row: j in row.values, axis=1)]
            if not indices.empty:
                index_for_columns = indices[0]
                break
        
    # устанавливаем заголовки
    df.columns = df.iloc[index_for_columns]
    
    df = df.loc[:, df.columns.notna()]
    
    df = df.drop(df.index[0:(index_for_columns+1)]) # удаляем данные выше строки, содержащей имена столбцов таблицы (наименование отчета, период и т.д.)
    
    df.dropna(axis=0, how='all', inplace=True) # удаляем пустые строки
    df.dropna(axis=1, how='all', inplace=True)
    
    print(f'{file_excel} удалены пустые строки')
    # получим наименование первого столбца, в котором находятся наши уровни
    # переименуем этот столбец

    df.columns.values[0] = 'Уровень'

    print(f'{file_excel} оставляем только табличные данные, переименовываем шапку таблицы')

    sign_1c = sign_1c_not_upp
    
    # Находим индексы столбцов с оборотамии сальдо
    debit_turnover_index = False
    for i in name_account_balance_movements['debit_turnover']:
        try:
            debit_turnover_index = df.columns.get_loc(i)
            if i == name_account_balance_movements['debit_turnover'][1]:
                sign_1c = sign_1c_upp
            break
        except KeyError:
            continue
    
    credit_turnover_index = False    
    for i in name_account_balance_movements['credit_turnover']:
        try:
            credit_turnover_index = df.columns.get_loc(i)
            if i == name_account_balance_movements['credit_turnover'][1]:
                sign_1c = sign_1c_upp
            break
        except KeyError:
            continue
            
    start_debit_balance_index = False
    for i in name_account_balance_movements['start_debit_balance']:
        try:
            start_debit_balance_index = df.columns.get_loc(i)
            if i == name_account_balance_movements['start_debit_balance'][1]:
                sign_1c = sign_1c_upp
            break
        except KeyError:
            continue
    
    start_credit_balance_index = False    
    for i in name_account_balance_movements['start_credit_balance']:
        try:
            start_credit_balance_index = df.columns.get_loc(i)
            if i == name_account_balance_movements['start_credit_balance'][1]:
                sign_1c = sign_1c_upp
            break
        except KeyError:
            continue
    
    end_debit_balance_index = False    
    for i in name_account_balance_movements['end_debit_balance']:
        try:
            end_debit_balance_index = df.columns.get_loc(i)
            if i == name_account_balance_movements['end_debit_balance'][1]:
                sign_1c = sign_1c_upp
            break
        except KeyError:
            continue
    
    end_credit_balance_index = False    
    for i in name_account_balance_movements['end_credit_balance']:
        try:
            end_credit_balance_index = df.columns.get_loc(i)
            if i == name_account_balance_movements['end_credit_balance'][1]:
                sign_1c = sign_1c_upp
            break
        except KeyError:
            continue
    
    indices_to_rename = [start_debit_balance_index,
                         start_credit_balance_index,
                         debit_turnover_index,
                         credit_turnover_index,
                         end_debit_balance_index,
                         end_credit_balance_index]
    new_names = ['Дебет_начало',
                 'Кредит_начало',
                 'Дебет_оборот',
                 'Кредит_оборот',
                 'Дебет_конец',
                 'Кредит_конец']
    
    # Добавляем префикс 'до' к столбцам до 'КредитОборот'
    if any(col in df.columns for col in name_account_balance_movements['debit_turnover']):
        df.columns = [col if idx <= debit_turnover_index else f'{str(col)}_до' if debit_turnover_index < idx < credit_turnover_index else col for idx, col in enumerate(df.columns)]

    # Добавляем префикс 'ко' к столбцам после 'КредитОборот'
    if any(col in df.columns for col in name_account_balance_movements['credit_turnover']):
        df.columns = [col if (idx < credit_turnover_index or col in name_account_balance_movements['credit_turnover'] + name_account_balance_movements['end_debit_balance'] + name_account_balance_movements['end_credit_balance']) else f'{str(col)}_ко' for idx, col in enumerate(df.columns)]
    

    # переименуем первые два столбца
    df.columns.values[0] = 'Уровень'
    logger.info(f'{file_excel}: успешно обновили шапку таблицы, удалили строки выше шапки')
    
    # Получаем текущие имена столбцов
    current_columns = df.columns.tolist()
    
    # Создаем словарь с новыми именами для желаемых индексов
    rename_dict = {current_columns[i]: new_names[j] for j, i in enumerate(indices_to_rename) if i}
    

    # Переименовываем столбцы
    df.rename(columns=rename_dict, inplace=True)
    
    
    # удаляем пустые строки и столбцы
    df.dropna(axis=0, how='all', inplace=True)

    logger.info(f'{file_excel}: удалили пустые строки и столбцы')


    
    return sign_1c, df
    
