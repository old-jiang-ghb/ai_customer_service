import os

from dotenv import load_dotenv

load_dotenv(override=True)

# deepseek
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
