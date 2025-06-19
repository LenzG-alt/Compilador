import ply.yacc as yacc
from Lexer import tokens, lexer # Assuming lexer instance is not directly used by yacc here
import os # For error file path management

# --- Operator Precedence ---
# Defines the precedence and associativity of operators.
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    # ('right', 'NOT'), # Example if NOT operator was added
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    # ('right', 'UMINUS'), # Example for unary minus
)

# --- Grammar Rules ---

# Top-level: A program is a list of function definitions (including main).
def p_program(p):
    '''program : declaration_list'''
    # AST: ('program', [declarations])
    # declarations can be function definitions or main function definition.
    p[0] = ('program', p[1])

def p_declaration_list(p):
    '''declaration_list : declaration declaration_list
                        | empty'''
    if len(p) == 3: # declaration declaration_list
        p[0] = [p[1]] + p[2] if p[2] else [p[1]] # p[2] could be empty list from recursive call
    else: # empty
        p[0] = []

def p_declaration(p):
    '''declaration : function_definition
                   | main_function_definition'''
    p[0] = p[1] # Pass through the function or main definition

# Function Definition
def p_function_definition(p):
    '''function_definition : type_specifier ID LPAREN parameter_list RPAREN block'''
    # AST: ('function', type_str, name_str, params_list_node, block_node)
    # params_list_node is ('params', [('param', p_type, p_name), ...])
    p[0] = ('function', p[1], p[2], p[4], p[6])

# Main Function Definition
def p_main_function_definition(p):
    '''main_function_definition : VOID_TYPE MAIN LPAREN parameter_list RPAREN block'''
    # AST: ('main_function', params_list_node, block_node)
    # 'void' return type is implicit.
    p[0] = ('main_function', p[4], p[6])


# Type Specifier (int, float, bool, string, void)
def p_type_specifier(p):
    '''type_specifier : INT_TYPE
                      | FLOAT_TYPE
                      | BOOL_TYPE
                      | STRING_TYPE
                      | VOID_TYPE'''
    p[0] = p[1] # The token value itself (e.g., 'int', 'float')


# Parameter List
def p_parameter_list(p):
    '''parameter_list : parameters_non_empty
                      | empty'''
    # AST: ('params', [('param', type, name), ...]) or ('params', []) if empty
    if p[1] is None: # empty
        p[0] = ('params', [])
    else:
        p[0] = ('params', p[1])

def p_parameters_non_empty(p):
    '''parameters_non_empty : parameter
                            | parameter COMMA parameters_non_empty'''
    if len(p) == 2: # single parameter
        p[0] = [p[1]]
    else: # parameter, parameters_non_empty
        p[0] = [p[1]] + p[3]

def p_parameter(p):
    '''parameter : type_specifier ID'''
    # AST: ('param', type_str, name_str)
    p[0] = ('param', p[1], p[2])


# Block of Statements
def p_block(p):
    '''block : LBRACE statement_list RBRACE'''
    # AST: ('block', [statements_list])
    p[0] = ('block', p[2])

def p_statement_list(p):
    '''statement_list : statement statement_list
                      | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2] if p[2] else [p[1]]
    else:
        p[0] = []


# Statements
def p_statement(p):
    '''statement : variable_declaration_statement
                 | assignment_statement
                 | if_statement
                 | while_statement
                 | for_statement
                 | return_statement
                 | print_statement
                 | expression_statement''' # For function calls as statements
    p[0] = p[1]

def p_variable_declaration_statement(p):
    '''variable_declaration_statement : type_specifier ID optional_initializer SEMI'''
    # AST: ('declaration', type_str, name_str, init_expr_node_or_None)
    p[0] = ('declaration', p[1], p[2], p[3])

def p_optional_initializer(p):
    '''optional_initializer : EQUALS expression
                            | empty'''
    p[0] = p[2] if len(p) == 3 else None

def p_assignment_statement(p):
    '''assignment_statement : ID EQUALS expression SEMI'''
    # AST: ('assignment', name_str, expr_node)
    p[0] = ('assignment', p[1], p[3])

def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN block optional_else'''
    # AST: ('if', condition_expr_node, then_block_node, else_block_node_or_None)
    p[0] = ('if', p[3], p[5], p[6])

def p_optional_else(p):
    '''optional_else : ELSE block
                     | empty'''
    p[0] = p[2] if len(p) == 3 else None

def p_while_statement(p):
    '''while_statement : WHILE LPAREN expression RPAREN block'''
    # AST: ('while', condition_expr_node, block_node)
    p[0] = ('while', p[3], p[5])

def p_for_statement(p):
    '''for_statement : FOR LPAREN for_init SEMI expression SEMI for_update RPAREN block'''
    # AST: ('for', init_node, condition_expr_node, update_node, block_node)
    # init_node and update_node can be declaration or assignment or empty (represented as None).
    p[0] = ('for', p[3], p[5], p[7], p[9])

