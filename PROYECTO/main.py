import sys
import os
from .Lexer import lexer
from .Parser import parser
from .ASTBuilder import ASTBuilder
from .ScopeChecker import ScopeChecker
from .TypeChecker import TypeChecker # Import the new TypeChecker

# Global constants for file paths
ARCHIVO_ENTRADA = "codigo.txt"
ARCHIVO_TOKENS = "salida/tokens.txt"
ARCHIVO_ERRORES_LEXICOS = "salida/errores_lexicos.txt"
ARCHIVO_ERRORES_SINTACTICOS = "salida/errores_sintacticos.txt"
AST_OUTPUT_FILE = "salida/ast.txt"
PARSE_TRACE_OUTPUT_FILE = "salida/parse_trace.txt"
SCOPE_ERRORS_FILE = "salida/errores_ambito.txt"
TYPE_ERRORS_FILE = "salida/errores_tipo.txt" # For TypeChecker errors

# Setup: Create 'salida' directory if it doesn't exist
# This is better done once at the start of main or test_compiler_stages
# if not os.path.exists('salida'):
#     os.makedirs('salida')

def test_compiler_stages():
    # Example codes
    code_valid_scope_type = """
    int suma(int a, int b) {
        int resultado = a + b;
        return resultado;
    }
    void main() {
        int x = 5;
        int y = 10;
        int z = suma(x, y);
        print(z);
        string s = "hello";
        s = s + " world";
        print(s);
        bool flag = true;
        if (flag) {
            print(1);
        } else {
            print(0);
        }
        float f1 = 0.5;
        int i1 = 10;
        f1 = i1 + f1; // float = int + float -> float
        print(f1);
        i1 = 2 + 3 * 4; // int = int + int * int -> int
        print(i1);
    }"""

    code_scope_error_y_undefined = """
    void main() {
        int x = 5;
        {
            int y = x + 2;
            print(y);
        }
        print(y); // Scope Error: y not defined here
    }"""

    code_scope_error_x_redeclared = """
    void main() {
        int x = 5;
        int x = 10; // Scope Error: x redeclared
    }"""

    code_scope_error_func_undefined = """
    void main() {
        calcular(); // Scope Error: calcular not defined
    }"""

    code_type_error_string_plus_int = """
    void main() {
        string s = "hello";
        int count = 5;
        print(s + count); // Type Error: string + int
    }"""

    code_type_error_if_condition = """
    void main() {
        int x = 10;
        if (x) { // Type Error: condition not bool
            print(1);
        }
    }"""

    code_type_error_assignment = """
    void main() {
        int num;
        num = "this is not a number"; // Type Error: string to int
    }"""

    code_type_error_return = """
    int get_val() {
        string msg = "message";
        return msg; // Type Error: returning string from int function
    }
    void main() {
        int v = get_val();
        print(v);
    }"""

    code_type_error_func_arg = """
    int add(int a, int b) {
        return a + b;
    }
    void main() {
        int res = add(5, "world"); // Type Error: "world" is not int for b
        print(res);
    }"""

    # Test cases: (name, code, expect_scope_error, expect_type_error_or_related_scope_issue)
    examples = [
        ("1. Programa válido (Scope & Type)", code_valid_scope_type, False, False),
        ("2. Error de ámbito (y no definida)", code_scope_error_y_undefined, True, True),
        ("3. Error de ámbito (x redeclarada)", code_scope_error_x_redeclared, True, False), # Type check might not run or pass if scope fails critically
        ("4. Error de ámbito (función no def)", code_scope_error_func_undefined, True, True),
        ("5. Error de tipo (string + int)", code_type_error_string_plus_int, False, True),
        ("6. Error de tipo (condición if)", code_type_error_if_condition, False, True),
        ("7. Error de tipo (asignación)", code_type_error_assignment, False, True),
        ("8. Error de tipo (return)", code_type_error_return, False, True),
        ("9. Error de tipo (argumento func)", code_type_error_func_arg, False, True),
    ]

    print("=== PRUEBAS DEL PIPELINE DEL COMPILADOR ===")
    overall_success = True

    project_dir = os.path.dirname(__file__) # PROYECTO directory
    salida_dir = os.path.join(project_dir, 'salida')
    if not os.path.exists(salida_dir):
        os.makedirs(salida_dir)

    # Global error file paths using project_dir
    g_err_lex_file = os.path.join(salida_dir, "errores_lexicos.txt")
    g_err_sin_file = os.path.join(salida_dir, "errores_sintacticos.txt")
    g_scope_err_file = os.path.join(salida_dir, "errores_ambito.txt")
    g_type_err_file = os.path.join(salida_dir, "errores_tipo.txt")


    for name, code, expect_scope_error, expect_type_error in examples:
        print(f"\n--- Test Case: {name} ---")
        print("Código:")
        print(code.strip())
        
        # Clear previous error logs for this specific test case by overwriting them
        # These files will store cumulative errors from all tests if not cleared per test.
        # For pipeline testing, it's often better to have separate files per test or clear them.
        # Here, we'll append, so they become a log for the entire test run.
        # Individual test success is determined by expect_X_error flags.
        # However, for clarity in a single test run output, let's clear them before each test case run.

        for f_path in [g_err_lex_file, g_err_sin_file, g_scope_err_file, g_type_err_file]:
            try:
                open(f_path, "w").close() # Clear file content for this test run
            except IOError:
                print(f"Warning: Could not clear file {f_path}")


        # 1. AST Building (Lexer + Parser + ASTBuilder)
        # Assuming Lexer and Parser correctly write to their error files if issues occur.
        builder = ASTBuilder()
        ast = builder.build_ast(code)
        # builder.ast_to_file(os.path.join(salida_dir, f"ast_{name.replace(' ', '_')}.txt"))


        if ast is None:
            print("❌ No se pudo construir el AST. Falló la prueba.")
            # Check if lexical or syntax errors were expected. This example suite doesn't explicitly test for them.
            overall_success = False
            continue
        print("✅ AST construido exitosamente.")

        # 2. Scope Checking
        scope_checker = ScopeChecker(error_file=g_scope_err_file)
        actual_scope_error_occurred = False
        scope_error_messages = [] # ScopeChecker might log multiple errors

        try:
            scope_checker.check_program(ast)
            scope_error_messages = scope_checker.get_errors() # Assuming ScopeChecker has get_errors()
            if not scope_error_messages:
                print("✅ Verificación de ámbito completada sin errores reportados por el checker.")
            else:
                actual_scope_error_occurred = True
                print(f"⚠️ Errores de ámbito detectados por ScopeChecker:")
                for err_msg in scope_error_messages: print(f"   - {err_msg}")

        except Exception as e_scope:
            actual_scope_error_occurred = True
            scope_error_messages.append(f"Excepción inesperada en ScopeChecker: {type(e_scope).__name__}: {str(e_scope)}")
            print(f"❌ {scope_error_messages[-1]}")
            overall_success = False

        if expect_scope_error:
            if actual_scope_error_occurred:
                print(f"✅ Prueba de ámbito pasada: Error(es) de ámbito esperado(s) y ocurrido(s).")
            else:
                print(f"❌ Falló la prueba de ámbito: Se esperaba un error de ámbito pero no se reportó ninguno.")
                overall_success = False
        else:
            if actual_scope_error_occurred:
                print(f"❌ Falló la prueba de ámbito: Error(es) de ámbito inesperado(s):")
                for err in scope_error_messages: print(f"   - {err}")
                overall_success = False
            else:
                print(f"✅ Prueba de ámbito pasada: No se esperaban errores de ámbito y ninguno ocurrió.")

        # 3. Type Checking
        type_checker = TypeChecker(scope_checker.symbol_table)
        actual_type_errors_reported = []
        type_check_exception_message = ""

        # Only run type checker if no scope errors were expected OR if they were expected but didn't prevent symbol table use
        # This logic can be refined: if critical scope errors occurred, type checking might be meaningless.
        # For now, run if scope check passed OR if scope errors were expected (implying AST might still be checkable)
        # A more robust check: if actual_scope_error_occurred AND not expect_scope_error, then maybe skip.

        # Let's always run TypeChecker if AST is available and ScopeChecker ran,
        # as TypeChecker might find errors due to incomplete symbol table from scope errors.
        # The `expect_type_error` flag will determine if these are "good" errors.

        try:
            type_checker.check_program(ast)
            actual_type_errors_reported = type_checker.get_errors()
            if not actual_type_errors_reported:
                print("✅ Verificación de tipo completada sin errores reportados por el checker.")
            else:
                print(f"⚠️ Errores de tipo detectados por TypeChecker:")
                with open(g_type_err_file, "a") as f: # Append to global type error log
                    f.write(f"--- Test Case: {name} ---\n")
                    for error_msg in actual_type_errors_reported:
                        print(f"   - {error_msg}")
                        f.write(f"- {error_msg}\n")
                    f.write("\n")

        except Exception as e_type_check:
            type_check_exception_message = f"Excepción inesperada en TypeChecker: {type(e_type_check).__name__}: {str(e_type_check)}"
            print(f"❌ {type_check_exception_message}")
            actual_type_errors_reported.append(type_check_exception_message) # Add exception to errors
            overall_success = False

        actual_type_error_occurred_flag = bool(actual_type_errors_reported) # Check if any errors were logged

        if expect_type_error:
            if actual_type_error_occurred_flag:
                print(f"✅ Prueba de tipo pasada: Error(es) de tipo esperado(s) y ocurrido(s).")
            else:
                print(f"❌ Falló la prueba de tipo: Se esperaba un error de tipo pero no se reportó ninguno.")
                overall_success = False
        else:
            if actual_type_error_occurred_flag:
                print(f"❌ Falló la prueba de tipo: Error(es) de tipo inesperado(s) reportado(s):")
                for err in actual_type_errors_reported: print(f"   - {err}")
                overall_success = False
            else:
                print(f"✅ Prueba de tipo pasada: No se esperaban errores de tipo y ninguno ocurrió.")

        print(f"--- Fin Test Case: {name} ---")

    print("\n--- Resumen de Pruebas del Compilador ---")
    if overall_success:
        print("✅ Todas las pruebas del compilador evaluadas pasaron sus expectativas.")
    else:
        print("❌ Algunas pruebas del compilador fallaron en sus expectativas.")


