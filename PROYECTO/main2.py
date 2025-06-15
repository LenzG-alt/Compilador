import Lexer
import Gramatica
from graphviz import Digraph
from TreeNode import TreeNode
import os

# Crear la carpeta si no existe
output_dir = "salida"
os.makedirs(output_dir, exist_ok=True)

# === Código de prueba ===
codigo = '''
void main() {
    int x = 10;
    float y = 5.5;
    return;
}
'''


# Reemplazamos el parser para devolver un árbol
Gramatica.build_parser(TreeNode)
resultado = Gramatica.parser.parse(codigo)

# === Visualización con Graphviz ===
dot = Digraph()
if resultado:
    resultado.render(dot)
    #with open("arbol.dot", "w") as f:
    #    f.write(dot.source)
    #print("\nÁrbol generado en 'arbol.dot'. Puedes visualizarlo en: https://dreampuf.github.io/GraphvizOnline")
    
    output_path = os.path.join(output_dir, "arbol.dot")
    with open(output_path, "w") as f:
        f.write(dot.source)
    print(f"\nÁrbol generado en '{output_path}'. Puedes visualizarlo en: https://dreampuf.github.io/GraphvizOnline")
    print("\nAnálisis completado. Archivos generados en la carpeta 'salida'.")
    
else:
    print("\nNo se generó árbol: error de análisis sintáctico.")
