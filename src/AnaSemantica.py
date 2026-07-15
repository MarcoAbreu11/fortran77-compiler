import sys
from AST import *

def analisar(ast, tabela):
    if not isinstance(ast, CompilationUnit):
        erro("O nó raiz da AST não é uma CompilationUnit.")
    
    analisar_programa(ast.program, tabela)

    nomes_funcoes = set(tabela['functions'].keys())
    for funcao in ast.functions:
        analisar_funcao(funcao, tabela, nomes_funcoes)

    return ast

def analisar_programa(programa, tabela):
    escopo = tabela['program']
    symbols = escopo['symbols']
    labels = escopo['labels']

    programa.body = analisar_instrucoes(programa.body, symbols, labels, tabela, dentro_funcao = False, nome_funcao_atual = None)

def analisar_funcao(funcao, tabela, nomes_funcoes):
    escopo = tabela['functions'][funcao.name]
    symbols = escopo['locals']
    labels = escopo['labels']

    funcao.body = analisar_instrucoes(funcao.body, symbols, labels, tabela, dentro_funcao = True, nome_funcao_atual = funcao.name)

    if not tem_return(funcao.body):
        erro(f"Função '{funcao.name}' não tem RETURN.")

def analisar_instrucoes(instrucoes, symbols, labels, tabela, dentro_funcao, nome_funcao_atual):
    nova_lista = []
 
    for instrucao in instrucoes:
        resultado = analisar_instrucao(
            instrucao, symbols, labels, tabela, dentro_funcao, nome_funcao_atual
        )
        nova_lista.append(resultado)
 
    return nova_lista

def analisar_instrucao(instrucao, symbols, labels, tabela, dentro_funcao, nome_funcao_atual):
    if isinstance(instrucao, Label):
        return instrucao

    if isinstance(instrucao, Declaration):
        return instrucao

    if isinstance(instrucao, Assign):
        return analisar_atribuicao(instrucao, symbols, labels, tabela, dentro_funcao, nome_funcao_atual)
    
    if isinstance(instrucao, If):
        return analisar_if(instrucao, symbols, labels, tabela, dentro_funcao, nome_funcao_atual)

    if isinstance(instrucao, DoLoop):
        return analisar_do(instrucao, symbols, labels, tabela, dentro_funcao, nome_funcao_atual)

    if isinstance(instrucao, Goto):
        return analisar_goto(instrucao, labels)
    
    if isinstance(instrucao, Print):
        return analisar_print(instrucao, symbols, labels, tabela, dentro_funcao, nome_funcao_atual)
    
    if isinstance(instrucao, Read):
        return analisar_read(instrucao, symbols, tabela, dentro_funcao, nome_funcao_atual)
    
    if isinstance(instrucao, Return):
        if not dentro_funcao:
            erro("RETURN fora de uma função.")
        return instrucao

    erro(f"Instrução desconhecida: {type(instrucao).__name__}")

def analisar_atribuicao(instrucao, symbols, labels, tabela, dentro_funcao, nome_funcao_atual):
    ref = instrucao.target

    if not isinstance(ref, Referencia):
        erro("Target de atribuição não é uma Referencia.")
    
    nome = ref.nome

    if nome not in symbols:
        erro(f"Variável '{nome}' usada sem declaração.")

    entrada = symbols[nome]
    kind = entrada["kind"]

    if kind == "param":
        erro(f"Não é permitido atribuir ao parâmetro '{nome}'.")

    elif kind in ("scalar", "return_var"):
        if ref.args:
            erro(f"'{nome}' é escalar mas está a ser usado como array.")
        instrucao.target = Var(nome, entrada["type"])
    
    elif kind == "array":
        if not ref.args:
            erro(f"'{nome}' é um array mas está a ser usado como escalar.")

        if len(ref.args) != 1:
            erro(f"Array '{nome}' tem de ter exatamente um índice.")
        
        indice = analisar_expressao(ref.args[0], symbols, tabela, dentro_funcao, nome_funcao_atual)

        if tipo_expressao(indice) != "integer":
            erro(f"Índice do array '{nome}' tem de ser inteiro.")
        
        instrucao.target = ArrayAccess(nome, indice, entrada["type"])
 
    elif kind == "function_ref":
        erro(f"'{nome}' é uma função e não pode ser target de atribuição.")
 
    else:
        erro(f"Kind desconhecido '{kind}' para '{nome}'.")
 
    instrucao.value = analisar_expressao(
        instrucao.value, symbols, tabela, dentro_funcao, nome_funcao_atual
    )
 
    return instrucao  

def analisar_if(instrucao, symbols, labels, tabela, dentro_funcao, nome_funcao_atual):
    instrucao.condition = analisar_expressao(
        instrucao.condition, symbols, tabela, dentro_funcao, nome_funcao_atual
    )
 
    tipo_cond = tipo_expressao(instrucao.condition)
    if tipo_cond != "logical":
        erro(f"Condição do IF tem de ser lógica, mas é '{tipo_cond}'.")
 
    instrucao.then_body = analisar_instrucoes(
        instrucao.then_body, symbols, labels, tabela, dentro_funcao, nome_funcao_atual
    )
    instrucao.else_body = analisar_instrucoes(
        instrucao.else_body, symbols, labels, tabela, dentro_funcao, nome_funcao_atual
    )
 
    return instrucao

