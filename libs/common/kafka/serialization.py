import msgpack


def pack_data(data: dict) -> bytes:
    return msgpack.packb(data, use_bin_type=True)


def unpack_data(data: bytes) -> dict:
    return msgpack.unpackb(data, raw=False)
