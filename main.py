import os
from parser import parser
from codegen import CGenerator

def main():
    caminho_entrada = "input/input.py"

    if not os.path.isfile(caminho_entrada):
        print(f"Erro: arquivo '{caminho_entrada}' não encontrado.")
        return

    # Lê o conteúdo do arquivo input/input.py
    with open(caminho_entrada, "r", encoding="utf-8") as f:
        codigo_python = f.read()

    # Faz o parsing do código Python
    ast = parser.parse(codigo_python)

    # Gera o código C
    gen = CGenerator()
    codigo_c = gen.generate(ast)

    # Cria a pasta 'output' se ela não existir
    os.makedirs("output", exist_ok=True)

    # Salva o código C no arquivo output/output.c
    with open("output/output.c", "w", encoding="utf-8") as f:
        f.write(codigo_c)

    print("Código C gerado em 'output/output.c'")

if __name__ == "__main__":
    main()
