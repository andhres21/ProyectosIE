# Definición de las categorías
bajoPeso = "Bajo peso"
pesoNormal = "Peso normal"
sobrePeso = "Sobrepeso"

while True:
    # Mostrar las opciones disponibles al usuario
    print("---------Opciones disponibles:---------")
    print("1. Calcular IMC y mostrar resultados")
    print("2. Leer información de un registro")
    print("3. Borrar información de un registro")
    print("4. Salir del programa")
    print("---------------------------------------")
    
    # Leer la opción del usuario
    opcion = int(input("Ingrese la opción deseada: "))
    
    # Validar la opción
    if not (1 <= opcion <= 4):
        print("Opción no válida. Intente de nuevo.")
        continue
    
    if opcion == 1:
        nombre = input("Ingrese su nombre: ")
        peso = float(input("Ingrese su peso en kilogramos: "))
        altura = float(input("Ingrese su altura en metros: "))
        
        # Validar peso y altura
        if peso == 0 or altura == 0:
            print("Peso y altura no válidos, no es posible procesar el IMC.")
            continue
        
        # Calcular IMC
        imc = peso / (altura ** 2)
        
        # Determinar la categoría
        if imc < 18.5:
            categoria = bajoPeso
        elif imc < 24.9:
            categoria = pesoNormal
        else:
            categoria = sobrePeso
        
        # Mostrar resultados
        print(f"\nNombre: {nombre}")
        print(f"IMC: {imc:.2f}")
        print(f"Categoría: {categoria}")
        
        # Guardar en archivo
        with open('imc.txt', 'a') as f:
            f.write(f"Nombre: {nombre}, IMC: {imc:.2f}, Categoría: {categoria}\n")
        
        print("Información guardada en 'imc.txt'.")
    
    elif opcion == 2:
        try:
            with open('imc.txt', 'r') as f:
                contenido = f.readlines()
            
            if not contenido:
                print("El archivo está vacío, ingrese un registro.")
                continue
            
            nombre_buscado = input("Ingrese el nombre del registro que desea leer: ")
            encontrado = False
            
            for linea in contenido:
                if nombre_buscado in linea:
                    print(f"\nRegistro encontrado:\n{linea}")
                    encontrado = True
                    break
            
            if not encontrado:
                print(f"No se encontró ningún registro con el nombre '{nombre_buscado}'.")
        
        except FileNotFoundError:
            print("No se encontró el archivo 'imc.txt'.")
    
    elif opcion == 3:
        try:
            with open('imc.txt', 'r') as f:
                contenido = f.readlines()
            
            if not contenido:
                print("El archivo está vacío, ingrese un registro.")
                continue
            
            nombre_buscado = input("Ingrese el nombre del registro que desea borrar: ")
            encontrado = False
            lineas_nuevas = []
            
            for linea in contenido:
                if nombre_buscado not in linea:
                    lineas_nuevas.append(linea)
                else:
                    print(f"Registro encontrado y eliminado:\n{linea}")
                    encontrado = True
            
            with open('imc.txt', 'w') as f:
                f.writelines(lineas_nuevas)
            
            if not encontrado:
                print(f"No se encontró ningún registro con el nombre '{nombre_buscado}'.")
        
        except FileNotFoundError:
            print("No se encontró el archivo 'imc.txt'.")
    
    elif opcion == 4:
        print("¡Gracias por usar el programa!")
        break