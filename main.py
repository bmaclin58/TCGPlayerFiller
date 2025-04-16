import os
import time

import pandas as pd
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from CardInput import process_card, search_for_card
from Cardhandler import load_card_data
from config import EXCEL_FILE
from driver import login, setup_driver


def main():
	# Load card data
	cards_df = load_card_data(EXCEL_FILE)
	if cards_df is None:
		print("Failed to load card data. Exiting.")
		return

	# Setup driver and login
	driver = setup_driver()
	try:
		if not login(driver):
			print("Login failed. Exiting.")
			driver.quit()
			return

		# Navigate to the product catalog page if not already there
		if "admin/product/catalog" not in driver.current_url:
			driver.get("https://store.tcgplayer.com/admin/product/catalog")
			# Wait for the page to load
			WebDriverWait(driver, 20).until(
					EC.presence_of_element_located((By.ID, "SearchValue"))
			)

		# Create separate lists for successful cards and skipped/failed cards
		successful_cards = []
		failed_cards = []
		skipped_cards = []
		non_english_cards = []
		foil_cards = []

		# Process each card
		for index, card in cards_df.iterrows():
			try:
				print(f"\nProcessing card {index + 1}/{len(cards_df)}: {card['Product Name']} ({card['Set Name']})")

				# Skip non-English cards
				if card['Language'] != 'English':
					print(f"Skipping non-English card: {card['Product Name']} ({card['Language']})")
					non_english_cards.append(f"{card['Product Name']} ({card['Language']})")
					continue

				# Skip foil cards
				if not pd.isna(card['Foil']) and card['Foil'].strip():
					print(f"Skipping foil card: {card['Product Name']}")
					foil_cards.append(card['Product Name'])
					continue

				# Search for the card
				search_attempt = 0
				search_success = False

				while search_attempt < 3 and not search_success:
					search_success = search_for_card(driver, card['Product Name'], card['Set Name'])
					if not search_success:
						search_attempt += 1
						print(f"Retrying search (attempt {search_attempt}/3)...")
						time.sleep(2)  # Wait before retrying

				if search_success:
					# Process the card
					process_attempt = 0
					process_success = False

					while process_attempt < 3 and not process_success:
						process_success = process_card(driver, card)
						if not process_success:
							process_attempt += 1
							print(f"Retrying processing (attempt {process_attempt}/3)...")
							time.sleep(2)  # Wait before retrying

					if process_success:
						successful_cards.append(card['Product Name'])
					else:
						failed_cards.append(card['Product Name'])
						print(f"Failed to process card after {process_attempt} attempts: {card['Product Name']}")
				else:
					skipped_cards.append(card['Product Name'])
					print(f"Failed to find card after {search_attempt} attempts: {card['Product Name']}")

				# Return to the catalog page for the next card
				driver.get("https://store.tcgplayer.com/admin/product/catalog")
				# Wait for the page to load
				WebDriverWait(driver, 20).until(
						EC.presence_of_element_located((By.ID, "SearchValue"))
				)

			except Exception as e:
				print(f"Unexpected error processing card {card['Product Name']}: {e}")
				failed_cards.append(card['Product Name'])

				# Try to recover and continue with the next card
				try:
					driver.get("https://store.tcgplayer.com/admin/product/catalog")
					WebDriverWait(driver, 20).until(
							EC.presence_of_element_located((By.ID, "SearchValue"))
					)
				except:
					print("Failed to recover. Restarting browser...")
					driver.quit()
					driver = setup_driver()
					if not login(driver):
						print("Login failed during recovery. Exiting.")
						break

		# Print summary
		print("\n=== Processing Summary ===")
		print(f"Total cards: {len(cards_df)}")
		print(f"Successfully processed: {len(successful_cards)}")
		print(f"Failed to process: {len(failed_cards)}")
		print(f"Skipped cards (not found): {len(skipped_cards)}")
		print(f"Non-English cards (skipped): {len(non_english_cards)}")
		print(f"Foil cards (skipped): {len(foil_cards)}")

		if failed_cards:
			print("\nFailed cards:")
			for card in failed_cards:
				print(f"- {card}")

		if skipped_cards:
			print("\nSkipped cards:")
			for card in skipped_cards:
				print(f"- {card}")

		if non_english_cards:
			print("\nNon-English cards (to process manually):")
			for card in non_english_cards:
				print(f"- {card}")

		if foil_cards:
			print("\nFoil cards (to process manually):")
			for card in foil_cards:
				print(f"- {card}")

	finally:
		# Always close the browser, even if there's an error
		driver.quit()


if __name__ == "__main__":
	main()
