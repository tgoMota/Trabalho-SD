import grpc
from concurrent import futures
import time
import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2
import hashlib
from concurrent import futures

MAX_CACHE_SIZE = 3
MAX_WORKERS = 10
PORT1 = 50051
PORT2 = 50052
PORT3 = 50053
PORT4 = 50054
PORT5 = 50055
PORT6 = 50056
PORT7 = 50057
ERROR = -1

EXIT_OPTION = 0
LOGIN_CLIENT = 1
CREATE_CLIENT = 2
UPDATE_CLIENT = 3
REMOVE_CLIENT = 4
RECOVER_CLIENT = 5
LIST_PRODUCTS = 6
LIST_ORDERES = 7
CREATE_ORDER = 8
UPDATE_ORDER = 9
REMOVE_ORDER = 10

CREATE_PRODUCT = 11
UPDATE_PRODUCT = 12
REMOVE_PRODUCT = 13
RECOVER_PRODUCT = 14

#MQTT
TOPIC = "sbdbrecover"
PORT_MQTT = 1883


def newUser(name, email, cpf, password, cellphone):
    return pb2.User(name=name, email=email, cpf=cpf, password=password, cellphone=cellphone)

def newCreateUser(cid, user):
    return pb2.CreateUser(cid=cid, user=user)

def newGetUser(cid, user):
    return pb2.GetUser(cid=cid, user=user)

def newUpdateUser(cid, user):
    return pb2.UpdateUser(cid=cid, user=user)

def newLogin(cid, password):
    return pb2.Login(cid=cid, password=password)

def newUserCID(cid):
    return pb2.UserCID(cid=cid)

def newProduct(pid, name, value, stock):
    return pb2.Product(pid=pid, name=name, value=value, stock=stock)

def newCreateProduct(pid, product):
    return pb2.CreateProduct(pid=pid, product=product)

def newUpdateProduct(pid, product):
    return pb2.UpdateProduct(pid=pid, product=product)

def newRemoveProduct(pid):
    return pb2.RemoveProduct(pid=pid)

#recebe lista de products pb2.Product
def newArrayProducts(products):
    return pb2.ArrayProducts(products=products)

def newProductPID(pid):
    return pb2.ProductPID(pid=pid)

def newOrder(oid, cid, OrderProductFull):
    print(f"chegou no newOrder, oid = {oid}, cid = {cid}, array = {OrderProductFull}")
    return pb2.Order(oid=oid, cid=cid, OrderProductFull=OrderProductFull)

def newOrderProduct(pid, quantity):
    return pb2.OrderProduct(pid=pid, quantity=quantity)

def newCreateOrder(cid, orderProduct): 
    return pb2.CreateOrder(cid=cid, orderProduct=orderProduct)

def newOrderOID(oid):
    return pb2.OrderOID(oid=oid)

def newArrayOrderes(oid, cid, products):
    return pb2.ArrayOrderes(oid = oid, cid=cid, products=products)

def newArrayOrderesProducts(orderes):
    return pb2.ArrayOrderesProducts(orderes=orderes)

def newOrderProductFull(product, quantity):
    return pb2.OrderProductFull(product=product, quantity=quantity)

def newUpdateUser(cid, oid, user):
    return pb2.UpdateUser(cid=cid, oid=oid, user=user)

def newOk(flag):
    return pb2.Ok(flag=flag)

def newResultListOrderes(arrayOrderes):
    return pb2.ResultListOrderes(arrayOrderes=arrayOrderes)

def newCancelOrder(cid, oid):
    return pb2.CancelOrder(cid=cid, oid=oid)

def newCreateProduct(pid, product):
    return pb2.CreateProduct(pid=pid, product=product)

def newUpdateCacheUser(UpdateUser):
    return pb2.UpdateCacheUser(type=1, updateUser=UpdateUser)

def newRemoveCacheUser(UserCID):
    return pb2.RemoveCacheUser(type=2, cid=UserCID)

