% Definición de las categorías
bajoPeso = "Bajo peso";
pesoNormal = "Peso normal";
sobrePeso = "Sobrepeso";

while true
    % Mostrar las opciones disponibles al usuario
    disp("---------Opciones disponibles:---------");
    disp("1. Calcular IMC y mostrar resultados");
    disp("2. Leer información de un registro");
    disp("3. Borrar información de un registro");
    disp("4. Salir del programa");
    disp("---------------------------------------");
    % Leer la opción del usuario
    opcion = input("Ingrese la opción deseada: ");

    % Validar la opción
    if ~(1 <= opcion && opcion <= 4)
        disp("Opción no válida. Intente de nuevo.");
        continue;
    end

    if opcion == 1
        nombre = input("Ingrese su nombre: ", "s");
        peso = input("Ingrese su peso en kilogramos: ");
        altura = input("Ingrese su altura en metros: ");

        % Validar peso y altura
        if peso == 0 || altura == 0
            disp("Peso y altura no válidos, no es posible procesar el IMC.");
            continue;
        end

        % Calcular IMC
        imc = peso / (altura ^ 2);

        % Determinar la categoría
        if imc < 18.5
            categoria = bajoPeso;
        elseif imc < 24.9
            categoria = pesoNormal;
        else
            categoria = sobrePeso;
        end

        % Mostrar resultados
        fprintf("\nNombre: %s\n", nombre);
        fprintf("IMC: %.2f\n", imc);
        fprintf("Categoría: %s\n", categoria);

        % Guardar en archivo
        fid = fopen('imc.txt', 'a');
        fprintf(fid, "Nombre: %s, IMC: %.2f, Categoría: %s\n", nombre, imc, categoria);
        fclose(fid);

        disp("Información guardada en 'imc.txt'.");

    elseif opcion == 2
        if exist('imc.txt', 'file') == 2
            fid = fopen('imc.txt', 'r');
            contenido = textscan(fid, '%s', 'Delimiter', '\n');
            fclose(fid);

            if isempty(contenido{1})
                disp("El archivo está vacío, ingrese un registro.");
                continue;
            end

            nombre_buscado = input("Ingrese el nombre del registro que desea leer: ", "s");
            encontrado = false;

            for i = 1:length(contenido{1})
                if ~isempty(strfind(contenido{1}{i}, nombre_buscado))
                    fprintf("\nRegistro encontrado:\n%s\n", contenido{1}{i});
                    encontrado = true;
                    break;
                end
            end

            if ~encontrado
                fprintf("No se encontró ningún registro con el nombre '%s'.\n", nombre_buscado);
            end
        else
            disp("No se encontró el archivo 'imc.txt'.");
        end

    elseif opcion == 3
        if exist('imc.txt', 'file') == 2
            fid = fopen('imc.txt', 'r');
            contenido = textscan(fid, '%s', 'Delimiter', '\n');
            fclose(fid);

            if isempty(contenido{1})
                disp("El archivo está vacío, ingrese un registro.");
                continue;
            end

            nombre_buscado = input("Ingrese el nombre del registro que desea borrar: ", "s");
            encontrado = false;
            lineas_nuevas = {};

            for i = 1:length(contenido{1})
                if isempty(strfind(contenido{1}{i}, nombre_buscado))
                    lineas_nuevas{end+1} = contenido{1}{i};
                else
                    fprintf("Registro encontrado y eliminado:\n%s\n", contenido{1}{i});
                    encontrado = true;
                end
            end

            fid = fopen('imc.txt', 'w');
            for i = 1:length(lineas_nuevas)
                fprintf(fid, "%s\n", lineas_nuevas{i});
            end
            fclose(fid);

            if ~encontrado
                fprintf("No se encontró ningún registro con el nombre '%s'.\n", nombre_buscado);
            end
        else
            disp("No se encontró el archivo 'imc.txt'.");
        end

    elseif opcion == 4
        disp("¡Gracias por usar el programa!");
        break;
    end
end
