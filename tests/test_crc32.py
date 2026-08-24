import csv
import os
import sys

sys.path.append(os.path.dirname(__file__))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import apply_noise, crc32, encode_text, new_rng, random_text

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")

MESSAGE_SIZES = [8, 32, 128, 512]
ERROR_RATES = [0.0, 0.005, 0.01, 0.02, 0.05, 0.08, 0.12, 0.18, 0.25]
TRIALS_PER_COMBO = 200
SERIES_COLOR = {
    8: "#2a78d6",
    32: "#eb6834",
    128: "#1baf7a",
    512: "#eda100",
}
INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
GRIDLINE = "#e1e0d9"
AXIS = "#c3c2b7"

def run_trial(size, error_rate, rng):
    text = random_text(size, rng)
    bits = encode_text(text)
    frame = crc32.calculate_integrity(bits)
    noisy = apply_noise(frame, error_rate, rng)

    actual_error = noisy != frame
    _, detected = crc32.verify_integrity(noisy)
    overhead_pct = 100 * crc32.CRC_SIZE / len(bits)

    return {
        "size": size,
        "error_rate": error_rate,
        "actual_error": actual_error,
        "detected": detected,
        "overhead_pct": overhead_pct,
    }


def run_sweep():
    rng = new_rng()
    rows = []

    for size in MESSAGE_SIZES:
        for error_rate in ERROR_RATES:
            for _ in range(TRIALS_PER_COMBO):
                rows.append(run_trial(size, error_rate, rng))

    return rows


def write_raw_csv(rows):
    path = os.path.join(RESULTS_DIR, "crc32_raw.csv")
    fieldnames = ["size", "error_rate", "actual_error", "detected", "overhead_pct"]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return path

def summarize(rows):
    groups = {}

    for row in rows:
        key = (row["size"], row["error_rate"])
        groups.setdefault(key, []).append(row)

    summary = []

    for (size, error_rate), group in sorted(groups.items()):
        with_error = [r for r in group if r["actual_error"]]
        n_actual_errors = len(with_error)
        n_detected = sum(1 for r in with_error if r["detected"])
        false_positives = sum(1 for r in group if not r["actual_error"] and r["detected"])
        detection_rate = (n_detected / n_actual_errors) if n_actual_errors else None

        summary.append({
            "size": size,
            "error_rate": error_rate,
            "n_trials": len(group),
            "n_actual_errors": n_actual_errors,
            "n_detected": n_detected,
            "detection_rate": detection_rate,
            "false_positives": false_positives,
            "overhead_pct": group[0]["overhead_pct"],
        })

    return summary

def write_summary_csv(summary):
    path = os.path.join(RESULTS_DIR, "crc32_summary.csv")
    fieldnames = [
        "size", "error_rate", "n_trials", "n_actual_errors",
        "n_detected", "detection_rate", "false_positives", "overhead_pct",
    ]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary)

    return path

def _style_axes(ax):
    ax.grid(True, color=GRIDLINE, linewidth=0.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(AXIS)
    ax.tick_params(colors=SECONDARY_INK)
    ax.set_facecolor("white")

def plot_detection_vs_error_rate(summary):
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
    fig.patch.set_facecolor("white")

    for size in MESSAGE_SIZES:
        points = sorted(
            (s for s in summary if s["size"] == size and s["detection_rate"] is not None),
            key=lambda s: s["error_rate"],
        )
        xs = [p["error_rate"] for p in points]
        ys = [p["detection_rate"] for p in points]

        ax.plot(
            xs, ys, marker="o", markersize=6, linewidth=2,
            color=SERIES_COLOR[size], label=f"{size} caracteres",
        )

    ax.axhline(1.0, color=AXIS, linewidth=1, linestyle="--", zorder=0)
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("Tasa de error del canal (probabilidad por bit)", color=INK)
    ax.set_ylabel("Tasa de detección de errores", color=INK)
    ax.set_title("CRC-32: tasa de detección vs. tasa de error del canal", color=INK)
    _style_axes(ax)

    legend = ax.legend(title="Tamaño del mensaje", frameon=False)
    plt.setp(legend.get_texts(), color=INK)
    plt.setp(legend.get_title(), color=INK)

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "crc32_detection_vs_error_rate.png")
    fig.savefig(path)
    plt.close(fig)

    return path

def plot_overhead_vs_size(summary):
    sizes = MESSAGE_SIZES
    overhead = [
        next(s["overhead_pct"] for s in summary if s["size"] == size)
        for size in sizes
    ]

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
    fig.patch.set_facecolor("white")

    ax.plot(sizes, overhead, marker="o", markersize=7, linewidth=2, color=SERIES_COLOR[8])
    ax.set_xscale("log")
    ax.set_xlabel("Tamaño del mensaje (caracteres, escala log)", color=INK)
    ax.set_ylabel("Overhead (%) — 32 bits de CRC / bits de datos", color=INK)
    ax.set_title("CRC-32: overhead vs. tamaño del mensaje", color=INK)
    _style_axes(ax)

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "crc32_overhead_vs_size.png")
    fig.savefig(path)
    plt.close(fig)

    return path

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)

    print(
        f"Ejecutando barrido de CRC-32: {len(MESSAGE_SIZES)} tamaños x "
        f"{len(ERROR_RATES)} tasas de error x {TRIALS_PER_COMBO} pruebas..."
    )

    rows = run_sweep()
    raw_path = write_raw_csv(rows)
    summary = summarize(rows)
    summary_path = write_summary_csv(summary)

    print(f"Resultados crudos:  {raw_path}")
    print(f"Resumen:            {summary_path}")

    plot1 = plot_detection_vs_error_rate(summary)
    plot2 = plot_overhead_vs_size(summary)

    print(f"Gráfica 1: {plot1}")
    print(f"Gráfica 2: {plot2}")

    total_errors = sum(s["n_actual_errors"] for s in summary)
    total_missed = sum(s["n_actual_errors"] - s["n_detected"] for s in summary)

    print(f"\nErrores simulados con al menos un bit alterado: {total_errors}")
    print(f"Errores NO detectados por CRC-32 (falsos negativos): {total_missed}")

if __name__ == "__main__":
    main()
