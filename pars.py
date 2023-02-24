#Синтаксический анализатор

import text
import scan
import table
from scan import Lex
import error    #подключаем сообщения об ошибках
import items
import enum
from gen import *
import vm as cm
import gen


# Типы данных
class Types(enum.Enum):
    Bool, Int = range(2)


# отладочная функция (просто выводит файл на экран)
# не используется
def testText():
    text.nextCh()
    while text.ch != text.chEOT:
        text.nextCh()


# отладочная функция (просто считает число лексем)
# не используется
def testScan():
    text.nextCh()   # читаем первый символ
    scan.nextLex()  # читаем первую лексему
    n = 0           # счетчик лексем
    while scan.lex != scan.Lex.EOT:
        #print('\n', scan.lex)
        n += 1
        scan.nextLex()  # читаем следующую лексему
    print("Число лексем:", n)


# проверяет следующую лексему (Читает следующую)
def skip(L: Lex):
    # if lex() == L:
    if scan.lex == L:
        scan.nextLex()
    else:
        error.expect(scan.lexName(L))


# проверяет следующую лексему (НЕ читает следующую)
def check(L: Lex):
    if scan.lex != L:
        error.expect(scan.lexName(L))


#
def ImportModule():
    check(Lex.NAME)
    name = scan.name
    if name in {"In", "Out"}:
        table.new(items.Module(name))
    else:
        error.ctxError("Предусмотрены только модули In и Out")
    scan.nextLex()


#   IMPORT Имя {"," Имя} ";".
def Import():
    skip(Lex.IMPORT)
    ImportModule()
    while scan.lex == Lex.COMMA:
        scan.nextLex()
        ImportModule()
    skip(Lex.SEMI)


# ["+" | "-"] (Число | Имя).
def ConstExpr():
    sign = 1
    if scan.lex in {Lex.PLUS, Lex.MINUS}:
        if scan.lex == Lex.MINUS:
            sign = -1
        scan.nextLex()
    if scan.lex == Lex.NUM:
        value = scan.num*sign
        scan.nextLex()
        return value
    elif scan.lex == Lex.NAME:
        x = table.find(scan.name)
        scan.nextLex()
        if type(x) != items.Const:
            error.expect("константа")
        else:
            return x.value*sign
    else:
        error.expect("число или имя константы")
    #scan.nextLex()


# Имя "=" КонстВыраж.
def ConstDecl():
    check(Lex.NAME)
    name = scan.name
    scan.nextLex()
    skip(Lex.EQ)
    value = ConstExpr()
    table.new(items.Const(name, Types.Int, value))


# Тип = Имя.
def Type():
    check(Lex.NAME)
    x = table.find(scan.name)
    if type(x) != items.Type:
        error.expect("имя типа")
    scan.nextLex()


# Имя {"," Имя} ":" Тип.
def VarDecl():
    check(Lex.NAME)
    table.new(items.Var(scan.name, Types.Int))
    scan.nextLex()
    while scan.lex == Lex.COMMA:
        scan.nextLex()
        check(Lex.NAME)
        table.new(items.Var(scan.name, Types.Int))
        scan.nextLex()
    skip(Lex.COLON)
    Type()


#   {CONST
#      {ОбъявлКонст ";"}
#   |VAR
#      {ОбъявлПерем ";"} }.
def DeclSeq():
    while scan.lex in {Lex.CONST, Lex.VAR}:
        if scan.lex == Lex.CONST:
            scan.nextLex()
            while scan.lex == Lex.NAME:
                ConstDecl()
                skip(Lex.SEMI)
        else: # VAR
            scan.nextLex()
            while scan.lex == Lex.NAME:
                VarDecl()
                skip(Lex.SEMI)


