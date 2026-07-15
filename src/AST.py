# No inicial
class AST:
    pass

# No raiz
class CompilationUnit(AST):
    def __init__(self, programa, funcoes = None):
        if funcoes == None:
            funcoes = []
        self.program = programa
        self.functions = funcoes
 
    def __repr__(self):
        return f"CompilationUnit(program = {self.program!r}, functions = {self.functions!r})"

class Program(AST):
    def __init__(self, nome, lista_instrucao = None):
        if lista_instrucao == None:
            lista_instrucao = []

        self.name = nome
        self.body = lista_instrucao 
 
    def __repr__(self):
        return f"Program(name = {self.name!r}, body = {self.body!r})"

class FunctionDef(AST):
    def __init__(self, nome, tipo_retorno, parametros = None, lista_instrucao = None):
        if lista_instrucao == None:
            lista_instrucao = []

        if parametros == None:
            parametros = []
        
        self.name = nome
        self.return_type = tipo_retorno
        self.params = parametros
        self.body = lista_instrucao
    
    def __repr__(self):
        return (f"FunctionDef(name = {self.name!r}, return_type = {self.return_type!r}, " f"params = {self.params!r}, body = {self.body!r})")

class Parametros(AST):
    def __init__(self, nome, tipo_parametro):
        self.name = nome
        self.param_type = tipo_parametro
    
    def __repr__(self):
        return f"Param(name = {self.name!r}, param_type = {self.param_type!r})"

class Declaration(AST):
    def __init__(self, tipo_variavel, variaveis):
        if variaveis == None:
            variaveis = []
        
        self.decl_type = tipo_variavel
        self.variables = variaveis
    
    def __repr__(self):
         return f"Declaration(decl_type = {self.decl_type!r}, variables = {self.variables!r})"

# intrucoes / comandos
class Assign(AST):
    def __init__(self, referencia, expressao):
        self.target  = referencia
        self.value = expressao

    def __repr__(self):
        return f"Assign(target = {self.target!r}, value = {self.value!r})"

class If(AST):
    def __init__(self, condicao, then_instrucoes = None, else_instrucoes = None):
        if then_instrucoes == None:
            then_instrucoes = []

        if else_instrucoes == None:
            else_instrucoes = []
        
        self.condition = condicao
        self.then_body = then_instrucoes
        self.else_body = else_instrucoes

    def __repr__(self):
        return (f"If(condition = {self.condition!r}, " f"then_body = {self.then_body!r}, else_body = {self.else_body!r})")


class DoLoop(AST):
    def __init__(self, var, inicio, fim, passo = None, instrucoes = None):
        if passo == None:
            passo = IntLiteral(1)
        
        if instrucoes == None:
            instrucoes = []
        
        self.var = var
        self.start = inicio
        self.end = fim
        self.step = passo
        self.body = instrucoes

    def __repr__(self):
        return (f"DoLoop(var = {self.var!r}, start = {self.start!r}, " f"end = {self.end!r}, step = {self.step!r}, body = {self.body!r})")
    
class Goto(AST):
    def __init__(self, label):
        self.label = label
    
    def __repr__(self):
        return f"Goto(label = {self.label!r})"

class Label(AST):
    def __init__(self, numero):
        self.label = numero
    
    def __repr__(self):
        return f"Label(label = {self.label!r})"

class Return(AST):
    def __repr__(self):
        return "Return()" 

class Continue(AST):
    def __repr__(self):
        return "Continue()" 

class Print(AST):
    def __init__(self, lista_prints = None):
        if lista_prints == None:
            lista_prints = []
        
        self.items = lista_prints
    
    def __repr__(self):
        return f"Print(items = {self.items!r})"


class Read(AST):
    def __init__(self, lista_reads = None):
        if lista_reads == None:
            lista_reads = []
        
        self.targets = lista_reads
    
    def __repr__(self):
        return f"Read(targets = {self.targets!r})"

# Referencias a variaveis / arrays / funcoes
class Var(AST):
    def __init__(self, nome, tipo_variavel = None):
        self.name = nome
        self.var_type = tipo_variavel
        self.result_type = tipo_variavel
 
    def __repr__(self):
        return f"Var(name = {self.name!r}, var_type = {self.var_type!r})"
        
class ArrayAccess(AST):
    def __init__(self, nome, indice, tipo_array = None):
        self.name = nome
        self.index = indice
        self.array_type = tipo_array
        self.result_type = tipo_array
    
    def __repr__(self):
        return (f"ArrayAccess(name = {self.name!r}, index = {self.index!r}, " f"array_type = {self.array_type!r})")

class FunctionCall(AST):
    def __init__(self, nome, argumentos = None, tipo_retorno = None):
        if argumentos == None:
            argumentos = []

        self.name = nome
        self.args = argumentos
        self.result_type = tipo_retorno
 
    def __repr__(self):
        return (f"FunctionCall(name = {self.name!r}, args = {self.args!r}, " f"result_type = {self.result_type!r})")

# Expressoes
class BinOp(AST):
    def __init__(self, operacao, esquerda, direita, tipo_resultado = None):
        self.op = operacao
        self.left = esquerda
        self.right = direita
        self.result_type = tipo_resultado
    
    def __repr__(self):
        return (f"BinOp(op = {self.op!r}, left = {self.left!r}, " f"right = {self.right!r}, result_type = {self.result_type!r})")

class UnaryOp(AST):
    def __init__(self, operacao, operando, tipo_resultado = None):
        self.op = operacao
        self.operand = operando
        self.result_type = tipo_resultado
    
    def __repr__(self):
        return (f"UnaryOp(op = {self.op!r}, operand = {self.operand!r}, result_type = {self.result_type!r})")

class Mod(AST):
    def __init__(self, esquerda, direita, tipo_resultado = "integer"):
        self.left = esquerda
        self.right = direita
        self.result_type = tipo_resultado
    
    def __repr__(self):
        return (f"Mod(left = {self.left!r}, right = {self.right!r}, " f"result_type = {self.result_type!r})")

# Literais
class IntLiteral(AST):
    def __init__(self, valor):
        self.value = valor
        self.result_type = "integer"

    def __repr__(self):
        return f"IntLiteral(value = {self.value!r})"

class RealLiteral(AST):
    def __init__(self, valor):
        self.value = valor
        self.result_type = "real"
    
    def __repr__(self):
        return f"RealLiteral(value = {self.value!r})"

class LogicalLiteral(AST):
    def __init__(self, valor):
        self.value = bool(valor)
        self.result_type = "logical"

    def __repr__(self):
        return f"LogicalLiteral(value = {self.value!r})"
 
    def como_inteiro(self):
        if self.value:
            return 1
        else:
            return 0

class StringLiteral(AST):
    def __init__(self, valor):
        self.value = str(valor)
        self.result_type = "string"
 
    def __repr__(self):
        return f"StringLiteral(value = {self.value!r})"

class Referencia(AST):
    def __init__(self, nome, args = None):
        if args == None:
            args = []
        self.nome = nome
        self.args = args
    
    def __repr__(self):
        return f"Ref(name = {self.nome!r}, args = {self.args!r})"