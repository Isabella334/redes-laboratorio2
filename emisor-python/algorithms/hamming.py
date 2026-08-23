def calc_r(m):
    if m < 1:
        raise ValueError("m debe ser un entero positivo")
    r = 1
    while (m + r + 1) > 2 ** r:
        r += 1
    return r


def mr(r):
    if r < 1:
        raise ValueError("r debe ser un entero positivo")

    m = 2 ** r - r - 1
    if m < 1:
        raise ValueError(
            f"r={r} es demasiado pequeño: no queda espacio para bits de datos"
        )
    return m

def code(datos, r):
    m = len(datos)
    n = m + r
    bloque = [0] * (n + 1)

    iterador_datos = iter(datos)
    for posicion in range(1, n + 1):
        if not (posicion > 0 and (posicion & (posicion - 1)) == 0):
            bloque[posicion] = int(next(iterador_datos))

    for i in range(r):
        posicion_paridad = 2 ** i
        valor_paridad = 0
        for posicion in range(1, n + 1):
            if posicion & posicion_paridad:
                valor_paridad ^= bloque[posicion]
        bloque[posicion_paridad] = valor_paridad

    return "".join(str(bit) for bit in bloque[1:])


def decode(bloque_codigo, r):
    n = len(bloque_codigo)
    bloque = [0] + [int(bit) for bit in bloque_codigo]

    sindrome = 0
    for i in range(r):
        posicion_paridad = 2 ** i
        valor_paridad = 0
        for posicion in range(1, n + 1):
            if posicion & posicion_paridad:
                valor_paridad ^= bloque[posicion]
        if valor_paridad != 0:
            sindrome += posicion_paridad

    hubo_error = sindrome != 0

    if hubo_error:
        if sindrome < n:
            bloque[sindrome] ^= 1

    datos = "".join(
        str(bloque[posicion])
        for posicion in range(1, n + 1)
        if not (posicion > 0 and (posicion & (posicion - 1)) == 0)
    )
    return datos, hubo_error


def calcular_integridad(bits, r: int = 4):
    m = mr(r)

    cantidad_padding = (-len(bits)) % m
    bits_con_padding = bits + "0" * cantidad_padding

    bloques_codificados = [code(bits_con_padding[i:i + m], r) for i in range(0, len(bits_con_padding), m)]

    trama = "".join(bloques_codificados)
    return trama, cantidad_padding


def message_correction(trama, r: int = 4, padding: int = 0):
    m = mr(r)
    n = m + r

    if len(trama) % n != 0:
        raise ValueError(
            f"La trama recibida ({len(trama)} bits) no es múltiplo del "
            f"tamaño de bloque esperado (n={n} para r={r})."
        )

    datos = []
    hubo_algun_error = False

    for i in range(0, len(trama), n):
        bloque = trama[i:i + n]
        datos_bloque, error_en_bloque = code(bloque, r)
        datos.append(datos_bloque)
        hubo_algun_error = hubo_algun_error or error_en_bloque

    datos_completos = "".join(datos)

    if padding:
        datos_completos = datos_completos[:-padding]

    return datos_completos, hubo_algun_error