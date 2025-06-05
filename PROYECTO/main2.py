import Lexer
import Gramatica
from graphviz import Digraph
import uuid

# === Código de prueba ===
codigo = '''
void main() {
    int x = 10;
    float y = 5.5;
    return;
}
'''

# === Árbol de derivación ===
class TreeNode:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children or []
        self.id = str(uuid.uuid4()).replace('-', '')

    def add_child(self, node):
        self.children.append(node)

    def render(self, dot):
        dot.node(self.id, self.label)
        for child in self.children:
            dot.edge(self.id, child.id)
            child.render(dot)

# Reemplazamos el parser para devolver un árbol
Gramatica.build_parser(TreeNode)
resultado = Gramatica.parser.parse(codigo)

# === Visualización con Graphviz ===
dot = Digraph()
if resultado:
    resultado.render(dot)
    with open("arbol.dot", "w") as f:
        f.write(dot.source)
    print("\nÁrbol generado en 'arbol.dot'. Puedes visualizarlo en: https://dreampuf.github.io/GraphvizOnline")
else:
    print("\nNo se generó árbol: error de análisis sintáctico.")
