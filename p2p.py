import threading
import socket
import json
import time
from P2P import udp as UDP
from P2P import encryption
from P2P import  config
import argparse
from prettytable import PrettyTable


class P2P_Node:

    def __init__(self):
        self.seed = config.seed
        self.pares = {}
        self.udp_socket = {}
        self.chaves_publicas_ECC_Ed25519 = {}
        self.chaves_publicas_Diffie_Hellman = {}
        self.myid = ""
        self.primo = 23
        self.gerador = 5
        self.dh = encryption.DiffieHellman(self.primo, self.gerador)
        self.encrypt = encryption.Encryption()
        self.dicionario_msgs = {}

    """Método para receber as mensagens"""

    def receive(self):

        while 1:

            data, addr = UDP.receber_mensagem_base(self.udp_socket)
            acao = json.loads(data)

            if acao['Tipo'] == 'Novo_Par':
                public_key = acao['public_key']
                public_key_diffie_hellman = acao['Diffie_Hellman_key']

                # adiciona o endereço socket ao dicionário pares
                self.pares[acao['data']] = addr

                # adiciona a chave pública ao dicionário de chaves publicas ECC_Ed25519
                self.chaves_publicas_ECC_Ed25519[acao['data']] = public_key

                # adiciona a chave pública diffie hellman ao dicionário de chaves diffie_hellman
                self.chaves_publicas_Diffie_Hellman[acao['data']] = public_key_diffie_hellman

                # envia o dicionário de pares e de chaves públicas destinatario que os outros pares se atualizem
                UDP.enviar_mensagem_JSON(self.udp_socket, addr, {
                    "Tipo": 'pares',
                    "data": self.pares,
                    "public_key": public_key,
                    "public_key_DH": public_key_diffie_hellman,
                    "dict_key": self.chaves_publicas_ECC_Ed25519,
                    "dict_key_DH": self.chaves_publicas_Diffie_Hellman
                })

            if acao['Tipo'] == 'pares':

                # atualiza o dicinário de pares
                self.pares.update(acao['data'])

                # atualiza o dicionário de chaves publicas
                self.chaves_publicas_ECC_Ed25519.update(acao['dict_key'])

                # atualiza o dicionário diffie hellman
                self.chaves_publicas_Diffie_Hellman.update(acao["dict_key_DH"]) 

                public_key = acao['public_key']
                public_key_DH = acao['public_key_DH']

                UDP.broadcast_mensagem_JSON(self.udp_socket, {
                    "Tipo": "introduzir",
                    "data": self.myid,
                    "public_key": public_key,
                    "public_key_DH": public_key_DH
                }, self.pares)

            if acao['Tipo'] == 'introduzir':

                if acao['data'] == self.myid:
                    print("\nVocê entrou no chat\n")
                else:
                    print(acao['data'] + " entrou no chat\n")

                self.pares[acao['data']] = addr
                self.chaves_publicas_ECC_Ed25519[acao['data']] = acao['public_key']
                self.chaves_publicas_Diffie_Hellman[acao['data']] = acao['public_key_DH']

            if acao['Tipo'] == 'input':
                # Recebe a mensagem criptografada e com a assinatura do remetente
                mensagem_criptada_assinada = acao['data'].encode('latin-1')

                time.sleep(0.1)

                timestamp_depois = time.time()

                 # calcula o tamanho em bytes da mensagem
                tamanho_mensagem_bytes = len(mensagem_criptada_assinada)

                # O id do remetente que ele mandou
                id_remetente = str(acao['id_remetente'])

                # pega a chave pública diffie hellman do remetente 
                chave_remetente_diffie_hellman = self.chaves_publicas_Diffie_Hellman[id_remetente]

                # gera sua chave compartilhada usando a chave pública do remetente
                self.dh.generate_secret_key(chave_remetente_diffie_hellman)

                # guarda a chave compartilhada em uma variável
                shared_key = self.dh.get_secret_key()

                # converte a chave para uma sequencia de bytes pois a chave 
                # a ser colocada no RC4 é em bytes
                shared_key_bytes = shared_key.to_bytes(16, 'big')

                # coloca a chave no RC4 para descriptogrfar
                self.encrypt.set_key(shared_key_bytes)

                # pega a chave publica do remetente destinatario verificar a assinatura
                chave_publica_remetente = self.chaves_publicas_ECC_Ed25519[id_remetente].encode('latin-1')

                tempo_descriptografar_inicial = time.time()
                # descriptografa a mensagem e verifica a assinatura
                msg_verificada = self.encrypt.decrypt(mensagem_criptada_assinada, chave_publica_remetente)

                time.sleep(0.1)

                tempo_descriptografar_final = time.time()

                tempo_total_descriptografia = tempo_descriptografar_final - tempo_descriptografar_inicial

                #tempo no inicio de envio do pacote
                timestamp_antes = acao['timestamp']

                #tempo de transmissão = valor do tempo quando chegou - o inicial
                tempo_transmissao = timestamp_depois - timestamp_antes

                #Daqui para baixo imprime as informações no terminal

                infos = PrettyTable()

                infos.field_names = ["Tamanho do Pacote", "Tempo de Transmissão", "Tempo de Criptografia", "Tempo para Descriptografar", "Tempo Total Gasto"]

                tamanho_msg_bytes = f'{tamanho_mensagem_bytes} bytes'

                tempo_transm = f'{tempo_transmissao:.4f} segundos.'

                tempo_criptografia = f"{acao['tempo_criptografia']:.4f} segundos."

                tempo_descriptografia = f'{tempo_total_descriptografia:.4f} segundos'

                tempo_total_gasto = f"{tempo_transmissao + tempo_total_descriptografia + acao['tempo_criptografia']:.4f} segundos."

                infos.add_row([tamanho_msg_bytes, tempo_transm, tempo_criptografia, tempo_descriptografia, tempo_total_gasto])

                # imprime a mensagem
                print(f'\n{id_remetente}: {msg_verificada.decode()}\n')

                #imprime a tabela com os tempos
                time.sleep(1)
                print(f'{infos}\n')
            

            if acao['Tipo'] == 'sair':
                if (self.myid == acao['data']):
                    time.sleep(0.5)
                    break;

                value, key = self.pares.pop(acao['data'])
                print(f"\n{acao['data']} saiu do chat.")


    """Método para iniciar o par e usar o nó seed para atualizar os outros pares"""

    def startpeer(self):

        #Cria a chave pública do algoritmo ECC_Ed25519
        chave_publica = self.encrypt.chave_publica

        #Cria a chave pública Diffie Hellman
        public_key_diffie_hellman = self.dh.get_public_key()

        #Envia a chave pública para o nó semente que manda para os outros pares
        UDP.enviar_mensagem_JSON(self.udp_socket, self.seed, {
            "Tipo": "Novo_Par",
            "data": self.myid,
            "public_key": chave_publica.decode('latin-1'),
            "Diffie_Hellman_key": public_key_diffie_hellman
        })

    
    """Método para enviar as mensagens"""

    def send(self):

        while 1:
            msg_input = input(">> ")

            if msg_input == '' or msg_input == None:
                print(f"\nDigite alguma coisa antes de enviar !!!\n")
                continue

            #sai do chat
            if msg_input == "sair":
                UDP.broadcast_mensagem_JSON(self.udp_socket, {
                    "Tipo": "sair",
                    "data": self.myid
                }, self.pares)
                break
            
            #imprime os pares conectados no chat
            if msg_input == "amigos":
                print(self.pares)
                continue
            
            #Manda a mensagem para um usuário específico
            msg = msg_input.split()
            if msg[-1] in self.pares.keys():

                destinatario = self.pares[msg[-1]]

                #pega o identificador do destinatário
                id_destinatario = str(msg[-1])

                # pega a chave pública diffie hellman do destinatário no dicionário de chaves
                chave_destinatario_diffie_hellman = self.chaves_publicas_Diffie_Hellman[id_destinatario]

                #usa a chave pública do destinatário para gerar a mesma chave compartilhada que o dest.
                self.dh.generate_secret_key(chave_destinatario_diffie_hellman)
                
                # guarda a chave compartilhada em uma variável
                shared_key = self.dh.get_secret_key()

                # converte a chave para uma sequencia de bytes
                shared_key_bytes = shared_key.to_bytes(16, 'big')

                # usa a chave compartilhada no RC4 para criptografar
                self.encrypt.set_key(shared_key_bytes)

                # mensagem sem criptografia
                texto_plano = ' '.join(msg[:-1])

                tempo_criptografia_inicial = time.time()

                #criptografa a mensagem usando a combinação dos algoritmos RC4, ECC_Ed25519 E SHA3_512
                msg_criptada_assinada = self.encrypt.encrypt(texto_plano.encode('utf-8'))

                time.sleep(0.1)

                tempo_criptografia_final = time.time()

                tempo_total_criptografia = tempo_criptografia_final - tempo_criptografia_inicial

                timestamp_antes = time.time()

                #envia a mensagem para o usário específico
                UDP.enviar_mensagem_JSON(self.udp_socket, destinatario, {
                    "Tipo": "input",
                    "data": msg_criptada_assinada.decode('latin-1'),
                    "id_remetente": self.myid,
                    "timestamp": timestamp_antes,
                    "tempo_criptografia": tempo_total_criptografia
                })

            #Manda a mensagem criptografada para todos os usuários de uma só vez
            else:

                for Id in self.pares:

                    chave_destinatario = self.chaves_publicas_Diffie_Hellman[str(Id)]

                    self.dh.generate_secret_key(chave_destinatario)

                    shared_key = self.dh.get_secret_key()

                    shared_key_bytes = shared_key.to_bytes(16, 'big')

                    self.encrypt.set_key(shared_key_bytes)

                    tempo_criptografia_inicial = time.time()

                    msg_criptada_assinada = self.encrypt.encrypt(msg_input.encode('utf-8'))

                    time.sleep(0.1)

                    tempo_criptografia_final = time.time()

                    tempo_total_criptografia = tempo_criptografia_final - tempo_criptografia_inicial

                    msg_final = msg_criptada_assinada.decode('latin-1')

                    self.dicionario_msgs[str(Id)] = msg_final

                    timestamp_antes = time.time()

                #envia a mensagem para todos os usários exceto o próprio
                UDP.broadcast_mensagem_JSON_exclui_user(self.udp_socket, {
                    "Tipo": "input",
                    "data": msg_input,
                    "id_remetente": self.myid,
                    "timestamp": timestamp_antes,
                    "tempo_criptografia": tempo_total_criptografia
                }, self.myid, self.pares, self.dicionario_msgs)
                continue


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', dest='port', type=int, required=True, help='A porta a ser usada')
    parser.add_argument('--user', dest='user_id', type=str, required=True, help='O ID do usuário')
    args = parser.parse_args()

    fromA = ("127.0.0.1", args.port)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((fromA[0], fromA[1]))
    peer = P2P_Node()
    peer.myid = args.user_id
    peer.udp_socket = udp_socket
    peer.startpeer()
    t1 = threading.Thread(target=peer.receive, args=())
    t2 = threading.Thread(target=peer.send, args=())

    t1.start()
    time.sleep(1) #aguarda 1 segundo para poder receber entrada 
    t2.start()


if __name__ == '__main__':
    main()

# Uso no terminal

# python @nome_do_arquivo @porta @id1

# exemplo:

# python main.py 8891 Matheus
