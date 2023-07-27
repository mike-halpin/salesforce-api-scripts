import logging

def get_logger(module_name, file_name="Log %(asctime)s.log"):
    # Create a logger
    logger = logging.getLogger(module_name)
    # Set the log level
    logger.setLevel(logging.DEBUG)

    # Create a console handler
    console_handler = logging.StreamHandler()
    # Set the level for this handler
    console_handler.setLevel(logging.DEBUG)
    # Create a formatter and set the formatter for the console handler.
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    # Add the console handler to the logger
    logger.addHandler(console_handler)
    
    # Create a file handler
    file_handler = logging.FileHandler(file_name)
    # Set the level for this handler
    file_handler.setLevel(logging.DEBUG)
    # Create a formatter and set the formatter for the file handler.
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger

