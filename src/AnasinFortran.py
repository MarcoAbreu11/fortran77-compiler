import ply.yacc as yacc
from AnalexFortran import *  
from AST import *
from TabelaSimbolos import *          
from AnaSemantica import *
from codegen import *
import subprocess
import sys
from pathlib import Path

# inicio
def p_inicio(p):
    "inicio : programa lista_funcoes"
    p[0] = CompilationUnit(p[1], p[2])

# lista funções
def p_lista_funcoes_multi(p):
    "lista_funcoes : lista_funcoes funcao"
    p[0] = p[1] + [p[2]]

def p_lista_funcoes_empty(p):
    "lista_funcoes : vazio"
    p[0] = []

# programa
def p_programa(p):
    "programa : PROGRAM ID lista_instrucao END"
    p[0] = Program(p[2].upper(), p[3])

# função
def p_funcao(p):
    "funcao : tipo FUNCTION ID LPAREN lista_parametros RPAREN lista_instrucao END"
    p[0] = FunctionDef(p[3].upper(), p[1], p[5], p[7])

# lista parametros
def p_lista_parametros_multi(p):
    "lista_parametros : lista_parametros_ext"
    p[0] = p[1]

def p_lista_parametros_single(p):
    "lista_parametros : vazio"
    p[0] = []

# lista parametros extensão
def p_lista_parametros_ext_multi(p):
    "lista_parametros_ext : lista_parametros_ext COMMA ID"
    p[0] = p[1] + [Parametros(p[3].upper(), None)]

def p_lista_parametros_ext_single(p):
    "lista_parametros_ext : ID"
    p[0] = [Parametros(p[1].upper(), None)]

# lista instrução
def p_lista_instrucao_multi(p):
    "lista_instrucao : lista_instrucao instrucao"
    if isinstance(p[2], list):
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1] + [p[2]]

def p_lista_instrucao_single(p):
    "lista_instrucao : instrucao"
    if isinstance(p[1], list):
        p[0] = p[1]
    else:
        p[0] = [p[1]]

# instrunção
def p_instrucao_multi(p):
    "instrucao : instrucao_sem_label"
    p[0] = p[1]

def p_instrucao_single(p):
    "instrucao : label instrucao_sem_label"
    p[0] = [Label(p[1]), p[2]]

# instrucao sem label
def p_instrucao_sem_label_single1(p):
    "instrucao_sem_label : declaracao"
    p[0] = p[1]

def p_instrucao_sem_label_single2(p):
    "instrucao_sem_label : atribuicao"
    p[0] = p[1]

def p_instrucao_sem_label_single3(p):
    "instrucao_sem_label : comando_if"
    p[0] = p[1]

def p_instrucao_sem_label_single4(p):
    "instrucao_sem_label : comando_do"
    p[0] = p[1]

def p_instrucao_sem_label_single5(p):
    "instrucao_sem_label : comando_goto"
    p[0] = p[1]

def p_instrucao_sem_label_single6(p):
    "instrucao_sem_label : comando_print"
    p[0] = p[1]

def p_instrucao_sem_label_single7(p):
    "instrucao_sem_label : comando_read"
    p[0] = p[1]

def p_instrucao_sem_label_single8(p):
    "instrucao_sem_label : comando_continue"
    p[0] = p[1]

def p_instrucao_sem_label_single9(p):
    "instrucao_sem_label : comando_return"
    p[0] = p[1]

# label
def p_label(p):
    "label : INTEGER_LIT"
    p[0] = p[1]

# declaração
def p_declaracao(p):
    "declaracao : tipo lista_variaveis"
    p[0] = Declaration(p[1], p[2])

# tipo
def p_tipo_single1(p):
    "tipo : INTEGER"
    p[0] = "integer"
 
def p_tipo_single2(p):
    "tipo : REAL"
    p[0] = "real"

def p_tipo_single3(p):
    "tipo : LOGICAL"
    p[0] = "logical"

# lista variaveis
def p_lista_variaveis_multi(p):
    "lista_variaveis : lista_variaveis COMMA variavel_decl"
    p[0] = p[1] + [p[3]]

def p_lista_variaveis_single(p):
    "lista_variaveis : variavel_decl"
    p[0] = [p[1]]

# variavel_decl
def p_variavel_decl_multi(p):
    "variavel_decl : ID LPAREN INTEGER_LIT RPAREN"
    p[0] = (p[1].upper(), p[3])

def p_variavel_decl_single(p):
    "variavel_decl : ID"
    p[0] = p[1].upper()

# atribuição
def p_atribuicao(p):
    "atribuicao : referencia ASSIGN expressao"
    p[0] = Assign(p[1], p[3])

# referencia
def p_referencia_multi(p):
    "referencia : ID LPAREN lista_argumentos RPAREN"
    p[0] = Referencia(p[1].upper(), p[3])