if __name__ == "__main__":
    project_root = os.path.dirname(__file__) # PROYECTO

    parsetab_file = os.path.join(project_root, "parsetab.py")
    parser_out_file = os.path.join(project_root, "parser.out")

    if os.path.exists(parsetab_file):
        try: os.remove(parsetab_file)
        except OSError as e: print(f"Could not remove {parsetab_file}: {e}")
    if os.path.exists(parser_out_file):
        try: os.remove(parser_out_file)
        except OSError as e: print(f"Could not remove {parser_out_file}: {e}")

    # Clear global log files at the start of the entire test suite run
    # These files will now accumulate errors from all test cases in this run.
    # If you want per-test-case logs, create unique filenames inside the loop.
    salida_dir_main = os.path.join(project_root, 'salida')
    if not os.path.exists(salida_dir_main):
        os.makedirs(salida_dir_main)

    files_to_clear_globally = [
        "salida/errores_lexicos.txt", "salida/errores_sintacticos.txt",
        "salida/errores_ambito.txt", "salida/errores_tipo.txt",
        "salida/ast.txt", "salida/parse_trace.txt" # General trace files
    ]
    for f_name_rel in files_to_clear_globally:
        full_path = os.path.join(project_root, f_name_rel)
        try:
            open(full_path, "w").close() # Create or clear the file
        except IOError:
            print(f"Warning: Could not clear/create file {full_path}")

    test_compiler_stages()

```
