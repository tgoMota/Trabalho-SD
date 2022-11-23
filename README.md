# Trabalho Sistetmas Distribuidos 2022/2
São 5 arquivos que serão utilizados nas conexoes, são eles: client.py, adm.py, portal_client.py, portal_adm.py, bd.py
os arquivos portal_adm.py, portal_client.py e bd.py são scripts que ficam escutando o tempo inteiro em uma porta, então
precisam ser executados antes dos arquivos client.py e adm.py que servem como clientes.
uma correta ordem em terminais diferentes, seria:
py portal_adm.py
py portal_client.py
py bd.py
(A ordem entre esses nao importa, o importante é que sejam executados antes do client.py e adm.py)
py client.py
py adm.py
(A ordem entre o client.py e adm.py tbm nao tem relevancia)
depois disso, basta interagir com a interface no terminal

###############
Há 4 entradas para testes escritos em 4 arquivos, 2 deles são reservados para a interface do client e
2 deles para a interface do adm. São os arquivos: test1Adm, test2Adm, test1Client, test2Client
