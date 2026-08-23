import socket

def serialize_metadata(metadata):
    return ",".join(f"{clave}={valor}" for clave, valor in metadata.items())

def send_information(host, puerto, algoritmo, trama, metadata):
    metadata_str = serialize_metadata(metadata)
    mensaje = f"{algoritmo}|{metadata_str}|{trama}\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
        cliente.connect((host, puerto))
        cliente.sendall(mensaje.encode("utf-8"))

    print(f"Frame enviado correctamente a {host}:{puerto} ({len(trama)} bits)")