import ply.yacc as yacc     # biblioteca de análise sintática (parser).
from lexer import tokens    # importados do analisador léxico (lexer.py), são usados nas regras.
from ast_nodes import *     # define as classes de nós da árvore sintática abstrata (como Program, Assignment, If, etc.).

# ---------------------------------------------------------------------
# PROGRAM
# ---------------------------------------------------------------------
    # Regra inicial. Um programa é uma lista de comandos (stmt_list).
    # Cria o nó raiz da AST do tipo Program, contendo todos os comandos.
def p_program(p):
    'program : stmt_list'
    p[0] = Program(p[1])


# ---------------------------------------------------------------------
# Lista de Comandos
# ---------------------------------------------------------------------
    # Caso tenha múltiplos comandos: acumula os comandos em uma lista.
    # Ignora comandos nulos (como quebras de linha isoladas).
def p_stmt_list_multi(p):
    'stmt_list : stmt_list statement'
    if p[2]:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = p[1]

    # Caso tenha apenas um comando.
    # Também ignora comandos nulos.
def p_stmt_list_single(p):
    'stmt_list : statement'
    if p[1]:
        p[0] = [p[1]]
    else:
        p[0] = []

# ---------------------------------------------------------------------
# Comandos Vazios ou de Indentação
# ---------------------------------------------------------------------
    # Comandos que representam apenas quebra de linha ou indentação são ignorados.
def p_statement_newline(p):
    'statement : NEWLINE'
    p[0] = None

def p_statement_indent(p):
    'statement : INDENT'
    p[0] = None

# ---------------------------------------------------------------------
# Comandos Simples
# ---------------------------------------------------------------------
    # Cada um desses comandos cria um nó na AST correspondente à sua ação
def p_stmt_pass(p):
    'statement : PASS NEWLINE'
    p[0] = Pass()

def p_stmt_break(p):
    'statement : BREAK NEWLINE'
    p[0] = Break()

def p_stmt_continue(p):
    'statement : CONTINUE NEWLINE'
    p[0] = Continue()

# ---------------------------------------------------------------------
# Atribuição
# ---------------------------------------------------------------------
    # Atribuição de valor a uma variável.
    # Exemplo: x = 5 → nó Assignment com Name('x') e Number(5).
def p_assign(p):
    'statement : NAME ASSIGN expression NEWLINE'
    p[0] = Assignment(Name(p[1]), p[3])

# ---------------------------------------------------------------------
# Definição de Função
# ---------------------------------------------------------------------
    # Função sem parâmetros.
    # Cria um nó FunctionDef com o nome da função e seu corpo (bloco).
def p_funcdef(p):
    'statement : DEF NAME LPAREN RPAREN COLON NEWLINE block'
    p[0] = FunctionDef(p[2], p[7])

# ---------------------------------------------------------------------
# Retorno de Função
# ---------------------------------------------------------------------
def p_stmt_return(p):
    'statement : RETURN expression NEWLINE'
    p[0] = Return(p[2])

# ---------------------------------------------------------------------
# Estrutura condicional (if / if-else)
# ---------------------------------------------------------------------
    # Cria um nó If com a condição (p[2]), o bloco then (p[5]) e opcionalmente o else (p[9]).
def p_if(p):
    'statement : IF expression COLON NEWLINE block'
    p[0] = If(p[2], p[5])

def p_if_else(p):
    'statement : IF expression COLON NEWLINE block ELSE COLON NEWLINE block'
    p[0] = If(p[2], p[5], p[9])

# ---------------------------------------------------------------------
# While
# ---------------------------------------------------------------------
    # Estrutura de repetição.
    # Cria um nó While com condição e corpo.
def p_while(p):
    'statement : WHILE expression COLON NEWLINE block'
    p[0] = While(p[2], p[5])

# ---------------------------------------------------------------------
# Bloco de Código Indentado
# ---------------------------------------------------------------------
    # Representa um bloco de código indentado (corpo de funções, ifs, laços).
    # Retorna a lista de comandos dentro da indentação.
def p_block(p):
    'block : INDENT stmt_list DEDENT'
    p[0] = p[2]

# ---------------------------------------------------------------------
# Expressões Binárias
# ---------------------------------------------------------------------
    # Gera um nó BinOp com os operandos esquerdo, operador e direito.
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression LT expression
                  | expression GT expression
                  | expression LE expression
                  | expression GE expression
                  | expression EQEQ expression
                  | expression NE expression'''
    p[0] = BinOp(p[1], p[2], p[3])

# ---------------------------------------------------------------------
# OUTRAS EXPRESSÕES
# ---------------------------------------------------------------------
    # Agrupamento de expressões com parênteses.
def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

    # Valor Numérico
def p_expression_number(p):
    'expression : NUMBER'
    p[0] = Number(p[1])

    # Variável ou Identificador
def p_expression_name(p):
    'expression : NAME'
    p[0] = Name(p[1])

# ---------------------------------------------------------------------
# Tratamentos de Erros
# ---------------------------------------------------------------------
def p_error(p):
    if p:
        print(f"Erro sintático: token inesperado {p.value!r}")
    else:
        print("Erro sintático: fim de arquivo inesperado")

# ---------------------------------------------------------------------
# Criação do Parser
# ---------------------------------------------------------------------
parser = yacc.yacc()
