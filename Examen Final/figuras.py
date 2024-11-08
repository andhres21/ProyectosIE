import psycopg2
import os
import re

# Configuración de la conexión a la base de datos PostgreSQL
conexion = psycopg2.connect(
    dbname="exfinal",
    user="andhres",
    password="abc123",
    host="localhost",
    port="5432"
)

cursor = conexion.cursor()

# Funciones de validación
def es_palindromo(cadena):
    return cadena == cadena[::-1]

def es_primo(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

def es_perfecto(num):
    suma = sum([i for i in range(1, num) if num % i == 0])
    return suma == num

# Funciones de base de datos y archivo
def guardar_historial(nombre_usuario, tipo, entrada, resultado):
    # Guarda en archivo de texto
    with open("salida.txt", "a") as file:
        file.write(f"{nombre_usuario},{tipo},{entrada},{resultado}\n")
    
    # Guarda en base de datos PostgreSQL
    query = """
    INSERT INTO historial (nombre_usuario, tipo, entrada, resultado)
    VALUES (%s, %s, %s, %s);
    """
    cursor.execute(query, (nombre_usuario, tipo, entrada, resultado))
    conexion.commit()
    print("Registro guardado en el archivo y la base de datos.")

def mostrar_historial():
    # Mostrar solo desde el archivo
    print("\n--- Historial en Archivo ---")
    if not os.path.exists("salida.txt"):
        print("No hay historial registrado en el archivo.")
    else:
        with open("salida.txt", "r") as file:
            for linea in file:
                print(linea.strip())

def borrar_dato(nombre):
    # Borrar en archivo de texto
    if not os.path.exists("salida.txt"):
        print("No hay historial registrado en el archivo.")
    else:
        with open("salida.txt", "r") as file:
            registros = file.readlines()
        
        registros_filtrados = [registro for registro in registros if not registro.startswith(nombre)]
        
        with open("salida.txt", "w") as file:
            file.writelines(registros_filtrados)
    
    # Borrar en base de datos PostgreSQL
    delete_query = "DELETE FROM historial WHERE nombre_usuario = %s;"
    cursor.execute(delete_query, (nombre,))
    conexion.commit()
    print("Los datos del usuario han sido borrados del archivo y la base de datos.")

# Menús del programa
def menu_principal():
    while True:
        print("\n--- Menú Principal ---")
        print("1. Ingreso al Programa")
        print("2. Historial de Datos")
        print("3. Borrado de Datos")
        print("4. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            nombre_usuario = solicitar_nombre_usuario()
            submenu_funcionalidades(nombre_usuario)
        
        elif opcion == "2":
            mostrar_historial()
        
        elif opcion == "3":
            nombre = solicitar_nombre_usuario()
            borrar_dato(nombre)
        
        elif opcion == "4":
            print("Esperamos que pase un feliz día")
            break
        
        else:
            print("Opción no válida. Intente de nuevo.")

def solicitar_nombre_usuario():
    while True:
        nombre_usuario = input("Ingrese su nombre: ")
        if re.match("^[A-Za-z]+$", nombre_usuario):
            return nombre_usuario
        else:
            print("Nombre inválido. Por favor, ingrese solo letras sin espacios ni números.")

def solicitar_numero(mensaje):
    while True:
        numero = input(mensaje)
        if numero.isdigit():
            return int(numero)
        else:
            print("Entrada inválida. Solo se permiten números.")

def solicitar_palindromo():
    while True:
        cadena = input("Ingrese una palabra, frase o número para verificar si es palíndromo: ").replace(" ", "").lower()
        # Permite letras y números en el detector de palíndromo
        if re.match("^[A-Za-z0-9]+$", cadena):
            return cadena
        else:
            print("Entrada inválida. Solo se permiten letras y números en el detector de palíndromo.")

def submenu_funcionalidades(nombre_usuario):
    while True:
        print("\n--- Submenú de Funcionalidades ---")
        print("1. Detector de Palíndromo")
        print("2. Detector de Número Primo")
        print("3. Detector de Número Perfecto")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            cadena = solicitar_palindromo()
            resultado = es_palindromo(cadena)
            print(f"Resultado: {'Es palíndromo' if resultado else 'No es palíndromo'}")
            guardar_historial(nombre_usuario, "Palíndromo", cadena, "Es" if resultado else "No es")
            break  # Regresa al menú principal después de ingresar datos
        
        elif opcion == "2":
            numero = solicitar_numero("Ingrese un número para verificar si es primo: ")
            resultado = es_primo(numero)
            print(f"Resultado: {'Es primo' if resultado else 'No es primo'}")
            guardar_historial(nombre_usuario, "Número Primo", numero, "Es" if resultado else "No es")
            break  # Regresa al menú principal después de ingresar datos
        
        elif opcion == "3":
            numero = solicitar_numero("Ingrese un número para verificar si es perfecto: ")
            resultado = es_perfecto(numero)
            print(f"Resultado: {'Es perfecto' if resultado else 'No es perfecto'}")
            guardar_historial(nombre_usuario, "Número Perfecto", numero, "Es" if resultado else "No es")
            break  # Regresa al menú principal después de ingresar datos
        
        else:
            print("Opción no válida. Intente de nuevo.")

# Ejecutar el programa
menu_principal()

# Cerrar la conexión a la base de datos
cursor.close()
conexion.close()
