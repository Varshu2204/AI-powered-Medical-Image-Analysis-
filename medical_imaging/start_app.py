import subprocess
import os

script_path = os.path.join(os.path.dirname(__file__), "medical.py")
subprocess.run(["streamlit", "run", script_path])