import pandas as pd
import os
from datetime import datetime


def load_card_data(file_path):
	"""Load card data from Excel file and prepare for processing"""
	try:
		# Create a backup of the original file
		if os.path.exists(file_path):
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			backup_path = f"{os.path.splitext(file_path)[0]}_{timestamp}_backup.xlsx"
			backup_df = pd.read_excel(file_path)
			backup_df.to_excel(backup_path, index=False)
			print(f"Created backup at {backup_path}")

		df = pd.read_excel(file_path, header=None)
		# Assuming column structure based on your data sample
		df.columns = ['Product Line', 'Set Name', 'Product Name', 'Number', 'Rarity',
		              'Quantity', 'TCG Marketplace Price', 'Foil', 'Language']

		# Add status column if it doesn't exist
		if 'Status' not in df.columns:
			df['Status'] = ''

		# Save the updated DataFrame back to the Excel file
		df.to_excel(file_path, index=False)

		print(f"Loaded {len(df)} cards for processing")
		return df

	except Exception as e:
		print(f"Error loading Excel file: {e}")
		return None


def update_card_status(file_path, index, status):
	"""Update the status of a card in the Excel file"""
	try:
		df = pd.read_excel(file_path)
		df.at[index, 'Status'] = status
		df.to_excel(file_path, index=False)
		return True
	except Exception as e:
		print(f"Error updating card status in Excel: {e}")
		return False
