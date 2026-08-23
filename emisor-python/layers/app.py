AVAILABLE_ALGORITHMS = {
    "1": "hamming",
    "2": "crc32",
}

def request_message():
    print("##### EMISOR #####\n")

    text = input("Escribe el mensaje a enviar: ")

    print("\nAlgoritmos disponibles:")
    print("  1. Hamming — corrección de errores (tamaño de bloque configurable)")
    print("  2. CRC-32 — detección de errores")
    option = input("Selecciona el algoritmo (1/2): ").strip()

    while option not in AVAILABLE_ALGORITHMS:
        option = input("Opción inválida. Selecciona 1 o 2: ").strip()

    algorithm = AVAILABLE_ALGORITHMS[option]

    r = 4
    if algorithm == "hamming":
        r_input = input("\nBits de paridad a usar en Hamming (Enter para usar 4, que da bloques de 11 bits de datos): ").strip()

        if r_input:
            r = int(r_input)

    error_rate = float(
        input("\nTasa de error del canal (probabilidad de que un bit se invierta): ")
    )

    host = input("\nHost/IP del receptor (ej. 127.0.0.1): ").strip() or "127.0.0.1"
    port = int(input("Puerto del receptor (ej. 5000): ").strip() or "5000")

    return {
        "text": text,
        "algorithm": algorithm,
        "r": r,
        "error_rate": error_rate,
        "host": host,
        "port": port,
    }


def show_send_summary(data, original_frame, noisy_frame, metadata):
    print("\n##### Resumen del envío #####")
    print(f"Mensaje:            {data['text']}")
    print(f"Algoritmo:          {data['algorithm']}")

    if metadata:
        print(f"Metadata:           {metadata}")

    print(f"Tasa de error:         {data['error_rate']}")
    print(f"Frame original:     {original_frame}")
    print(f"Frame con ruido:        {noisy_frame}")
    print(f"Enviado a:         {data['host']}:{data['port']}")