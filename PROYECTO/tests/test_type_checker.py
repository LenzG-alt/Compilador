# PROYECTO/tests/test_type_checker.py

# This file adapts the example usage and basic tests from
# PROYECTO/TypeChecker.py's `if __name__ == '__main__':` block
# into a standalone test script.

from PROYECTO.TypeChecker import TypeChecker # Adjusted import path

# Mock SymbolTable for testing (mimicking ScopeChecker.SymbolTable behavior)
class MockSymbolTable:
    def __init__(self):
        self.variables = {} # var_name -> {'type': type_str, 'scope_level': int}
        self.functions = {} # func_name -> {'params': [(type, name)], 'return_type': type_str}
        # Add other necessary attributes or methods if TypeChecker relies on them
        # e.g., scope management if TypeChecker uses it beyond lookups.
        # For the tests copied, TypeChecker primarily uses lookup_variable and lookup_function.

    def add_variable(self, name, type_str, scope='global'): # Simplified
        self.variables[name] = {'type': type_str, 'scope': scope}

    def lookup_variable(self, name):
        return self.variables.get(name, None)

    def add_function(self, name, params, return_type): # params = list of (type, name)
        self.functions[name] = {'params': params, 'return_type': return_type}

    def lookup_function(self, name):
        return self.functions.get(name, None)

