# **Proyecto Evola**

##  **Nombre del Lenguaje**
EVOLA

## **Curso**
Compiladores

## **Nombre del docente**
Vicente Enrique Machaca Arceda

## **Descripción del Proyecto**
Evola es un lenguaje de programación que combina la simplicidad de Python, la eficiencia de “C + +” y se tomaron algunos elementos de otros lenguajes, con el objetivo de crear una herramienta con una sintaxis minimalista, permitiendo una fácil comprensión y escritura. La idea es ofrecer un compilador que haga el trabajo de forma eficiente, pero sin complicaciones, permitiendo que tanto novatos como expertos programen de manera ágil y productiva. 

## **Integrantes del Grupo**

1. **Castro Mamani Sebastian** 
2. **Arapa Chua Davis** 
3. **Ocharan Coaquira Miguel**
4. **Delgado Chipana Piero Adrian**


## **Especificación Léxica**

| **Token**         | **Expresión Regular**                          | **Descripción**                                |
|---------------|--------------------------------------------|--------------------------------------------|
| **variable float** | `[0-9]+ . [0-9]*`                          | Variables decimales                        |
| **variable bool** | `[0|1]`                                    | Variables de verdadero/falso               |
| **variable int**  | `[1-9]+`                                   | Variables de enteros                       |
| **Literal**       | `“.”`                                      | Variable string                            |
| **Id**            | `[a-z, A-Z] ([a-z, A-Z] | [0-9])*`         | Ids que se pueden colocar para darles un valor |
| **oSuma**         | `+`                                        | Suma                                       |
| **oResta**        | `-`                                        | Resta                                      |
| **oMult**         | `*`                                        | Multiplica                                 |
| **oDiv**          | `/`                                        | Divide                                     |
| **oResiduo**      | `%`                                        | Da el residuo de 2 números                 |
| **oOR**           | `||`                                       | Expresa el or: un valor o el otro          |
| **oAND**          | `&`                                        | Expresa y: un valor y el otro              |
| **oMayor**        | `>`                                        | Mayor que un número                        |
| **oMenor**        | `<`                                        | Menor que un número                        |
| **oIgual**        | `=`                                        | Igual a                                    |
| **oDiff**         | `!`                                        | Diferente de                               |
| **oDot**          | `°`                                        | Punto                                      |
| **oComa**         | `,`                                        | Coma                                       |
| **oSemi_coma**    | `;`                                        | Punto y coma                               |
| **corchLeft**     | `[`                                        | Corchete izquierdo                         |
| **corchRight**   | `]`                                        | Corchete derecho                           |
| **parLeft**       | `(`                                        | Paréntesis izquierdo                       |
| **parRight**      | `)`                                        | Paréntesis derecho                         |
| **keyLeft**       | `{`                                        | Llave izquierda                           |
| **keyRight**      | `}`                                        | Llave derecha                              |
| **For**           | `for`                                      | Palabra para hacer un bucle                |
| **While**         | `while`                                    | Palabra para hacer un bucle                |
| **Return**        | `return`                                   | Retorna un ID o valor                      |
| **Do**            | `do`                                       | Palabra para hacer algo                    |
| **In**            | `cin`                                      | Input                                      |
| **Out**           | `cout`                                     | Output                                     |
| **Void**          | `void`                                     | Variable vacía                             |
| **Main**          | `main`                                     | Función principal donde comienza la ejecución del programa |
| **Print**         | `print`                                    | Imprime variables                          |
| **If**            | `if`                                       | Función si condicional                     |
| **Else**          | `else`                                     | Función sino condicional                   |
| **false**         | `false`                                    | Valor Falso                                |
| **true**          | `true`                                     | Valor Verdadero                            |
| **int**           | `int`                                      | Tipo entero                                |
| **float**         | `float`                                    | Tipo flotante                              |
| **bool**          | `bool`                                     | Tipo booleano                              |
| **string**        | `string`                                   | Tipo string                                |

## **Ejemplo de Código**

### **Hola Mundo**

```
void main() {
    print("Hola Mundo");
}

```

### **Bucles Anidados**

```
void main() {
    int i, j;
    for (i = 1; i < 5; i = i + 1) {
        for (j = 1; j < 5; j = j + 1) {
            print(i);
            print(j);
        }
    }
}


```



### **Recursividad**

```
int factorial(int n) {
    if n < 2 {
        return 1;
    } else {
        return n * factorial(n - 1);
   }
}

void main() {
    int num = 5;
    int result = factorial(num);
    print(result);
}

```
