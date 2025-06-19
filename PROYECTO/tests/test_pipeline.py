import sys
import os
import unittest

# Adjust path to import modules from PROYECTO directory
# This assumes test_pipeline.py is in PROYECTO/tests/
# and modules like Lexer, Parser are in PROYECTO/
current_dir = os.path.dirname(__file__)
project_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_dir)

from Lexer import lexer  # For re-initializing if needed by parser
from Parser import parser
from ASTBuilder import ASTBuilder
from ScopeChecker import ScopeChecker
from TypeChecker import TypeChecker

# --- Configuration for Test Output ---
TEST_OUTPUT_DIR = os.path.join(project_dir, "salida_tests") # Separate output for tests

# Define paths for error logs specific to tests
LEXER_ERR_FILE_T = os.path.join(TEST_OUTPUT_DIR, "test_errores_lexicos.txt")
PARSER_ERR_FILE_T = os.path.join(TEST_OUTPUT_DIR, "test_errores_sintacticos.txt")
SCOPE_ERR_FILE_T = os.path.join(TEST_OUTPUT_DIR, "test_errores_ambito.txt")
TYPE_ERR_FILE_T = os.path.join(TEST_OUTPUT_DIR, "test_errores_tipo.txt")
AST_FILE_T_PREFIX = os.path.join(TEST_OUTPUT_DIR, "test_ast_") # Prefix for AST files per test


class TestCompilerPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up for all tests; create output directory."""
        os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

        # Optional: Clear parsetab.py before test suite to ensure fresh parser state
        # This might be better handled globally if running tests via a script.
        parsetab_file = os.path.join(project_dir, "parsetab.py")
        if os.path.exists(parsetab_file):
            try: os.remove(parsetab_file)
            except OSError: pass # Ignore if it fails (e.g., permissions)


    def _clear_test_log_files(self):
        """Clears specific log files before each test case that uses them."""
        files_to_clear = [
            LEXER_ERR_FILE_T, PARSER_ERR_FILE_T,
            SCOPE_ERR_FILE_T, TYPE_ERR_FILE_T
        ]
        for f_path in files_to_clear:
            try:
                open(f_path, 'w').close()
            except IOError:
                print(f"Warning: Could not clear test log file {f_path}")

    def _run_compiler_pipeline(self, code_str, test_name):
        """
        Helper to run the code through the compiler pipeline for testing.
        Returns a dictionary with AST, and boolean flags for errors.
        """
        self._clear_test_log_files() # Clear logs for this specific run

        results = {
            'ast': None,
            'lexical_errors': False,
            'syntax_errors': False,
            'scope_errors': False,
            'type_errors': False,
            'scope_error_messages': [],
            'type_error_messages': []
        }

        # 1. AST Building
        ast_builder = ASTBuilder(output_dir=TEST_OUTPUT_DIR) # ASTBuilder uses its own output_dir
        try:
            # Reset lexer for each parse if it maintains state across parses
            lexer.lineno = 1
            # parser.parse might also need lexer instance directly if not globally managed
            results['ast'] = ast_builder.build_ast(code_str)

            # Check for error files directly. Lexer and Parser should write to their own logs.
            # This needs to be aligned with how Lexer/Parser t_error rules are configured.
            # For this test setup, we assume they might write to specific test log files
            # or the ASTBuilder/main.py would redirect them.
            # For simplicity, let's assume Lexer/Parser are configured to output to general log files
            # and we check those, or rely on exceptions for critical errors.
            # The new Lexer/Parser write to "salida/errores_lexicos.txt" etc.
            # ASTBuilder doesn't create those files, Lexer/Parser do.
            # So, we need to point them to the TEST_OUTPUT_DIR for tests.
            # This is tricky. For now, let's assume if ast_builder.build_ast fails or returns None,
            # it's due to lex/parse errors.
            # A more robust way would be to pass error file paths to Lexer/Parser instances
            # used by ASTBuilder, or have ASTBuilder collect these errors.

            # Re-evaluating: The Lexer and Parser are now writing errors to fixed paths
            # "salida/errores_lexicos.txt" and "salida/errores_sintacticos.txt".
            # For testing, we should ideally redirect these.
            # Since that's not easily done without modifying Lexer/Parser.py structure
            # for testability, we'll check the *default* log locations,
            # but this is not ideal for parallel tests or clean test environments.
            # A better approach would be for Lexer/Parser to take error file paths in __init__ or a setup method.
            # For now, we will use the default paths as defined in Lexer/Parser.py
            default_lexer_err_file = os.path.join(project_dir, "salida", "errores_lexicos.txt")
            default_parser_err_file = os.path.join(project_dir, "salida", "errores_sintacticos.txt")

            if os.path.exists(default_lexer_err_file) and os.path.getsize(default_lexer_err_file) > 0:
                results['lexical_errors'] = True
            if os.path.exists(default_parser_err_file) and os.path.getsize(default_parser_err_file) > 0:
                results['syntax_errors'] = True

            if results['ast']:
                ast_builder.save_ast_to_file(filename=f"{os.path.basename(AST_FILE_T_PREFIX)}{test_name}.txt")

        except Exception:
            results['syntax_errors'] = True
            return results

        if not results['ast'] or results['lexical_errors'] or results['syntax_errors']:
            return results

        # 2. Scope Checking
        scope_checker = ScopeChecker(output_dir=TEST_OUTPUT_DIR, error_filename=os.path.basename(SCOPE_ERR_FILE_T))
        try:
            scope_checker.check_program(results['ast'])
            if scope_checker.errors:
                results['scope_errors'] = True
                results['scope_error_messages'] = scope_checker.errors
                scope_checker.save_errors_to_file()
        except Exception as e_scope:
            results['scope_errors'] = True
            results['scope_error_messages'] = [f"Exception in ScopeChecker: {e_scope}"]


        # 3. Type Checking
        type_checker = TypeChecker(symbol_table=scope_checker.symbol_table,
                                   output_dir=TEST_OUTPUT_DIR,
                                   error_filename=os.path.basename(TYPE_ERR_FILE_T))
        try:
            type_checker.check_program(results['ast'])
            if type_checker.errors:
                results['type_errors'] = True
                results['type_error_messages'] = type_checker.errors
                type_checker.save_errors_to_file()
        except Exception as e_type:
            results['type_errors'] = True
            results['type_error_messages'] = [f"Exception in TypeChecker: {e_type}"]

        return results

    # --- Test Cases (adapted from original main.py's test_compiler_stages) ---

    def test_01_valid_program(self):
        code = """
        int suma(int a, int b) {
            int resultado = a + b;
            return resultado;
        }
        void main() {
            int x = 5;
            int y = 10;
            int z = suma(x, y); // Call
            print(z);
            string s = "hello";
            s = s + " world"; // string concat
            print(s);
            bool flag = true;
            if (flag) {
                print(1); // int literal
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
        results = self._run_compiler_pipeline(code, "valid_program")
        self.assertIsNotNone(results['ast'], "AST should be generated for valid code.")
        self.assertFalse(results['lexical_errors'], "No lexical errors expected.")
        self.assertFalse(results['syntax_errors'], "No syntax errors expected.")
        self.assertFalse(results['scope_errors'], f"No scope errors expected. Got: {results['scope_error_messages']}")
        self.assertFalse(results['type_errors'], f"No type errors expected. Got: {results['type_error_messages']}")

    def test_02_scope_error_y_undefined(self):
        code_actual_fail = """
        void main() {
            int x = 5;
            if (x == 5) {
                int y_in_if = 10;
            }
            print(y_in_if); // Error: y_in_if not defined here
        }"""
        results = self._run_compiler_pipeline(code_actual_fail, "scope_y_undefined")
        self.assertTrue(results['scope_errors'], f"Expected scope error for undefined 'y_in_if'. Messages: {results['scope_error_messages']}")

    def test_03_scope_error_x_redeclared(self):
        code = """
        void main() {
            int x = 5;
            int x = 10; // Scope Error: x redeclared in same scope
        }"""
        results = self._run_compiler_pipeline(code, "scope_x_redeclared")
        self.assertTrue(results['scope_errors'], f"Expected scope error for redeclared 'x'. Messages: {results['scope_error_messages']}")

    def test_04_scope_error_func_undefined_call(self):
        code = """
        void main() {
            calcular(); // Scope Error: calcular not defined
        }"""
        results = self._run_compiler_pipeline(code, "scope_func_undefined")
        # An undefined function call will be caught by ScopeChecker first when it tries to look up the function.
        self.assertTrue(results['scope_errors'],
                        f"Expected scope error for undefined function 'calcular'. Scope: {results['scope_error_messages']}")


    def test_05_type_error_string_plus_int(self):
        code = """
        void main() {
            string s = "hello";
            int count = 5;
            print(s + count); // Type Error: string + int (if '+' is not overloaded for this)
        }"""
        results = self._run_compiler_pipeline(code, "type_string_plus_int")
        self.assertTrue(results['type_errors'], f"Expected type error for string + int. Messages: {results['type_error_messages']}")

    def test_06_type_error_if_condition_not_bool(self):
        code = """
        void main() {
            int x = 10;
            if (x) { // Type Error: condition not bool
                print(1);
            }
        }"""
        results = self._run_compiler_pipeline(code, "type_if_condition_not_bool")
        self.assertTrue(results['type_errors'], f"Expected type error for non-boolean if condition. Messages: {results['type_error_messages']}")

    def test_07_type_error_assignment_mismatch(self):
        code = """
        void main() {
            int num;
            num = "this is not a number"; // Type Error: string to int
        }"""
        results = self._run_compiler_pipeline(code, "type_assignment_mismatch")
        self.assertTrue(results['type_errors'], f"Expected type error for string to int assignment. Messages: {results['type_error_messages']}")

    def test_08_type_error_return_mismatch(self):
        code = """
        int get_val() {
            string msg = "message";
            return msg; // Type Error: returning string from int function
        }
        void main() {
            int v = get_val(); // Call is okay if function signature is found
            print(v);
        }"""
        results = self._run_compiler_pipeline(code, "type_return_mismatch")
        self.assertTrue(results['type_errors'], f"Expected type error for return type mismatch. Messages: {results['type_error_messages']}")

    def test_09_type_error_function_arg_mismatch(self):
        code = """
        int add(int a, int b) {
            return a + b;
        }
        void main() {
            int res = add(5, "world"); // Type Error: "world" is not int for b
            print(res);
        }"""
        results = self._run_compiler_pipeline(code, "type_func_arg_mismatch")
        self.assertTrue(results['type_errors'], f"Expected type error for function argument mismatch. Messages: {results['type_error_messages']}")

    def test_10_valid_for_loop(self):
        code = """
        void main() {
            int sum = 0;
            for (int i = 0; i < 5; i = i + 1) {
                sum = sum + i;
            }
            print(sum); // Should be 10
        }"""
        results = self._run_compiler_pipeline(code, "valid_for_loop")
        self.assertFalse(results['scope_errors'], f"No scope errors expected for valid for-loop. Got: {results['scope_error_messages']}")
        self.assertFalse(results['type_errors'], f"No type errors expected for valid for-loop. Got: {results['type_error_messages']}")


if __name__ == '__main__':
    unittest.main()
