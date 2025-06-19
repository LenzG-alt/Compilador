import ply.lex as lex
import os

# === Reserved Words ===
# Dictionary mapping reserved words to their token types.
reserved = {
    'int': 'INT_TYPE',   # Changed to avoid conflict with INT_NUM literal
    'float': 'FLOAT_TYPE', # Changed to avoid conflict with FLOAT_NUM literal
    'bool': 'BOOL_TYPE',
    'string': 'STRING_TYPE',
    'void': 'VOID_TYPE',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'main': 'MAIN',
    'return': 'RETURN',
    'print': 'PRINT',
    'true': 'TRUE_LITERAL', # Changed to be specific
    'false': 'FALSE_LITERAL',# Changed to be specific
}

# === List of Token Names ===
# Includes literals, operators, delimiters, and reserved words.
tokens = [
    # Identifiers
    'ID',

    # Literals
    'INT_NUM', 'FLOAT_NUM',
    'STRING_LITERAL',
    
    # Operators
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',          # Arithmetic
    'EQ', 'NE', 'LT', 'GT', 'LE', 'GE',                 # Comparison
    'AND', 'OR',                                        # Logical (Note: 'NOT' is often a unary operator)
    'EQUALS',                                           # Assignment
    
    # Delimiters
    'LPAREN', 'RPAREN',   # ( )
    'LBRACE', 'RBRACE',   # { }
    'COMMA', 'SEMI',      # , ;
] + list(reserved.values())

# === Regular Expression Rules for Simple Tokens ===
# Operators
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'

# Comparison Operators
t_EQ = r'=='
t_NE = r'!='
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='

# Logical Operators
t_AND = r'&&'
t_OR = r'\|\|'
# Note: A 'NOT' token (e.g., '!') would typically be defined here if needed.

# Assignment Operator
t_EQUALS = r'='

# Delimiters
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_SEMI = r';'

# === Regular Expression Rules with Action Code ===

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Check if the identifier is a reserved word.
    t.type = reserved.get(t.value, 'ID')
    return t

def t_FLOAT_NUM(t):
    r'\d+\.\d+'
    try:
        t.value = float(t.value)
    except ValueError:
        print(f"Lexer Error: Invalid float literal '{t.value}' at line {t.lineno}")
        t.value = 0.0 # Default value on error
    return t

def t_INT_NUM(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print(f"Lexer Error: Invalid integer literal '{t.value}' at line {t.lineno}")
        t.value = 0 # Default value on error
    return t

def t_STRING_LITERAL(t):
    r'"([^\"]|\.)*"'
    # Remove quotes and handle common escape sequences.
    t.value = t.value[1:-1].replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
    return t

# === Ignored Characters ===
# Whitespace (spaces, tabs)
t_ignore = ' \t'

# Comments (single-line and multi-line)
def t_COMMENT(t):
    r'//.* | /\*(.|\n)*?\*/'
    # r'//.*'  # Matches single-line comments
    # r'/\*(.|\n)*?\*/' # Matches multi-line comments (non-greedy)
    pass # No return value means token is discarded.

# === Line Number Tracking ===
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# === Error Handling Rule ===
# This rule is triggered for any characters not matched by other rules.
def t_error(t):
    message = f"Lexical Error: Illegal character '{t.value[0]}' at line {t.lineno}, position {t.lexpos}."

    # Try to get the full line for context
    line_start = t.lexer.lexdata.rfind('\n', 0, t.lexpos) + 1
    line_end = t.lexer.lexdata.find('\n', t.lexpos)
    if line_end < 0:
        line_end = len(t.lexer.lexdata)
    error_line_context = t.lexer.lexdata[line_start:line_end].strip()

    full_error_message = f"{message}\nContext: \"{error_line_context}\""
    
    # It's good practice for the lexer/parser to log errors to a designated error stream or file.
    # This was previously writing to "salida/errores_lexicos.txt".
    # We'll ensure this path is correct and directory exists.
    error_file_path = "salida/errores_lexicos.txt"
    os.makedirs(os.path.dirname(error_file_path), exist_ok=True)
    with open(error_file_path, "a", encoding="utf-8") as f_err:
        f_err.write(full_error_message + "\n\n")

    print(full_error_message) # Also print to stdout for immediate visibility
    
    t.lexer.skip(1) # Skip the illegal character and continue.

# === Build the Lexer ===
lexer = lex.lex()

# --- Helper function for testing the lexer (optional) ---
def test_lexer(input_string):
    """
    Feeds input_string to the lexer and prints the tokens.
    """
    lexer.input(input_string)
    print("\n--- Lexer Tokens ---")
    while True:
        tok = lexer.token()
        if not tok:
            break # No more input
        print(f"  Type: {tok.type}, Value: '{tok.value}', Line: {tok.lineno}, Pos: {tok.lexpos}")
    print("--- End of Lexer Tokens ---")

# Example usage (remove or comment out for production):
# if __name__ == '__main__':
#     # Clear previous lexical errors for test run
#     if os.path.exists("salida/errores_lexicos.txt"):
#         os.remove("salida/errores_lexicos.txt")
#     os.makedirs("salida", exist_ok=True)
#
#     data = """
#     int count = 10;
#     float amount = 20.5;
#     string name = "Test";
#     if (count > 5) {
#         print(name + " " + true); // Example using 'true'
#     }
#     // This is a comment
#     /* Multi-line
#        comment */
#     int err = 10$; // lexical error here
#     """
#     test_lexer(data)
#
#     data2 = "void main() { int x = 1; }"
#     test_lexer(data2)
