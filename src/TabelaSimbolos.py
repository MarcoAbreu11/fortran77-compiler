import sys
from AST import *

def construir_tabela(ast):
    if not isinstance(ast, CompilationUnit):
        erro('O nó raiz da AST não é uma CompilationUnit.')
    
    tabela = {
        'program' : processar_programa(ast.program),
        'functions' : {}
    }

    for funcao in ast.functions:
        nome_funcao, instrucao_funcao = processar_funcao(funcao)

        tabela['functions'][nome_funcao] = instrucao_funcao

        tipo_parametros = [p['type'] for p in instrucao_funcao['params']]

        tabela['program']['symbols'][nome_funcao] = {
            'type' : instrucao_funcao['return_type'],
            'kind' : 'function_ref',
            'params' : tipo_parametros,
            'return_type' : instrucao_funcao["return_type"]
        }
    
    return tabela

def processar_funcao(funcao):
    if not isinstance(funcao, FunctionDef):
        erro("Esperado nó Funcao.")
 
    nome_f = funcao.name
 
   
    params_lista = []
    locals_dict = {}
 
    for p in funcao.params:
        if not isinstance(p, Parametros):
            erro(f"Parâmetro inválido na função '{nome_f}'.")
        entrada = {"type": None, "kind": "param"}
        locals_dict[p.name] = entrada
        params_lista.append({"name": p.name, "type": None, "kind": "param"})
 
    locals_dict[nome_f] = {
        "type": funcao.return_type,
        "kind": "return_var"
    }
 
    labels = recolher_labels(funcao.body)
 
    for instrucao in funcao.body:
        if isinstance(instrucao, Declaration):
            registar_declaracao(
                instrucao,
                locals_dict,
                escopo_nome = nome_f,
                params_lista = params_lista
            )
 
    for p in params_lista:
        if p["type"] is None:
            erro(f"Parâmetro '{p['name']}' da função '{nome_f}' nunca foi declarado com tipo.")
 
    escopo_f = {
        "return_type": funcao.return_type,
        "params": params_lista,
        "locals": locals_dict,
        "labels": labels
    }
 
    return nome_f, escopo_f



def processar_programa(programa):
    if not isinstance(programa, Program):
        erro('Esperado nó Programa.')
    
    escopo = {
        'name' : programa.name,
        'symbols' : {}
    }

    escopo['labels'] = recolher_labels(programa.body)

    for instrucao in programa.body:
        if isinstance(instrucao, Declaration):
            registar_declaracao(instrucao, escopo['symbols'], programa.name)
    
    return escopo

def registar_declaracao(declaracao, symbols, escopo_nome, params_lista=None):
    tipo = declaracao.decl_type
 
    for var in declaracao.variables:
 
        if isinstance(var, tuple):
            nome, tamanho = var
            kind = "array"
        else:
            nome = var
            kind = "scalar"
 
        if nome in symbols:
            existente = symbols[nome]
 
            if existente["kind"] == "param":
                existente["type"] = tipo
                for p in params_lista:
                    if p["name"] == nome:
                        p["type"] = tipo
                        break
                continue

            elif existente["kind"] == "return_var":
                erro(f"'{nome}' é a variável de retorno da função '{escopo_nome}' e não pode ser redeclarada.")
 
            else:
                erro(f"Variável '{nome}' declarada mais do que uma vez no escopo '{escopo_nome}'.")
 
        entrada = {"type": tipo, "kind": kind}
        if kind == "array":
            entrada["size"] = tamanho
 
        symbols[nome] = entrada


def recolher_labels(instrucoes):
    labels = set()
 
    def visitar(lista):
        for instrucao in lista:
            if isinstance(instrucao, Label):
                if instrucao.label in labels:
                    erro(f"Label '{instrucao.label}' definido mais do que uma vez no mesmo escopo.")
                labels.add(instrucao.label)
            elif isinstance(instrucao, If):
                visitar(instrucao.then_body)
                visitar(instrucao.else_body)
            elif isinstance(instrucao, DoLoop):
                visitar(instrucao.body)
 
    visitar(instrucoes)
    return labels


def erro(aviso):
    print(aviso)
    sys.exit(1)
