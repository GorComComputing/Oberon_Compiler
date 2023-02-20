# Загрузчик программ

from vm import M


def Load(p):
    for pc, cmd in enumerate(p):
        M[pc] = cmd
