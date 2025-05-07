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

    # Inferência de tipo simples para retorno e variáveis
    def infer_type(self, expr, env):
        from ast_nodes import Number, BinOp, Name, FunctionCall
        if isinstance(expr, Number):
            return 'float' if isinstance(expr.value, float) else 'int'
        if isinstance(expr, BinOp):
            t1 = self.infer_type(expr.left, env)
            t2 = self.infer_type(expr.right, env)
            return 'float' if 'float' in (t1, t2) else 'int'
        if isinstance(expr, Name):
            return env.get(expr.id, 'int')
        if isinstance(expr, FunctionCall):
            return env.get(expr.name + '_ret', 'int')
        return 'int'

    # Função Principal: Generate
        # Essa função navega na AST e chama recursivamente o código necessário para cada tipo de nó.
        # Ela trata os comandos e estruturas do programa (e não expressões).
    def generate(self, node):
        # PROGRAM
            # Itera sobre todos os comandos do programa e gera código para cada um.
            # No final, retorna todo o código como uma string com quebras de linha.
        if isinstance(node, Program):
            # Cabeçalhos
            self.result.append("#include <stdio.h>")
            self.result.append("#include <string.h>")
            self.result.append("")
            # Separar defs e main
            funcs, mains = [], []
            for s in node.statements:
                (funcs if isinstance(s, FunctionDef) else mains).append(s)
            # Inferir tipos de retorno
            env = {}
            for f in funcs:
                param_env = {p: t for p, t in zip(f.params, f.types)}
                for st in f.body:
                    if isinstance(st, Return):
                        env[f.name + '_ret'] = self.infer_type(st.value, param_env)
                        break
                else:
                    env[f.name + '_ret'] = 'void'
            # Gerar funções
            for f in funcs:
                self.generate(f)
                self.result.append("")
            # Gerar main
            self.emit("int main() {")
            self.indent_level += 1
            for s in mains:
                self.generate(s)
            self.emit("return 0;")
            self.indent_level -= 1
            self.emit("}")
            return "\n".join(self.result)
        # FUNCTION DEF
            # Gera a definição de uma função em C.
            # O nome da função vem de node.name, e o corpo é gerado recursivamente com node.body.
            # O corpo da função é indentado.
        elif isinstance(node, FunctionDef):
            # Retorno e assinatura
            env = {p: t for p, t in zip(node.params, node.types)}
            ret = 'void'
            for st in node.body:
                if isinstance(st, Return):
                    ret = self.infer_type(st.value, env)
                    break
            sig = ', '.join(f"{t} {p}" for t, p in zip(node.types, node.params))
            self.emit(f"{ret} {node.name}({sig}) {{")
            self.indent_level += 1
            for st in node.body:
                self.generate(st)
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
            t = self.infer_type(node.value, {})
            self.emit(f"{t} {node.target.id} = {expr};")

        # COMANDOS SIMPLES
            # Traduções diretas dos comandos break, continue, e pass.
            # O pass vira um comentário, já que não tem equivalente em C.
        elif isinstance(node, Break):
            self.emit("break;")
        elif isinstance(node, Continue):
            self.emit("continue;")
        elif isinstance(node, Pass):
            self.emit("// pass")
        # Comentário Python → comentário C
        elif isinstance(node, Comment):
            # emitir com // prefixo
            self.emit(f"// {node.text}")

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
        # STRING
        elif isinstance(expr, String):
            # imprime a aspa junto
            return expr.value
        elif isinstance(expr, UnaryOp):
            operand = self.generate_expr(expr.operand)
            return f"{expr.op}{operand}"
        # Função chamada
        elif isinstance(expr, FunctionCall):
            args = ', '.join(self.generate_expr(arg) for arg in expr.args)  # Gera os argumentos
            return f"{expr.name}({args})"
        # ERROS
            # Erro para expressões não tratadas
        else:
            raise NotImplementedError(f"Expressão não tratada: {type(expr).__name__}")
