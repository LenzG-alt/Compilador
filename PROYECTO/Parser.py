import ply.yacc as yacc
from .Lexer import tokens, lexer

# Precedence rules for operators
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
)

def p_programa(p):
    '''programa : funciones'''
    # print(f"DEBUG: p_programa entered, p[1] from funciones is {p[1] if len(p) > 1 else 'N/A'}") # Minimized for ScopeChecker test
    p[0] = ('program', p[1])

def p_funciones(p):
    '''funciones : funcion_or_main funciones
                 | funcion_or_main'''
    # print(f"DEBUG: p_funciones entered, len(p)={len(p)}") # Minimized for ScopeChecker test
    if len(p) == 3: # funcion_or_main funciones
        p[0] = [p[1]] + p[2]
        # print(f"DEBUG: p_funciones (recursive) assigned p[0]=[{p[1]}] + {p[2]}") # Minimized
    else: # funcion_or_main (len(p) == 2)
        p[0] = [p[1]]
        # print(f"DEBUG: p_funciones (base) assigned p[0]=[{p[1]}]") # Minimized

def p_funcion_or_main(p):
    '''funcion_or_main : regular_function
                       | main_function_def'''
    # print(f"DEBUG: p_funcion_or_main entered, p[1] is {p[1]}") # Minimized for ScopeChecker test
    p[0] = p[1] # Pass through the result

def p_regular_function(p):
    '''regular_function : tipo ID LPAREN parametros RPAREN bloque'''
    # print(f"DEBUG: p_regular_function for ID {p[2]} entered. tipo={p[1]}") # Minimized for ScopeChecker test
    p[0] = ('function', p[1], p[2], p[4], p[6]) # AST: (type, name, params, block)
    # print(f"DEBUG: p_regular_function assigned p[0]={p[0]}") # Minimized

def p_main_function_def(p):
    '''main_function_def : VOID MAIN LPAREN parametros RPAREN bloque'''
    # print(f"DEBUG: p_main_function_def entered.") # Minimized for ScopeChecker test
    p[0] = ('main_function', p[4], p[6]) # AST: (params, block) void is implicit
    # print(f"DEBUG: p_main_function_def assigned p[0]={p[0]}") # Minimized

# Old p_funcion and p_funcion_rest are effectively removed by not being defined below.
# Make sure p_tipo, p_parametros, p_bloque are still defined as they are used.
# (They are defined later in the file, so they should be fine)

def p_parametros(p):
    '''parametros : parametro parametros_rest
                  | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_parametros_rest(p):
    '''parametros_rest : COMMA parametro parametros_rest
                       | empty'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_parametro(p):
    '''parametro : tipo ID'''
    p[0] = ('param', p[1], p[2])

def p_bloque(p):
    '''bloque : LBRACE instrucciones RBRACE'''
    p[0] = ('block', p[2])

def p_instrucciones(p):
    '''instrucciones : instruccion instrucciones
                     | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_instruccion(p):
    '''instruccion : declaracion SEMI
                   | asignacion SEMI
                   | If
                   | While
                   | For
                   | Return
                   | Print'''
    p[0] = p[1]

def p_declaracion(p):
    '''declaracion : tipo ID inicializacion'''
    p[0] = ('declaration', p[1], p[2], p[3])

def p_inicializacion(p):
    '''inicializacion : EQUALS exp
                      | empty'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None

def p_asignacion(p):
    '''asignacion : ID EQUALS exp'''
    p[0] = ('assignment', p[1], p[3])

def p_If(p):
    '''If : IF LPAREN exp RPAREN bloque Else'''
    p[0] = ('if', p[3], p[5], p[6])

