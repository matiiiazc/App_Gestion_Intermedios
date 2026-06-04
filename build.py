import os

os.system(
    """
    pyinstaller
    --noconfirm
    --windowed
    --onedir
    --name AplicacionIntermedios
    main.py
    """
)

print("Compilación finalizada")