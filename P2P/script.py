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
from main import P2P_Node

for i in range(3):
    command = 'python main.py --port 889{} --user id{}'.format(i+1,i+1)
    # can't create peers too fast. 
    time.sleep(0.2) 
    os.system('start cmd /k "{}"'.format(command))


"""
Essa pasta serve apenas para iniciar 4 pares de uma vez

Basta executar a pasta ex: --> python script.py

"""

