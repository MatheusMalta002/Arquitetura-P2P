seed = ("127.0.0.1",8891)


# O nó semente (também conhecido como bootstrap node) é um nó especial na rede P2P que
# é usado para ajudar outros nós a se conectar entre si. É responsável por manter uma 
# lista de pares (também chamados de nós) que estão atualmente na rede e por responder a
# consultas de novos nós que desejam ingressar na rede. Quando um novo nó entra na rede
# ele envia uma mensagem para o nó semente, que responde com a lista atualizada de pares 
# na rede. Isso permite que o novo nó se conecte com outros nós e comece a enviar e receber 
# mensagens. Sem o nó semente, os nós teriam que descobrir uns aos outros por conta própria,
# o que seria difícil em uma rede grande e dinâmica.