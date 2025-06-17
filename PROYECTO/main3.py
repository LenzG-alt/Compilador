import sys
from ASTBuilder import build_and_visualize_ast

def main():
    if len(sys.argv) > 1:
        # Leer archivo de entrada
        with open(sys.argv[1], 'r') as f:
            input_code = f.read()
    else:
        # Ejemplo de código de prueba
        input_code = """
        main() {
            int x = 5;
            if (x > 0) {
                print("Positivo");
            } else {
                print("Negativo");
            }
            return 0;
        }
        """
    
    print("Analizando código...\n")
    
    try:
        # Construir y visualizar el AST
        ast, trace = build_and_visualize_ast(input_code)
        
        print("\nAnálisis completado. Resultados guardados en:")
        print("- salida/ast.txt")
        print("- salida/parse_trace.txt")
    except Exception as e:
        print(f"\nError durante el análisis: {str(e)}")

if __name__ == "__main__":
    main()