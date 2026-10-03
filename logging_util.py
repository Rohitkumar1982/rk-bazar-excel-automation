import logging
import time

# Log file name matches the previous pattern: reading_writing_searching<timestamp>.log
log_file = "reading_writing_searching" + str(time.time()) + ".log"

logger = logging.getLogger("excel_automation")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(log_file, encoding="UTF-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
