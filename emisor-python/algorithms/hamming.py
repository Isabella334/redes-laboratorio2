def calculate_r(m):
    if m < 1:
        raise ValueError("m must be a positive integer")

    r = 1
    while (m + r + 1) > 2 ** r:
        r += 1

    return r


def calculate_m(r):
    if r < 1:
        raise ValueError("r must be a positive integer")

    m = 2 ** r - r - 1

    if m < 1:
        raise ValueError(
            f"r={r} is too small: there is no space left for data bits"
        )

    return m


def encode(data, r):
    m = len(data)
    n = m + r
    block = [0] * (n + 1)

    data_iter = iter(data)

    for pos in range(1, n + 1):
        if not (pos > 0 and (pos & (pos - 1)) == 0):
            block[pos] = int(next(data_iter))

    for i in range(r):
        parity_pos = 2 ** i
        parity = 0

        for pos in range(1, n + 1):
            if pos & parity_pos:
                parity ^= block[pos]

        block[parity_pos] = parity

    return "".join(str(bit) for bit in block[1:])


def decode(codeword, r):
    n = len(codeword)
    block = [0] + [int(bit) for bit in codeword]

    syndrome = 0

    for i in range(r):
        parity_pos = 2 ** i
        parity = 0

        for pos in range(1, n + 1):
            if pos & parity_pos:
                parity ^= block[pos]

        if parity != 0:
            syndrome += parity_pos

    error = syndrome != 0

    if error:
        if syndrome <= n:
            block[syndrome] ^= 1

    data = "".join(
        str(block[pos])
        for pos in range(1, n + 1)
        if not (pos > 0 and (pos & (pos - 1)) == 0)
    )

    return data, error


def calculate_integrity(bits, r: int = 4):
    m = calculate_m(r)

    padding = (-len(bits)) % m
    padded_bits = bits + "0" * padding

    encoded_blocks = [
        encode(padded_bits[i:i + m], r)
        for i in range(0, len(padded_bits), m)
    ]

    frame = "".join(encoded_blocks)

    return frame, padding


def correct_message(frame, r: int = 4, padding: int = 0):
    m = calculate_m(r)
    n = m + r

    if len(frame) % n != 0:
        raise ValueError(
            f"The received frame ({len(frame)} bits) is not a multiple "
            f"of the expected block size (n={n} for r={r})."
        )

    data_blocks = []
    error_check = False

    for i in range(0, len(frame), n):
        block = frame[i:i + n]
        block_data, block_error = decode(block, r)

        data_blocks.append(block_data)
        error_check = error_check or block_error

    data = "".join(data_blocks)

    if padding:
        data = data[:-padding]

    return data, error_check