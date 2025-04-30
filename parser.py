import ply.yacc as yacc
from lexer import tokens  # importa tokens definidos no lexer

# Lista global de linhas de código C geradas
output = []

def write(s):
    output.append(s)

# Gramática inicial
def p_program(p):
    'program : stmt_list'
    pass  # nada a fazer aqui; output já foi escrito

def p_statement_newline(p):
    'statement : NEWLINE'
    p[0] = None

def p_stmt_list_multi(p):
    'stmt_list : stmt_list statement'
    if p[2] is not None:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = p[1]

def p_stmt_list_single(p):
    'stmt_list : statement'
    if p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_stmt_pass(p):
    'statement : PASS NEWLINE'
    write("/* pass */")

def p_statement_indent(p):
    'statement : INDENT'
    p[0] = None

# Função (def)
def p_funcdef(p):
    'statement : DEF NAME LPAREN RPAREN COLON NEWLINE block'
    write(f"void {p[2]}() {{")
    for stmt in p[7]:
        write("    " + stmt)
    write("}")

# If sem else
def p_if(p):
    'statement : IF expression COLON NEWLINE block'
    write(f"if ({p[2]}) {{")
    for stmt in p[5]:
        write("    " + stmt)
    write("}")

# If com else
def p_if_else(p):
    '''statement : IF expression COLON NEWLINE block ELSE COLON NEWLINE block'''
    write(f"if ({p[2]}) {{")
    for stmt in p[5]:
        write("    " + stmt)
    write("} else {")
    for stmt in p[9]:
        write("    " + stmt)
    write("}")

# While
def p_while(p):
    'statement : WHILE expression COLON NEWLINE block'
    write(f"while ({p[2]}) {{")
    for stmt in p[5]:
        write("    " + stmt)
    write("}")

# Break e continue
def p_stmt_break(p):
    'statement : BREAK NEWLINE'
    write("break;")

def p_stmt_continue(p):
    'statement : CONTINUE NEWLINE'
    write("continue;")

# Atribuição simples
def p_assign(p):
    'statement : NAME ASSIGN expression NEWLINE'
    write(f"{p[1]} = {p[3]};")

# Expressões com precedência
precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('nonassoc','LT','LE','GT','GE','EQEQ','NE'),
)

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
    p[0] = f"({p[1]} {p[2]} {p[3]})"

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = f"({p[2]})"

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_expression_name(p):
    'expression : NAME'
    p[0] = p[1]

# Bloco para lidar com a indentação
def p_block(p):
    'block : INDENT stmt_list DEDENT'
    p[0] = p[2]

# Erro sintático
def p_error(p):
    if p:
        print(f"Erro sintático: token inesperado {p.value!r}")
    else:
        print("Erro sintático: fim de arquivo inesperado")

parser = yacc.yacc()
