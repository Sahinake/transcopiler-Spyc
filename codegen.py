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
        # Mapa de tipos de variáveis definidas no main
        self.main_env = {}

    # Função Emit
        # Adiciona uma linha ao código C, com a indentação apropriada (4 espaços por nível).
        # É uma função auxiliar que facilita a geração de código identado corretamente.
    def emit(self, line):
        self.result.append("    " * self.indent_level + line)

    # Inferência de tipo simples para retorno e variáveis
    def infer_type(self, expr, env):
        from ast_nodes import Number, BinOp, Name, FunctionCall, String
        # input() sempre retorna string
        if isinstance(expr, FunctionCall) and expr.name == 'input':
            return 'char*'
        if isinstance(expr, Number):
            return 'float' if isinstance(expr.value, float) else 'int'
        if isinstance(expr, String):
            return 'char*'
        if isinstance(expr, BinOp):
            t1 = self.infer_type(expr.left, env)
            t2 = self.infer_type(expr.right, env)
            return 'float' if 'float' in (t1, t2) else 'int'
        if isinstance(expr, Name):
            # procura nas variáveis do main e depois no ambiente local
            return self.main_env.get(expr.id, env.get(expr.id, 'int'))
        return 'int'

    # Função Principal: Generate
        # Essa função navega na AST e chama recursivamente o código necessário para cada tipo de nó.
        # Ela trata os comandos e estruturas do programa (e não expressões).
    def generate(self, node, env=None, is_main=False):
        if env is None:
            env = {}
        # PROGRAM
            # Itera sobre todos os comandos do programa e gera código para cada um.
            # No final, retorna todo o código como uma string com quebras de linha.
        if isinstance(node, Program):
            # Cabeçalhos
            self.result.append("#include <stdio.h>")
            self.result.append("#include <string.h>")
            self.result.append("")

            # Separar definições de função e statements do main
            funcs, mains = [], []
            for s in node.statements:
                (funcs if isinstance(s, FunctionDef) else mains).append(s)

            # Inferir tipos de retorno das funções
            func_env = {}
            for f in funcs:
                env = {p: t for p, t in zip(f.params, f.types)}
                ret_t = 'void'
                for st in f.body:
                    if isinstance(st, Return):
                        ret_t = self.infer_type(st.value, env)
                        break
                func_env[f.name + '_ret'] = ret_t

            # Gerar funções
            for f in funcs:
                self.generate(f)
                self.result.append("")

            # Gerar main
            self.emit("int main() {")
            self.indent_level += 1

            # Declaração antecipada de variáveis do main (sem inicialização)
            for var, t in self.main_env.items():
                self.emit(f"{t} {var};")

            for s in mains:
                self.generate(s, self.main_env, is_main=True)
                
            self.emit("return 0;")
            self.indent_level -= 1
            self.emit("}")
            return "\n".join(self.result)
        # FUNCTION DEF
            # Gera a definição de uma função em C.
            # O nome da função vem de node.name, e o corpo é gerado recursivamente com node.body.
            # O corpo da função é indentado.
        elif isinstance(node, FunctionDef):
            # Cria o escopo local a partir dos parâmetros
            local_env = {p: t for p, t in zip(node.params, node.types)}
            
            # Inferir tipo de retorno
            ret = 'void'
            for st in node.body:
                if isinstance(st, Return):
                    ret = self.infer_type(st.value, local_env)
                    break
            
            # Geração da assinatura
            sig = ', '.join(f"{t} {p}" for t, p in zip(node.types, node.params))
            self.emit(f"{ret} {node.name}({sig}) {{")
            self.indent_level += 1

            # Gerar o corpo da função com o escopo local
            for st in node.body:
                self.generate(st, local_env)  # <-- usa o escopo

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
            local_env = env.copy()
            for stmt in node.body:
                self.generate(stmt, local_env)
            self.indent_level -= 1
            if node.else_body:
                self.emit("} else {")
                self.indent_level += 1
                local_env_else = env.copy()
                for stmt in node.else_body:
                    self.generate(stmt, local_env_else)
                self.indent_level -= 1
            self.emit("}")

        # WHILE
            # Traduz um laço while.
            # A condição é passada para generate_expr.
            # O corpo é gerado com recursão e indentado.
        elif isinstance(node, While):
            self.emit(f"while ({self.generate_expr(node.condition)}) {{")
            self.indent_level += 1
            local_env_while = env.copy()
            for stmt in node.body:
                self.generate(stmt, local_env_while)
            self.indent_level -= 1
            self.emit("}")

        # ASSIGNMENT
            # Traduz uma atribuição.
            # Usa generate_expr para avaliar o lado direito.
            # Aqui há uma simplificação: toda variável é declarada como int. Isso pode ser melhorado depois, se desejar gerar código com inferência ou tipos diferentes.
        elif isinstance(node, Assignment):
            var = node.target.id
            if isinstance(node.value, FunctionCall) and node.value.name == 'input':
                t = self.infer_type(node.value, env)
                if var not in env:
                    self.emit(f"char {var}[256];")
                env[var] = t
                if is_main:
                    self.main_env[var] = t
                if node.value.args:
                    prompt = self.generate_expr(node.value.args[0])
                    self.emit(f"printf({prompt});")
                self.emit(f"scanf(\"%255s\", {var});")
            else:
                expr = self.generate_expr(node.value)
                t = self.infer_type(node.value, env)
                if var not in env:
                    self.emit(f"{t} {var} = {expr};")
                else:
                    self.emit(f"{var} = {expr};")
                env[var] = t
                if is_main:
                    self.main_env[var] = t

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

        elif isinstance(node, FunctionCall):
            # Mapeamento de print()
            if node.name == 'print':
                specs, vals = [], []
                for arg in node.args:
                    t = self.infer_type(arg, {})
                    if t == 'int': spec = '%d'
                    elif t == 'float': spec = '%f'
                    else: spec = '%s'
                    specs.append(spec)
                    vals.append(self.generate_expr(arg))
                fmt = ' '.join(specs) + '\\n'
                args_list = ', '.join(vals)
                self.emit(f"printf(\"{fmt}\", {args_list});")
            else:
                args = ', '.join(self.generate_expr(a) for a in node.args)
                self.emit(f"{node.name}({args});")

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
