"""Redraw the homepage picture of the Court Decisions database (map of decisions by
country, split by court level and outcome) from the data being published, so its
numbers are never behind the data. See tools/home_cases.py."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
subprocess.run([sys.executable, os.path.join(ROOT, "tools", "home_cases.py"), os.path.join(ROOT, "site")], check=True)
