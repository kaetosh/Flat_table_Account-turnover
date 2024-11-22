"""
Найдем пустые значения в столбце Счет (не заполненные поля Вид субконто или субконто),
чтобы в дальнейшем поставить признак "Не заполнено"
"""


from utility_functions import is_accounting_code

def handle_missing_values_in_account(df, sign_1c):    
    

    column_name_with_count = next((s for s in df.columns.to_list() if str(s).startswith("Показ")), None)
    if column_name_with_count:
        try:

            mask = df[column_name_with_count].str.contains('Кол.', na=False)
            df.loc[~mask, sign_1c] = df.loc[~mask, sign_1c].fillna('Не_заполнено')
            df[sign_1c].ffill(inplace=True)
        except KeyError:
            return None
    else:
        try:
            df[sign_1c].fillna('Не_заполнено', inplace=True)
        except KeyError:
            return None
    df[sign_1c] = df[sign_1c].apply(lambda x: str(x))
    df[sign_1c] = df[sign_1c].apply(lambda x: f'0{x}' if (len(str(x)) == 1 and is_accounting_code(x)) else x)
    
    return df
