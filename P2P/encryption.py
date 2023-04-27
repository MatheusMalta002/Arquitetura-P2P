import hashlib #importa biblioteca de hash para usar sha3_512
import nacl.signing as ECC_Ed25519
from Cryptodome.Cipher import ARC4 as RC4
import random

"""Classe utilizada para garantir confidencialidade, autenticidade e integridade"""

class Encryption:

    def __init__(self):
        self.key = None # chave única para o funcionamento do rc4
        self.chave_privada = ECC_Ed25519.SigningKey.generate()  # chave privada
        self.chave_publica = self.chave_privada.verify_key.encode()  # chave pública

    """Método para criptografar as mensagens usando o RC4, assiná-las usando o ECC Ed25519 e verificar integridade com hash SHA3_512"""

    def encrypt(self, plaintext):
        # cria a instancia do algoritmo de criptografia simétrica RC4
        cipher = RC4.new(self.key)

        # Passa a mensagem em texto plano para ser criptografada
        ciphertext = cipher.encrypt(plaintext)

        # calcula o hash da mensagem criptografada
        ciphertext_hash = hashlib.sha3_512(ciphertext).digest()

        # utiliza a chave privada do par para assinar a mensagem e o hash da mensagem
        mensagem_assinada = self.chave_privada.sign(ciphertext + ciphertext_hash).signature

        # Retorna a mensagem assinada, o texto criptografado e o hash da mensagem
        return mensagem_assinada + ciphertext + ciphertext_hash

    """Método para descriptografar e verificar assinatura e verificar se houve alteração na hash."""

    def decrypt(self, mensagem_criptografada, chave_publica):

        # separa a assinatura, a mensagem cifrada e o hash da mensagem
        mensagem_assinada = mensagem_criptografada[:64]

        ciphertext = mensagem_criptografada[64:-64]
        
        ciphertext_hash = mensagem_criptografada[-64:]

        # utiliza a chave publica do remetente para verificar a autenticidade da mensagem e do hash
        chave_verificacao = ECC_Ed25519.VerifyKey(chave_publica)

        # se a verificação tiver sucesso o acesso a mensagem é permitido
        try:
            chave_verificacao.verify(mensagem_assinada + ciphertext + ciphertext_hash)

            # verifica o hash da mensagem criptografada
            if ciphertext_hash != hashlib.sha3_512(ciphertext).digest():

                raise ValueError('A mensagem foi adulterada')

            cipher = RC4.new(self.key)
        
            plaintext = cipher.decrypt(ciphertext)

            return plaintext

        # caso a verificação falhe um erro é lançado
        except ECC_Ed25519.exceptions.BadSignatureError:

            raise ValueError('A mensagem não pode ser autenticada.')
        
    def set_key(self, key):
        self.key = key


"""Classe Diffie Hellman para troca de chaves segura"""

class DiffieHellman:

    def __init__(self, p, g):
        self.p = p
        self.g = g
        self.a = random.randint(1, p-1)
        self.A = pow(g, self.a, p)
        self.secret_key = None
    
    # gerar a chave secreta compartilhada
    def generate_secret_key(self, B):
        self.secret_key = pow(B, self.a, self.p)

    #retornar a chave pública 
    def get_public_key(self):
        return self.A

    #retornar a chave secreta gerada de antemão
    def get_secret_key(self):
        return self.secret_key

"""

Explicação sobre a implementação do Diffie Hellman

#------------------#
#Sobre o valor [p] #
#------------------#

O valor de p é um número primo que é compartilhado entre os usuários. 
Ele é usado para definir o espaço de operação do algoritmo, ou seja, 
define o conjunto de valores possíveis que podem ser usados para gerar
as chaves privadas e públicas. Esse valor não é secreto e pode ser 
conhecido por qualquer pessoa, sem comprometer a segurança do algoritmo.

#------------------#
#sobre o valor [g] #
#------------------#

O valor de g é chamado de gerador e é um número inteiro que é escolhido de
forma aleatória dentro do intervalo [1, p-1]. Esse valor também é público e
 pode ser compartilhado sem comprometer a segurança do algoritmo.

O valor de p e g são valores públicos que são compartilhados pelos usuários
e podem ser enviados através de um canal não seguro sem comprometer a segurança
 do esquema Diffie-Hellman.

#------------#
#Explicação: #
#------------#

O construtor da classe recebe os dois parâmetros (p e g), que são os valores públicos
compartilhados pelos usuários. Ele também gera um número aleatório a entre 1 e p-1, 
que é o segredo privado do usuário.

O método {generate_secret_key} recebe o valor público (B / chave pública do outro par)
enviado pelo outro usuário e calcula a chave secreta compartilhada usando a fórmula B^a mod p.

Os métodos [get_public_key] e (get_secret_key) retornam, respectivamente, a [chave pública A]
 gerada pelo usuário e a (chave secreta compartilhada).

"""