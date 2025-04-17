import os
from datetime import datetime


def create_log_file():
	"""Create and return the log file path"""
	log_dir = "logs"
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)

	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	log_file = os.path.join(log_dir, f"card_processing_{timestamp}.log")

	# Create the file with a header
	with open(log_file, 'w') as f:
		f.write(f"=== Card Processing Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")

	return log_file


def log_card_status(log_file, card_name, set_name, status, message=""):
	"""Log the status of a card to the log file"""
	try:
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		with open(log_file, 'a') as f:
			log_entry = f"[{timestamp}] {card_name} ({set_name}): {status}"
			if message:
				log_entry += f" - {message}"
			f.write(log_entry + "\n")
		return True
	except Exception as e:
		print(f"Error writing to log file: {e}")
		return False


def log_summary(log_file, total, successful, failed, skipped, non_english, foil):
	"""Log the summary statistics to the log file"""
	try:
		with open(log_file, 'a') as f:
			f.write("\n\n=== Processing Summary ===\n")
			f.write(f"Total cards: {total}\n")
			f.write(f"Successfully processed: {successful}\n")
			f.write(f"Failed to process: {failed}\n")
			f.write(f"Skipped cards (not found): {skipped}\n")
			f.write(f"Non-English cards (skipped): {non_english}\n")
			f.write(f"Foil cards (skipped): {foil}\n")
		return True
	except Exception as e:
		print(f"Error writing summary to log file: {e}")
		return False
