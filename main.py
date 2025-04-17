import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from CardInput import process_card, search_for_card
from Cardhandler import load_card_data
from config import EXCEL_FILE
from driver import login, setup_driver
from card_logger import create_log_file, log_card_status, log_summary


def update_excel_status(df, index, status):
	"""Update the status column in the Excel file"""
	try:
		# If 'Status' column doesn't exist, add it
		if 'Status' not in df.columns:
			df['Status'] = ""

		# Update the status for this card
		df.at[index, 'Status'] = status

		# Save the updated dataframe back to Excel
		df.to_excel(EXCEL_FILE, index=False)
		return True
	except Exception as e:
		print(f"Error updating Excel file: {e}")
		return False


def main():
	# Create log file
	log_file = create_log_file()

	# Load card data
	cards_df = load_card_data(EXCEL_FILE)
	if cards_df is None:
		print("Failed to load card data. Exiting.")
		return

	# If 'Status' column doesn't exist, add it
	if 'Status' not in cards_df.columns:
		cards_df['Status'] = ""

	# Setup driver and login
	driver = setup_driver()
	try:
		if not login(driver):
			print("Login failed. Exiting.")
			log_card_status(log_file, "SYSTEM", "SYSTEM", "ERROR", "Login failed")
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

				# Skip already processed cards (if they have a status)
				if 'Status' in cards_df.columns and not pd.isna(card['Status']) and card['Status'] != "":
					print(f"Skipping already processed card: {card['Product Name']} (Status: {card['Status']})")

					# Add to appropriate list based on existing status
					if card['Status'] == "SUCCESS":
						successful_cards.append(card['Product Name'])
					elif card['Status'] == "FAILED":
						failed_cards.append(card['Product Name'])
					elif card['Status'] == "SKIPPED":
						skipped_cards.append(card['Product Name'])
					elif card['Status'] == "NON-ENGLISH":
						non_english_cards.append(f"{card['Product Name']} ({card['Language']})")
					elif card['Status'] == "FOIL":
						foil_cards.append(card['Product Name'])

					continue

				# Skip non-English cards
				if card['Language'] != 'English':
					print(f"Skipping non-English card: {card['Product Name']} ({card['Language']})")
					non_english_cards.append(f"{card['Product Name']} ({card['Language']})")
					log_card_status(log_file, card['Product Name'], card['Set Name'], "NON-ENGLISH",
					                f"Language: {card['Language']}")
					update_excel_status(cards_df, index, "NON-ENGLISH")
					continue

				# Skip foil cards
				if not pd.isna(card['Foil']) and card['Foil'].strip():
					print(f"Skipping foil card: {card['Product Name']}")
					foil_cards.append(card['Product Name'])
					log_card_status(log_file, card['Product Name'], card['Set Name'], "FOIL")
					update_excel_status(cards_df, index, "FOIL")
					continue

				# Search for the card
				search_success = search_for_card(driver, card['Product Name'], card['Set Name'])

				if not search_success:
					print(f"Failed to find card: {card['Product Name']}")
					print("You can now manually open the screen and press 'P' to proceed or 'Q' to skip this card.")

					log_card_status(log_file, card['Product Name'], card['Set Name'], "SEARCH_FAILED",
					                "Waiting for manual intervention")

					while True:
						user_input = input("Press 'P' to continue or 'Q' to skip: ").strip().lower()
						if user_input == 'p':
							print(f"Continuing with manual intervention for card: {card['Product Name']}")
							search_success = True
							log_card_status(log_file, card['Product Name'], card['Set Name'], "MANUAL_INTERVENTION",
							                "Proceeding after manual search")
							break
						elif user_input == 'q':
							print(f"Skipping card: {card['Product Name']}")
							skipped_cards.append(card['Product Name'])
							log_card_status(log_file, card['Product Name'], card['Set Name'], "SKIPPED",
							                "User chose to skip")
							update_excel_status(cards_df, index, "SKIPPED")
							break  # Just break from the while loop, not return
						else:
							print("Invalid input. Please press 'P' or 'Q'.")

					if user_input == 'q':
						continue  # Skip to the next card instead of returning

				if search_success:
					# Process the card
					process_attempt = 0
					process_success = False

					while process_attempt < 3 and not process_success:
						process_success = process_card(driver, card)
						if not process_success:
							process_attempt += 1
							print(f"Retrying processing (attempt {process_attempt}/3)...")
							log_card_status(log_file, card['Product Name'], card['Set Name'], "RETRY",
							                f"Attempt {process_attempt}/3")
							time.sleep(2)  # Wait before retrying

					if process_success:
						successful_cards.append(card['Product Name'])
						log_card_status(log_file, card['Product Name'], card['Set Name'], "SUCCESS")
						update_excel_status(cards_df, index, "SUCCESS")
					else:
						failed_cards.append(card['Product Name'])
						print(f"Failed to process card after {process_attempt} attempts: {card['Product Name']}")
						log_card_status(log_file, card['Product Name'], card['Set Name'], "FAILED",
						                f"After {process_attempt} attempts")
						update_excel_status(cards_df, index, "FAILED")

				# Return to the catalog page for the next card
				driver.get("https://store.tcgplayer.com/admin/product/catalog")
				# Wait for the page to load
				WebDriverWait(driver, 20).until(
						EC.presence_of_element_located((By.ID, "SearchValue"))
				)

			except Exception as e:
				print(f"Unexpected error processing card {card['Product Name']}: {e}")
				failed_cards.append(card['Product Name'])
				log_card_status(log_file, card['Product Name'], card['Set Name'], "ERROR", str(e))
				update_excel_status(cards_df, index, "FAILED")

				# Try to recover and continue with the next card
				try:
					driver.get("https://store.tcgplayer.com/admin/product/catalog")
					WebDriverWait(driver, 20).until(
							EC.presence_of_element_located((By.ID, "SearchValue"))
					)
				except:
					print("Failed to recover. Restarting browser...")
					log_card_status(log_file, "SYSTEM", "SYSTEM", "ERROR", "Failed to recover, restarting browser")
					driver.quit()
					driver = setup_driver()
					if not login(driver):
						print("Login failed during recovery. Exiting.")
						log_card_status(log_file, "SYSTEM", "SYSTEM", "ERROR", "Login failed during recovery")
						break

		# Log summary to file
		log_summary(log_file, len(cards_df), len(successful_cards), len(failed_cards),
		            len(skipped_cards), len(non_english_cards), len(foil_cards))

		# Print summary
		print("\n=== Processing Summary ===")
		print(f"Total cards: {len(cards_df)}")
		print(f"Successfully processed: {len(successful_cards)}")
		print(f"Failed to process: {len(failed_cards)}")
		print(f"Skipped cards (not found): {len(skipped_cards)}")
		print(f"Non-English cards (skipped): {len(non_english_cards)}")
		print(f"Foil cards (skipped): {len(foil_cards)}")
		print(f"Log file created at: {log_file}")

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