def newUpdateCacheProduct(UpdateProduct):
    return pb2.UpdateCacheProduct(type=3, updateProduct=UpdateProduct)

def newRemoveCacheProduct(RemoveProduct):
    return pb2.RemoveCacheProduct(type=4, removeProduct=RemoveProduct)

def newUpdateOrder(cid, oid, pid, quantity):
    return pb2.UpdateOrder(cid=cid, oid=oid, pid=pid, quantity=quantity)

def createServer(unary, workers, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))
    pb2_grpc.add_UnaryServicer_to_server(unary, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()
    return server

def printFlagMessage(ok, success, failure):
    print(success if ok.flag == 1 else failure)

def takeHash(value):
    result = hashlib.md5(value.encode())
    return result.hexdigest()

def printMainOptions():
    print(f"{LOGIN_CLIENT} - Fazer Login")
    print(f"{CREATE_CLIENT} - Cadastrar")
    print(f"{EXIT_OPTION} - Sair")

def printOptionsClient():
    print(f"{LIST_PRODUCTS} - Listar Produtos")
    print(f"{LIST_ORDERES} - Listar Pedidos")
    print(f"{CREATE_ORDER} - Fazer Pedido")
    print(f"{UPDATE_ORDER} - Modificar Pedido")
    print(f"{REMOVE_ORDER} - Cancelar Pedido")
    print(f"{EXIT_OPTION} - Sair")

def fillDatabasePID(databasePID):
    pid1 = newProductPID(takeHash("iPhone17"))
    pid2 = newProductPID(takeHash("iPhone13"))
    pid3 = newProductPID(takeHash("iPhone20"))
    pid4 = newProductPID(takeHash("Samsung Galaxy Y"))
    pid5 = newProductPID(takeHash("Monitor 144hz Samsung"))
    databasePID[takeHash("iPhone17")] = newProduct(pid=pid1,name="iPhone17", value=1982, stock=2)
    databasePID[takeHash("iPhone13")] = newProduct(pid=pid2,name="iPhone13", value=4200, stock=4)
    databasePID[takeHash("iPhone20")] = newProduct(pid=pid3,name="iPhone20", value=9200, stock=6)
    databasePID[takeHash("Samsung Galaxy Y")] = newProduct(pid=pid4,name="Samsung Galaxy Y", value=4200, stock=10)
    databasePID[takeHash("Monitor 144hz Samsung")] = newProduct(pid=pid5,name="Monitor 144hz Samsung", value=1700, stock=7)

def fillDatabaseCID(databaseCID):
    databaseCID["1"] = newUser("Emilio", "emilio@gmail.com", "1", takeHash("1"), "34991276566")
    databaseCID["2"] = newUser("Rodrigo", "Rodrigo@gmail.com", "2", takeHash("83213123"), "34992256166")
    databaseCID["3"] = newUser("Roberta Muzy", "robertamuzy@gmail.com", "3", takeHash("877381"), "34881246261")
    databaseCID["4"] = newUser("Paulo Muzy", "paulomuzy@gmail.com", "4", takeHash("832131"), "34981256361")
    databaseCID["5"] = newUser("Renato Cariani", "renatocariani@gmail.com", "5", takeHash("4213213"), "34988123566")

def fillDatabaseOID(databaseOID):
    productsOrder1 = [newOrderProduct(newProductPID(takeHash("iPhone17")), 2), newOrderProduct(newProductPID(takeHash("Samsung Galaxy Y")), 2)]
    productsOrder2 = [newOrderProduct(newProductPID(takeHash("Samsung Galaxy Y")), 5), newOrderProduct(newProductPID(takeHash("Monitor 144hz Samsung")), 3)]
    databaseOID["1"] = newArrayOrderes(newOrderOID("1"), newUserCID("1"), productsOrder1)
    databaseOID["2"] = newArrayOrderes(newOrderOID("2"), newUserCID(takeHash("2")), productsOrder2)