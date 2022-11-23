import grpc
from concurrent import futures
import time
import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2
import interface as I
import cache as C
from concurrent import futures
import random
import time
from threading import Thread
from paho.mqtt import client as mqtt_client
from google.protobuf.json_format import Parse, ParseDict
import json

cacheCID = C.Cache(I.MAX_CACHE_SIZE)
cachePID = C.Cache(I.MAX_CACHE_SIZE)
############################### ######################## MOSQUITTO SUB

broker = 'broker.emqx.io'
port = I.PORT_MQTT
topic = I.TOPIC
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'emqx'
password = 'public'


def connect_mqtt() -> mqtt_client:
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


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        obj = json.loads(msg.payload.decode())
        top = msg.topic
        type = obj["type"]
        if type == 1: #atualizar usuario nas caches
            up = obj["updateUser"]
            UpdateUser = Parse(json.dumps(up), pb2.UpdateUser())
            print(f"up = {UpdateUser}")
            ok = cacheCID.update(UpdateUser.cid, UpdateUser.user)
            print("\nSUB: Cliente Atualizado com sucesso na cache")
        if type == 2: #remover usuario nas caches
            up = obj["cid"]
            UserCID = Parse(json.dumps(up), pb2.UserCID())
            print(f"up = {UserCID}")
            ok = cacheCID.removeByKey(UserCID)
            print("\nSUB: Cliente Removido com sucesso na cache")
        if type == 3: #atualizar produto nas caches
            up = obj["updateProduct"]
            updateProduct = Parse(json.dumps(up), pb2.UpdateProduct())
            print(f"up = {updateProduct}")
            ok = cachePID.update(updateProduct.pid, updateProduct.product)
            print("\nSUB: Produto Atualizado com sucesso na cache")
        if type == 4: #remover produto nas caches
            up = obj["removeProduct"]
            removeProduct = Parse(json.dumps(up), pb2.RemoveProduct())
            print(f"up = {removeProduct}")
            ok = cachePID.removeByKey(removeProduct.pid)
            print("\nSUB: Produto removido com sucesso das cache")
    
    client.subscribe(topic)
    client.on_message = on_message


def runSub():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

###############################
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
        
    def authenticateClient(self, Login):
        ok = self.stub.GetServerResponseLoginUser(Login)
        if ok.flag == 0:
            return ok
        GetUser = self.stub.GetServerResponseGetUser(Login.cid)
        cacheCID.insert(GetUser.cid, GetUser.user)
        cacheCID.print()
        return ok

    def updateUser(self, updateUserMessage):
        ok = self.stub.GetServerResponseUpdateUser(updateUserMessage)
        return ok
    
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
        print(f"Pedido de cancelamento chegou aqui = {CancelOrder}")
        ok = self.stub.GetServerResponseCancelOrder(CancelOrder)
        return ok
    
    def updateOrder(self, UpdateOrder):
        ok = self.stub.GetServerResponseUpdateOrder(UpdateOrder)
        return ok
    
class UnaryService(pb2_grpc.UnaryServicer):

    def __init__(self, *args, **kwargs):
        pass

    def GetServerResponseCreateUser(self, request, context):
        print(f'Chegou no portal_client user = {request}')
        client = UnaryClient(I.PORT2)
        ok = client.createUser(request)
        return ok
    
    def GetServerResponseLoginUser(self, request, context):
        print(f"login chegou no portal client = {request}")
        client = UnaryClient(I.PORT2)
        ok = client.authenticateClient(request)
        return ok
    
    def GetServerResponseRemoveUser(self, request, context):
        print(f'Chegou no portal_client userCID = {request}')
        client = UnaryClient(I.PORT2)
        ok = client.removeUser(request)
        return ok
    
    def GetServerResponseUpdateUser(self, request, context):
        print(f'Chegou no portal_client userCID = {request}')
        client = UnaryClient(I.PORT2)
        ok = client.updateUser(request)
        return ok
    
    def GetServerResponseListProducts(self, request, context):
        print(f"chegou aq a requisicao de listar produtos = {request}")
        client = UnaryClient(I.PORT2)
        products = client.listProducts(request)
        return products
    
    def GetServerResponseListOrderes(self, request, context):
        print(f"cid = {request}")
        client = UnaryClient(I.PORT2)
        orderes = client.listOrderes(request)
        return orderes
    
    def GetServerResponseProduct(self, request, context):
        client = UnaryClient(I.PORT2)
        product = client.getProduct(request)
        return product
    
    def GetServerResponseCreateOrder(self, request, context):
        client = UnaryClient(I.PORT2)
        ok = client.createOrder(request)
        return ok
    
    def GetServerResponseCancelOrder(self, request, context):
        client = UnaryClient(I.PORT2)
        ok = client.cancelOrder(request)
        return ok
    
    def GetServerResponseUpdateOrder(self, request, context):
        print(f"chegou update order em portal client = {request}")
        client = UnaryClient(I.PORT2)
        ok = client.updateOrder(request)
        return ok

def runUnary(): #cria server grpc unario
    server = I.createServer(UnaryService(), I.MAX_WORKERS, I.PORT3)

def mqtAndUnary():
    mqt = Thread(target=runSub)
    unary = Thread(target=runUnary)
    mqt.start()
    unary.start()
    mqt.join()
    unary.join()

if __name__ == '__main__':
    mqtAndUnary()