import random
import time

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import LOGIN_URL, PASSWORD, USERNAME


def setup_driver():
	"""Set up and return a configured Chrome WebDriver using undetected-chromedriver"""
	try:
		options = uc.ChromeOptions()
		options.add_argument("--window-size=1920,1080")

		# Do not add the --headless flag as it makes detection more likely

		driver = uc.Chrome(options=options,use_subprocess=False)
		driver.maximize_window()
		return driver

	except ImportError:
		print("undetected_chromedriver not installed. Install with: pip install undetected-chromedriver")
		# Fall back to regular selenium
		return setup_regular_driver()


def setup_regular_driver():
	"""Set up and return a configured Chrome WebDriver"""
	chrome_options = Options()
	chrome_options.add_argument("--window-size=1920,1080")

	service = Service(ChromeDriverManager().install())
	driver = webdriver.Chrome(service=service, options=chrome_options)
	driver.maximize_window()
	return driver


def login(driver):
	"""Login to TCGPlayer admin page"""
	driver.get(LOGIN_URL)

	# Wait for the login form to appear
	try:
		# Check if we're already logged in by looking for a common element on the dashboard
		try:
			already_logged_in = WebDriverWait(driver, 5).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, "#sellerportal-navigation-app-container"))
			)
			print("Already logged in!")
			return True
		except TimeoutException:
			# Not logged in, proceed with login
			pass

		username_field = WebDriverWait(driver, 30).until(
				EC.presence_of_element_located((By.ID, "tcg-input-7"))
		)
		password_field = driver.find_element(By.ID, "tcg-input-10")

		captcha_detected = driver.find_elements(By.CSS_SELECTOR,
		                                        ".g-recaptcha, .recaptcha, iframe[title*='recaptcha'], iframe[src*='recaptcha']")
		if captcha_detected:
			handle_captcha(driver)
			print("CAPTCHA solved, continuing with login...")

		username_field.send_keys(USERNAME)
		password_field.send_keys(PASSWORD)

		login_button = driver.find_element(By.CLASS_NAME, "tcg-standard-button")
		login_button.click()

		# Wait for the page to load after login
		WebDriverWait(driver, 30).until(
				EC.url_contains("admin/product/catalog")
		)
		print("Login successful!")
	except TimeoutException:
		print("Login page elements not found or timed out.")
		return False
	except Exception as e:
		print(f"Login failed: {e}")
		return False

	return True


def handle_captcha(driver):
	"""Pauses execution and waits for user to manually solve CAPTCHA"""
	try:
		print("\n\n=== CAPTCHA DETECTED! ===")
		print("Please solve the CAPTCHA in the browser window.")
		input("Press Enter once you've solved the CAPTCHA to continue...")
		return True
	except Exception as e:
		print(f"Error checking for CAPTCHA: {e}")

	return False


def humanize_actions(driver):
	"""Adds random mouse movements to seem more human-like"""
	try:
		# Random mouse movements
		actions = ActionChains(driver)
		for _ in range(3):
			x, y = random.randint(100, 700), random.randint(100, 500)
			actions.move_by_offset(x, y)
			actions.pause(random.uniform(0.1, 0.5))
		actions.perform()

		# Random delay
		time.sleep(random.uniform(1, 3))
	except Exception as e:
		print(f"Error during humanized actions: {e}")