#Множитель =
#   Имя ["(" Выраж | Тип ")"]
#   | Число
#   | "(" Выраж ")".
def Factor():
    if scan.lex == Lex.NAME:
        x = table.find(scan.name)
        if type(x) == items.Const:
            GenConst(x.value)
            scan.nextLex()
            return x.typ
        elif type(x) == items.Var:
            GenAddr(x)
            Gen(cm.LOAD)
            scan.nextLex()
            return x.typ
        elif type(x) == items.Func:
            scan.nextLex()
            skip(Lex.LPAR)
            Function(x)
            skip(Lex.RPAR)
            return x.typ
        else:
            error.expect("имя константы, переменной или функции")
    elif scan.lex == Lex.NUM:
        Gen(scan.num)
        scan.nextLex()
        return Types.Int
    elif scan.lex == Lex.LPAR:
        scan.nextLex()
        T = Expression()
        skip(Lex.RPAR)
        return T
    else:
        error.expect("имя, число или '('")


# Слагаемое = Множитель {ОперУмн Множитель}.
def Term():
    T = Factor()    # множитель
    while scan.lex in {Lex.MULT, Lex.DIV, Lex.MOD}:
        Op = scan.lex
        TestInt(T)
        scan.nextLex()
        T = Factor()    # множитель
        TestInt(T)
        if Op == Lex.DIV:
            Gen(cm.DIV)
        elif Op == Lex.MULT:
            Gen(cm.MULT)
        else:
            Gen(cm.MOD)
    return T


#ПростоеВыраж = ["+"|"-"] Слагаемое {ОперСлож Слагаемое}.
def SimpleExpr():
    if scan.lex in {Lex.PLUS, Lex.MINUS}:
        op = scan.lex
        scan.nextLex()
        T = Term()  # слагаемое
        TestInt(T)
        if op == Lex.MINUS:
            Gen(cm.NEG)
    else:
        T = Term()
    while scan.lex in {Lex.PLUS, Lex.MINUS}:
        op = scan.lex
        TestInt(T)
        scan.nextLex()
        T = Term()  # слагаемое
        TestInt(T)
        if op == Lex.PLUS:
            Gen(cm.ADD)
        else:
            Gen(cm.SUB)
    return T


# проверить, что выражение целого типа
def TestInt(T):
    if T != Types.Int:
        error.expect("выражение целого типа")


# Выраж = ПростоеВыраж [Отношение ПростоеВыраж].
def Expression():
    T = SimpleExpr()
    if scan.lex in {Lex.EQ, Lex.NE, Lex.LT, Lex.LE, Lex.GT, Lex.GE}:
        op = scan.lex
        TestInt(T)
        scan.nextLex()
        T = SimpleExpr()
        TestInt(T)
        GenComp(op)
        return Types.Bool
    else:
        return T


# Параметр = Переменная | Выраж.
def Parameter():
    Expression()


#   Переменная ":=" Выраж
def AssStatement(x):
    # x - переменная
    GenAddr(x)
    skip(Lex.NAME)
    skip(Lex.ASS)
    T = Expression()
    if x.typ != T:
        error.ctxError("Несоответсвие типов при присваивании")
    Gen(cm.SAVE)


def IntExpr():
    T = Expression()
    if T != Types.Int:
        error.expect("выражение целого типа")


# проверка переменной
def Variable():
    check(Lex.NAME)
    v = table.find(scan.name)
    if type(v) != items.Var:
        error.expect("имя переменной")
    GenAddr(v)
    scan.nextLex()


def Procedure(x):
    if x.name == "HALT":
        value = ConstExpr()
        GenConst(value)
        Gen(cm.STOP)
    elif x.name == "INC":
        # INC(v); INC(v, n)
        Variable()
        Gen(cm.DUP)
        Gen(cm.LOAD)
        if scan.lex == Lex.COMMA:
            scan.nextLex()
            IntExpr()
        else:
            Gen(1)
        Gen(cm.ADD)
        Gen(cm.SAVE)
    elif x.name == "DEC":
        # DEC(v); DEC(v, n)
        Variable()
        Gen(cm.DUP)
        Gen(cm.LOAD)
        if scan.lex == Lex.COMMA:
            scan.nextLex()
            IntExpr()
        else:
            Gen(1)
        Gen(cm.SUB)
        Gen(cm.SAVE)
        if scan.lex == Lex.COMMA:
            scan.nextLex()
            IntExpr()
    elif x.name == "In.Open":
        pass
    elif x.name == "In.Int":
        Variable()
        Gen(cm.IN)
        Gen(cm.SAVE)
    elif x.name == "Out.Int":
        # Out.Int(e, f)
        IntExpr()
        skip(Lex.COMMA)
        IntExpr()
        Gen(cm.OUT)
    elif x.name == "Out.Ln":
        Gen(cm.LN)
    else:
        assert False


