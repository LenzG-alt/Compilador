import os

class TypeChecker:
    """
    Performs type checking on an AST, using a symbol table populated by ScopeChecker.
    """
    def __init__(self, symbol_table, output_dir='salida', error_filename="errores_tipo.txt"):
        """
        Initializes the TypeChecker.

        Args:
            symbol_table (SymbolTable): The symbol table from ScopeChecker.
            output_dir (str): Directory to save error logs.
            error_filename (str): Name of the file for type errors.
        """
        self.symbol_table = symbol_table
        self.errors = []
        self.current_function_return_type = None # Stores the expected return type of the current function
        self.output_dir = output_dir
        self.error_file_path = os.path.join(output_dir, error_filename)
        os.makedirs(self.output_dir, exist_ok=True)
        # Clear previous errors at the start of a new check
        with open(self.error_file_path, 'w', encoding='utf-8') as f:
            f.write("") # Create or truncate the file

    def _log_error(self, message: str, node=None):
        """
        Logs a type error. Includes line number if node information is available.

        Args:
            message (str): The error message.
            node: The AST node associated with the error (optional, for line numbers).
        """
        # Placeholder for line number extraction - requires consistent AST node metadata
        line_info = ""
        # Example: if node and isinstance(node, tuple) and len(node) > 2 and isinstance(node[-1], dict) and 'lineno' in node[-1]:
        #     line_info = f" (Line approx. {node[-1]['lineno']})"

        full_message = f"Type Error{line_info}: {message}"
        self.errors.append(full_message)
        print(full_message) # Also print to console

    def save_errors_to_file(self):
        """Saves collected type errors to the specified error file."""
        if not self.errors:
            print("No type errors to save.")
            return

        try:
            with open(self.error_file_path, 'a', encoding='utf-8') as f: # Append mode
                f.write("--- Type Errors ---\n")
                for error in self.errors:
                    f.write(f"{error}\n")
                f.write("--- End of Type Errors ---\n\n")
            print(f"Type errors saved to {self.error_file_path}")
        except IOError as e:
            print(f"Error saving type errors to file {self.error_file_path}: {e}")

    def check_program(self, ast_node):
        """
        Starts type checking for the entire program.
        Assumes ast_node is ('program', [function_definitions_and_main])
        """
        if not (isinstance(ast_node, tuple) and ast_node[0] == 'program' and len(ast_node) > 1):
            self._log_error("Invalid AST root for type checking.", ast_node)
            return

        declarations = ast_node[1] # List of functions and main

        for decl_node in declarations:
            if decl_node[0] == 'function':
                # ('function', return_type_str, name_str, params_list_node, block_node)
                _, return_type, _, _, block_node = decl_node
                self.current_function_return_type = return_type
                # ScopeChecker handles scope entry/exit for symbol table.
                # TypeChecker uses the existing symbol table state for the function's scope.
                self._check_node(block_node)
                self.current_function_return_type = None # Reset after checking function

            elif decl_node[0] == 'main_function':
                # ('main_function', params_list_node, block_node)
                _, _, block_node = decl_node
                self.current_function_return_type = 'void' # Main implicitly returns void
                self._check_node(block_node)
                self.current_function_return_type = None

    def _check_node(self, node):
        """
        Recursively checks a node or dispatches to specific handlers.
        This method primarily handles statements. Expressions are handled by `_infer_expression_type`.
        """
        if node is None:
            return

        if isinstance(node, tuple) and node: # Ensure node is a non-empty tuple
            node_type = node[0]

            if node_type == 'block':
                # ('block', [statements_list])
                # SymbolTable handles actual scope entry/exit. TypeChecker just processes statements.
                # New scopes for blocks (if, while, for) are entered by ScopeChecker.
                # TypeChecker relies on the symbol_table reflecting the correct current scope.
                for stmt_node in node[1]:
                    self._check_node(stmt_node)

            elif node_type == 'declaration':
                # ('declaration', declared_type_str, var_name_str, init_expr_node_or_None)
                self._check_declaration(node)

            elif node_type == 'assignment':
                # ('assignment', var_name_str, value_expr_node)
                self._check_assignment(node)

            elif node_type == 'if':
                # ('if', condition_expr_node, then_block_node, else_block_node_or_None)
                self._check_if_statement(node)

            elif node_type == 'while':
                # ('while', condition_expr_node, block_node)
                self._check_while_statement(node)

            elif node_type == 'for':
                # ('for', init_node, condition_expr_node, update_node, block_node)
                self._check_for_statement(node)

            elif node_type == 'return':
                # ('return', expr_node_or_None)
                self._check_return_statement(node)

            elif node_type == 'print':
                # ('print', expr_node)
                self._check_print_statement(node)

            elif node_type == 'call':
                # Function call used as a statement. Infer type to check arguments.
                self._infer_expression_type(node)

            # Other node types (expressions) are typically handled by _infer_expression_type
            # when they appear as part of statements.

        elif isinstance(node, list): # Should ideally not be common if AST is well-structured
            for item in node:
                self._check_node(item)

    def _check_declaration(self, decl_node):
        # ('declaration', declared_type_str, var_name_str, init_expr_node_or_None)
        _, declared_type, var_name, init_expr = decl_node

        if init_expr is not None:
            value_type = self._infer_expression_type(init_expr)
            if value_type != 'error_type': # Proceed only if initializer type is valid
                if not self._is_assignable(declared_type, value_type):
                    self._log_error(f"Cannot assign initial value of type '{value_type}' to variable '{var_name}' of type '{declared_type}'.", decl_node)

    def _check_assignment(self, assign_node):
        # ('assignment', var_name_str, value_expr_node)
        _, var_name, value_expr = assign_node

        var_info = self.symbol_table.lookup_variable(var_name)
        if not var_info:
            # This error should ideally be caught by ScopeChecker.
            # Logging here as a safeguard or if ScopeChecker issues don't halt compilation.
            self._log_error(f"Variable '{var_name}' not declared (assignment check).", assign_node)
            return

        declared_type = var_info['type']
        value_type = self._infer_expression_type(value_expr)

        if value_type != 'error_type':
            if not self._is_assignable(declared_type, value_type):
                self._log_error(f"Cannot assign value of type '{value_type}' to variable '{var_name}' of type '{declared_type}'.", assign_node)

    def _check_if_statement(self, if_node):
        # ('if', condition_expr, then_block_node, else_block_node_or_None)
        _, condition_expr, then_block, else_block = if_node

        condition_type = self._infer_expression_type(condition_expr)
        if condition_type != 'bool' and condition_type != 'error_type':
            self._log_error(f"If statement condition must be boolean, got '{condition_type}'.", condition_expr)

        self._check_node(then_block)
        if else_block is not None:
            self._check_node(else_block)

    def _check_while_statement(self, while_node):
        # ('while', condition_expr, block_node)
        _, condition_expr, block = while_node

        condition_type = self._infer_expression_type(condition_expr)
        if condition_type != 'bool' and condition_type != 'error_type':
            self._log_error(f"While loop condition must be boolean, got '{condition_type}'.", condition_expr)

        self._check_node(block)

    def _check_for_statement(self, for_node):
        # ('for', init_node, condition_expr_node, update_node, block_node)
        _, init_node, condition_expr, update_node, block = for_node

        if init_node: self._check_node(init_node) # init_node can be declaration or assignment

        condition_type = self._infer_expression_type(condition_expr)
        if condition_type != 'bool' and condition_type != 'error_type':
             self._log_error(f"For loop condition must be boolean, got '{condition_type}'.", condition_expr)

        if update_node: self._check_node(update_node) # update_node is usually assignment

        self._check_node(block)

    def _check_return_statement(self, return_node):
        # ('return', expr_node_or_None)
        _, expr_node = return_node

        if self.current_function_return_type is None:
            self._log_error("Return statement found outside of a function context.", return_node)
            return

        actual_return_type = 'void'
        if expr_node is not None:
            actual_return_type = self._infer_expression_type(expr_node)

        if actual_return_type == 'error_type': # Error already logged by _infer_expression_type
            return

        expected_return_type = self.current_function_return_type

        if expected_return_type == 'void':
            if actual_return_type != 'void':
                self._log_error(f"Function '{self.symbol_table.lookup_function(self.current_function_name) if hasattr(self, 'current_function_name') else 'current function'}' with 'void' return type cannot return a value of type '{actual_return_type}'.", return_node)
        elif not self._is_assignable(expected_return_type, actual_return_type):
            self._log_error(f"Return type mismatch: Expected '{expected_return_type}', got '{actual_return_type}'.", return_node)

    def _check_print_statement(self, print_node):
        # ('print', expr_node)
        _, expr_node = print_node
        expr_type = self._infer_expression_type(expr_node)

        if expr_type == 'error_type':
            return # Error already logged
        if expr_type == 'void':
             self._log_error(f"Cannot print expression of type 'void'.", print_node)
        # Allow printing of int, float, string, bool

    def _infer_binary_op_type(self, op_name_node, left_type, right_type):
        # op_name_node is the AST node for the operator itself, e.g., ('plus', left_expr, right_expr)
        # op is the string like 'plus', 'eq'
        op = op_name_node[0]

        # Arithmetic Operations
        if op in ('plus', 'minus', 'times', 'divide', 'mod'):
            if op == 'plus': # Special case for string concatenation
                if left_type == 'string' and right_type == 'string': return 'string'

            if left_type == 'int' and right_type == 'int': return 'int'
            if (left_type == 'float' or left_type == 'int') and \
               (right_type == 'float' or right_type == 'int'):
                return 'float' # Promote to float if either is float
            self._log_error(f"Operator '{op}' undefined for types '{left_type}' and '{right_type}'.", op_name_node)
            return 'error_type'

        # Comparison Operations -> bool
        elif op in ('eq', 'ne', 'lt', 'gt', 'le', 'ge'):
            # Allow comparison between compatible types (e.g., int/float, string/string)
            if (left_type in ('int', 'float') and right_type in ('int', 'float')) or \
               (left_type == 'string' and right_type == 'string') or \
               (left_type == 'bool' and right_type == 'bool'):
                return 'bool'
            self._log_error(f"Cannot compare types '{left_type}' and '{right_type}' with operator '{op}'.", op_name_node)
            return 'error_type'

        # Logical Operations -> bool (require bool operands)
        elif op in ('and', 'or'):
            if left_type == 'bool' and right_type == 'bool':
                return 'bool'
            self._log_error(f"Logical operator '{op}' requires boolean operands, got '{left_type}' and '{right_type}'.", op_name_node)
            return 'error_type'

        else: # Should not happen if parser is correct
            self._log_error(f"Unknown binary operator '{op}'.", op_name_node)
            return 'error_type'

    def _infer_unary_op_type(self, op_name_node, operand_type):
        # op_name_node is the AST node for the operator, e.g., ('not', operand_expr)
        op = op_name_node[0]

        if op == 'not':
            if operand_type == 'bool': return 'bool'
            self._log_error(f"Operator 'not' undefined for type '{operand_type}'.", op_name_node)
            return 'error_type'
        elif op == 'unary_minus': # Example, if you add unary minus
            if operand_type == 'int': return 'int'
            if operand_type == 'float': return 'float'
            self._log_error(f"Operator 'unary_minus' undefined for type '{operand_type}'.", op_name_node)
            return 'error_type'

        self._log_error(f"Unknown unary operator '{op}'.", op_name_node)
        return 'error_type'


    def _infer_expression_type(self, expr_node):
        """
        Infers the type of an expression node.
        Returns the type as a string (e.g., 'int', 'float', 'bool', 'string', 'void', 'error_type').
        """
        if expr_node is None: # E.g. empty return statement in some AST representations
            return 'void'
        if not isinstance(expr_node, tuple) or not expr_node:
            self._log_error(f"Invalid expression node structure: {expr_node}", expr_node)
            return 'error_type'

        node_type_category = expr_node[0]

        if node_type_category == 'number': # ('number', value)
            val = expr_node[1]
            if isinstance(val, int): return 'int'
            if isinstance(val, float): return 'float'
            self._log_error(f"Unknown number literal type: {val}", expr_node)
            return 'error_type'

        elif node_type_category == 'string': # ('string', value)
            return 'string'

        elif node_type_category == 'bool': # ('bool', True/False)
            return 'bool'

        elif node_type_category == 'id': # ('id', var_name_str)
            var_name = expr_node[1]
            var_info = self.symbol_table.lookup_variable(var_name)
            if var_info:
                return var_info['type']
            self._log_error(f"Variable '{var_name}' not declared (type inference).", expr_node)
            return 'error_type'

        elif node_type_category == 'call':
            # ('call', func_name_str, args_list_node)
            # args_list_node is ('args', [arg_expr_node, ...]) or None
            _, func_name, args_list_node = expr_node
            func_info = self.symbol_table.lookup_function(func_name)

            if not func_info:
                self._log_error(f"Function '{func_name}' not defined (type inference).", expr_node)
                return 'error_type'

            expected_param_types = [p[0] for p in func_info['params']] # p is (type, name)
            actual_arg_exprs = args_list_node[1] if args_list_node and args_list_node[0] == 'args' else []

            if len(expected_param_types) != len(actual_arg_exprs):
                self._log_error(f"Function '{func_name}' expects {len(expected_param_types)} arguments, got {len(actual_arg_exprs)}.", expr_node)
                return 'error_type' # Halt further arg checks for this call

            for i, arg_expr in enumerate(actual_arg_exprs):
                arg_type = self._infer_expression_type(arg_expr)
                if arg_type == 'error_type': return 'error_type' # Error in arg, propagate

                expected_param_type = expected_param_types[i]
                if not self._is_assignable(expected_param_type, arg_type):
                    self._log_error(f"Type mismatch for argument {i+1} of function '{func_name}': Expected '{expected_param_type}', got '{arg_type}'.", arg_expr)
                    return 'error_type'

            return func_info['return_type']

        # Binary operators
        elif node_type_category in ('plus', 'minus', 'times', 'divide', 'mod',
                                    'or', 'and',
                                    'eq', 'ne', 'lt', 'gt', 'le', 'ge'):
            # ('op_name', left_expr, right_expr)
            left_expr = expr_node[1]
            right_expr = expr_node[2]

            left_type = self._infer_expression_type(left_expr)
            if left_type == 'error_type': return 'error_type'

            right_type = self._infer_expression_type(right_expr)
            if right_type == 'error_type': return 'error_type'

            return self._infer_binary_op_type(expr_node, left_type, right_type)

        # Unary operators (example)
        elif node_type_category in ('not', 'unary_minus'):
            # ('op_name', operand_expr)
            operand_expr = expr_node[1]
            operand_type = self._infer_expression_type(operand_expr)
            if operand_type == 'error_type': return 'error_type'
            return self._infer_unary_op_type(expr_node, operand_type)

        else:
            self._log_error(f"Cannot infer type for unhandled expression node: {expr_node[0]}", expr_node)
            return 'error_type'

    def _is_assignable(self, var_type: str, value_type: str) -> bool:
        """
        Checks if a value of `value_type` can be assigned to a variable of `var_type`.
        Implements type compatibility rules (e.g., int to float is okay).
        """
        if var_type == value_type:
            return True
        if var_type == 'float' and value_type == 'int': # Implicit conversion: int to float
            return True
        # Add other promotion/conversion rules if any (e.g. float to int with truncation if allowed)
        # For now, strict assignment or int to float.

        # Prevent cascading errors if a type is already 'error_type'
        if var_type == 'error_type' or value_type == 'error_type':
            return True # Assume error was logged where 'error_type' originated

        return False

    def get_errors(self) -> list:
        """Returns the list of collected type errors."""
        return self.errors

# The __main__ block from the original TypeChecker.py has been removed.
# Testing should be done via a dedicated test script (e.g., in PROYECTO/tests/)
# or through the main compiler pipeline (new main.py).