def p_referencia_single(p):
    "referencia : ID"
    p[0] = Referencia(p[1].upper())

# comando if
def p_comando_if_multi1(p):
    "comando_if : IF expressao THEN lista_instrucao ELSE lista_instrucao ENDIF"
    p[0] = If(p[2], p[4], p[6])

def p_comando_if_multi2(p):
    "comando_if : IF expressao THEN lista_instrucao ENDIF"
    p[0] = If(p[2], p[4])

# comando do
def p_comando_do(p):
    "comando_do : DO label ID ASSIGN expressao COMMA expressao opt_step lista_instrucao label CONTINUE"
    if p[2] != p[10]:
        print(f'O label do inicio do Do {p[2]} é diferente do label final {p[10]}')
        sys.exit(1)
    p[0] = DoLoop(p[3].upper(), p[5], p[7], p[8], p[9])

# passo opticional
def p_opt_step_multi(p):
    "opt_step : COMMA expressao"
    p[0] = p[2]

def p_opt_step_empty(p):
    "opt_step : vazio"
    p[0] = p[1]

# comando goto
def p_comando_goto(p):
    "comando_goto : GOTO label"
    p[0] = Goto(p[2])

def p_comando_continue(p):
    "comando_continue : CONTINUE"
    p[0] = Continue()

# comando_return
def p_comando_return(p):
    "comando_return : RETURN"
    p[0] = Return()

# comando print
def p_comando_print(p):
    "comando_print : PRINT TIMES COMMA lista_prints"
    p[0] = Print(p[4])

# lista prints
def p_lista_prints_multi(p):
    "lista_prints : lista_prints COMMA elemento_print"
    p[0] = p[1] + [p[3]]

def p_lista_prints_single(p):
    "lista_prints : elemento_print"
    p[0] = [p[1]]

# elemento print
def p_elemento_print_single1(p):
    "elemento_print : STRING"
    p[0] = StringLiteral(p[1])

def p_elemento_print_single2(p):
    "elemento_print : expressao"
    p[0] = p[1]

# comando read
def p_comando_read(p):
    "comando_read : READ TIMES COMMA lista_reads"
    p[0] = Read(p[4])

# lista reads
def p_lista_reads_multi(p):
    "lista_reads : lista_reads COMMA referencia"
    p[0] = p[1] + [p[3]]

def p_lista_reads_single(p):
    "lista_reads : referencia"
    p[0] = [p[1]]

# expressao
def p_expressao_multi(p):
    "expressao : expressao OR termo_logico"
    p[0] = BinOp('OR', p[1], p[3])

def p_expressao_single(p):
    "expressao : termo_logico"
    p[0] = p[1]

# termo logico
def p_termo_logico_multi(p):
    "termo_logico : termo_logico AND fator_logico"
    p[0] = BinOp('AND', p[1], p[3])

def p_termo_logico_single(p):
    "termo_logico : fator_logico"
    p[0] = p[1]

# fator logico
def p_fator_logico_multi(p):
    "fator_logico : NOT fator_logico"
    p[0] = UnaryOp('NOT', p[2])

def p_fator_logico_single(p):
    "fator_logico : comparacao"
    p[0] = p[1]

# comparacao
def p_comparacao_multi1(p):
    "comparacao : expressao_aritmetica EQ expressao_aritmetica"
    p[0] = BinOp('==', p[1], p[3])

def p_comparacao_multi2(p):
    "comparacao : expressao_aritmetica NE expressao_aritmetica"
    p[0] = BinOp('!=', p[1], p[3])

def p_comparacao_multi3(p):
    "comparacao : expressao_aritmetica LT expressao_aritmetica"
    p[0] = BinOp('<', p[1], p[3])

def p_comparacao_multi4(p):
    "comparacao : expressao_aritmetica LE expressao_aritmetica"
    p[0] = BinOp('<=', p[1], p[3])

def p_comparacao_multi5(p):
    "comparacao : expressao_aritmetica GT expressao_aritmetica"
    p[0] = BinOp('>', p[1], p[3])
def p_comparacao_multi6(p):
    "comparacao : expressao_aritmetica GE expressao_aritmetica"
    p[0] = BinOp('>=', p[1], p[3])

def p_comparacao_single(p):
    "comparacao : expressao_aritmetica"
    p[0] = p[1]

# expressao aritmetica
def p_expressao_aritmetica_multi1(p):
    "expressao_aritmetica : expressao_aritmetica PLUS termo"
    p[0] = BinOp('+', p[1], p[3])

def p_expressao_aritmetica_multi2(p):
    "expressao_aritmetica : expressao_aritmetica MINUS termo"
    p[0] = BinOp('-', p[1], p[3])

def p_expressao_aritmetica_single(p):
    "expressao_aritmetica : termo"
    p[0] = p[1]

# termo 
def p_termo_multi1(p):
    "termo : termo TIMES fator"
    p[0] = BinOp('*', p[1], p[3])

