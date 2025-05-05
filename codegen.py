from ast_nodes import * # Importa todas as classes definidas no ast_nodes.py

# ---------------------------------------------------------------------------------------------------
# CLASSE CGENERATOR
# ---------------------------------------------------------------------------------------------------
# Essa classe implementa o gerador de código C: recebe a árvore sintática como entrada e devolve uma string com o código equivalente em C.
class CGenerator:
    def __init__(self):
        # Controla o nível de indentação (quantidade de espaços antes das linhas de código).
        self.indent_level = 0
        # Lista onde o código C gerado será acumulado linha por linha.
        self.result = []

    # Função Emit
        # Adiciona uma linha ao código C, com a indentação apropriada (4 espaços por nível).
        # É uma função auxiliar que facilita a geração de código identado corretamente.
    def emit(self, line):
        self.result.append("    " * self.indent_level + line)

    # Função Principal: Generate
        # Essa função navega na AST e chama recursivamente o código necessário para cada tipo de nó.
        # Ela trata os comandos e estruturas do programa (e não expressões).
    def generate(self, node):
        # PROGRAM
            # Itera sobre todos os comandos do programa e gera código para cada um.
            # No final, retorna todo o código como uma string com quebras de linha.
        if isinstance(node, Program):
            for stmt in node.statements:
                self.generate(stmt)
            return "\n".join(self.result)
        # FUNCTION DEF
            # Gera a definição de uma função em C.
            # O nome da função vem de node.name, e o corpo é gerado recursivamente com node.body.
            # O corpo da função é indentado.
        elif isinstance(node, FunctionDef):
            self.emit(f"void {node.name}() {{")
            self.indent_level += 1
            for stmt in node.body:
                self.generate(stmt)
            self.indent_level -= 1
            self.emit("}")

        # RETURN
        elif isinstance(node, Return):
            expr = self.generate_expr(node.value)
            self.emit(f"return {expr};")

        # IF / ELSE
            # Gera um bloco if (e opcionalmente else) em C.
            # Usa generate_expr para obter a condição.
            # Trata separadamente os corpos if e else.
        elif isinstance(node, If):
            self.emit(f"if ({self.generate_expr(node.condition)}) {{")
            self.indent_level += 1
            for stmt in node.body:
                self.generate(stmt)
            self.indent_level -= 1
            if node.else_body:
                self.emit("} else {")
                self.indent_level += 1
                for stmt in node.else_body:
                    self.generate(stmt)
                self.indent_level -= 1
            self.emit("}")

        # WHILE
            # Traduz um laço while.
            # A condição é passada para generate_expr.
            # O corpo é gerado com recursão e indentado.
        elif isinstance(node, While):
            self.emit(f"while ({self.generate_expr(node.condition)}) {{")
            self.indent_level += 1
            for stmt in node.body:
                self.generate(stmt)
            self.indent_level -= 1
            self.emit("}")

        # ASSIGNMENT
            # Traduz uma atribuição.
            # Usa generate_expr para avaliar o lado direito.
            # Aqui há uma simplificação: toda variável é declarada como int. Isso pode ser melhorado depois, se desejar gerar código com inferência ou tipos diferentes.
        elif isinstance(node, Assignment):
            expr = self.generate_expr(node.value)
            self.emit(f"int {node.target.id} = {expr};")

        # COMANDOS SIMPLES
            # Traduções diretas dos comandos break, continue, e pass.
            # O pass vira um comentário, já que não tem equivalente em C.
        elif isinstance(node, Break):
            self.emit("break;")
        elif isinstance(node, Continue):
            self.emit("continue;")
        elif isinstance(node, Pass):
            self.emit("// pass")

        # ERRO PARA NÓS NÃO TRATADOS
            # Levanta um erro caso seja passado um nó que ainda não tem suporte na geração de código.
        else:
            raise NotImplementedError(f"Node não tratado: {type(node).__name__}")

    # GERAÇÃO DE EXPRESSÕES
        # Essa função trata expressões, como x + y ou 3 * z.
    def generate_expr(self, expr):
        # BINOP
            # Constrói uma expressão binária com parênteses ao redor.
            # Ex: x + 1 vira (x + 1).
        if isinstance(expr, BinOp):
            left = self.generate_expr(expr.left)
            right = self.generate_expr(expr.right)
            # Parênteses aqui
            return f"({left} {expr.op} {right})"
        # NAME
            # Retorna o nome da variável diretamente.
        elif isinstance(expr, Name):
            return expr.id
        # NUMBER
            # Retorna o número como string.
        elif isinstance(expr, Number):
            return str(expr.value)
        # ERROS
            # Erro para expressões não tratadas
        else:
            raise NotImplementedError(f"Expressão não tratada: {type(expr).__name__}")
