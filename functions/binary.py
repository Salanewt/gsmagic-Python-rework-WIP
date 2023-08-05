import os
from PIL import Image

class Bits:
    @staticmethod
    def open_file(filename):
        try:
            with open(filename, 'rb') as file:
                return file.read()
        except:
            return None

    @staticmethod
    def open_file_part(filename, addr, size):
        with open(filename, 'rb') as file:
            file.seek(addr)
            data = file.read(size)
        return data

    @staticmethod   
    def save_file_part(filename, addr, size, data):
        with open(filename, 'r+b') as file:
            file.seek(addr)
            file.write(data[:size])
        return data

    @staticmethod
    def save_file(filename, buffer):
        with open(filename, 'wb') as file:
            file.write(buffer)

    @staticmethod
    def get_int16(buffer, pos):
        return buffer[pos] | (buffer[pos + 1] << 8)

    @staticmethod    
    def set_int16(buffer, pos, value):
        buffer[pos] = value & 0xFF
        buffer[pos + 1] = (value >> 8) & 0xFF

    @staticmethod
    def get_int32(buffer, pos):
        return (buffer[pos] | (buffer[pos + 1] << 8) | (buffer[pos + 2] << 16) | (buffer[pos + 3] << 24))

    @staticmethod
    def set_int32(buffer, pos, value):
        buffer[pos] = value & 0xFF
        buffer[pos + 1] = (value >> 8) & 0xFF
        buffer[pos + 2] = (value >> 16) & 0xFF
        buffer[pos + 3] = (value >> 24) & 0xFF

    @staticmethod
    def get_uint32(buffer, pos):
        return buffer[pos] | (buffer[pos + 1] << 8) | (buffer[pos + 2] << 16) | (buffer[pos + 3] << 24)

    @staticmethod
    def get_bits(buf, addr, num_of_bits):
        value = 0
        for i in range(0, num_of_bits, 8):
            value |= buf[addr] << i
            addr += 1
        return value

    @staticmethod
    def set_bits(buf, addr, num_of_bits, value):
        for j in range(0, num_of_bits, 8):
            buf[addr + (j >> 3)] = value & 0xFF
            value >>= 8

    @staticmethod
    def get_string(buffer, pos, length):
        strbuild = []
        while length > 0:
            strbuild.append(chr(buffer[pos]))
            pos += 1
            length -= 1
        return ''.join(strbuild)

    @staticmethod
    def get_text_long(txt, index):
        strbuild = []
        src_entry = index
        p = 0
        n = 0
        str_pos = 0xC300 + Bits.getInt32(txt, src_entry * 4)
        while n != 0:
            n = txt[src_pos]
            src_pos += 1
            if n != 0:
                if n < 32 or n > 0x7E:  # ~
                    strbuild.append('[' + str(n) + ']')
                    # Commands 17, 18, 19, 20, 26, and 29 may have args that use 1 and 3 = Skip these.
                    if (n == 1 or n == 3) and (p < 17 or p > 20) and p != 26 and p != 29:
                        strbuild.append("\r\n")
                        # n = 0
                else:
                    strbuild.append(chr(n))
            p = n
        return ''.join(strbuild)

    @staticmethod
    def text_to_bytes(items):
        bytes_array = bytearray(0x80000)
        a = 0
        b = 0
        for item in items:
            bytes_array[a] = b & 0xFF
            bytes_array[a + 1] = (b >> 8) & 0xFF
            bytes_array[a + 2] = (b >> 16) & 0xFF
            bytes_array[a + 3] = (b >> 24) & 0xFF
            a += 4
            for char in item:
                bytes_array[0xC300 + b] = char
                b += 1
            bytes_array[b] = 0
            b += 1
        return bytes_array

    @staticmethod
    def num_list(range_val):
        return list(range(range_val))

    @staticmethod
    def num_list_with_start(start, range_val):
        return list(range(start, start + range_val))

    @staticmethod
    def get_text_short(txt, index):
        p = 0
        n = 0
        strbuild = []
        if index < 0:
            return ""  # Blank string in case -1 should be used!
        src_pos = Bits.getInt32(txt, index << 2)
        if Bits.getInt32(txt, 0) == 0:
            src_pos += 0xC300
        while n != 0:
            n = txt[src_pos]
            src_pos += 1
            if n != 0:
                if n < 32 or n > 0x7E:  # ~
                    strbuild.append('[' + str(n) + ']')
                    # Commands 17, 18, 19, 20, 26, and 29 may have args that use 1 and 3 = Skip these.
                    if (n == 1 or n == 3) and (p < 17 or p > 20) and p != 26 and p != 29:
                        n = 0
                else:
                    strbuild.append(chr(n))
            p = n
        return ''.join(strbuild)
    
    @staticmethod
    def list_words(txt):
        qq = 0
        if qq == 1:
            return

        qq += 1
        limit = 15000
        words = [None] * limit
        freq = [0] * limit
        word_count = 0
        strbuild = []
        for index in range(12461):
            src_pos = Bits.getInt32(txt, index << 2)
            if Bits.getInt32(txt, 0) == 0:
                src_pos += 0xC300
            while True:
                n = txt[src_pos]
                src_pos += 1
                if n > 0x40 and n != 0xDF:
                    n |= 0x20
                if (n == 0x27) or (n >= 0x61 and n <= 0x7A) or (n >= 0xDF):
                    strbuild.append(chr(n))
                else:
                    if strbuild:
                        str2 = ''.join(strbuild)
                        strbuild.clear()
                        if word_count == limit:
                            break
                        i = 0
                        for i in range(word_count):
                            if words[i] == str2:
                                freq[i] += 1
                                break
                        if i == word_count:
                            words[i] = str2
                            freq[i] += 1
                            word_count += 1
            if word_count == limit:
                break
        words_with_freq = [(str(i + 1) + "\t" + words[i] + "\t" + str(freq[i])) for i in range(word_count)]
        return words_with_freq

    @staticmethod
    def get_text_matches(txt, str_input, items):
        bytes_array = bytearray(0x200)
        a = 0
        b = 0
        while a < len(str_input):
            if str_input[a] == '[':
                num = 0
                a += 1
                while str_input[a] != ']':
                    num = (num * 10) + int(str_input[a]) - 0x30
                    a += 1
                a += 1
                bytes_array[b] = num & 0xFF
                b += 1
            elif str_input[a] == '\r' and str_input[a + 1] == '\n':
                a += 2
            else:
                bytes_array[b] = ord(str_input[a])
                a += 1
                b += 1

        match_list = []
        for i in items:
            src_entry = i * 4
            if src_entry < 0 or src_entry > 12460 * 4:
                if bytes_array[0] == 0:
                    match_list.append(i)
                continue

            src_pos = 0xC300 + Bits.getInt32(txt, src_entry)
            n = 0
            while True:
                if bytes_array[n] == 0:
                    match_list.append(i)
                    break
                if txt[src_pos + n] == 0:
                    break
                if txt[src_pos + n] == bytes_array[n]:
                    n += 1
                    continue

                # Not case sensitive check:
                if 0x41 <= (txt[src_pos + n] & 0xDF) <= 0x5A:  # Letters-only
                    if (txt[src_pos + n] ^ 0x20) == bytes_array[n]:
                        n += 1
                        continue

                src_pos += 1
                n = 0

        return match_list

    @staticmethod
    def pixels_to_image(array, width, height, zoom):
        if zoom <= 0:
            return Image.new('RGB', (1, 1))
        
        new_width = width * zoom
        new_height = height * zoom
        array2 = [0] * (new_width * new_height)

        i = 0
        for yt in range(0, new_height * (new_width * zoom), (new_width * zoom) * zoom):
            for xt in range(yt, yt + (new_width * zoom), zoom):
                palt = array[i]
                for y in range(xt, xt + (new_width * zoom) * zoom, new_width * zoom):
                    for x in range(y, y + zoom):
                        array2[x] = palt
                i += 1

        return Bits.pixels_to_image(array2, new_width, new_height)

    @staticmethod
    def pixels_to_image(array, width, height):
        # Assuming the array contains pixel values in RGBA format (32-bit pixels)
        pixel_array = bytearray(array)
        bitmap = Image.frombytes('RGBA', (width, height), pixel_array)
        return bitmap