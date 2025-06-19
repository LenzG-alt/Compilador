import os

class SymbolTable:
    """
    Manages symbols (variables and functions) and their scopes.
    """
    def __init__(self):
        self.global_scope = {}
        self.scope_stack = [self.global_scope]
        self.functions = {}
        # Scope history might be useful for debugging, but can be verbose.
        # Consider making its population optional or removing if not essential.
        self.scope_history = []

    def enter_scope(self):
        """Enters a new, nested scope."""
        new_scope = {}
        self.scope_stack.append(new_scope)
        self._record_scope_state("Enter Scope")

    def exit_scope(self):
        """Exits the current scope, returning to the parent scope."""
        if len(self.scope_stack) > 1:
            self._record_scope_state("Exit Scope")
            self.scope_stack.pop()
        else:
            # Cannot exit global scope; this might indicate a logic error if called.
            print("Warning: Attempted to exit global scope.")

    @property
    def current_scope(self):
        """Returns the currently active scope dictionary."""
        return self.scope_stack[-1]

    def _record_scope_state(self, action: str):
        """Records the current state of scopes and functions for history/debugging."""
        # This can be performance-intensive if scopes are large or history is long.
        # For production, this might be disabled or optimized.
        state = {
            'action': action,
            'scopes': [dict(scope) for scope in self.scope_stack], # Deep copy for history
            'functions': dict(self.functions) # Deep copy
        }
        self.scope_history.append(state)

    def add_variable(self, name: str, var_type: str, value=None) -> bool:
        """
        Adds a variable to the current scope.

        Args:
            name (str): The name of the variable.
            var_type (str): The type of the variable.
            value: The initial value of the variable (optional).

        Returns:
            bool: True if added successfully, False if already declared in the current scope.
        """
        if name in self.current_scope:
            return False # Indicate error: variable already declared in this scope

        self.current_scope[name] = {
            'type': var_type,
            'value': value,
            'scope_level': len(self.scope_stack) -1 # 0 for global, 1+ for local
        }
        self._record_scope_state(f"Declare Variable '{name}' ({var_type})")
        return True

    def add_function(self, name: str, params: list = None, return_type: str = 'void') -> bool:
        """
        Adds a function to the global function registry.

        Args:
            name (str): The name of the function.
            params (list): A list of tuples, where each tuple is (param_type, param_name).
            return_type (str): The return type of the function.

        Returns:
            bool: True if added successfully, False if already declared.
        """
        if name in self.functions:
            return False # Indicate error: function already declared

        self.functions[name] = {
            'params': params or [],
            'return_type': return_type,
            'scope': 'global' # Functions are typically global in simple languages
        }
        self._record_scope_state(f"Declare Function '{name}'")
        return True
        
    def lookup_variable(self, name: str):
        """
        Looks up a variable in the current and enclosing scopes.

        Args:
            name (str): The name of the variable to look up.

        Returns:
            dict: The variable's information if found, otherwise None.
        """
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
    
    def lookup_function(self, name: str):
        """
        Looks up a function in the global function registry.

        Args:
            name (str): The name of the function.

        Returns:
            dict: The function's information if found, otherwise None.
        """
        return self.functions.get(name)

    def get_symbol_table_report(self) -> str:
        """Generates a string report of the current symbol table state."""
        report_lines = ["--- Symbol Table Report ---"]

        report_lines.append("\n[Functions]")
        if self.functions:
            for name, info in self.functions.items():
                param_details = ", ".join([f"{p_name}: {p_type}" for p_type, p_name in info['params']])
                report_lines.append(f"  Function: {name}({param_details}) -> {info['return_type']}")
        else:
            report_lines.append("  (No functions defined)")

        report_lines.append("\n[Scopes & Variables]")
        for i, scope in enumerate(self.scope_stack):
            scope_type = "Global" if i == 0 else f"Local (Depth {i})"
            report_lines.append(f"  Scope: {scope_type}")
            if scope:
                for name, info in scope.items():
                    report_lines.append(f"    Var: {name}, Type: {info['type']}, Value: {info.get('value', 'N/A')}, Level: {info.get('scope_level', 'N/A')}")
            else:
                report_lines.append("    (No variables in this scope)")
        
        report_lines.append("--- End of Symbol Table Report ---")
        return "\n".join(report_lines)

    def get_scope_history_report(self) -> str:
        """Generates a string report of the scope history (for debugging)."""
        report_lines = ["--- Scope History Report ---"]
        if not self.scope_history:
            report_lines.append("  (No history recorded)")
        
        for i, state in enumerate(self.scope_history, 1):
            report_lines.append(f"\nStep {i}: {state['action']}")
            # Optionally, print details of scopes/functions at each step
            # This can be very verbose, so keeping it minimal here.
            # report_lines.append(f"  Current Scopes: {len(state['scopes'])}")
            # report_lines.append(f"  Current Functions: {list(state['functions'].keys())}")

        report_lines.append("--- End of Scope History Report ---")
        return "\n".join(report_lines)


