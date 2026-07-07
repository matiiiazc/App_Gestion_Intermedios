import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--windowed",
    "--onedir",
    "--name", "AplicacionIntermedios",
    "main.py"
])

print("Compilación finalizada")