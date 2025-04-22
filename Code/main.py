import csv

## = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ##
## = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ##
class Node:
    def __init__(self, label, is_terminal=False, value=None):
        self.label = label  # Etiqueta del nodo (no terminal o terminal)
        self.is_terminal = is_terminal  # Flag para indicar si es un terminal
        self.value = value  # Valor del token (para terminales)
        self.children = []  # Hijos del nodo
        self.node_id = None  # ID único para el nodo en el gráfico

    def add_child(self, node):
        self.children.append(node)
        return node
        
    def agregar_epsilon(self):
      
        if not self.children and not self.is_terminal:
            epsilon_node = Node("ε", is_terminal=True, value="ε")
            self.add_child(epsilon_node)
        else:
            for child in self.children:
                child.agregar_epsilon()

    def to_graphviz(self):
        nodes = []
        edges = []
        
        def traverse(node, node_counter=[0]):
            if node.node_id is None:
                node.node_id = f"node{node_counter[0]}"
                node_counter[0] += 1
            
            # Definir el estilo del nodo
            shape = "box" if node.is_terminal else "ellipse"
            label = node.value if node.is_terminal and node.value else node.label
            
            # Añadir nodo
            nodes.append(f'  {node.node_id} [label="{label}", shape={shape}];')
            
            # Añadir aristas
            for child in node.children:
                child_id = traverse(child, node_counter)
                edges.append(f'  {node.node_id} -> {child_id};')
                
            return node.node_id
        
        traverse(self)
        
        graphviz_code = "digraph SyntaxTree {\n"
        graphviz_code += "  node [fontname=\"Arial\"];\n"
        graphviz_code += "\n".join(nodes)
        graphviz_code += "\n"
        graphviz_code += "\n".join(edges)
        graphviz_code += "\n}"
        
        return graphviz_code

## = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =##
## = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =##

class AnalizadorSintacticoLL:
    def __init__(self, archivo_tabla):
        self.tabla = self.cargar_tabla_csv(archivo_tabla)
        self.node_counter = 0
    
    def cargar_tabla_csv(self, archivo):
        tabla = {}
        with open(archivo, newline='') as csvfile:
            reader = list(csv.reader(csvfile, delimiter=';'))
            terminales = reader[0][1:]  # Saltar la primera columna vacía
            for fila in reader[1:]:
                no_terminal = fila[0]
                for i, celda in enumerate(fila[1:]):
                    produccion = celda.strip()
                    if produccion:  # Solo agregamos si hay producción
                        lado_derecho = produccion.split() if produccion != 'ε' else ['ε']
                        tabla[(no_terminal, terminales[i])] = lado_derecho
        return tabla

    def analizar(self, tokens):
        # Agregar el símbolo de fin de entrada
        tokens.append('$')
        
        # Inicializar pila y puntero de entrada
        root = Node('E')  # Nodo raíz con el símbolo inicial
        pila = [('$', None), ('E', root)]  # Pila con tuplas (símbolo, nodo)
        indice = 0
        token_actual = tokens[indice]
        
        # Para seguimiento del análisis
        pasos = []
        
        paso_num = 1
        while pila[-1][0] != '$':  # Mientras no hayamos llegado al fondo de la pila
            X, node = pila[-1]  # Tope de la pila
            
            # Guardamos el estado actual
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join([p[0] for p in pila])
            accion = ""
            
            if X == token_actual:  # Si coincide con el token actual
                accion = f"Terminal {X}"
                pila.pop()         # Eliminar de la pila
                
                # Si el nodo no es None, marcarlo como terminal y asignar el valor
                if node:
                    node.is_terminal = True
                    node.value = X
                
                indice += 1        # Avanzar al siguiente token
                if indice < len(tokens):
                    token_actual = tokens[indice]
                    
            elif (X, token_actual) in self.tabla:  # Si hay una regla de producción
                produccion = self.tabla[(X, token_actual)]
                produccion_str = ' '.join(produccion) if produccion != ['ε'] else 'ε'
                accion = f"{X} → {produccion_str}"
                
                pila.pop()         # Eliminar no terminal
                
                # Agregar la producción a la pila (en orden inverso)
                child_nodes = []
                for simbolo in produccion:
                    if simbolo != 'ε':  # No agregar epsilon
                        child_node = Node(simbolo)
                        child_nodes.append(child_node)
                        
                # Agregar los nodos como hijos del nodo actual
                if node:
                    for child in child_nodes:
                        node.add_child(child)
                
                # Agregar a la pila en orden inverso
                for i in range(len(child_nodes) - 1, -1, -1):
                    simbolo = produccion[i] if i < len(produccion) else None
                    if simbolo != 'ε':
                        pila.append((simbolo, child_nodes[i]))
            else:
                # Error: no hay regla para esta combinación
                pasos.append((paso_num, pila_actual, entrada_restante, "ERROR: No hay regla definida"))
                return {
                    "resultado": "Error sintáctico",
                    "mensaje": f"Error sintáctico en el token '{token_actual}' (posición {indice}). No hay regla definida para el no terminal '{X}'.",
                    "pasos": pasos,
                    "arbol": None,
                    "graphviz": None
                }
            
            pasos.append((paso_num, pila_actual, entrada_restante, accion))
            paso_num += 1
        
        # Verificar que hemos consumido toda la entrada
        if token_actual == '$':
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join([p[0] for p in pila])
            pasos.append((paso_num, pila_actual, entrada_restante, "ACEPTAR"))
            
            root.agregar_epsilon()
            # Generar el código Graphviz
            graphviz_code = root.to_graphviz()
            
            return {
                "resultado": "Aceptado",
                "mensaje": "Análisis completado: La cadena pertenece a la gramática.",
                "pasos": pasos,
                "arbol": root,
                "graphviz": graphviz_code
            }
        else:
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join([p[0] for p in pila])
            pasos.append((paso_num, pila_actual, entrada_restante, "ERROR: Entrada no consumida"))
            
            return {
                "resultado": "Error sintáctico",
                "mensaje": f"Error sintáctico: Entrada no consumida completamente. Token actual: '{token_actual}'",
                "pasos": pasos,
                "arbol": None,
                "graphviz": None
            }

