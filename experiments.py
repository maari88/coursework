import time
import math
import matplotlib.pyplot as plt
from generator import TaskGenerator
from algorithms import GreedyAlgorithm, LocalSearchAlgorithm


class ExperimentRunner:
    """Клас для автоматизованого проведення серій експериментів та побудови графіків"""

    @staticmethod
    def run_dimensionality_experiment(n_values=[10, 20, 30, 50, 100], r_repeats=10, cr=0.5, p_syn=0.3, sr=0.3):
        """
        Дослідження впливу розмірності задачі (n) на час та точність (5.4 та 5.5).
        """
        print("\n" + "=" * 90)
        print(" ЕКСПЕРИМЕНТ: ВПЛИВ РОЗМІРНОСТІ НА ЕФЕКТИВНІСТЬ АЛГОРИТМІВ")
        print("=" * 90)
        print(
            f"{'n':<5} | {'Win-rate ЛП':<15} | {'Середнє покращення (δ)':<25} | {'Час Жадібного (мс)':<20} | {'Час ЛП (мс)':<15}")
        print("-" * 90)

        results = []
        times_g_list = []
        times_ls_list = []
        deltas_list = []

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
                t_g = (end_g - start_g) * 1000

                # 3. Вимір часу та розв'язання Локальним пошуком
                start_ls = time.perf_counter()
                x_ls, f_ls, iters = LocalSearchAlgorithm.solve(task, x_g, strategy="first")
                end_ls = time.perf_counter()
                t_ls = (end_ls - start_ls) * 1000

                # 4. Збір статистики
                time_greedy_total += t_g
                time_ls_total += t_ls

                if f_ls > f_g:
                    wins += 1
                    delta = ((f_ls - f_g) / f_g) * 100 if f_g > 0 else 0
                    total_delta += delta

            # Усереднення результатів
            win_rate = (wins / r_repeats) * 100
            avg_delta = (total_delta / wins) if wins > 0 else 0.0
            avg_time_g = time_greedy_total / r_repeats
            avg_time_ls = time_ls_total / r_repeats

            print(f"{n:<5} | {win_rate:>12.1f}%   | +{avg_delta:>22.2f}% | {avg_time_g:>18.3f} | {avg_time_ls:>13.3f}")

            # Збереження для графіків
            times_g_list.append(avg_time_g)
            times_ls_list.append(avg_time_ls)
            deltas_list.append(avg_delta)
            results.append({
                "n": n, "win_rate": win_rate, "avg_delta": avg_delta,
                "avg_time_g": avg_time_g, "avg_time_ls": avg_time_ls
            })

        print("-" * 90)

        # ==========================================
        # ПОБУДОВА ГРАФІКІВ
        # ==========================================
        # 5.4 (Точність)
        plt.figure(figsize=(8, 5))
        plt.plot(n_values, deltas_list, marker='o', color='green', linewidth=2)
        plt.xlabel('Кількість проєктів (n)')
        plt.ylabel('Середнє покращення δ (%)')
        plt.title('Залежність точності (покращення) від розмірності задачі')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.savefig('graph_5_4_accuracy.png', bbox_inches='tight')
        plt.close()

        # 5.5 (Час)
        plt.figure(figsize=(8, 5))
        plt.plot(n_values, times_g_list, marker='s', label='Жадібний алгоритм', linewidth=2)
        plt.plot(n_values, times_ls_list, marker='^', label='Алгоритм локального пошуку', linewidth=2)
        plt.xlabel('Кількість проєктів (n)')
        plt.ylabel('Час виконання (мс)')
        plt.title('Залежність часу виконання від розмірності задачі')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.savefig('graph_5_5_time.png', bbox_inches='tight')
        plt.close()

        print("\nГрафіки збережено як 'graph_5_4_accuracy.png' та 'graph_5_5_time.png'")

        print("Триває генерація...")
        ExperimentRunner.exp_5_2_stagnation(n=n_values[-1] if n_values else 50, r_repeats=r_repeats)
        ExperimentRunner.exp_5_3_task_params(n=n_values[-1] if n_values else 30, r_repeats=r_repeats)
        print("\nУСІ ЕКСПЕРИМЕНТИ ЗАВЕРШЕНО!")

        return results

    @staticmethod
    def exp_5_2_stagnation(n=50, r_repeats=10):
        """5.2 (Умова стагнації)"""
        pi_labels = ["5n", "10n", "20n", "5n log(n)"]
        pi_values = [5 * n, 10 * n, 20 * n, int(5 * n * math.log2(n))] if n > 0 else [1, 2, 3, 4]

        times = []
        profits = []

        for pi in pi_values:
            t_total, f_total = 0, 0
            for _ in range(r_repeats):
                task = TaskGenerator.generate_task(n=n, cr=0.5, p_syn=0.3, sr=0.3)
                x_g, f_g = GreedyAlgorithm.solve(task)
                start = time.perf_counter()
                x_ls, f_ls, _ = LocalSearchAlgorithm.solve(task, x_g, strategy="first")
                t_total += (time.perf_counter() - start) * 1000
                f_total += f_ls
            times.append(t_total / r_repeats)
            profits.append(f_total / r_repeats)

        fig, ax1 = plt.subplots(figsize=(8, 5))
        ax1.plot(pi_labels, times, marker='o', color='tab:red', label='Час (мс)')
        ax1.set_xlabel('Параметр стагнації (π)')
        ax1.set_ylabel('Час виконання (мс)', color='tab:red')

        ax2 = ax1.twinx()
        ax2.plot(pi_labels, profits, marker='s', color='tab:blue', label='Цільова функція')
        ax2.set_ylabel('Середній прибуток', color='tab:blue')

        plt.title(f'Залежність часу та точності від умови завершення (n={n})')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.savefig('graph_5_2_stagnation.png', bbox_inches='tight')
        plt.close()

    @staticmethod
    def exp_5_3_task_params(n=30, r_repeats=10):
        """5.3 (Вплив CR та SR)"""
        cr_values = [0.3, 0.5, 0.8]
        sr_values = [0.1, 0.3, 0.5]

        results_matrix = []
        for cr in cr_values:
            row = []
            for sr in sr_values:
                delta_total = 0
                valid_wins = 0
                for _ in range(r_repeats):
                    task = TaskGenerator.generate_task(n=n, cr=cr, p_syn=0.3, sr=sr)
                    x_g, f_g = GreedyAlgorithm.solve(task)
                    x_ls, f_ls, _ = LocalSearchAlgorithm.solve(task, x_g)
                    if f_ls > f_g and f_g > 0:
                        delta_total += ((f_ls - f_g) / f_g) * 100
                        valid_wins += 1
                row.append((delta_total / valid_wins) if valid_wins > 0 else 0)
            results_matrix.append(row)

        fig, ax = plt.subplots(figsize=(8, 5))
        width = 0.2
        x = range(len(cr_values))

        for i, sr in enumerate(sr_values):
            offsets = [pos + (i - 1) * width for pos in x]
            vals = [results_matrix[j][i] for j in range(len(cr_values))]
            ax.bar(offsets, vals, width, label=f'Синергія SR={sr}')

        ax.set_xticks(x)
        ax.set_xticklabels([f'CR={cr}' for cr in cr_values])
        ax.set_xlabel('Жорсткість бюджету (CR)')
        ax.set_ylabel('Відносне покращення δ (%)')
        ax.set_title('Вплив параметрів задачі на ефективність Локального пошуку')
        ax.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.savefig('graph_5_3_params.png', bbox_inches='tight')
        plt.close()