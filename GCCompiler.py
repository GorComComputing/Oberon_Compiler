#Компилятор Oberon

import pars
import text
import vm
import gen


# Дизассемблер Python
# import dis
# dis.dis(gen)


print("Компилятор языка Oberon")
text.Reset()
# Запуск компилятора
pars.Compile()
print("\nКомпиляция завершена")
vm.printCode(gen.PC)
# Запуск виртуальной машины
vm.Run()



