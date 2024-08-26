import sounddevice as sd
import numpy as np
import wave
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import welch

def grabar_audio(duracion, archivo):
    fs = 44100  # Frecuencia de muestreo
    print("Comenzando la grabación...")
    audio = sd.rec(int(duracion * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()  # Espera a que la grabación termine
    print("Grabación finalizada.")
    # Guardar el archivo de audio
    audio = np.array(audio)
    audio = np.squeeze(audio)
    with wave.open(archivo, 'w') as wf:
        wf.setnchannels(1)  # Canal mono
        wf.setsampwidth(2)  # 16 bits por muestra
        wf.setframerate(fs)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    print(f"Archivo de audio grabado correctamente como {archivo}.")

def reproducir_audio(archivo):
    try:
        # Leer archivo WAV
        fs, data = wavfile.read(archivo)
        sd.play(data, fs)
        sd.wait()  # Espera a que la reproducción termine
    except Exception as e:
        print(f"Error al reproducir el audio: {e}")

def graficar_audio(archivo):
    try:
        fs, data = wavfile.read(archivo)
        tiempo = np.linspace(0, len(data) / fs, num=len(data))
        plt.figure()
        plt.plot(tiempo, data)
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.title('Audio')
        plt.show()
    except Exception as e:
        print(f"Error al graficar el audio: {e}")

def graficar_densidad(archivo):
    try:
        fs, data = wavfile.read(archivo)
        f, Pxx = welch(data, fs, window='hann', nperseg=len(data))
        plt.figure()
        plt.semilogy(f, Pxx)
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Densidad espectral de potencia (dB/Hz)')
        plt.title('Espectro de frecuencia del audio grabado')
        plt.show()
    except Exception as e:
        print(f"Error al graficar la densidad espectral: {e}")

def menu():
    opcion = 0
    archivo = 'audio.wav'
    while opcion != 5:
        print("Seleccione una opción:")
        print("1. Grabar")
        print("2. Reproducir")
        print("3. Graficar")
        print("4. Graficar densidad")
        print("5. Salir")
        try:
            opcion = int(input("Ingrese su elección: "))
            if opcion == 1:
                duracion = int(input("Ingrese la duración de la grabación en segundos: "))
                grabar_audio(duracion, archivo)
            elif opcion == 2:
                reproducir_audio(archivo)
            elif opcion == 3:
                graficar_audio(archivo)
            elif opcion == 4:
                graficar_densidad(archivo)
            elif opcion == 5:
                print("Saliendo del programa...")
            else:
                print("Opción no válida.")
        except ValueError:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()