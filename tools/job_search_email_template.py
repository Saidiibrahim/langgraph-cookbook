from langchain.tools import tool
from utils import read_file
from datetime import datetime
from tempfile import TemporaryDirectory
from pathlib import Path
import os

_TEMP_DIRECTORY = TemporaryDirectory()
WORKING_DIRECTORY = Path(_TEMP_DIRECTORY.name)
os.makedirs(WORKING_DIRECTORY, exist_ok=True)

html_template = read_file(
    file_name='job-search-email-template.html',
    bucket_name='test',
    destination=WORKING_DIRECTORY / 'job-search-email-template.html'
)

@tool
def load_job_search_email_template():
    """Use this tool to load the job search email template"""
    try:
        template_path = WORKING_DIRECTORY / 'job-search-email-template.html'
        with open(template_path, 'r') as file:
            html_template = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The HTML template file could not be found. Please ensure the file exists at '{template_path}'.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the HTML template file: {e}")
    return html_template


if __name__ == "__main__":
    html_template = load_job_search_email_template()
    print(html_template)