def p_for_init(p):
    '''for_init : variable_declaration_statement_no_semi
                | assignment_statement_no_semi
                | empty'''
    # variable_declaration_statement_no_semi would be type_specifier ID optional_initializer
    # assignment_statement_no_semi would be ID EQUALS expression
    p[0] = p[1]

def p_variable_declaration_statement_no_semi(p):
    '''variable_declaration_statement_no_semi : type_specifier ID optional_initializer'''
    p[0] = ('declaration', p[1], p[2], p[3])

def p_assignment_statement_no_semi(p):
    '''assignment_statement_no_semi : ID EQUALS expression'''
    p[0] = ('assignment', p[1], p[3])


def p_for_update(p):
    '''for_update : assignment_statement_no_semi
                  | empty'''
    p[0] = p[1]


def p_return_statement(p):
    '''return_statement : RETURN optional_expression SEMI'''
    # AST: ('return', expr_node_or_None)
    p[0] = ('return', p[2])

def p_optional_expression(p):
    '''optional_expression : expression
                           | empty'''
    p[0] = p[1]

def p_print_statement(p):
    '''print_statement : PRINT LPAREN expression RPAREN SEMI'''
    # AST: ('print', expr_node)
    p[0] = ('print', p[3])

def p_expression_statement(p):
    '''expression_statement : expression SEMI'''
    # Typically for function calls that are statements.
    # The expression itself will be ('call', ...)
    p[0] = p[1]


# Expressions (following a common hierarchy for precedence)
# expression -> logical_or_expression
# logical_or_expression -> logical_and_expression ( OR logical_and_expression )*
# logical_and_expression -> equality_expression ( AND equality_expression )*
# equality_expression -> relational_expression ( (EQ | NE) relational_expression )*
# relational_expression -> additive_expression ( (LT | GT | LE | GE) additive_expression )*
# additive_expression -> multiplicative_expression ( (PLUS | MINUS) multiplicative_expression )*
# multiplicative_expression -> primary_expression ( (TIMES | DIVIDE | MOD) primary_expression )*
# primary_expression -> ID | INT_NUM | FLOAT_NUM | STRING_LITERAL | TRUE_LITERAL | FALSE_LITERAL | LPAREN expression RPAREN | function_call

def p_expression(p):
    '''expression : logical_or_expression'''
    p[0] = p[1]

def p_logical_or_expression(p):
    '''logical_or_expression : logical_and_expression
                             | logical_or_expression OR logical_and_expression'''
    if len(p) == 2: p[0] = p[1]
    else: p[0] = ('or', p[1], p[3]) # AST: ('or', left_expr, right_expr)

def p_logical_and_expression(p):
    '''logical_and_expression : equality_expression
                              | logical_and_expression AND equality_expression'''
    if len(p) == 2: p[0] = p[1]
    else: p[0] = ('and', p[1], p[3]) # AST: ('and', left_expr, right_expr)

def p_equality_expression(p):
    '''equality_expression : relational_expression
                           | equality_expression EQ relational_expression
                           | equality_expression NE relational_expression'''
    if len(p) == 2: p[0] = p[1]
    else: p[0] = (p[2].lower(), p[1], p[3]) # AST: ('eq'/'ne', left, right) (using token value for op)

def p_relational_expression(p):
    '''relational_expression : additive_expression
                             | relational_expression LT additive_expression
                             | relational_expression GT additive_expression
                             | relational_expression LE additive_expression
                             | relational_expression GE additive_expression'''
    if len(p) == 2: p[0] = p[1]
    else: p[0] = (p[2].lower(), p[1], p[3]) # AST: ('lt'/'gt'/'le'/'ge', left, right)

def p_additive_expression(p):
    '''additive_expression : multiplicative_expression
                           | additive_expression PLUS multiplicative_expression
                           | additive_expression MINUS multiplicative_expression'''
    if len(p) == 2: p[0] = p[1]
    else: p[0] = ('plus' if p[2] == '+' else 'minus', p[1], p[3]) # AST: ('plus'/'minus', left, right)

def p_multiplicative_expression(p):
    '''multiplicative_expression : primary_expression
                                 | multiplicative_expression TIMES primary_expression
                                 | multiplicative_expression DIVIDE primary_expression
                                 | multiplicative_expression MOD primary_expression'''
    if len(p) == 2: p[0] = p[1]
    else:
        op_map = {'*': 'times', '/': 'divide', '%': 'mod'}
        p[0] = (op_map[p[2]], p[1], p[3]) # AST: ('times'/'divide'/'mod', left, right)

