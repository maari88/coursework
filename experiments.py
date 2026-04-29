import time
from generator import TaskGenerator
from algorithms import GreedyAlgorithm, LocalSearchAlgorithm


class ExperimentRunner:
    """Клас для автоматизованого проведення серій експериментів"""

    @staticmethod
    def run_dimensionality_experiment(n_values=[10, 20, 30, 50, 100], r_repeats=10, cr=0.5, p_syn=0.3, sr=0.3):
        """
        Дослідження впливу розмірності задачі (n) на час та точність
        r_repeats - кількість незалежних задач для усереднення результатів.
        """
        print("\n" + "=" * 90)
        print(" ЕКСПЕРИМЕНТ: ВПЛИВ РОЗМІРНОСТІ НА ЕФЕКТИВНІСТЬ АЛГОРИТМІВ")
        print("=" * 90)
        print(
            f"{'n':<5} | {'Win-rate ЛП':<15} | {'Середнє покращення (δ)':<25} | {'Час Жадібного (мс)':<20} | {'Час ЛП (мс)':<15}")
        print("-" * 90)

        results = []

        for n in n_values:
            wins = 0
            total_delta = 0.0
            time_greedy_total = 0.0
            time_ls_total = 0.0

            for _ in range(r_repeats):
                # 1. Генерація індивідуальної задачі
                task = TaskGenerator.generate_task(n=n, cr=cr, p_syn=p_syn, sr=sr, p_rule=0.1)

                # 2. Вимір часу та розв'язання Жадібним алгоритмом
                start_g = time.perf_counter()
                x_g, f_g = GreedyAlgorithm.solve(task)
                end_g = time.perf_counter()
                t_g = (end_g - start_g) * 1000  # перевід у мілісекунди

                # 3. Вимір часу та розв'язання Локальним пошуком (покращення жадібного)
                start_ls = time.perf_counter()
                x_ls, f_ls, iters = LocalSearchAlgorithm.solve(task, x_g, strategy="first")
                end_ls = time.perf_counter()
                t_ls = (end_ls - start_ls) * 1000

                # 4. Збір статистики
                time_greedy_total += t_g
                time_ls_total += t_ls

                if f_ls > f_g:
                    wins += 1
                    # Формула відносного покращення (δ)
                    delta = ((f_ls - f_g) / f_g) * 100 if f_g > 0 else 0
                    total_delta += delta

            # Усереднення результатів для поточної розмірності n
            win_rate = (wins / r_repeats) * 100
            avg_delta = (total_delta / wins) if wins > 0 else 0.0
            avg_time_g = time_greedy_total / r_repeats
            avg_time_ls = time_ls_total / r_repeats

            print(f"{n:<5} | {win_rate:>12.1f}%   | +{avg_delta:>22.2f}% | {avg_time_g:>18.3f} | {avg_time_ls:>13.3f}")

            results.append({
                "n": n,
                "win_rate": win_rate,
                "avg_delta": avg_delta,
                "avg_time_greedy": avg_time_g,
                "avg_time_ls": avg_time_ls
            })

        print("-" * 90)
        print("Експеримент завершено.")
        return results