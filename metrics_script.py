import os
import shutil
import subprocess
import sys
import csv
import json
from pathlib import Path
from collections import defaultdict

SOURCE_TESTS = Path("/home/tikhomirov/Downloads/custom")
GROUND_TRUTH_FILE = Path("/home/tikhomirov/Downloads/ground_truth.csv")
WORK_DIR = Path("/home/tikhomirov/aggregator_work")
BANDIT_CMD = "bandit"
SEMGREP_CMD = "semgrep"
CODEQL_CMD = "codeql"
SEMGREP_RULES_SOURCE = Path("/home/tikhomirov/Semgrep/semgrep-rules/python")
CUSTOM_SEMGREP_RULE = Path("/home/tikhomirov/Semgrep/custom_semgrep.yml")
CODEQL_QUERY = "python-security-extended"

CUSTOM_TEST_FILES = ["Gyp_3B.py", "Gyp_5A.py", "Gyp_9.py"]
CUSTOM_CATEGORIES = {3, 5, 9}

def get_file_category(filename):
    mapping = {
        "Gyp_1.py": 1,
        "Gyp_2A.py": 2,
        "Gyp_2B.py": 2,
        "Gyp_3A.py": 3,
        "Gyp_3B.py": 3,
        "Gyp_3C.py": 3,
        "Gyp_4A.py": 4,
        "Gyp_4B.py": 4,
        "Gyp_5A.py": 5,
        "Gyp_5B.py": 5,
        "Gyp_6A.py": 6,
        "Gyp_6B.py": 6,
        "Gyp_7A.py": 7,
        "Gyp_7B.py": 7,
        "Gyp_8A.py": 8,
        "Gyp_8B.py": 8,
        "Gyp_9.py": 9,
        "Gyp_10.py": 10,
        "Gyp_11A.py": 11,
        "Gyp_11B.py": 11,
        "Gyp_12.py": 12,
        "Gyp_13A.py": 13,
        "Gyp_13B.py": 13,
    }
    return mapping.get(filename)

def load_ground_truth(csv_file):
    gt = {}
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = row['filename'].strip()
            vuln = row['vulnerable'].strip().lower() == 'true'
            gt[fname] = vuln
    return gt

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)

def prepare_work_dir(source_tests, source_rules, work_dir):
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    tests_dest = work_dir / "tests"
    ensure_dir(tests_dest)
    py_files = list(source_tests.glob("*.py"))
    if not py_files:
        print(f"В {source_tests} нет .py файлов")
        sys.exit(1)
    for f in py_files:
        shutil.copy(f, tests_dest / f.name)
    print(f"Скопировано {len(py_files)} тестов в {tests_dest}")

    rules_dest = None
    if source_rules.exists() and source_rules.is_dir():
        rules_dest = work_dir / "semgrep-rules"
        shutil.copytree(source_rules, rules_dest, dirs_exist_ok=True)
        print(f"Скопированы правила Semgrep в {rules_dest}")
    else:
        print(f"Правила Semgrep не найдены, будет использован --config auto")

    return tests_dest, rules_dest

def run_bandit(tests_dir, out_file):
    cmd = [BANDIT_CMD, "-r", str(tests_dir), "-f", "csv", "-o", str(out_file)]
    print("Запуск Bandit...")
    subprocess.run(cmd)
    print("Bandit завершён")

def run_semgrep(tests_dir, config, out_file):
    """config может быть директорией или файлом, либо 'auto'."""
    if config is None:
        cmd = [SEMGREP_CMD, "scan", "--config", "auto", "--json", "-o", str(out_file), str(tests_dir)]
    else:
        cmd = [SEMGREP_CMD, "scan", "--config", str(config), "--json", "-o", str(out_file), str(tests_dir)]
    print(f"Запуск Semgrep с конфигурацией {config if config else 'auto'}...")
    subprocess.run(cmd)
    print("Semgrep завершён")

def run_codeql(tests_dir, out_file):
    db_path = tests_dir.parent / "codeql-db"
    if db_path.exists():
        shutil.rmtree(db_path)
    cmd_create = [CODEQL_CMD, "database", "create", str(db_path),
                  "--language=python", "--source-root", str(tests_dir)]
    print("Создание базы данных CodeQL...")
    subprocess.run(cmd_create)

    cmd_analyze = [CODEQL_CMD, "database", "analyze", str(db_path),
                   CODEQL_QUERY, "--format=csv", "--output", str(out_file)]
    print("Запуск анализа CodeQL...")
    subprocess.run(cmd_analyze)
    print("CodeQL завершён")

