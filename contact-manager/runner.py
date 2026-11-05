"""
Puente entre la terminal web y el programa real (app/main.py), dentro de Pyodide.

El navegador no puede bloquearse esperando el teclado, y input() es bloqueante. Así que cada
vez que el usuario pulsa Enter se REEJECUTA la sesión completa con todas las líneas escritas
hasta ahora; cuando el programa pide una línea que todavía no existe, se detiene con NeedInput
y la terminal muestra lo nuevo. Como el programa es determinista, el resultado es idéntico al
de una sesión normal, y el código de app/ no se modifica.
"""

import builtins
import io
import os
import sys

ROOT = "/home/pyodide"
CSV_PATH = os.path.join(ROOT, "contacts_export.csv")


class NeedInput(BaseException):
    """El programa pidió una línea que el usuario todavía no ha escrito."""


def _reset():
    """Deja el entorno como en un primer arranque: sin datos y con los módulos de app recargados."""
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    for nombre in os.listdir(ROOT):
        if nombre.startswith("contacts"):
            os.remove(os.path.join(ROOT, nombre))
    for modulo in [m for m in sys.modules if m == "app" or m.startswith("app.")]:
        del sys.modules[modulo]


def run(entradas):
    """Ejecuta el programa con las líneas dadas. Devuelve (salida, estado): 'waiting' o 'done'."""
    _reset()
    lineas = list(entradas)
    posicion = 0
    salida = io.StringIO()

    def input_simulado(prompt=""):
        nonlocal posicion
        salida.write(str(prompt))
        if posicion >= len(lineas):
            raise NeedInput()
        valor = lineas[posicion]
        posicion += 1
        salida.write(valor + "\n")  # eco de lo escrito, como en una terminal real
        return valor

    input_original, stdout_original = builtins.input, sys.stdout
    builtins.input, sys.stdout = input_simulado, salida
    estado = "done"
    try:
        from app.main import main

        main()
    except NeedInput:
        estado = "waiting"
    except SystemExit:
        pass
    finally:
        builtins.input, sys.stdout = input_original, stdout_original
    return salida.getvalue(), estado


def csv_exportado():
    """Contenido del CSV si el usuario lo exportó en esta sesión; si no, None."""
    if not os.path.exists(CSV_PATH):
        return None
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as archivo:
        return archivo.read()
