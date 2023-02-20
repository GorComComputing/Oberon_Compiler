#Компилятор Gor.Com Compiller

import pars
import text
import vm
import loader
from programs import *


def Init():
    text.Reset()


# не используется
def Done():
    pass


print("Компилятор \"Gor.Com Compiller\"")
Init()

# Запуск компилятора
pars.Compile()
print("\nКомпиляция завершена")

#vm.M[0] = 100
#vm.M[1] = 10
#vm.M[2] = vm.OUT

# Загрузка программы в машинном коде
#loader.Load(c3c)
#loader.Load(I_Kruglov)

# Запуск виртуальной машины
vm.Run()

Done()  # не используется
