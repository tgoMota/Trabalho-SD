import grpc
from concurrent import futures
import time
import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2
import interface as I
from threading import Thread
import json
from google.protobuf.json_format import MessageToJson

databaseCID = dict()
databasePID = dict()
databaseOID = dict()
nextOID = dict()
I.fillDatabasePID(databasePID)
I.fillDatabaseCID(databaseCID)
I.fillDatabaseOID(databaseOID)

######################## MOSQUITTO PUB
import random
import time

from paho.mqtt import client as mqtt_client


broker = 'broker.emqx.io'
port = 1883
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'emqx'
password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def sendOnTopic(topic, msg):
    client = connect_mqtt()
    client.loop_start()
    for i in range(3):
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
            print(f"{msg} enviada com sucesso no topico {topic}")
            break
    client.disconnect()
        
###############################

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

    def createUser(self, user):
        return self.stub.GetServerResponseCreateUser(user)

class UnaryService(pb2_grpc.UnaryServicer):
    def __init__(self, *args, **kwargs):
        pass

    def GetServerResponseCreateUser(self, request, context):
        print(f'BD recebeu {request}\n')
        cid = request.cid.cid
        if cid in databaseCID:
            print('Erro: Cliente já existente')
            return I.newOk(0) #Erro
        databaseCID[cid] = request.user
        return I.newOk(1) #usuario criado com sucesso
    
    def GetServerResponseGetUser(self, request, context):
        print(f'BD recebeu GetUser {request}\n')
        cid = request
        user = databaseCID[cid.cid]
        print(f'BD pegou cid =  {cid} e user = {user}\n')
        return I.newGetUser(cid, user) #usuario encontrado com sucesso
    
    def GetServerResponseLoginUser(self, request, context):
        print(f"BD recebeu {request}")
        for cid in databaseCID:
            user = databaseCID[cid]
            #print(f"user = {user}")
            if cid == request.cid.cid and user.password == request.password:
                print(f"user = {user}")
                print(f"ja enviou e retornou")
                return I.newOk(1) #dados informados batem com o banco de dados
        return I.newOk(0) #nao ha cadastro correspondente
    
    def GetServerResponseRemoveUser(self, request, context):
        cid = request.cid
        if cid not in databaseCID:
            return I.newOk(0) #usuario nao encontrado
        toSend = I.newRemoveCacheUser(request)
        user_update_json = MessageToJson(toSend)
        sendOnTopic(I.TOPIC, user_update_json)
        del databaseCID[cid]
        print('Removido com sucesso no BD')
        #listarClientes()
        return I.newOk(1) #usuario removido
    
    def GetServerResponseRecoverUser(self, request, context):
        print(f"requisicao de recover chegou no bd = {request}")
        if request.cid not in databaseCID:
            return I.newUser("-1", "-1", "-1", "-1", "-1")
        return databaseCID[request.cid]

    def GetServerResponseUpdateUser(self, request, context):
        print(f"bd recebeu request = {request}")
        cid = request.cid.cid
        if cid not in databaseCID:
            return I.newOk(0) #usuario nao encontrado
        toSend = I.newUpdateCacheUser(request)
        user_update_json = MessageToJson(toSend)
        sendOnTopic(I.TOPIC, user_update_json)
        databaseCID[cid] = request.user
        print('Atualizado com sucesso no BD')
        return I.newOk(1) #cadastrado modificado
    
    def GetServerResponseListProducts(self, request, context):
        products = []
        for productPid in databasePID:
            products.append(databasePID[productPid])
        return I.newArrayProducts(products)

    def GetServerResponseListOrderes(self, request, context):
        #print(f"chegou aqui no bd cid = {request}")
        orderes = []
        for orderOID in databaseOID:
            #print(f"dentro do for: {orderOID}, {databaseOID}")
            order = databaseOID[orderOID]
            #print(f"dentro do for: type order = {type(order)}")
            if order.cid == request:
                orderes.append(order)
        
        #print(f"chegou no bd, retornou {orderes}")
        return I.newResultListOrderes(orderes)
    
    def GetServerResponseProduct(self, request, context):
        pid = request.pid
        if pid not in databasePID:
            return I.newProduct(I.newProductPID("-1"), "", 0, 0)
        
        product = databasePID[pid]
        return product

    def GetServerResponseCreateOrder(self, request, context):
        oid = nextOID["oid"]
        #print(f"nxtOid = {oid}")
        print(f'Chegou aq no bd = {request}')
        databaseOID[str(oid)] = I.newArrayOrderes(I.newOrderOID(str(oid)), request.cid, request.orderProduct)
        #diminuir quantidades dos produtos #fazer dps
        nextOID["oid"] = oid+1
        return I.newOk(1)
    
    def GetServerResponseCancelOrder(self, request, context):
        #print(f"chegou aq no bd, request = {request}")
        oid = request.oid.oid
        if oid not in databaseOID:
            return I.newOk(0) #pedido nao existe
        del databaseOID[oid]
        return I.newOk(1) #pedido cancelado com sucesso
    
    def GetServerResponseCreateProduct(self, request, context):
        print(f'Chegou no portal_client CreateProduct = {request}')
        pid = request.pid.pid
        if pid in databasePID:
            return I.newOk(0) #produto ja existe
        databasePID[pid] = request.product
        return I.newOk(1) #produto criado com sucesso
    
    def GetServerResponseRemoveProduct(self, request, context):
        #print(f"chegou aq no bd, request = {request}")
        pid = request.pid.pid
        if pid not in databasePID:
            return I.newOk(0) #pedido nao existe
        toSend = I.newRemoveCacheProduct(request)
        user_update_json = MessageToJson(toSend)
        sendOnTopic(I.TOPIC, user_update_json)
        del databasePID[pid]
        return I.newOk(1) #produto removido com sucesso
    
    def GetServerResponseCancelOrder(self, request, context):
        print(f"Pedido de cancelamento chegou aqui = {request}")
        oid = request.oid.oid
        print(f"ORDER = {databaseOID[oid]}")
        if oid not in databaseOID or databaseOID[oid].cid.cid != request.cid.cid:
            return I.newOk(0) #pedido nao existe
        del databaseOID[oid]
        print("\n\nCANCELOU\n\n")
        return I.newOk(1) #produto removido com sucesso
    
    def GetServerResponseUpdateProduct(self, request, context):
        print(f"request de update chegou aq = {request}")
        pid = request.pid.pid
        if pid not in databasePID:
            return I.newOk(0) #produto nao existe
        toSend = I.newUpdateCacheProduct(request)
        user_update_json = MessageToJson(toSend)
        sendOnTopic(I.TOPIC, user_update_json)
        databasePID[pid] = request.product
        return I.newOk(1) #produto atualizado com sucesso
    
    def GetServerResponseRecoverProduct(self, request, context):
        print(f"requisicao de recover chegou no bd = {request}")
        if request.pid not in databasePID:
            print("\nChegou aq nao recuperou\n")
            return I.newProduct(I.newProductPID("-1"), "-1", -1, -1)
        return databasePID[request.pid]
    
    def GetServerResponseUpdateOrder(self, request, context):
        oid = request.oid.oid
        if oid not in databaseOID:
            return I.newOk(0)
        idx = 0
        for product in databaseOID[oid].products:
            print(f"p = {product}")
            if product.pid == request.pid:
                databaseOID[oid].products[idx].quantity = request.quantity
                return I.newOk(1)
            idx = idx + 1
        return I.newOk(0)

def runUnary(): #cria server grpc unario
    server = I.createServer(UnaryService(), I.MAX_WORKERS, I.PORT2)  
###########################
# funçoes para fins de teste
def listarClientes():
    print('Clients: ', end="{")
    for client in databaseCID.items():
        print(client, end=" , ")
    print('}')

def listarProdutos():
    print('Produtos: ', end="{")
    for product in databasePID.items():
        print(product, end=" , ")
    print('}')

def listarPedidos():
    print('Pedidos: ', end="{")
    for order in databaseOID.items():
        print(order, end=" , ")
    print('}')
    
###########################
# main
if __name__ == '__main__':
    nextOID["oid"] = 3
    runUnary()