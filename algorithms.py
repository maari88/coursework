import copy


class GreedyAlgorithm:
    """Клас, що реалізує жадібний евристичний алгоритм"""

    @staticmethod
    def calculate_objective(x, task):
        """Допоміжна функція для розрахунку цільової функції (ЦФ) портфеля"""
        total_profit = 0
        # Базовий прибуток
        for i, proj in enumerate(task.projects):
            if x[i] == 1:
                total_profit += proj.profit

        # Синергетичні бонуси
        for pair_key, bonus in task.synergies.items():
            id1, id2 = map(int, pair_key.split('_'))
            if x[id1 - 1] == 1 and x[id2 - 1] == 1:
                total_profit += bonus

        return total_profit

    @staticmethod
    def solve(task):
        n = task.n
        x = [0] * n
        q_curr = 0
        r_curr = 0

        efficiencies = []
        for i, p in enumerate(task.projects):
            eff = p.profit / p.cost
            efficiencies.append((i, p.id, eff))

        efficiencies.sort(key=lambda item: item[2], reverse=True)

        for i, p_id, eff in efficiencies:
            if x[i] == 1:
                continue  # Проєкт вже в портфелі (доданий раніше як підтримка)

            cand = {p_id}  # Пакет кандидатів
            added_new = True

            while added_new:
                added_new = False
                for a_id, b_list in task.rules.items():
                    # Якщо в пакеті є залежний проєкт, а підтримуючого немає ні в портфелі, ні в пакеті
                    if a_id in cand:
                        support_exists_in_x = any(x[b - 1] == 1 for b in b_list)
                        support_exists_in_cand = any(b in cand for b in b_list)

                        if not support_exists_in_x and not support_exists_in_cand:
                            # Шукаємо найкращий проєкт з b_list за ефективністю
                            best_b_id = None
                            best_b_eff = -1
                            for b in b_list:
                                if b not in cand:
                                    # Знаходимо ефективність проєкту b
                                    b_eff = next(item[2] for item in efficiencies if item[1] == b)
                                    if b_eff > best_b_eff:
                                        best_b_eff = b_eff
                                        best_b_id = b

                            if best_b_id is not None:
                                cand.add(best_b_id)
                                added_new = True

            # Перевірка ресурсів для всього пакету
            c_cand = sum(task.projects[p_id_cand - 1].cost for p_id_cand in cand)
            r_cand = sum(task.projects[p_id_cand - 1].risk for p_id_cand in cand)

            if (q_curr + c_cand <= task.Q) and (r_curr + r_cand <= task.R_max):
                for p_id_cand in cand:
                    x[p_id_cand - 1] = 1
                q_curr += c_cand
                r_curr += r_cand

        # Обчислення фінального значення ЦФ
        f_best = GreedyAlgorithm.calculate_objective(x, task)
        return x, f_best


class LocalSearchAlgorithm:
    """Клас, що реалізує алгоритм локального пошуку"""

    @staticmethod
    def is_valid(x, task):
        """Перевірка портфеля на допустимість"""
        q_curr = sum(task.projects[i].cost for i in range(task.n) if x[i] == 1)
        r_curr = sum(task.projects[i].risk for i in range(task.n) if x[i] == 1)

        if q_curr > task.Q or r_curr > task.R_max:
            return False

        for a_id, b_list in task.rules.items():
            if x[a_id - 1] == 1:
                # Має бути хоча б один підтримуючий проєкт
                if not any(x[b - 1] == 1 for b in b_list):
                    return False
        return True

    @staticmethod
    def solve(task, initial_x, strategy="best"):
        """
        Локальний пошук з околом Swap та Add/Remove.
        strategy: "first" (Перше покращення) або "best" (Найкраще покращення)
        """
        current_x = copy.deepcopy(initial_x)
        current_f = GreedyAlgorithm.calculate_objective(current_x, task)

        iteration = 0
        improvement_found = True

        while improvement_found:
            improvement_found = False
            iteration += 1
            best_neighbor_x = None
            best_neighbor_f = current_f

            in_portfolio = [i for i in range(task.n) if current_x[i] == 1]
            out_portfolio = [i for i in range(task.n) if current_x[i] == 0]

            neighbors = []

            # 1. Операції Swap
            for i in in_portfolio:
                for j in out_portfolio:
                    neighbor = copy.deepcopy(current_x)
                    neighbor[i] = 0
                    neighbor[j] = 1
                    neighbors.append(neighbor)

            # 2. Операції Add (Пробуємо просто додати проєкт, якщо є бюджет)
            for j in out_portfolio:
                neighbor = copy.deepcopy(current_x)
                neighbor[j] = 1
                neighbors.append(neighbor)

            # Оцінюємо окіл
            for neighbor in neighbors:
                if LocalSearchAlgorithm.is_valid(neighbor, task):
                    neighbor_f = GreedyAlgorithm.calculate_objective(neighbor, task)
                    if neighbor_f > best_neighbor_f:
                        best_neighbor_f = neighbor_f
                        best_neighbor_x = neighbor
                        if strategy == "first":
                            break  # Стратегія першого покращення

            # Якщо знайшли кращий стан, переходимо в нього
            if best_neighbor_x is not None:
                current_x = best_neighbor_x
                current_f = best_neighbor_f
                improvement_found = True

        return current_x, current_f, iteration