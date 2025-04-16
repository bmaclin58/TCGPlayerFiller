import pandas as pd

def load_card_data(file_path):
	"""Load card data from Excel file and filter out non-English and foil cards"""
	try:
		df = pd.read_excel(file_path, header=None)
		# Assuming column structure based on your data sample
		df.columns = ['Product Line', 'Set Name', 'Product Name', 'Number', 'Rarity',
		              'Quantity', 'TCG Marketplace Price', 'Foil', 'Language']

		# Filter out non-English cards and foil cards
		filtered_df = df[(df['Language'] == 'English') & (df['Foil'].isna())]

		if filtered_df.empty:
			print("No valid cards found after filtering out non-English and foil cards")
			return None

		print(f"Loaded {len(filtered_df)} valid cards for processing")
		return filtered_df

	except Exception as e:
		print(f"Error loading Excel file: {e}")
		return None
