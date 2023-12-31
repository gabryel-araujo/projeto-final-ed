import socket
import sys
import os
import platform
from Lista_Encadeada import *
from Cliente_Class import *

carrinho = Lista()
HOST = '127.0.0.1'
PORTA = 41800
cmd_client = ['GET_MENU', 'SEND', 'QUIT']  # MÉTODOS DO PROTOCOLO.
req = ''
resp = ''
v_total = 0
cardapio =''


def options() -> str:
    limpaTerminal()
    print("===Menu===")
    print("1 - Mostrar cardápio")
    print("2 - Abrir carrinho")
    print("3 - Finalizar Pedido")
    print("X - Sair")

    while True:
        escolha = input("Escolha uma opção: ").lower()
        if escolha in ['1', '2', '3', 'x']:
            break
        else:
            print("Opção inválida! Por favor, escolha uma opção válida.")

    return escolha


def fazPedido(carrinho)->str: # Função responsável pela solicitação, armazenamento do cardápio e escolha do pedido.
    global v_total
    global cardapio
    global menu
    pedido = []
    while True:
        limpaTerminal()
        if cardapio == '': #Caso o cliente ainda não tenha recebido o cardápio, realiza a requisição.
            req = f'{cmd_client[0]}/\n' 
            sock.send(str.encode(req)) #Envia o método na requisição.
            resp = sock.recv(1024)
            resp = resp.decode()
            resp = resp.split('\n') #Separando a mensagem do protocolo do conteúdo.
            if resp[0] == 'SENT_MENU':
                cardapio = resp[1] #Adiciona em uma variável apenas a parte contendo o cardápio.
                cardapio = cardapio.split('*') #Separa o cardápio pelas linhas.                
                cardapio = [item.split(',') for item in cardapio] #Dessa vez, separa o cardápio por elemento.
        tam = len(cardapio)
        i = 0
        cardapio_view = '=============== CARDÁPIO ===================\n'
        while i < tam: # Looping responsável pela exibição do cardápio.
            cardapio_view += f'{i+1} - {cardapio[i][0]}: R$ {cardapio[i][1]}\n' 
            i += 1
        print(cardapio_view)
        # escolha = int(input("\nEscolha uma opção: "))
        while True:
            try:
                escolha = int(input("Escolha uma opção: "))
                if escolha in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    break
                else:
                    print("Opção inválida! Por favor, escolha uma opção válida.")
            except ValueError:
                print("Opção inválida! Por favor, digite um número inteiro.")
        quant = int(input("Quantidade: "))
        produto = cardapio[escolha-1][0]
        cont = contItem(carrinho, produto)
        if cont == 0:  # Verifica se o pedido já foi adicionado ao carrinho.
            pedido = [produto, quant]
            carrinho.append(pedido)
        else:  
            local = carrinho.elemento(cont)
            local[1] += quant  #Caso o item já tenha sido adicionado, atualiza apenas a quantidade.
        valor_item = quant*float(cardapio[escolha-1][1]) # Armazena a multiplicação entre a quantidade e o valor do item.
        v_total += valor_item  # Adiciona o valor do item no valor total do pedido.
        print("\nCarrinho: ", carrinho)
        print(f'Total: {v_total:.2f}')
        print("\nDeseja continuar comprando? (S/N)")
        confirmacao = input('Opção: ').lower()
        if confirmacao == 'n':
            menu = options()
            return menu 
        else:
            menu = '2'
            return menu
            
