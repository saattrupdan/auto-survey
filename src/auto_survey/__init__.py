"""Automated literature surveys."""

import logging
import os

from dotenv import load_dotenv
from termcolor import colored

fmt = colored("%(message)s", "light_yellow")
logging.basicConfig(level=logging.INFO, format=fmt)

load_dotenv(dotenv_path=".env")

os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = "/opt/local/lib:$DYLD_FALLBACK_LIBRARY_PATH"
