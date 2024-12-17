import os
from datetime import datetime

class Logger:
    def __init__(self, log_path: str, init: bool = False, clear: bool = False):
        """
        Initialize the Logger with a specific log file path.

        Args:
            log_path (str): Path to the log file.
            init (bool): Whether to initialize a new run header. Default is False.
            clear (bool): Whether to clear the log file on initialization. Default is False.
        """
        self.log_path = log_path
        # Ensure the log directory exists
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

        # Clear the log file if requested
        if clear:
            self._clear_log()

        # Initialize new run header if requested
        if init:
            self._write_header()

    def _write_header(self):
        """Writes a header indicating a new run."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = "\n" + "=" * 40 + f"\nNew Run at {timestamp}\n" + "=" * 40 + "\n"
        self._write_to_log(header)

    def _clear_log(self):
        """Clears the content of the log file."""
        try:
            with open(self.log_path, "w") as f:
                f.write("")
        except IOError as e:
            print(f"Error clearing log file: {e}")

    def _write_to_log(self, log_entry: str):
        """Writes a log entry to the log file."""
        try:
            with open(self.log_path, "a") as f:
                f.write(log_entry)
        except IOError as e:
            print(f"Logging Error: {e}")

    def info(self, message: str):
        """Logs an informational message."""
        self._log_message(message, "INFO")

    def warning(self, message: str):
        """Logs a warning message."""
        self._log_message(message, "WARNING")

    def error(self, message: str):
        """Logs an error message."""
        self._log_message(message, "ERROR")

    def _log_message(self, message: str, level: str):
        """Formats and writes the log message to the log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{level}] {message} || {timestamp}\n"
        self._write_to_log(log_entry)

# Example usage
# if __name__ == "__main__":
#     logger = Logger("logs/app.log", init=True, clear=True)
#     logger.info("Application started")
#     logger.warning("This is a warning message")
#     logger.error("This is an error message")
