import sys
import os

# Determine the path for openssl.conf based on whether it's running from the executable or source code
if getattr(sys, 'frozen', False):  # If running from the bundled executable
    config_path = os.path.join(sys._MEIPASS, 'thu_learn_downloader', 'openssl.conf')
else:
    config_path = os.path.join(os.path.dirname(__file__), 'thu_learn_downloader', 'openssl.conf')

# Now you can use config_path to load the openssl.conf file
print(f"Config file path: {config_path}")
os.environ['OPENSSL_CONF'] = config_path