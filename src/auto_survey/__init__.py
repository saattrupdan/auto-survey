"""Automated literature surveys."""

import logging

from dotenv import load_dotenv
from termcolor import colored

from auto_survey.utils import suppress_logging

fmt = colored("%(message)s", "light_yellow")
logging.basicConfig(level=logging.INFO, format=fmt)

load_dotenv(dotenv_path=".env")
