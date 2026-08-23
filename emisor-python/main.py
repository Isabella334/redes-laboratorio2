from layers import app, presentation, link, noise, transmission

def main() -> None:
    datos = app.request_message()
    bits = presentation.encode_message(datos["texto"])
    frame, metadata = link.calculate_integrity(bits, datos["algoritmo"], datos["r"])
    frame_con_ruido = noise.apply_noise(frame, datos["tasa_error"])
    app.show_send_summary(datos, frame, frame_con_ruido, metadata)
    transmission.send_information(
        host=datos["host"],
        puerto=datos["puerto"],
        algoritmo=datos["algoritmo"],
        frame=frame_con_ruido,
        metadata=metadata,
    )

if __name__ == "__main__":
    main()