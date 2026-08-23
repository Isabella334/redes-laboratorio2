from layers import app, presentation, link, noise, transmission

def main() -> None:
    datos = app.request_message()
    bits = presentation.encode_message(datos["text"])
    frame, metadata = link.calculate_integrity(bits, datos["algorithm"], datos["r"])
    frame_con_ruido = noise.apply_noise(frame, datos["error_rate"])
    app.show_send_summary(datos, frame, frame_con_ruido, metadata)
    transmission.send_information(
        host=datos["host"],
        puerto=datos["port"],
        algoritmo=datos["algorithm"],
        trama=frame_con_ruido,
        metadata=metadata,
    )

if __name__ == "__main__":
    main()