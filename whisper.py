from whispercpp import Whisper

w = Whisper('small')

result = w.transcribe("voice_task_425709869.ogg")
text = w.extract_text(result)
print(text)
