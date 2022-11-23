import grpc
from concurrent import futures
import time
import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2
import interface as I
import interface_adm as I_A

class UnaryClient(object):
    """
    Client for gRPC functionality
    """
    def __init__(self, port):
        self.host = 'localhost'
        self.server_port = port

        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        self.stub = pb2_grpc.UnaryStub(self.channel)

    def createUser(self, CreateUser):
        ok = self.stub.GetServerResponseCreateUser(CreateUser)
        return ok
    
    def makeLogin(self, Login):
        cid = self.stub.GetServerResponseLoginUser(Login)
        return cid
    
    def updateUser(self, updateUserMessage):
        ok = self.stub.GetServerResponseUpdateUser(updateUserMessage)
        return ok
    
    def recoverUser(self, cid):
        user = self.stub.GetServerResponseRecoverUser(cid)
        return user
    
    def removeUser(self, cid):
        ok = self.stub.GetServerResponseRemoveUser(cid)
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
    
    def createProduct(self, CreateProduct):
        ok = self.stub.GetServerResponseCreateProduct(CreateProduct)
        return ok
    
    def updateProduct(self, UpdateProduct):
        ok = self.stub.GetServerResponseUpdateProduct(UpdateProduct)
        return ok
    
    def removeProduct(self, RemoveProduct):
        ok = self.stub.GetServerResponseRemoveProduct(RemoveProduct)
        return ok
    
    def recoverProduct(self, ProductPID):
        product = self.stub.GetServerResponseRecoverProduct(ProductPID)
        return product
    
def read_user():
    name = input("Nome: ")
    email = input("Email: ")
    cpf = input("CPF: ")
    password = I.takeHash(input("Senha: "))
    cellphone = input("Numero para contato: ")
    return I.newUser(name, email, cpf, password, cellphone)

def read_product():
    name = input("Nome: ")
    value = float(input("Valor: "))
    stock = int(input("Estoque: "))
    pid = I.newProductPID(name)
    return I.newProduct(pid, name, value, stock)
    
##################################
#Funcoes ADM
#casos de uso
#cadastrar cliente
def requestCreateClient(cid, user):
    client = UnaryClient(I.PORT1)
    ok = client.createUser(I.newCreateUser(cid, user))
    return ok

#moficiar usuario
def requestUpdateUser(cid, user):
    client = UnaryClient(I.PORT1)
    ok = client.updateUser(I.newUpdateUser(cid, user))
    return ok

#recuperar Cliente
def requestRecoverClient(cid):
    client = UnaryClient(I.PORT1)
    user = client.recoverUser(cid)
    return user

#remover cadastro de cliente
def requestRemoveClient(cid):
    client = UnaryClient(I.PORT1)
    ok = client.removeUser(cid)
    return ok

#criar produto
def requestCreateProduct(product):
    client = UnaryClient(I.PORT1)
    pid = product.pid
    ok = client.createProduct(I.newCreateProduct(pid, product))
    return ok

#atualizar produto
def requestUpdateProduct(pid, product):
    client = UnaryClient(I.PORT1)
    ok = client.updateProduct(I.newUpdateProduct(pid, product))
    return ok

#remover produto
def requestRemoveProduct(pid):
    client = UnaryClient(I.PORT1)
    ok = client.removeProduct(I.newRemoveProduct(pid))
    return ok

#recuperar produto
def requestRecoverProduct(pid):
    client = UnaryClient(I.PORT1)
    product = client.recoverProduct(pid)
    return product


if __name__ == '__main__':
    while True:
        I_A.printOptionsAdm()
        option = int(input("Digita a opcao desejada: "))
        if option == I.CREATE_CLIENT:
            print("         Digite os dados do cliente:")
            user = read_user()
            cid = I.newUserCID(user.cpf)
            ok = requestCreateClient(cid, user)
            I.printFlagMessage(ok, "Cadastrado com sucesso!", "Cid ja existente")
        if option == I.UPDATE_CLIENT:
            cid = I.newUserCID(input("Digite o cid: "))
            print("---------------------\n         Digite os novos dados:")
            user = read_user()
            ok = requestUpdateUser(cid, user)
            I.printFlagMessage(ok, "Cliente Atualizado com sucesso!", "Nao foi possivel atualizar o cadastro")
        if option == I.REMOVE_CLIENT:
            cid = I.newUserCID(input("Digite o cid do cliente a ser removido: "))
            ok = requestRemoveClient(cid)
            I.printFlagMessage(ok, "A conta foi deletada com sucesso", "Nao foi possivel deletar a conta")
        if option == I.RECOVER_CLIENT:
            cid = I.newUserCID(input("Digite o cid do cliente a ser recuperado: "))
            user = requestRecoverClient(cid)
            if user.name == "-1":
                print("Nao foi possivel recuperar o client\n")
            else:
                print("Cliente recuperado com sucesso")
                print(f"user = {user}")
        if option == I.CREATE_PRODUCT:
            print("         Digite os dados do produto:")
            product = read_product()
            if product.stock <= 0 or product.value <= 0:
                print("Numeros invalidos")
                continue
            ok = requestCreateProduct(product)
            I.printFlagMessage(ok, "Produto Criado com sucesso!", "Nao foi possivel criar o produto")
        if option == I.UPDATE_PRODUCT:
            pid = I.newProductPID(input("Digite o pid: "))
            print("---------------------\n         Digite os novos dados:")
            name = input("Nome: ")
            value = float(input("Valor: "))
            stock = int(input("Estoque: "))
            if stock <= 0 or value <= 0:
                print("Numeros invalidos")
                continue
            product = I.newProduct(pid, name, value, stock)
            ok = requestUpdateProduct(pid, product)
            I.printFlagMessage(ok, "Produto Atualizado com sucesso!", "O produto nao existe")
        if option == I.REMOVE_PRODUCT:
            pid = I.newProductPID(input("Digite o pid do produto a ser removido: "))
            ok = requestRemoveProduct(pid)
            I.printFlagMessage(ok, "Produto Removido com sucesso!", "O produto nao existe")
        if option == I.RECOVER_PRODUCT:
            pid = I.newProductPID(input("Digite o pid do produto a ser recuperado: "))
            product = requestRecoverProduct(pid)
            if product.pid.pid == "-1":
                print("Nao foi possivel recuperar o produto\n")
            else:
                print("Produto recuperado com sucesso")
                print(f"product = {product}")
        
        if option == I.EXIT_OPTION:
            exit(0)