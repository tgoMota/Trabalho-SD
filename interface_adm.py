import interface as I
def generateCid(user):
    return I.newUserCID(user.cpf)

def printOptionsAdm():
    print(f"{I.CREATE_CLIENT} - Cadastrar Cliente")
    print(f"{I.UPDATE_CLIENT} - Atualizar Cliente")
    print(f"{I.REMOVE_CLIENT} - Remover Cliente")
    print(f"{I.RECOVER_CLIENT} - Recuperar Cliente")
    print(f"{I.CREATE_PRODUCT} - Inserir Produto")
    print(f"{I.REMOVE_PRODUCT} - Remover Produto")
    print(f"{I.UPDATE_PRODUCT} - Atualizar Produto")
    print(f"{I.RECOVER_PRODUCT} - Recuperar Produto")
    print(f"{I.EXIT_OPTION} - Sair")