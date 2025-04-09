import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get environment setting
env = os.getenv("ENV", "python").lower()  # Default to "python" unless explicitly "local"

def error_display():
    output = f"Python Version: {sys.version}\n"

    # Check Virtual Environment
    venv = os.environ.get("VIRTUAL_ENV")
    output += f"Virtual Environment: {venv}" if venv else "No Virtual Environment Active"

    # Print to stderr if local, otherwise normal print
    if env == "local":
        print(output, file=sys.stderr)
    else:
        print(output)

# Call function to test output