def p_termo_multi2(p):
    "termo : termo DIVIDE fator"
    p[0] = BinOp('/', p[1], p[3])

def p_termo_single(p):
    "termo : fator"
    p[0] = p[1]

# fator
def p_fator_multi(p):
    "fator : MINUS fator"
    p[0] = UnaryOp('-', p[2])

def p_fator_single(p):
    "fator : primario"
    p[0] = p[1]

# primario 
def p_primario_single1(p):
    "primario : INTEGER_LIT"
    p[0] = IntLiteral(p[1])

def p_primario_single2(p):
    "primario : REAL_LIT"
    p[0] = RealLiteral(p[1])

def p_primario_single3(p):
    "primario : TRUE"
    p[0] = LogicalLiteral(True)

def p_primario_single4(p):
    "primario : FALSE"
    p[0] = LogicalLiteral(False)

def p_primario_single5(p):
    "primario : referencia"
    p[0] = p[1]

def p_primario_multi1(p):
    "primario : LPAREN expressao RPAREN"
    p[0] = p[2]

def p_primario_multi2(p):
    "primario : MOD LPAREN expressao COMMA expressao RPAREN"
    p[0] = Mod(p[3], p[5])

# lista argumentos
def p_lista_argumentos_single1(p):
    "lista_argumentos : lista_argumentos_ext"
    p[0] = p[1]

def p_lista_argumentos_single2(p):
    "lista_argumentos : vazio"
    p[0] = []

# lista argumentos extensão
def p_lista_argumentos_ext_multi(p):
    "lista_argumentos_ext : lista_argumentos_ext COMMA expressao"
    p[0] = p[1] + [p[3]]

def p_lista_argumentos_ext_single(p):
    "lista_argumentos_ext : expressao"
    p[0] = [p[1]]

# vazio
def p_vazio(p):
    "vazio :"
    p[0] = None

def p_error(p):
    if p:
        print(f'Erro sintático no token {p.type} ({p.value} na linha {p.lineno})')
        sys.exit(1)
    else:
        print("Erro sintático no fim do input")
        sys.exit(1)

parser = yacc.yacc()

SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent
TESTES_DIR = BASE_DIR / "test"
RESULT_DIR = BASE_DIR / "test_result"
COMPILADOR = SRC_DIR / "AnasinFortran.py"
 
 
def correr_teste(ficheiro_teste: Path) -> str:
    with open(ficheiro_teste, "r", encoding="utf-8") as f:
        codigo_fonte = f.read()
 
    resultado = subprocess.run(
        [sys.executable, str(COMPILADOR)],
        input=codigo_fonte,
        capture_output=True,
        text=True,
    )
 
    if resultado.returncode != 0:
        saida = (
            f"ERRO ao compilar '{ficheiro_teste.name}' "
            f"(codigo de saida {resultado.returncode}):\n"
            f"{resultado.stderr.strip()}\n{resultado.stdout.strip()}"
        ).strip()
    else:
        saida = resultado.stdout
 
    return saida
 
 
def main_testes():
    if not TESTES_DIR.is_dir():
        print(f"Pasta de testes nao encontrada: {TESTES_DIR}")
        sys.exit(1)
 
    RESULT_DIR.mkdir(exist_ok=True)
 
    ficheiros_teste = sorted(p for p in TESTES_DIR.iterdir() if p.is_file())
 
    if not ficheiros_teste:
        print(f"Nenhum ficheiro de teste encontrado em {TESTES_DIR}")
        return
 
    for ficheiro in ficheiros_teste:
        print(f"\n===== {ficheiro.name} =====")
 
        saida = correr_teste(ficheiro)
        print(saida)
 
        ficheiro_resultado = RESULT_DIR / f"{ficheiro.stem}.txt"
        with open(ficheiro_resultado, "w", encoding="utf-8") as f:
            f.write(saida)
 
    print(f"\nResultados guardados em: {RESULT_DIR}")


def compilar(codigo_fonte: str) -> str:
    """Corre o pipeline completo (léxica -> sintática -> semântica -> geração
    de código) sobre o código fonte fornecido e devolve o código objeto."""
    codigo_fonte = codigo_fonte.replace("\r\n", "\n").replace("\r", "\n")

    lexer.lineno = 1
    ast = parser.parse(codigo_fonte, lexer=lexer)

    tabela = construir_tabela(ast)
    ast = analisar(ast, tabela)

    codigo_objeto = generate(ast, tabela)
    return codigo_objeto


def main_compilar():
    """Lê o código fonte a partir do stdin, compila-o e imprime o
    código objeto resultante no terminal."""
    codigo_fonte = sys.stdin.read()
    codigo_objeto = compilar(codigo_fonte)
    print(codigo_objeto)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "-t", "test"):
        main_testes()
    else:
        main_compilar()