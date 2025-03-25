import ply.lex as lex

tokens = (
'oSuma','oResta','oMult','oDiv','oResiduo',
'oOR','oAND','oMayor','oMenor','oIgual','oDiff',
'oDot','oComa','oSemi_coma',
'corchLeft','corchRight','parLeft','parRight','keyLeft','keyRight',
'For','While','Return','Do',
'In','Out',
'Void','Main',
'Print',
'If','Else',
'false','True',
'int',
'float',
'bool',
'string'
    )

t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t' 

def t_error(t):
    print("Illegal Character '%s'" % t.valueÑ[0])
    t.lexer.skip(1)

lexer = lex.lex()

data = '''3+4+10+
-20 *2'''

lexer.input(data)

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)