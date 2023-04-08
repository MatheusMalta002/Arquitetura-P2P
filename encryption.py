import nacl.signing as ECC_Ed25519
from Cryptodome.Cipher import ARC4 as RC4


class Encryption:

    def __init__(self, key):
        self.key = key  # chave única para o funcionamento do rc4
        self.chave_privada = ECC_Ed25519.SigningKey.generate()  # chave privada
        self.chave_publica = self.chave_privada.verify_key.encode()  # chave pública

    """Método para criptografar as mensagens usando o RC4 e assiná-las usando o ECC Ed25519"""

    def encrypt(self, plaintext):
        # cria a instancia do algoritmo de criptografia simétrica RC4
        cipher = RC4.new(self.key)

        # Passa a mensagem em texto plano para ser criptografada
        ciphertext = cipher.encrypt(plaintext)

        # utiliza a chave privada do par para assinar a mensagem
        mensagem_assinada = self.chave_privada.sign(ciphertext).signature

        # Retorna a mensagem assinada e o texto criptografado
        return mensagem_assinada + ciphertext

    """Método para descriptografar e verificar assinatura"""

    def decrypt(self, mensagem_criptografada, chave_publica):

        # separa a assinatura da mensagem cifrada
        mensagem_assinada = mensagem_criptografada[:64]

        ciphertext = mensagem_criptografada[64:]

        # utiliza a chave publica do remetente para verificar a autenticidade da mensagem
        chave_verificacao = ECC_Ed25519.VerifyKey(chave_publica)

        # se a verificação tiver sucesso o acesso a mensagem é permitido
        try:

            chave_verificacao.verify(mensagem_assinada + ciphertext)

            cipher = RC4.new(self.key)

            plaintext = cipher.decrypt(ciphertext)

            return plaintext

        # caso a verificação falhe um erro é lançado
        except ECC_Ed25519.exceptions.BadSignatureError:

            raise ValueError('A mensagem não pode ser autenticada.')