def parse_bandit_csv(file):
    warned = set()
    if not file.exists():
        return warned
    with open(file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fpath = row.get('filename', '')
            if fpath:
                warned.add(Path(fpath).name)
    return warned

def parse_semgrep_json(file):
    warned = set()
    if not file.exists():
        return warned
    with open(file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Ошибка парсинга JSON Semgrep из {file}")
            return warned
    ignore_msg = "Missing 'encoding' parameter. 'open()' uses device locale encodings by default"
    file_warnings = defaultdict(list)
    for result in data.get('results', []):
        path = result.get('path', '')
        if not path:
            continue
        message = result.get('extra', {}).get('message', '')
        file_warnings[Path(path).name].append(message)

    for fname, messages in file_warnings.items():
        useful = [msg for msg in messages if ignore_msg not in msg]
        if useful:
            warned.add(fname)
    return warned

def parse_codeql_csv(file):
    warned = set()
    if not file.exists():
        return warned
    with open(file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            for cell in row:
                if cell.endswith('.py'):
                    warned.add(Path(cell).name)
                    break
    return warned

def compute_metrics(warned_files, ground_truth_subset):
    TP = FP = TN = FN = 0
    for fname, is_vuln in ground_truth_subset.items():
        if fname in warned_files:
            if is_vuln:
                TP += 1
            else:
                FP += 1
        else:
            if is_vuln:
                FN += 1
            else:
                TN += 1
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        'TP': TP, 'FP': FP, 'TN': TN, 'FN': FN,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

def compute_metrics_by_category(warned_files, ground_truth, file_to_cat):
    files_by_cat = defaultdict(list)
    for fname in ground_truth.keys():
        cat = file_to_cat(fname)
        if cat is not None:
            files_by_cat[cat].append(fname)
        else:
            print(f"Файл {fname} не имеет категории.")
    metrics = {}
    for cat, flist in files_by_cat.items():
        subset = {f: ground_truth[f] for f in flist}
        metrics[cat] = compute_metrics(warned_files, subset)
    return metrics

def main():
    if not SOURCE_TESTS.exists():
        print(f"Исходная директория тестов {SOURCE_TESTS} не найдена")
        sys.exit(1)

    if not GROUND_TRUTH_FILE.exists():
        print(f"Файл ground truth {GROUND_TRUTH_FILE} не найден")
        sys.exit(1)
    ground_truth = load_ground_truth(GROUND_TRUTH_FILE)
    print(f"Загружено {len(ground_truth)} записей ground truth")

    tests_dir, rules_dir = prepare_work_dir(SOURCE_TESTS, SEMGREP_RULES_SOURCE, WORK_DIR)

    copied_names = {f.name for f in tests_dir.glob("*.py")}
    missing = set(ground_truth.keys()) - copied_names
    if missing:
        print(f"Следующие файлы из ground truth отсутствуют в {SOURCE_TESTS}:")
        for f in sorted(missing):
            print(f"   {f}")
        for f in missing:
            del ground_truth[f]

    bandit_out = WORK_DIR / "bandit_results.csv"
    semgrep_out = WORK_DIR / "semgrep_results.json"
    codeql_out = WORK_DIR / "codeql_results.csv"

    run_bandit(tests_dir, bandit_out)
    run_semgrep(tests_dir, rules_dir, semgrep_out)
    run_codeql(tests_dir, codeql_out)

    bandit_warned = parse_bandit_csv(bandit_out)
    semgrep_warned = parse_semgrep_json(semgrep_out)
    codeql_warned = parse_codeql_csv(codeql_out)

    overall_bandit = compute_metrics(bandit_warned, ground_truth)
    overall_semgrep = compute_metrics(semgrep_warned, ground_truth)
    overall_codeql = compute_metrics(codeql_warned, ground_truth)

    bandit_by_cat = compute_metrics_by_category(bandit_warned, ground_truth, get_file_category)
    semgrep_by_cat = compute_metrics_by_category(semgrep_warned, ground_truth, get_file_category)
    codeql_by_cat = compute_metrics_by_category(codeql_warned, ground_truth, get_file_category)

    print("\n" + "="*80)
    print("Результаты тестирования на стандартном наборе правил")
    print("="*80)
    header = f"{'Кат':<4} {'Инструмент':<10} {'TP':<4} {'FP':<4} {'TN':<4} {'FN':<4} {'Prec':<6} {'Recall':<7} {'F1':<6}"
    print(header)
    print("-"*80)

    all_cats = sorted(set(bandit_by_cat.keys()) | set(semgrep_by_cat.keys()) | set(codeql_by_cat.keys()))
    for cat in all_cats:
        for tool, cat_metrics in [("Bandit", bandit_by_cat), ("Semgrep", semgrep_by_cat), ("CodeQL", codeql_by_cat)]:
            m = cat_metrics.get(cat, {'TP':0,'FP':0,'TN':0,'FN':0,'precision':0.0,'recall':0.0,'f1':0.0})
            print(f"{cat:<4} {tool:<10} {m['TP']:<4} {m['FP']:<4} {m['TN']:<4} {m['FN']:<4} {m['precision']:.3f}  {m['recall']:.3f}   {m['f1']:.3f}")
        print()

    print("\n" + "="*80)
    print("Общие метрики:")
    print("="*80)
    for name, metrics in [("Bandit", overall_bandit),
                          ("Semgrep", overall_semgrep),
                          ("CodeQL", overall_codeql)]:
        print(f"\n{name}:")
        print(f"  TP: {metrics['TP']}, FP: {metrics['FP']}, TN: {metrics['TN']}, FN: {metrics['FN']}")
        print(f"  Precision: {metrics['precision']:.3f}")
        print(f"  Recall:    {metrics['recall']:.3f}")
        print(f"  F1-score:  {metrics['f1']:.3f}")

    print("\n" + "="*80)
    print("Тестирование Semgrep на собственном наборе правил")
    print("="*80)

    for f in tests_dir.glob("*.py"):
        if f.name not in CUSTOM_TEST_FILES:
            f.unlink()
    print(f"Оставлены файлы: {CUSTOM_TEST_FILES} в {tests_dir}")

    if not CUSTOM_SEMGREP_RULE.exists():
        print(f"Пользовательское правило {CUSTOM_SEMGREP_RULE} не найдено")
        sys.exit(1)

    custom_rules_dir = WORK_DIR / "custom_rules"
    ensure_dir(custom_rules_dir)
    custom_rule_dest = custom_rules_dir / "custom_semgrep.yml"
    shutil.copy(CUSTOM_SEMGREP_RULE, custom_rule_dest)
    print(f"Пользовательское правило скопировано в {custom_rule_dest}")

    custom_semgrep_out = WORK_DIR / "semgrep_custom_results.json"
    run_semgrep(tests_dir, custom_rules_dir, custom_semgrep_out)

    semgrep_custom_warned = parse_semgrep_json(custom_semgrep_out)

    custom_ground_truth = {f: ground_truth[f] for f in CUSTOM_TEST_FILES if f in ground_truth}

    def custom_cat(fname):
        cat = get_file_category(fname)
        return cat if cat in CUSTOM_CATEGORIES else None

    custom_metrics_by_cat = compute_metrics_by_category(semgrep_custom_warned, custom_ground_truth, custom_cat)

    print("\n" + "-"*60)
    print("Результаты тестирования на собственном наборе правил")
    print("-"*60)
    for cat in sorted(CUSTOM_CATEGORIES):
        m = custom_metrics_by_cat.get(cat, {'TP':0,'FP':0,'TN':0,'FN':0,'precision':0.0,'recall':0.0,'f1':0.0})
        print(f"Категория {cat}: TP={m['TP']}, FP={m['FP']}, TN={m['TN']}, FN={m['FN']}, "
              f"Precision={m['precision']:.3f}, Recall={m['recall']:.3f}, F1={m['f1']:.3f}")

    custom_overall = compute_metrics(semgrep_custom_warned, custom_ground_truth)
    print(f"\nОбщие метрики:")
    print(f"  TP={custom_overall['TP']}, FP={custom_overall['FP']}, TN={custom_overall['TN']}, FN={custom_overall['FN']}")
    print(f"  Precision={custom_overall['precision']:.3f}, Recall={custom_overall['recall']:.3f}, F1={custom_overall['f1']:.3f}")

    report_file = Path.cwd() / "aggregator_results.txt"
    with open(report_file, "w", encoding='utf-8') as f:
        f.write("Результаты тестирования на стандартном наборе правил\n")
        f.write(header + "\n")
        f.write("-"*80 + "\n")
        for cat in all_cats:
            for tool, cat_metrics in [("Bandit", bandit_by_cat), ("Semgrep", semgrep_by_cat), ("CodeQL", codeql_by_cat)]:
                m = cat_metrics.get(cat, {'TP':0,'FP':0,'TN':0,'FN':0,'precision':0.0,'recall':0.0,'f1':0.0})
                f.write(f"{cat:<4} {tool:<10} {m['TP']:<4} {m['FP']:<4} {m['TN']:<4} {m['FN']:<4} {m['precision']:.3f}  {m['recall']:.3f}   {m['f1']:.3f}\n")
            f.write("\n")
        f.write("\nОбщие метрики\n")
        for name, m in [("Bandit", overall_bandit), ("Semgrep", overall_semgrep), ("CodeQL", overall_codeql)]:
            f.write(f"{name}: TP={m['TP']}, FP={m['FP']}, TN={m['TN']}, FN={m['FN']}, "
                    f"Precision={m['precision']:.3f}, Recall={m['recall']:.3f}, F1={m['f1']:.3f}\n")

        f.write("\n\nРезультаты тестирования на собственном наборе правил\n")
        for cat in sorted(CUSTOM_CATEGORIES):
            m = custom_metrics_by_cat.get(cat, {})
            f.write(f"Категория {cat}: TP={m.get('TP',0)}, FP={m.get('FP',0)}, TN={m.get('TN',0)}, FN={m.get('FN',0)}, "
                    f"Precision={m.get('precision',0):.3f}, Recall={m.get('recall',0):.3f}, F1={m.get('f1',0):.3f}\n")
        f.write(f"\nОбщие метрики: TP={custom_overall['TP']}, FP={custom_overall['FP']}, "
                f"TN={custom_overall['TN']}, FN={custom_overall['FN']}, "
                f"Precision={custom_overall['precision']:.3f}, Recall={custom_overall['recall']:.3f}, F1={custom_overall['f1']:.3f}\n")

    print(f"\nПолный отчёт сохранён в {report_file}")

if __name__ == "__main__":
    main()
