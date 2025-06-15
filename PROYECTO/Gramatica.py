import ply.yacc as yacc
from Lexer import tokens

TreeNode = None  # Será inyectado por build_parser

def p_programa(p):
    'programa : funciones mainF'
    p[0] = TreeNode('programa', [p[1], p[2]])

def p_funciones_rec(p):
    'funciones : funcion funciones'
    p[0] = TreeNode('funciones', [p[1], p[2]])

def p_funciones_empty(p):
    'funciones :'
    p[0] = TreeNode('funciones', [TreeNode('ε')])

def p_funcion(p):
    'funcion : tipo ID LPAREN parametros RPAREN bloque'
    p[0] = TreeNode('funcion', [p[1], TreeNode(p[2]), p[4], p[6]])

def p_parametros(p):
    'parametros : parametro parametros_rest'
    p[0] = TreeNode('parametros', [p[1], p[2]])

def p_parametros_empty(p):
    'parametros :'
    p[0] = TreeNode('parametros', [TreeNode('ε')])

def p_parametros_rest(p):
    'parametros_rest : COMMA parametro parametros_rest'
    p[0] = TreeNode('parametros_rest', [p[2], p[3]])

def p_parametros_rest_empty(p):
    'parametros_rest :'
    p[0] = TreeNode('parametros_rest', [TreeNode('ε')])

def p_parametro(p):
    'parametro : tipo ID'
    p[0] = TreeNode('parametro', [p[1], TreeNode(p[2])])

def p_mainF(p):
    'mainF : VOID MAIN LPAREN RPAREN bloque'
    p[0] = TreeNode('main', [p[5]])

def p_tipo(p):
    '''tipo : INT
           | FLOAT
           | BOOL
           | STRING'''
    p[0] = TreeNode('tipo', [TreeNode(p[1])])

def p_bloque(p):
    'bloque : LBRACE instrucciones RBRACE'
    p[0] = TreeNode('bloque', [p[2]])

def p_instrucciones(p):
    'instrucciones : argumento instrucciones'
    p[0] = TreeNode('instrucciones', [p[1], p[2]])

def p_instrucciones_empty(p):
    'instrucciones :'
    p[0] = TreeNode('instrucciones', [TreeNode('ε')])

def p_argumento(p):
    '''argumento : If
                 | While
                 | For
                 | Return
                 | Print
                 | tipo ID declaracion
                 | asignacion'''
    if len(p) == 2:
        p[0] = TreeNode('argumento', [p[1]])
    elif len(p) == 4:
        p[0] = TreeNode('declaracion', [p[1], TreeNode(p[2]), p[3]])
    else:
        p[0] = p[1]

def p_asignacion(p):
    'asignacion : ID EQUALS exp SEMI'
    p[0] = TreeNode('asignacion', [TreeNode(p[1]), TreeNode('='), p[3]])

def p_declaracion_valor(p):
    'declaracion : EQUALS exp SEMI'
    p[0] = TreeNode('declaracion', [TreeNode('='), p[2]])

def p_declaracion_empty(p):
    'declaracion : SEMI'
    p[0] = TreeNode('declaracion vacía')

def p_If(p):
    'If : IF LPAREN exp RPAREN bloque Else'
    p[0] = TreeNode('if', [p[3], p[5], p[6]])

def p_Else(p):
    '''Else : ELSE bloque
            | '''
    if len(p) == 3:
        p[0] = TreeNode('else', [p[2]])
    else:
        p[0] = TreeNode('else', [TreeNode('ε')])

def p_While(p):
    'While : WHILE LPAREN exp RPAREN bloque'
    p[0] = TreeNode('while', [p[3], p[5]])

def p_For(p):
    'For : FOR LPAREN asignacion SEMI exp SEMI asignacion RPAREN bloque'
    p[0] = TreeNode('for', [p[3], p[5], p[7], p[9]])

def p_Return(p):
    'Return : RETURN exp2 SEMI'
    p[0] = TreeNode('return', [p[2]])

