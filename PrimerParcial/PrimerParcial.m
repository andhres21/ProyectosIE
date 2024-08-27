pkg load database

% Función para conectar a la base de datos PostgreSQL
function conn = conectar_bd()
  conn = pq_connect(setdbopts('dbname', 'bd_andhres', 'host', 'localhost', 'port', '5432', 'user', 'andhres', 'password', 'abc123'));
endfunction

% Función para crear las tablas si no existen
function crear_tablas(conn)
  query = [
    "CREATE TABLE IF NOT EXISTS menuPrecios ("
    "combustible VARCHAR(50) PRIMARY KEY, "
    "precio_por_litro NUMERIC(10, 2) NOT NULL);"
  ];
  pq_exec_params(conn, query);

  query = [
    "CREATE TABLE IF NOT EXISTS menuGasolinera ("
    "id SERIAL PRIMARY KEY, "
    "nombre VARCHAR(100) NOT NULL, "
    "identificacion VARCHAR(50) NOT NULL, "
    "combustible VARCHAR(50) NOT NULL REFERENCES menuPrecios(combustible), "
    "litros NUMERIC(10, 2) NOT NULL, "
    "monto_total NUMERIC(10, 2) NOT NULL);"
  ];
  pq_exec_params(conn, query);
endfunction

% Función para inicializar los precios de los combustibles
function inicializar_precios_combustibles(conn)
  precios = struct("Regular", 36.90, "Premium", 28.80, "Diesel", 30.50);
  fields = fieldnames(precios);
  for i = 1:length(fields)
    combustible = fields{i};
    precio = precios.(combustible);
    query = sprintf([
      "INSERT INTO menuPrecios (combustible, precio_por_litro) VALUES ('%s', %.2f) "
      "ON CONFLICT (combustible) DO UPDATE SET precio_por_litro = EXCLUDED.precio_por_litro;"
    ], combustible, precio);
    pq_exec_params(conn, query);
  endfor
endfunction

% Función para obtener los precios de todos los combustibles
function precios = obtener_precios_combustibles(conn)
  query = "SELECT combustible, precio_por_litro FROM menuPrecios;";
  Datos = pq_exec_params(conn, query);
  precios = struct();
  for i = 1:size(Datos, 1)
    combustible = Datos{i, 1};
    precio = Datos{i, 2};
    precios.(combustible) = precio;
  endfor
endfunction

% Función para obtener el precio de un tipo de combustible
function precio = obtener_precio_combustible(conn, tipo_combustible)
  query = sprintf("SELECT precio_por_litro FROM menuPrecios WHERE combustible = '%s';", tipo_combustible);
  Datos = pq_exec_params(conn, query);
  if size(Datos, 1) > 0
    precio = Datos{1, 1};
  else
    disp(['El combustible ', tipo_combustible, ' no está disponible.']);
    precio = NaN;
  endif
endfunction

% Función para guardar los datos del cliente
function guardar_datos_cliente(conn, nombre, identificacion, combustible, litros, monto_total)
  query = sprintf([
    "INSERT INTO menuGasolinera (nombre, identificacion, combustible, litros, monto_total) "
    "VALUES ('%s', '%s', '%s', %.2f, %.2f);"
  ], nombre, identificacion, combustible, litros, monto_total);
  pq_exec_params(conn, query);

  % Guardar en archivo de texto
  fid = fopen('facturas.txt', 'a');
  fprintf(fid, 'Nombre: %s, Identificación: %s, Combustible: %s, Litros: %.2f, Monto Total: Q%.2f\n', ...
          nombre, identificacion, combustible, litros, monto_total);
  fclose(fid);
endfunction

% Función para mostrar todos los registros
function mostrar_registros(conn)
  query = "SELECT * FROM menuGasolinera;";
  Datos = pq_exec_params(conn, query);
  if size(Datos, 1) > 0
    disp('Registros en la base de datos:');
    for i = 1:size(Datos, 1)
      disp(sprintf('ID: %d, Nombre: %s, Identificación: %s, Combustible: %s, Litros: %.2f, Monto Total: Q%.2f', ...
                   Datos{i, 1}, Datos{i, 2}, Datos{i, 3}, Datos{i, 4}, Datos{i, 5}, Datos{i, 6}));
    endfor
  else
    disp('No hay registros en la base de datos.');
  endif
endfunction

% Función principal
function main()
  conn = conectar_bd();
  crear_tablas(conn);
  inicializar_precios_combustibles(conn);

  while true
    nombre = input('Ingrese su nombre: ', 's');
    identificacion = input('Ingrese su número de placa: ', 's');

    precios_combustibles = obtener_precios_combustibles(conn);

    disp('Elija el tipo de combustible que desea.');
    keys = fieldnames(precios_combustibles);
    for i = 1:numel(keys)
      disp(sprintf('%d. %s - Q%.2f', i, keys{i}, precios_combustibles.(keys{i})));
    endfor

    opcion_combustible = input('Ingrese el número de su opción: ');

    if opcion_combustible >= 1 && opcion_combustible <= numel(keys)
      tipo_combustible = keys{opcion_combustible};
    else
      disp('Opción no válida.');
      continue;
    endif

    precio_por_litro = obtener_precio_combustible(conn, tipo_combustible);
    if isnan(precio_por_litro)
      continue;
    endif

    litros = input('Ingrese la cantidad en litros a despachar: ');
    if litros <= 0
      disp('La cantidad de litros debe ser mayor a cero.');
      continue;
    endif

    monto_total = litros * precio_por_litro;
    disp(sprintf('El monto total a pagar por %.2f litros de %s es: Q%.2f', litros, tipo_combustible, monto_total));

    guardar_datos_cliente(conn, nombre, identificacion, tipo_combustible, litros, monto_total);

    while true
      disp('¿Qué desea hacer a continuación?');
      disp('1. Ver todos los registros');
      disp('2. Continuar con el próximo cliente');
      disp('3. Salir del programa');

      opcion = input('Ingrese el número de su opción: ');

      if opcion == 1
        mostrar_registros(conn);
      elseif opcion == 2
        break; % Salir del bucle interno para continuar con el próximo cliente
      elseif opcion == 3
        pq_close(conn);
        disp('Conexión con PostgreSQL cerrada.');
        return; % Salir del programa
      else
        disp('Opción no válida.');
      endif
    endwhile
  endwhile
endfunction

% Ejecutar la función principal
main()
