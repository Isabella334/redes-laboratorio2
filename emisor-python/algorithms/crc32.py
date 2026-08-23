CRC32_POLYNOMIAL = "100000100110000010001110110110111"
CRC_SIZE = 32


def calculate_remainder(bits):
    poly_len = len(CRC32_POLYNOMIAL)
    dividend = list(bits + "0" * CRC_SIZE)

    for i in range(len(bits)):
        if dividend[i] == "1":
            for j in range(poly_len):
                dividend[i + j] = str(
                    int(dividend[i + j]) ^ int(CRC32_POLYNOMIAL[j])
                )

    remainder = "".join(dividend[len(bits):])
    return remainder


def calculate_integrity(bits):
    crc = calculate_remainder(bits)
    return bits + crc


def verify_integrity(frame):
    if len(frame) <= CRC_SIZE:
        raise ValueError("The frame is too short to contain a valid CRC-32")

    data = frame[:-CRC_SIZE]
    received_crc = frame[-CRC_SIZE:]
    calculated_crc = calculate_remainder(data)

    error = calculated_crc != received_crc
    return data, error


def correct_message(frame):
    data, error = verify_integrity(frame)
    return data, error