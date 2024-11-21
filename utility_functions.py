# A function for determining whether a value is an accounting
def is_accounting_code(value):
    if value:
        # Проверка на значение "000"
        if str(value) == "000":
            return True

        try:
            parts = str(value).split('.')
            has_digit = any(part.isdigit() for part in parts)
            # Проверка, состоит ли каждая часть только из цифр (длиной 1 или 2) или (если длина меньше 3) только из букв
            return has_digit and all(
                (part.isdigit() and len(part) <= 2) or (len(part) < 3 and part.isalpha()) for part in parts)
        except TypeError:
            return False
    else:
        return False
