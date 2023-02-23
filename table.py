# Таблица имен
import error    #подключаем сообщения об ошибках
import items

_table = []             # таблица по принципу стека

# Открытие блока
def OpenScope():
    _table.append({})   # добавляем пустой словарь


# Закрытие блока
def CloseScope():
    _table.pop(-1)      # удаляем последний добавленный словарь


# для добавления стандартных идентификаторов (добавляет не проверяя, есть ли в таблице)
def add(item):
    last = _table[-1]   # последний блок в таблице имен
    last[item.name] = item


# (добавляет Проверяя, есть ли в таблице)
def new(item):
    last = _table[-1]
    if item.name in last:
        error.ctxError("Повторное объявление имени")
    else:
        add(item)


# поиск в таблице имен
def find(name):
    for block in reversed(_table):
        if name in block:
            return block[name]
    error.ctxError("Необъявленное имя")


# извлечь переменные из таблицы имен
def getVars():
    vars = []
    lastBlock = _table[-1]
    for item in lastBlock.values():
        if type(item) == items.Var:
            vars.append(item)
    return vars
