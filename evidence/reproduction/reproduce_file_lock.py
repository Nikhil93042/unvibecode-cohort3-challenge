import os
import sys
import time
import threading
from pathlib import Path

test_dir = Path(r"C:\Users\HP\Downloads\unvibecode-cohort3\evidence\reproduction")
test_dir.mkdir(parents=True, exist_ok=True)
target_file = test_dir / "shipreadyv2_pass1_full_results.jsonl"
target_file.write_text('{"request_id": "test_init"}\n', encoding="utf-8")

stop_event = threading.Event()
collision_detected = []

def reader_thread():
    # Simulates customer_runner.py: read_jsonl_quiet polling the results file
    while not stop_event.is_set():
        try:
            if target_file.is_file():
                _ = target_file.read_text(encoding="utf-8").splitlines()
        except Exception:
            pass
        time.sleep(0.005)

def writer_thread():
    # Simulates 03_shipreadyv2_pass1_full_runner.py: atomic_write_text
    temporary = target_file.with_suffix(target_file.suffix + ".tmp")
    for i in range(100):
        if stop_event.is_set():
            break
        text = f'{{"request_id": "req_{i}", "status": "completed"}}\n'
        temporary.write_text(text, encoding="utf-8", newline="\n")
        try:
            temporary.replace(target_file)
        except PermissionError as e:
            collision_detected.append((i, str(e)))
            print(f"[REPRODUCED] Attempt {i}: PermissionError caught: {e}")
            break
        time.sleep(0.01)
    stop_event.set()

t_reader = threading.Thread(target=reader_thread)
t_writer = threading.Thread(target=writer_thread)

t_reader.start()
t_writer.start()

t_writer.join()
stop_event.set()
t_reader.join()

if collision_detected:
    print(f"\nSUCCESSFULLY REPRODUCED: Caught {len(collision_detected)} collision(s).")
    print(f"Error detail: {collision_detected[0]}")
else:
    print("No collision occurred in this sample run.")
