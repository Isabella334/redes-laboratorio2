import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from algorithms import hamming, crc32
from layers import presentation


def flip_bit(bits: str, pos: int) -> str:
    bit_list = list(bits)
    bit_list[pos] = "1" if bit_list[pos] == "0" else "0"
    return "".join(bit_list)


def test_hamming(r: int, text: str = "Hello"):
    print(f"##### Prueba: Hamming con r={r} #####")

    bits = presentation.encode_message(text)
    m = hamming.calculate_m(r)
    n = m + r

    print(f"Texto original:          {text}")
    print(f"Bits originales:         {bits} ({len(bits)} bits)")
    print(
        f"Configuración del bloque: m={m} bits de datos, "
        f"r={r} bits de paridad, n={n} total"
    )

    frame, padding = hamming.calculate_integrity(bits, r)

    print(f"Bits de relleno agregados: {padding} bits")
    print(f"Trama codificada:          {frame} ({len(frame)} bits)")

    noisy_frame = flip_bit(frame, 1)
    print(f"Trama con error:           {noisy_frame}")

    recovered_bits, error = hamming.correct_message(
        noisy_frame,
        r,
        padding
    )

    print(f"¿Error detectado?:         {error}")
    print(f"Bits recuperados:          {recovered_bits}")
    print(f"Coincide con el original:  {recovered_bits == bits}")
    print()


def test_crc32():
    print("##### Prueba: CRC-32 #####")

    text = "Hi"
    bits = presentation.encode_message(text)

    print(f"Texto original:      {text}")
    print(f"Bits originales:     {bits}")

    frame = crc32.calculate_integrity(bits)

    print(f"Trama codificada:    {frame}")

    # Caso 1: sin errores
    data, error = crc32.verify_integrity(frame)

    print(
        f"[Sin ruido] ¿Error detectado?: {error} "
        f"(debería ser False)"
    )

    # Caso 2: error simulado
    noisy_frame = flip_bit(frame, 5)
    data, error = crc32.verify_integrity(noisy_frame)

    print(
        f"[Con ruido] ¿Error detectado?: {error} "
        f"(debería ser True)"
    )

    print()


if __name__ == "__main__":
    test_hamming(r=3)
    test_hamming(r=4)
    test_hamming(r=5)

    test_crc32()