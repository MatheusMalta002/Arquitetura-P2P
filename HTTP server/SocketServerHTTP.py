import socket
import sys
import pathlib
from threading import Thread
import os

#----------------------- lista de acesso maximo:
# se o endereço estiver nessa lista ele vai poder acessar a "pagina secreta"
maximum_access_Addresses=[]

#-----------------------

text_file_type_array = ['html','css','js']
allowed_file_extensions =['html','css','js','py','svg','mp4','mp3','ppt','docx','pdf','png','jpg','gif','ico','txt']
#supported_binary_files = ['svg','png','jpeg','gif']
pasta_atual = pathlib.Path()
socket_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#----------------------- endereços do servidor:

sv_port = 9898
sv_addr ='0.0.0.0'
socket_server.bind((sv_addr,sv_port))
socket_server.listen(11)

#----------------------- Definindo a função das threads
def list_files_in_directory(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def generate_html_response(path):
    html_response = '<html><head><title>Directory Listing</title></head><body><h1>Index of {0}</h1><ul>'.format(path)
    
    for file in pathlib.Path(path).iterdir():
        if file.is_file():
            html_response += f'<li><a href="{file}">{file.name}</a></li>'
        elif file.is_dir():
            html_response += f'<li><a href="{file}">{file.name}/</a></li>'

    html_response += '</ul></body></html>'
    return html_response

def Server_Thread(socket_client,client_addr):

    print(f'Client {client_addr[0]} successfully connected on port:{client_addr[1]}')

    received_data= socket_client.recv(1024)
    received_data = received_data.decode()

    #----------------------- Quebrando o Header:

    headers_list = received_data.split('\r\n')
    GET_header = headers_list[0]

    ##----------------------- Erro 505:

    if 'HTTP/1.0' in GET_header:

        file = open(pasta_atual/'505.html','r',encoding='utf-8')
        file_content = file.read()

        answer_header = f'HTTP/1.0 505 Version not Supported\r\n\r\n'
        answer_body = file_content

        five_o_five_answer = answer_header + answer_body

        socket_client.sendall(five_o_five_answer.encode('utf-8'))
        socket_client.close()
        return False

    #----------------------- Procurando pelo Pacote Desejado:

    desired_file = GET_header.split(' ')[1][1:]
    print(f'GET file--> {desired_file}')
    #-----------------------
    # Se a página inicial for solicitada, gerar uma resposta HTML dinâmica com a lista de arquivos
    # if desired_file == '':
    #     html_response = '<html><head><title>Directory Listing</title></head><body><h1>Index of/</h1><ul>'

    #     for file in pathlib.Path().iterdir():

    #         if file.is_file():
    #             html_response += f'<li><a href="{file.name}">{file.name}</a></li>'

    #         elif file.is_dir():
    #             html_response +=f'<li><a href="{file.name}">{file.name}</a></li>'
            
    #     html_response += '</ul></body></html>'

    #     answer_header = f'HTTP/1.1 200 OK\r\n\r\n'
    #     answer_body = html_response

    #     socket_client.sendall((answer_header + answer_body).encode('utf-8'))
    #     socket_client.close()
    #     return
    #------------------------------------------------
    # if desired_file == '':
    #     #desired_file = '.'

    #     if os.path.isdir(desired_file):
    #         answer_header = f'HTTP/1.1 200 OK\r\n\r\n'
    #         answer_body = generate_html_response(desired_file)
    #     elif os.path.isfile(desired_file):
    #         answer_header = f'HTTP/1.1 200 OK\r\n\r\n'
    #         answer_body = generate_html_response(desired_file)

    #     socket_client.sendall((answer_header + answer_body).encode('utf-8'))
    #     socket_client.close()
    #     return False
#--------------------------------------
    path_file = pathlib.Path(desired_file)
    if path_file.exists() and path_file.is_dir():
        html_response = '<html><head><title>Directory Listing</title></head><body><h1>Index of/</h1><ul>'

        for file in path_file.iterdir():
            variavel_teste = file.name.split('/')[-1]
            if file.is_file():
                html_response += f'<li><a href="/{path_file/variavel_teste}">{file.name}</a></li>'

            elif file.is_dir():
                html_response += f'<li><a href="/{path_file/variavel_teste}">{file.name}</a></li>'
        html_response += '</ul></body></html>'

        answer_header = f'HTTP/1.1 200 OK\r\n\r\n'
        answer_body = html_response

        socket_client.sendall((answer_header + answer_body).encode('utf-8'))
        socket_client.close()
        return

#----------------------- Erro 400:

    #----------------------- Erro 400:

    File = desired_file.split('.')[-1] #coletando a extensão do arquivo

    if File not in allowed_file_extensions and File != 'HTTP%20server/':
        file = open(pasta_atual/'400.html','r',encoding='utf-8')
        file_content = file.read()

        answer_header = f'HTTP/1.1 400 Bad Request\r\n\r\n'
        answer_body = file_content

        BadRequestAnswer = answer_header + answer_body
        socket_client.sendall(BadRequestAnswer.encode(('utf-8')))
        socket_client.close()
        return False

    #----------------------- Erro 403:

    if desired_file == 'pagina_secreta.html':
        if client_addr[0] not in maximum_access_Addresses:
            file = open(pasta_atual/'403.html','r',encoding='utf-8')
            file_content = file.read()
            
            answer_header = f'HTTP/1.1 403 Forbidden\r\n\r\n'
            answer_body = file_content

            Forbidden_answer = answer_header + answer_body

            socket_client.sendall(Forbidden_answer.encode(('utf-8')))
            socket_client.close()
            return False
        
    #----------------------- checando a extensão/tipo do arquivo (considerando que ele é permitido):
    
    type_of_file = desired_file.split('.')[-1]
    binary_file = False
    if type_of_file in text_file_type_array:
        pass
    else:
        binary_file = True

    #----------------------- Pegando o Pacote:

    try:
        if binary_file:
            file = open(pasta_atual/desired_file,'rb')
        else:
            file = open(pasta_atual/desired_file,'r',encoding='utf-8')
        file_content = file.read()

    except FileNotFoundError:
        print(f'o arquivo ∎ {desired_file} ∎ não existe')
        #-----------------------abrindo o html do erro 404 : 
        file = open(pasta_atual/'404.html','r',encoding='utf-8')
        file_content = file.read()

        answer_header = f'HTTP/1.1 404 File not found \r\n\r\n'
        answer_body = file_content
        not_found_response = answer_header + answer_body

        socket_client.sendall(not_found_response.encode('utf-8'))
        socket_client.close()
        return False

    #----------------------- Resposta pro Browser:

    answer_header = f'HTTP/1.1 200 OK\r\n\r\n'
    answer_body = file_content

    if binary_file:
        Definitive_Answer = bytes(answer_header, 'utf-8') + answer_body
        socket_client.sendall(Definitive_Answer)
    else:
        Definitive_Answer = answer_header + answer_body
        socket_client.sendall(Definitive_Answer.encode('utf-8'))

    #-----------------------
    #socket_client.sendall(Definitive_Answer.encode('utf-8'))
    socket_client.close()
    
#----------------------- loop com threads:

while True:
    
    print(f'HTTP Server listening on ∎∎∎ address:{sv_addr} ∎∎∎ port:{sv_port} ∎∎∎')
    socket_client,client_addr = socket_server.accept()
    Thread(target=Server_Thread, args=(socket_client,client_addr)).start()

socket_server.close()
