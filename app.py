import os
import time
import requests

from dotenv import load_dotenv
from flask import Flask, request, jsonify




# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()


imgflip_ai_url = "https://api.imgflip.com/ai_meme"
imgflip_username = os.getenv("IMGFLIP_USERNAME")
imgflip_password = os.getenv("IMGFLIP_PASSWORD")

