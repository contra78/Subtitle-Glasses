import tkinter as tk
import numpy as np
import threading
import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer


model = Model("vosk-model-small-en-us-0.15")


q = queue.Queue()


def recognize_speech_in_background():
    recognizer = KaldiRecognizer(model, 16000)

    def callback(indata, frames, time, status):
        if status:
            print(f"SoundDevice Status: {status}", flush=True)
        
        # Convert indata to a numpy array, ensuring it's in the correct format
        indata_bytes = np.frombuffer(indata, dtype=np.int16).tobytes()

        if recognizer.AcceptWaveform(indata_bytes):
            result = recognizer.Result()
            text = json.loads(result).get('text', '')
            q.put(text)
        else:
            partial_result = recognizer.PartialResult()
            partial_text = json.loads(partial_result).get('partial', '')
            q.put(partial_text)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            sd.sleep(1000)


# ฟังก์ชันอัปเดตข้อความใน UI
def update_text(text_output):
    try:
        while True:
            text = q.get_nowait()
            text_output.set(text)  # อัปเดตข้อความใน UI
    except queue.Empty:
        pass
    root.after(100, update_text, text_output)  # เรียกใช้ตัวเองซ้ำทุกๆ 100 ms

# สร้างหน้าต่าง GUI
root = tk.Tk()
root.title("Real-time Speech Recognition")
root.geometry("400x200")

# สร้างพื้นที่แสดงผลข้อความ
text_output = tk.StringVar()
label = tk.Label(root, textvariable=text_output, wraplength=350, justify="left")
label.pack(pady=20)

# เริ่มการฟังเสียงแบบ real-time
threading.Thread(target=recognize_speech_in_background, daemon=True).start()

# อัปเดตข้อความใน UI แบบ real-time
root.after(100, update_text, text_output)

# เริ่มต้นการทำงานของ GUI
root.mainloop()
