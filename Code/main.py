import csv

class AnalizadorSintacticoLL:
    def __init__(self, archivo_tabla):
        self.tabla = self.cargar_tabla_csv(archivo_tabla)
    
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
        pila = ['$', 'E']  # Comenzamos con el símbolo inicial E y el marcador de fondo $
        indice = 0
        token_actual = tokens[indice]
        
        # Para seguimiento del análisis
        pasos = []
        
        paso_num = 1
        while pila[-1] != '$':  # Mientras no hayamos llegado al fondo de la pila
            X = pila[-1]  # Tope de la pila
            
            # Guardamos el estado actual
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join(pila)
            accion = ""
            
            if X == token_actual:  # Si coincide con el token actual
                accion = f"Emparejar {X}"
                pila.pop()         # Eliminar de la pila
                indice += 1        # Avanzar al siguiente token
                if indice < len(tokens):
                    token_actual = tokens[indice]
            elif (X, token_actual) in self.tabla:  # Si hay una regla de producción
                produccion = self.tabla[(X, token_actual)]
                produccion_str = ' '.join(produccion) if produccion != ['ε'] else 'ε'
                accion = f"{X} → {produccion_str}"
                
                pila.pop()         # Eliminar no terminal
                
                # Agregar la producción a la pila (en orden inverso)
                for simbolo in reversed(produccion):
                    if simbolo != 'ε':  # No agregar epsilon
                        pila.append(simbolo)
            else:
                # Error: no hay regla para esta combinación
                pasos.append((paso_num, pila_actual, entrada_restante, "ERROR: "))
                return {
                    "resultado": "Error sintáctico",
                    "mensaje": f"Error sintáctico en el token '{token_actual}' (posición {indice}). No hay regla definida para el no terminal '{X}'.",
                    "pasos": pasos
                }
            
            pasos.append((paso_num, pila_actual, entrada_restante, accion))
            paso_num += 1
        
        # Verificar que hemos consumido toda la entrada
        if token_actual == '$':
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join(pila)
            pasos.append((paso_num, pila_actual, entrada_restante, "ACEPTAR"))
            
            return {
                "resultado": "Aceptado",
                "mensaje": "Análisis completado: La cadena pertenece a la gramática.",
                "pasos": pasos
            }
        else:
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join(pila)
            pasos.append((paso_num, pila_actual, entrada_restante, "ERROR: Entrada no consumida"))
            
            return {
                "resultado": "Error sintáctico",
                "mensaje": f"Error sintáctico: Entrada no consumida completamente. Token actual: '{token_actual}'",
                "pasos": pasos
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

    return resultados

def analizar_desde_archivo2(archivo_tokens, archivo_tabla):
    with open(archivo_tokens, 'r') as f:
        cadena = f.read().strip()
    
    tokens = cadena.split()
    analizador = AnalizadorSintacticoLL("tabla_sintactica.csv")
    resultado = analizador.analizar(tokens)

    # Imprimir resultado
    print("\n=== ANÁLISIS SINTÁCTICO ===")
    print(f"Entrada: {cadena}")
    print(f"Resultado: {resultado['resultado']}")
    print(f"Mensaje: {resultado['mensaje']}")
    print("\n=== PASOS DEL ANÁLISIS ===")

    # Tabla
    titulos = ["Paso", "Pila", "Entrada", "Acción"]
    anchos = [4, 20, 20, 25]
    imprimir_tabla(resultado['pasos'], titulos, anchos)

    return resultado
    
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
    analizador = AnalizadorSintacticoLL("tabla_sintactica.csv")  # <-- Agrega el nombre del archivo
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
    
    return resultado



# Probar las cadenas solicitadas
print("\n--- EJEMPLO 1 ---")
analizar_cadena("int + int")

print("\n--- EJEMPLO 2 ---")
analizar_cadena("int * int")

print("\n--- EJEMPLO 3 ---")
analizar_cadena("int + + int")

# Prueba desde archivo
print("\n--- PRUEBA DESDE ARCHIVO ---")
analizar_desde_archivo("tokens.txt", "tabla_sintactica.csv")