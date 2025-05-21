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
        # Ambiente para armazenar informações das funções: nome -> {"params_types": [...], "ret_type": "int"/"void"/...}
        self.func_signatures = {}

    # Função Emit
        # Adiciona uma linha ao código C, com a indentação apropriada (4 espaços por nível).
        # É uma função auxiliar que facilita a geração de código identado corretamente.
    def emit(self, line):
        self.result.append("    " * self.indent_level + line)

    # Inferência de tipo simples para retorno e variáveis
    def infer_type(self, expr, env):
        from ast_nodes import Number, BinOp, Name, FunctionCall, String
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
            return self.main_env.get(expr.id, env.get(expr.id, 'int'))
        if isinstance(expr, FunctionCall):
            # Tenta pegar assinatura da função
            sig = self.func_signatures.get(expr.name)
            if sig:
                return sig.get("ret_type", "int")
            return 'int'
        return 'int'
    
    # Função para inferir tipos dos argumentos passados em chamadas de funções em todo o programa
    def infer_function_params_types(self, node):
        # Percorre todos os nós recursivamente e para cada FunctionCall guarda os tipos dos argumentos
        if isinstance(node, FunctionCall):
            # Extrair tipos dos argumentos
            arg_types = [self.infer_type(arg, {}) for arg in node.args]
            # Atualizar assinatura da função, se já existir, confirmar compatibilidade ou expandir
            sig = self.func_signatures.get(node.name)
            if sig is None:
                self.func_signatures[node.name] = {
                    "params_types": arg_types,
                    "ret_type": "int"  # Inicialmente padrão
                }
            else:
                # Ajustar tipos para o mais geral (exemplo: se já tinha int e agora recebe float, muda para float)
                new_types = []
                for i, t in enumerate(arg_types):
                    if i < len(sig["params_types"]):
                        old_t = sig["params_types"][i]
                        if old_t == 'int' and t == 'float':
                            new_types.append('float')
                        else:
                            new_types.append(old_t)
                    else:
                        new_types.append(t)
                sig["params_types"] = new_types

        # Recursão para outros tipos de nó
        if hasattr(node, 'statements'):
            for s in node.statements:
                self.infer_function_params_types(s)
        if hasattr(node, 'body'):
            for s in node.body:
                self.infer_function_params_types(s)
        if hasattr(node, 'args'):
            for a in node.args:
                self.infer_function_params_types(a)
        if hasattr(node, 'value'):
            self.infer_function_params_types(node.value)
        if hasattr(node, 'left'):
            self.infer_function_params_types(node.left)
        if hasattr(node, 'right'):
            self.infer_function_params_types(node.right)
        if hasattr(node, 'condition'):
            self.infer_function_params_types(node.condition)
        if hasattr(node, 'else_body') and node.else_body:
            for s in node.else_body:
                self.infer_function_params_types(s)

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
            # Primeiro: inferir assinaturas das funções pelas chamadas
            self.infer_function_params_types(node)

            # Cabeçalhos
            self.result.append("#include <stdio.h>")
            self.result.append("#include <string.h>")
            self.result.append("")

            # Separar definições de função e statements do main
            funcs, mains = [], []
            for s in node.statements:
                (funcs if isinstance(s, FunctionDef) else mains).append(s)

            # Atualizar assinaturas das funções definidas com base no que foi inferido
            for f in funcs:
                sig = self.func_signatures.get(f.name)
                if sig:
                    f.types = sig["params_types"]
                else:
                    # Caso não haja assinatura inferida, colocar tudo int
                    f.types = ['int'] * len(f.params)
                # Inferir o tipo de retorno
                local_env = {p: t for p, t in zip(f.params, f.types)}
                ret_t = 'void'
                for st in f.body:
                    if isinstance(st, Return):
                        ret_t = self.infer_type(st.value, local_env)
                        break
                self.func_signatures[f.name] = {"params_types": f.types, "ret_type": ret_t}

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
            local_env = {p: t for p, t in zip(node.params, node.types)}
            ret = self.func_signatures.get(node.name, {}).get("ret_type", "void")
            sig = ', '.join(f"{t} {p}" for t, p in zip(node.types, node.params))
            self.emit(f"{ret} {node.name}({sig}) {{")
            self.indent_level += 1
            for st in node.body:
                self.generate(st, local_env)
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
            if node.name == 'print':
                specs, vals = [], []
                for arg in node.args:
                    t = self.infer_type(arg, {})
                    if t == 'int':
                        spec = '%d'
                    elif t == 'float':
                        spec = '%f'
                    else:
                        spec = '%s'
                    specs.append(spec)
                    vals.append(self.generate_expr(arg))
                fmt = ' '.join(specs) + '\\n'
                args_list = ', '.join(vals)
                self.emit(f'printf("{fmt}", {args_list});')
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
