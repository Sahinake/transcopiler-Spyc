import os
from lexer import lexer
from parser import parser, output

def transpile(input_code):
    lexer.input(codigo_python)
    print("Tokens:")
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

    result = parser.parse(codigo_python, lexer=lexer)
    print("Conteúdo de parser.output:", output)

    # Junta e salva o código C
    c_code = "\n".join(output)
    if not os.path.exists("output"):
        os.makedirs("output")
    with open("output/output.c", "w") as f:
        f.write(c_code)

    print("Código C gerado com sucesso em 'output/output.c'!")

if __name__ == "__main__":
    codigo_python = '''\
def foo():
    x = 10
    if x > 0:
        x = x - 1
    else:
        x = x + 1
    while x < 20:
        x = x + 2
'''

    print("Código de entrada:", codigo_python)
    transpile(codigo_python)
