import ply.yacc as yacc
from Lexer import tokens

class TreeNode:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []

    def to_dot(self):
        counter = [0]
        lines = ["digraph G {"]

        def add_node(node, parent_id=None):
            node_id = f"node{counter[0]}"
            lines.append(f'{node_id} [label="{node.name}"]')
            current_id = node_id
            counter[0] += 1
            for child in node.children:
                child_id = add_node(child, current_id)
                lines.append(f"{current_id} -> {child_id}")
            return current_id

        add_node(self)
        lines.append("}")
        return "\n".join(lines)

TreeNodeClass = TreeNode
TreeNode = TreeNodeClass

def p_programa(p):
    'programa : funciones mainF'
    p[0] = TreeNode('programa', [p[1], p[2]])

def p_funciones_rec(p):
    'funciones : funcion funciones'
    p[0] = TreeNode('funciones', [p[1], p[2]])

def p_funciones_empty(p):
    'funciones :'
    p[0] = TreeNode('funciones (vacío)')

def p_funcion(p):
    'funcion : tipo ID LPAREN parametros RPAREN bloque'
    p[0] = TreeNode('funcion', [p[1], TreeNode(p[2]), p[4], p[6]])

def p_parametros(p):
    'parametros : parametro parametros_rest'
    p[0] = TreeNode('parametros', [p[1], p[2]])

def p_parametros_empty(p):
    'parametros :'
    p[0] = TreeNode('parametros (vacío)')

def p_parametros_rest(p):
    'parametros_rest : COMMA parametro parametros_rest'
    p[0] = TreeNode('parametros_rest', [p[2], p[3]])

def p_parametros_rest_empty(p):
    'parametros_rest :'
    p[0] = TreeNode('parametros_rest (vacío)')

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
    p[0] = TreeNode('instrucciones (vacío)')

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
    p[0] = TreeNode('asignacion', [TreeNode(p[1]), p[3]])

def p_declaracion_valor(p):
    'declaracion : EQUALS exp SEMI'
    p[0] = TreeNode('= exp', [p[2]])

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
        p[0] = TreeNode('else (vacío)')

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
        p[0] = TreeNode('exp2 (vacío)')

def p_Print(p):
    'Print : PRINT LPAREN exp RPAREN SEMI'
    p[0] = TreeNode('print', [p[3]])

# Aquí deberías continuar agregando las reglas para exp, E, Eo, C, Co, R, etc.
# ...

def p_exp(p):
    'exp : E'
    pass

def p_E(p):
    'E : C Eo'
    pass

def p_Eo(p):
    '''Eo : OROR C Eo
          | '''
    pass

def p_C(p):
    'C : R Co'
    pass

def p_Co(p):
    '''Co : AND R Co
          | '''
    pass

def p_R(p):
    'R : T Ro'
    pass

def p_Ro(p):
    '''Ro : EQ T Ro
          | LT T Ro
          | GT T Ro
          | LE T Ro
          | GE T Ro
          | EQEQ T Ro
          | NE T Ro
          | '''
    pass

def p_T(p):
    'T : F To'
    pass

def p_To(p):
    '''To : PLUS F To
          | MINUS F To
          | '''
    pass

def p_F(p):
    'F : A Fo'
    pass

def p_Fo(p):
    '''Fo : TIMES A Fo
          | DIVIDE A Fo
          | MOD A Fo
          | '''
    pass

def p_A(p):
    '''A : LPAREN L RPAREN
         | ID B
         | NUM
         | TRUE
         | FALSE'''
    pass

def p_L(p):
    '''L : E Lo
         | '''
    pass

def p_Lo(p):
    '''Lo : COMMA E Lo
          | '''
    pass

def p_B(p):
    '''B : LPAREN L RPAREN
         | '''
    pass


def p_error(p):
    if p:
        print(f"Error de sintaxis en token: {p.type} (valor: {p.value})")
    else:
        print("Error de sintaxis: entrada incompleta o vacía")

def build_parser(TreeNodeClass):
    global TreeNode
    TreeNode = TreeNodeClass
    global parser
    parser = yacc.yacc()