def Function(x):
    if x.name == "ABS":
        IntExpr()       # x
        Gen(cm.DUP)     # x,x
        Gen(0)          # x,x,0
        Gen(gen.PC+3)   # x,x,0,A
        Gen(cm.IFGE)
        Gen(cm.NEG)
    elif x.name == "MIN":
        # MIN(INTEGER)
        Type()
        Gen(scan.MAXINT)
        Gen(cm.NEG)
        Gen(1)
        Gen(cm.SUB)
    elif x.name == "MAX":
        # MAX(INTEGER)
        Type()
        Gen(scan.MAXINT)
    elif x.name == "ODD":
        IntExpr()
        Gen(2)      # x,2
        Gen(cm.MOD) # x MOD 2
        Gen(0)      # x MOD 2,0
        Gen(0)      # x MOD 2,0, 0_фиктивный адрес перехода
        Gen(cm.IFEQ)
    else:
        assert False


#   |[Имя "."] Имя ["(" [Параметр {"," Параметр}] ")"]
def CallStatement(x):
    # x - процедура или модуль
    skip(Lex.NAME)
    if scan.lex == Lex.DOT:
        if type(x) != items.Module:
            error.expect("имя модуля слева от точки")
        scan.nextLex()
        check(Lex.NAME)
        key = x.name + '.' + scan.name
        x = table.find(key)
        if type(x) != items.Proc:
            error.expect("процедура")
        scan.nextLex()
    elif type(x) != items.Proc:
        error.expect("имя процедуры")


    if scan.lex == Lex.LPAR:
        scan.nextLex()
        Procedure(x)
        skip(Lex.RPAR)
    elif x.name == "Out.Ln":
        Gen(cm.LN)
    elif x.name not in {"Out.Ln", "In.Open"}:
        error.expect("Out.Ln или In.Open")

        #else:
        #    scan.nextLex()  # закрывающая скобка


#   Переменная ":=" Выраж
#   |[Имя "."] Имя ["(" [Параметр {"," Параметр}] ")"]
def AssOrCall():
    check(Lex.NAME)
    x = table.find(scan.name)
    if type(x) == items.Var:
        AssStatement(x)
    #if scan.lex == Lex.ASS:
        #scan.nextLex()
        #skip(Lex.ASS)
        #Expression()
    elif type(x) == items.Proc or type(x) == items.Module:
        CallStatement(x)
    #else:
        #if scan.lex == Lex.DOT:
        #    scan.nextLex()
        #    skip(Lex.NAME)
        #if scan.lex == Lex.LPAR:
        #    scan.nextLex()
        #    if scan.lex != Lex.RPAR:
        #        Parameter()
        #        while scan.lex == Lex.COMMA:
        #            scan.nextLex()
        #            Parameter()
        #        skip(Lex.RPAR)
        #    else:
        #        scan.nextLex()  # закрывающая скобка
    else:
        error.expect("имя переменной или процедуры")


#   IF Выраж THEN
#      ПослОператоров
#   {ELSIF Выраж THEN
#      ПослОператоров}
#   [ELSE
#      ПослОператоров]
#    END
def IfStatement():
    skip(Lex.IF)
    BoolExpr()
    CondPC = gen.PC
    LastGOTO = 0
    skip(Lex.THEN)
    StatSeq()
    while scan.lex == Lex.ELSIF:
        Gen(LastGOTO)
        Gen(cm.GOTO)
        LastGOTO = gen.PC
        fixup(CondPC, gen.PC)
        scan.nextLex()
        BoolExpr()
        CondPC = gen.PC
        skip(Lex.THEN)
        StatSeq()
    if scan.lex == Lex.ELSE:
        Gen(LastGOTO)
        Gen(cm.GOTO)
        LastGOTO = gen.PC
        fixup(CondPC, gen.PC)
        scan.nextLex()
        StatSeq()
    else:
        fixup(CondPC, gen.PC)
    skip(Lex.END)
    fixup(LastGOTO, gen.PC)