def analisar_do(instrucao, symbols, labels, tabela, dentro_funcao, nome_funcao_atual):
    nome_var = instrucao.var

    if nome_var not in symbols:
        erro(f"Variável de controlo '{nome_var}' do DO não declarada.")

    if symbols[nome_var]["type"] != "integer":
        erro(f"Variável de controlo '{nome_var}' do DO tem de ser inteira.")
 
    instrucao.start = analisar_expressao(
        instrucao.start, symbols, tabela, dentro_funcao, nome_funcao_atual
    )
    instrucao.end = analisar_expressao(
        instrucao.end, symbols, tabela, dentro_funcao, nome_funcao_atual
    )
    instrucao.step = analisar_expressao(
        instrucao.step, symbols, tabela, dentro_funcao, nome_funcao_atual
    )
 
    instrucao.body = analisar_instrucoes(
        instrucao.body, symbols, labels, tabela, dentro_funcao, nome_funcao_atual
    )
 
    return instrucao

def analisar_goto(instrucao, labels):
    if instrucao.label not in labels:
        erro(f"GOTO para label '{instrucao.label}' que não existe no escopo.")
    return instrucao

def analisar_print(instrucao, symbols, labels, tabela, dentro_funcao, nome_funcao_atual):
    novos_items = []
    for item in instrucao.items:
        if isinstance(item, StringLiteral):
            novos_items.append(item)
        else:
            novos_items.append(
                analisar_expressao(item, symbols, tabela, dentro_funcao, nome_funcao_atual)
            )
    instrucao.items = novos_items
    return instrucao

def analisar_read(instrucao, locals, tabela, dentro_funcao, nome_funcao_atual):
    novos_targets = []
    for ref in instrucao.targets:
        if not isinstance(ref, Referencia):
            erro("Target de READ não é uma Referencia.")
 
        nome = ref.nome
        if nome not in locals:
            erro(f"Variável '{nome}' usada em READ sem declaração.")
 
        entrada = locals[nome]
        kind = entrada["kind"]

        if kind == "param":
            erro(f"Não é permitido fazer READ para o parâmetro '{nome}'.")
            
        elif kind in ("scalar", "return_var"):
            if ref.args:
                erro(f"'{nome}' é escalar mas está a ser usado como array em READ.")
            novos_targets.append(Var(nome, entrada["type"]))
 
        elif kind == "array":
            if not ref.args:
                erro(f"'{nome}' é um array mas está a ser usado como escalar em READ.")

            if len(ref.args) != 1:
                erro(f"Array '{nome}' tem de ter exatamente um índice.")

            indice = analisar_expressao(ref.args[0], locals, tabela, dentro_funcao, nome_funcao_atual)

            if tipo_expressao(indice) != "integer":
                erro(f"Índice do array '{nome}' tem de ser inteiro.")

            novos_targets.append(ArrayAccess(nome, indice, entrada["type"]))
 
        else:
            erro(f"READ apenas suportado para escalares e arrays, não para '{kind}'.")
 
    instrucao.targets = novos_targets
    return instrucao

def analisar_expressao(expr, symbols, tabela, dentro_funcao, nome_funcao_atual):
    if isinstance(expr, IntLiteral):
        return expr
 
    if isinstance(expr, RealLiteral):
        return expr
 
    if isinstance(expr, LogicalLiteral):
        return expr
 
    if isinstance(expr, StringLiteral):
        return expr
 
    if isinstance(expr, Referencia):
        return resolver_referencia(expr, symbols, tabela, dentro_funcao, nome_funcao_atual)
 
    if isinstance(expr, BinOp):
        expr.left = analisar_expressao(expr.left, symbols, tabela, dentro_funcao, nome_funcao_atual)
        expr.right = analisar_expressao(expr.right, symbols, tabela, dentro_funcao, nome_funcao_atual)
        expr.result_type = tipo_binop(expr.op, expr.left, expr.right)
        return expr
 
    if isinstance(expr, UnaryOp):
        expr.operand = analisar_expressao(expr.operand, symbols, tabela, dentro_funcao, nome_funcao_atual)
        expr.result_type = tipo_unaryop(expr.op, expr.operand)
        return expr
    
    if isinstance(expr, Mod):
        expr.left = analisar_expressao(expr.left, symbols, tabela, dentro_funcao, nome_funcao_atual)
        expr.right = analisar_expressao(expr.right, symbols, tabela, dentro_funcao, nome_funcao_atual)
        if tipo_expressao(expr.left) != "integer":
            erro("Primeiro argumento de MOD tem de ser inteiro.")
        if tipo_expressao(expr.right) != "integer":
            erro("Segundo argumento de MOD tem de ser inteiro.")
        expr.result_type = "integer"
        return expr
 
    erro(f"Expressão desconhecida: {type(expr).__name__}")

