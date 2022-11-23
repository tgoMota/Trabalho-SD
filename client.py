import grpc
import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2
import interface as I


class UnaryClient(object):
    """
    Client for gRPC functionality
    """

    def __init__(self, port):
        self.host = 'localhost'
        self.server_port = port

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        # bind the client and the server
        self.stub = pb2_grpc.UnaryStub(self.channel)

    def makeLogin(self, Login):
        ok = self.stub.GetServerResponseLoginUser(Login)
        return ok
    
    def listProducts(self, cid):
        products = self.stub.GetServerResponseListProducts(cid)
        return products
    
    def listOrderes(self, cid):
        orderes = self.stub.GetServerResponseListOrderes(cid)
        return orderes

    def getProduct(self, pid):
        product = self.stub.GetServerResponseProduct(pid)
        return product
    
    def createOrder(self, CreateOrder):
        ok = self.stub.GetServerResponseCreateOrder(CreateOrder)
        return ok
    
    def cancelOrder(self, CancelOrder):
        ok = self.stub.GetServerResponseCancelOrder(CancelOrder)
        return ok
    
    def updateOrder(self, UpdateOrder):
        ok = self.stub.GetServerResponseUpdateOrder(UpdateOrder)
        return ok


##############################################################
# Funcoes Cliente

# solicita cid para o adm e retorna o cid, -1 se o cadastro já existir no banco de dados
def requestLoginClient(Login):
    client = UnaryClient(I.PORT3)
    ok = client.makeLogin(Login)
    return ok

# solicita uma lista de produtos disponiveis
def requestListProducts(cid):
    client = UnaryClient(I.PORT3)
    products = client.listProducts(cid)
    return products

# solicita uma lista de seus pedidos
def requestListOrderes(cid):
    client = UnaryClient(I.PORT3)
    orderes = client.listOrderes(cid)
    return orderes

# requisitar informacoes sobre produto
def requestProductByPID(pid):
    client = UnaryClient(I.PORT3)
    product = client.getProduct(pid)
    return product

# criar pedido
def requestCreateOrder(CreateOrder):
    client = UnaryClient(I.PORT3)
    ok = client.createOrder(CreateOrder)
    return ok

# cancelar pedido
def requestCancelOrder(CancelOrder):
    client = UnaryClient(I.PORT3)
    ok = client.cancelOrder(CancelOrder)
    return ok

# atualizar pedido
def requestUpdateOrder(cid, oid, pid, quantity):
    client = UnaryClient(I.PORT3)
    ok = client.updateOrder(I.newUpdateOrder(cid, oid, pid, quantity))
    return ok
##############################################################
# main
if __name__ == '__main__':
    option = 1
    cid = I.newUserCID(str(I.ERROR))
    logged = False
    while logged == False:
        cid = I.newUserCID(input("Digite seu cid: "))
        password = I.takeHash(input("Digite sua senha: "))
        ok = requestLoginClient(I.newLogin(cid, password))
        if ok.flag == 0:
            print("Os dados digitados nao correspondem a nenhum registro")
        else:
            print("Login efetuado com sucesso!")
            logged = True

    print(f'Meu cid eh {cid.cid}')
    option = 1
    while option != I.EXIT_OPTION:
        I.printOptionsClient()
        option = int(input())
        if option == I.LIST_PRODUCTS:
            products = requestListProducts(cid)
            print(f'Produtos: {products}')
        if option == I.LIST_ORDERES:
            orderes = requestListOrderes(cid)
            print(f'Pedidos: {orderes}')
        if option == I.CREATE_ORDER:
            qtd = int(input("Digite quantos produtos diferentes deseja comprar: "))
            products = []
            success = True
            for i in range(qtd):
                pid = input("Digite o pid do produto que deseja comprar: ")
                qtd_pid = int(input("Digite a quantidade desse projeto que deseja: "))
                pid = I.newProductPID(pid)
                product = requestProductByPID(pid)
                print(f"pegou produto: {product}")
                if product.pid.pid == -1:
                    print("ERRO: Produto nao encontrado no sistema")
                    success = False
                    break
                if product.stock < qtd:
                    print("ERRO: Produto em falta para essa quantidade")
                    success = False
                    break

                products.append(I.newOrderProduct(pid, qtd_pid))
            if success == True:
                order = I.newCreateOrder(cid, products)
                ok = requestCreateOrder(order)
                I.printFlagMessage(ok, "Pedido Feito com Sucesso", "Nao foi possivel realizar o pedido")
        if option == I.UPDATE_ORDER:
            oid = I.newOrderOID(input("Digite o oid do pedido que deseja modificar: "))
            pid = I.newProductPID(input("Digite o pid do pedido que deseja modificar: "))
            quantity = int(input("Digite a nova quantidade do produto que deseja"))
            ok = requestUpdateOrder(cid, oid, pid, quantity)
            I.printFlagMessage(ok, "Pedido Atualizado com Sucesso", "Nao foi possivel atualizar o pedido")
        if option == I.REMOVE_ORDER:
            oid = input("Qual o oid do pedido que deseja cancelar: ")
            oid = I.newOrderOID(oid)
            ok = requestCancelOrder(I.newCancelOrder(cid, oid))
            I.printFlagMessage(ok, "Pedido Cancelado com Sucesso", "Nao foi possivel cancelar o pedido")

    print('Volte sempre!')
