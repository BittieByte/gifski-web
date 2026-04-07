from flask import Flask
import os

app = Flask(__name__)

# Get project root (/app in Docker)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Absolute uploads path
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

import app.routes
