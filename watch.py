import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, restart_func):
        self.restart_func = restart_func

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"[WATCH] Change detected in {event.src_path}")
            self.restart_func()

def run_main():
    return subprocess.Popen(["python", "main.py"])

def main_watch_loop():
    print("[DEV] Starting main.py...")
    process = run_main()

    def restart():
        nonlocal process
        print("[DEV] Restarting...")
        process.kill()
        time.sleep(0.5)
        process = run_main()

    observer = Observer()
    handler = ReloadHandler(restart)
    observer.schedule(handler, ".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[DEV] Stopping...")
        observer.stop()
        process.kill()

    observer.join()

if __name__ == "__main__":
    main_watch_loop()
