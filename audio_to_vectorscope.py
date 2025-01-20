import librosa
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cv2
from scipy.signal import hilbert
import moviepy.editor as mpe # moviepy==1.0.3

def audio_to_vectorscope(audio_file_vectorscope, audio_file_soundtrack, output_video_file, fps=30, duration=None, width=1920, height=1080):
    """
    Genera un video vectorscopio con audio a partir de dos archivos MP3.

    Args:
        audio_file_vectorscope: Audio para el vectorscopio.
        audio_file_soundtrack: Audio para la banda sonora.
        output_video_file: Ruta del video de salida.
        fps: Cuadros por segundo.
        duration: Duración del video (opcional).
        width: Ancho del video.
        height: Alto del video.
    """

    # 1. Cargar el audio para el vectorscopio (en mono)
    y_vec, sr_vec = librosa.load(audio_file_vectorscope, sr=None, mono=True)  # y_vec: datos de audio, sr_vec: frecuencia de muestreo

    # 2. Calcular la Transformada de Hilbert para obtener la componente imaginaria
    y_hilbert = np.imag(hilbert(y_vec))  #  Necesario para crear el efecto de vectorscopio

    # 3. Crear canales "izquierdo" y "derecho" artificiales (para el efecto visual)
    y_left = y_vec  # Canal izquierdo será la señal original
    y_right = np.roll(y_hilbert, int(sr_vec / 20)) # Canal derecho: Hilbert desfasado para un efecto visual interesante


    # 4. Configurar la figura de Matplotlib
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)  #  Ajustar el tamaño de la figura para la resolución deseada
    ax = plt.Axes(fig, [0., 0., 1., 1.])  # Crear los ejes ocupando toda la figura (sin márgenes)
    ax.set_axis_off()  # Ocultar los ejes
    ax.set_xlim([-0.65, 0.65])  # Límites del vectorscopio (ajusta según la amplitud del audio)
    ax.set_ylim([-0.65, 0.65])
    ax.set_aspect('equal')  # Mantener el aspecto 1:1 para el vectorscopio
    fig.add_axes(ax) # Agregar los ejes a la figura
    line, = ax.plot([], [], color='lime', lw=1) # Inicializar la línea del vectorscopio (color verde lima)
    fig.set_facecolor('black') #  Fondo negro


    # 5. Función de animación (se llama en cada frame)
    def animate(i):  # i es el número de frame actual
        start_sample = int(i * sr_vec / fps)  # Calcular la muestra de inicio para este frame
        end_sample = int((i + 1) * sr_vec / fps)  # Calcular la muestra final para este frame
        x = y_left[start_sample:end_sample]  # Datos para el eje x del vectorscopio
        y_plot = y_right[start_sample:end_sample] # Datos para el eje y del vectorscopio
        line.set_data(x, y_plot) # Actualizar los datos de la línea del vectorscopio
        return line,  # Devolver la línea actualizada


    # 6. Calcular el número total de frames de la animación
    if duration:
        num_frames = int(duration * fps) #  Si se especifica una duración, usarla para calcular frames
    else:
        num_frames = int(len(y_vec) * fps / sr_vec) # Si no, calcular frames según la longitud del audio



    # 7. Crear la animación
    ani = animation.FuncAnimation(fig, animate, frames=num_frames, interval=1000 / fps, blit=True) # blit=True para optimización

    # 8. Guardar la animación como un video temporal (sin audio)
    temp_video_file = "temp_video.mp4" 
    FFMpegWriter = animation.writers['ffmpeg']
    writer = FFMpegWriter(fps=fps, metadata=dict(artist='Me'), bitrate=1800)  # bitrate para controlar la calidad
    ani.save(temp_video_file, writer=writer)  # Guardar el video temporal


    # 9. Cargar el video temporal y el audio de la banda sonora con Moviepy
    video_clip = mpe.VideoFileClip(temp_video_file) # Cargar el video temporal
    audio_clip = mpe.AudioFileClip(audio_file_soundtrack) # Cargar el audio de la banda sonora

    # 10. Combinar el video y el audio, y guardar el video final
    final_video = video_clip.set_audio(audio_clip) #  Añadir el audio al video
    final_video.write_videofile(output_video_file, codec="libx264", audio_codec="aac") # Guardar el video final (codecs para compatibilidad)


    # 11. Eliminar el archivo de video temporal
    import os  
    os.remove(temp_video_file)  # Limpiar el archivo temporal



# Ejemplo de uso (reemplaza con tus archivos de audio)
audio_to_vectorscope("audio.mp3", "audio.mp3", "vectorscopio_con_audio.mp4")