import logging

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# обработчик для DEBUG
debug_handler = logging.FileHandler('debug.log', encoding='utf-8')
debug_handler.setLevel(logging.DEBUG)

# обработчик для INFO
info_handler = logging.FileHandler('info.log', encoding='utf-8')
info_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
debug_handler.setFormatter(formatter)
info_handler.setFormatter(formatter)

logger.addHandler(debug_handler)
logger.addHandler(info_handler)