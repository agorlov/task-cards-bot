import os
import time
import json
import logging
from queue import Queue
from threading import Thread

def process_voice(meta_data, wav_path):
    print(f"Обработка: {wav_path} с метаданными: {meta_data}")
    # Возможный код, который может вызвать исключение
    # if "error" in meta_data:
    #     raise ValueError("Симуляция ошибки обработки")

def scan_and_enqueue(directory, queue):
    processed = set()
    while True:
        files = os.listdir(directory)
        json_files = [f for f in files if f.endswith('.json')]
        for json_file in json_files:
            wav_file = json_file.replace('.json', '.wav')
            if wav_file in files:
                pair = (json_file, wav_file)
                if pair not in processed:
                    queue.put(pair)
                    processed.add(pair)
        time.sleep(1)

def process_queue(directory, queue, done_directory):
    while True:
        json_file, wav_file = queue.get()
        json_path = os.path.join(directory, json_file)
        wav_path = os.path.join(directory, wav_file)
        try:
            with open(json_path, 'r') as f:
                json_data = json.load(f)
            process_voice(json_data, wav_path)
            os.rename(json_path, os.path.join(done_directory, json_file))
            os.rename(wav_path, os.path.join(done_directory, wav_file))
        except Exception as e:
            logging.error(f"Ошибка при обработке {json_path} и {wav_path}: {e}")
        finally:
            queue.task_done()

def main():
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    directory_to_watch = "voice_inbound"
    directory_done = "voice_done"
    if not os.path.exists(directory_done):
        os.mkdir(directory_done)

    queue = Queue()
    scanner_thread = Thread(target=scan_and_enqueue, args=(directory_to_watch, queue))
    processor_thread = Thread(target=process_queue, args=(directory_to_watch, queue, directory_done))

    scanner_thread.start()
    processor_thread.start()

    scanner_thread.join()
    processor_thread.join()

if __name__ == "__main__":
    main()
