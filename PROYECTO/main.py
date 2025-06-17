import sys
import os
from .Lexer import lexer # Needed by ASTBuilder implicitly
from .Parser import parser # Needed by ASTBuilder implicitly
from .ASTBuilder import ASTBuilder # test_scope_checker uses this
from .ScopeChecker import ScopeChecker # test_scope_checker uses this

# Global constants for file paths (test_scope_checker might use these for error reporting)
ARCHIVO_ENTRADA = "codigo.txt" # Or a dummy if not directly used by test_scope_checker's AST build from string
ARCHIVO_TOKENS = "salida/tokens.txt"
ARCHIVO_ERRORES_LEXICOS = "salida/errores_lexicos.txt"
ARCHIVO_ERRORES_SINTACTICOS = "salida/errores_sintacticos.txt"
AST_OUTPUT_FILE = "salida/ast.txt"
PARSE_TRACE_OUTPUT_FILE = "salida/parse_trace.txt"

# Setup: Create 'salida' directory if it doesn't exist (test_scope_checker might create error files there)
if not os.path.exists('salida'):
    os.makedirs('salida')

# Function to test scope checking (from main4.py / previous consolidated main.py)
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
        print(y); // Error: y not defined here
    }
    """

    # Ejemplo 3: Programa con redeclaración
    code3 = """
    void main() {
        int x = 5;
        int x = 10; // Error: x redeclared
    }
    """

    # Ejemplo 4: Programa con función no definida
    code4 = """
    void main() {
        calcular(); // Error: calcular not defined
    }
    """

    examples = [
        ("1. Programa válido", code1, False),
        ("2. Error de ámbito", code2, True),
        ("3. Redeclaración", code3, True),
        ("4. Función no definida", code4, True)
    ]

    print("=== PRUEBAS DE VERIFICACIÓN DE ÁMBITO ===")
    all_tests_passed = True
    for name, code, expect_error in examples:
        print(f"\n--- Test: {name} ---")
        print("Código:")
        print(code.strip())
        
        # Ensure error log files are clean for this specific test run portion
        if os.path.exists(ARCHIVO_ERRORES_LEXICOS):
            open(ARCHIVO_ERRORES_LEXICOS, "w").close()
        if os.path.exists(ARCHIVO_ERRORES_SINTACTICOS):
            open(ARCHIVO_ERRORES_SINTACTICOS, "w").close()

        builder = ASTBuilder()
        ast = builder.build_ast(code)

        if ast is None:
            print("\n❌ No se pudo construir el AST.")
            # Optionally, read and print lexical/syntax errors from files if needed for detailed debugging
            # For this test, the primary check is ScopeChecker's behavior.
            all_tests_passed = False
            continue

        checker = ScopeChecker()
        try:
            checker.check_program(ast) # This prints its own reports (symbol table, history)
            if expect_error:
                print("\n❌ Prueba falló: Se esperaba un error de ámbito pero no se encontró.")
                all_tests_passed = False
            else:
                print("\n✅ Prueba exitosa: Programa válido y sin errores de ámbito.")
        except ValueError as e:
            if expect_error:
                print(f"\n✅ Prueba exitosa: Error de ámbito detectado correctamente.")
                print(f"   Mensaje de error: {str(e)}")
            else:
                print(f"\n❌ Prueba falló: Error de ámbito inesperado.")
                print(f"   Mensaje de error: {str(e)}")
                all_tests_passed = False
        except Exception as e_other: # Catch any other unexpected exceptions from check_program
            print(f"\n❌ Prueba falló: Excepción inesperada durante la verificación de ámbito: {type(e_other).__name__}: {str(e_other)}")
            import traceback
            traceback.print_exc()
            all_tests_passed = False

    print("\n--- Resumen de Pruebas de Ámbito ---")
    if all_tests_passed:
        print("✅ Todas las pruebas de verificación de ámbito pasaron.")
    else:
        print("❌ Algunas pruebas de verificación de ámbito fallaron.")

if __name__ == "__main__":
    # Ensure parsetab.py and parser.out are regenerated for the current Parser.py state
    # by removing them before Parser module (and thus yacc) is first imported.
    # This is a bit tricky if ASTBuilder or ScopeChecker import Parser at their top level.
    # A cleaner way is to do this *before* the python -c script runs.
    # For now, assuming yacc.yacc() in Parser.py handles staleness or we rely on external cleanup.

    # Clean up parsetab and parser.out before running tests
    # This is important if Parser.py has changed, to ensure tables are regenerated.
    if os.path.exists("PROYECTO/parsetab.py"): # Assuming script is run from /app
        os.remove("PROYECTO/parsetab.py")
    if os.path.exists("PROYECTO/parser.out"):
        os.remove("PROYECTO/parser.out")

    test_scope_checker()
