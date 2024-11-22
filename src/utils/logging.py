import os
from datetime import datetime

def log_it(log_message, log_type="INFO", log_path="./logs/main2.log", init=False):
    """
    Logs a message to a specified file.
    
    Parameters:
        log_message (str): The message to log.
        log_type (str): The type of log (e.g., INFO, ERROR, WARNING).
        log_path (str): The file path for the log file.
        init (bool): Whether to initialize (clear) the log file.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Initialize the log file if requested
    if init:
        with open(log_path, "a") as log_file:
            log_file.write(f"\n{'#' * 50}\n")
            log_file.write(f"New run at {timestamp}\n")
            log_file.write(f"{'#' * 50}\n")
        return

    # Append log message to the file
    log_entry = f"[{log_type}] {timestamp}: {log_message}\n"
    
    try:
        with open(log_path, "a") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"Error writing to log file: {e}")
