import socket
import threading
import sys
import json

"""As mensagens foram serializadas usando json para
   poder enviar mensagens mais complexas como dicionários
   e arrays.
"""

# Função para enviar mensagem como string para um endereço
def enviar_mensagem_base(udp_socket, toA, mensagem):
    udp_socket.sendto(mensagem.encode(), (toA[0], toA[1]))


# Função para receber mensagem e retornar mensagem e endereço
def receber_mensagem_base(udp_socket):
    data, addr = udp_socket.recvfrom(1024)
    return data.decode(), addr


# Função para enviar mensagem como JSON para um endereço
def enviar_mensagem_JSON(udp_socket, toA, mensagem):
    enviar_mensagem_base(udp_socket, toA, json.dumps(mensagem))


# Função para enviar mensagem para vários peers
def broadcast_mensagem_base(udp_socket, mensagem, peers):
    for p in peers.values():
        enviar_mensagem_base(udp_socket, p, mensagem)


# Função para enviar mensagem como JSON para vários peers
def broadcast_mensagem_JSON(udp_socket, mensagem, peers):
    for p in peers.values():
        enviar_mensagem_JSON(udp_socket, p, mensagem)


def broadcast_mensagem_JSON_exclui_user(udp_socket, mensagem, user, peers):
    remetente = str(user)

    if remetente in peers:
        del peers[remetente]
    else:
        pass

    for p in peers.values():
        enviar_mensagem_JSON(udp_socket, p, mensagem)


# Thread para receber mensagens
def receber(udp_socket):
    while 1:
        data, addr = receber_mensagem_base(udp_socket)
        print(data)


# Thread para enviar mensagens
def enviar(udp_socket):
    while 1:
        msg = input("Por favor, digite a mensagem e a porta:")
        l = msg.split()
        porta = int(l[-1])
        s = ' '.join(l[:-1])
        toA = ('127.0.0.1', porta)
        enviar_mensagem_base(udp_socket, toA, s)


def main():
    porta = int(sys.argv[1])  # Obtém a porta a partir da linha de comando
    fromA = ("127.0.0.1", porta)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((fromA[0], fromA[1]))
    t1 = threading.Thread(target=receber, args=(udp_socket,))
    t2 = threading.Thread(target=enviar, args=(udp_socket,))
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()