def analizar_desde_archivo(archivo_tokens, archivo_tabla):
    with open(archivo_tokens, 'r') as f:
        lineas = f.readlines()

    analizador = AnalizadorSintacticoLL(archivo_tabla)
    resultados = []

    for i, linea in enumerate(lineas, start=1):
        cadena = linea.strip()
        if not cadena:
            continue  # Saltar líneas vacías

        tokens = cadena.split()
        resultado = analizador.analizar(tokens)
        resultados.append(resultado)

        # Imprimir resultados
        print(f"\n=== ANÁLISIS SINTÁCTICO - Línea {i} ===")
        print(f"Entrada: {cadena}")
        print(f"Resultado: {resultado['resultado']}")
        print(f"Mensaje: {resultado['mensaje']}")
        print("\n=== PASOS DEL ANÁLISIS ===")

        titulos = ["Paso", "Pila", "Entrada", "Acción"]
        anchos = [4, 20, 20, 25]
        imprimir_tabla(resultado['pasos'], titulos, anchos)
        
        if resultado["graphviz"]:
            print("\n=== ÁRBOL SINTÁCTICO (GRAPHVIZ) ===")
            print(resultado["graphviz"])
            print("\nPuede visualizar este árbol en: https://dreampuf.github.io/GraphvizOnline")

    return resultados


def imprimir_tabla(datos, titulos, anchos):
    # Función auxiliar para truncar o rellenar una cadena al ancho especificado
    def formatear_celda(texto, ancho):
        texto = str(texto)
        if len(texto) > ancho:
            return texto[:ancho-3] + "..."
        return texto.ljust(ancho)
    
    # Crear una línea separadora
    separador = "+"
    for ancho in anchos:
        separador += "-" * (ancho + 2) + "+"
    
    # Imprimir encabezado
    print(separador)
    header = "|"
    for titulo, ancho in zip(titulos, anchos):
        header += " " + formatear_celda(titulo, ancho) + " |"
    print(header)
    print(separador)
    
    # Imprimir datos
    for fila in datos:
        linea = "|"
        for valor, ancho in zip(fila, anchos):
            linea += " " + formatear_celda(valor, ancho) + " |"
        print(linea)
    
    # Imprimir línea final
    print(separador)

def analizar_cadena(cadena):
    tokens = cadena.strip().split()
    analizador = AnalizadorSintacticoLL("tabla_sintactica.csv")
    resultado = analizador.analizar(tokens)
    
    # Imprimir resultado
    print("\n=== ANÁLISIS SINTÁCTICO ===")
    print(f"Entrada: {cadena}")
    print(f"Resultado: {resultado['resultado']}")
    print(f"Mensaje: {resultado['mensaje']}")
    print("\n=== PASOS DEL ANÁLISIS ===")
    
    # Definir las columnas de la tabla
    titulos = ["Paso", "Pila", "Entrada", "Acción"]
    anchos = [4, 20, 20, 25]  # Anchos de cada columna
    
    # Imprimir la tabla con los pasos
    imprimir_tabla(resultado['pasos'], titulos, anchos)
    
    if resultado["graphviz"]:
        print("\n=== ÁRBOL SINTÁCTICO ===")
        print(resultado["graphviz"])
    
    return resultado


# Probar las cadenas solicitadas
print("\n--- EJEMPLO 1 ---")
analizar_cadena("int + int")

'''
print("\n--- EJEMPLO 2 ---")
analizar_cadena("int * int")

print("\n--- EJEMPLO 3 ---")
analizar_cadena("int + + int")

# Prueba desde archivo
print("\n--- PRUEBA DESDE ARCHIVO ---")
analizar_desde_archivo("tokens.txt", "tabla_sintactica.csv")
'''