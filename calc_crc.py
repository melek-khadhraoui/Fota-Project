import struct 
import sys

POLY = 0x04C11DB7

def crc32_stm32(data):
    crc = 0xFFFFFFFF
    for i in range(0, len(data), 4):
        chunk = data[i:i+4]
        if len(chunk) < 4:
            chunk = chunk + b'\x00' * (4 - len(chunk))
        chunk_reversed = chunk[::-1]
        word = struct.unpack('>I', chunk_reversed)[0]
        # print(f"Word {i}: 0x{word:08X}")  # Disable debug prints in Jenkins
        crc = crc32_update_word(crc, word)
    return crc

def crc32_update_word(crc, word):
    for i in range(32):
        bit = ((crc >> 31) ^ (word >> (31 - i))) & 1
        crc = (crc << 1) & 0xFFFFFFFF
        if bit:
            crc ^= POLY
    return crc & 0xFFFFFFFF

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python calc_crc.py <firmware_file>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, "rb") as f:
        file_data = f.read()

    crc = crc32_stm32(file_data)
    print(f"{crc:08X}")  # Just print hex CRC without prefix for easy parsing


