from Lexer import lexer
import Parser
import os


# Archivo de entrada (cambia esto por tu archivo)
ARCHIVO_ENTRADA = "codigo.txt"
ARCHIVO_TOKENS = "salida/tokens.txt"
ARCHIVO_ERRORES = "salida/errores_lexicos.txt"
if not os.path.exists('salida'):
    os.makedirs('salida')

# Limpiar archivos de salida
with open(ARCHIVO_ERRORES, "w", encoding="utf-8") as f:
    f.write("=== ERRORES LÉXICOS ===\n\n")

with open(ARCHIVO_TOKENS, "w", encoding="utf-8") as f:
    f.write("=== TOKENS ENCONTRADOS ===\n\n")
    f.write(f"{'Tipo':<15} {'Valor':<20} {'Línea'}\n")
    f.write("-" * 40 + "\n")

# Procesar archivo de entrada
try:
    with open(ARCHIVO_ENTRADA, "r", encoding="utf-8") as f:
        data = f.read()
    
    lexer.input(data)
    token_count = 0


    while True:
        tok = lexer.token()
        if not tok:
            break
        token_count += 1
        
        with open(ARCHIVO_TOKENS, "a", encoding="utf-8") as tokens_file:
            tokens_file.write(f"{tok.type:<15} {str(tok.value):<20} {tok.lineno}\n")
    
    print(f"\nAnálisis completado. Tokens encontrados: {token_count}")
    
    # Verificar si hubo errores
    with open(ARCHIVO_ERRORES, "r", encoding="utf-8") as error_file:
        errores = error_file.readlines()
    
    if len(errores) > 2:
        print("Se encontraron errores léxicos. Ver 'errores_lexicos.txt'")
    else:
        print("No se encontraron errores léxicos.")
    
    print(f"\nResultados guardados en:\n- {ARCHIVO_TOKENS}\n- {ARCHIVO_ERRORES}")

except FileNotFoundError:
    print(f"Error: No se encontró el archivo de entrada '{ARCHIVO_ENTRADA}'")
except Exception as e:
    print(f"Error inesperado: {str(e)}")