def run_type_checker_tests():
    print("--- Running Standalone TypeChecker Tests ---")

    mock_symbol_table = MockSymbolTable()
    # Populate symbol table for a more meaningful test
    mock_symbol_table.add_variable("x", "int")
    mock_symbol_table.add_variable("y", "float")
    mock_symbol_table.add_variable("s", "string")
    mock_symbol_table.add_variable("b", "bool")
    mock_symbol_table.add_function("myFunc", [('int', 'a'), ('string', 'b_str')], "bool")
    mock_symbol_table.add_function("proc", [], "void")
    # From main.py test cases, useful for statement checking tests
    mock_symbol_table.add_variable("g_int", "int")
    mock_symbol_table.add_variable("g_float", "float")
    mock_symbol_table.add_variable("g_string", "string")
    mock_symbol_table.add_variable("g_bool", "bool")
    mock_symbol_table.add_variable("g_bool_in_if", "bool")
    mock_symbol_table.add_variable("g_str_in_if", "string")


    type_checker = TypeChecker(mock_symbol_table)

    # --- Test cases for infer_expression_type (from TypeChecker.py) ---
    print("\n--- Expression Inference Tests (from TypeChecker.py) ---")
    ast_id_x = ('id', 'x')
    ast_id_y = ('id', 'y')
    ast_id_s = ('id', 's')
    ast_id_b = ('id', 'b')
    ast_id_unknown = ('id', 'unknown')
    ast_num_int = ('number', 10)
    ast_num_float = ('number', 5.5)
    ast_str_lit = ('string', "hello")
    ast_bool_lit = ('bool', True)

    print(f"Type of x ('id', 'x'): {type_checker.infer_expression_type(ast_id_x)}")
    print(f"Type of y ('id', 'y'): {type_checker.infer_expression_type(ast_id_y)}")
    print(f"Type of s ('id', 's'): {type_checker.infer_expression_type(ast_id_s)}")
    print(f"Type of b ('id', 'b'): {type_checker.infer_expression_type(ast_id_b)}")
    print(f"Type of unknown ('id', 'unknown'): {type_checker.infer_expression_type(ast_id_unknown)}")
    print(f"Type of 10 ('number', 10): {type_checker.infer_expression_type(ast_num_int)}")
    print(f"Type of 5.5 ('number', 5.5): {type_checker.infer_expression_type(ast_num_float)}")
    print(f"Type of \"hello\" ('string', \"hello\"): {type_checker.infer_expression_type(ast_str_lit)}")
    print(f"Type of True ('bool', True): {type_checker.infer_expression_type(ast_bool_lit)}")

    type_checker.errors = []

    print("\n--- Binary Operation Expression Tests (from TypeChecker.py) ---")
    ast_plus_int_int = ('plus', ast_id_x, ast_num_int)
    print(f"Type of x + 10: {type_checker.infer_expression_type(ast_plus_int_int)}")

    ast_plus_int_float = ('plus', ast_id_x, ast_num_float)
    print(f"Type of x + 5.5: {type_checker.infer_expression_type(ast_plus_int_float)}")

    ast_plus_str_str = ('plus', ast_str_lit, ast_id_s)
    print(f"Type of \"hello\" + s: {type_checker.infer_expression_type(ast_plus_str_str)}")

    ast_plus_error = ('plus', ast_id_x, ast_str_lit)
    print(f"Type of x + \"hello\": {type_checker.infer_expression_type(ast_plus_error)}")

    ast_eq_int_int = ('eq', ast_id_x, ast_num_int)
    print(f"Type of x == 10: {type_checker.infer_expression_type(ast_eq_int_int)}")

    ast_and_bool_bool = ('and', ast_id_b, ast_bool_lit)
    print(f"Type of b and True: {type_checker.infer_expression_type(ast_and_bool_bool)}")

    ast_and_error = ('and', ast_id_b, ast_num_int)
    print(f"Type of b and 10: {type_checker.infer_expression_type(ast_and_error)}")

    type_checker.errors = []

    print("\n--- Function Call Expression Tests (from TypeChecker.py) ---")
    ast_call_ok = ('call', 'myFunc', [ast_id_x, ast_id_s])
    print(f"Type of myFunc(x,s): {type_checker.infer_expression_type(ast_call_ok)}")

    ast_call_arg_count_err = ('call', 'myFunc', [ast_id_x])
    print(f"Type of myFunc(x): {type_checker.infer_expression_type(ast_call_arg_count_err)}")

    current_errors = type_checker.get_errors() # Check errors immediately for this one
    if any("expects 2 arguments, but got 1" in err for err in current_errors):
        print("  -> Correctly logged argument count error for myFunc(x).")
    type_checker.errors = [] # Clear for next specific test

    ast_call_arg_type_err = ('call', 'myFunc', [ast_id_y, ast_id_s]) # y is float, myFunc expects int
    print(f"Type of myFunc(y,s): {type_checker.infer_expression_type(ast_call_arg_type_err)}")

    current_errors = type_checker.get_errors()
    if any("Expected 'int', got 'float'" in err for err in current_errors):
        print("  -> Correctly logged argument type error for myFunc(y,s).")
    type_checker.errors = []


    ast_call_proc = ('call', 'proc', [])
    print(f"Type of proc(): {type_checker.infer_expression_type(ast_call_proc)}")

    ast_call_unknown_func = ('call', 'unknown_func', [])
    print(f"Type of unknown_func(): {type_checker.infer_expression_type(ast_call_unknown_func)}")

    # --- Test cases for statements (adapted from TypeChecker.py's __main__ for statement checks) ---
    print("\n--- Statement Checking Tests (Adapted from TypeChecker.py) ---")
    type_checker.errors = [] # Fresh start for statement errors

    print("--- Declaration Statement Tests ---")
    decl_ok_node = ('declaration', 'int', 'x_decl_ok', ('number', 10))
    mock_symbol_table.add_variable("x_decl_ok", "int")
    type_checker._check_declaration(decl_ok_node)

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

    assign_undeclared_node = ('assignment', 'undeclared_var_assign', ('number', 10))
    type_checker._check_assignment(assign_undeclared_node)

    print("\n--- If Statement Tests ---")
    if_ok_node = ('if', ('bool', True), ('block', []), None)
    type_checker._check_if(if_ok_node)

    if_complex_node = ('if',
                       ('eq', ('id', 'g_int'), ('number', 10)),
                       ('block', [('assignment', 'g_bool_in_if', ('bool', False))]),
                       ('block', [('assignment', 'g_str_in_if', ('plus', ('id','g_int'), ('number',1)) )])) # Error: int to string assign
    type_checker._check_if(if_complex_node)


    if_err_cond_node = ('if', ('number', 10), ('block', []), None)
    type_checker._check_if(if_err_cond_node)

    print("\n--- While Statement Tests ---")
    while_ok_node = ('while',
                     ('lt', ('id', 'g_int'), ('number', 20)),
                     ('block', [('assignment', 'g_int', ('plus', ('id', 'g_int'), ('number', 1)))]))
    type_checker._check_while(while_ok_node)

    while_err_cond_node = ('while', ('string', "not bool"), ('block', []))
    type_checker._check_while(while_err_cond_node)

    print("\n--- Return Statement Tests ---")
    type_checker.current_function_return_type = 'int'
    return_ok_node = ('return', ('number', 10))
    type_checker._check_return(return_ok_node)

    return_err_type_node = ('return', ('string', "hello"))
    type_checker._check_return(return_err_type_node)

    type_checker.current_function_return_type = 'void'
    return_void_ok_node = ('return', None)
    type_checker._check_return(return_void_ok_node)

    return_void_err_val_node = ('return', ('number', 10))
    type_checker._check_return(return_void_err_val_node)
    type_checker.current_function_return_type = None

    print("\n--- Print Statement Tests ---")
    print_ok_str_node = ('print', ('string', "Hello"))
    type_checker._check_print(print_ok_str_node)

    print_ok_id_node = ('print', ('id', 'g_int'))
    type_checker._check_print(print_ok_id_node)

    print_err_void_node = ('print', ('call', 'proc', [])) # proc returns void
    type_checker._check_print(print_err_void_node)

    # --- Display All Collected Errors from TypeChecker ---
    all_errors = type_checker.get_errors()
    if all_errors:
        print("\n--- All Collected Errors During Standalone Tests ---")
        for error_idx, error_message in enumerate(all_errors):
            print(f"Error {error_idx + 1}: {error_message}")
    else:
        print("\n--- No errors collected during standalone TypeChecker tests. ---")

if __name__ == '__main__':
    # To make this runnable from project root (e.g. python -m PROYECTO.tests.test_type_checker)
    # ensure PROYECTO is in PYTHONPATH or adjust imports.
    # If run directly as PROYECTO/tests/test_type_checker.py, Python needs to find PROYECTO package.
    # One way: Add project root to sys.path if not already there.
    import sys
    import os
    # Get the absolute path to the 'PROYECTO' directory
    current_dir = os.path.dirname(os.path.abspath(__file__)) # PROYECTO/tests
    project_dir = os.path.dirname(current_dir) # PROYECTO
    if project_dir not in sys.path:
        sys.path.insert(0, os.path.dirname(project_dir)) # Add parent of PROYECTO (e.g. /app)

    # Now the import from PROYECTO.TypeChecker should work
    run_type_checker_tests()

```
