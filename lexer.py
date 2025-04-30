# lexer.py
import ply.lex as lex

# Tokens
tokens = [
    'NAME','NUMBER',
    'PLUS','MINUS','TIMES','DIVIDE',
    'LT','GT','LE','GE','EQEQ','NE',
    'ASSIGN','LPAREN','RPAREN','COLON',
    'NEWLINE','INDENT','DEDENT',
    'PASS',
]

# Palavras-chave
reserved = {
    'def': 'DEF',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'break': 'BREAK',
    'continue': 'CONTINUE'
}
tokens += list(reserved.values())

# Tokens simples
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
t_PASS = r'pass'

def t_COMMENT(t):
    r'\#.*'
    pass

def t_NAME(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'NAME')
    return t

def t_NUMBER(t):
    r'\d+'
    return t

# Ignorar espaços entre tokens
t_ignore = ' \t'

# Stack de indentação
INDENT_STACK = [0]

def t_NEWLINE(t):
    r'\n[ \t]*'
    t.lexer.lineno += 1
    indent = len(t.value) - 1
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
def lexer_token():
    if hasattr(lexer, 'pending_tokens') and lexer.pending_tokens:
        return lexer.pending_tokens.pop(0)
    else:
        return lexer.original_token()

def t_error(t):
    print(f"Caracter inválido: {t.value[0]!r} na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()
lexer.original_token = lexer.token
lexer.token = lexer_token
lexer.dedent_queue = []
