# from django.apps import AppConfig


# class MainConfig(AppConfig):
#     name = 'main'

import requests
import threading
import time
from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        """This runs automatically when Django starts - no user needed"""

        def ping_loop():
            """This function runs forever in the background"""
            urls = [
                "https://blue-25bdc.containers.snapdeploy.app/Account/login/",
                "https://blue-25bdc.containers.snapdeploy.app/Task/ads-health-check/",
                "https://blue-25bdc.containers.snapdeploy.app/Withdraw/withdraw-health-check/",
                "https://blue-25bdc.containers.snapdeploy.app/Account/login-health-check/",
            ]

            while True:
                for url in urls:
                    try:
                        requests.get(url, timeout=30)
                        print(f"✅ Ping sent: {url}")
                    except Exception as e:
                        print(f"❌ Ping failed: {url} — {e}")

                time.sleep(65)  # every 1 minute and 5 seconds

        thread = threading.Thread(target=ping_loop, daemon=True)
        thread.start()
        print("🚀 Keep-alive thread started!")