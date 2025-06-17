import ply.yacc as yacc
from Lexer import tokens, lexer

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
    p[0] = ('program', p[1])

def p_funciones(p):
    '''funciones : funcion funciones
                 | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_funcion(p):
    '''funcion : tipo ID funcion_rest
               | MAIN LPAREN RPAREN bloque'''
    if len(p) == 4:
        p[0] = ('function', p[1], p[2], p[3])
    else:
        p[0] = ('main_function', p[4])

def p_funcion_rest(p):
    '''funcion_rest : inicializacion SEMI
                    | LPAREN parametros RPAREN bloque'''
    if len(p) == 3:
        p[0] = ('var_declaration', p[1])
    else:
        p[0] = ('function_declaration', p[2], p[4])

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
    pass

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

parser = yacc.yacc()