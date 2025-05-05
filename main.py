import os
from parser import parser
from codegen import CGenerator

codigo_python = '''
def soma():
    return 1 + 2
'''

# Faz o parsing do código Python
ast = parser.parse(codigo_python)

# Gera o código C
gen = CGenerator()
codigo_c = gen.generate(ast)

# Cria a pasta 'output' se ela não existir
os.makedirs("output", exist_ok=True)

# Salva o código C no arquivo 'output/output.c'
with open("output/output.c", "w") as f:
    f.write(codigo_c)

print("Código C gerado em 'output/output.c'")
