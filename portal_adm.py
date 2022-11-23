import grpc
from concurrent import futures
import time
import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2
import interface as I
import cache as C
import random
from paho.mqtt import client as mqtt_client
from threading import Thread
from google.protobuf.json_format import Parse, ParseDict
import json

cacheCID = C.Cache(I.MAX_CACHE_SIZE)
cachePID = C.Cache(I.MAX_CACHE_SIZE)

##########################
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
        type = obj["type"]
        if type == 1: #atualizar usuario nas caches
            up = obj["updateUser"]
            UpdateUser = Parse(json.dumps(up), pb2.UpdateUser())
            print(f"up = {UpdateUser}")
            ok = cacheCID.update(UpdateUser.cid, UpdateUser.user)
            print("\nSUB: Cliente Atualizado com sucesso na cache")
            cacheCID.print()
        if type == 2: #remover usuario nas caches
            up = obj["cid"]
            UserCID = Parse(json.dumps(up), pb2.UserCID())
            print(f"up = {UserCID}")
            ok = cacheCID.removeByKey(UserCID)
            print("\nSUB: Cliente Removido com sucesso na cache")
            cacheCID.print()
        if type == 3: #atualizar produto nas caches
            up = obj["updateProduct"]
            updateProduct = Parse(json.dumps(up), pb2.UpdateProduct())
            print(f"up = {updateProduct}")
            ok = cachePID.update(updateProduct.pid, updateProduct.product)
            print("\nSUB: Produto Atualizado com sucesso na cache")
            cachePID.print()
        if type == 4: #remover produto nas caches
            up = obj["removeProduct"]
            removeProduct = Parse(json.dumps(up), pb2.RemoveProduct())
            print(f"up = {removeProduct}")
            ok = cachePID.removeByKey(removeProduct.pid)
            print("\nSUB: Produto removido com sucesso das cache")
            cachePID.print()
    
    client.subscribe(topic)
    client.on_message = on_message


def runSub():
    client = connect_mqtt()
    subscribe(client, )
    client.loop_forever()


##########################
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
    
    def updateUser(self, updateUserMessage):
       ok = self.stub.GetServerResponseUpdateUser(updateUserMessage)
       return ok
    
    def removeUser(self, cid):
        ok = self.stub.GetServerResponseRemoveUser(cid)
        return ok
    
    def recoverUser(self, cid):
        user = self.stub.GetServerResponseRecoverUser(cid)
        return user
    
    def createProduct(self, CreateProduct):
        ok = self.stub.GetServerResponseCreateProduct(CreateProduct)
        return ok
    
    def updateProduct(self, UpdateProduct):
        ok = self.stub.GetServerResponseUpdateProduct(UpdateProduct)
        return ok
    
    def removeProduct(self, RemoveProduct):
        ok = self.stub.GetServerResponseRemoveProduct(RemoveProduct)
        return ok
    
    def recoverProduct(self, pid):
        product = self.stub.GetServerResponseRecoverProduct(pid)
        return product
    

class UnaryService(pb2_grpc.UnaryServicer):
    def __init__(self, *args, **kwargs):
        pass

    def GetServerResponseCreateUser(self, request, context):
        print(f'portal ADM recebeu {request}\n')
        client_portal_adm = UnaryClient(I.PORT2)
        ok = client_portal_adm.createUser(request)
        if ok.flag == 0:
            return ok
        cacheCID.insert(request.cid, request.user)
        cacheCID.print()
        return ok
    
    def GetServerResponseUpdateUser(self, request, context):
        print(f'portal ADM recebeu {request}\n')
        client_portal_adm = UnaryClient(I.PORT2)
        ok = client_portal_adm.updateUser(request)
        if ok.flag == 0:
            return ok
        cacheCID.insert(request.cid, request.user)
        cacheCID.print()
        print(f"portal retornou - atualizado com sucesso{request}")
        return ok
    
    def GetServerResponseRemoveUser(self, request, context):
        print(f'Chegou no portal_client userCID = {request}')
        client = UnaryClient(I.PORT2)
        ok = client.removeUser(request)
        return ok

    def GetServerResponseRecoverUser(self, request, context):
        print(f"chegou no recover user = {request}")
        client = UnaryClient(I.PORT2)
        if cacheCID.has(request) == True:
            tup = cacheCID.getByKey(request) #(userCID, user)
            return tup[1] #apenas o user
        user = client.recoverUser(request)
        return user
        
    def GetServerResponseCreateProduct(self, request, context):
        print(f'Chegou no portal_client CreateProduct = {request}')
        client = UnaryClient(I.PORT2)
        ok = client.createProduct(request)
        if ok.flag == 0:
            return ok
        cachePID.insert(request.pid, request.product)
        cachePID.print()
        return ok
    
    def GetServerResponseRemoveProduct(self, request, context):
        print(f"chegou aq no portalADM recover product, request = {request}")
        client = UnaryClient(I.PORT2)
        ok = client.removeProduct(request)
        return ok
    
    def GetServerResponseUpdateProduct(self, request, context):
        print(f"chegou aq no portalADM update, request = {request}")
        client = UnaryClient(I.PORT2)
        ok = client.updateProduct(request)
        if ok.flag == 0:
            return ok
        cachePID.insert(request.pid, request.product)
        cachePID.print()
        return ok
    
    def GetServerResponseRecoverProduct(self, request, context):
        print(f"chegou no recover product = {request}")
        client = UnaryClient(I.PORT2)
        if cachePID.has(request) == True:
            tup = cachePID.getByKey(request) #(userCID, user)
            return tup[1] #apenas o product
        product = client.recoverProduct(request)
        return product

def runUnary(): #cria server grpc unario
    server = I.createServer(UnaryService(), I.MAX_WORKERS, I.PORT1)

def mqtAndUnary():
    mqt = Thread(target=runSub)
    unary = Thread(target=runUnary)
    mqt.start()
    unary.start()
    mqt.join()
    unary.join()
if __name__ == '__main__':
    mqtAndUnary()