class ScopeChecker:
    """
    Performs scope checking on an AST using a SymbolTable.
    """
    def __init__(self, output_dir='salida', error_filename="errores_ambito.txt"):
        """
        Initializes the ScopeChecker.

        Args:
            output_dir (str): Directory to save error logs.
            error_filename (str): Name of the file for scope errors.
        """
        self.symbol_table = SymbolTable()
        self.errors = []
        self.output_dir = output_dir
        self.error_file_path = os.path.join(output_dir, error_filename)
        os.makedirs(self.output_dir, exist_ok=True)
        # Clear previous errors at the start of a new check
        with open(self.error_file_path, 'w', encoding='utf-8') as f:
            f.write("") # Create or truncate the file

    def _log_error(self, message: str, node=None):
        """
        Logs a scope error. Includes line number if node information is available.
        
        Args:
            message (str): The error message.
            node: The AST node associated with the error (optional, for line numbers).
        """
        # Attempt to get line number if node is structured like ('type', ..., {'lineno': X})
        # This depends on how parser/ASTBuilder structures nodes with metadata.
        # For now, assume node might not have line info directly accessible this way.
        # A more robust solution would be to ensure nodes carry line info.
        line_info = ""
        if node and isinstance(node, tuple) and len(node) > 0: # Basic check
            # This is a placeholder: actual line number extraction needs AST node structure knowledge
            # E.g., if nodes are like ('type', val, metadata_dict)
            # if len(node) > 2 and isinstance(node[-1], dict) and 'lineno' in node[-1]:
            #     line_info = f" (Line approx. {node[-1]['lineno']})"
            pass # No standard line number info assumed for now

        full_message = f"Scope Error{line_info}: {message}"
        self.errors.append(full_message)
        print(full_message) # Also print to console for immediate feedback

    def save_errors_to_file(self):
        """Saves collected scope errors to the specified error file."""
        if not self.errors:
            print("No scope errors to save.")
            return

        try:
            with open(self.error_file_path, 'a', encoding='utf-8') as f: # Append mode
                f.write("--- Scope Errors ---\n")
                for error in self.errors:
                    f.write(f"{error}\n")
                f.write("--- End of Scope Errors ---\n\n")
            print(f"Scope errors saved to {self.error_file_path}")
        except IOError as e:
            print(f"Error saving scope errors to file {self.error_file_path}: {e}")

    def check_program(self, ast_node):
        """
        Starts scope checking for the entire program.
        Assumes ast_node is ('program', [function_definitions_and_main])
        """
        if not (isinstance(ast_node, tuple) and ast_node[0] == 'program' and len(ast_node) > 1):
            self._log_error("Invalid AST root: Expected ('program', [declarations]).", ast_node)
            return

        declarations = ast_node[1] # List of functions and main

        # First pass: Register all function signatures globally
        for decl in declarations:
            if decl[0] == 'function': # ('function', type_str, name_str, params_list, block_node)
                _, return_type, name, params_list_node, _ = decl
                # Transform params_list: [('param', p_type, p_name), ...] to [(p_type, p_name), ...]
                extracted_params = [(param_node[1], param_node[2]) for param_node in params_list_node[1]] if params_list_node[0] == 'params' else [] # Adjusted for ('params', [...])
                if not self.symbol_table.add_function(name, extracted_params, return_type):
                    self._log_error(f"Function '{name}' already declared.", decl)
            elif decl[0] == 'main_function': # ('main_function', params_list, block_node)
                _, params_list_node, _ = decl
                extracted_params = [(param_node[1], param_node[2]) for param_node in params_list_node[1]] if params_list_node[0] == 'params' else [] # Adjusted
                if not self.symbol_table.add_function('main', extracted_params, 'void'):
                    self._log_error("Main function 'main' already declared (should not happen if grammar is correct).", decl)
        
        # Second pass: Check function bodies and main
        for decl in declarations:
            if decl[0] == 'function':
                self._check_function_definition(decl)
            elif decl[0] == 'main_function':
                self._check_main_function_definition(decl)

        # Optionally, print reports after checking
        # print("\n" + self.symbol_table.get_symbol_table_report())
        # print("\n" + self.symbol_table.get_scope_history_report())


    def _check_function_definition(self, func_node):
        """Checks a function definition: ('function', type, name, params, block)."""
        # func_node: ('function', type_str, name_str, params_list_node, block_node)
        # params_list_node: ('params', [('param', p_type, p_name), ...])
        _, _, _, params_list_node, block_node = func_node
        
        self.symbol_table.enter_scope()

        # Add parameters to the new local scope
        if params_list_node and params_list_node[0] == 'params':
            for param_decl_node in params_list_node[1]: # param_decl_node is ('param', p_type, p_name)
                _, p_type, p_name = param_decl_node
                if not self.symbol_table.add_variable(p_name, p_type):
                    self._log_error(f"Parameter '{p_name}' redeclared in function scope.", param_decl_node)

        self._check_block(block_node)
        self.symbol_table.exit_scope()

    def _check_main_function_definition(self, main_func_node):
        """Checks the main function definition: ('main_function', params, block)."""
        # main_func_node: ('main_function', params_list_node, block_node)
        _, params_list_node, block_node = main_func_node

        self.symbol_table.enter_scope()
        if params_list_node and params_list_node[0] == 'params':
            for param_decl_node in params_list_node[1]:
                _, p_type, p_name = param_decl_node
                if not self.symbol_table.add_variable(p_name, p_type):
                    self._log_error(f"Parameter '{p_name}' redeclared in main function scope.", param_decl_node)

        self._check_block(block_node)
        self.symbol_table.exit_scope()

    def _check_block(self, block_node):
        """Checks a block of statements: ('block', [statements_list])."""
        if not (block_node and block_node[0] == 'block'):
            self._log_error("Invalid block structure.", block_node)
            return

        # A block itself does not create a new scope unless it's a function body
        # or a specific block scope construct (if language supports general block scopes).
        # For if/while/for, new scopes are typically created for their bodies.
        
        statements = block_node[1]
        for stmt_node in statements:
            self._check_statement(stmt_node)

    def _check_statement(self, stmt_node):
        """Dispatches to specific statement checking methods."""
        if not isinstance(stmt_node, tuple) or not stmt_node:
            # self._log_error(f"Invalid statement structure: {stmt_node}", stmt_node)
            return # Could be an empty statement or malformed

        stmt_type = stmt_node[0]

        if stmt_type == 'declaration':
            # ('declaration', type_str, name_str, init_expr_node_or_None)
            _, var_type, name, init_expr = stmt_node
            if not self.symbol_table.add_variable(name, var_type): # Value from init_expr not stored in ST here
                self._log_error(f"Variable '{name}' already declared in this scope.", stmt_node)
            if init_expr:
                self._check_expression(init_expr)
        
        elif stmt_type == 'assignment':
            # ('assignment', name_str, expr_node)
            _, name, expr_node = stmt_node
            if self.symbol_table.lookup_variable(name) is None:
                self._log_error(f"Variable '{name}' not declared before assignment.", stmt_node)
            self._check_expression(expr_node)

        elif stmt_type == 'if':
            # ('if', condition_expr_node, then_block_node, else_block_node_or_None)
            _, condition_expr, then_block, else_block = stmt_node
            self._check_expression(condition_expr)

            self.symbol_table.enter_scope()
            self._check_block(then_block)
            self.symbol_table.exit_scope()

            if else_block:
                self.symbol_table.enter_scope()
                self._check_block(else_block)
                self.symbol_table.exit_scope()

        elif stmt_type == 'while':
            # ('while', condition_expr_node, block_node)
            _, condition_expr, block = stmt_node
            self._check_expression(condition_expr)

            self.symbol_table.enter_scope()
            self._check_block(block)
            self.symbol_table.exit_scope()

        elif stmt_type == 'for':
            # ('for', init_assign_node, condition_expr_node, update_assign_node, block_node)
            _, init_node, condition_expr, update_node, block = stmt_node

            self.symbol_table.enter_scope()
            if init_node: self._check_statement(init_node) # Could be declaration or assignment
            self._check_expression(condition_expr)
            if update_node: self._check_statement(update_node) # Usually assignment
            self._check_block(block)
            self.symbol_table.exit_scope()

        elif stmt_type == 'return':
            # ('return', expr_node_or_None)
            _, expr_node = stmt_node
            if expr_node:
                self._check_expression(expr_node)

        elif stmt_type == 'print':
            # ('print', expr_node)
            _, expr_node = stmt_node
            self._check_expression(expr_node)

        elif stmt_type == 'call': # Function call as a statement
            # ('call', func_name_str, args_list_node)
            # args_list_node is ('args', [arg_expr_node, ...]) or None
            _, func_name, args_list_node = stmt_node
            func_info = self.symbol_table.lookup_function(func_name)
            if func_info is None:
                self._log_error(f"Function '{func_name}' not defined.", stmt_node)

            actual_arg_count = len(args_list_node[1]) if args_list_node and args_list_node[0] == 'args' else 0
            if func_info and len(func_info['params']) != actual_arg_count:
                expected_count = len(func_info['params'])
                self._log_error(f"Function '{func_name}' expects {expected_count} arguments, got {actual_arg_count}.", stmt_node)

            if args_list_node and args_list_node[0] == 'args':
                for arg_expr_node in args_list_node[1]:
                    self._check_expression(arg_expr_node)
        # Add other statement types if any (e.g., break, continue)

    def _check_expression(self, expr_node):
        """Checks an expression node for used identifiers and function calls."""
        if not isinstance(expr_node, tuple) or not expr_node:
            return # Literal (number, string, bool) or malformed

        expr_type = expr_node[0]

        if expr_type == 'id':
            # ('id', name_str)
            var_name = expr_node[1]
            if self.symbol_table.lookup_variable(var_name) is None:
                self._log_error(f"Variable '{var_name}' not declared before use.", expr_node)
        
        elif expr_type == 'call':
            # ('call', func_name_str, args_list_node)
            _, func_name, args_list_node = expr_node
            func_info = self.symbol_table.lookup_function(func_name)
            if func_info is None:
                self._log_error(f"Function '{func_name}' not defined.", expr_node)

            actual_arg_count = len(args_list_node[1]) if args_list_node and args_list_node[0] == 'args' else 0
            if func_info and len(func_info['params']) != actual_arg_count:
                expected_count = len(func_info['params'])
                self._log_error(f"Function '{func_name}' expects {expected_count} arguments, got {actual_arg_count}.", expr_node)

            if args_list_node and args_list_node[0] == 'args':
                for arg_expr_node in args_list_node[1]:
                    self._check_expression(arg_expr_node) # Recursively check argument expressions

        # For binary/unary operators, recursively check operands
        elif expr_type in ('plus', 'minus', 'times', 'divide', 'mod',
                           'or', 'and',
                           'eq', 'ne', 'lt', 'gt', 'le', 'ge'):
            # ('op', left_expr, right_expr)
            if len(expr_node) > 1: self._check_expression(expr_node[1])
            if len(expr_node) > 2: self._check_expression(expr_node[2])
        
        elif expr_type in ('not', 'unary_minus'): # Example unary ops
             # ('op', expr)
            if len(expr_node) > 1: self._check_expression(expr_node[1])

        # Literals ('number', val), ('string', val), ('bool', val) don't need scope checking here.
        # ('params', ...) and ('args', ...) are part of other structures, handled there.
