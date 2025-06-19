# PROYECTO/tests/test_type_checker.py

# This file adapts the example usage and basic tests from
# PROYECTO/TypeChecker.py's `if __name__ == '__main__':` block
# into a standalone test script.

import sys
import os

# --- Robust sys.path modification ---
# Goal: Ensure the directory *containing* the 'PROYECTO' package is in sys.path.
# This allows imports like `from PROYECTO.SomeModule import Something`.

# current_script_dir is /path/to/PROYECTO/tests
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# project_dir (PROYECTO) is /path/to/PROYECTO
project_dir = os.path.dirname(current_script_dir)
# project_container_dir (parent of PROYECTO) is /path/to
project_container_dir = os.path.dirname(project_dir)

# Add the container of PROYECTO to sys.path if not already there.
if project_container_dir not in sys.path:
    sys.path.insert(0, project_container_dir)

# --- Imports ---
# Now we can use absolute imports from the PROYECTO package.
from PROYECTO.TypeChecker import TypeChecker
from PROYECTO.ScopeChecker import SymbolTable # Using actual SymbolTable for future, though Mock is used now.


# Mock SymbolTable for testing (mimicking ScopeChecker.SymbolTable behavior)
class MockSymbolTable:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def add_variable(self, name, type_str, scope='global'):
        self.variables[name] = {'type': type_str, 'scope': scope}

    def lookup_variable(self, name):
        return self.variables.get(name, None)

    def add_function(self, name, params, return_type):
        self.functions[name] = {'params': params, 'return_type': return_type}

    def lookup_function(self, name):
        return self.functions.get(name, None)

