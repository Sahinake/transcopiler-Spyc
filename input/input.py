# ==== Funções com tipos e retorno ====

def soma(a, b):
    return a + b

def multiplica(x, y):
    return x * y

# ==== Uso de variáveis com tipos diferentes ====

numero = 7
preco = 19.99
saudacao = "Olá, Mundo!"

# ==== Chamada de funções ====

# parâmetros tipo int
resultado = soma(3, numero)
# parâmetros tipo float
total = multiplica(2.5, 4.0)

# ==== Entrada do usuário ====

nome = input("Digite seu nome: ")
idade = input("Digite sua idade: ")

# ==== Saída para o usuário ====

print("Nome:", nome)
print("Idade:", idade)
print("Mensagem:", saudacao)
print("Resultado da soma:", resultado)
print("Total da multiplicação:", total)

# ==== Bloco condicional ====

if total > 30.0:
    print("Tá muito caro!")
else:
    print("Tá baratim!")

# ==== Comentário de fim de arquivo ====
# Tudo funcionando como esperado!
