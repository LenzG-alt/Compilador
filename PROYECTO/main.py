import sys
import os
from Lexer import lexer, test_lexer # Keep test_lexer for potential direct lexer testing
from Parser import parser
from ASTBuilder import ASTBuilder, build_and_display_ast # build_and_display_ast for quick AST view
from ScopeChecker import ScopeChecker
from TypeChecker import TypeChecker

# --- Configuration ---
OUTPUT_DIR = "salida"
# Error files managed by respective modules, but main can coordinate clearing/setup if needed.
LEXER_ERROR_FILE = os.path.join(OUTPUT_DIR, "errores_lexicos.txt")
PARSER_ERROR_FILE = os.path.join(OUTPUT_DIR, "errores_sintacticos.txt")
SCOPE_ERROR_FILE = os.path.join(OUTPUT_DIR, "errores_ambito.txt")
TYPE_ERROR_FILE = os.path.join(OUTPUT_DIR, "errores_tipo.txt")
AST_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ast_generated.txt") # Main AST output
TOKEN_TRACE_FILE = os.path.join(OUTPUT_DIR, "token_trace_generated.txt") # Main token trace output

def clear_previous_logs():
    """Clears log files from previous runs."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log_files = [
        LEXER_ERROR_FILE, PARSER_ERROR_FILE,
        SCOPE_ERROR_FILE, TYPE_ERROR_FILE,
        AST_OUTPUT_FILE, TOKEN_TRACE_FILE
    ]
    for log_file in log_files:
        try:
            open(log_file, 'w').close() # Create or truncate the file
        except IOError as e:
            print(f"Warning: Could not clear log file {log_file}: {e}")

def compile_file(source_code_path):
    """
    Compiles the given source code file through all stages.
    """
    print(f"--- Compiling: {source_code_path} ---")

    try:
        with open(source_code_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: Source code file not found: {source_code_path}")
        return False
    except IOError as e:
        print(f"Error reading source code file {source_code_path}: {e}")
        return False

    clear_previous_logs()

    # 1. AST Building (Lexer + Parser are used by ASTBuilder)
    print("\n[Phase 1: AST Construction]")
    ast_builder = ASTBuilder(output_dir=OUTPUT_DIR)
    ast = None
    lexical_errors_exist = False
    syntax_errors_exist = False

    try:
        ast = ast_builder.build_ast(code)
        # Check if lexer/parser error files were populated by them directly
        if os.path.exists(LEXER_ERROR_FILE) and os.path.getsize(LEXER_ERROR_FILE) > 0:
            lexical_errors_exist = True
            print("Lexical errors detected. See 'salida/errores_lexicos.txt'.")

        if os.path.exists(PARSER_ERROR_FILE) and os.path.getsize(PARSER_ERROR_FILE) > 0:
            syntax_errors_exist = True
            print("Syntax errors detected. See 'salida/errores_sintacticos.txt'.")

        if ast and not lexical_errors_exist and not syntax_errors_exist:
            print("AST constructed successfully.")
            ast_builder.save_ast_to_file(filename=os.path.basename(AST_OUTPUT_FILE))
            # ast_builder.print_ast() # Optional: print AST to console
            # ast_builder.save_token_trace_to_file(filename=os.path.basename(TOKEN_TRACE_FILE)) # Optional
        elif not ast:
            print("AST construction failed. Further checks may be unreliable.")
            # No need to return False yet, Scope/Type checkers might still run on partial AST if desired
            # but typically compilation would halt or be marked as failed.
            # For this example, we'll let it proceed to show error reporting from all phases.
    except Exception as e:
        print(f"Error during AST construction phase: {e}")
        # AST construction failed critically, probably should not proceed.
        return False

    if lexical_errors_exist or syntax_errors_exist:
        print("Compilation halted due to lexical or syntax errors.")
        return False # Halt if fundamental parsing errors occurred

    if not ast:
        print("AST is None after build phase, cannot proceed with semantic checks.")
        return False


    # 2. Scope Checking
    print("\n[Phase 2: Scope Checking]")
    scope_checker = ScopeChecker(output_dir=OUTPUT_DIR, error_filename=os.path.basename(SCOPE_ERROR_FILE))
    scope_errors_found = False
    try:
        scope_checker.check_program(ast) # ScopeChecker logs errors internally
        if scope_checker.errors:
            scope_errors_found = True
            print(f"{len(scope_checker.errors)} scope error(s) found.")
            scope_checker.save_errors_to_file() # Saves errors to its configured file
        else:
            print("Scope checking completed successfully.")
    except Exception as e:
        print(f"Error during Scope Checking phase: {e}")
        scope_errors_found = True # Treat exceptions as errors

    # print(scope_checker.symbol_table.get_symbol_table_report()) # Optional: for debugging

    if scope_errors_found:
        print("Compilation has scope errors.")
        # Depending on language design, type checking might still proceed or halt.
        # For this example, let type checking run to find more potential errors.
        # However, a real compiler might halt or have a flag.


    # 3. Type Checking
    print("\n[Phase 3: Type Checking]")
    type_checker = TypeChecker(symbol_table=scope_checker.symbol_table,
                               output_dir=OUTPUT_DIR,
                               error_filename=os.path.basename(TYPE_ERROR_FILE))
    type_errors_found = False
    try:
        type_checker.check_program(ast) # TypeChecker logs errors internally
        if type_checker.errors:
            type_errors_found = True
            print(f"{len(type_checker.errors)} type error(s) found.")
            type_checker.save_errors_to_file() # Saves errors
        else:
            print("Type checking completed successfully.")
    except Exception as e:
        print(f"Error during Type Checking phase: {e}")
        type_errors_found = True


    # --- Compilation Summary ---
    print("\n--- Compilation Summary ---")
    if not lexical_errors_exist and not syntax_errors_exist and not scope_errors_found and not type_errors_found:
        print(f"Successfully compiled '{source_code_path}'.")
        print(f"AST saved to '{AST_OUTPUT_FILE}'.")
        # Add other output info if any (e.g., token trace)
        return True
    else:
        print(f"Compilation of '{source_code_path}' failed with errors:")
        if lexical_errors_exist: print(f"  - Lexical errors reported in '{LEXER_ERROR_FILE}'.")
        if syntax_errors_exist: print(f"  - Syntax errors reported in '{PARSER_ERROR_FILE}'.")
        if scope_errors_found: print(f"  - Scope errors reported in '{SCOPE_ERROR_FILE}'.")
        if type_errors_found: print(f"  - Type errors reported in '{TYPE_ERROR_FILE}'.")
        return False

if __name__ == "__main__":
    # Remove PLY's generated parsetab.py and parser.out for cleaner rebuilds,
    # especially during development.
    # These files are typically in the same directory as Parser.py.
    project_dir = os.path.dirname(__file__) # PROYECTO directory
    parsetab_file = os.path.join(project_dir, "parsetab.py")
    # parser_out_file = os.path.join(project_dir, "parser.out") # If yacc(debug=True) was used

    if os.path.exists(parsetab_file):
        try: os.remove(parsetab_file)
        except OSError as e: print(f"Warning: Could not remove {parsetab_file}: {e}")
    # if os.path.exists(parser_out_file):
    #     try: os.remove(parser_out_file)
    #     except OSError as e: print(f"Warning: Could not remove {parser_out_file}: {e}")


    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Create a default 'codigo.txt' if none provided, for demonstration.
        input_file = "codigo.txt"
        print(f"No input file specified. Using default: '{input_file}'")
        default_code_content = """
// Default example code for main.py
void main() {
    int x = 10;
    string message = "Hello, Compiler!";

    if (x > 5) {
        print(message);
    }

    int y = 0;
    // Example of a for loop
    for (int i = 0; i < 3; i = i + 1) {
        y = y + i;
        print(y);
    }

    // Undeclared variable to show scope error
    // print(undeclared_var);

    // Type error example
    // x = "this should be an int";
}
"""
        try:
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(default_code_content)
            print(f"Created default '{input_file}'. Please edit or provide a file path as an argument.")
        except IOError as e:
            print(f"Could not create default input file '{input_file}': {e}")
            sys.exit(1)

    compile_file(input_file)
