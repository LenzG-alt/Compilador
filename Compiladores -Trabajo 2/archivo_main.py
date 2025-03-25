import ply.lex as lex

# Definición de tokens
tokens = (
    'oSUMA', 'oRESTA', 'oMULT', 'oDIV', 'oRESIDUO',
    'oOR', 'oAND', 'oMAYOR', 'oMENOR', 'oIGUAL', 'oDIFF',
    'oDot', 'oComa', 'oSemi_coma',
    'corchLEFT', 'corchRIGHT', 'parLEFT', 'parRIGHT', 'keyLEFT', 'keyRIGHT',
    'for', 'while', 'return', 'do',
    'in', 'out',
    'void', 'main', 'print',
    'if', 'else', 'false', 'true',
    'INT', 'float', 'bool', 'string',
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
t_oIGUAL = r'=' # Igual a
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

def t_for(t):
    r'\bfor\b'
    t.type = 'for'
    return t

def t_while(t):
    r'\bwhile\b'
    t.type = 'while'
    return t

def t_return(t):
    r'\breturn\b'
    t.type = 'return'
    return t
def t_do(t):
    r'\bdo\b'
    t.type = 'do'
    return t

t_in = r'\bIn\b'
t_out = r'\bOut\b'

def t_void(t):
    r'\bvoid\b'
    t.type = 'void'
    return t

def t_main(t):
    r'\bvmain\b'
    t.type = 'main'
    return t

def t_print(t):
    r'\bprint\b'
    t.type = 'print'
    return t

def t_if(t):
    r'\bif\b'
    t.type = 'if'
    return t

def t_else(t):
    r'\belse\b'
    t.type = 'else'
    return t

def t_false(t):
    r'\bfalse\b'
    t.type = 'false'
    return t

def t_true(t):
    r'\btrue\b'
    t.type = 'true'
    return t

def t_INT(t):
    r'\bint\b'
    t.type = 'INT'
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

def leer_archivo(archivo):
    try:
        with open(archivo, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"El archivo {archivo} no se encuentra.")
        return None

# Función para escribir los tokens en un archivo
def escribir_tokens_en_archivo(tokens, archivo_salida):
    with open(archivo_salida, 'w') as f:
        for token in tokens:
            f.write(f"Token: {token.type}, Valor: {token.value}, Línea: {token.lineno}\n")

# Leer los datos desde el archivo 'data.txt'
data = leer_archivo("c:/Users/arapa/Documents/Compilador/data.txt")
#data = leer_archivo("data.txt")
#data = leer_archivo("ejem1.txt")
#data = leer_archivo("ejem2.txt")
#data = leer_archivo("ejem3.txt")

# Si el archivo se leyó correctamente, pasamos los datos al lexer
if data:
    lexer.input(data)

    # Crear una lista para guardar los tokens
    tokens_generados = []

    # Generar los tokens
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_generados.append(tok)

    # Escribir los tokens en un archivo de salida
    escribir_tokens_en_archivo(tokens_generados, 'tokens_salida.txt')

    print("Los tokens han sido escritos en 'tokens_salida.txt'.")