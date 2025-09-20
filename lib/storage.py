def load_tasks(path: str) -> list[dict]:
    """Carga la lista de tareas desde un archivo JSON.

    Si el archivo no existe → devuelve [].
    Si está corrupto → imprime aviso y devuelve [] (no crashea).
    Si el contenido no es una lista → devuelve [].
    """
    import json
    import os

    if not os.path.exists(path):
        return []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print(f"El contenido de {path} no es una lista. Devolviendo lista vacía.")
                return []
    except json.JSONDecodeError:
        print(f"El archivo {path} está corrupto o no es un JSON válido. Devolviendo lista vacía.")
        return []
    except Exception as e:
        print(f"Ocurrió un error al leer {path}: {e}. Devolviendo lista vacía.")
        return []



def save_tasks(path: str, tasks: list[dict]) -> None:
    """Guarda la lista de tareas en un archivo JSON.

    Si hay un error al escribir, imprime un aviso (no crashea).
    """
    import json
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ocurrió un error al escribir en {path}: {e}.")
        # No crashea, solo avisa

