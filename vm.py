# Виртуальная машина
import error

# Команды виртуальной машины
STOP = -1
ADD  = -2
SUB  = -3
MULT = -4
DIV  = -5
MOD  = -6
NEG  = -7
LOAD = -8
SAVE = -9
DUP  = -10
DROP = -11
SWAP = -12
OVER = -13
GOTO = -14
IFLT = -15
IFLE = -16
IFGT = -17
IFGE = -18
IFEQ = -19
IFNE = -20
IN   = -21
OUT  = -22
LN   = -23


#Память
MEM_SIZE = 8*1024   # 8 килослов
M = [STOP]*MEM_SIZE # Память по умолчанию заполнена командами STOP

# Мнемоника
_mnemo = [
    "",
    "STOP",
    "ADD",
    "SUB",
    "MULT",
    "DIV",
    "MOD",
    "NEG",
    "LOAD",
    "SAVE",
    "DUP",
    "DROP",
    "SWAP",
    "OVER",
    "GOTO",
    "IFLT",
    "IFLE",
    "IFGT",
    "IFGE",
    "IFEQ",
    "IFNE",
    "IN",
    "OUT",
    "LN"
]


# Процессор виртуальной машины
def Run():
    PC = 0
    SP = MEM_SIZE
    cnt = 0     # Счетчик тактов
    while True:
        cnt += 1
        cmd = M[PC]
        PC += 1
        if cmd >= 0:
            SP -= 1
            M[SP] = cmd
        elif cmd == ADD:
            SP += 1
            M[SP] = M[SP] + M[SP - 1]
        elif cmd == SUB:
            SP += 1
            M[SP] = M[SP] - M[SP - 1]
        elif cmd == MULT:
            SP += 1
            M[SP] = M[SP] * M[SP - 1]
        elif cmd == DIV:
            SP += 1
            M[SP] = M[SP] // M[SP - 1]
        elif cmd == MOD:
            SP += 1
            M[SP] = M[SP] % M[SP - 1]
        elif cmd == NEG:
            M[SP] = -M[SP]
        elif cmd == LOAD:
            M[SP] = M[M[SP]]
        elif cmd == SAVE:
            M[M[SP+1]] = M[SP]
            SP += 2
        elif cmd == DUP:
            M[SP-1] = M[SP]
            SP -= 1
        elif cmd == DROP:
            SP += 1
        elif cmd == SWAP:
            temp = M[SP]
            M[SP] = M[SP+1]
            M[SP+1] = temp
        elif cmd == OVER:
            M[SP-1] = M[SP+1]
            SP -= 1
        elif cmd == GOTO:
            PC = M[SP]
            SP += 1
        elif cmd == IFEQ:
            if M[SP+2] == M[SP+1]:
                PC = M[SP]
            SP += 3
        elif cmd == IFNE:
            if M[SP+2] != M[SP+1]:
                PC = M[SP]
            SP += 3
        elif cmd == IFLT:
            if M[SP+2] < M[SP+1]:
                PC = M[SP]
            SP += 3
        elif cmd == IFLE:
            if M[SP+2] <= M[SP+1]:
                PC = M[SP]
            SP += 3
        elif cmd == IFGT:
            if M[SP+2] > M[SP+1]:
                PC = M[SP]
            SP += 3
        elif cmd == IFGE:
            if M[SP+2] >= M[SP+1]:
                PC = M[SP]
            SP += 3
        elif cmd == IN:
            SP -= 1
            try:
                M[SP] = int(input("?"))
            except:
                error.Error("Неправильный ввод")
        elif cmd == OUT:
            print(f"{M[SP+1]:{M[SP]}}", end="")
            SP += 2
        elif cmd == LN:
            print()
        elif cmd == STOP:
            break
        else:
            error.Error("Недопустимая команда")

    print("Количество тактов", cnt)

    # Если в стеке что-то сталось, то выводит
    if SP < MEM_SIZE:
        print("Код возврата", M[SP])


# Печатает сгенерированный код
def printCode(PC):
    for pc in range(0, PC):
        print(pc, ') ', M[pc] if M[pc] >= 0 else _mnemo[-M[pc]])






