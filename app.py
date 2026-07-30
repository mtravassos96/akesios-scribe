from pathlib import Path
import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

def main():
    # Directory to be monitored
    path = Path("audios")
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    while True:
        cmd = input(">")
        if cmd == "q": break

    observer.stop()
    observer.join()

if __name__ == "__main__":
    main()