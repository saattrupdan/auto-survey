"""Automated literature surveys."""

import logging
import warnings

import litellm
from dotenv import load_dotenv
from termcolor import colored

# Suppress debug info from all other loggers than ours
litellm.suppress_debug_info = True
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
logger_names_to_ignore = [
    logger
    for logger in logging.root.manager.loggerDict.keys()
    if logger != "auto_survey"
] + ["weasyprint"]
for logging_name in logger_names_to_ignore:
    logging.getLogger(logging_name).setLevel(logging.CRITICAL)

fmt = colored("%(message)s", "light_yellow")
logging.basicConfig(level=logging.INFO, format=fmt)

load_dotenv(dotenv_path=".env")
