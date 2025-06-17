class SymbolTable:
    def __init__(self):
        self.global_scope = {}
        self.current_scope = self.global_scope
        self.scope_stack = [self.global_scope]
        self.functions = {}
        self.scope_history = []
    
    def enter_scope(self):
        new_scope = {}
        self.current_scope = new_scope
        self.scope_stack.append(new_scope)
        self._record_scope_state("Entrar ámbito")
    
    def exit_scope(self):
        if len(self.scope_stack) > 1:
            self._record_scope_state("Salir ámbito")
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
    
    def _record_scope_state(self, action):
        state = {
            'action': action,
            'scopes': [dict(scope) for scope in self.scope_stack],
            'functions': dict(self.functions)
        }
        self.scope_history.append(state)
    
    def add_variable(self, name, var_type=None, value=None):
        if name in self.current_scope:
            raise ValueError(f"Error: Ya existe una variable llamada '{name}' en este ámbito")
        self.current_scope[name] = {
            'type': var_type,
            'value': value,
            'scope': 'local' if len(self.scope_stack) > 1 else 'global'
        }
        self._record_scope_state(f"Declarar variable '{name}'")
    
    def add_function(self, name, params=None, return_type=None):
        if name in self.functions:
            raise ValueError(f"Error: Ya existe una función llamada '{name}'")
        self.functions[name] = {
            'params': params or [],
            'return_type': return_type,
            'scope': 'global'
        }
        self._record_scope_state(f"Declarar función '{name}'")

        
    def lookup_variable(self, name):
        """Busca una variable en los ámbitos actuales"""
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
    
    def lookup_function(self, name):
        """Busca una función en la tabla de símbolos"""
        return self.functions.get(name)
    
    def check_variable_usage(self, name):
        """Verifica si una variable está declarada y accesible"""
        var_info = self.lookup_variable(name)
        if var_info is None:
            raise ValueError(f"Error: La variable '{name}' no está declarada en este ámbito")
        return var_info
    
    def check_function_call(self, name, args_count):
        """Verifica si una función está definida y los argumentos son correctos"""
        func_info = self.lookup_function(name)
        if func_info is None:
            raise ValueError(f"Error: La función '{name}()' no ha sido definida")
        
        if len(func_info['params']) != args_count:
            raise ValueError(f"Error: La función '{name}()' espera {len(func_info['params'])} argumentos, pero se proporcionaron {args_count}")
    
    def get_symbol_table_report(self):
        """Genera un reporte completo de la tabla de símbolos"""
        report = []
        
        # Variables globales
        global_vars = []
        for name, info in self.global_scope.items():
            global_vars.append(f"{name} (tipo: {info['type']}, valor: {info.get('value', 'N/A')})")
        
        # Funciones
        functions = []
        for name, info in self.functions.items():
            params = ", ".join([f"{p[0]} {p[1]}" for p in info['params']])
            functions.append(f"{name} (retorna: {info['return_type']}, parámetros: {params})")
        
        # Ámbito actual
        current_scope_vars = []
        for name, info in self.current_scope.items():
            if name not in self.global_scope:  # Para no duplicar globales
                current_scope_vars.append(f"{name} (tipo: {info['type']}, valor: {info.get('value', 'N/A')})")
        
        report.append("=== TABLA DE SÍMBOLOS ===")
        report.append("\nVariables globales:")
        report.extend(global_vars if global_vars else ["(ninguna)"])
        
        report.append("\nFunciones definidas:")
        report.extend(functions if functions else ["(ninguna)"])
        
        report.append("\nVariables en ámbito actual:")
        report.extend(current_scope_vars if current_scope_vars else ["(ninguna)"])
        
        return "\n".join(report)
    
    def get_scope_history_report(self):
        """Genera un reporte del historial de cambios en los ámbitos"""
        report = ["=== HISTORIAL DE ÁMBITOS ==="]
        
        for i, state in enumerate(self.scope_history, 1):
            report.append(f"\nPaso {i}: {state['action']}")
            
            for j, scope in enumerate(state['scopes']):
                scope_name = "Global" if j == 0 else f"Local {j}"
                vars_in_scope = [f"{name} (tipo: {info['type']})" for name, info in scope.items()]
                
                if vars_in_scope:
                    report.append(f"  {scope_name}: {', '.join(vars_in_scope)}")
                else:
                    report.append(f"  {scope_name}: (vacío)")
            
            if state['functions']:
                report.append("  Funciones: " + ", ".join(state['functions'].keys()))
        
        return "\n".join(report)

