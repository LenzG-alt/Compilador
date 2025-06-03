import Lexer

data = "int x = 5;"

Lexer.lexer.input(data)
for tok in Lexer.lexer:
    print(tok)
