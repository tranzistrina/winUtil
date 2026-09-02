import cv2
import os
import glob
import re
import tkinter as tk
from tkinter import filedialog
from natsort import natsorted
import sys

def natural_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def sorted_naturally(list_of_paths):
    try:
        return natsorted(list_of_paths)
    except Exception:
        return sorted(list_of_paths, key=natural_key)

def load_frame_paths(folder, pattern="igra_*.png"):
    search = os.path.join(folder, pattern)
    paths = glob.glob(search)
    paths = sorted_naturally(paths)
    return paths

def preload_frames(paths):
    frames = []
    for p in paths:
        img = cv2.imread(p)
        if img is None:
            print(f"Warning: не удалось загрузить {p}")
            continue
        frames.append(img)
    return frames

def export_video(frames, out_path, fps):
    if not frames:
        raise ValueError("Нет кадров для записи.")
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, float(fps), (w, h))
    for f in frames:
        if len(f.shape) == 2:
            f_bgr = cv2.cvtColor(f, cv2.COLOR_GRAY2BGR)
        else:
            f_bgr = f
        writer.write(f_bgr)
    writer.release()
    print("Экспорт завершён:", out_path)

WINDOW_NAME = "Просмотр кадров — Управление: Space Пауза/Воспроизв., ←/→ шаг, v Экспорт, q Выход"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
folder = os.getcwd()
frame_pattern = "igra_*.png"
fps_val = 10
paused = False

def choose_folder_dialog():
    root = tk.Tk()
    root.withdraw()
    f = filedialog.askdirectory(initialdir=folder)
    root.destroy()
    return f

def main():
    global folder, fps_val, paused
    print("Откройте папку с кадрами (например igra_1.png, igra_2.png ...).")
    print("Если хотите выбрать папку — нажмите 'o' в окне просмотра, либо перед запуском установите переменную folder в коде.")
    folder = choose_folder_dialog() or folder
    frame_paths = load_frame_paths(folder, frame_pattern)
    if not frame_paths:
        print(f"В папке {folder} не найдено файлов по шаблону {frame_pattern}.")
        return
    print(f"Найдено {len(frame_paths)} кадров. Загружаем в память...")
    frames = preload_frames(frame_paths)
    if not frames:
        print("Не удалось загрузить ни одного кадра.")
        return
    total = len(frames)
    max_fps = 60
    init_fps = min(max(1, fps_val), max_fps)
    def nothing(x): pass
    cv2.createTrackbar("FPS", WINDOW_NAME, init_fps, max_fps, nothing)
    cv2.createTrackbar("Frame", WINDOW_NAME, 0, total-1, nothing)
    idx = 0
    while True:
        tb_fps = cv2.getTrackbarPos("FPS", WINDOW_NAME)
        if tb_fps < 1: tb_fps = 1
        tb_frame = cv2.getTrackbarPos("Frame", WINDOW_NAME)
        if tb_frame != idx:
            idx = tb_frame
            paused = True
        frame = frames[idx]
        disp = frame.copy()
        text = f"{idx+1}/{total}  FPS:{tb_fps}  Folder:{os.path.basename(folder)}"
        cv2.putText(disp, text, (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1, cv2.LINE_AA)
        cv2.imshow(WINDOW_NAME, disp)
        delay_ms = int(1000.0 / tb_fps) if not paused else 30
        key = cv2.waitKey(delay_ms) & 0xFF
        if not paused:
            idx += 1
            if idx >= total: idx = 0
            cv2.setTrackbarPos("Frame", WINDOW_NAME, idx)
        if key == ord(' '):
            paused = not paused
            print("Paused" if paused else "Play")
        elif key == ord('q') or key == 27:
            print("Выход.")
            break
        elif key == ord('v'):
            out_name = os.path.join(folder, "igra_video_export.mp4")
            export_fps = tb_fps
            print(f"Экспорт видео в {out_name} с fps={export_fps} ...")
            try:
                export_video(frames, out_name, export_fps)
            except Exception as e:
                print("Ошибка при экспорте:", e)
        elif key == ord('o'):
            newf = choose_folder_dialog()
            if newf:
                folder = newf
                frame_paths = load_frame_paths(folder, frame_pattern)
                if not frame_paths:
                    print("Ничего не найдено в выбранной папке.")
                else:
                    frames = preload_frames(frame_paths)
                    total = len(frames)
                    cv2.destroyWindow(WINDOW_NAME)
                    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                    cv2.createTrackbar("FPS", WINDOW_NAME, init_fps, max_fps, nothing)
                    cv2.createTrackbar("Frame", WINDOW_NAME, 0, total-1, nothing)
                    idx = 0
                    paused = True
                    print(f"Загружено {total} кадров из {folder}.")
        elif key == 81 or key == ord('a'):
            paused = True
            idx = (idx - 1) % total
            cv2.setTrackbarPos("Frame", WINDOW_NAME, idx)
        elif key == 83 or key == ord('d'):
            paused = True
            idx = (idx + 1) % total
            cv2.setTrackbarPos("Frame", WINDOW_NAME, idx)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
