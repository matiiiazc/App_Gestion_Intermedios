import os
import shutil
import tkinter as tk

from tkinter import (
    filedialog,
    messagebox
)

APP_NAME = "Aplicacion_Intermedios"

root = tk.Tk()
root.withdraw()

destino_base = filedialog.askdirectory(
    title="Seleccione carpeta"
)

if not destino_base:
    exit()

destino = os.path.join(
    destino_base,
    APP_NAME
)

os.makedirs(destino, exist_ok=True)

os.makedirs(
    os.path.join(destino, "database"),
    exist_ok=True
)

os.makedirs(
    os.path.join(destino, "certs"),
    exist_ok=True
)

os.makedirs(
    os.path.join(destino, "logs"),
    exist_ok=True
)

os.makedirs(
    os.path.join(destino, "backups"),
    exist_ok=True
)

messagebox.showinfo(
    "Instalación",
    f"Instalado en:\n{destino}"
)