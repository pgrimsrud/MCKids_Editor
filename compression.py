
class BitBuffer:
    def __init__(self, bytes):
        self.data = bytes
        self.bitPtr = 0
        self.bytePtr = 0

    def clear(self):
        self.data.clear()
        self.bitPtr = 0
        self.bytePtr = 0

    def incBitPtr(self):
        self.bitPtr += 1
        if self.bitPtr >= 8:
            self.bitPtr -= 8
            self.bytePtr += 1

    def read_bit(self):
        bit = (self.data[self.bytePtr] >> (7 - self.bitPtr)) & 0x01
        self.incBitPtr()
        return bit

    def read_bits(self, numberOfBits):
        value = 0
        for i in range(numberOfBits):
            value += self.read_bit() << (numberOfBits - 1 - i)
        return value

    def write_bit(self, bit):
        if len(self.data) < self.bytePtr + 1:
            self.data.append(0)
        self.data[self.bytePtr] += bit << (7 - self.bitPtr)
        self.incBitPtr()

    def write_bits(self, value, bits):
        for i in range(bits):
            self.write_bit((value >> bits - 1 - i) & 0x01)

    def write_byte(self, value):
        self.write_bits(value, 8)

    def toByteArray(self):
        return self.data

def decompress_old(data, offset_size, length_size):
    bit_ptr = 0
    result = []
    while 1:
        if (data[bit_ptr>>3] >> (7-(bit_ptr & 7))) & 1 == 1:
            bit_ptr += 1
            byte = 0
            for i in range(0,8):
                byte += ((data[bit_ptr>>3] >> (7-(bit_ptr & 7))) & 1) << (7-i)
                bit_ptr += 1
            result.append(byte)
        else:
            bit_ptr += 1
            offset = 0
            for i in range(0,offset_size):
                offset += ((data[bit_ptr>>3] >> (7-(bit_ptr & 7))) & 1) << (offset_size-1-i)
                bit_ptr += 1
            length = 0
            for i in range(0,length_size):
                length += ((data[bit_ptr>>3] >> (7-(bit_ptr & 7))) & 1) << (length_size-1-i)
                bit_ptr += 1
            if offset == 0 and length == 0:
                break
            length += 3
            for i in range(0,length):
                result.append(result[len(result)-offset])

    return result


def decompress(data, offset_size, length_size):
    output = []
    buffer = BitBuffer(data)
    while 1:
        if buffer.read_bit() == 1:
            output.append(buffer.read_bits(8))
        else:
            offset = buffer.read_bits(offset_size)
            length = buffer.read_bits(length_size)
            if offset == 0 and length == 0:
                break
            length += 3
            for i in range(length):
                output.append(output[len(output) - offset])
    return output

def compress(data, offset_size, length_size):
    ptr = 0
    buffer = BitBuffer([])
    max_offset = (1 << offset_size)
    max_length = (1 << length_size) + 3
    while ptr < len(data):
        offset, length = find_previous_occurance(data, ptr, max_offset, max_length)
        if offset > 0:
            buffer.write_bit(0)
            buffer.write_bits(offset, offset_size)
            buffer.write_bits(length - 3, length_size)
            ptr += length
        else:
            buffer.write_bit(1)
            buffer.write_byte(data[ptr])
            ptr += 1

    buffer.write_bit(0)
    buffer.write_bits(0, offset_size)
    buffer.write_bits(0, length_size)
    return buffer.toByteArray()

def find_previous_occurance(data, ptr, max_offset, max_length):
    longest_found = 0
    found_offset = 0
    for i in range(1, min(max_offset, len(data))):
        length = 0
        while (len(data) > ptr + length) and (length + 1 < max_length) and (ptr + length - i >= 0) and (data[ptr + length] == data[ptr + length - i]):
            length += 1

        if length >= 3 and length > longest_found:
            longest_found = length
            found_offset = i

    return found_offset, longest_found


