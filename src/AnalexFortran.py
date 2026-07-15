import ply.lex as lex
import sys

PalavrasReservadas = {
    'program': 'PROGRAM', 'end': 'END', 'integer': 'INTEGER',
    'real': 'REAL', 'logical': 'LOGICAL', 'if': 'IF', 'then': 'THEN',
    'else': 'ELSE', 'endif': 'ENDIF', 'do': 'DO', 'continue': 'CONTINUE',
    'goto': 'GOTO', 'read': 'READ', 'print': 'PRINT', 'return': 'RETURN',
    'function': 'FUNCTION', 'subroutine': 'SUBROUTINE', 'mod': 'MOD', 'character' : 'CHARACTER' 
}

tokens = [
    'ID', 'INTEGER_LIT', 'REAL_LIT', 'STRING',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER',
    'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
    'AND', 'OR', 'NOT',
    'ASSIGN', 'LPAREN', 'RPAREN', 'COMMA',
    'TRUE', 'FALSE'
] + list(PalavrasReservadas.values())

def t_REAL_LIT(t):
    r'\d+\.\d*([eE][+-]?\d+)?'
    t.value = float(t.value)
    return t

def t_INTEGER_LIT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r"'[^']*'"
    t.value = t.value[1:-1]
    return t

def t_PLUS(t):
    r'\+'
    return t

def t_MINUS(t):
    r'\-'
    return t

def t_POWER(t):
    r'\*\*'
    return t

def t_TIMES(t):
    r'\*'
    return t

def t_DIVIDE(t):
    r'\/'
    return t

def t_EQ(t):
    r'\.[Ee][Qq]\.'
    return t

def t_NE(t):
    r'\.[Nn][Ee]\.'
    return t

def t_LT(t):
    r'\.[Ll][Tt]\.'
    return t

def t_LE(t):
    r'\.[Ll][Ee]\.'
    return t

def t_GT(t):
    r'\.[Gg][Tt]\.'
    return t

def t_GE(t):
    r'\.[Gg][Ee]\.'
    return t

def t_AND(t):
    r'\.[Aa][Nn][Dd]\.'
    return t

def t_OR(t):
    r'\.[Oo][Rr]\.'
    return t

def t_NOT(t):
    r'\.[Nn][Oo][Tt]\.'
    return t

def t_ASSIGN(t):
    r'\='
    return t

def t_LPAREN(t):
    r'\('
    return t

def t_RPAREN(t):
    r'\)'
    return t

def t_COMMA(t):
    r'\,'
    return t

def t_TRUE(t):
    r'\.[Tt][Rr][Uu][Ee]\.'
    return t

def t_FALSE(t):
    r'\.[Ff][Aa][Ll][Ss][Ee]\.'
    return t

def t_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = PalavrasReservadas.get(t.value.lower(), 'ID')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t\r'

def t_comment(t):
    r'!.*'
    pass

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lineno}")
    sys.exit(1)

lexer = lex.lex()