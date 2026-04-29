import random
from models import Project, PortfolioTask

class TaskGenerator:
    """Клас для автоматичної генерації екземплярів задачі інвестиційного портфеля"""

    @staticmethod
    def generate_task(n, cost_range=(50, 300), profit_range=(20, 150), risk_range=(1, 10),
                      cr=0.5, p_rule=0.2, p_syn=0.3, sr=0.3):
        projects = []
        total_cost = 0
        total_risk = 0

        # 1. Генерація множини незалежних проєктів
        for i in range(1, n + 1):
            c = random.randint(cost_range[0], cost_range[1])
            p = random.randint(profit_range[0], profit_range[1])
            r = random.randint(risk_range[0], risk_range[1])
            projects.append(Project(project_id=i, cost=c, profit=p, risk=r))
            total_cost += c
            total_risk += r

        # 2. Формування глобальних обмежень (за коефіцієнтом CR)
        Q = int(cr * total_cost)
        R_max = int(cr * total_risk)

        # 3. Накладання логічних правил (A_k => B_k)
        rules = {}
        for i in range(1, n):
            if random.random() <= p_rule:
                possible_supports = list(range(i + 1, n + 1))
                if possible_supports:
                    k = random.randint(1, min(2, len(possible_supports)))
                    supports = random.sample(possible_supports, k)
                    rules[i] = supports

        # 4. Генерація синергетичного графа
        synergies = {}
        for i in range(n):
            for j in range(i + 1, n):
                if random.random() <= p_syn:
                    pa = projects[i].profit
                    pb = projects[j].profit
                    # Бонус розраховується від середнього прибутку пари
                    bonus = int(sr * (pa + pb) / 2)
                    if bonus > 0:
                        key = f"{projects[i].id}_{projects[j].id}"
                        synergies[key] = bonus

        # 5. Повернення готового об'єкта задачі
        return PortfolioTask(n, projects, Q, R_max, rules, synergies)