import psycopg2

# Función para conectar a la base de datos PostgreSQL
def conectar_bd():
    return psycopg2.connect(
        user="andhres",
        password="abc123",
        host="localhost",
        port="5432",
        database="bd_andhres"
    )

# Función para crear las tablas si no existen
def crear_tablas(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menuPrecios (
                combustible VARCHAR(50) PRIMARY KEY,
                precio_por_litro NUMERIC(10, 2) NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menuGasolinera (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                identificacion VARCHAR(50) NOT NULL,
                combustible VARCHAR(50) NOT NULL REFERENCES menuPrecios(combustible),
                litros NUMERIC(10, 2) NOT NULL,
                monto_total NUMERIC(10, 2) NOT NULL
            );
        """)
    conn.commit()

# Función para actualizar los precios de los combustibles en la base de datos
def inicializar_precios_combustibles(conn):
    precios = {
        'Regular': 36.90,
        'Premium': 28.80,
        'Diesel': 30.50
    }
    with conn.cursor() as cursor:
        for combustible, precio in precios.items():
            cursor.execute(
                """
                INSERT INTO menuPrecios (combustible, precio_por_litro)
                VALUES (%s, %s)
                ON CONFLICT (combustible) DO UPDATE SET precio_por_litro = EXCLUDED.precio_por_litro;
                """,
                (combustible, precio)
            )
    conn.commit()

# Función para obtener los precios de todos los combustibles
def obtener_precios_combustibles(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT combustible, precio_por_litro FROM menuPrecios")
        precios = cursor.fetchall()
        return {combustible: float(precio) for combustible, precio in precios}

# Función para obtener el precio de un tipo de combustible desde la tabla menuPrecios
def obtener_precio_combustible(conn, tipo_combustible):
    with conn.cursor() as cursor:
        cursor.execute("SELECT precio_por_litro FROM menuPrecios WHERE combustible = %s", (tipo_combustible,))
        resultado = cursor.fetchone()
        if resultado:
            return float(resultado[0])
        else:
            print(f"El combustible {tipo_combustible} no está disponible.")
            return None

# Función para guardar los datos del cliente en la tabla menuGasolinera y en un archivo de texto
def guardar_datos_cliente(conn, nombre, identificacion, combustible, litros, monto_total):
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO menuGasolinera (nombre, identificacion, combustible, litros, monto_total) VALUES (%s, %s, %s, %s, %s)",
            (nombre, identificacion, combustible, litros, monto_total)
        )
    conn.commit()

    # Obtener el precio por litro del combustible seleccionado
    precio_por_litro = obtener_precio_combustible(conn, combustible)
    if precio_por_litro is None:
        return  # Si no se encuentra el precio, no se guarda en el archivo

    # Guardar en archivo de texto
    with open("C:\\Users\\BEST COMPUTER\\Desktop\\ProyectosIE\\PrimerParcial\\facturas.txt", "a") as archivo:
        archivo.write(f"NOMBRE DEL CLIENTE: {nombre}\n")
        archivo.write(f"IDENTIFICACIÓN DEL VEHÍCULO: {identificacion}\n")
        archivo.write(f"TIPO DE COMBUSTIBLE: {combustible}\n")
        archivo.write(f"CANTIDAD DE LITROS: {litros}\n")
        archivo.write(f"PRECIO POR LITRO: Q{precio_por_litro:.2f}\n")
        archivo.write(f"MONTO TOTAL A PAGAR: Q{monto_total:.2f}\n")
        archivo.write("\n")  # Añadir una línea en blanco
        archivo.write("********************************************\n")  # Línea de separación
        archivo.write("\n")  # Línea en blanco para mayor separación

# Función para mostrar todos los registros ingresados
def mostrar_registros(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM menuGasolinera")
        registros = cursor.fetchall()
        if registros:
            print("\nRegistros en la base de datos:")
            for registro in registros:
                print(f"ID: {registro[0]}, Nombre: {registro[1]}, Identificación: {registro[2]}, Combustible: {registro[3]}, Litros: {registro[4]}, Monto Total: Q{registro[5]:.2f}")
        else:
            print("No hay registros en la base de datos.")

# Función para eliminar un registro mediante identificación
def eliminar_registro(conn, identificacion):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM menuGasolinera WHERE identificacion = %s", (identificacion,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Registro con identificación {identificacion} eliminado exitosamente.")
        else:
            print(f"No se encontró ningún registro con identificación {identificacion}.")

def main():
    # Conexión a la base de datos
    conn = conectar_bd()

    # Crear las tablas si no existen
    crear_tablas(conn)

    # Ingresar los precios de los combustibles
    inicializar_precios_combustibles(conn)

    while True:
        # Solicitar datos del usuario
        nombre = input("Ingrese su nombre: ")
        identificacion = input("Ingrese su número de placa: ")

        # Obtener precios actualizados
        precios_combustibles = obtener_precios_combustibles(conn)

        # Menú de combustibles
        print("Elija el tipo de combustible que desea.")
        for i, (combustible, precio) in enumerate(precios_combustibles.items(), start=1):
            print(f"{i}. {combustible} - Q{precio:.2f}")

        opcion_combustible = input("Ingrese el número de su opción: ")

        if opcion_combustible == '1':
            tipo_combustible = 'Regular'
        elif opcion_combustible == '2':
            tipo_combustible = 'Premium'
        elif opcion_combustible == '3':
            tipo_combustible = 'Diesel'
        else:
            print("Opción no válida.")
            continue

        # Obtener el precio del combustible elegido
        precio_por_litro = obtener_precio_combustible(conn, tipo_combustible)
        if precio_por_litro is None:
            continue

        # Solicitar cantidad de litros
        try:
            litros = float(input("Ingrese la cantidad en litros a despachar: "))
            if litros <= 0:
                raise ValueError("La cantidad de litros debe ser mayor a cero.")
        except ValueError as e:
            print(f"Error: {e}")
            continue

        # Calcular el monto total
        monto_total = litros * precio_por_litro

        # Mostrar el monto total a pagar
        print(f"El monto total a pagar por {litros} litros de {tipo_combustible} es: Q{monto_total:.2f}")

        # Guardar los datos del cliente en la base de datos y en un archivo
        guardar_datos_cliente(conn, nombre, identificacion, tipo_combustible, litros, monto_total)

        while True:
            print("\n¿Qué desea hacer a continuación?")
            print("1. Ver todos los registros")
            print("2. Continuar con el próximo cliente")
            print("3. Eliminar registro mediante identificación")
            print("4. Salir del programa")

            opcion = input("Ingrese el número de su opción: ")

            if opcion == '1':
                mostrar_registros(conn)
            elif opcion == '2':
                break  # Salir del bucle interno para continuar con el próximo cliente
            elif opcion == '3':
                identificacion_a_eliminar = input("Ingrese la placa del vehículo cuyo registro desea eliminar: ")
                eliminar_registro(conn, identificacion_a_eliminar)
            elif opcion == '4':
                conn.close()
                return  # Salir del programa
            else:
                print("Opción no válida.")

if __name__ == "__main__":
    main()