"""Runs the analyses in order (each step reads the results of the previous ones)."""
import glob
import os
import subprocess
import sys

aqui = os.path.dirname(os.path.abspath(__file__))
for script in sorted(glob.glob(os.path.join(aqui, '0*.py'))):
    print(f'\n=== {os.path.basename(script)} ===', flush=True)
    subprocess.run([sys.executable, '-X', 'utf8', script], cwd=aqui, check=True)
