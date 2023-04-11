<h1>Projeto de Redes 💻</h1>
</br>
<h2>Projeto 1: Segurança numa Arquitetura P2P</h2>

<h3>Objetivos do projeto:</h3>

<li> Implementar uma arquitetura P2P </li>
<li> Implementar  Segurança na comunicação P2P</li>
<li> Garantir Autenticidade </li>
<li> Garantir Confidencialidade</li>
<li> Garantir Integridade</li>

<h3>Algoritmos utilizados na Segurança:</h3>
<li> Algoritmo de chave simétrica RC4 para criptografia</li>
<li> Algoritmo de chave assimétrica ECC Ed25519 para assinatura de mensagem</li>
<li> Hash SHA3_512 para verificação de integridade da mensagem</li>
<li> Algoritmo Diffie Hellman para troca de chaves seguras</li>


<h3>Diagrama utilizado para implementar o P2P:</h3>

![p2pChatRoom_image](https://user-images.githubusercontent.com/104574086/231212163-8538a19d-edef-45df-9706-7863ae5f1b38.png)

<h3>Sobre a implementação do P2P:</h3>

<p>Para a implementação do P2P foi utilizado um diagrama como referencia.
O nó semente (também conhecido como bootstrap node) é um nó especial na rede P2P que
é usado para ajudar outros nós a se conectar entre si. É responsável por manter uma 
lista de pares (também chamados de nós) que estão atualmente na rede e por responder a
consultas de novos nós que desejam ingressar na rede. Quando um novo nó entra na rede
ele envia uma mensagem para o nó semente, que responde com a lista atualizada de pares 
na rede. Isso permite que o novo nó se conecte com outros nós e comece a enviar e receber 
mensagens. Sem o nó semente, os nós teriam que descobrir uns aos outros por conta própria,
o que seria difícil em uma rede grande e dinâmica.Esse nó semente também é responsável por atualiar
os dicionários de pares e os dicionários de chaves púbicas.</p>


<h3>Nota:</h3>

<p>Essa implementação de segurança é apenas para fins educacionais,
uma implementação de segurança real não trabalha exatamente da forma
que foi implementada nesse projeto e, além disso, utiliza algoritmos
mais confiáveis atualmente. Como exemplo, atualmente não se utiliza 
mais o RC4, já que descobriram que ele é um algoritmo não confiável
que permite ataques.</p>




