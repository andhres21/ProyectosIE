% Comprueba si estamos ejecutando en MATLAB o en Octave
if (exist('OCTAVE_VERSION', 'builtin') ~= 0)
% Estamos en Octave
  pkg load signal;
end
% Menu principal
opcion = 0;
while opcion ~= 5
  % Menu de opciones
  disp('Seleccione una opcion:')
  disp('1. Grabar')
  disp('2. Reproducir')
  disp('3. Graficar')
  disp('4. Graficar densidad')
  disp('5. Salir')
  opcion = input('Ingrese su eleccién: ');
    switch opcion
      case 1
        %Grabacion de audio
        try
          duracion = input('Ingrese la duracién de la grabacién en segundos: ');
          disp('Comenzando la grabacién...');
          recObj = audiorecorder;
          recordblocking(recObj, duracion);
          disp('Grabacion finalizada.');
          data = getaudiodata(recObj);
          audiowrite('audio.wav', data, recObj.SampleRate);
          disp('Archivo de audio grabado correctamente.');
        catch
          disp('Error al grabar el audio.');
        end
      case 2
        % Reproduccién de audio
        try
          [data, fs] = audioread('audio.wav');
          sound(data, fs);
        catch
          disp('Error al reproducir el audio.');
        end
      case 3
        % Grafico de audio
        try
          [data, fs] = audioread('audio.wav');
          tiempo = linspace(0, length(data)/fs, length(data));
          plot(tiempo, data);
          xlabel('Tiempo (s)');
          ylabel('Amplitud');
          title('Audio');
        catch
          disp('Error al graficar el audio.');
        end
      case 4
        % Graficando espectro de frecuencia
      try
        disp('Graficando espectro de frecuencia...');
        [audio, Fs] = audioread('audio.wav'); % Lee la senal desde el archivo .wav
        N = length(audio); % Numero de muestras de la senal
        f = linspace(0, Fs/2, N/2+1); % Vector de frecuencias
        ventana = hann(N); %reducir el efecto de las discontinuidades al calcular la FFT
        Sxx = pwelch(audio, ventana, 0, N, Fs); % Densidad espectral de potencia
        plot(f, 10*log10(Sxx(1:N/2+1))); % Grafica el espectro de frecuencia en dB
        xlabel('Frecuencia (Hz)');
        ylabel('Densidad espectral de potencia (dB/Hz)');
        title('Espectro de frecuencia de la sefial grabada');
      catch
        disp('Error al graficar el audio.');
      end
      case 5
      % Salir
        disp('Saliendo del programa...');
      otherwise
        disp('Opcion no valida.');
    end
  end
