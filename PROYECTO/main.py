import sys
import os
from Lexer import lexer
from Parser import parser
from ASTBuilder import build_and_visualize_ast, ASTBuilder
from ScopeChecker import ScopeChecker

# Global constants for file paths
ARCHIVO_ENTRADA = "codigo.txt"
ARCHIVO_TOKENS = "salida/tokens.txt"
ARCHIVO_ERRORES_LEXICOS = "salida/errores_lexicos.txt"
ARCHIVO_ERRORES_SINTACTICOS = "salida/errores_sintacticos.txt"
AST_OUTPUT_FILE = "salida/ast.txt"
PARSE_TRACE_OUTPUT_FILE = "salida/parse_trace.txt"

# Setup: Create 'salida' directory if it doesn't exist
if not os.path.exists('salida'):
    os.makedirs('salida')

# Function to perform lexical and syntactic analysis (from main_original.py)
def run_lexical_syntactic_analysis():
    try:
        # Read input file
        with open(ARCHIVO_ENTRADA, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # Clear error files
        open(ARCHIVO_ERRORES_LEXICOS, "w").close()
        open(ARCHIVO_ERRORES_SINTACTICOS, "w").close()

        print("=== Análisis Léxico ===")
        lexer.input(source_code)
        
        # Print all tokens
        print("\nTokens encontrados:")
        # Reset lexer for token iteration if it was already iterated or partially iterated
        # This depends on how the lexer is implemented. Assuming it needs a reset or re-input.
        lexer.input(source_code) # Re-input for iteration
        for token in lexer:
            print(f"Línea {token.lineno}: {token.type} -> {token.value}")

        print("\n=== Análisis Sintáctico ===")
        # The lexer object might be consumed after the loop above.
        # It's safer to pass the source_code again or a freshly reset lexer.
        # For many PLY-based lexers, input() resets its state.
        lexer.input(source_code) # Ensure lexer is reset before parsing
        ast = parser.parse(source_code, lexer=lexer)
        print("\nÁrbol de Sintaxis Abstracta (AST):")
        print(ast)

        # Check for lexical errors
        with open(ARCHIVO_ERRORES_LEXICOS, "r") as f:
            lex_errors = f.read()
            if lex_errors:
                print("\nErrores léxicos encontrados:")
                print(lex_errors)
            else:
                print("\nNo se encontraron errores léxicos")

        # Check for syntax errors
        with open(ARCHIVO_ERRORES_SINTACTICOS, "r") as f:
            syntax_errors = f.read()
            if syntax_errors:
                print("\nErrores sintácticos encontrados:")
                print(syntax_errors)
            else:
                print("\nNo se encontraron errores sintácticos")

    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {ARCHIVO_ENTRADA}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

# Function to perform detailed lexical analysis and save tokens (from main2.py)
def run_detailed_lexical_analysis():
    try:
        # Initialize/Clear output files
        with open(ARCHIVO_ERRORES_LEXICOS, "w", encoding="utf-8") as f:
            f.write("=== ERRORES LÉXICOS ===\n\n")

        with open(ARCHIVO_TOKENS, "w", encoding="utf-8") as f:
            f.write("=== TOKENS ENCONTRADOS ===\n\n")
            f.write(f"{'Tipo':<15} {'Valor':<20} {'Línea'}\n")
            f.write("-" * 40 + "\n")

        # Read input file
        with open(ARCHIVO_ENTRADA, "r", encoding="utf-8") as f:
            source_code = f.read()

        lexer.input(source_code)
        token_count = 0

        while True:
            tok = lexer.token()
            if not tok:
                break
            token_count += 1

            with open(ARCHIVO_TOKENS, "a", encoding="utf-8") as tokens_file:
                tokens_file.write(f"{tok.type:<15} {str(tok.value):<20} {tok.lineno}\n")

        print(f"\nAnálisis léxico detallado completado. Tokens encontrados: {token_count}")

        # Verify if lexical errors were written by the lexer
        # (The lexer itself should handle writing to ARCHIVO_ERRORES_LEXICOS)
        with open(ARCHIVO_ERRORES_LEXICOS, "r", encoding="utf-8") as error_file:
            # Readlines and check if more than the header exists.
            # The header is "=== ERRORES LÉXICOS ===\n" and a newline, so > 2 lines means errors.
            # However, some lexers might just append errors without checking the header.
            # A more robust check might be file size or content after the header.
            # For simplicity, checking if content beyond the header + an empty line exists.
            error_content = error_file.read()
            if len(error_content.strip()) > len("=== ERRORES LÉXICOS ==="):
                 print(f"Se encontraron errores léxicos. Ver '{ARCHIVO_ERRORES_LEXICOS}'")
            else:
                print("No se encontraron errores léxicos.")

        print(f"\nResultados guardados en:\n- {ARCHIVO_TOKENS}\n- {ARCHIVO_ERRORES_LEXICOS}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de entrada '{ARCHIVO_ENTRADA}'")
    except Exception as e:
        print(f"Error inesperado durante el análisis léxico detallado: {str(e)}")

# Function to generate and visualize AST (from main3.py)
def generate_and_visualize_ast(input_code_str=None, input_filepath=None):
    input_code = None
    source_description = ""

    if input_code_str:
        input_code = input_code_str
        source_description = "string input"
    elif input_filepath:
        try:
            with open(input_filepath, 'r', encoding='utf-8') as f:
                input_code = f.read()
            source_description = input_filepath
        except FileNotFoundError:
            print(f"Error: Input file '{input_filepath}' not found.")
            # Fall through to default or ARCHIVO_ENTRADA
        except Exception as e:
            print(f"Error reading file '{input_filepath}': {str(e)}")
            # Fall through

    if not input_code: # If no string or specific file, try global ARCHIVO_ENTRADA
        try:
            with open(ARCHIVO_ENTRADA, 'r', encoding='utf-8') as f:
                input_code = f.read()
            source_description = ARCHIVO_ENTRADA
        except FileNotFoundError:
            print(f"Error: Default input file '{ARCHIVO_ENTRADA}' not found. Using example code.")
        except Exception as e:
            print(f"Error reading default file '{ARCHIVO_ENTRADA}': {str(e)}. Using example code.")

    if not input_code: # If all else fails, use the example code
        source_description = "default example code"
        input_code = """
        main() {
            int x = 5;
            if (x > 0) {
                print("Positivo");
            } else {
                print("Negativo");
            }
            return 0;
        }
        """
        print(f"Using {source_description} for AST generation.")

    print(f"\nAnalizando código desde {source_description} para AST...\n")

    try:
        # Assuming build_and_visualize_ast writes to AST_OUTPUT_FILE and PARSE_TRACE_OUTPUT_FILE
        # as suggested by main3.py's print statements.
        # The actual implementation of build_and_visualize_ast (in ASTBuilder.py)
        # should use these global constants or be modified to do so.
        ast, trace = build_and_visualize_ast(input_code) # build_and_visualize_ast should handle its file outputs

        print("\nAnálisis AST completado. Resultados (esperados) en:")
        print(f"- {AST_OUTPUT_FILE}")
        print(f"- {PARSE_TRACE_OUTPUT_FILE}")
        # Optionally, we could return ast and trace if they are needed by the caller
    except Exception as e:
        print(f"\nError durante la generación del AST: {str(e)}")

# Function to test scope checking (from main4.py)
def test_scope_checker():
    # Ejemplo 1: Programa válido
    code1 = """
    int suma(int a, int b) {
        int resultado = a + b;
        return resultado;
    }

    void main() {
        int x = 5;
        int y = 10;
        int z = suma(x, y);
        print(z);
    }
    """

    # Ejemplo 2: Programa con errores de ámbito
    code2 = """
    void main() {
        int x = 5;
        {
            int y = x + 2;
            print(y);
        }
        print(y);
    }
    """

    # Ejemplo 3: Programa con redeclaración
    code3 = """
    void main() {
        int x = 5;
        int x = 10;
    }
    """

    # Ejemplo 4: Programa con función no definida
    code4 = """
    void main() {
        calcular();
    }
    """

    examples = [
        ("1. Programa válido", code1, False),
        ("2. Error de ámbito", code2, True),
        ("3. Redeclaración", code3, True),
        ("4. Función no definida", code4, True)
    ]

    print("=== PRUEBAS DE VERIFICACIÓN DE ÁMBITO ===")
    for name, code, expect_error in examples:
        print(f"\n{name}")
        print("Código:")
        print(code.strip())

        # Construir AST
        # Ensure ASTBuilder is available (imported in PROYECTO/main.py)
        builder = ASTBuilder()
        # build_ast likely uses the globally imported parser and lexer
        ast = builder.build_ast(code)

        if ast is None:
            print("\n❌ No se pudo construir el AST debido a errores sintácticos")
            # Potentially print lexical/syntax errors here if available from builder/parser
            # This might require build_ast to return more info or for error files to be checked
            print(f"   Check '{ARCHIVO_ERRORES_LEXICOS}' and '{ARCHIVO_ERRORES_SINTACTICOS}'.")
            continue

        # Verificar ámbito
        # Ensure ScopeChecker is available (imported in PROYECTO/main.py)
        checker = ScopeChecker()
        try:
            checker.check_program(ast)
            if expect_error:
                print("\n❌ Prueba falló: Se esperaba un error pero no se encontró")
            else:
                print("\n✅ Prueba exitosa: Programa válido")
        except ValueError as e:
            if expect_error:
                print(f"\n✅ Prueba exitosa: Error detectado correctamente")
            else:
                print(f"\n❌ Prueba falló: Error inesperado")
            print(f"  Mensaje de error: {str(e)}")

# def main():
#     print("Hello World from the new main.py")
#     # Placeholder for future merged functionality

if __name__ == "__main__":
    # Default action: Perform general lexical and syntactic analysis on ARCHIVO_ENTRADA
    # This function prints tokens, AST, and checks for errors in error files.
    run_lexical_syntactic_analysis()

    # --- Uncomment one of the following sections to run other functionalities ---

    # Option 1: Perform detailed lexical analysis
    # This function saves all tokens to ARCHIVO_TOKENS and lexical errors to ARCHIVO_ERRORES_LEXICOS.
    # run_detailed_lexical_analysis()

    # Option 2: Generate and visualize Abstract Syntax Tree (AST)
    # This function can take input from various sources and saves AST/trace to files.
    # generate_and_visualize_ast() # Uses ARCHIVO_ENTRADA by default, or example code if not found
    # generate_and_visualize_ast(input_filepath="PROYECTO/codigo.txt") # Specify an input file
    # generate_and_visualize_ast(input_code_str="void main() { int x = 1; print(x); }") # Provide code as a string

    # Option 3: Run tests for the Scope Checker
    # This function uses predefined code examples to test scope validation logic.
    # test_scope_checker()
