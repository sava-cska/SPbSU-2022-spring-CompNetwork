def count_checksum(bytes):
    idx = 0
    sum = 0
    while idx < len(bytes):
        num = int.from_bytes(bytes[idx:(idx + 2)], byteorder='little', signed=False)
        sum = sum ^ num
        idx += 2
    return (1 << 16) - 1 - sum

def check_checksum(bytes, checksum):
    idx = 0
    sum = checksum
    while idx < len(bytes):
        num = int.from_bytes(bytes[idx:(idx + 2)], byteorder='little', signed=False)
        sum = sum ^ num
        idx += 2
    mask = (1 << 16) - 1
    return mask == sum