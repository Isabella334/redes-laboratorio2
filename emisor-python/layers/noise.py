import random

def apply_noise(frame, error_rate):
    if not 0 <= error_rate <= 1:
        raise ValueError("La tasa de error debe estar entre 0 y 1")

    noisy_bits = []

    for bit in frame:
        if random.random() < error_rate:
            flipped_bit = "1" if bit == "0" else "0"
            noisy_bits.append(flipped_bit)
        else:
            noisy_bits.append(bit)

    return "".join(noisy_bits)