import speedtest
import time

def measure_speed():
    st = speedtest.Speedtest()
    # Измеряем скорость загрузки
    download_speed = st.download() / 1_000_000  # в мегабитах в секунду
    # Измеряем скорость отправки
    upload_speed = st.upload() / 1_000_000  # в мегабитах в секунду
    return download_speed, upload_speed

while True:
    try:
        download_speed, upload_speed = measure_speed()
        print(f"Скорость загрузки: {download_speed:.2f} Mbps")
        print(f"Скорость отправки: {upload_speed:.2f} Mbps")
        print("-" * 20)
    except speedtest.ConfigRetrievalError:
        print("Не удается получить доступ к настройкам Speedtest.net. Пожалуйста, проверьте подключение к интернету.")
    except speedtest.NoMatchedServers:
        print("Не удалось найти сервер для тестирования скорости. Пожалуйста, попробуйте еще раз позже.")
    time.sleep(5)  # пауза в 5 секунд перед следующим измерением