# PROYECTO/TypeChecker.py

class TypeChecker:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.errors = []
        self.current_function_return_type = None

    def log_error(self, message, node=None):
        # print(f"Node: {node}") # For debugging
        self.errors.append(message)

    def check_program(self, node):
        if node[0] != 'program':
            self.log_error("Invalid AST root, expected 'program'.", node)
            return

        functions_list = node[1]
        for func_or_main in functions_list:
            if func_or_main[0] == 'function':
                _, return_type, name, params_list, block_node = func_or_main
                self.current_function_return_type = return_type
                # ScopeChecker should have added params to symbol_table for the function's scope
                # If TypeChecker needs its own scope management that mirrors SymbolTable's,
                # this is where we'd `enter_scope`. For now, assume SymbolTable handles it.
                self.check_node(block_node)
                self.current_function_return_type = None
            elif func_or_main[0] == 'main_function':
                _, params_list, block_node = func_or_main
                self.current_function_return_type = 'void'
                self.check_node(block_node)
                self.current_function_return_type = None

    def check_node(self, node):
        if node is None:
            return

        if isinstance(node, tuple):
            node_type = node[0]

            if node_type == 'block':
                # ('block', [statements])
                # SymbolTable manages actual scope entry/exit. TypeChecker just processes statements.
                for stmt in node[1]:
                    self.check_node(stmt)
            elif node_type == 'declaration':
                # ('declaration', type_str, name_str, init_expr_node_or_None)
                self._check_declaration(node)
            elif node_type == 'assignment':
                # ('assignment', name_str, expr_node)
                self._check_assignment(node)
            elif node_type == 'if':
                # ('if', condition_expr_node, then_block_node, else_block_node_or_None)
                self._check_if(node)
            elif node_type == 'while':
                # ('while', condition_expr_node, block_node)
                self._check_while(node)
            elif node_type == 'for':
                # ('for', init_assign_node, condition_expr_node, update_assign_node, block_node)
                self._check_for(node)
            elif node_type == 'return':
                # ('return', expr_node_or_None)
                self._check_return(node)
            elif node_type == 'print':
                # ('print', expr_node)
                self._check_print(node)
            elif node_type == 'call':
                # Function call used as a statement
                self.infer_expression_type(node) # Infer to check args, return type not used here
            # Other expression nodes are handled by infer_expression_type when they are part of statements.

        elif isinstance(node, list): # Should not happen if blocks are handled correctly
            for item in node:
                self.check_node(item)
        # Else: Literals or other simple nodes not requiring direct check_node actions.

    def _check_declaration(self, decl_node):
        # ('declaration', declared_type_str, var_name_str, init_expr_node_or_None)
        _, declared_type, var_name, init_expr = decl_node

        # Variable type itself is usually validated by parser against known types (INT, FLOAT etc)
        # ScopeChecker handles duplicate declarations.

        if init_expr is not None:
            value_type = self.infer_expression_type(init_expr)
            if value_type != 'error_type': # Proceed only if initializer is valid
                if not self.is_assignable(declared_type, value_type):
                    self.log_error(f"Type mismatch in declaration of '{var_name}': Cannot assign '{value_type}' to '{declared_type}'.", decl_node)
        # If init_expr is None, no type checking needed for assignment part.

    def _check_assignment(self, assign_node):
        # ('assignment', var_name_str, value_expr_node)
        _, var_name, value_expr = assign_node

        var_info = self.symbol_table.lookup_variable(var_name)
        if not var_info:
            # This error should ideally be caught by ScopeChecker.
            # If it reaches here, it means ScopeChecker might have missed it or is not run before TypeChecker.
            self.log_error(f"Assignment to undeclared variable '{var_name}'.", assign_node)
            return

        declared_type = var_info['type']
        value_type = self.infer_expression_type(value_expr)

        if value_type != 'error_type':
            if not self.is_assignable(declared_type, value_type):
                self.log_error(f"Type mismatch in assignment to '{var_name}': Cannot assign '{value_type}' to '{declared_type}'.", assign_node)

    def _check_if(self, if_node):
        # ('if', condition_expr, then_block_node, else_block_node_or_None)
        _, condition_expr, then_block, else_block = if_node

        condition_type = self.infer_expression_type(condition_expr)
        if condition_type != 'bool' and condition_type != 'error_type':
            self.log_error(f"If statement condition must be boolean, got '{condition_type}'.", condition_expr)

        self.check_node(then_block) # Check the 'then' block

        if else_block is not None:
            self.check_node(else_block) # Check the 'else' block

    def _check_while(self, while_node):
        # ('while', condition_expr, block_node)
        _, condition_expr, block = while_node

        condition_type = self.infer_expression_type(condition_expr)
        if condition_type != 'bool' and condition_type != 'error_type':
            self.log_error(f"While loop condition must be boolean, got '{condition_type}'.", condition_expr)

        self.check_node(block) # Check the loop body

    def _check_for(self, for_node):
        # ('for', init_node, condition_expr_node, update_node, block_node)
        # init_node and update_node can be 'declaration' or 'assignment' or None
        _, init_node, condition_expr, update_node, block = for_node

        if init_node:
            self.check_node(init_node)

        condition_type = self.infer_expression_type(condition_expr)
        if condition_type != 'bool' and condition_type != 'error_type':
             self.log_error(f"For loop condition must be boolean, got '{condition_type}'.", condition_expr)

        if update_node:
            self.check_node(update_node)

        self.check_node(block) # Check the loop body

    def _check_return(self, return_node):
        # ('return', expr_node_or_None)
        _, expr = return_node

        expected_return_type = self.current_function_return_type
        if expected_return_type is None:
            self.log_error("Return statement found outside of a function.", return_node)
            return

        actual_return_type = 'void' # Assume void if expr is None
        if expr is not None:
            actual_return_type = self.infer_expression_type(expr)

        if actual_return_type == 'error_type':
            return

        if expected_return_type == 'void':
            if actual_return_type != 'void':
                self.log_error(f"Function with 'void' return type cannot return a value of type '{actual_return_type}'.", return_node)
        elif not self.is_assignable(expected_return_type, actual_return_type):
            self.log_error(f"Type mismatch in return statement: Expected '{expected_return_type}', got '{actual_return_type}'.", return_node)

    def _check_print(self, print_node):
        # ('print', expr_node)
        _, expr = print_node
        expr_type = self.infer_expression_type(expr)

        if expr_type == 'error_type':
            pass
        elif expr_type in ('void'):
             self.log_error(f"Cannot print expression of type '{expr_type}'.", print_node)


    def _infer_binary_op_type(self, op, left_type, right_type, node):
        op_map = {
            'plus': '+', 'minus': '-', 'times': '*', 'divide': '/', 'mod': '%',
            'or': 'or', 'and': 'and',
            'eq': '==', 'ne': '!=', 'lt': '<', 'gt': '>', 'le': '<=', 'ge': '>='
        }
        symbol_op = op_map.get(op, op)

        if symbol_op in ('+', '-', '*', '/', '%'):
            if symbol_op == '+' and left_type == 'string' and right_type == 'string':
                return 'string'
            if left_type == 'int' and right_type == 'int':
                return 'int'
            elif (left_type == 'int' and right_type == 'float') or \
                 (left_type == 'float' and right_type == 'int') or \
                 (left_type == 'float' and right_type == 'float'):
                return 'float'
            else:
                self.log_error(f"Type mismatch: Cannot apply operator '{symbol_op}' to '{left_type}' and '{right_type}'.", node)
                return 'error_type'
        elif symbol_op in ('==', '!=', '<', '>', '<=', '>='):
            if (left_type in ('int', 'float') and right_type in ('int', 'float')) or \
               (left_type == 'string' and right_type == 'string') or \
               (left_type == 'bool' and right_type == 'bool'):
                return 'bool'
            else:
                self.log_error(f"Type mismatch: Cannot compare '{left_type}' and '{right_type}' with '{symbol_op}'.", node)
                return 'error_type'
        elif symbol_op in ('and', 'or'):
            if left_type == 'bool' and right_type == 'bool':
                return 'bool'
            else:
                self.log_error(f"Type mismatch: Logical operator '{symbol_op}' requires boolean operands, got '{left_type}' and '{right_type}'.", node)
                return 'error_type'
        else:
            self.log_error(f"Unknown binary operator '{op}'.", node)
            return 'error_type'

    def infer_expression_type(self, expr_node):
        if expr_node is None: # E.g. empty return statement
            return 'void'

        node_type = expr_node[0]

        if node_type == 'number':
            if isinstance(expr_node[1], int):
                return 'int'
            elif isinstance(expr_node[1], float):
                return 'float'
            else:
                self.log_error(f"Unknown number literal type: {expr_node[1]}", expr_node)
                return 'error_type'
        elif node_type == 'string':
            return 'string'
        elif node_type == 'bool':
            return 'bool'
        elif node_type == 'id':
            var_name = expr_node[1]
            var_info = self.symbol_table.lookup_variable(var_name)
            if var_info:
                return var_info['type']
            else:
                self.log_error(f"Undeclared variable '{var_name}'.", expr_node)
                return 'error_type'
        elif node_type in ('plus', 'minus', 'times', 'divide', 'mod', 'or', 'and', 'eq', 'ne', 'lt', 'gt', 'le', 'ge'):
            op = node_type
            left_expr = expr_node[1]
            right_expr = expr_node[2]

            left_type = self.infer_expression_type(left_expr)
            if left_type == 'error_type': return 'error_type'

            right_type = self.infer_expression_type(right_expr)
            if right_type == 'error_type': return 'error_type'

            return self._infer_binary_op_type(op, left_type, right_type, expr_node)

        elif node_type == 'call':
            func_name = expr_node[1]
            arg_exprs = expr_node[2]

            func_info = self.symbol_table.lookup_function(func_name)
            if not func_info:
                self.log_error(f"Call to undefined function '{func_name}'.", expr_node)
                return 'error_type'

            expected_param_count = len(func_info['params'])
            actual_arg_count = len(arg_exprs)
            if expected_param_count != actual_arg_count:
                self.log_error(f"Function '{func_name}' expects {expected_param_count} arguments, but got {actual_arg_count}.", expr_node)
                return 'error_type'

            param_types = [p[0] for p in func_info['params']]
            for i, arg_expr in enumerate(arg_exprs):
                arg_type = self.infer_expression_type(arg_expr)
                if arg_type == 'error_type': return 'error_type'

                if i < len(param_types):
                    expected_param_type = param_types[i]
                    if not self.is_assignable(expected_param_type, arg_type):
                        self.log_error(f"Type mismatch in argument {i+1} of function '{func_name}': Expected '{expected_param_type}', got '{arg_type}'.", arg_expr)
                        return 'error_type'
            return func_info['return_type']

        else:
            self.log_error(f"Cannot infer type for unhandled expression node type: '{node_type}'.", expr_node)
            return 'error_type'

    def is_assignable(self, var_type, value_type):
        if var_type == value_type:
            return True
        if var_type == 'float' and value_type == 'int':
            return True
        if var_type == 'int' and value_type == 'float':
            return True
        # Prevent cascading errors if a type is already 'error_type'
        if var_type == 'error_type' or value_type == 'error_type':
            return True # Assume error was logged where 'error_type' originated
        return False

    def get_errors(self):
        return self.errors
