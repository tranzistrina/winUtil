import os
from pytube import YouTube

def download_video(url):
    yt = YouTube(url)
    current_directory = os.getcwd()
    output_path = os.path.join(current_directory, "videos")
    os.makedirs(output_path, exist_ok=True)  # создаем каталог, если его нет
    yt.streams.first().download(output_path)

def download_playlist_videos():
    # Открываем файл "ссылка.txt" и считываем ссылку на видео
    with open("ссылка.txt", "r") as file:
        video_url = file.read().strip()

    download_video(video_url)

download_playlist_videos()