# проверить, что выражение логического типа
def TestBool(T):
    if T != Types.Bool:
        error.expect("логическое выражение")


def BoolExpr():
    T = Expression()
    TestBool(T)


#    WHILE Выраж DO
#      ПослОператоров
#    END
def WhileStatement():
    WhilePC = gen.PC
    skip(Lex.WHILE)
    BoolExpr()
    CondPC = gen.PC
    skip(Lex.DO)
    StatSeq()
    skip(Lex.END)
    Gen(WhilePC)
    Gen(cm.GOTO)
    # vm.M[CondPC - 2] = gen.PC
    fixup(CondPC, gen.PC)   # адресная привязка


#[
#   Переменная ":=" Выраж
#   |[Имя "."] Имя ["(" [Параметр {"," Параметр}] ")"]
#   |IF Выраж THEN
#      ПослОператоров
#   {ELSIF Выраж THEN
#      ПослОператоров}
#   [ELSE
#      ПослОператоров]
#    END
#   |WHILE Выраж DO
#      ПослОператоров
#    END
#].
def Statement():
    if scan.lex == Lex.NAME:
        AssOrCall()
    elif scan.lex == Lex.IF:
        IfStatement()
    elif scan.lex == Lex.WHILE:
        WhileStatement()


#   Оператор {";" Оператор }.
def StatSeq():
    Statement()
    while scan.lex == Lex.SEMI:
        scan.nextLex()
        Statement()


def AllocVars():
    vars = table.getVars()
    for v in vars:
        if v.addr > 0:
            fixup(v.addr, gen.PC)
            Gen(0)
        else:
            error.Warning("Переменная " + v.name + " объявлена, но не используется")


#   MODULE Имя ";"
#   [Импорт]
#   ПослОбъявл
#   [BEGIN
#      ПослОператоров]
#   END Имя ".".
def Module():
    skip(Lex.MODULE)
    if scan.lex == Lex.NAME:
        table.new(items.Module(scan.name))
        scan.nextLex()
    else:
        error.expect("Ожидается имя")
    #skip(Lex.NAME)
    skip(Lex.SEMI)
    if scan.lex == Lex.IMPORT:
        Import()
    DeclSeq()
    if scan.lex == Lex.BEGIN:
        scan.nextLex()
        StatSeq()
    skip(Lex.END)
    check(Lex.NAME)
    x = table.find(scan.name)
    if type(x) != items.Module:
        error.expect("имя модуля")
    elif x.name != scan.name:
        error.expect("имя модуля" + scan.name)
    scan.nextLex()
    skip(Lex.DOT)
    Gen(cm.STOP)
    AllocVars()


# основная функция компилятора
def Compile():
    text.nextCh()   # читаем первый символ
    scan.nextLex()  # читаем первую лексему

    table.OpenScope()   # Блок стандартных идентификаторов
    table.add(items.Type("INTEGER", Types.Int))
    table.add(items.Func("ODD", Types.Bool))
    table.add(items.Func("ABS", Types.Int))
    table.add(items.Func("MAX", Types.Int))
    table.add(items.Func("MIN", Types.Int))
    table.add(items.Proc("HALT"))
    table.add(items.Proc("INC"))
    table.add(items.Proc("DEC"))
    table.add(items.Proc("In.Open"))
    table.add(items.Proc("In.Int"))
    table.add(items.Proc("Out.Int"))
    table.add(items.Proc("Out.Ln"))

    table.OpenScope()   # Блок модуля

    Module()

    table.CloseScope()  # Закрытие блока модуля
    table.CloseScope()  # Закрытие блока стандартных идентификаторов