'''
if __name__ == '__main__':
    print("TypeChecker class with statement checking logic.")

    # Mock SymbolTable for testing (mimicking ScopeChecker.SymbolTable)
    class MockSymbolTable:
        def __init__(self):
            self.variables = {} # var_name -> {'type': type_str, 'scope_level': int}
            self.functions = {} # func_name -> {'params': [(type, name)], 'return_type': type_str}
            self.current_scope_level = 0

        def add_variable(self, name, type_str):
            # Simplified: assumes unique names for testing, no real scope handling here
            self.variables[name] = {'type': type_str, 'scope_level': self.current_scope_level}
            # print(f"MockST: Added var {name} type {type_str}")


        def lookup_variable(self, name):
            # Simplified lookup
            # print(f"MockST: Looking up var {name}")
            return self.variables.get(name)

        def add_function(self, name, params, return_type):
            self.functions[name] = {'params': params, 'return_type': return_type}
            # print(f"MockST: Added func {name}")


        def lookup_function(self, name):
            # print(f"MockST: Looking up func {name}")
            return self.functions.get(name)

    st = MockSymbolTable()
    tc = TypeChecker(st)

    # --- Populate Symbol Table for Tests ---
    st.add_variable("g_int", "int")
    st.add_variable("g_float", "float")
    st.add_variable("g_string", "string")
    st.add_variable("g_bool", "bool")
    st.add_function("get_int", [], "int")
    st.add_function("proc_void", [], "void")
    st.add_function("needs_bool", [('bool', 'b_param')], "void")
    st.add_function("needs_int_float", [('int', 'i_param'), ('float', 'f_param')], "string")

    # --- Test Cases ---
    tc.errors = [] # Reset errors

    print("\n--- Declaration Tests ---")
    # int x = 10; (OK)
    decl_ok_node = ('declaration', 'int', 'x_ok', ('number', 10))
    st.add_variable("x_ok", "int") # Simulate ScopeChecker action
    tc._check_declaration(decl_ok_node)

    # float y = x_ok; (OK, int to float)
    decl_ok_assign_id = ('declaration', 'float', 'y_ok', ('id', 'x_ok'))
    st.add_variable("y_ok", "float")
    tc._check_declaration(decl_ok_assign_id)

    # int z = 0.5; (OK by rule: float to int)
    decl_float_to_int_node = ('declaration', 'int', 'z_f_to_i', ('number', 0.5))
    st.add_variable("z_f_to_i", "int")
    tc._check_declaration(decl_float_to_int_node)

    # string s = 10; (Error)
    decl_err_node = ('declaration', 'string', 's_err', ('number', 10))
    st.add_variable("s_err", "string")
    tc._check_declaration(decl_err_node)

    print("\n--- Assignment Tests ---")
    # g_int = 20; (OK)
    assign_ok_node = ('assignment', 'g_int', ('number', 20))
    tc._check_assignment(assign_ok_node)

    # g_float = g_int; (OK, int to float)
    assign_ok_int_to_float_node = ('assignment', 'g_float', ('id', 'g_int'))
    tc._check_assignment(assign_ok_int_to_float_node)

    # g_string = g_int; (Error)
    assign_err_node = ('assignment', 'g_string', ('id', 'g_int'))
    tc._check_assignment(assign_err_node)

    # undeclared_var = 10; (Error - logged by _check_assignment if ScopeChecker missed)
    assign_undeclared_node = ('assignment', 'undeclared_var', ('number', 10))
    tc._check_assignment(assign_undeclared_node)

    print("\n--- If Statement Tests ---")
    # if (true) { } (OK)
    if_ok_node = ('if', ('bool', True), ('block', []), None)
    tc._check_if(if_ok_node)

    # if (g_int == 10) { g_bool = false; } else { g_string = "err"; } (OK structure)
    st.add_variable("g_bool_in_if", "bool") # ensure var exists for assignment in block
    st.add_variable("g_str_in_if", "string")
    if_complex_node = ('if',
                       ('eq', ('id', 'g_int'), ('number', 10)),
                       ('block', [('assignment', 'g_bool_in_if', ('bool', False))]),
                       ('block', [('assignment', 'g_str_in_if', ('string', "error_in_else"))])) # type error in assign
    tc._check_if(if_complex_node)


    # if (10) { } (Error: condition not bool)
    if_err_cond_node = ('if', ('number', 10), ('block', []), None)
    tc._check_if(if_err_cond_node)

    print("\n--- While Statement Tests ---")
    # while (g_int < 20) { g_int = g_int + 1; } (OK)
    st.add_variable("g_int_plus_one", "int") # For the result of g_int + 1 if it were a separate var
    while_ok_node = ('while',
                     ('lt', ('id', 'g_int'), ('number', 20)),
                     ('block', [('assignment', 'g_int', ('plus', ('id', 'g_int'), ('number', 1)))]))
    tc._check_while(while_ok_node)

    # while ("string") {} (Error: condition not bool)
    while_err_cond_node = ('while', ('string', "not bool"), ('block', []))
    tc._check_while(while_err_cond_node)

    print("\n--- For Statement Tests ---")
    # for (int i=0; i<10; i=i+1) { print i; }
    # Note: Parser.py AST for 'for' is ('for', init, cond, update, block)
    # init/update can be declaration/assignment. Need to ensure 'i' is in symbol table for loop body.
    st.add_variable("i", "int") # Simulate declaration for loop var 'i'
    for_ok_node = ('for',
                   ('declaration', 'int', 'i', ('number', 0)), # or ('assignment', 'i', ('number', 0)) if already declared
                   ('lt', ('id', 'i'), ('number', 10)),
                   ('assignment', 'i', ('plus', ('id', 'i'), ('number', 1))),
                   ('block', [('print', ('id', 'i'))])
                  )
    # For the test to run properly, we'd need a way to handle loop variable scope,
    # or assume 'i' is declared before the loop for this simplified test.
    # For now, let's assume 'i' is handled by symbol table (added above).
    tc._check_for(for_ok_node) # This will try to re-declare 'i' if not handled by ST scopes.
                               # For isolated _check_for test, it's tricky.
                               # A proper test would run check_program.

    print("\n--- Return Statement Tests ---")
    tc.current_function_return_type = 'int'
    return_ok_node = ('return', ('number', 10))
    tc._check_return(return_ok_node)

    return_err_type_node = ('return', ('string', "hello"))
    tc._check_return(return_err_type_node)

    tc.current_function_return_type = 'void'
    return_void_ok_node = ('return', None)
    tc._check_return(return_void_ok_node)

    return_void_err_val_node = ('return', ('number', 10))
    tc._check_return(return_void_err_val_node)
    tc.current_function_return_type = None # Reset

    print("\n--- Print Statement Tests ---")
    print_ok_str_node = ('print', ('string', "Hello"))
    tc._check_print(print_ok_str_node)

    print_ok_id_node = ('print', ('id', 'g_int'))
    tc._check_print(print_ok_id_node)

    # print proc_void(); (Error: cannot print void)
    print_err_void_node = ('print', ('call', 'proc_void', []))
    tc._check_print(print_err_void_node)

    print("\n--- Call Statement Test ---")
    # needs_bool(g_int == 0); (OK)
    call_stmt_ok_node = ('call', 'needs_bool', [('eq', ('id', 'g_int'), ('number', 0))])
    tc.check_node(call_stmt_ok_node) # Using check_node for dispatch

    # needs_bool(g_string); (Error)
    call_stmt_err_node = ('call', 'needs_bool', [('id', 'g_string')])
    tc.check_node(call_stmt_err_node)


    # --- Display Errors ---
    errors = tc.get_errors()
    if errors:
        print("\n--- Collected Type Errors ---")
        for error in errors:
            print(error)
    else:
        print("\n--- No type errors detected in these specific tests (or errors handled as expected). ---")

'''
