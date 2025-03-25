import ply.lex as lex

# Definición de tokens
tokens = (
    'oSUMA', 'oRESTA', 'oMULT', 'oDIV', 'oRESIDUO',
    'oOR', 'oAND', 'oMAYOR', 'oMENOR', 'oIGUAL', 'oDIFF',
    'oDot', 'oComa', 'oSemi_coma',
    'corchLEFT', 'corchRIGHT', 'parLEFT', 'parRIGHT', 'keyLEFT', 'keyRIGHT',
    'For', 'While', 'Return', 'Do',
    'In', 'Out',
    'Void', 'Main', 'Print',
    'If', 'Else', 'false', 'True',
    'int', 'float', 'bool', 'string',
    'NUMBER', 'new_line', 'variable_float', 'variable_bool', 'variable_int', 'literal', 'Id'
)

# Definición de las expresiones regulares para los tokens
t_oSUMA = r'\+'
t_oRESTA = r'\-'
t_oMULT = r'\*'
t_oDIV = r'/'
t_oRESIDUO = r'%'

t_oOR = r'\|\|'  # OR lógico
t_oAND = r'&&'   # AND lógico
t_oMAYOR = r'>'  # Mayor que
t_oMENOR = r'<'  # Menor que
t_oIGUAL = r'==' # Igual a
t_oDIFF = r'!='  # Diferente de

t_oDot = r'\.'
t_oComa = r','
t_oSemi_coma = r';'

t_corchLEFT = r'\{'
t_corchRIGHT = r'\}'
t_parLEFT = r'\('
t_parRIGHT = r'\)'
t_keyLEFT = r'\['
t_keyRIGHT = r'\]'

def t_For(t):
    r'\bFor\b'
    t.type = 'For'
    return t

def t_While(t):
    r'\bWhile\b'
    t.type = 'While'
    return t

def t_Return(t):
    r'\bReturn\b'
    t.type = 'Return'
    return t
def t_Do(t):
    r'\bDo\b'
    t.type = 'Do'
    return t

t_In = r'\bIn\b'
t_Out = r'\bOut\b'

def t_Void(t):
    r'\bVoid\b'
    t.type = 'Void'
    return t

def t_Main(t):
    r'\bMain\b'
    t.type = 'Main'
    return t

def t_Print(t):
    r'\bPrint\b'
    t.type = 'Print'
    return t

def t_If(t):
    r'\bIf\b'
    t.type = 'If'
    return t

def t_Else(t):
    r'\bPrint\b'
    t.type = 'Else'
    return t

def t_false(t):
    r'\bfalse\b'
    t.type = 'false'
    return t

def t_True(t):
    r'\bTrue\b'
    t.type = 'True'
    return t

def t_int(t):
    r'\bint\b'
    t.type = 'int'
    return t


def t_float(t):
    r'\bfloat\b'
    t.type = 'float'
    return t


def t_bool(t):
    r'\bbool\b'
    t.type = 'bool'
    return t


def t_string(t):
    r'\bstring\b'
    t.type = 'string'
    return t
# Nuevos tokens
t_variable_float = r'[0-9]+\.[0-9]*'  # Números decimales (flotantes)
t_variable_bool = r'[01]'  # 0 o 1, valores booleanos
t_variable_int = r'[1-9]+'  # Números enteros positivos
t_literal = r'\".*?\"'  # Cadenas de texto (literales)
t_Id = r'[a-zA-Z][a-zA-Z0-9]*'  # Identificadores

# Token para números
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Manejo de saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejo de errores léxicos
def t_error(t):
    print(f"Illegal Character '{t.value[0]}'")
    t.lexer.skip(1)

# Creación del lexer
lexer = lex.lex()

# Datos de entrada para probar
data = '''int x = 5;
float y = 3.14;
bool isTrue = 1;
bool isFalse = 0;
string saludo = "Hola Mundo";
Print saludo;

Void main() {
    int a = 3;
    float b = 4.5;
    bool result = a > b;
    Print a + b;
    
    If a > b {
        Print "A es mayor que B";
    } Else {
        Print "B es mayor que A";
    }
    
    For int i = 0; i < 5; i++ {
        Print i;
    }
}'''

# Pasar los datos de entrada al lexer
lexer.input(data)

# Imprimir los tokens reconocidos
while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)