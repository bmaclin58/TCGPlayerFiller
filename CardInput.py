import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def search_for_card(driver, card_name, set_name):
	"""Search for a card by name and set the Product Line to Magic and Set Name"""
	try:
		# Clear search field and enter card name
		search_field = WebDriverWait(driver, 10).until(
				EC.element_to_be_clickable((By.ID, "SearchValue"))
		)
		search_field.clear()
		search_field.send_keys(card_name)


		# Set Product Line to Magic
		product_line_select = Select(driver.find_element(By.ID, "CategoryId"))
		product_line_select.select_by_visible_text("Magic")

		time.sleep(1)

		# Set the Set Name
		set_select = Select(driver.find_element(By.ID, "SetNameId"))

		# Try to find the correct set by different methods
		found = False

		# First try: Exact match
		try:
			set_select.select_by_visible_text(set_name)
			found = True
		except NoSuchElementException:
			pass


		if not found:
			print(f"Set name '{set_name}' not found. Looking for partial match...")
			options = set_select.options
			for option in options:
				# Skip the "All Set Names" option
				if option.text == "All Set Names":
					continue

				# Try to find a partial match
				if (set_name.lower() in option.text.lower() or
						(set_name.split()[0].lower() in option.text.lower())):
					set_select.select_by_visible_text(option.text)
					print(f"Selected partial match: {option.text}")
					found = True
					break

		if not found:
			# If no match found, just use "All Set Names" and rely on card name search
			print(f"No match found for set: {set_name}. Using 'All Set Names' instead.")
			set_select.select_by_visible_text("All Set Names")


		# Wait for search results
		try:
			WebDriverWait(driver, 10).until(
					EC.presence_of_element_located((By.ID, "inv-actions-wrapper-top"))
			)
			return True
		except TimeoutException:
			print("Search results not found or timed out")
			return False

	except Exception as e:
		print(f"Error searching for card: {e}")
		return False


def process_card(driver, card_data):
	"""Process a single card - get price, set discounted price, and quantity"""
	try:
		# Find the current price
		price_element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-bind='formatCurrency: lowestPrice']"))
		)
		current_price_text = price_element.text.replace('$', '').strip()
		current_price = float(current_price_text)

		# Calculate discounted price (10% off)
		discounted_price = round(current_price * 0.9, 2)

		# Enter the new price
		price_input = driver.find_element(By.CSS_SELECTOR, "input[data-bind*='textInput: newPrice']")
		price_input.clear()
		price_input.send_keys(str(discounted_price))

		# Enter the quantity
		quantity_input = driver.find_element(By.CSS_SELECTOR, "input[data-bind*='textInput: quantity']")
		quantity_input.clear()
		quantity_input.send_keys(str(card_data['Quantity']))

		# Click Save
		save_button = driver.find_element(By.CSS_SELECTOR, "input[value='Save'][data-bind*='click: saveProducts']")
		save_button.click()

		# Wait for save to complete
		time.sleep(2)

		print(
			f"Processed {card_data['Product Name']} - Original price: ${current_price}, New price: ${discounted_price}, Quantity: {card_data['Quantity']}")
		return True

	except Exception as e:
		print(f"Error processing card: {e}")
		return False
