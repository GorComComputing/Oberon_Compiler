# Генератор кода
import vm
import vm as cm

PC = 0      #Счетчик команд времени компиляции


def Gen(cmd):
    global PC
    vm.M[PC] = cmd
    PC += 1


def GenConst(c):
    Gen(abs(c))
    if c < 0:
        Gen(cm.NEG)


def GenAddr(v):
    Gen(100)    # Заглушка
