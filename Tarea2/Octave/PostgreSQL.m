#Comandos para conectarse
pkg load database
conn = pq_connect(setdbopts('dbname','bd_andhres', 'host', 'localhost','port',
                            '5432', 'user', 'andhres', 'password', 'abc123'));
disp("Conexión con PostgreSQL abierta.");
#------------------------------------------------------------------------------
#Comando para ingresar valores
pq_exec_params(conn, "INSERT INTO redes (nombre, carnet) VALUES ('BENJAMIN', 2000);");
#------------------------------------------------------------------------------
#Comando para eliminar valores
pq_exec_params(conn, "DELETE FROM redes WHERE carnet = 2023;");
#------------------------------------------------------------------------------
#Comando para actualizar valores
pq_exec_params(conn, "UPDATE redes SET nombre = 'JULISA' WHERE nombre = 'CARLOS';");
#------------------------------------------------------------------------------
#Comando para visualizar valores
Datos = pq_exec_params(conn, "SELECT * FROM redes;");
disp("Datos de la tabla 'redes':");
disp(Datos);
#------------------------------------------------------------------------------
#Comando para desconectarse
pq_close(conn);
disp("Conexión con PostgreSQL cerrada.");