# Primary Expressions
def p_primary_expression_literal(p):
    '''primary_expression : INT_NUM
                          | FLOAT_NUM
                          | STRING_LITERAL
                          | TRUE_LITERAL
                          | FALSE_LITERAL'''
    # AST: ('number', value) for int/float, ('string', value), ('bool', True/False)
    if p.slice[1].type == 'INT_NUM' or p.slice[1].type == 'FLOAT_NUM':
        p[0] = ('number', p[1])
    elif p.slice[1].type == 'STRING_LITERAL':
        p[0] = ('string', p[1])
    elif p.slice[1].type == 'TRUE_LITERAL':
        p[0] = ('bool', True)
    elif p.slice[1].type == 'FALSE_LITERAL':
        p[0] = ('bool', False)

def p_primary_expression_id(p):
    '''primary_expression : ID'''
    # AST: ('id', name_str)
    p[0] = ('id', p[1])

def p_primary_expression_group(p):
    '''primary_expression : LPAREN expression RPAREN'''
    p[0] = p[2] # Pass through the grouped expression

def p_primary_expression_function_call(p):
    '''primary_expression : function_call_expression'''
    p[0] = p[1]

# Function Call (as an expression)
def p_function_call_expression(p):
    '''function_call_expression : ID LPAREN argument_list RPAREN'''
    # AST: ('call', func_name_str, args_list_node)
    # args_list_node is ('args', [arg_expr_node, ...]) or ('args', [])
    p[0] = ('call', p[1], p[3])

def p_argument_list(p):
    '''argument_list : arguments_non_empty
                     | empty'''
    # AST: ('args', [arg_expr_node, ...]) or ('args', []) if empty
    if p[1] is None: # empty
        p[0] = ('args', [])
    else:
        p[0] = ('args', p[1])

def p_arguments_non_empty(p):
    '''arguments_non_empty : expression
                           | expression COMMA arguments_non_empty'''
    if len(p) == 2: # single argument
        p[0] = [p[1]]
    else: # expression, arguments_non_empty
        p[0] = [p[1]] + p[3]


# Empty production rule (for optional parts of grammar)
def p_empty(p):
    'empty :'
    p[0] = None # Or sometimes [] for lists, depending on how it's used.


# Error rule for syntax errors
def p_error(p):
    error_file_path = "salida/errores_sintacticos.txt"
    os.makedirs(os.path.dirname(error_file_path), exist_ok=True)

    if p:
        message = f"Syntax Error: Unexpected token '{p.value}' (type: {p.type}) at line {p.lineno}, position {p.lexpos}."
        # Try to get context of the error line
        line_start = lexer.lexdata.rfind('\n', 0, p.lexpos) + 1
        line_end = lexer.lexdata.find('\n', p.lexpos)
        if line_end < 0:
            line_end = len(lexer.lexdata)
        error_line_context = lexer.lexdata[line_start:line_end].strip()
        full_error_message = f"{message}\nContext: \"{error_line_context}\""
    else:
        full_error_message = "Syntax Error: Unexpected end of input (EOF)."

    with open(error_file_path, "a", encoding="utf-8") as f_err:
        f_err.write(full_error_message + "\n\n")

    print(full_error_message) # Also print to stdout

# Build the parser
# For debugging, can add debug=True, but it's verbose.
# optimize=True can be used for production if tables are stable.
# write_tables=True will generate parsetab.py for faster startups.
parser = yacc.yacc(write_tables=True, debug=False)

# --- Helper for testing (optional) ---
# if __name__ == '__main__':
#     # Clear previous syntax errors for test run
#     if os.path.exists("salida/errores_sintacticos.txt"):
#         os.remove("salida/errores_sintacticos.txt")
#     # Ensure lexer error file is also clear if testing lexer + parser
#     if os.path.exists("salida/errores_lexicos.txt"):
#         os.remove("salida/errores_lexicos.txt")
#     os.makedirs("salida", exist_ok=True)
#
#     test_code_valid = """
#     int add(int a, int b) {
#         return a + b;
#     }
#     void main() {
#         int result = add(5, 10);
#         print(result);
#         if (result > 10) {
#             string msg = "Greater";
#             print(msg);
#         } else {
#             print("Not greater");
#         }
#         for (int i = 0; i < 5; i = i + 1) {
#             print(i);
#         }
#     }
#     """
#     print("\n--- Parsing Valid Code ---")
#     ast = parser.parse(test_code_valid, lexer=lexer) # Pass lexer instance
#     if ast:
#         print("Parsing successful. AST (simplified):")
#         # A full AST print can be very long. Just confirming structure.
#         print(f"Program node: {ast[0]}")
#         print(f"Number of top-level declarations: {len(ast[1])}")
#     else:
#         print("Parsing failed for valid code (unexpected).")
#
#     test_code_syntax_error = """
#     void main() {
#         int x = 5 + ; // Syntax error here
#     }
#     """
#     print("\n--- Parsing Code with Syntax Error ---")
#     ast_err = parser.parse(test_code_syntax_error, lexer=lexer)
#     if not ast_err:
#         print("Parsing correctly failed as expected due to syntax error.")
#     else:
#         print("Parsing succeeded for invalid code (unexpected).")
