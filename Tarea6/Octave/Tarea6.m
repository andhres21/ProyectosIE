pkg load database; % Cargar el paquete de base de datos

% Datos de conexión a la base de datos
DB_NAME = "bd_andhres";
USER = "andhres";
PASSWORD = "abc123";
HOST = "localhost";
PORT = "5432";

% Ruta del archivo de facturas
FACTURAS_FILE = "C:\Users\BEST COMPUTER\Desktop\ProyectosIE\Tarea6\facturas.txt";

% Conectar a la base de datos
function conn = conectar_bd()
    try
        conn = pq_connect(setdbopts('dbname','bd_andhres', 'host', 'localhost', 'port', '5432', 'user', 'andhres', 'password', 'abc123'));
    catch
        disp("Error al conectar a la base de datos.");
        conn = [];
    end
end

% Crear tablas si no existen
function crear_tablas()
    conn = conectar_bd();
    if !isempty(conn)
        try
            % Crear tabla clientes
            pq_exec(conn, "CREATE TABLE IF NOT EXISTS clientes (id SERIAL PRIMARY KEY, nombre VARCHAR(100), nit VARCHAR(20), placa VARCHAR(20));");

            % Crear tabla estacionamiento
            pq_exec(conn, "CREATE TABLE IF NOT EXISTS estacionamiento (id SERIAL PRIMARY KEY, cliente_id INT REFERENCES clientes(id), hora_entrada TIME, hora_salida TIME, tiempo_total_horas INT, monto_total NUMERIC(10, 2));");

            disp("Tablas creadas (si no existían) exitosamente.");
        catch
            disp("Error al crear las tablas.");
        end
        pq_close(conn);
    end
end

% Validar entrada de tiempo
function es_valida = validar_hora(hora)
    partes = strsplit(hora, ":");
    if length(partes) == 2
        horas = str2double(partes{1});
        minutos = str2double(partes{2});
        es_valida = (0 <= horas && horas < 24) && (0 <= minutos && minutos < 60);
    else
        es_valida = false;
    end
end

% Calcular el monto total a pagar
function monto_total = calcular_monto(tiempo_horas)
    if tiempo_horas <= 1
        monto_total = 15.00;
    else
        monto_total = 15.00 + (tiempo_horas - 1) * 20.00;
    end
end

% Calcular tiempo total en horas y minutos
function [horas, minutos] = calcular_tiempo_total(hora_entrada, hora_salida)
    formato = "HH:MM";
    entrada = datenum(hora_entrada, formato);
    salida = datenum(hora_salida, formato);

    % Si la hora de salida es menor que la hora de entrada, asumimos que pasó la medianoche
    if salida < entrada
        salida = salida + 1;
    end

    tiempo_total = salida - entrada;
    total_segundos = tiempo_total * 24 * 3600;
    horas = floor(total_segundos / 3600);
    minutos = floor(mod(total_segundos, 3600) / 60);
end

