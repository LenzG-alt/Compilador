class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # Lista de diccionarios, cada uno representa un ámbito
        self.errores = []   # Lista de errores semánticos

    def enter_scope(self):
        """Ingresar a un nuevo ámbito (por ejemplo, dentro de una función)."""
        self.scopes.append({})

    def exit_scope(self):
        """Salir del ámbito actual (eliminar variables locales)."""
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            self.errores.append("Error: No se puede salir del ámbito global.")

    def add_variable(self, name, tipo):
        """Agregar una variable al ámbito actual."""
        current_scope = self.scopes[-1]
        if name in current_scope:
            self.errores.append(f"Error: La variable '{name}' ya está definida en el ámbito actual.")
        else:
            current_scope[name] = tipo

    def variable_exists(self, name):
        """Verificar si una variable existe en cualquier ámbito (local o global)."""
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False

    def get_variable_type(self, name):
        """Obtener el tipo de una variable, si existe."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def log_error(self, message):
        """Registrar un error semántico personalizado."""
        self.errores.append(message)

    def export_to_txt(self, path='salida/tabla_simbolos.txt'):
        """Exportar la tabla de símbolos a un archivo de texto."""
        with open(path, 'w') as f:
            f.write("=== Tabla de Símbolos ===\n\n")
            for i, scope in enumerate(self.scopes):
                scope_name = "Global" if i == 0 else f"Local {i}"
                f.write(f"-- Ámbito: {scope_name} --\n")
                for name, tipo in scope.items():
                    f.write(f"{name} : {tipo}\n")
                f.write("\n")
            if self.errores:
                f.write("=== Errores Semánticos ===\n")
                for err in self.errores:
                    f.write(f"{err}\n")