def p_exp2(p):
    '''exp2 : exp
           | '''
    if len(p) == 2:
        p[0] = TreeNode('exp2', [p[1]])
    else:
        p[0] = TreeNode('exp2', [TreeNode('ε')])

def p_Print(p):
    'Print : PRINT LPAREN exp RPAREN SEMI'
    p[0] = TreeNode('print', [p[3]])

# Aquí deberías continuar agregando las reglas para exp, E, Eo, C, Co, R, etc.
# ...
def p_exp(p):
    'exp : E'
    p[0] = p[1]

def p_E(p):
    'E : C Eo'
    p[0] = TreeNode('E', [p[1], p[2]])

def p_Eo(p):
    '''Eo : OROR C Eo
          | '''
    if len(p) == 4:
        p[0] = TreeNode('OROR', [p[2], p[3]])
    else:
        p[0] = TreeNode('Eo', [TreeNode('ε')])

def p_C(p):
    'C : R Co'
    p[0] = TreeNode('C', [p[1], p[2]])

def p_Co(p):
    '''Co : AND R Co
          | '''
    if len(p) == 4:
        p[0] = TreeNode('AND', [p[2], p[3]])
    else:
        p[0] = TreeNode('Co', [TreeNode('ε')])

def p_R(p):
    'R : T Ro'
    p[0] = TreeNode('R', [p[1], p[2]])

def p_Ro(p):
    '''Ro : EQ T Ro
          | LT T Ro
          | GT T Ro
          | LE T Ro
          | GE T Ro
          | EQEQ T Ro
          | NE T Ro
          | '''
    if len(p) == 4:
        p[0] = TreeNode(p[1], [p[2], p[3]])
    else:
        p[0] = TreeNode('Ro', [TreeNode('ε')])

def p_T(p):
    'T : F To'
    p[0] = TreeNode('T', [p[1], p[2]])

def p_To(p):
    '''To : PLUS F To
          | MINUS F To
          | '''
    if len(p) == 4:
        p[0] = TreeNode(p[1], [p[2], p[3]])
    else:
        p[0] = TreeNode('To', [TreeNode('ε')])

def p_F(p):
    'F : A Fo'
    p[0] = TreeNode('F', [p[1], p[2]])

def p_Fo(p):
    '''Fo : TIMES A Fo
          | DIVIDE A Fo
          | MOD A Fo
          | '''
    if len(p) == 4:
        p[0] = TreeNode(p[1], [p[2], p[3]])
    else:
        p[0] = TreeNode('Fo', [TreeNode('ε')])

def p_A(p):
    '''A : LPAREN L RPAREN
         | ID B
         | NUM
         | TRUE
         | FALSE'''
    if p[1] == '(':
        p[0] = TreeNode('()', [p[2]])
    elif p.slice[1].type == 'ID':
        p[0] = TreeNode('ID', [TreeNode(p[1]), p[2]])
    else:
        p[0] = TreeNode(str(p[1]))

def p_L(p):
    '''L : E Lo
         | '''
    if len(p) == 3:
        p[0] = TreeNode('L', [p[1], p[2]])
    else:
        p[0] = TreeNode('L', [TreeNode('ε')])

def p_Lo(p):
    '''Lo : COMMA E Lo
          | '''
    if len(p) == 4:
        p[0] = TreeNode(',', [p[2], p[3]])
    else:
        p[0] = TreeNode('Lo', [TreeNode('ε')])

def p_B(p):
    '''B : LPAREN L RPAREN
         | '''
    if len(p) == 4:
        p[0] = TreeNode('B', [p[2]])
    else:
        p[0] = TreeNode('B', [TreeNode('ε')])

def p_error(p):
    if p:
        print(f"Error de sintaxis en token: {p.type} (valor: {p.value})")
    else:
        print("Error de sintaxis: entrada incompleta o vacía")



def build_parser(TreeNodeClass):
    global TreeNode
    TreeNode = TreeNodeClass
    global parser
    #parser = yacc.yacc()
    parser = yacc.yacc(outputdir="salida")

    