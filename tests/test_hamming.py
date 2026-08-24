import csv
import os
import sys

sys.path.append(os.path.dirname(__file__))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import apply_noise, encode_text, hamming, new_rng, random_text

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")

SIZES = [8, 32, 128, 512]
ERROR_RATES = [0.0, 0.005, 0.01, 0.02, 0.05, 0.08, 0.12, 0.18, 0.25]
FIXED_R = 4
TRIALS_PER_COMBO = 200

R_VALUES = [3, 4, 5, 6, 7, 8]
R_ERROR_RATES = [0.01, 0.05, 0.1, 0.15]
R_FIXED_SIZE = 256
R_TRIALS_PER_COMBO = 200

SIZE_COLOR = {
    8: "#2a78d6",
    32: "#eb6834",
    128: "#1baf7a",
    512: "#eda100",
}
R_COLOR = {
    3: "#2a78d6",
    4: "#eb6834",
    5: "#1baf7a",
    6: "#eda100",
    7: "#e87ba4",
    8: "#008300",
}

INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
GRIDLINE = "#e1e0d9"
AXIS = "#c3c2b7"


def run_trial(size, error_rate, r, rng):
    text = random_text(size, rng)
    bits = encode_text(text)
    frame, padding = hamming.calculate_integrity(bits, r)
    noisy = apply_noise(frame, error_rate, rng)

    actual_error = noisy != frame
    recovered, has_error_flag = hamming.correct_message(noisy, r, padding)
    success = recovered == bits
    overhead_pct = 100 * (len(frame) - len(bits)) / len(bits)

    return {
        "size": size,
        "error_rate": error_rate,
        "r": r,
        "actual_error": actual_error,
        "has_error_flag": has_error_flag,
        "success": success,
        "overhead_pct": overhead_pct,
    }

def classify(row):
    if not row["actual_error"]:
        return "no_error"
    if row["success"]:
        return "corrected_ok"
    return "wrongly_corrected" if row["has_error_flag"] else "silently_corrupted"

def sweep_by_size(rng):
    rows = []
    for size in SIZES:
        for error_rate in ERROR_RATES:
            for _ in range(TRIALS_PER_COMBO):
                rows.append(run_trial(size, error_rate, FIXED_R, rng))
    return rows

def sweep_by_r(rng):
    rows = []
    for r in R_VALUES:
        for error_rate in R_ERROR_RATES:
            for _ in range(R_TRIALS_PER_COMBO):
                rows.append(run_trial(R_FIXED_SIZE, error_rate, r, rng))
    return rows

def write_raw_csv(rows, filename):
    path = os.path.join(RESULTS_DIR, filename)
    fieldnames = ["size", "error_rate", "r", "actual_error", "has_error_flag", "success", "overhead_pct"]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return path

def summarize(rows, group_keys):
    groups = {}

    for row in rows:
        key = tuple(row[k] for k in group_keys)
        groups.setdefault(key, []).append(row)

    summary = []

    for key, group in sorted(groups.items()):
        with_error = [r for r in group if r["actual_error"]]
        n_actual_errors = len(with_error)
        n_corrected_ok = sum(1 for r in with_error if classify(r) == "corrected_ok")
        n_wrongly_corrected = sum(1 for r in with_error if classify(r) == "wrongly_corrected")
        n_silently_corrupted = sum(1 for r in with_error if classify(r) == "silently_corrupted")
        success_rate = (n_corrected_ok / n_actual_errors) if n_actual_errors else None

        entry = dict(zip(group_keys, key))
        entry.update({
            "n_trials": len(group),
            "n_actual_errors": n_actual_errors,
            "n_corrected_ok": n_corrected_ok,
            "n_wrongly_corrected": n_wrongly_corrected,
            "n_silently_corrupted": n_silently_corrupted,
            "success_rate": success_rate,
            "overhead_pct": group[0]["overhead_pct"],
        })
        summary.append(entry)

    return summary

def write_summary_csv(summary, filename, group_keys):
    path = os.path.join(RESULTS_DIR, filename)
    fieldnames = group_keys + [
        "n_trials", "n_actual_errors", "n_corrected_ok",
        "n_wrongly_corrected", "n_silently_corrupted", "success_rate", "overhead_pct",
    ]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary)

    return path

def style_axes(ax):
    ax.grid(True, color=GRIDLINE, linewidth=0.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(AXIS)
    ax.tick_params(colors=SECONDARY_INK)
    ax.set_facecolor("white")

def plot_success_vs_error_by_size(summary):
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
    fig.patch.set_facecolor("white")

    for size in SIZES:
        points = sorted(
            (s for s in summary if s["size"] == size and s["success_rate"] is not None),
            key=lambda s: s["error_rate"],
        )
        xs = [p["error_rate"] for p in points]
        ys = [p["success_rate"] for p in points]

        ax.plot(
            xs, ys, marker="o", markersize=6, linewidth=2,
            color=SIZE_COLOR[size], label=f"{size} caracteres",
        )

    ax.axhline(1.0, color=AXIS, linewidth=1, linestyle="--", zorder=0)
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("Tasa de error del canal (probabilidad por bit)", color=INK)
    ax.set_ylabel("Tasa de corrección exitosa", color=INK)
    ax.set_title(f"Hamming (r={FIXED_R}): corrección exitosa vs. tasa de error", color=INK)
    style_axes(ax)

    legend = ax.legend(title="Tamaño del mensaje", frameon=False)
    plt.setp(legend.get_texts(), color=INK)
    plt.setp(legend.get_title(), color=INK)

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "hamming_success_vs_error_rate.png")
    fig.savefig(path)
    plt.close(fig)

    return path

