import os
import subprocess

try:
    result = subprocess.run(['cygpath', '-u', '.'], capture_output=True, text=True, check=True)
    print("Cygpath output:", result.stdout)
except subprocess.CalledProcessError as e:
    print("Error running cygpath:", e)
    print("Stderr:", e.stderr)
except FileNotFoundError:
    print("cygpath not found.  Make sure it's in your PATH.")

print("Current working directory:", os.getcwd())
print("Contents of current directory:", os.listdir('.'))