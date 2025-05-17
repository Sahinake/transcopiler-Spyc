# SpyC/Pychon- Transpilador de Python para C

SpyC é um transpilador simples que converte um subconjunto da linguagem Python para código C equivalente.  
Este projeto foi desenvolvido como parte da disciplina de **Compiladores** e utiliza a biblioteca [PLY (Python Lex-Yacc)](https://www.dabeaz.com/ply/) para análise léxica e sintática.

## Funcionalidades

- ✅ Suporte a comandos: `pass`, `break`, `continue`
- ✅ Definição de funções com parâmetros e `return`
- ✅ Escopo local de variáveis por bloco (funções, `if`, `while`, etc.)
- ✅ Estruturas de controle: `if`, `else`, `while`
- ✅ Atribuições, operações aritméticas e booleanas
- ✅ Função `print()` com múltiplos argumentos e tipos mistos (`int`, `float`, `str`)
- ✅ Função `input()` com leitura de strings e mensagem opcional
- ✅ Geração de código C com indentação apropriada

## Estrutura do Projeto
```bash
├── output
    └── output.c             # Código equivalente em C
├── lexer.py                 # Analisador léxico (tokens)
├── parser.py                # Analisador sintático e construtor de AST
├── ast_nodes.py             # Definições dos nós da AST
├── gencode.py               # Geração de código C a partir da AST
├── main.py                  # Arquivo principal para rodar o transpilador
├── requirements.txt         # Dependências do projeto
└── README.md                # Este arquivo
```

## Requisitos

- Python 3.8+
- [PLY](https://pypi.org/project/ply/)

Para instalar as dependências:

```bash
pip install -r requirements.txt
```

## Como usar
Execute o transpilador passando um código Python válido:

```bash
python main.py input.py
```
A saída em C será impressa no terminal ou salva em um arquivo de saída, conforme configurado. Para compilar e executar o código em C equivalente, use os comandos:
```bash
gcc output/output.c -o ./output/program
./output/program
```


### Observações
- O código Python de entrada deve seguir a indentação correta (como no Python real).
- Apenas um subconjunto da linguagem é suportado por enquanto.
- Tipos de variáveis são inferidos automaticamente com base nas expressões (ex: int, float, char*).
- Variáveis lidas com input() são tratadas como strings (char[]).

## Autores
Projeto desenvolvido por estudantes da disciplina de Compiladores.
Universidade UFCA — 2025.
