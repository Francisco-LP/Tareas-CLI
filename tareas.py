#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ToDo CLI
"""

import os
import csv
from datetime import datetime
from typing import Dict, Any
from lib.storage import load_tasks, save_tasks

DATA_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")

# ---- Estado de ejecución (se carga desde JSON) ----
tasks: Dict[int, Dict[str, Any]] = {}
next_id: int = 1  # se recalcula al iniciar


# ---------- Utilidades ----------
def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def parse_bool(s: str) -> bool:
    s = (s or "").strip().lower()
    return s in {"s", "si", "sí", "y", "yes", "1", "true", "verdadero"}

def input_with_default(prompt: str, default: str) -> str:
    """Muestra el valor actual y si el usuario presiona Enter, lo conserva."""
    val = input(f"{prompt} [{default}]: ").strip()
    return default if val == "" else val

def input_bool_with_default(prompt: str, default: bool) -> bool:
    """Pide s/n mostrando el valor actual; Enter conserva el valor existente."""
    actual = "sí" if default else "no"
    raw = input(f"{prompt} (s/n) [{actual}]: ").strip().lower()
    if raw == "":
        return default
    return raw in {"s", "si", "sí", "y", "yes", "1", "true", "verdadero"}


def input_non_empty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("⚠️  El texto no puede estar vacío. Intenta de nuevo.")

def input_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            return int(raw)
        print("⚠️  Debes ingresar un número válido.")

def recalc_next_id() -> None:
    global next_id
    if tasks:
        next_id = max(tasks.keys()) + 1
    else:
        next_id = 1


# ---------- Persistencia ----------
def load_state() -> None:
    """Carga tasks desde tasks.json y recalcula el next_id."""
    global tasks
    raw = load_tasks(DATA_FILE)  
    tasks = {}
    for t in raw:
        try:
            tid = int(t["id"])
            tasks[tid] = t
        except Exception:
            continue
    recalc_next_id()

def persist() -> None:
    """Guarda tasks (dict) como list en JSON."""
    as_list = [tasks[k] for k in sorted(tasks.keys())]
    save_tasks(DATA_FILE, as_list)


# ---------- Lógica de negocio ----------
def add_task(title: str, description: str, done: bool) -> dict:
    global next_id
    task = {
        "id": next_id,
        "date": now_iso(),
        "title": title.strip(),
        "description": description.strip(),
        "done": bool(done),
        "updated_at": now_iso(),
    }
    tasks[next_id] = task
    next_id += 1
    persist()
    return task

def edit_task(task_id: int, title: str, description: str, done: bool) -> bool:
    t = tasks.get(task_id)
    if not t:
        return False
    t["title"] = title.strip()
    t["description"] = description.strip()
    t["done"] = bool(done)
    t["updated_at"] = now_iso()
    persist()
    return True

def delete_task(task_id: int) -> bool:
    if task_id in tasks:
        del tasks[task_id]
        persist()
        return True
    return False

def list_tasks() -> None:
    clear_screen()
    print("📋 Lista de tareas:\n")
    if not tasks:
        print("No hay tareas. Usa la opción '1' para agregar.\n")
        return

    print(f"{'ID':<4} {'✓':<1} {'FECHA':<19} {'TÍTULO':<30} {'DESCRIPCIÓN':<40}")
    print("-" * 100)
    for tid in sorted(tasks.keys()):
        t = tasks[tid]
        check = "✔" if t.get("done") else " "
        date = (t.get("date") or "")[:19]
        title = (t.get("title") or "")[:30]
        desc = (t.get("description") or "")[:40]
        print(f"{t['id']:<4} {check:<1} {date:<19} {title:<30} {desc:<40}")
    print()


# ---------- Exportaciones ----------
def ensure_export_dir() -> None:
    os.makedirs(EXPORT_DIR, exist_ok=True)

def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def export_json() -> str:
    ensure_export_dir()
    path = os.path.join(EXPORT_DIR, f"tasks_{timestamp()}.json")
    payload = [tasks[k] for k in sorted(tasks.keys())]
    save_tasks(path, payload)
    return path

def export_csv() -> str:
    ensure_export_dir()
    path = os.path.join(EXPORT_DIR, f"tasks_{timestamp()}.csv")
    fieldnames = ["id", "date", "title", "description", "done", "updated_at"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for tid in sorted(tasks.keys()):
            row = {k: tasks[tid].get(k, "") for k in fieldnames}
            writer.writerow(row)
    return path


# ---------- Menús ----------
def export_menu() -> None:
    clear_screen()
    print("💾 Guardar / Exportar\n")
    print("1) Exportar a JSON (snapshot para compartir)")
    print("2) Exportar a CSV  (abrir en Excel/Sheets)")
    print("3) Volver")
    choice = input("Elige una opción [1-3]: ").strip()
    if choice == "1":
        p = export_json()
        print(f"✅ Exportado JSON en: {p}\n")
        input("Enter para continuar...")
    elif choice == "2":
        p = export_csv()
        print(f"✅ Exportado CSV en: {p}\n")
        input("Enter para continuar...")

def main_menu() -> None:
    load_state()
    while True:
        clear_screen()
        print("======= Tareas-App =======\n")
        print("1. Agregar tarea")
        print("2. Editar tarea")
        print("3. Eliminar tarea")
        print("4. Ver tareas")
        print("5. Guardar / Exportar")
        print("6. Salir")
        opcion = input("Selecciona una opción [1-6]: ").strip()

        if opcion == "1":
            clear_screen()
            print("➕ Agregar tarea\n")
            title = input_non_empty("Título: ")
            description = input_non_empty("Descripción: ")
            done = parse_bool(input("¿Completada? (s/n): "))
            add_task(title, description, done)
            print("✅ Tarea agregada.\n")
            input("Enter para continuar...")

        elif opcion == "2":
            list_tasks()
            print("✏️  Editar tarea\n")
            task_id = input_int("Ingresa el ID de la tarea a editar: ")
            if task_id not in tasks:
                print("❌ ID no encontrado.\n")
                input("Enter para continuar...")
            else:
                t = tasks[task_id]
                title = input_with_default("Nuevo título", t["title"])
                description = input_with_default("Nueva descripción", t["description"])
                done = input_bool_with_default("¿Completada?", t["done"])
                
                edit_task(task_id, title, description, done)
                print("✅ Tarea editada.\n")
                input("Enter para continuar...")


        elif opcion == "3":
            list_tasks()
            print("🗑️  Eliminar tarea\n")
            task_id = input_int("Ingresa el ID de la tarea a eliminar: ")
            if task_id not in tasks:
                print("❌ ID no encontrado.\n")
                input("Enter para continuar...")
            else:
                confirm = parse_bool(input("¿Seguro que deseas eliminarla? (s/n): "))
                if confirm and delete_task(task_id):
                    print("✅ Tarea eliminada.\n")
                else:
                    print("↩️  Operación cancelada.\n")
                input("Enter para continuar...")

        elif opcion == "4":
            list_tasks()
            input("Enter para continuar...")

        elif opcion == "5":
            export_menu()

        elif opcion == "6":
            print("👋 Saliendo. ¡Hasta luego!")
            break

        else:
            print("⚠️  Opción no válida. Intenta de nuevo.\n")
            input("Enter para continuar...")


if __name__ == "__main__":
    main_menu()
