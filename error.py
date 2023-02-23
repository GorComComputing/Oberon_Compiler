#Сообщения об ошибках
import loc
import text

#Основная функция сообщения об ошибке
def _error(msg, p):
    while text.ch not in {text.chEOL, text.chEOT}:
        text.nextCh()
    print(' ' * (p-1), '^', sep='') #указывает на позицию символа с ошибкой
    print(msg)
    exit(1)  #Завершает работу программы с кодом возврата 1


#сообщаем о лексической ошибке
def lexError(msg):
    _error(msg, loc.pos)    # указывает на начало символа


#сообщаем о синтаксической ошибке
def expect(msg):
    _error("Ожидается " + msg, loc.lexPos)    # указывает на начало лексемы


#сообщаем о контекстной (семантической) ошибке
def ctxError(msg):
    _error(msg, loc.lexPos)


#Функция Error печатает сообщения об ошибке и завершает программу
def Error(msg):
    print()
    print(msg)
    exit(2)  #Завершает работу программы с кодом возврата 2


# предупреждение
def Warning(msg):
    print()
    print(msg)
