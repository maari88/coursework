import random


class GreedyAlgorithm:
    """Клас, що реалізує жадібний евристичний алгоритм"""

    @staticmethod
    def calculate_objective(x, task):
        total_profit = 0
        for i, proj in enumerate(task.projects):
            if x[i] == 1:
                total_profit += proj.profit

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
                continue

            cand = {p_id}
            added_new = True

            while added_new:
                added_new = False
                for a_id, b_list in task.rules.items():
                    if a_id in cand:
                        support_exists_in_x = any(x[b - 1] == 1 for b in b_list)
                        support_exists_in_cand = any(b in cand for b in b_list)

                        if not support_exists_in_x and not support_exists_in_cand:
                            best_b_id = None
                            best_b_eff = -1
                            for b in b_list:
                                if b not in cand:
                                    b_eff = next(item[2] for item in efficiencies if item[1] == b)
                                    if b_eff > best_b_eff:
                                        best_b_eff = b_eff
                                        best_b_id = b

                            if best_b_id is not None:
                                cand.add(best_b_id)
                                added_new = True

            c_cand = sum(task.projects[p_id_cand - 1].cost for p_id_cand in cand)
            r_cand = sum(task.projects[p_id_cand - 1].risk for p_id_cand in cand)

            if (q_curr + c_cand <= task.Q) and (r_curr + r_cand <= task.R_max):
                for p_id_cand in cand:
                    x[p_id_cand - 1] = 1
                q_curr += c_cand
                r_curr += r_cand

        f_best = GreedyAlgorithm.calculate_objective(x, task)
        return x, f_best


class LocalSearchAlgorithm:
    """Клас, що реалізує оптимізований алгоритм ЛП (Delta Evaluation)"""

    @staticmethod
    def solve(task, initial_x, strategy="first", pi=None):
        if pi is None:
            pi = 10 * task.n

        costs = [p.cost for p in task.projects]
        risks = [p.risk for p in task.projects]
        profits = [p.profit for p in task.projects]

        # Швидка карта синергій
        syn_map = {i: {} for i in range(task.n)}
        for pair_key, bonus in task.synergies.items():
            id1, id2 = map(int, pair_key.split('_'))
            syn_map[id1 - 1][id2 - 1] = bonus
            syn_map[id2 - 1][id1 - 1] = bonus

        current_x = initial_x[:]

        # Обчислення початкового стану
        current_cost = sum(costs[i] for i in range(task.n) if current_x[i])
        current_risk = sum(risks[i] for i in range(task.n) if current_x[i])
        current_profit = GreedyAlgorithm.calculate_objective(current_x, task)

        best_x = current_x[:]
        best_f = current_profit

        stagnation_counter = 0
        iteration = 0

        while stagnation_counter < pi:
            iteration += 1

            in_portfolio = [i for i in range(task.n) if current_x[i] == 1]
            out_portfolio = [i for i in range(task.n) if current_x[i] == 0]

            operations = []
            for i in in_portfolio:
                for j in out_portfolio:
                    operations.append(('swap', i, j))
            for j in out_portfolio:
                operations.append(('add', j))
            for i in in_portfolio:
                operations.append(('remove', i))

            random.shuffle(operations)

            step_best_x = None
            step_best_f = current_profit
            step_best_cost = current_cost
            step_best_risk = current_risk

            valid_neighbors = []

            # --- ОБЧИСЛЕННЯ ЗА ДЕЛЬТОЮ (Миттєве відсікання) ---
            for op in operations:
                op_type = op[0]

                if op_type == 'swap':
                    i, j = op[1], op[2]
                    new_cost = current_cost - costs[i] + costs[j]
                    new_risk = current_risk - risks[i] + risks[j]
                elif op_type == 'add':
                    j = op[1]
                    new_cost = current_cost + costs[j]
                    new_risk = current_risk + risks[j]
                else:
                    i = op[1]
                    new_cost = current_cost - costs[i]
                    new_risk = current_risk - risks[i]

                if new_cost > task.Q or new_risk > task.R_max:
                    continue

                neighbor_x = current_x[:]
                if op_type == 'swap':
                    neighbor_x[i] = 0;
                    neighbor_x[j] = 1
                elif op_type == 'add':
                    neighbor_x[j] = 1
                else:
                    neighbor_x[i] = 0

                # Перевірка логічних правил
                is_valid = True
                for a_id, b_list in task.rules.items():
                    if neighbor_x[a_id - 1] == 1:
                        if not any(neighbor_x[b - 1] == 1 for b in b_list):
                            is_valid = False
                            break
                if not is_valid:
                    continue

                new_profit = current_profit
                if op_type == 'swap':
                    new_profit = new_profit - profits[i] + profits[j]
                    # Віднімаємо втрачену синергію
                    for syn_j, bonus in syn_map[i].items():
                        if neighbor_x[syn_j] == 1 and syn_j != j:
                            new_profit -= bonus
                    # Додаємо нову синергію
                    for syn_j, bonus in syn_map[j].items():
                        if neighbor_x[syn_j] == 1 and syn_j != i:
                            new_profit += bonus
                elif op_type == 'add':
                    new_profit += profits[j]
                    for syn_j, bonus in syn_map[j].items():
                        if neighbor_x[syn_j] == 1:
                            new_profit += bonus
                else:
                    new_profit -= profits[i]
                    for syn_j, bonus in syn_map[i].items():
                        if neighbor_x[syn_j] == 1:
                            new_profit -= bonus

                # Зберігаємо 5 випадкових валідних сусідів для стрибка зі стагнації
                if len(valid_neighbors) < 5:
                    valid_neighbors.append((neighbor_x, new_cost, new_risk, new_profit))

                if new_profit > step_best_f:
                    step_best_f = new_profit
                    step_best_x = neighbor_x
                    step_best_cost = new_cost
                    step_best_risk = new_risk

                    if strategy == "first":
                        break

            if step_best_x is not None:
                current_x = step_best_x
                current_f = step_best_f
                current_cost = step_best_cost
                current_risk = step_best_risk

                if current_f > best_f:
                    best_f = current_f
                    best_x = current_x[:]
                    stagnation_counter = 0
                else:
                    stagnation_counter += 1
            else:
                stagnation_counter += 1
                if valid_neighbors:
                    current_x, current_cost, current_risk, current_f = random.choice(valid_neighbors)

        return best_x, best_f, iteration