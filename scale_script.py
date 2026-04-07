import os
import subprocess
import time
import csv
import shutil
import threading
import psutil
from pathlib import Path
import matplotlib.pyplot as plt

BASE_DIR = Path("/home/tikhomirov/codeql_scale_test")
CODEQL_CMD = "codeql"
CODEQL_QUERY = "python-security-extended"
MAX_N = 200
TIMEOUT_SEC = 300
RESULTS_CSV = "codeql_scale_resources.csv"

resource_data = []
stop_monitor = False

def monitor_resources(pid):
    global resource_data, stop_monitor
    try:
        parent = psutil.Process(pid)
        while not stop_monitor:
            try:
                children = parent.children(recursive=True)
                all_procs = [parent] + children
                total_mem = sum(p.memory_info().rss for p in all_procs) / (1024 * 1024)
                resource_data.append((time.time(), 0, total_mem))
                time.sleep(0.5)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
    except Exception as e:
        print(f"Ошибка мониторинга: {e}")

def generate_test_file(n, output_dir):
    conditions = []
    for i in range(n):
        conditions.append(f"    if os.urandom(1)[0] > 128:")
        conditions.append(f"        s = s + 'a{i}'")
        conditions.append(f"    else:")
        conditions.append(f"        s = s + 'b{i}'")
    cond_text = "\n".join(conditions)

    code = f'''from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

@app.route('/test')
def test():
    user_input = request.args.get('cmd', '')
    s = user_input
{cond_text}
    subprocess.run(s, shell=True)
    return "done"
'''
    file_path = output_dir / f"test_n_{n}.py"
    with open(file_path, "w") as f:
        f.write(code)
    return file_path

def run_codeql(file_path):
    global resource_data, stop_monitor
    resource_data = []
    stop_monitor = False

    test_dir = file_path.parent
    db_path = test_dir / "codeql-db"
    if db_path.exists():
        shutil.rmtree(db_path)

    cmd_create = [
        CODEQL_CMD, "database", "create", str(db_path),
        "--language=python", "--source-root", str(test_dir)
    ]
    try:
        subprocess.run(cmd_create, timeout=TIMEOUT_SEC, capture_output=True, check=True)
    except Exception as e:
        print(f"Ошибка создания БД: {e}")
        return False, None, (0, 0, 0, 0)

    cmd_analyze = [
        CODEQL_CMD, "database", "analyze", str(db_path),
        CODEQL_QUERY, "--format=csv", "--output", str(test_dir / "results.csv")
    ]
    start = time.time()
    process = subprocess.Popen(cmd_analyze, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(1)

    monitor_thread = threading.Thread(target=monitor_resources, args=(process.pid,))
    monitor_thread.start()

    try:
        process.wait(timeout=TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        process.kill()
        stop_monitor = True
        monitor_thread.join()
        print("Таймаут анализа")
        return False, None, (0, 0, 0, 0)
    elapsed = time.time() - start

    stop_monitor = True
    monitor_thread.join()

    found_target = False
    out_file = test_dir / "results.csv"
    target_filename = file_path.name
    if out_file.exists():
        with open(out_file, "r", encoding="utf-8") as f:
            for line in f:
                if "Uncontrolled command line" in line and target_filename in line:
                    found_target = True
                    break

    if resource_data:
        mem_vals = [r[2] for r in resource_data]
        avg_mem = sum(mem_vals) / len(mem_vals)
        max_mem = max(mem_vals)
    else:
        avg_mem = max_mem = 0

    return found_target, elapsed, (0, 0, avg_mem, max_mem)

def main():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    break_n = None

    for n in range(1, MAX_N + 1):
        print(f"\nИтерация: {n}")
        test_file = generate_test_file(n, BASE_DIR)
        found, elapsed, (_, _, avg_mem, max_mem) = run_codeql(test_file)

        if elapsed is None:
            results.append({
                "n": n,
                "paths": 2**(n+1) - 2,
                "found": found,
                "time": -1,
                "avg_mem": 0,
                "max_mem": 0
            })
            print("CodeQL: анализ прерван")
            if break_n is None:
                break_n = n
        else:
            results.append({
                "n": n,
                "paths": 2**(n+1) - 2,
                "found": found,
                "time": elapsed,
                "avg_mem": avg_mem,
                "max_mem": max_mem
            })
            print(f"CodeQL: found={found}, time={elapsed:.2f}s, MEM avg={avg_mem:.1f}MB, max={max_mem:.1f}MB")
            if not found and break_n is None:
                break_n = n

    with open(RESULTS_CSV, "w", newline="") as f:
        fieldnames = ["n", "paths", "found", "time", "avg_mem", "max_mem"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n Результаты сохранены в {RESULTS_CSV}")
    if break_n:
        print(f"CodeQL перестал находить уязвимость при n = {break_n}")
    else:
        print(f"CodeQL находил уязвимость при всех n до {MAX_N}")

    try:
        plt.rcParams['font.size'] = 12

        n_vals = [r["n"] for r in results]
        times = [r["time"] if r["time"] >= 0 else 0 for r in results]
        avg_mem = [r["avg_mem"] for r in results]
        max_mem = [r["max_mem"] for r in results]

        plt.figure(figsize=(10, 6))
        plt.plot(n_vals, times, linestyle='-', color='b', linewidth=1.5)
        plt.xlabel('Итерация (n)', fontsize=12)
        plt.ylabel('Время анализа (с)', fontsize=12)
        plt.tight_layout()
        plt.savefig("codeql_time_graph.png")
        plt.close()
        print("График времени сохранён в codeql_time_graph.png")

        plt.figure(figsize=(10, 6))
        plt.plot(n_vals, avg_mem, 'g-', label='Средняя память (МБайт)', linewidth=1.5)
        plt.plot(n_vals, max_mem, 'g--', label='Максимальная память (МБайт)', linewidth=1.5)
        plt.xlabel('Итерация (n)', fontsize=12)
        plt.ylabel('Память (МБайт)', fontsize=12)
        plt.legend()
        plt.tight_layout()
        plt.savefig("codeql_memory_graph.png")
        plt.close()
        print("График памяти сохранён в codeql_memory_graph.png")

    except ImportError:
        print("matplotlib не установлен, график не построен.")

if __name__ == "__main__":
    main()