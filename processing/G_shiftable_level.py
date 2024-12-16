import pandas as pd
from utility_functions import is_accounting_code, catch_errors


@catch_errors()
def shiftable_level(df, par=False):
    
    for j in range(5):
        list_lev = [i for i in df.columns.to_list() if 'Level' in i]
        for i in list_lev:
            # если в столбце есть и субсчет и субконто, нужно выравнивать столбцы
            if df[i].apply(is_accounting_code).nunique() == 2:
                shift_level = i  # получили столбец, в котором есть и субсчет и субконто, например Level_2
                lm = int(shift_level.split('_')[-1])  # получим его хвостик, например 2
                # получим перечень столбцов, которые бум двигать (первый - это столбец, где есть и субсчет и субконто)
                new_list_lev = list_lev[lm:]
                # сдвигаем:
                df[new_list_lev] = df.apply(
                    lambda x: pd.Series([x[i] for i in new_list_lev]) if is_accounting_code(
                        x[new_list_lev[0]]) else pd.Series([x[i] for i in list_lev[lm - 1:-1]]), axis=1)
                break

    if par and not df['Level_0'].apply(is_accounting_code).all():
        return None
    
    # Разделяем столбцы на две группы
    level_columns = [col for col in df.columns if 'Level_' in col]
    
    # Сортируем столбцы с Level_ по числовому значению в их названиях
    level_columns.sort(key=lambda x: int(x.split('_')[1]))
    
    if par:
        df.rename(columns={'Субконто': 'Аналитика'}, inplace=True)
        
    # Определяем желаемый порядок столбцов
    desired_order = [
        'Исх.файл',
        'Аналитика',
        'Дебет_начало',
        'Количество_Дебет_начало',
        'Кредит_начало',
        'Количество_Кредит_начало',
        'Дебет_оборот',
        'Количество_Дебет_оборот'
    ]
    
    # Находим столбцы, заканчивающиеся на '_до' и '_ко'
    do_columns = df.filter(regex='_до$').columns.tolist()
    ko_columns = df.filter(regex='_ко$').columns.tolist()
    
    do_columns.sort()
    ko_columns.sort()
    
    # Добавляем найденные столбцы к желаемому порядку
    desired_order.extend(do_columns)
    desired_order.append('Кредит_оборот')
    desired_order.append('Количество_Кредит_оборот')
    desired_order.extend(ko_columns)
    desired_order.append('Дебет_конец')
    desired_order.append('Количество_Дебет_конец')
    desired_order.append('Кредит_конец')
    desired_order.append('Количество_Кредит_конец')
    
    # Отбор существующих столбцов
    existing_columns = [col for col in desired_order if col in df.columns]
    
    # Используем reindex для сортировки DataFrame
    df = df.reindex(columns=(existing_columns + level_columns)).copy()
    
    return df
