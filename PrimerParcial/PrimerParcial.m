pkg load database

% Función para conectar a la base de datos PostgreSQL
function conn = conectar_bd()
    conn = pq_connect(setdbopts('dbname', 'bd_andhres', 'host', 'localhost', 'port', '5432', 'user', 'andhres', 'password', 'abc123'));
endfunction

% Función para crear las tablas si no existen
function crear_tablas(conn)
    pq_exec_params(conn, "CREATE TABLE IF NOT EXISTS menuPrecios (combustible VARCHAR(50) PRIMARY KEY, precio_por_litro NUMERIC(10, 2) NOT NULL);");
    pq_exec_params(conn, "CREATE TABLE IF NOT EXISTS menuGasolinera (id SERIAL PRIMARY KEY, nombre VARCHAR(100) NOT NULL, identificacion VARCHAR(50) NOT NULL, combustible VARCHAR(50) NOT NULL REFERENCES menuPrecios(combustible), litros NUMERIC(10, 2) NOT NULL, monto_total NUMERIC(10, 2) NOT NULL);");
endfunction

% Función para actualizar los precios de los combustibles en la base de datos
function inicializar_precios_combustibles(conn)
        pq_exec_params(conn, "UPDATE menuPrecios SET precio_por_litro = 36.90 WHERE combustible = 'Regular';");
        pq_exec_params(conn, "UPDATE menuPrecios SET precio_por_litro = 30.70 WHERE combustible = 'Premium';");
        pq_exec_params(conn, "UPDATE menuPrecios SET precio_por_litro = 34.20 WHERE combustible = 'Diesel';");
endfunction

% Función para obtener los precios de todos los combustibles
function precios = obtener_precios_combustibles(conn)
    resultados = pq_exec_params(conn, "SELECT combustible, CAST(precio_por_litro AS FLOAT) FROM menuPrecios;");
    precios = {};
    for i = 1:rows(resultados)
        campo = char(resultados{i, 1});
        precios.(campo) = resultados{i, 2}; % Asignación directa utilizando paréntesis
    endfor
endfunction



% Función para obtener el precio de un tipo de combustible desde la tabla menuPrecios
function precio = obtener_precio_combustible(conn, tipo_combustible)
    resultados = pq_exec_params(conn, "SELECT precio_por_litro FROM menuPrecios WHERE combustible = $1;", {tipo_combustible});
    if isempty(resultados)
        disp(["El combustible ", tipo_combustible, " no está disponible."]);
        precio = NaN;
    else
        precio = resultados{1, 1};
    endif
endfunction

% Función para guardar los datos del cliente en la tabla menuGasolinera y en un archivo de texto
function guardar_datos_cliente(conn, nombre, identificacion, combustible, litros, monto_total)
    pq_exec_params(conn, "INSERT INTO menuGasolinera (nombre, identificacion, combustible, litros, monto_total) VALUES ($1, $2, $3, $4, $5);", {nombre, identificacion, combustible, litros, monto_total});

    precio_por_litro = obtener_precio_combustible(conn, combustible);
    if isnan(precio_por_litro)
        return;
    endif

    % Guardar en archivo de texto
    archivo = fopen("facturas.txt", "a");
    fprintf(archivo, "NOMBRE DEL CLIENTE: %s\n", nombre);
    fprintf(archivo, "IDENTIFICACIÓN DEL VEHÍCULO: %s\n", identificacion);
    fprintf(archivo, "TIPO DE COMBUSTIBLE: %s\n", combustible);
    fprintf(archivo, "CANTIDAD DE LITROS: %.2f\n", litros);
    fprintf(archivo, "PRECIO POR LITRO: Q%.2f\n", precio_por_litro);
    fprintf(archivo, "MONTO TOTAL A PAGAR: Q%.2f\n", monto_total);
    fprintf(archivo, "\n********************************************\n\n");
    fclose(archivo);
endfunction

