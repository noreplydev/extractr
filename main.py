#!/usr/bin/env python3
import logging
import sys
import numpy as np
import os
from gguf.gguf_reader import GGUFReader

logger = logging.getLogger("reader")


def parse_memmap(value):
    """
    normalize np.memmap values:
    - uint8 1D -> UTF-8
    - length 1 -> scalar python
    - number -> list
    - bool -> list of bools
    """

    arr = np.asarray(value)

    # text
    if arr.dtype == np.uint8:
        raw = arr.tobytes()  
        try:
            txt = raw.decode("utf-8")
            return txt
        except UnicodeDecodeError:
            # cannot decode as UTF8 return as intlist
            return arr.tolist()

    # scalar
    if arr.size == 1:
        return arr.reshape(()).item()

    # number
    if arr.dtype.kind in ("i", "u"):   # int
        return arr.astype(np.int64, copy=False).tolist()
    if arr.dtype.kind == "f":          # float
        return arr.astype(np.float64, copy=False).tolist()
    if arr.dtype.kind == "b":          # bool
        return arr.astype(np.bool_, copy=False).tolist()

    # fallback
    return arr.tolist()


def read_gguf_fields(gguf_file_path):
    reader = GGUFReader(gguf_file_path)

    print("── Model ────")
    print(os.path.basename(gguf_file_path)) 
    print("────────────────────────")
    max_key_length = max(len(key) for key in reader.fields.keys())
    for key, field in reader.fields.items():
        value = field.parts[field.data[0]]
        text = parse_memmap(value)
        print(f"{key:{max_key_length}} : {text}") 


if __name__ == '__main__':
    if len(sys.argv) < 2:
        logger.info("Usage: extractr <gguf_filepath>")
        sys.exit(1)

    gguf_file_path = sys.argv[1]
    try: 
        read_gguf_fields(gguf_file_path)
    except:
        print("Cannot read gguf file:", gguf_file_path)
                    