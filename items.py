# Элементы таблицы имен

class Module:
    def __init__(self, name: str):
        assert type(name) == str    # дополнительная проверка на строку
        self.name = name


class Const:
    def __init__(self, name, typ, value):
        assert type(name) == str    # дополнительная проверка на строку
        self.name = name
        self.typ = typ
        self.value = value


class Var:
    def __init__(self, name, typ):
        assert type(name) == str    # дополнительная проверка на строку
        self.name = name
        self.typ = typ
        self.addr = 0 #addr - место последнего использования переменной


class Type:
    def __init__(self, name, typ):
        assert type(name) == str    # дополнительная проверка на строку
        self.name = name
        self.typ = typ


class Func:
    def __init__(self, name, typ):
        assert type(name) == str    # дополнительная проверка на строку
        self.name = name
        self.typ = typ


class Proc:
    def __init__(self, name):
        assert type(name) == str    # дополнительная проверка на строку
        self.name = name

