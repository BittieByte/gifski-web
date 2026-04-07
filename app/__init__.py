from flask import Flask

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

import app.routes