def resolver_referencia(ref, symbols, tabela, dentro_funcao, nome_funcao_atual):
    nome = ref.nome
 
    if nome not in symbols:
        erro(f"'{nome}' usada sem declaração.")
 
    entrada = symbols[nome]
    kind = entrada["kind"]
 
    if kind in ("scalar", "param", "return_var"):
        if ref.args:
            erro(f"'{nome}' é escalar mas está a ser usado com argumentos.")
        return Var(nome, entrada["type"])
 
    if kind == "array":
        if not ref.args:
            erro(f"'{nome}' é um array mas está a ser usado como escalar.")

        if len(ref.args) != 1:
            erro(f"Array '{nome}' tem de ter exatamente um índice.")

        indice = analisar_expressao(ref.args[0], symbols, tabela, dentro_funcao, nome_funcao_atual)

        if tipo_expressao(indice) != "integer":
            erro(f"Índice do array '{nome}' tem de ser inteiro.")
        
        return ArrayAccess(nome, indice, entrada["type"])
 
    if kind == "function_ref":
        if nome == nome_funcao_atual:
            erro(f"Recursão não permitida: função '{nome}' chama-se a si própria.")
 
        info_funcao = tabela["functions"][nome]
        params_esperados = info_funcao["params"]
 
        if len(ref.args) != len(params_esperados):
            erro(f"Função '{nome}' espera {len(params_esperados)} argumento(s), "
                 f"mas recebeu {len(ref.args)}.")
 
        args_resolvidos = []
        for i, (arg, param) in enumerate(zip(ref.args, params_esperados)):
            arg_resolvido = analisar_expressao(arg, symbols, tabela, dentro_funcao, nome_funcao_atual)
            tipo_arg = tipo_expressao(arg_resolvido)
            tipo_param = param["type"]

            if tipo_arg != tipo_param:
                erro(f"Argumento {i+1} de '{nome}' tem tipo '{tipo_arg}' "
                     f"mas esperava '{tipo_param}'.")
            
            args_resolvidos.append(arg_resolvido)
 
        return FunctionCall(nome, args_resolvidos, entrada["type"])
 
    erro(f"Kind desconhecido '{kind}' para '{nome}'.")

def tipo_expressao(expr):
 
    if isinstance(expr, IntLiteral):
        return "integer"
    
    if isinstance(expr, RealLiteral):
        return "real"
    
    if isinstance(expr, LogicalLiteral):
        return "logical"
    
    if isinstance(expr, StringLiteral):
        return "string"
    
    if isinstance(expr, Var):
        return expr.var_type
    
    if isinstance(expr, ArrayAccess):
        return expr.array_type
    
    if isinstance(expr, FunctionCall):
        return expr.result_type
    
    if isinstance(expr, BinOp):
        return expr.result_type
    
    if isinstance(expr, UnaryOp):
        return expr.result_type
    
    if isinstance(expr, Mod):
        return expr.result_type
 
    erro(f"Não foi possível determinar o tipo de: {type(expr).__name__}")

def tipo_binop(op, esquerda, direita):
    tipo_e = tipo_expressao(esquerda)
    tipo_d = tipo_expressao(direita)

    if op in ("AND", "OR"):
        if tipo_e != "logical" or tipo_d != "logical":
            erro(f"Operador '{op}' requer operandos lógicos, mas tem '{tipo_e}' e '{tipo_d}'.")
        return "logical"
 
    if op in ("==", "!=", "<", "<=", ">", ">="):
        if tipo_e != tipo_d:
            erro(f"Operador '{op}' requer operandos do mesmo tipo, mas tem '{tipo_e}' e '{tipo_d}'.")
        return "logical"
 
    if op in ("+", "-", "*", "/"):
        if tipo_e != tipo_d:
            erro(f"Operador '{op}' requer operandos do mesmo tipo, mas tem '{tipo_e}' e '{tipo_d}'.")

        if tipo_e not in ("integer", "real"):
            erro(f"Operador '{op}' não suportado para tipo '{tipo_e}'.")
        return tipo_e
 
    erro(f"Operador binário desconhecido: '{op}'.")

def tipo_unaryop(op, operando):
    tipo = tipo_expressao(operando)
 
    if op == "NOT":
        if tipo != "logical":
            erro(f"Operador '.NOT.' requer operando lógico, mas tem '{tipo}'.")
        return "logical"
 
    if op == "-":
        if tipo not in ("integer", "real"):
            erro(f"Operador unário '-' não suportado para tipo '{tipo}'.")
        return tipo
 
    erro(f"Operador unário desconhecido: '{op}'.")

def tem_return(instrucoes):
    for instrucao in instrucoes:
        if isinstance(instrucao, Return):
            return True
        if isinstance(instrucao, If):
            if tem_return(instrucao.then_body) or tem_return(instrucao.else_body):
                return True
    return False

def erro(aviso):
    print(aviso)
    sys.exit(1)