% Función para mostrar todos los registros ingresados
function mostrar_registros(conn)
    resultados2 = pq_exec_params(conn, "SELECT * FROM menuGasolinera;");
    if isempty(resultados2)
        disp("No hay registros en la base de datos.");
    else
        disp("\nRegistros en la base de datos:");
        for i = 1:rows(resultados2)
            fprintf("ID: %d, Nombre: %s, Identificación: %s, Combustible: %s, Litros: %.2f, Monto Total: Q%.2f\n", resultados2{i, 1}, resultados2{i, 2}, resultados2{i, 3}, resultados2{i, 4}, resultados2{i, 5}, resultados2{i, 6});
        endfor
    endif
endfunction

% Función para eliminar un registro mediante identificación
function eliminar_registro(conn, identificacion)
    pq_exec_params(conn, "DELETE FROM menuGasolinera WHERE identificacion = $1;", {identificacion});
    if pq_affected_rows(conn) > 0
        disp(["Registro con identificación ", identificacion, " eliminado exitosamente."]);
    else
        disp(["No se encontró ningún registro con identificación ", identificacion, "."]);
    endif
endfunction

% Función principal
function main()
    % Conexión a la base de datos
    conn = conectar_bd();

    % Crear las tablas si no existen
    crear_tablas(conn);

    % Ingresar los precios de los combustibles
    inicializar_precios_combustibles(conn);

    while true
        % Solicitar datos del usuario
        nombre = input("Ingrese su nombre: ", "s");
        identificacion = input("Ingrese su número de placa: ", "s");

        % Obtener precios actualizados
        precios_combustibles = obtener_precios_combustibles(conn);

        % Menú de combustibles
        disp("Elija el tipo de combustible que desea.");
        combustibles = fieldnames(precios_combustibles);
        for i = 1:length(combustibles)
            fprintf("%d. %s - Q%.2f\n", i, combustibles{i}, precios_combustibles.(combustibles{i}));
        endfor

        opcion_combustible = input("Ingrese el número de su opción: ");

        if opcion_combustible > 0 && opcion_combustible <= length(combustibles)
            tipo_combustible = combustibles{opcion_combustible};
        else
            disp("Opción no válida.");
            continue;
        endif

        % Obtener el precio del combustible elegido
        precio_por_litro = obtener_precio_combustible(conn, tipo_combustible);
        if isnan(precio_por_litro)
            continue;
        endif

        % Solicitar cantidad de litros
        litros = input("Ingrese la cantidad en litros a despachar: ");
        if litros <= 0
            disp("La cantidad de litros debe ser mayor a cero.");
            continue;
        endif

        % Calcular el monto total
        monto_total = litros * precio_por_litro;

        % Mostrar el monto total a pagar
        fprintf("El monto total a pagar por %.2f litros de %s es: Q%.2f\n", litros, tipo_combustible, monto_total);

        % Guardar los datos del cliente en la base de datos y en un archivo
        guardar_datos_cliente(conn, nombre, identificacion, tipo_combustible, litros, monto_total);

        while true
            disp("\n¿Qué desea hacer a continuación?");
            disp("1. Ver todos los registros");
            disp("2. Continuar con el próximo cliente");
            disp("3. Eliminar registro mediante identificación");
            disp("4. Salir del programa");

            opcion = input("Ingrese el número de su opción: ");

            if opcion == 1
                mostrar_registros(conn);
            elseif opcion == 2
                break;  % Salir del bucle interno para continuar con el próximo cliente
            elseif opcion == 3
                identificacion_a_eliminar = input("Ingrese la placa del vehículo cuyo registro desea eliminar: ", "s");
                eliminar_registro(conn, identificacion_a_eliminar);
            elseif opcion == 4
                pq_close(conn);
                disp("Conexión con PostgreSQL cerrada.");
                return;  % Salir del programa
            else
                disp("Opción no válida.");
            endif
        endwhile
    endwhile
endfunction

% Ejecutar el programa
main();

