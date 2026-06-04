import os
import shutil
from datetime import datetime


# ==== CONFIGURACION ====
VERSION_NUEVA = "1.0.1"

PROTEGIDOS = {
    "database",   # nunca se toca
    "backups",    # nunca se toca
    "logs",       # nunca se toca
    "certs",      # nunca se toca
}

BASE          = os.path.dirname(os.path.abspath(__file__))
UPDATE_FOLDER = os.path.join(BASE, "update_files")
VERSION_FILE  = os.path.join(BASE, "version.txt")
DB_PATH       = os.path.join(BASE, "database", "intermedios.db")
BACKUPS_DIR   = os.path.join(BASE, "backups")


# ==== FUNCIONES ====

def version_actual() -> str:
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, encoding="utf-8") as f:
            return f.read().strip()
    return "desconocida"


def crear_backup():
    if not os.path.exists(DB_PATH):
        return
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    fecha   = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(BACKUPS_DIR, f"intermedios_{fecha}.db")
    shutil.copy2(DB_PATH, destino)
    print(f"Backup creado: {destino}")


def actualizar():
    if not os.path.exists(UPDATE_FOLDER):
        print(f"No se encontró la carpeta update_files en:\n{UPDATE_FOLDER}")
        return

    print(f"Version actual : {version_actual()}")
    print(f"Version nueva  : {VERSION_NUEVA}")
    print("Haciendo backup de la base de datos...")
    crear_backup()

    print("Copiando archivos nuevos...")
    for item in os.listdir(UPDATE_FOLDER):

        # ==== NUNCA TOCAR CARPETAS PROTEGIDAS ====
        if item in PROTEGIDOS:
            print(f"  [OMITIDO] {item}")
            continue

        origen  = os.path.join(UPDATE_FOLDER, item)
        destino = os.path.join(BASE, item)

        if os.path.isdir(origen):
            shutil.copytree(origen, destino, dirs_exist_ok=True)
            print(f"  [CARPETA] {item}")
        else:
            shutil.copy2(origen, destino)
            print(f"  [ARCHIVO] {item}")

    # ==== ACTUALIZAR VERSION ====
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(VERSION_NUEVA)

    print(f"\nActualizacion finalizada — version {VERSION_NUEVA}")


if __name__ == "__main__":
    actualizar()