import sys
import os
import random
import string
import csv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from algorithms import hamming
from layers import presentation, noise

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

MESSAGE_SIZES = [8, 32, 128, 512]
ERROR_RATES = [0, 0.5, 1, 2, 5, 10, 15, 20, 25]
HAMMING_R = 4
TRIALS = 200


def random_text(length: int) -> str:
    alphabet = string.ascii_letters + " "
    return "".join(random.choices(alphabet, k=length))


def run_trial(text: str, r: int, error_rate: float) -> dict:
    bits = presentation.encode_message(text)
    frame, padding = hamming.calculate_integrity(bits, r)
    noisy_frame = noise.apply_noise(frame, error_rate)

    bit_flipped = noisy_frame != frame

    decoded_bits, error_detected = hamming.correct_message(noisy_frame, r, padding)
    exact_match = decoded_bits == bits

    overhead_pct = (len(frame) - len(bits)) / len(bits) * 100

    return {
        "bit_flipped": bit_flipped,
        "error_detected": error_detected,
        "exact_match": exact_match,
        "overhead_pct": overhead_pct,
    }


def build_table() -> list[dict]:
    rows = []

    for size in MESSAGE_SIZES:
        for rate_pct in ERROR_RATES:
            rate = rate_pct / 100

            errors_occurred = 0
            errors_detected = 0
            successfully_corrected = 0
            overhead_values = []

            for _ in range(TRIALS):
                text = random_text(size)
                result = run_trial(text, HAMMING_R, rate)

                if result["bit_flipped"]:
                    errors_occurred += 1
                    if result["error_detected"]:
                        errors_detected += 1

                if result["exact_match"]:
                    successfully_corrected += 1

                overhead_values.append(result["overhead_pct"])

            detection_rate = (
                (errors_detected / errors_occurred * 100) if errors_occurred > 0 else 100.0
            )
            correction_rate = successfully_corrected / TRIALS * 100
            avg_overhead = sum(overhead_values) / len(overhead_values)

            rows.append({
                "characters": size,
                "error_rate_pct": rate_pct,
                "errors_occurred": errors_occurred,
                "errors_detected": errors_detected,
                "detection_rate_pct": round(detection_rate, 2),
                "successfully_corrected": successfully_corrected,
                "correction_rate_pct": round(correction_rate, 2),
                "overhead_pct": round(avg_overhead, 3),
            })

            print(
                f"chars={size:<4} error={rate_pct:<5}% -> "
                f"detected={detection_rate:.1f}%  corrected={correction_rate:.1f}%  "
                f"overhead={avg_overhead:.2f}%"
            )

    return rows


def save_csv(rows: list[dict]):
    path = os.path.join(RESULTS_DIR, "hamming_table.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nTabla guardada en: {path}")


def print_markdown_table(rows: list[dict]):
    print("\n--- Tabla en formato Markdown (para copiar al reporte) ---\n")
    headers = [
        "Caracteres", "Tasa de error (%)", "Cantidad de errores",
        "Errores detectados", "Tasa de detección (%)",
        "Corregidos exitosamente", "Tasa de corrección (%)", "Overhead (%)"
    ]
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join(["---"] * len(headers)) + "|")
    for r in rows:
        print(
            f"| {r['characters']} | {r['error_rate_pct']} | {r['errors_occurred']} | "
            f"{r['errors_detected']} | {r['detection_rate_pct']} | "
            f"{r['successfully_corrected']} | {r['correction_rate_pct']} | {r['overhead_pct']} |"
        )


def plot_success_rate_by_size(rows: list[dict]):
    print("\nGenerando gráfica: tasa de corrección vs. tasa de error, por tamaño de mensaje ...")
    plt.figure(figsize=(8, 6))

    for size in MESSAGE_SIZES:
        subset = [r for r in rows if r["characters"] == size]
        x = [r["error_rate_pct"] for r in subset]
        y = [r["correction_rate_pct"] for r in subset]
        plt.plot(x, y, marker="o", label=f"{size} caracteres")

    plt.title(f"Tasa de corrección exitosa vs. tasa de error (Hamming, r={HAMMING_R})")
    plt.xlabel("Tasa de error del canal (%)")
    plt.ylabel("Mensajes recuperados exactamente (%)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(title="Tamaño del mensaje")
    plt.ylim(-5, 105)

    path = os.path.join(RESULTS_DIR, "success_rate_by_size.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Guardada en: {path}")


def plot_overhead_by_size(rows: list[dict]):
    print("Generando gráfica: overhead vs. tamaño de mensaje ...")
    sizes = MESSAGE_SIZES
    overheads = []
    for size in sizes:
        subset = [r["overhead_pct"] for r in rows if r["characters"] == size]
        overheads.append(sum(subset) / len(subset))

    plt.figure(figsize=(7, 5))
    plt.plot(sizes, overheads, marker="o", color="#8E44AD")
    plt.title(f"Overhead de Hamming vs. tamaño del mensaje (r={HAMMING_R})")
    plt.xlabel("Tamaño del mensaje (caracteres)")
    plt.ylabel("Overhead promedio (%)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xscale("log")
    plt.xticks(sizes, [str(s) for s in sizes])

    for x, y in zip(sizes, overheads):
        plt.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 8), ha="center")

    path = os.path.join(RESULTS_DIR, "overhead_by_size.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Guardada en: {path}")


if __name__ == "__main__":
    random.seed(42)
    rows = build_table()
    save_csv(rows)
    print_markdown_table(rows)
    plot_success_rate_by_size(rows)
    plot_overhead_by_size(rows)
    print("\n¡Listo!")