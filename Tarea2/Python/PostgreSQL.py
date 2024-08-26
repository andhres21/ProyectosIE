import psycopg2
# Conectarse a la base de datos
try:
    connection = psycopg2.connect(
        user="andhres",
        password="abc123",
        host="localhost",  # o la dirección de tu servidor PostgreSQL
        port="5432",       # puerto por defecto de PostgreSQL
        database="bd_andhres"
    )
    cursor = connection.cursor()
#------------------------------------------------------------------------------
    # # Comando para ingresar valores
    # insertarV = "INSERT INTO redes (nombre, carnet) VALUES (%s, %s);"
    # Valores = ('ANA', 2024)
    # cursor.execute(insertarV, Valores)
    # connection.commit()
    # print("Datos insertados correctamente en la tabla 'redes'.")
#------------------------------------------------------------------------------
    # # Comando para eliminar valores
    # eliminarV = "DELETE FROM redes WHERE carnet = %s;"
    # ELIMINAR = 2023
    # cursor.execute(eliminarV, (ELIMINAR,))
    # connection.commit()
    # print(f"Dato con carnet {ELIMINAR} eliminado correctamente.")
# --------------------------------------------------------------------------
    # Comando para actualizar valores
    actualizarV = "UPDATE redes SET carnet = %s WHERE carnet = %s;"
    NUEVO = "2007"
    ANTIGUO = "2024"
    cursor.execute(actualizarV, (NUEVO, ANTIGUO))
    connection.commit()
    print(f"Nombre actualizado correctamente a '{NUEVO}' para el carnet {ANTIGUO}.")
#------------------------------------------------------------------------------
    #Comando para visualizar la tabla
    Visualizar = "SELECT * FROM redes;"
    cursor.execute(Visualizar)
    records = cursor.fetchall()
    print("Datos de la tabla 'redes':")
    for record in records:
        print(record)
#------------------------------------------------------------------------------
except (Exception, psycopg2.Error) as error:
    print("Error al interactuar con PostgreSQL", error)
finally:
    # Cerrar la conexión a la base de datos
    if connection:
        cursor.close()
        connection.close()
        print("Conexión con PostgreSQL cerrada.")