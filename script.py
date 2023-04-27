# import os
# Comando para linux

# from subprocess import call
# from subprocess import Popen
# import time
# for i in range(4):
#     command = 'python main.py 889{} id{}'.format(i+1,i+1)
#     # can't create peers too fast. 
#     time.sleep(0.2) 
#     Popen(['xterm','-e',command])

# comando para windows

import os
import time
from p2p import P2P_Node
import pyautogui

for i in range(3):
    command = 'python p2p.py --port 889{} --user id{}'.format(i+1,i+1)
    # can't create peers too fast. 
    time.sleep(0.2) 
    os.system('start cmd /k "{}"'.format(command))

    

#     # aguarda 1 segundo para garantir que a janela do terminal esteja aberta
# time.sleep(1)

# # digita a mensagem "oi" no terminal do nó P2P
# pyautogui.typewrite("oi")
# pyautogui.press("enter")



"""
Essa pasta serve apenas para iniciar 4 pares de uma vez

Basta executar a pasta ex: --> python script.py

"""

