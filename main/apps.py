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
            while True:
                try:
                    # Ping your Render site
                    requests.get(
                        "https://blue-a7ca.onrender.com/Account/login/", 
                        timeout=30
                    )
                    print("✅ Ping sent! Site is alive.")
                except Exception as e:
                    print(f"❌ Ping failed: {e}")
                
                # Wait 5 minutes (300 seconds) before next ping
                time.sleep(300)
        
        # Start the background thread
        # 'daemon=True' means it stops when Django stops
        thread = threading.Thread(target=ping_loop, daemon=True)
        thread.start()
        print("🚀 Keep-alive thread started!")