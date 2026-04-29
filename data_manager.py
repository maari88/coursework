import json
import os
from models import PortfolioTask


class DataManager:
    """Клас для збереження та завантаження задач у форматі JSON"""

    @staticmethod
    def save_task_to_file(task, filename="task_data.json"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(task.to_dict(), f, indent=4, ensure_ascii=False)
            print(f"[Успіх] Задачу збережено у файл {filename}")
        except Exception as e:
            print(f"[Помилка] Не вдалося зберегти файл: {e}")

    @staticmethod
    def load_task_from_file(filename="task_data.json"):
        if not os.path.exists(filename):
            print(f"[Помилка] Файл {filename} не знайдено.")
            return None

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"[Успіх] Задачу завантажено з файлу {filename}")
            return PortfolioTask.from_dict(data)
        except Exception as e:
            print(f"[Помилка] Не вдалося завантажити файл: {e}")
            return None