def plot_success_vs_r(summary):
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
    fig.patch.set_facecolor("white")

    for r in R_VALUES:
        points = sorted(
            (s for s in summary if s["r"] == r and s["success_rate"] is not None),
            key=lambda s: s["error_rate"],
        )
        xs = [p["error_rate"] for p in points]
        ys = [p["success_rate"] for p in points]

        ax.plot(
            xs, ys, marker="o", markersize=6, linewidth=2,
            color=R_COLOR[r], label=f"r={r}",
        )

    ax.axhline(1.0, color=AXIS, linewidth=1, linestyle="--", zorder=0)
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("Tasa de error del canal (probabilidad por bit)", color=INK)
    ax.set_ylabel("Tasa de corrección exitosa", color=INK)
    ax.set_title(f"Hamming: corrección exitosa vs. tasa de error, por r\n(mensaje de {R_FIXED_SIZE} caracteres)", color=INK)
    style_axes(ax)

    legend = ax.legend(title="Bits de paridad (r)", frameon=False)
    plt.setp(legend.get_texts(), color=INK)
    plt.setp(legend.get_title(), color=INK)

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "hamming_success_vs_r.png")
    fig.savefig(path)
    plt.close(fig)

    return path


def plot_overhead_vs_r():
    rs = R_VALUES
    overhead = []

    for r in rs:
        m = hamming.calculate_m(r)
        overhead.append(100 * r / m)

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
    fig.patch.set_facecolor("white")

    ax.plot(rs, overhead, marker="o", markersize=7, linewidth=2, color=SIZE_COLOR[8])
    ax.set_xlabel("Bits de paridad (r)", color=INK)
    ax.set_ylabel("Overhead (%) — bits de paridad r / bits de datos m", color=INK)
    ax.set_title("Hamming: overhead vs. r", color=INK)
    ax.set_xticks(rs)
    style_axes(ax)

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "hamming_overhead_vs_r.png")
    fig.savefig(path)
    plt.close(fig)

    return path

def _print_totals(summary, label):
    total_errors = sum(s["n_actual_errors"] for s in summary)
    total_ok = sum(s["n_corrected_ok"] for s in summary)
    total_wrong_flagged = sum(s["n_wrongly_corrected"] for s in summary)
    total_silent = sum(s["n_silently_corrupted"] for s in summary)

    print(f"\n[{label}] Casos con al menos un bit alterado: {total_errors}")
    print(f"[{label}] Corregidos correctamente:              {total_ok}")
    print(f"[{label}] 'Corregidos' pero incorrectos:         {total_wrong_flagged}  (el receptor cree que funcionó)")
    print(f"[{label}] Corrompidos sin ninguna alerta:        {total_silent}  (el más peligroso: nadie se entera)")

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)

    rng = new_rng()

    print(
        f"Sweep 1/2 (tamaño x tasa de error, r={FIXED_R}): "
        f"{len(SIZES)} x {len(ERROR_RATES)} x {TRIALS_PER_COMBO} pruebas..."
    )
    rows_size = sweep_by_size(rng)
    write_raw_csv(rows_size, "hamming_raw_by_size.csv")
    summary_size = summarize(rows_size, ["size", "error_rate"])
    write_summary_csv(summary_size, "hamming_summary_by_size.csv", ["size", "error_rate"])
    plot1 = plot_success_vs_error_by_size(summary_size)
    _print_totals(summary_size, "tamaño x tasa de error")

    print(
        f"\nSweep 2/2 (r x tasa de error, tamaño={R_FIXED_SIZE}): "
        f"{len(R_VALUES)} x {len(R_ERROR_RATES)} x {R_TRIALS_PER_COMBO} pruebas..."
    )
    rows_r = sweep_by_r(rng)
    write_raw_csv(rows_r, "hamming_raw_by_r.csv")
    summary_r = summarize(rows_r, ["r", "error_rate"])
    write_summary_csv(summary_r, "hamming_summary_by_r.csv", ["r", "error_rate"])
    plot2 = plot_success_vs_r(summary_r)
    _print_totals(summary_r, "r x tasa de error")

    plot3 = plot_overhead_vs_r()

    print(f"\nGráfica 1: {plot1}")
    print(f"Gráfica 2: {plot2}")
    print(f"Gráfica 3: {plot3}")

if __name__ == "__main__":
    main()
