"""
Найдем пустые значения в столбце Счет (не заполненные поля Вид субконто или субконто),
чтобы в дальнейшем поставить признак "Не заполнено"
"""


from utility_functions import is_accounting_code

def handle_missing_values_in_account(df, sign_1c):
    df[sign_1c].fillna('Не_заполнено', inplace=True)
    df[sign_1c] = df[sign_1c].apply(lambda x: str(x))
    df[sign_1c] = df[sign_1c].apply(lambda x: f'0{x}' if (len(str(x)) == 1 and is_accounting_code(x)) else x)
    return df
