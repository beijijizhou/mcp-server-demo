

import os
import sys
# /Users/hongzhonghu/Library/Logs/Claude
def debug():
    print(f"Python Version: {sys.version}",file=sys.stderr)

    # Print Virtual Environment (if any)
    venv = os.environ.get("VIRTUAL_ENV")
    if venv:
        print(f"Virtual Environment: {venv}",file=sys.stderr)
    else:
        print("No Virtual Environment Active", file=sys.stderr)