class ScopeChecker:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
    
    def check_program(self, ast):
        if ast[0] != 'program':
            raise ValueError("AST no válido: debe comenzar con 'program'")
        
        # Primero registrar todas las funciones
        for func_node in ast[1]: # ast[1] is the list of functions
            if func_node[0] == 'function': # ('function', type_str, name_str, params_list, block_node)
                _, return_type, name, params_list, _ = func_node # block_node not needed for registration
                # Transform params_list: [('param', p_type, p_name), ...] to [(p_type, p_name), ...]
                extracted_params = [(param_node[1], param_node[2]) for param_node in params_list]
                self.symbol_table.add_function(name, extracted_params, return_type)
            elif func_node[0] == 'main_function': # ('main_function', params_list, block_node)
                _, params_list, _ = func_node # block_node not needed for registration
                extracted_params = [(param_node[1], param_node[2]) for param_node in params_list] # Assuming params_list structure is same
                self.symbol_table.add_function('main', extracted_params, 'void') # Main implicitly void

        # Luego verificar los cuerpos de las funciones
        for func_node in ast[1]: # Iterate again to check bodies in new scopes
            if func_node[0] == 'function':
                self.check_function(func_node)
            elif func_node[0] == 'main_function':
                self.check_main_function(func_node)
        
        print("\n" + self.symbol_table.get_symbol_table_report())
        print("\n" + self.symbol_table.get_scope_history_report())
    
    # check_functions method is removed as its logic is merged into check_program's second loop.

    def check_function(self, func_node): # Receives ('function', type_str, name_str, params_list, block_node)
        _, return_type, name, params_list, block_node = func_node
        
        self.symbol_table.enter_scope()

        # Añadir parámetros como variables locales
        # params_list is [('param', p_type, p_name), ...]
        for param_node in params_list:
            # param_node is ('param', p_type, p_name)
            self.symbol_table.add_variable(param_node[2], param_node[1]) # name, type

        # block_node is ('block', [statements])
        self.check_block(block_node[1])
        self.symbol_table.exit_scope()
    
    def check_main_function(self, func_node): # Receives ('main_function', params_list, block_node)
        """Verifica la función main"""
        _, params_list, block_node = func_node

        self.symbol_table.enter_scope()

        # params_list is [('param', p_type, p_name), ...]
        for param_node in params_list:
             # param_node is ('param', p_type, p_name)
            self.symbol_table.add_variable(param_node[2], param_node[1]) # name, type

        # block_node is ('block', [statements])
        self.check_block(block_node[1])
        self.symbol_table.exit_scope()
    
    def check_block(self, statements):
        """Verifica un bloque de instrucciones"""
        for stmt in statements:
            self.check_statement(stmt)
    
    def check_statement(self, stmt):
        """Verifica una instrucción individual"""
        if isinstance(stmt, tuple):
            stmt_type = stmt[0]
            
            if stmt_type == 'declaration':
                self.check_declaration(stmt)
            elif stmt_type == 'assignment':
                self.check_assignment(stmt)
            elif stmt_type == 'if':
                self.check_if(stmt)
            elif stmt_type == 'while':
                self.check_while(stmt)
            elif stmt_type == 'for':
                self.check_for(stmt)
            elif stmt_type == 'return':
                self.check_return(stmt)
            elif stmt_type == 'print':
                self.check_print(stmt)
            elif stmt_type == 'call':
                self.check_function_call(stmt)
    
    def check_declaration(self, decl):
        """Verifica una declaración de variable"""
        _, var_type, name, init_value = decl
        self.symbol_table.add_variable(name, var_type)
        
        if init_value is not None:
            self.check_expression(init_value)
    
    def check_assignment(self, assign):
        """Verifica una asignación de variable"""
        _, name, expr = assign
        self.symbol_table.check_variable_usage(name)
        self.check_expression(expr)
    
    def check_if(self, if_stmt):
        """Verifica una instrucción if"""
        _, condition, then_block, else_block = if_stmt
        self.check_expression(condition)
        
        self.symbol_table.enter_scope()
        self.check_block(then_block[1])
        self.symbol_table.exit_scope()
        
        if else_block is not None:
            self.symbol_table.enter_scope()
            self.check_block(else_block[1])
            self.symbol_table.exit_scope()
    
    def check_while(self, while_stmt):
        """Verifica una instrucción while"""
        _, condition, block = while_stmt
        self.check_expression(condition)
        
        self.symbol_table.enter_scope()
        self.check_block(block[1])
        self.symbol_table.exit_scope()
    
    def check_for(self, for_stmt):
        """Verifica una instrucción for"""
        _, init, condition, update, block = for_stmt
        
        self.symbol_table.enter_scope()
        self.check_assignment(init)
        self.check_expression(condition)
        self.check_assignment(update)
        self.check_block(block[1])
        self.symbol_table.exit_scope()
    
    def check_return(self, return_stmt):
        """Verifica una instrucción return"""
        _, expr = return_stmt
        if expr is not None:
            self.check_expression(expr)
    
    def check_print(self, print_stmt):
        """Verifica una instrucción print"""
        _, expr = print_stmt
        self.check_expression(expr)
    
    def check_function_call(self, call):
        """Verifica una llamada a función"""
        _, name, args = call
        self.symbol_table.check_function_call(name, len(args))
        
        for arg in args:
            self.check_expression(arg)
    
    def check_expression(self, expr):
        """Verifica una expresión"""
        if isinstance(expr, tuple):
            if expr[0] in ('or', 'and', '==', '!=', '<', '>', '<=', '>=', '+', '-', '*', '/', '%'):
                self.check_expression(expr[1])
                self.check_expression(expr[2])
            elif expr[0] == 'call':
                self.check_function_call(expr)
            elif expr[0] == 'id':
                self.symbol_table.check_variable_usage(expr[1])
        elif isinstance(expr, list):
            for e in expr:
                self.check_expression(e)
    
    def get_errors(self):
        """Obtiene los errores encontrados"""
        return self.errors
    
    def log_error(self, message):
        """Registra un error"""
        self.errors.append(message)