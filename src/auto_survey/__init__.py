"""Automated literature surveys."""

import logging

from dotenv import load_dotenv
from termcolor import colored

fmt = f"[%(asctime)s]\n{colored('%(message)s', 'light_yellow')}\n"
logging.basicConfig(level=logging.INFO, format=fmt, datefmt="%Y-%m-%d %H:%M:%S")

load_dotenv(dotenv_path=".env")
