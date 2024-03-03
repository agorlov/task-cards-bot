"""
Скрипт скачивает бинарные файлы моделей в директорию ./models
"""


from faster_whisper import WhisperModel


# Run on GPU with FP16
#model = WhisperModel(model_size, device="cuda", compute_type="float16")

model = WhisperModel("small", device="cpu", compute_type="int8", download_root="./models")

segments, info = model.transcribe("voice_task_425709869.ogg", beam_size=5, language='ru')

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))



print("Теперь скачаем среднюю модель:")

model = WhisperModel("medium", device="cpu", compute_type="int8", download_root="./models")

segments, info = model.transcribe("voice_task_425709869.ogg", beam_size=5, language='ru')

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