def run_type_checker_tests():
    print("--- Running Standalone TypeChecker Tests ---")

    # Ensure the output directory for test logs exists
    test_output_dir = os.path.join(project_dir, "salida_tests_typechecker_standalone")
    os.makedirs(test_output_dir, exist_ok=True)


    mock_symbol_table = MockSymbolTable()
    # Populate symbol table
    mock_symbol_table.add_variable("x", "int")
    mock_symbol_table.add_variable("y", "float")
    mock_symbol_table.add_variable("s", "string")
    mock_symbol_table.add_variable("b", "bool")
    mock_symbol_table.add_function("myFunc", [('int', 'a'), ('string', 'b_str')], "bool")
    mock_symbol_table.add_function("proc", [], "void")

    # Variables from original test cases for statement checking
    mock_symbol_table.add_variable("g_int", "int")
    mock_symbol_table.add_variable("g_float", "float")
    mock_symbol_table.add_variable("g_string", "string")
    mock_symbol_table.add_variable("g_bool", "bool")
    mock_symbol_table.add_variable("g_bool_in_if", "bool")
    mock_symbol_table.add_variable("g_str_in_if", "string")


    type_checker = TypeChecker(mock_symbol_table, output_dir=test_output_dir)

    # --- Test cases for infer_expression_type ---
    print("\n--- Expression Inference Tests ---")
    ast_id_x = ('id', 'x')
    ast_id_y = ('id', 'y')
    ast_id_s = ('id', 's')
    ast_id_b = ('id', 'b')
    ast_id_unknown = ('id', 'unknown')
    ast_num_int = ('number', 10)
    ast_num_float = ('number', 5.5)
    ast_str_lit = ('string', "hello")
    ast_bool_lit = ('bool', True)

    def print_expr_type(label, expr_node):
        inferred_type = type_checker._infer_expression_type(expr_node) # Accessing protected for direct test
        print(f"Type of {label}: {inferred_type}")

    print_expr_type("x ('id', 'x')", ast_id_x)
    print_expr_type("y ('id', 'y')", ast_id_y)
    print_expr_type("s ('id', 's')", ast_id_s)
    print_expr_type("b ('id', 'b')", ast_id_b)
    print_expr_type("unknown ('id', 'unknown')", ast_id_unknown)
    print_expr_type("10 ('number', 10)", ast_num_int)
    print_expr_type("5.5 ('number', 5.5)", ast_num_float)
    print_expr_type("\"hello\" ('string', \"hello\")", ast_str_lit)
    print_expr_type("True ('bool', True)", ast_bool_lit)

    type_checker.errors = []

    print("\n--- Binary Operation Expression Tests ---")
    ast_plus_int_int = ('plus', ast_id_x, ast_num_int)
    print_expr_type("x + 10", ast_plus_int_int)

    ast_plus_int_float = ('plus', ast_id_x, ast_num_float)
    print_expr_type("x + 5.5", ast_plus_int_float)

    ast_plus_str_str = ('plus', ast_str_lit, ast_id_s)
    print_expr_type("\"hello\" + s", ast_plus_str_str)

    ast_plus_error = ('plus', ast_id_x, ast_str_lit)
    print_expr_type("x + \"hello\" (error expected)", ast_plus_error)

    ast_eq_int_int = ('eq', ast_id_x, ast_num_int)
    print_expr_type("x == 10", ast_eq_int_int)

    ast_and_bool_bool = ('and', ast_id_b, ast_bool_lit)
    print_expr_type("b and True", ast_and_bool_bool)

    ast_and_error = ('and', ast_id_b, ast_num_int)
    print_expr_type("b and 10 (error expected)", ast_and_error)

    type_checker.errors = []

    print("\n--- Function Call Expression Tests ---")
    # AST for args is ('args', [arg_expr_node, ...])
    ast_call_ok = ('call', 'myFunc', ('args', [ast_id_x, ast_id_s]))
    print_expr_type("myFunc(x,s)", ast_call_ok)

    ast_call_arg_count_err = ('call', 'myFunc', ('args', [ast_id_x]))
    print_expr_type("myFunc(x) (arg count error expected)", ast_call_arg_count_err)

    ast_call_arg_type_err = ('call', 'myFunc', ('args', [ast_id_y, ast_id_s]))
    print_expr_type("myFunc(y,s) (arg type error expected)", ast_call_arg_type_err)

    ast_call_proc = ('call', 'proc', ('args', []))
    print_expr_type("proc()", ast_call_proc)

    ast_call_unknown_func = ('call', 'unknown_func', ('args', []))
    print_expr_type("unknown_func() (error expected)", ast_call_unknown_func)

    type_checker.errors = []

    print("\n--- Statement Checking Tests ---")

    print("--- Declaration Statement Tests ---")
    decl_ok_node = ('declaration', 'int', 'x_decl_ok', ('number', 10))
    mock_symbol_table.add_variable("x_decl_ok", "int")
    type_checker._check_declaration(decl_ok_node) # Accessing protected for direct test

    decl_ok_assign_id_node = ('declaration', 'float', 'y_decl_ok', ('id', 'x_decl_ok'))
    mock_symbol_table.add_variable("y_decl_ok", "float")
    type_checker._check_declaration(decl_ok_assign_id_node)

    decl_float_to_int_node = ('declaration', 'int', 'z_f_to_i_decl', ('number', 0.5))
    mock_symbol_table.add_variable("z_f_to_i_decl", "int")
    type_checker._check_declaration(decl_float_to_int_node)

    decl_err_node = ('declaration', 'string', 's_decl_err', ('number', 10))
    mock_symbol_table.add_variable("s_decl_err", "string")
    type_checker._check_declaration(decl_err_node)

    print("\n--- Assignment Statement Tests ---")
    assign_ok_node = ('assignment', 'g_int', ('number', 20))
    type_checker._check_assignment(assign_ok_node)

    assign_ok_int_to_float_node = ('assignment', 'g_float', ('id', 'g_int'))
    type_checker._check_assignment(assign_ok_int_to_float_node)

    assign_err_node = ('assignment', 'g_string', ('id', 'g_int'))
    type_checker._check_assignment(assign_err_node)

    print("\n--- If Statement Tests ---")
    if_ok_node = ('if', ('bool', True), ('block', []), None)
    type_checker._check_if_statement(if_ok_node)

    if_complex_node = ('if',
                       ('eq', ('id', 'g_int'), ('number', 10)),
                       ('block', [('assignment', 'g_bool_in_if', ('bool', False))]),
                       ('block', [('assignment', 'g_str_in_if', ('plus', ('id','g_int'), ('number',1)) )]))
    type_checker._check_if_statement(if_complex_node)

    if_err_cond_node = ('if', ('number', 10), ('block', []), None)
    type_checker._check_if_statement(if_err_cond_node)

    print("\n--- While Statement Tests ---")
    while_ok_node = ('while',
                     ('lt', ('id', 'g_int'), ('number', 20)),
                     ('block', [('assignment', 'g_int', ('plus', ('id', 'g_int'), ('number', 1)))]))
    type_checker._check_while_statement(while_ok_node)

    while_err_cond_node = ('while', ('string', "not bool"), ('block', []))
    type_checker._check_while_statement(while_err_cond_node)

    print("\n--- Return Statement Tests ---")
    type_checker.current_function_return_type = 'int'
    return_ok_node = ('return', ('number', 10))
    type_checker._check_return_statement(return_ok_node)

    return_err_type_node = ('return', ('string', "hello"))
    type_checker._check_return_statement(return_err_type_node)

    type_checker.current_function_return_type = 'void'
    return_void_ok_node = ('return', None)
    type_checker._check_return_statement(return_void_ok_node)

    return_void_err_val_node = ('return', ('number', 10))
    type_checker._check_return_statement(return_void_err_val_node)
    type_checker.current_function_return_type = None

    print("\n--- Print Statement Tests ---")
    print_ok_str_node = ('print', ('string', "Hello"))
    type_checker._check_print_statement(print_ok_str_node)

    print_ok_id_node = ('print', ('id', 'g_int'))
    type_checker._check_print_statement(print_ok_id_node)

    print_err_void_node = ('print', ('call', 'proc', ('args', [])))
    type_checker._check_print_statement(print_err_void_node)

    all_errors = type_checker.get_errors()
    if all_errors:
        print("\n--- All Collected Errors During Standalone TypeChecker Tests ---")
        for error_idx, error_message in enumerate(all_errors):
            print(f"Error {error_idx + 1}: {error_message}")
        type_checker.save_errors_to_file()
        print(f"Standalone test errors saved to {type_checker.error_file_path}")
    else:
        print("\n--- No type errors collected during these standalone tests. ---")

if __name__ == '__main__':
    run_type_checker_tests()
