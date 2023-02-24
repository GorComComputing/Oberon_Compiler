#Лексический анализатор

from enum import Enum #подключаем класс Enum
import string

import text     #подключаем текстовый драйвер
import error    #подключаем сообщения об ошибках
import loc


#объявляем класс Lex производный от  Enum с перечислением лексем
class Lex(Enum):
    NONE, NAME, NUM, MODULE, IMPORT, BEGIN, END, CONST, \
    VAR, WHILE, DO, IF, THEN, ELSIF, ELSE, MULT, DIV, MOD, \
    PLUS, MINUS, EQ, NE, LT, LE, GT, GE, DOT, COMMA, \
    COLON, SEMI, ASS, LPAR, RPAR, EOT = range(34)   # COLON - двоеточие

lex = Lex.NONE  #хранит текущую лексему
num = 0         #содержит значение числа, если лексема NUM
name = ""       #содержит имя, если лексема NAME

MAXINT = 0x7FFFFFFF #ограничение типа int 32-разрядами

#переменная _kw - это хэш-таблица (словарь) (_ используется только в этом файле)
_kw = { #словарь с именами и константами ключевых слов
    "MODULE": Lex.MODULE,
    "IMPORT": Lex.IMPORT,
    "CONST": Lex.CONST,
    "VAR": Lex.VAR,
    "BEGIN": Lex.BEGIN,
    "END": Lex.END,
    "IF": Lex.IF,
    "THEN": Lex.THEN,
    "ELSIF": Lex.ELSIF,
    "ELSE": Lex.ELSE,
    "WHILE": Lex.WHILE,
    "DO": Lex.DO,
    "DIV": Lex.DIV,
    "MOD": Lex.MOD,
    "ARRAY": Lex.NONE,
    "RECORD": Lex.NONE,
    "POINTER": Lex.NONE,
    "SET": Lex.NONE,
    "WITH": Lex.NONE,
    "CASE": Lex.NONE,
    "OF": Lex.NONE,
    "LOOP": Lex.NONE,
    "EXIT": Lex.NONE,
    "PROCEDURE": Lex.NONE,
    "FOR": Lex.NONE,
    "TO": Lex.NONE,
    "BY": Lex.NONE,
    "IN": Lex.NONE,
    "IS": Lex.NONE,
    "NIL": Lex.NONE,
    "OR": Lex.NONE,
    "TYPE": Lex.NONE,
    "REPEAT": Lex.NONE,
    "UNTIL": Lex.NONE,
    "RETURN": Lex.NONE
}


# словарь для подставления имени лексемы в сообщении об ошибках
_names = {
    Lex.NAME: 'имя',
    Lex.NUM: 'число',
    Lex.MULT: '"*"',
    Lex.PLUS: '"+"',
    Lex.MINUS: '"-"',
    Lex.EQ: '"="',
    Lex.NE: '"#"',
    Lex.LT: '"<"',
    Lex.LE: '"<="',
    Lex.GT: '">"',
    Lex.GE: '">="',
    Lex.DOT: '"."',
    Lex.COMMA: '","',
    Lex.COLON: '":"',
    Lex.SEMI: '";"',
    Lex.ASS: '":="',
    Lex.LPAR: '"("',
    Lex.RPAR: '")"',
    Lex.EOT: '"конец текста"',
}

# подставляет имя лексемы для сообщения об ошибках
def lexName(L: Lex):
    return _names.get(L, L.name)


#Собирает имя идентификатора в одну строку
def scanName():
    global name, lex #Указываем, что name и lex глобальные переменные
    name = text.ch   #Первый символ идентификатора или ключевого слова
    text.nextCh()
    while text.ch in string.ascii_letters + string.digits:
        name += text.ch #читаем остальные символы и цифры
        text.nextCh()
    #print(name)
    lex = _kw.get(name, Lex.NAME) #если ключ есть в словаре..., если нет, то второй параметр
    #print(lex)


#собираем число
def scanNumber():
    global num, lex  #глобальная переменная
    num = 0
    while text.ch in string.digits: #пока идут цифры
        #d = int(text.ch) #конвертируем строку в integer
        d = ord(text.ch) - ord('0') #перевод из строки в int через вычитание кода ASCII
        if num > (MAXINT - d)//10:  #проверка на размер int
            error.lexError("Слишком большое число")
        else:
            num = 10*num + d #накапливание числа слева направо
        text.nextCh()
    lex = Lex.NUM
    #print(num)


#обработка комментариев
def Comment():
    # пропуск *
    text.nextCh()
    while True:
        while text.ch not in {'*', text.chEOT}:
            # проверяем на начало вложенного комментария
            if text.ch == '(':
                text.nextCh()
                if text.ch == '*':
                    Comment()
            else:
                text.nextCh()
        if text.ch == text.chEOT:
            error.lexError("Не закончен комментарий")
        else: # здесь *
            text.nextCh()
        if text.ch == ')': break

    text.nextCh()


#функция выбора следующей лексемы (это и есть сам сканер)
def nextLex():
    global lex #глобальная переменная

    while text.ch in {text.chSPACE, text.chTAB, text.chEOL}:
        text.nextCh()  #пропускаем пробелы, табуляцию, и конец строки

    # переводим указатель курсора на начало лексемы
    loc.lexPos = loc.pos

    if text.ch in string.ascii_letters: #если сивол (большой и малый регистр)
        scanName()
    elif text.ch in string.digits: #если цифра
        scanNumber()
    elif text.ch == ';':
        lex = Lex.SEMI
        text.nextCh()
    elif text.ch == '.':
        lex = Lex.DOT
        text.nextCh()
    elif text.ch == ',':
        lex = Lex.COMMA
        text.nextCh()
    elif text.ch == '+':
        lex = Lex.PLUS
        text.nextCh()
    elif text.ch == '-':
        lex = Lex.MINUS
        text.nextCh()
    elif text.ch == '*':
        lex = Lex.MULT
        text.nextCh()
    elif text.ch == ':':###########
        text.nextCh()
        if text.ch == '=':
            lex = Lex.ASS
            text.nextCh()
        else:
            lex = Lex.COLON
    elif text.ch == '=':
        lex = Lex.EQ
        text.nextCh()
    elif text.ch == '#':
        lex = Lex.NE
        text.nextCh()
    elif text.ch == '>':###########
        text.nextCh()
        if text.ch == '=':
            lex = Lex.GE
            text.nextCh()
        else:
            lex = Lex.GT
    elif text.ch == '<':###########
        text.nextCh()
        if text.ch == '=':
            lex = Lex.LE
            text.nextCh()
        else:
            lex = Lex.LT
    elif text.ch == '(':#############
         text.nextCh()
         if text.ch == '*':
            Comment()   #пропускаем комментарий
            nextLex()   #вызываем новую лексему
         else:
            lex = Lex.LPAR
    elif text.ch == ')':
        lex = Lex.RPAR
        text.nextCh()
    elif text.ch == text.chEOT: #если конец файла
        lex = Lex.EOT
    else:
        error.lexError("Недопустимый символ")
        text.nextCh()


#def lex():
#    return _lex

