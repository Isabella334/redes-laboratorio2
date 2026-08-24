import sys
import os
import random

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from algorithms import hamming
from layers import presentation, noise

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

TEST_MESSAGE = "Este es un mensaje de prueba para el laboratorio de redes"
TRIALS = 200 


def simulate_send(text, r, error_rate):
    bits = presentation.encode_message(text)
    frame, padding = hamming.calculate_integrity(bits, r)
    noisy_frame = noise.apply_noise(frame, error_rate)
    recovered_bits, _ = hamming.correct_message(noisy_frame, r, padding)
    return recovered_bits == bits


def overhead(r):
    m = hamming.calculate_m(r)
    n = m + r
    return (r / n) * 100


def plot_overhead_vs_r():
    print("Generando gráfica 1: overhead vs. r ...")
    r_values = [3, 4, 5, 6, 7]
    overheads = [overhead(r) for r in r_values]

    plt.figure(figsize=(7, 5))
    plt.plot(r_values, overheads, marker="o", color="#2E75B6")
    plt.title("Hamming overhead vs. parity bits (r)")
    plt.xlabel("Parity bits (r)")
    plt.ylabel("Overhead (%)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(r_values)

    for x, y in zip(r_values, overheads):
        plt.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 8), ha="center")

    path = os.path.join(RESULTS_DIR, "overhead_vs_r.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Guardada en: {path}")


def plot_success_vs_error(r: int = 4):
    print(f"Generando gráfica 2: tasa de éxito vs. tasa de error (r={r}) ...")
    error_rates = [0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3]
    success_rates = []

    for rate in error_rates:
        hits = sum(simulate_send(TEST_MESSAGE, r, rate) for _ in range(TRIALS))
        success_rates.append((hits / TRIALS) * 100)
        print(f"  tasa_error={rate:<6} -> éxito={success_rates[-1]:.1f}%")

    plt.figure(figsize=(7, 5))
    plt.plot(error_rates, success_rates, marker="o", color="#2E7D32")
    plt.title(f"Success rate vs. channel error rate (Hamming, r={r})")
    plt.xlabel("Channel error rate (probability per bit)")
    plt.ylabel("Messages recovered exactly (%)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.ylim(-5, 105)

    path = os.path.join(RESULTS_DIR, "success_vs_error.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Guardada en: {path}")


def plot_success_vs_r(error_rate: float = 0.02):
    print(f"Generando gráfica 3: tasa de éxito vs. r (tasa_error={error_rate}) ...")
    r_values = [3, 4, 5, 6, 7]
    success_rates = []

    for r in r_values:
        hits = sum(simulate_send(TEST_MESSAGE, r, error_rate) for _ in range(TRIALS))
        success_rates.append((hits / TRIALS) * 100)
        print(f"  r={r} -> éxito={success_rates[-1]:.1f}%")

    plt.figure(figsize=(7, 5))
    plt.plot(r_values, success_rates, marker="o", color="#C0392B")
    plt.title(f"Success rate vs. block size (error_rate={error_rate})")
    plt.xlabel("Parity bits (r)")
    plt.ylabel("Messages recovered exactly (%)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(r_values)
    plt.ylim(-5, 105)

    path = os.path.join(RESULTS_DIR, "success_vs_r.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Guardada en: {path}")


if __name__ == "__main__":
    random.seed(42)  # para resultados reproducibles
    plot_overhead_vs_r()
    plot_success_vs_error(r=4)
    plot_success_vs_r(error_rate=0.02)
    print("\n¡Listo! Revisa la carpeta 'results/' para ver las gráficas generadas.")