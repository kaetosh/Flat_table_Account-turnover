from config import exclude_values
from utility_functions import catch_errors


@catch_errors()
def lines_delete(df, sign_1c, file_excel):  

    df[sign_1c] = df[sign_1c].apply(lambda x: str(x))
    column_name_with_count = next((s for s in df.columns.to_list() if str(s).startswith("Показ")), None)
    
    # Определяем желаемый порядок столбцов
    desired_order = [
        'Дебет_начало',
        'Кредит_начало',
        'Дебет_оборот',
        'Кредит_оборот',
        'Дебет_конец',
        'Кредит_конец'
    ]
    
    # Находим столбцы, заканчивающиеся на '_до' и '_ко'
    do_columns = df.filter(regex='_до$').columns.tolist()
    ko_columns = df.filter(regex='_ко$').columns.tolist()
    
    do_columns.sort()
    ko_columns.sort()
    
    # Добавляем найденные столбцы к желаемому порядку
    desired_order.extend(do_columns)
    desired_order.append('Кредит_оборот')
    desired_order.extend(ko_columns)
    desired_order.append('Дебет_конец')
    desired_order.append('Кредит_конец')
    desired_order = [col for col in desired_order if col in df.columns]

    if sign_1c == 'Субконто' and df[sign_1c].isin(['Количество']).any():
        for i in desired_order:
            df[f'Количество_{i}'] = df[i].shift(-1)
    elif column_name_with_count:
        for i in desired_order:
            df[f'Количество_{i}'] = df[i].shift(-1)

    max_level = df['Уровень'].max()
    
    df = df[~df[sign_1c].str.contains('Итого')]
    df = df[~df[sign_1c].str.contains('Количество')]
    if column_name_with_count:
        df = df[~df[column_name_with_count].str.contains('Кол.', na=False)]
        df = df.drop([column_name_with_count], axis=1)
    
    
    for i in range(max_level):
        df = df[~((df['Уровень']==i) & (df[sign_1c] == df[f'Level_{i}']) & (i<df['Уровень'].shift(-1)))]

    df = df[~df[sign_1c].isin(exclude_values)].copy()
    df[sign_1c] = df[sign_1c].astype(str)

    # Список необходимых столбцов
    required_columns = ['Дебет_начало', 'Кредит_начало', 'Дебет_оборот', 'Кредит_оборот', 'Дебет_конец', 'Кредит_конец']
    
    # Отбор существующих столбцов
    existing_columns = [col for col in required_columns if col in df.columns]
    
    df = df[df[existing_columns].notna().any(axis=1)]
    df.rename(columns={'Счет': 'Субконто'}, inplace=True)
    df.drop('Уровень', axis=1, inplace=True)
    df['Исх.файл'] = file_excel
    
    return df
