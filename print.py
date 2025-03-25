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
    'NUMBER', 'new_line'
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

t_For = r'\bFor\b'
t_While = r'\bWhile\b'
t_Return = r'\bReturn\b'
t_Do = r'\bDo\b'

t_In = r'\bIn\b'
t_Out = r'\bOut\b'

t_Void = r'\bVoid\b'
t_Main = r'\bMain\b'
t_Print = r'\bPrint\b'

t_If = r'\bIf\b'
t_Else = r'\bElse\b'
t_false = r'\bfalse\b'
t_True = r'\bTrue\b'

t_int = r'\bint\b'
t_float = r'\bfloat\b'
t_bool = r'\bbool\b'
t_string = r'\bstring\b'

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
int y = 10;
int suma = x + y;
Print suma;

Void main() {
    Print "Hola Mundo";
    int a = 3;
    int b = 4;
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