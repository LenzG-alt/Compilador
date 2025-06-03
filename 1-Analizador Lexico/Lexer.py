import ply.lex as lex

# === Palabras reservadas ===
reserved = {
    'int': 'INT',
    'float': 'FLOAT',
    'bool': 'BOOL',
    'string': 'STRING',
    'void': 'VOID',
    'main': 'MAIN',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'return': 'RETURN',
    'print': 'PRINT',
    'true': 'TRUE',
    'false': 'FALSE'
}

# === Tokens ===
tokens = [
    'ID', 'NUM',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'EQUALS', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE', 'EQEQ',
    'OROR', 'AND',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'COMMA', 'SEMI'
] + list(reserved.values())

# === Reglas de expresiones regulares ===
t_EQUALS = r'='
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_MOD     = r'%'
t_EQ      = r'='
t_NE      = r'!='
t_LT      = r'<'
t_GT      = r'>'
t_LE      = r'<='
t_GE      = r'>='
t_EQEQ    = r'=='
t_OROR    = r'\|\|'
t_AND     = r'&'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_COMMA   = r','
t_SEMI    = r';'

# === Reglas para identificadores y números ===
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUM(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

# === Ignorar espacios y tabulaciones ===
t_ignore = ' \t'

# === Contar líneas ===
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# === Manejo de errores ===
def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# === Construir el analizador léxico ===
lexer = lex.lex()
