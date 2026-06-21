import requests
import time
import logging

URL = "https://blue-a7ca.onrender.com/Account/login/"
INTERVAL = 300  # 5 minutes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

while True:
    try:
        response = requests.get(URL, timeout=60)
        if response.status_code == 200:
            logging.info(f"Ping successful — status {response.status_code}")
        else:
            logging.warning(f"Unexpected status code: {response.status_code}")
    except requests.exceptions.Timeout:
        logging.error("Request timed out")
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    time.sleep(INTERVAL)