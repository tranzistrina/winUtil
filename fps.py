import os
from moviepy.editor import VideoFileClip

def decrease_fps(input_file, output_file, target_fps):
    clip = VideoFileClip(input_file)
    new_clip = clip.set_fps(target_fps)
    new_clip.write_videofile(output_file, audio=True)

def main():
    # Чтение желаемого FPS из файла
    with open('fps.txt', 'r') as file:
        target_fps = int(file.readline().strip())

    directory = os.getcwd()  # Текущая директория
    
    for file in os.listdir(directory):
        if file.endswith(".mp4"):
            input_file = os.path.join(directory, file)
            output_file = os.path.join(directory, f"{os.path.splitext(file)[0]}-fps.mp4")
            decrease_fps(input_file, output_file, target_fps)
            print(f"Успешно обработан файл: {file}")

if __name__ == "__main__":
    main()