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
    print(f"##### Test: Hamming with r={r} #####")

    bits = presentation.encode_message(text)
    m = hamming.calculate_m(r)
    n = m + r

    print(f"Original text:      {text}")
    print(f"Original bits:      {bits} ({len(bits)} bits)")
    print(
        f"Block config:       m={m} data bits, "
        f"r={r} parity bits, n={n} total"
    )

    frame, padding = hamming.calculate_integrity(bits, r)

    print(f"Padding added:      {padding} bits")
    print(f"Encoded frame:      {frame} ({len(frame)} bits)")

    noisy_frame = flip_bit(frame, 1)
    print(f"Frame with error:   {noisy_frame}")

    recovered_bits, error = hamming.verify_integrity(
        noisy_frame,
        r,
        padding
    )

    print(f"Error detected?:    {error}")
    print(f"Recovered bits:     {recovered_bits}")
    print(f"Matches original:   {recovered_bits == bits}")
    print()


def test_crc32():
    print("##### Test: CRC-32 #####")

    text = "Hi"
    bits = presentation.encode_message(text)

    print(f"Original text:      {text}")
    print(f"Original bits:      {bits}")

    frame = crc32.calculate_integrity(bits)

    print(f"Encoded frame:      {frame}")

    # Case 1: no errors
    data, error = crc32.verify_integrity(frame)

    print(
        f"[No noise] Error detected?: {error} "
        f"(should be False)"
    )

    # Case 2: simulated error
    noisy_frame = flip_bit(frame, 5)
    data, error = crc32.verify_integrity(noisy_frame)

    print(
        f"[With noise] Error detected?: {error} "
        f"(should be True)"
    )

    print()


if __name__ == "__main__":
    test_hamming(r=3)
    test_hamming(r=4)
    test_hamming(r=5)

    test_crc32()