def carrinho_pedidos(lista):
    limpaTerminal()
    global v_total
    global cardapio
    global menu
    print("===Carrinho===\n")
    if lista.estaVazia():
        print("Seu carrinho está vazio! Adicione algo para fazer seu pedido!")
        print("\n1 - Adicionar item")
        print("2 - Voltar")
    else:
        print(lista)
        print(f'Total: {v_total:.2f}')
        print("\n1 - Remover item")
        print("2 - Adicionar item")
        print("3 - Voltar")
    
    escolha = input("\nEscolha uma opção: ").lower()
    if escolha == '1' and not lista.estaVazia():
        item = input('Insira a posição do item no carrinho: ').capitalize()
        remove_quantidade = int(input('Quantidade a remover: '))
        try:
            if len(item) < 9:
                produto = lista.elemento(int(item))
                quant = produto[1]
                if remove_quantidade >= quant: 
                    lista.remover(int(item)) 
                    
                else:
                    new_quant = quant - remove_quantidade   
                    produto[1] = new_quant
                    
            
            for item in cardapio:
                if (item[0] == produto[0]) and (remove_quantidade < quant):
                    v_remove = remove_quantidade * float(item[1])
                    v_total -= v_remove
                elif(item[0] == produto[0]) and (remove_quantidade >= quant):
                    v_total -= (quant * float(item[1]))
                    
                                
            carrinho_pedidos(lista)
        except ListaException as le:
            print(le)
            input()
            carrinho_pedidos(lista)
    elif (escolha == '2' and not lista.estaVazia()) or (escolha == '1' and lista.estaVazia()):
        menu = '1'
        return menu
    elif (escolha == '3' and not lista.estaVazia()) or (escolha == '2' and lista.estaVazia()):
        menu = options()
        return menu

def contItem(lista, produto):
    for i, item in enumerate(lista):
        if item[0] == produto:
            return i + 1  # Retorna a posição do item (começando em 1)
    return 0


def dadosPagamento():
    limpaTerminal()
    global v_total
    cliente = Cliente()
    print("Para finalizar, preencha os campos abaixo:")
    cliente.setNome(input("Nome: "))
    cliente.setTelefone(input("Telefone: "))
    cliente.setCep(input("Cep: "))
    print("\nVALOR TOTAL:", v_total)
    print("Forma de pagamento:")
    print("1 - Cartão (pagamento na entrega)\n2 - Dinheiro")
    cliente.setPagamento(input("Opção: "))
    if cliente.getPagamento() == 'Dinheiro':
        print("Vai ser necessário troco?(S/N)")
        troco = input().lower()
        if troco == 's':
            valor = float(input("Troco para quanto? "))
            while valor < v_total:
                print(f'O valor informado tem que ser maior que {v_total}')
                valor = float(input("Troco para quanto? "))
            cliente.setTroco(valor)             
    return cliente


def esvaziaCarrinho(lista):
    while not (lista.estaVazia()):
        lista.remover(lista.tamanho())


def limpaTerminal():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

# -------------- Início programa principal ------------

if len(sys.argv) > 1:
    HOST = sys.argv[1]

servidor = (HOST, PORTA)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect(servidor)
except ConnectionRefusedError as cre:
    print("A pizzaria se encontra fechada")
    sys.exit()

menu = options()
while True:
    if menu == "1": 
        fazPedido(carrinho)

    elif menu == "2":
        carrinho_pedidos(carrinho)

    elif menu == "3":
        if not carrinho.estaVazia():
            dados = dadosPagamento()
            req = f'{cmd_client[1]}/{dados}/ Pedido:{carrinho}\n'
            sock.send(str.encode(req))
            resp = sock.recv(1024)
            resp = resp.decode()
            resp = resp.split('/') 
            if resp[0] == 'SEND_OK':
                print(resp[1])
            input('\nPressione ENTER para voltar ao MENU...')
            esvaziaCarrinho(carrinho)
            menu = options()
            v_total = 0
            
            
        else:
            limpaTerminal()
            print("\nSeu carrinho está vazio! Adicione algo para fazer seu pedido!")
            input("\nPressione ENTER para ir ao cardápio...")
            fazPedido(carrinho)

    elif menu == 'x':
        req = cmd_client[2]
        sock.send(str.encode(req))
        req = sock.recv(1024)
        req = req.decode()
        req = req.split('/')
        if req[0] == 'QUIT_OK':
            print(req[1])
            break
        
sock.close()