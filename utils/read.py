import os

BITS_IN_BYTE = 8

SUPPORTED_SYMBOL_LENS = (1, 2, 4, 8)
DEFAULT_SYMBOL_LEN = 4

# A bitmask to extract the low symbol_len bits from an integer.
# Note: the bitmask for an 8-bit symbol is unnecessary since we can just take the byte as it is.
_mask = {
    1: 0b00000001,
    2: 0b00000011,
    4: 0b00001111,
}

# Read 1MB chunks by default
DEFAULT_CHUNK_LEN = 1048576


def bytes_needed(N: int) -> int:
    """Returns the minimum number of bytes needed to represent N bits.

    Parameters
    ----------
    N : int
        The number of bits to represent

    Returns
    -------
    int
        The minimum number of bytes needed to represent N bits
    """
    return (N + BITS_IN_BYTE - 1) // BITS_IN_BYTE


def symbols_from_bytes(b: bytes, symbol_len: int = DEFAULT_SYMBOL_LEN) -> list[int]:
    """Extract a list of symbols from a bytes object.

    Parameters
    ----------
    b : bytes
        the input bytes object
    symbol_len : int
        the symbol length in bits

    Returns
    -------
    list of int
        the list of symbols
    """
    if symbol_len not in SUPPORTED_SYMBOL_LENS:
        raise ValueError(f"Unsupported symbol_len: {symbol_len}, supported {SUPPORTED_SYMBOL_LENS}")
    # Short-circuit in the case of 8-bit symbols
    if symbol_len == BITS_IN_BYTE:
        return list(b)

    symbols_in_byte = BITS_IN_BYTE // symbol_len
    S = [0] * (len(b) * symbols_in_byte)
    for i in range(len(b)):
        for j in range(symbols_in_byte):
            S[(i * symbols_in_byte) + j] = (b[i] >> ((symbols_in_byte - j - 1) * symbol_len)) & _mask[symbol_len]
    return S


def read_file(file: str, n_symbols: int, symbol_len: int = DEFAULT_SYMBOL_LEN, first_seq: bool = True) -> list[int]:
    """Reads a sequence of bytes from a binary file and transforms it into a sequence of symbols by
    applying a masking process

    Parameters
    ----------
    file : str
        path to file
    n_symbols : int
        number of symbols
    symbol_len : int
        the symbol length in bits (supported lengths: 1, 2, 4, 8)
    first_seq : bool
        read the first or last sequence from the file

    Returns
    -------
    list of int
        sequence of symbols
    """
    if symbol_len not in SUPPORTED_SYMBOL_LENS:
        raise ValueError(f"Unsupported symbol_len: {symbol_len}, supported {SUPPORTED_SYMBOL_LENS}")

    n_bytes = bytes_needed(n_symbols * symbol_len)

    file_size = os.path.getsize(file)
    if n_bytes > file_size:
        raise ValueError(f"File too small (size: {file_size}B, requested: {n_bytes}B): {file}")

    with open(file, "rb") as f:
        if not first_seq:
            f.seek(-n_bytes, os.SEEK_END)
        b = f.read(n_bytes)

    return symbols_from_bytes(b, symbol_len)


def read_file_chunks(file: str, n_bytes: int = DEFAULT_CHUNK_LEN):
    """Reads a binary file in chunks.

    Returns a bytes object of n_bytes elements. If less than n_bytes are available in the file (e.g. small file, or
    reading the last chunk), returns between 0 and n_bytes elements.

    Parameters
    ----------
    file : str
        the input file
    n_bytes : int
        size in bytes of the chunk to read

    Returns
    -------
    bytes generator
        a generator expression producing the binary file chunk by chunk
    """
    with open(file, "rb") as f:
        while b := f.read(n_bytes):
            yield b
