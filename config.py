import os

from dotenv import load_dotenv

load_dotenv()

# Configuration
EXCEL_FILE = 'mtgedit.xlsx'
LOGIN_URL = 'https://store.tcgplayer.com/admin/product/catalog'
USERNAME = os.getenv('TCGPLAYER_USERNAME')
PASSWORD = os.getenv('TCGPLAYER_PASSWORD')

# Check if credentials are loaded
if not USERNAME or not PASSWORD:
	raise ValueError("TCGPlayer credentials not found in .env file. Please check your .env file configuration.")
