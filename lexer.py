# lexer.py
import ply.lex as lex   # Importa o módulo lex do PLY para criar o analisador léxico.

# TOKENS
# -------------------------------------------------------------------------------------
# Esses são os tipos de tokens que o lexer irá reconhecer. Estão incluídos:
    # Operadores Aritméticos: +, -, *, /
    # Comparações: ==, !=, <, <=, etc.
    # Símbolos: =, (, ), :
    # Controle de Indentação: NEWLINE, INDENT, DEDENT
    # Palavras Reservadas e Identificadores
# -------------------------------------------------------------------------------------

tokens = [
    'NAME','NUMBER', 'STRING',
    'PLUS','MINUS','TIMES','DIVIDE',
    'LT','GT','LE','GE','EQEQ','NE',
    'ASSIGN','LPAREN','RPAREN','COLON',
    'NEWLINE','INDENT','DEDENT',
    'COMMA',
    'TYPE',
    'COMMENT',
]

# PALAVRAS-CHAVE
# Essas são palavras-chave do Python
reserved = {
    'def': 'DEF',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'pass': 'PASS',
    'return': 'RETURN',
}
tokens += list(reserved.values())

# EXPRESSÕES REGULARES
# Essas regras usam expressões regulares para tokens que têm uma forma fixa. Cada variável t_NOME define a regex correspondente.
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQEQ    = r'=='
t_NE      = r'!='
t_LE      = r'<='
t_GE      = r'>='
t_LT      = r'<'
t_GT      = r'>'
t_ASSIGN  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_COLON   = r':'
t_COMMA = r','

# COMENTÁRIOS
# Essa função ignora comentários iniciados por #. Eles não são retornados como tokens.
def t_COMMENT(t):
    r'\#.*'
    # t.value recebe tudo depois do '#', opcionalmente sem a própria '#'
    t.value = t.value[1:].lstrip()
    return t

# IDENTIFICADORES E PALAVRAS-CHAVE
# Reconhece nomes de variáveis ou funções.
# Se for uma palavra-chave reservada (como if, while, etc.), troca o tipo para o correspondente (IF, WHILE...).

def t_TYPE(t):
    r'int|float|char'   # ou qualquer regex que cubra seus tipos
    return t

def t_NAME(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'NAME')
    return t

# NÚMEROS
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

# STRINGS
def t_STRING(t):
    r'(\".*?\"|\'.*?\')'
    return t

# Ignorar espaços entre tokens
# Espaços e tabulações dentro da linha são ignorados. O recuo (indentação) só é tratado por uma regra especial com NEWLINE.
t_ignore = ' \t'


# IDENTAÇÃO
# -------------------------------------------------------------------------------------
# Essa é a parte mais complexa e crucial para emular o comportamento do Python (que depende de indentação):
# Stack de indentação
# -------------------------------------------------------------------------------------

INDENT_STACK = [0]      # Mantém a pilha de indentação. Ex: [0, 4, 8] para blocos com 0, 4 e 8 espaços.

# NOVA LINHA
# Quando encontra uma nova linha, ele:
    # Conta a indentação da nova linha.
    # Cria e retorna um token NEWLINE.
    # Se a indentação aumentou, emite um INDENT.
    # Se diminuiu, emite um ou mais DEDENT, até chegar no nível certo.
    # Os tokens INDENT/DEDENT são armazenados em t.lexer.pending_tokens, que serão entregues um a um.
def t_NEWLINE(t):
    r'\n[ \t]*'
    t.lexer.lineno += 1
    indent_str = t.value[1:]  # Pega os espaços/tabs após o \n
    indent = 0
    for ch in indent_str:
        if ch == ' ':
            indent += 1
        elif ch == '\t':
            indent += 4  # ou 8, dependendo do padrão adotado

    t.value = '\n'
    tokens_to_emit = []

    # sempre emitimos um NEWLINE
    tok = lex.LexToken()
    tok.type  = 'NEWLINE'
    tok.value = '\n'
    tok.lineno = t.lexer.lineno
    tok.lexpos = t.lexpos
    tokens_to_emit.append(tok)

    if indent > INDENT_STACK[-1]:
        INDENT_STACK.append(indent)
        tok = lex.LexToken()
        tok.type  = 'INDENT'
        tok.value = ''
        tok.lineno = t.lexer.lineno
        tok.lexpos = t.lexpos
        tokens_to_emit.append(tok)
    else:
        # emitir quantos DEDENT forem necessários
        while indent < INDENT_STACK[-1]:
            INDENT_STACK.pop()
            tok = lex.LexToken()
            tok.type  = 'DEDENT'
            tok.value = ''
            tok.lineno = t.lexer.lineno
            tok.lexpos = t.lexpos
            tokens_to_emit.append(tok)

    # agora guardamos essa lista no lexer e emitimos um por vez
    t.lexer.pending_tokens = tokens_to_emit
    return t.lexer.token()  # pega o primeiro
    
# Garante emissão de DEDENTs após NEWLINE
# Essa função sobrescreve lexer.token() para que ele retorne os tokens pendentes primeiro (como INDENT/DEDENT), antes de continuar a análise normal.
def lexer_token():
    if hasattr(lexer, 'pending_tokens') and lexer.pending_tokens:
        return lexer.pending_tokens.pop(0)
    else:
        return lexer.original_token()

# ERROS
# Captura qualquer caractere não reconhecido e mostra uma mensagem de erro.
def t_error(t):
    print(f"Caracter inválido: {t.value[0]!r} na linha {t.lexer.lineno}")
    t.lexer.skip(1)

def t_eof(t):
    # Ao encontrar o EOF, emite um DEDENT para cada indent extra ainda na pilha
    while len(INDENT_STACK) > 1:
        INDENT_STACK.pop()
        tok = lex.LexToken()
        tok.type   = 'DEDENT'
        tok.value  = ''
        tok.lineno = t.lexer.lineno
        tok.lexpos = t.lexpos
        if not hasattr(t.lexer, 'pending_tokens'):
            t.lexer.pending_tokens = []
        t.lexer.pending_tokens.append(tok)
    return None  # Fim de arquivo, não retorna token

# CRIAÇÃO DO LEXER
# -------------------------------------------------------------------------------------
# Cria o analisador léxico.
# Salva a função original token().
# Substitui por lexer_token() para gerenciar INDENT/DEDENT.
# -------------------------------------------------------------------------------------

lexer = lex.lex()
lexer.original_token = lexer.token
lexer.token = lexer_token
lexer.dedent_queue = []
