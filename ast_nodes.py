# ---------------------------------------------------------------------------------------------------
# Essas classes representam os diferentes tipos de nós de uma árvore sintática, e cada classe corresponde a uma estrutura ou expressão no código fonte. A árvore gerada por essas classes é usada para construir o programa em C.
# A classe Node serve como uma classe base para todas as outras classes que representam nós na árvore sintática abstrata (AST).
# AST é uma estrutura de dados que representa a estrutura hierárquica do código-fonte de maneira mais abstrata. Cada tipo de comando ou expressão no código será representado por um nó na árvore.
# ---------------------------------------------------------------------------------------------------

class Node:
    pass

# ---------------------------------------------------------------------------------------------------
# PROGRAM
# ---------------------------------------------------------------------------------------------------
# Program representa o programa inteiro.
# Ele possui um atributo statements, que armazena uma lista de declarações (no caso, a lista de comandos do programa).
# O nó Program é o ponto de entrada da árvore, que é alimentado com a lista de comandos que foram extraídos e processados pelo parser.

class Program(Node):
    def __init__(self, statements):
        self.statements = statements
        
# ---------------------------------------------------------------------------------------------------
# FUNCTION DEF
# ---------------------------------------------------------------------------------------------------
# FunctionDef representa a definição de uma função.
    # name: o nome da função.
    # body: o corpo da função, que é uma lista de comandos.
# A classe armazena o nome da função e o corpo dela, sendo útil para gerar o código de definição de funções na linguagem alvo (C).

class FunctionDef(Node):
    def __init__(self, name, params, types, body):
        self.name = name
        self.params = params
        self.types = types  # Tipos dos parâmetros (ex: ['int', 'int'])
        self.body = body

class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name  # Nome da função chamada
        self.args = args  # Lista de argumentos (ex: [x, y])

# ---------------------------------------------------------------------------------------------------
# IF
# ---------------------------------------------------------------------------------------------------
# If representa uma estrutura condicional if (e opcionalmente, o else).
    # condition: a condição que é avaliada.
    # body: o corpo do bloco de código a ser executado se a condição for verdadeira.
    # else_body: o corpo do bloco de código a ser executado caso a condição seja falsa. Este parâmetro é opcional (pode ser None).
# Essa classe permite que a árvore represente tanto if com ou sem else.

class If(Node):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body

# ---------------------------------------------------------------------------------------------------
# WHILE
# ---------------------------------------------------------------------------------------------------
# While representa a estrutura de repetição while.
    # condition: a condição que é avaliada antes de cada iteração.
    # body: o corpo do laço, ou seja, o conjunto de comandos que são executados enquanto a condição for verdadeira.
# A classe armazena a condição do laço e o seu corpo.

class While(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

# ---------------------------------------------------------------------------------------------------
# ASSIGNMENT
# ---------------------------------------------------------------------------------------------------
# Assignment representa uma atribuição de valor a uma variável.
    # target: a variável ou nome do lado esquerdo da atribuição (ex: x).
    # value: o valor ou expressão do lado direito da atribuição (ex: 5 ou uma expressão como a + b).
# A classe armazena a variável de destino e o valor a ser atribuído a ela.

class Assignment(Node):
    def __init__(self, target, value):
        self.target = target
        self.value = value

# ---------------------------------------------------------------------------------------------------
# COMANDOS SIMPLES (BREAK, CONTINUE, PASS)
# ---------------------------------------------------------------------------------------------------
# Break, Continue, e Pass são comandos simples, que representam:
    # Break: interrompe um laço (como um break no C).
    # Continue: pula para a próxima iteração de um laço (como um continue no C).
    # Pass: não faz nada, sendo um comando nulo (usado como um espaço reservado ou no lugar de código em desenvolvimento).
# Estas classes não têm atributos, já que representam apenas a ação de interrupção ou continuação no fluxo de execução.
class Break(Node): pass
class Continue(Node): pass
class Pass(Node): pass


# ---------------------------------------------------------------------------------------------------
# BINOP
# ---------------------------------------------------------------------------------------------------
# BinOp representa uma operação binária (como soma, subtração, multiplicação, etc.).
    # left: o operando à esquerda da operação.
    # op: o operador (por exemplo, +, -, *, etc.).
    # right: o operando à direita da operação.
# Essa classe é útil para operações aritméticas ou comparações, como a + b, x > y, etc.
class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

# ---------------------------------------------------------------------------------------------------
# NAME
# ---------------------------------------------------------------------------------------------------
# Name representa um identificador, ou seja, o nome de uma variável ou função.
    # id: o nome da variável ou função.
    # Usado para representar variáveis no código, como x, y, foo, etc.

class Name(Node):
    def __init__(self, id):
        self.id = id

# ---------------------------------------------------------------------------------------------------
# NUMBER
# ---------------------------------------------------------------------------------------------------
# Number representa um valor numérico (inteiro ou real).
    # value: o valor numérico real (ex: 5, 3.14).
# Usado para representar números constantes no código.

class Number(Node):
    def __init__(self, value):
        self.value = value

# ---------------------------------------------------------------------------------------------------
# STRING
# ---------------------------------------------------------------------------------------------------
class String(Node):
    def __init__(self, value):
        # value já inclui as aspas, ex: '"hello"' ou "'mundo'"
        self.value = value

class UnaryOp(Node):
    def __init__(self, op, operand):
        self.op = op      # ex: '!'
        self.operand = operand

# ---------------------------------------------------------------------------------------------------
# RETURN
# ---------------------------------------------------------------------------------------------------

class Return(Node):
    def __init__(self, value):
        self.value = value

