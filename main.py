import sys
from models import Project, PortfolioTask
from data_manager import DataManager
from generator import TaskGenerator
from algorithms import GreedyAlgorithm, LocalSearchAlgorithm
from experiments import ExperimentRunner


def input_task_manually():
    """Функція для покрокового введення індивідуальної задачі через консоль"""
    print("\n--- Введення індивідуальної задачі вручну ---")
    try:
        n = int(input("Введіть кількість проєктів (n): "))
        projects = []

        print("\nВведіть параметри для кожного проєкту:")
        for i in range(1, n + 1):
            print(f" Проєкт №{i}:")
            c = float(input("   Вартість (cost): "))
            p = float(input("   Прибуток (profit): "))
            r = float(input("   Ризик (risk): "))
            projects.append(Project(project_id=i, cost=c, profit=p, risk=r))

        print("\nВведіть глобальні обмеження:")
        Q = float(input("   Бюджет капіталовкладень (Q): "))
        R_max = float(input("   Граничний ризик (R_max): "))

        print("\nВведіть логічні правила (A => B).")
        print("Натисніть Enter замість ID проєкту, щоб завершити введення правил.")
        rules = {}
        while True:
            a_str = input("   ID проєкту, що потребує підтримки (A_k) (або Enter): ")
            if not a_str.strip():
                break
            a_id = int(a_str)
            b_str = input(f"   ID проєктів, які підтримують (B_k), через кому (напр. 1,2): ")
            b_list = [int(x.strip()) for x in b_str.split(',')]
            rules[a_id] = b_list

        print("\nВведіть синергетичні пари.")
        print("Натисніть Enter замість номерів, щоб завершити введення пар.")
        synergies = {}
        while True:
            pair_str = input("   Введіть пару проєктів через пробіл (напр. 2 3) (або Enter): ")
            if not pair_str.strip():
                break
            id1, id2 = map(int, pair_str.split())
            bonus = float(input("   Бонус за синергію: "))
            key = f"{min(id1, id2)}_{max(id1, id2)}"
            synergies[key] = bonus

        print("\n[Успіх] Задачу успішно введено!")
        return PortfolioTask(n, projects, Q, R_max, rules, synergies)

    except ValueError:
        print("\n[Помилка] Некоректний ввід. Потрібно вводити числа. Спробуйте знову.")
        return None


def print_menu():
    print("\n" + "=" * 50)
    print(" СИСТЕМА ОПТИМІЗАЦІЇ ІНВЕСТИЦІЙНОГО ПОРТФЕЛЯ")
    print("=" * 50)
    print("1. Ввести індивідуальну задачу (ІЗ) вручну")
    print("2. Згенерувати ІЗ випадковим чином")
    print("3. Зберегти поточну ІЗ у файл")
    print("4. Завантажити ІЗ з файлу")
    print("5. Розв'язати задачу (Жадібний + Локальний пошук)")
    print("6. Запустити пакетне експериментальне дослідження")
    print("0. Вихід")
    print("=" * 50)


def main():
    current_task = None

    while True:
        print_menu()
        choice = input("Оберіть дію (0-6): ")

        if choice == '1':
            # --- БЛОК ВВЕДЕННЯ ВРУЧНУ ---
            task = input_task_manually()
            if task:
                current_task = task

        elif choice == '2':
            # --- БЛОК ГЕНЕРАЦІЇ ---
            try:
                n = int(input("Введіть кількість проєктів (наприклад, 10): "))
                cr = float(input("Введіть жорсткість обмежень CR (від 0.1 до 1.0, наприклад, 0.5): "))
                p_syn = float(input("Введіть ймовірність синергії (від 0.0 до 1.0, наприклад, 0.3): "))

                current_task = TaskGenerator.generate_task(n=n, cr=cr, p_syn=p_syn)
                print(f"\n[Успіх] Згенеровано задачу на {n} проєктів!")
                print(f"Бюджет (Q): {current_task.Q}, Граничний ризик (R_max): {current_task.R_max}")
                print(f"Кількість логічних правил: {len(current_task.rules)}")
                print(f"Кількість синергетичних пар: {len(current_task.synergies)}")
            except ValueError:
                print("\n[Помилка] Будь ласка, вводьте коректні числові значення.")

        elif choice == '3':
            # --- БЛОК ЗБЕРЕЖЕННЯ ---
            if current_task:
                filename = input("Введіть ім'я файлу для збереження (натисніть Enter для 'task_data.json'): ")
                if not filename:
                    filename = "task_data.json"
                DataManager.save_task_to_file(current_task, filename)
            else:
                print("\n[Увага] Немає активної задачі для збереження. Згенеруйте або введіть її.")

        elif choice == '4':
            # --- БЛОК ЗАВАНТАЖЕННЯ ---
            filename = input("Введіть ім'я файлу (або натисніть Enter для 'task_data.json'): ")
            if not filename:
                filename = "task_data.json"
            loaded_task = DataManager.load_task_from_file(filename)
            if loaded_task:
                current_task = loaded_task

        elif choice == '5':
            # --- БЛОК РОЗВ'ЯЗАННЯ ---
            if current_task is None:
                print("\n[Увага] Немає активної задачі. Згенеруйте або завантажте її (пункт 2 або 4).")
                continue

            print("\n--- Запуск Жадібного Алгоритму ---")
            greedy_x, greedy_f = GreedyAlgorithm.solve(current_task)
            print(f"Обрані проєкти (бінарний вектор): {greedy_x}")
            print(f"Цільова функція (Прибуток): {greedy_f}")

            print("\n--- Запуск Локального Пошуку ---")
            ls_x, ls_f, iters = LocalSearchAlgorithm.solve(current_task, greedy_x, strategy="first")
            print(f"Обрані проєкти (бінарний вектор): {ls_x}")
            print(f"Цільова функція (Прибуток): {ls_f}")
            print(f"Витрачено ітерацій: {iters}")

            if ls_f > greedy_f:
                improvement = ls_f - greedy_f
                print(f"\n[Успіх] Локальний пошук покращив розв'язок на {improvement} тис. од.!")
            else:
                print("\n[Інфо] Жадібний алгоритм одразу знайшов сильний (локально оптимальний) розв'язок.")

        elif choice == '6':
            # --- БЛОК ЕКСПЕРИМЕНТІВ ---
            try:
                print("\nНалаштування пакетного експерименту:")
                start_n = int(input("Початкова розмірність (наприклад, 10): "))
                end_n = int(input("Кінцева розмірність (наприклад, 100): "))
                step = int(input("Крок зміни розмірності (наприклад, 20): "))
                repeats = int(input("Кількість задач для кожної розмірності (R, наприклад, 10): "))

                n_values = list(range(start_n, end_n + 1, step))
                ExperimentRunner.run_dimensionality_experiment(n_values=n_values, r_repeats=repeats)

            except ValueError:
                print("\n[Помилка] Будь ласка, вводьте лише цілі числа.")

        elif choice == '0':
            print("\nЗавершення роботи. До побачення!")
            sys.exit(0)
        else:
            print("\n[Помилка] Невірний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    main()