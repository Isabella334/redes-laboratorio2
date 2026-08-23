from algorithms import hamming, crc32

def calculate_integrity(bits, algorithm, r: int = 4):
    if algorithm == "hamming":
        frame, padding = hamming.calculate_integrity(bits, r)
        metadata = {"r": r, "padding": padding}
        return frame, metadata
    if algorithm == "crc32":
        frame = crc32.calculate_integrity(bits)
        return frame, {}

    raise ValueError(f"Algoritmo desconocido: {algorithm}")


def verify_integrity(frame, algorithm, metadata):
    if algorithm == "hamming":
        r = metadata["r"]
        padding = metadata["padding"]
        return hamming.correct_message(frame, r, padding)
    if algorithm == "crc32":
        return crc32.verify_integrity(frame)

    raise ValueError(f"Algoritmo desconocido: {algorithm}")