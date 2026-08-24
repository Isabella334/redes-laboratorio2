import socket
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from layers import link


def decode_message(bits):
    chars = [bits[i:i + 8] for i in range(0, len(bits), 8)]
    return "".join(chr(int(char, 2)) for char in chars)


def _parse_metadata(metadata_str):
    if not metadata_str:
        return {}

    metadata = {}

    for pair in metadata_str.split(","):
        key, value = pair.split("=")
        metadata[key] = int(value)

    return metadata


def process_connection(connection: socket.socket) -> None:
    received_data = b""

    while not received_data.endswith(b"\n"):
        chunk = connection.recv(4096)

        if not chunk:
            break

        received_data += chunk

    message = received_data.decode("utf-8").strip()
    algorithm, metadata_str, frame = message.split("|", 2)
    metadata = _parse_metadata(metadata_str)

    print(
        f"\nFrame recibida ({len(frame)} bits) "
        f"utilizando el algoritmo: {algorithm}"
    )

    if metadata:
        print(f"Metadatos recibidos: {metadata}")

    data_bits, error = link.verify_integrity(
        frame,
        algorithm,
        metadata
    )

    if algorithm == "hamming":
        text = decode_message(data_bits)

        if error:
            print(
                "Se detectaron y corrigieron errores de un solo bit "
                "en cada bloque afectado."
            )

        print(f"Mensaje decodificado: {text}")

    else:
        if error:
            print(
                "ERROR: Se detectó un error en el frame "
                "y no puede ser corregido."
            )
        else:
            text = decode_message(data_bits)
            print(f"Mensaje decodificado: {text}")


def start_receiver(port: int = 5000) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", port))
        server.listen(1)

        print(f"Receptor de prueba escuchando en el puerto {port}...")

        while True:
            connection, address = server.accept()

            with connection:
                process_connection(connection)


if __name__ == "__main__":
    start_receiver()