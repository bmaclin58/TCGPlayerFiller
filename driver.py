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

from config import LOGIN_URL


def setup_driver():
	"""Set up and return a configured Chrome WebDriver using undetected-chromedriver"""
	try:
		options = uc.ChromeOptions()
		options.add_argument("--window-size=1920,1080")

		# Do not add the --headless flag as it makes detection more likely

		driver = uc.Chrome(options=options, use_subprocess=False)
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
	"""Login with explicit manual intervention for reliability"""
	driver.get(LOGIN_URL)

	try:
		# Check if already logged in
		try:
			already_logged_in = WebDriverWait(driver, 5).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, "#sellerportal-navigation-app-container"))
			)
			print("Already logged in!")
			return True
		except TimeoutException:
			# Not logged in, continue with manual login
			pass

		print("\n=== MANUAL LOGIN REQUIRED ===")
		print("1. Please log in manually in the browser window.")
		print("2. Use your TCGPlayer credentials.")
		print("3. Solve any CAPTCHA if present.")
		input("Press Enter once you've logged in to continue...")

		# Verify successful login
		try:
			WebDriverWait(driver, 10).until(
					EC.url_contains("admin/product/catalog")
			)
			print("Login successful!")
			return True
		except TimeoutException:
			print("Login verification failed. Please make sure you're properly logged in.")
			return False

	except Exception as e:
		print(f"Login process error: {e}")
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
