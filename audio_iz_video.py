import os
from moviepy.editor import VideoFileClip

def extract_audio_from_videos():
    # Создаем папку для сохранения аудиофайлов, если её еще нет
    if not os.path.exists('extracted_audio'):
        os.makedirs('extracted_audio')

    # Получаем текущую директорию
    current_directory = os.getcwd()

    # Перебираем все файлы в текущей директории
    for filename in os.listdir(current_directory):
        filepath = os.path.join(current_directory, filename)
        if os.path.isfile(filepath) and filename.endswith('.mp4'):
            try:
                # Извлекаем аудиодорожку из видео
                video = VideoFileClip(filepath)
                audio = video.audio
                audio_filepath = os.path.join('extracted_audio', f'{os.path.splitext(filename)[0]}.mp3')
                # Сохраняем аудио в формате MP3
                audio.write_audiofile(audio_filepath)
                print(f"Аудиодорожка из {filename} успешно извлечена и сохранена в {audio_filepath}")
            except Exception as e:
                print(f"Ошибка при обработке {filename}: {str(e)}")

if __name__ == "__main__":
    extract_audio_from_videos()