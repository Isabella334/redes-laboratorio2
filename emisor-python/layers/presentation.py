def encode_message(text):
    return "".join(format(ord(char), "08b") for char in text)