import os
from Parser import parser, lexer  # Asegúrate de importar lexer desde tu Parser.py


class ASTBuilder:
    def __init__(self):
        self.parse_trace = []
        self.ast = None
    
    def build_ast(self, input_code):
        """Construye el AST a partir del código de entrada"""
        try:
            self.ast = parser.parse(input_code, lexer=lexer)
            return self.ast
        except Exception as e:
            print(f"Error al construir el AST: {str(e)}")
            raise
    
    def trace_parse(self, input_code):
        """Registra el recorrido del parser al construir el AST"""
        self.parse_trace = []
        
        # Usamos una copia del lexer para el tracing
        debug_lexer = lexer.clone()
        debug_lexer.input(input_code)
        
        # Tokenización independiente
        while True:
            tok = debug_lexer.token()
            if not tok:
                break
            self.parse_trace.append({
                'type': tok.type,
                'value': tok.value,
                'lineno': tok.lineno,
                'lexpos': tok.lexpos
            })
        
        # Parse real
        self.ast = parser.parse(input_code, lexer=lexer)
        return self.parse_trace
    
    def save_ast_to_file(self, filename='salida/ast.txt'):
        """Guarda el AST en un archivo de texto"""
        os.makedirs('salida', exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            self._write_node(f, self.ast, 0)
    
    def _write_node(self, file, node, indent):
        """Función auxiliar para escribir el AST recursivamente"""
        if node is None:
            return
            
        if isinstance(node, tuple):
            file.write('  ' * indent + f"{node[0]}:\n")
            for child in node[1:]:
                self._write_node(file, child, indent + 1)
        elif isinstance(node, list):
            for child in node:
                self._write_node(file, child, indent)
        else:
            file.write('  ' * indent + str(node) + '\n')
    
    def save_trace_to_file(self, filename='salida/parse_trace.txt'):
        """Guarda el recorrido del parser en un archivo de texto"""
        os.makedirs('salida', exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            for tok in self.parse_trace:
                f.write(f"Token: {tok['type']}\n")
                f.write(f"Valor: {tok['value']}\n")
                f.write(f"Línea: {tok['lineno']}\n")
                f.write(f"Posición: {tok['lexpos']}\n")
                f.write("-" * 40 + "\n")
    
    def print_ast(self):
        """Imprime el AST de forma legible en consola"""
        if self.ast is None:
            print("No hay AST generado")
            return
        print("\nÁrbol Sintáctico Abstracto (AST):")
        self._print_node(self.ast, 0)
    
    def _print_node(self, node, indent):
        """Función auxiliar para imprimir el AST recursivamente"""
        if node is None:
            return
            
        if isinstance(node, tuple):
            print('  ' * indent + f"{node[0]}:")
            for child in node[1:]:
                self._print_node(child, indent + 1)
        elif isinstance(node, list):
            for child in node:
                self._print_node(child, indent)
        else:
            print('  ' * indent + str(node))
    
    def print_parse_trace(self):
        """Imprime el recorrido del parser en consola"""
        if not self.parse_trace:
            print("No hay registro de análisis")
            return
            
        print("\nRecorrido del Análisis Léxico:")
        for tok in self.parse_trace:
            print(f"Token: {tok['type']}")
            print(f"Valor: {tok['value']}")
            print(f"Línea: {tok['lineno']}")
            print(f"Posición: {tok['lexpos']}")
            print("-" * 40)

def build_and_visualize_ast(input_code):
    """Función conveniente para construir y visualizar el AST"""
    builder = ASTBuilder()
    
    try:
        # Construir AST
        ast = builder.build_ast(input_code)
        
        # Registrar recorrido
        trace = builder.trace_parse(input_code)
        
        # Guardar resultados
        builder.save_ast_to_file()
        builder.save_trace_to_file()
        
        # Mostrar en consola
        builder.print_ast()
        builder.print_parse_trace()
        
        return ast, trace
        
    except Exception as e:
        print(f"\nError durante el análisis: {str(e)}")
        return None, None
    
    def build_and_validate_ast(self, input_code):
        """Construye el AST y valida los ámbitos"""
        try:
            # Construir AST como antes
            self.ast = parser.parse(input_code, lexer=lexer)
            
            # Validar ámbitos
            self.scope_checker.validate_ast(self.ast)
            
            # Guardar errores si los hay
            if self.scope_checker.get_errors():
                self.scope_checker.save_errors_to_file()
                print("Se encontraron errores de ámbito. Ver 'salida/errores_ambito.txt'")
            
            return self.ast
            
        except Exception as e:
            print(f"Error al construir el AST: {str(e)}")
            raise