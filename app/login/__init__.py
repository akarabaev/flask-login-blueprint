import os
from pathlib import Path

from flask import Blueprint


current_file_directory = Path(os.path.abspath(__file__)).parent

template_folder = os.path.join(current_file_directory, 'templates')
static_folder = os.path.join(current_file_directory, 'static')


bp = Blueprint('login_bp', __name__, template_folder=template_folder, static_folder=static_folder, static_url_path="/static_login")

from .routes import *