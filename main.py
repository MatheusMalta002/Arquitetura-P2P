import threading
import socket
import sys
import json
import time
import udp as UDP
from encryption import Encryption
from config import seed


class P2P_Node:
    seed = seed
    pares = {}
    udp_socket = {}
    chaves_publicas = {}
    myid = ""

    def __init__(self):
        self.private_key = b'\x01\x23\x45\x67\x89\xAB\xCD\xEF\xFE\xDC\xBA\x98\x76\x54\x32\x10'
        self.encryption = Encryption(self.private_key)

    def receive(self):

        while 1:

            data, addr = UDP.receber_mensagem_base(self.udp_socket)
            acao = json.loads(data)

            if acao['Tipo'] == 'Novo_Par':
                public_key = acao['public_key']

                # adiciona o endereço socket ao dicionário pares
                self.pares[acao['data']] = addr

                # adiciona a chave pública ao dicionário de chaves publicas
                self.chaves_publicas[acao['data']] = public_key

                # envia o dicionário de pares e de chaves públicas para que os outros pares se atualizem
                UDP.enviar_mensagem_JSON(self.udp_socket, addr, {
                    "Tipo": 'pares',
                    "data": self.pares,
                    "public_key": public_key,
                    "dict_key": self.chaves_publicas
                })

            if acao['Tipo'] == 'pares':
                self.pares.update(acao['data'])  # atualiza o dicinário de pares
                self.chaves_publicas.update(acao['dict_key'])  # atualiza o dicionário de chaves publicas

                public_key = acao['public_key']

                UDP.broadcast_mensagem_JSON(self.udp_socket, {
                    "Tipo": "introduzir",
                    "data": self.myid,
                    "public_key": public_key,
                }, self.pares)

            if acao['Tipo'] == 'introduzir':

                if acao['data'] == self.myid:
                    print("\nVocê entrou no chat\n")
                else:
                    print(acao['data'] + " entrou no chat\n")

                self.pares[acao['data']] = addr
                self.chaves_publicas[acao['data']] = acao['public_key']

            if acao['Tipo'] == 'input':
                # Recebe a mensagem criptografada e com a assinatura do remetente
                mensagem_criptada_assinada = acao['data'].encode('latin-1')

                # O id do remetente que ele mandou
                id_remetente = str(acao['id_remetente'])

                # pega a chave publica do remetente para verificar a assinatura
                chave_publica_remetente = self.chaves_publicas[id_remetente].encode('latin-1')

                # descriptografa a mensagem e verifica a assinatura
                msg_verificada = self.encryption.decrypt(mensagem_criptada_assinada, chave_publica_remetente)

                # imprime a mensagem
                print(f'{id_remetente}: {msg_verificada.decode()}')

            if acao['Tipo'] == 'exit':
                if (self.myid == acao['data']):
                    time.sleep(0.5)
                    break;

                value, key = self.pares.pop(acao['data'])
                print(acao['data'] + " is left.")

    def startpeer(self):

        # Quando um par é criado sua chave pública é compartilhada com todos os pares
        chave_publica = self.encryption.chave_publica

        UDP.enviar_mensagem_JSON(self.udp_socket, self.seed, {
            "Tipo": "Novo_Par",
            "data": self.myid,
            "public_key": chave_publica.decode('latin-1')
        })

    def send(self):
        while 1:
            msg_input = input(">> ")
            if msg_input == "exit":
                UDP.broadcast_mensagem_JSON(self.udp_socket, {
                    "Tipo": "exit",
                    "data": self.myid
                }, self.pares)
                break
            if msg_input == "friends":
                print(self.pares)
                continue

            l = msg_input.split()
            if l[-1] in self.pares.keys():

                toA = self.pares[l[-1]]
                texto_plano = ' '.join(l[:-1])

                msg_criptada_assinada = self.encryption.encrypt(texto_plano.encode('utf-8'))

                UDP.enviar_mensagem_JSON(self.udp_socket, toA, {
                    "Tipo": "input",
                    "data": msg_criptada_assinada.decode('latin-1'),
                    "id_remetente": self.myid
                })

            else:

                msg_criptada_assinada = self.encryption.encrypt(msg_input.encode('utf-8'))

                UDP.broadcast_mensagem_JSON_exclui_user(self.udp_socket, {
                    "Tipo": "input",
                    "data": msg_criptada_assinada.decode('latin-1'),
                    "id_remetente": self.myid
                }, self.myid, self.pares)
                continue


def main():
    port = int(sys.argv[1])
    fromA = ("127.0.0.1", port)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((fromA[0], fromA[1]))
    peer = P2P_Node()
    peer.myid = sys.argv[2]
    peer.udp_socket = udp_socket
    peer.startpeer()
    t1 = threading.Thread(target=peer.receive, args=())
    t2 = threading.Thread(target=peer.send, args=())

    t1.start()
    time.sleep(1)
    t2.start()


if __name__ == '__main__':
    main()

# Uso no terminal

# python @nome_do_arquivo @porta @id1

# exemplo:

# python main.py 8891 Matheus