def p_Else(p):
    '''Else : ELSE bloque
            | empty'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None

def p_While(p):
    '''While : WHILE LPAREN exp RPAREN bloque'''
    p[0] = ('while', p[3], p[5])

def p_For(p):
    '''For : FOR LPAREN asignacion SEMI exp SEMI asignacion RPAREN bloque'''
    p[0] = ('for', p[3], p[5], p[7], p[9])

def p_Return(p):
    '''Return : RETURN exp_opt SEMI'''
    p[0] = ('return', p[2])

def p_exp_opt(p):
    '''exp_opt : exp
               | empty'''
    p[0] = p[1]

def p_Print(p):
    '''Print : PRINT LPAREN exp RPAREN SEMI'''
    p[0] = ('print', p[3])

def p_tipo(p):
    '''tipo : INT
            | FLOAT
            | BOOL
            | STRING
            | VOID'''
    p[0] = p[1]

def p_exp(p):
    '''exp : E'''
    p[0] = p[1]

def p_E(p):
    '''E : C E_rest'''
    if p[2] is None:
        p[0] = p[1]
    else:
        p[0] = ('or', p[1], p[2])

def p_E_rest(p):
    '''E_rest : OR C E_rest
              | empty'''
    if len(p) == 4:
        if p[3] is None:
            p[0] = p[2]
        else:
            p[0] = ('or', p[2], p[3])
    else:
        p[0] = None

def p_C(p):
    '''C : R C_rest'''
    if p[2] is None:
        p[0] = p[1]
    else:
        p[0] = ('and', p[1], p[2])

def p_C_rest(p):
    '''C_rest : AND R C_rest
              | empty'''
    if len(p) == 4:
        if p[3] is None:
            p[0] = p[2]
        else:
            p[0] = ('and', p[2], p[3])
    else:
        p[0] = None

def p_R(p):
    '''R : T R_rest'''
    if p[2] is None:
        p[0] = p[1]
    else:
        p[0] = (p[2][0], p[1], p[2][1])

def p_R_rest(p):
    '''R_rest : EQ T R_rest
              | NE T R_rest
              | LT T R_rest
              | GT T R_rest
              | LE T R_rest
              | GE T R_rest
              | empty'''
    if len(p) == 4:
        if p[3] is None:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], (p[3][0], p[2], p[3][1]))
    else:
        p[0] = None

def p_T(p):
    '''T : F T_rest'''
    if p[2] is None:
        p[0] = p[1]
    else:
        p[0] = (p[2][0], p[1], p[2][1])

def p_T_rest(p):
    '''T_rest : PLUS F T_rest
              | MINUS F T_rest
              | empty'''
    if len(p) == 4:
        if p[3] is None:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], (p[3][0], p[2], p[3][1]))
    else:
        p[0] = None

def p_F(p):
    '''F : A F_rest'''
    if p[2] is None:
        p[0] = p[1]
    else:
        p[0] = (p[2][0], p[1], p[2][1])

def p_F_rest(p):
    '''F_rest : TIMES A F_rest
              | DIVIDE A F_rest
              | MOD A F_rest
              | empty'''
    if len(p) == 4:
        if p[3] is None:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], (p[3][0], p[2], p[3][1]))
    else:
        p[0] = None

def p_A(p):
    '''A : LPAREN exp RPAREN
         | ID llamada_func
         | INT_NUM
         | FLOAT_NUM
         | STRING_LITERAL
         | TRUE
         | FALSE'''
    if len(p) == 4:
        p[0] = p[2]
    elif len(p) == 3:
        p[0] = ('call', p[1], p[2]) if p[2] is not None else ('id', p[1])
    else:
        if p.slice[1].type == 'STRING_LITERAL':
            p[0] = ('string', p[1])
        elif p.slice[1].type in ['INT_NUM', 'FLOAT_NUM']:
            p[0] = ('number', p[1])
        else:  # TRUE or FALSE
            p[0] = ('bool', p[1] == 'true')

def p_llamada_func(p):
    '''llamada_func : LPAREN lista_args RPAREN
                    | empty'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = None

def p_lista_args(p):
    '''lista_args : exp lista_args_rest
                  | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_lista_args_rest(p):
    '''lista_args_rest : COMMA exp lista_args_rest
                       | empty'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_empty(p):
    'empty :'
    p[0] = None # Explicitly set p[0] for empty rules

def p_error(p):
    if p:
        error_msg = f"Error sintáctico en línea {p.lineno}: Token inesperado '{p.value}' de tipo '{p.type}'"
        line_start = lexer.lexdata.rfind('\n', 0, p.lexpos) + 1
        line_end = lexer.lexdata.find('\n', p.lexpos)
        if line_end < 0:
            line_end = len(lexer.lexdata)
        error_line = lexer.lexdata[line_start:line_end]
        marker = ' ' * (p.lexpos - line_start) + '^'
        
        with open("salida/errores_sintacticos.txt", "a", encoding="utf-8") as error_file:
            error_file.write(f"{error_msg}\n{error_line}\n{marker}\n\n")
    else:
        error_msg = "Error sintáctico: Fin de archivo inesperado"
        with open("salida/errores_sintacticos.txt", "a", encoding="utf-8") as error_file:
            error_file.write(f"{error_msg}\n")

parser = yacc.yacc(debug=True) # Removed errorlog and debuglog for now to ensure tool stability