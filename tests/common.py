import os
import random
import string
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "emisor-python"))

from algorithms import crc32, hamming 
from layers import noise, presentation

RANDOM_SEED = 42
ALPHABET = string.ascii_letters + string.digits + " .,!?"

def random_text(n_chars, rng):
    return "".join(rng.choice(ALPHABET) for _ in range(n_chars))

def new_rng():
    return random.Random(RANDOM_SEED)

def encode_text(text):
    return presentation.encode_message(text)

def apply_noise(frame, error_rate, rng):
    return "".join( ("1" if bit == "0" else "0") if rng.random() < error_rate else bit for bit in frame)

__all__ = [
    "crc32",
    "hamming",
    "noise",
    "random_text",
    "new_rng",
    "encode_text",
    "apply_noise",
]