% Ingresar datos del cliente y calcular el monto
function ingresar_datos_usuario()
    nombre = input("Ingrese el nombre del cliente: ", "s");
    nit = input("Ingrese el NIT del cliente: ", "s");
    placa = input("Ingrese la identificación del vehículo (placa): ", "s");

    hora_entrada = input("Ingrese la hora de entrada (HH:MM): ", "s");
    while !validar_hora(hora_entrada)
        disp("Hora de entrada inválida. Intente nuevamente.");
        hora_entrada = input("Ingrese la hora de entrada (HH:MM): ", "s");
    end

    hora_salida = input("Ingrese la hora de salida (HH:MM): ", "s");
    while !validar_hora(hora_salida)
        disp("Hora de salida inválida. Intente nuevamente.");
        hora_salida = input("Ingrese la hora de salida (HH:MM): ", "s");
    end

    % Calcular tiempo total en horas y minutos
    [horas_totales, minutos_totales] = calcular_tiempo_total(hora_entrada, hora_salida);

    % Redondear el tiempo total para el monto
    tiempo_total_horas = horas_totales + minutos_totales / 60;
    horas_cobradas = floor(tiempo_total_horas);
    if mod(tiempo_total_horas, 1) > 0
        horas_cobradas = horas_cobradas + 1;
    end

    monto_total = calcular_monto(horas_cobradas);

    % Conectar a la base de datos y guardar los datos
    conn = conectar_bd();
    if !isempty(conn)
        try
            % Insertar en la tabla clientes
            cliente_id = pq_exec(conn, sprintf("INSERT INTO clientes (nombre, nit, placa) VALUES ('%s', '%s', '%s') RETURNING id;", nombre, nit, placa));
            cliente_id = cliente_id{1, 1};

            % Insertar en la tabla estacionamiento
            pq_exec(conn, sprintf("INSERT INTO estacionamiento (cliente_id, hora_entrada, hora_salida, tiempo_total_horas, monto_total) VALUES (%d, '%s', '%s', %d, %.2f);", cliente_id, hora_entrada, hora_salida, horas_cobradas, monto_total));

            disp("\n--- Resumen de la Transacción ---");
            disp(sprintf("Cliente: %s", nombre));
            disp(sprintf("NIT: %s", nit));
            disp(sprintf("Placa: %s", placa));
            disp(sprintf("Entrada: %s", hora_entrada));
            disp(sprintf("Salida: %s", hora_salida));
            disp(sprintf("Tiempo Total: %d horas y %d minutos", horas_totales, minutos_totales));
            disp(sprintf("Cantidad de horas cobradas: %d horas", horas_cobradas));
            disp(sprintf("Monto total a pagar: Q%.2f", monto_total));
            disp("*********************************************");

            % Guardar en facturas.txt
            fid = fopen(FACTURAS_FILE, "a");
            fprintf(fid, "Cliente: %s\n", nombre);
            fprintf(fid, "NIT: %s\n", nit);
            fprintf(fid, "Placa: %s\n", placa);
            fprintf(fid, "Entrada: %s\n", hora_entrada);
            fprintf(fid, "Salida: %s\n", hora_salida);
            fprintf(fid, "Tiempo Total: %d horas y %d minutos\n", horas_totales, minutos_totales);
            fprintf(fid, "Cantidad de horas cobradas: %d horas\n", horas_cobradas);
            fprintf(fid, "Monto: Q%.2f\n", monto_total);
            fprintf(fid, "*********************************************\n");
            fclose(fid);
            disp("Factura guardada exitosamente.");
        catch
            disp("Error al procesar la transacción.");
        end
        pq_close(conn);
    end
end

% Mostrar historial de datos
function mostrar_historial()
    conn = conectar_bd();
    if !isempty(conn)
        try
            query = "SELECT c.nombre, c.nit, c.placa, e.hora_entrada, e.hora_salida, e.tiempo_total_horas, e.monto_total FROM estacionamiento e JOIN clientes c ON e.cliente_id = c.id;";
            registros = pq_exec(conn, query);
            if !isempty(registros)
                for i = 1:size(registros, 1)
                    disp(sprintf("Cliente: %s, NIT: %s, Placa: %s, Entrada: %s, Salida: %s, Tiempo: %.2f horas, Monto: Q%.2f", registros{i, 1}, registros{i, 2}, registros{i, 3}, registros{i, 4}, registros{i, 5}, registros{i, 6}, registros{i, 7}));
                end
            else
                disp("No hay registros en la base de datos.");
            end
        catch
            disp("Error al mostrar el historial.");
        end
        pq_close(conn);
    end
end

% Borrar datos del historial
function borrar_datos()
    conn = conectar_bd();
    if !isempty(conn)
        try
            pq_exec(conn, "DELETE FROM estacionamiento;");
            pq_exec(conn, "DELETE FROM clientes;");
            disp("Datos borrados exitosamente.");
        catch
            disp("Error al borrar los datos.");
        end
        pq_close(conn);
    end
end

% Función principal del programa
function main()
    crear_tablas(); % Crear las tablas al inicio del programa

    while true
        disp("\n--- Menú Principal ---");
        disp("1. Ingreso de datos del usuario.");
        disp("2. Historial de datos.");
        disp("3. Borrado de datos.");
        disp("4. Salir.");

        opcion = input("Seleccione una opción: ", "s");

        switch opcion
            case "1"
                ingresar_datos_usuario();
            case "2"
                mostrar_historial();
            case "3"
                borrar_datos();
            case "4"
                disp("Saliendo del programa...");
                break;
            otherwise
                disp("Opción no válida. Intente nuevamente.");
        end
        if opcion == "4"
            break;
        end
    end
end

main();
