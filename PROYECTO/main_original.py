import sys
from Lexer import lexer
from Parser import parser
import os

def main():

    input_file = "codigo.txt"

    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        if not os.path.exists('salida'):
            os.makedirs('salida')
        # Clear error files
        open("salida/errores_lexicos.txt", "w").close()
        open("salida/errores_sintacticos.txt", "w").close()

        print("=== Análisis Léxico ===")
        lexer.input(source_code)

        # Print all tokens
        print("\nTokens encontrados:")
        for token in lexer:
            print(f"Línea {token.lineno}: {token.type} -> {token.value}")

        print("\n=== Análisis Sintáctico ===")
        ast = parser.parse(source_code, lexer=lexer)  # Añade debug=True
        print("\nÁrbol de Sintaxis Abstracta (AST):")
        print(ast)

        # Check for lexical errors
        with open("salida/errores_lexicos.txt", "r") as f:
            lex_errors = f.read()
            if lex_errors:
                print("\nErrores léxicos encontrados:")
                print(lex_errors)
            else:
                print("\nNo se encontraron errores léxicos")

        # Check for syntax errors
        with open("salida/errores_sintacticos.txt", "r") as f:
            syntax_errors = f.read()
            if syntax_errors:
                print("\nErrores sintácticos encontrados:")
                print(syntax_errors)
            else:
                print("\nNo se encontraron errores sintácticos")

    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {input_file}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == "__main__":
    main()