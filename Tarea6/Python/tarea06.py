import psycopg2
from datetime import datetime, timedelta
import os

# Datos de conexión a la base de datos
DB_NAME = "bd_andhres"
USER = "andhres"
PASSWORD = "abc123"
HOST = "localhost"
PORT = "5432"

# Ruta del archivo de facturas
FACTURAS_FILE = r"C:\Users\BEST COMPUTER\Desktop\ProyectosIE\Tarea6\facturas.txt"

# Conectar a la base de datos
def conectar_bd():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Crear tablas si no existen
def crear_tablas():
    conn = conectar_bd()
    if conn is not None:
        try:
            cur = conn.cursor()

            # Crear tabla clientes
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100),
                    nit VARCHAR(20),
                    placa VARCHAR(20)
                );
            """)

            # Crear tabla estacionamiento
            cur.execute("""
                CREATE TABLE IF NOT EXISTS estacionamiento (
                    id SERIAL PRIMARY KEY,
                    cliente_id INT REFERENCES clientes(id),
                    hora_entrada TIME,
                    hora_salida TIME,
                    tiempo_total_horas INT,
                    monto_total NUMERIC(10, 2)
                );
            """)

            conn.commit()
            print("Tablas creadas (si no existían) exitosamente.")

        except Exception as e:
            print(f"Error al crear las tablas: {e}")
            conn.rollback()

        finally:
            cur.close()
            conn.close()

# Validar entrada de tiempo
def validar_hora(hora):
    try:
        partes = hora.split(":")
        if len(partes) == 2 and 0 <= int(partes[0]) < 24 and 0 <= int(partes[1]) < 60:
            return True
        return False
    except ValueError:
        return False

# Calcular el monto total a pagar
def calcular_monto(tiempo_horas):
    if tiempo_horas <= 1:
        return 15.00
    else:
        return 15.00 + (tiempo_horas - 1) * 20.00

# Calcular tiempo total en horas y minutos
def calcular_tiempo_total(hora_entrada, hora_salida):
    formato = "%H:%M"
    entrada = datetime.strptime(hora_entrada, formato)
    salida = datetime.strptime(hora_salida, formato)
    
    # Si la hora de salida es menor que la hora de entrada, asumimos que pasó la medianoche
    if salida < entrada:
        salida += timedelta(days=1)
    
    tiempo_total = salida - entrada
    total_segundos = tiempo_total.total_seconds()
    horas = int(total_segundos // 3600)
    minutos = int((total_segundos % 3600) // 60)
    return horas, minutos

# Ingresar datos del cliente y calcular el monto
def ingresar_datos_usuario():
    nombre = input("Ingrese el nombre del cliente: ")
    nit = input("Ingrese el NIT del cliente: ")
    placa = input("Ingrese la identificación del vehículo (placa): ")

    hora_entrada = input("Ingrese la hora de entrada (HH:MM): ")
    while not validar_hora(hora_entrada):
        print("Hora de entrada inválida. Intente nuevamente.")
        hora_entrada = input("Ingrese la hora de entrada (HH:MM): ")

    hora_salida = input("Ingrese la hora de salida (HH:MM): ")
    while not validar_hora(hora_salida):
        print("Hora de salida inválida. Intente nuevamente.")
        hora_salida = input("Ingrese la hora de salida (HH:MM): ")

    # Calcular tiempo total en horas y minutos
    horas_totales, minutos_totales = calcular_tiempo_total(hora_entrada, hora_salida)
    
    # Redondear el tiempo total para el monto
    tiempo_total_horas = horas_totales + minutos_totales / 60
    horas_cobradas = int(tiempo_total_horas)
    if tiempo_total_horas % 1 > 0:
        horas_cobradas += 1

    monto_total = calcular_monto(horas_cobradas)

    # Conectar a la base de datos y guardar los datos
    conn = conectar_bd()
    if conn is not None:
        try:
            cur = conn.cursor()

            # Insertar en la tabla clientes
            cur.execute("""
                INSERT INTO clientes (nombre, nit, placa) 
                VALUES (%s, %s, %s) RETURNING id;
            """, (nombre, nit, placa))
            cliente_id = cur.fetchone()[0]

            # Insertar en la tabla estacionamiento
            cur.execute("""
                INSERT INTO estacionamiento (cliente_id, hora_entrada, hora_salida, tiempo_total_horas, monto_total) 
                VALUES (%s, %s, %s, %s, %s);
            """, (cliente_id, hora_entrada, hora_salida, horas_cobradas, monto_total))

            conn.commit()

            print("\n--- Resumen de la Transacción ---")
            print(f"Cliente: {nombre}")
            print(f"NIT: {nit}")
            print(f"Placa: {placa}")
            print(f"Entrada: {hora_entrada}")
            print(f"Salida: {hora_salida}")
            print(f"Tiempo Total: {horas_totales} horas y {minutos_totales} minutos")
            print(f"Cantidad de horas cobradas: {horas_cobradas} horas")
            print(f"Monto total a pagar: Q{monto_total:.2f}")
            print("*********************************************")

            # Guardar en facturas.txt
            with open(FACTURAS_FILE, "a") as file:
                file.write(f"Cliente: {nombre}\n")
                file.write(f"NIT: {nit}\n")
                file.write(f"Placa: {placa}\n")
                file.write(f"Entrada: {hora_entrada}\n")
                file.write(f"Salida: {hora_salida}\n")
                file.write(f"Tiempo Total: {horas_totales} horas y {minutos_totales} minutos\n")
                file.write(f"Cantidad de horas cobradas: {horas_cobradas} horas\n")
                file.write(f"Monto: Q{monto_total:.2f}\n")
                file.write("*********************************************\n")
            print("Factura guardada exitosamente.")

        except Exception as e:
            print(f"Error al procesar la transacción: {e}")
            conn.rollback()

        finally:
            cur.close()
            conn.close()

# Mostrar historial de datos
def mostrar_historial():
    conn = conectar_bd()
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT c.nombre, c.nit, c.placa, e.hora_entrada, e.hora_salida, e.tiempo_total_horas, e.monto_total
                FROM estacionamiento e
                JOIN clientes c ON e.cliente_id = c.id;
            """)
            registros = cur.fetchall()
            if registros:
                for registro in registros:
                    print(f"Cliente: {registro[0]}, NIT: {registro[1]}, Placa: {registro[2]}, Entrada: {registro[3]}, Salida: {registro[4]}, Tiempo: {registro[5]:.2f} horas, Monto: Q{registro[6]:.2f}")
            else:
                print("No hay registros en la base de datos.")

        except Exception as e:
            print(f"Error al mostrar el historial: {e}")

        finally:
            cur.close()
            conn.close()

# Borrar datos del historial
def borrar_datos():
    conn = conectar_bd()
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM estacionamiento;")
            cur.execute("DELETE FROM clientes;")
            conn.commit()
            print("Datos borrados exitosamente.")

        except Exception as e:
            print(f"Error al borrar los datos: {e}")
            conn.rollback()

        finally:
            cur.close()
            conn.close()

# Función principal del programa
def main():
    crear_tablas()  # Crear las tablas al inicio del programa
    
    while True:
        print("\n--- Menú Principal ---")
        print("1. Ingreso de datos del usuario.")
        print("2. Historial de datos.")
        print("3. Borrado de datos.")
        print("4. Salir.")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            ingresar_datos_usuario()
        elif opcion == "2":
            mostrar_historial()
        elif opcion == "3":
            borrar_datos()
        elif opcion == "4":
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida, por favor seleccione nuevamente.")

if __name__ == "__main__":
    main()