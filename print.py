import ply.lex as lex

tokens = (
'oSUMA','oRESTA','oMULT','oDIV','oRESIDUO',

'oOR','oAND','oMAYOR','oMENOR','oIGUAL','oDIFF',

'oDot','oComa','oSemi_coma',

'corchLEFT','corchRIGHT','parLEFT','parRIGHT','keyLEFT','keyRIGHT',

'For','While','Return','Do',

'In','Out',

'Void','Main','Print',

'If','Else','false','True',

'int','float','bool','string',

'NUMBER', 'new_line'   
)

t_oSUMA = r'\+'
t_oRESTA = r'\-'
t_oMULT = r'\*'
t_oDIV = r'/'
t_oRESIDUO = r'\('

"""
t_oOR = r'\'
t_oAND = r'\'
t_oMAYOR = r'\'
t_oMENOR = r'\'
t_oIGUAL = r'\'
"""

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