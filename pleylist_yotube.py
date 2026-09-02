import os
from pytube import Playlist

def download_playlist_videos():
    # Открываем файл "ссылка.txt" и считываем ссылку на плейлист
    with open("ссылка.txt", "r") as file:
        playlist_url = file.read().strip()

    playlist = Playlist(playlist_url)
    current_directory = os.getcwd()
    output_path = os.path.join(current_directory, "playlist_videos")
    os.makedirs(output_path, exist_ok=True)  # создаем каталог, если его нет
    for video in playlist.videos:
        video.streams.first().download(output_path)

download_playlist_videos()