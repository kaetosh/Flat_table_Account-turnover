import pandas as pd
from utility_functions import catch_errors


@catch_errors()
def revolutions_before_processing(df, sign_1c):

    # Список необходимых столбцов
    required_columns = ['Дебет_начало', 'Кредит_начало', 'Дебет_оборот', 'Кредит_оборот', 'Дебет_конец', 'Кредит_конец']
    
    # Отбор существующих столбцов
    existing_columns = [col for col in required_columns if col in df.columns]
    
    if df[df[sign_1c] == 'Итого'][existing_columns].empty:
        return None
    else:
        df_for_check = df[df[sign_1c] == 'Итого'][[sign_1c] + existing_columns].copy().tail(2).iloc[[0]]
        df_for_check[existing_columns] = df_for_check[existing_columns].astype(float)
        df_for_check.fillna(0, inplace = True)

        for i in required_columns:
            if i in existing_columns:
                df[i] = pd.to_numeric(df[i], errors='coerce')

        df_for_check['Сальдо_начало_до_обработки'] = ((df_for_check['Дебет_начало'] if 'Дебет_начало' in existing_columns else 0) 
                                                      - (df_for_check['Кредит_начало'] if 'Кредит_начало' in existing_columns else 0))
        
        df_for_check['Сальдо_конец_до_обработки'] = ((df_for_check['Дебет_конец'] if 'Дебет_конец' in existing_columns else 0) 
                                                     - (df_for_check['Кредит_конец'] if 'Кредит_конец' in existing_columns else 0))
        
        df_for_check['Оборот_до_обработки'] = ((df_for_check['Дебет_оборот'] if 'Дебет_оборот' in existing_columns else 0)
                                               - (df_for_check['Кредит_оборот'] if 'Кредит_оборот' in existing_columns else 0))
        
        df_for_check = df_for_check[[
                                     'Сальдо_начало_до_обработки',
                                     'Оборот_до_обработки',
                                     'Сальдо_конец_до_обработки']].copy()
        df_for_check = df_for_check.reset_index(drop=True)
        
        return df_for_check

def revolutions_after_processing(df, df_for_check, file_excel):
    
    # Список необходимых столбцов
    required_columns = ['Дебет_начало', 'Кредит_начало', 'Дебет_оборот', 'Кредит_оборот', 'Дебет_конец', 'Кредит_конец']
    
    # Отбор существующих столбцов
    existing_columns = [col for col in required_columns if col in df.columns]
    
    df_for_check_2 = pd.DataFrame()
    df_for_check_2['Сальдо_начало_после_обработки'] = [(df['Дебет_начало'].sum() if 'Дебет_начало' in existing_columns else 0) - (df['Кредит_начало'].sum() if 'Кредит_начало' in existing_columns else 0)]

    # Фильтрация столбцов, названия которых заканчиваются на "_до"
    do_columns = df.filter(regex='_до$')
    do_columns = do_columns.loc[:, ~do_columns.columns.str.startswith('Количество_')]
    
    # Вычисление суммы значений этих столбцов
    sum_do_columns = do_columns.sum().sum()
    
    # Фильтрация столбцов, названия которых заканчиваются на "_ко"
    ko_columns = df.filter(regex='_ко$')
    ko_columns = ko_columns.loc[:, ~ko_columns.columns.str.startswith('Количество_')]
    
    # Вычисление суммы значений этих столбцов
    sum_ko_columns = ko_columns.sum().sum()
    
    df_for_check_2['Оборот_после_обработки'] = sum_do_columns - sum_ko_columns
    df_for_check_2['Сальдо_конец_после_обработки'] = [(df['Дебет_конец'].sum() if 'Дебет_конец' in existing_columns else 0) - (df['Кредит_конец'].sum() if 'Кредит_конец' in existing_columns else 0)]
    df_for_check_2 = df_for_check_2.reset_index(drop=True)
    df_for_check = df_for_check.reset_index(drop=True)
    
    # Объединение DataFrame с использованием внешнего соединения
    merged_df = pd.concat([df_for_check, df_for_check_2], axis=1)

    # Заполнение отсутствующих значений нулями
    merged_df = merged_df.infer_objects().fillna(0)

    # Вычисление разницы
    merged_df['Разница_сальдо_нач'] = merged_df['Сальдо_начало_до_обработки'] - merged_df['Сальдо_начало_после_обработки']
    merged_df['Разница_оборот'] = merged_df['Оборот_до_обработки'] - merged_df['Оборот_после_обработки']
    merged_df['Разница_сальдо_кон'] = merged_df['Сальдо_конец_до_обработки'] - merged_df['Сальдо_конец_после_обработки']
    
    merged_df['Разница_сальдо_нач'] = merged_df['Разница_сальдо_нач'].apply(lambda x: round(x))
    merged_df['Разница_оборот'] = merged_df['Разница_оборот'].apply(lambda x: round(x))
    merged_df['Разница_сальдо_кон'] = merged_df['Разница_сальдо_кон'].apply(lambda x: round(x))

    merged_df['Исх.файл'] = file_excel
    
    return merged_df
