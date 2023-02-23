# Генератор кода
import vm
import vm as cm
from scan import Lex

PC = 0      #Счетчик команд времени компиляции


def Gen(cmd):
    global PC
    vm.M[PC] = cmd
    PC += 1


def GenConst(c):
    Gen(abs(c))
    if c < 0:
        Gen(cm.NEG)


# генерируем адрес переменной
def GenAddr(v):
    Gen(v.addr)
    v.addr = PC + 1


# генерация кода для сравнения
def GenComp(op):
    Gen(0)
    if op == Lex.EQ:
        Gen(cm.IFNE)
    elif op == Lex.NE:
        Gen(cm.IFEQ)
    elif op == Lex.GE:
        Gen(cm.IFLT)
    elif op == Lex.GT:
        Gen(cm.IFLE)
    elif op == Lex.LE:
        Gen(cm.IFGT)
    elif op == Lex.LT:
        Gen(cm.IFGE)


# Фиксируем наверху (записываем в ячейку памяти наверху)
def fixup(A, PC):
    while A > 0:
        temp = vm.M[A - 2]
        vm.M[A - 2] = PC
        A = temp

