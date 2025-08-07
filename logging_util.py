import logging
import time

logger = logging.getLogger("reading-writing-searching-automation-logger")
logger.setLevel(logging.INFO)

# log line formatter
formatter = logging.Formatter('%(asctime)s: [%(levelname)s]: %(message)s')

# handler for log file
file_handler = logging.FileHandler('reading_writing_searching'+str(time.time())+'.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# handler for stdout
stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)
