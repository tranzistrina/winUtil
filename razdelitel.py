import os
from moviepy.video.io.VideoFileClip import VideoFileClip

def split_video(video_path, output_dir, segment_duration=5):
    clip = VideoFileClip(video_path)
    total_duration = clip.duration
    
    # Определяем количество сегментов
    num_segments = int(total_duration / (segment_duration * 60)) + 1
    
    for i in range(num_segments):
        start_time = i * segment_duration * 60
        end_time = min((i + 1) * segment_duration * 60, total_duration)
        segment = clip.subclip(start_time, end_time)
        output_path = os.path.join(output_dir, f'segment_{i}.mp4')
        segment.write_videofile(output_path)
        print(f'Segment {i} created: {output_path}')

def main():
    input_dir = os.getcwd()  # Текущая директория
    output_dir = os.path.join(input_dir, 'segments')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    video_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and f.endswith('.mp4')]
    
    for video_file in video_files:
        video_path = os.path.join(input_dir, video_file)
        split_video(video_path, output_dir)

if __name__ == "__main__":
    main()
