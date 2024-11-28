"""
Нам нужно сохранить записи самого глубокого уровня иерархии и преобразовать данные так,
чтобы уровни выше по иерархии были представлены в горизонтальной форме.
"""

from utility_functions import catch_errors


def fill_level(row, prev_value, level, sign_1c) -> float:
    if row['Уровень'] == level:
        return row[sign_1c]
    else:
        return prev_value

@catch_errors()
def horizontal_structure(df, sign_1c):

    # Инициализация переменной для хранения предыдущего значения
    prev_value = None

    # получим максимальный уровень иерархии
    max_level = df['Уровень'].max()
    
    if df.empty:
        return True, df

    # разнесем уровни в горизонтальную ориентацию в цикле
    for i in range(max_level + 1):
        df[f'Level_{i}'] = df.apply(lambda x: fill_level(x, prev_value, i, sign_1c), axis=1)
        for j, row in df.iterrows():
            if row['Уровень'] == i:
                prev_value = row[sign_1c]
                if prev_value == 'Количество':
                    prev_value = df.at[j-1, sign_1c]
            df.at[j, f'Level_{i}'] = prev_value
    return False, df
