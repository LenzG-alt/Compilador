from Parser import parser, lexer
from ASTBuilder import ASTBuilder
from ScopeChecker import ScopeChecker

def test_scope_checker():
    # Ejemplo 1: Programa válido
    code1 = """
    int suma(int a, int b) {
        int resultado = a + b;
        return resultado;
    }
    
    void main() {
        int x = 5;
        int y = 10;
        int z = suma(x, y);
        print(z);
    }
    """
    
    # Ejemplo 2: Programa con errores de ámbito
    code2 = """
    void main() {
        int x = 5;
        {
            int y = x + 2;
            print(y);
        }
        print(y);
    }
    """
    
    # Ejemplo 3: Programa con redeclaración
    code3 = """
    void main() {
        int x = 5;
        int x = 10;
    }
    """
    
    # Ejemplo 4: Programa con función no definida
    code4 = """
    void main() {
        calcular();
    }
    """
    
    examples = [
        ("1. Programa válido", code1, False),
        ("2. Error de ámbito", code2, True),
        ("3. Redeclaración", code3, True),
        ("4. Función no definida", code4, True)
    ]
    
    print("=== PRUEBAS DE VERIFICACIÓN DE ÁMBITO ===")
    for name, code, expect_error in examples:
        print(f"\n{name}")
        print("Código:")
        print(code.strip())
        
        # Construir AST
        builder = ASTBuilder()
        ast = builder.build_ast(code)
        
        if ast is None:
            print("\n❌ No se pudo construir el AST debido a errores sintácticos")
            continue
        
        # Verificar ámbito
        checker = ScopeChecker()
        try:
            checker.check_program(ast)
            if expect_error:
                print("\n❌ Prueba falló: Se esperaba un error pero no se encontró")
            else:
                print("\n✅ Prueba exitosa: Programa válido")
        except ValueError as e:
            if expect_error:
                print(f"\n✅ Prueba exitosa: Error detectado correctamente")
            else:
                print(f"\n❌ Prueba falló: Error inesperado")
            print(f"  Mensaje de error: {str(e)}")

if __name__ == "__main__":
    test_scope_checker()