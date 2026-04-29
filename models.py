class Project:
    """Клас, що описує один інвестиційний проєкт"""
    def __init__(self, project_id, cost, profit, risk):
        self.id = project_id
        self.cost = cost
        self.profit = profit
        self.risk = risk

    def to_dict(self):
        return {"id": self.id, "cost": self.cost, "profit": self.profit, "risk": self.risk}

    @classmethod
    def from_dict(cls, data):
        return cls(data['id'], data['cost'], data['profit'], data['risk'])


class PortfolioTask:
    """Клас, що описує індивідуальну задачу формування портфеля"""
    def __init__(self, n, projects, Q, R_max, rules, synergies):
        self.n = n
        self.projects = projects
        self.Q = Q
        self.R_max = R_max
        # Логічні правила: словник {A_id: [B_id1, B_id2]})
        self.rules = rules
        # Синергія: словник {"id1_id2": бонус})
        self.synergies = synergies

    def to_dict(self):
        return {
            "n": self.n,
            "projects": [p.to_dict() for p in self.projects],
            "Q": self.Q,
            "R_max": self.R_max,
            "rules": self.rules,
            "synergies": self.synergies
        }

    @classmethod
    def from_dict(cls, data):
        projects = [Project.from_dict(p) for p in data['projects']]
        rules = {int(k): v for k, v in data['rules'].items()}
        return cls(data['n'], projects, data['Q'], data['R_max'], rules, data['synergies'])