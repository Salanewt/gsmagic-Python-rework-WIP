from datetime import datetime
from functions.binary import Bits

class Compression:
    bitTable = [0x1, 0x0, 0x3, 0x1, 0x4, 0x5, 0x4, 0xD,
            0x4, 0x3, 0x4, 0xB, 0x4, 0x7, 0x6, 0xF,
            0x6, 0x2F, 0x6, 0x1F, 0x8, 0x3F, 0x8, 0xBF,
            0x8, 0x7F, 0xA, 0xFF, 0xA, 0x2FF, 0xA, 0x1FF,
            0xA, 0x3FF]

    @staticmethod
    def decompress(src, srcPos, des, desPos):
        return Compression.decompressf(src, srcPos + 1, des, desPos, src[srcPos])

    @staticmethod
    def decompressf(src, srcPos, des, desPos, format):
        desStart = desPos
        bits = 0
        readcount = 0
        i = 0
        _byte = 0
        n = 0
        z = 0xFEDCBA9876543210

        if format == 0 or format == 2:
            bitnum = 0
            if srcPos & 1 == 1:
                bits = src[srcPos]
                bitnum = 8
                srcPos += 1
            bits += src[srcPos] << bitnum
            srcPos += 1
            bits += src[srcPos] << (8 + bitnum)
            srcPos += 1

            while True:
                readcount = 0
                if bits & 1 == 1:
                    bits >>= 1
                    bitnum -= 1
                    if format == 0:
                        des[desPos] = bits & 0xFF
                        desPos += 1
                        bits >>= 8
                        bitnum -= 8
                    else:
                        if bits & 1 == 1:
                            i = 2
                            bits >>= 1
                            bitnum -= 1
                        elif bits & 2 == 2:
                            i = 3
                            bits >>= 2
                            bitnum -= 2
                        else:
                            i = 4
                            bits >>= 2
                            bitnum -= 2

                        for offset in range(0, 8, 4):
                            _byte = bits & ((1 << i) - 1)
                            bits >>= i
                            bitnum -= i
                            n = (0xF & (z >> (_byte << 2)))
                            if _byte != 0xF:
                                z = (z & ((-1) << ((_byte + 1) << 2))) | ((z & (((1 << (_byte << 2)) - 1)) << 4)) | n
                            else:
                                z = (z << 4) | n
                            des[desPos] |= n << offset
                            desPos += 1

                elif bits & 3 == 0:
                    readcount = 2
                    bits >>= 2
                    bitnum -= 2
                elif bits & 7 == 2:
                    readcount = 3
                    bits >>= 3
                    bitnum -= 3
                elif bits & 0xF == 6:
                    readcount = 4
                    bits >>= 4
                    bitnum -= 4
                elif bits & 0x1F == 0xE:
                    readcount = 5
                    bits >>= 5
                    bitnum -= 5
                elif bits & 0x7F == 0x1E:
                    readcount = 6
                    bits >>= 7
                    bitnum -= 7
                elif bits & 0x7F == 0x5E:
                    readcount = 7
                    bits >>= 7
                    bitnum -= 7
                elif bits & 0x3F == 0x3E:
                    readcount = 7 + ((bits >> 6) & 3)
                    bits >>= 8
                    bitnum -= 8
                    if readcount == 7:
                        readcount = 10 + (bits & 127)
                        bits >>= 7
                        bitnum -= 7
                        if readcount == 10:
                            return srcPos, desPos

                if bitnum < 0:
                    bitnum += 16
                    bits += (src[srcPos] << bitnum) + (src[srcPos + 1] << (8 + bitnum))
                    srcPos += 2

                if readcount != 0:
                    offset = 0
                    if bits & 1 == 0:
                        bits >>= 1
                        bitnum -= 1
                        offset = desPos - desStart - 33
                        _byte = 12
                        while offset < (1 << (_byte - 1)):
                            _byte -= 1
                        offset = 32 + (bits & ((1 << _byte) - 1))
                        bits >>= _byte
                        bitnum -= _byte
                    else:
                        bits >>= 1
                        bitnum -= 1
                        offset = bits & 31
                        bits >>= 5
                        bitnum -= 5

                    if bitnum < 0:
                        bitnum += 16
                        bits += (src[srcPos] << bitnum) + (src[srcPos + 1] << (8 + bitnum))
                        srcPos += 2

                    while readcount > 0:
                        des[desPos] = des[desPos - offset - 1]
                        desPos += 1
                        readcount -= 1

        else:  # Format 1
            while True:
                bits = src[srcPos]
                srcPos += 1
                for j in range(0x80, 0, -1):
                    if bits & j == 0:
                        des[desPos] = src[srcPos]
                        desPos += 1
                        srcPos += 1
                    else:
                        readcount = src[srcPos]
                        srcPos += 1
                        offset = src[srcPos] | ((readcount & 0xF0) << 4)
                        readcount = readcount & 15
                        if readcount == 0:
                            if offset == 0:
                                return srcPos, desPos

                            readcount = src[srcPos] + 16
                            srcPos += 1

                        while readcount >= 0:
                            des[desPos] = des[desPos - offset]
                            desPos += 1
                            readcount -= 1

    @staticmethod
    def compressFormat1(src, srcPos, des, desPos):
        return Compression.compressFormat1Internal(src, srcPos, len(src), des, desPos)

    @staticmethod
    def compressFormat1Internal(src, srcPos, srcLen, des, desPos):
        c = datetime.now()

        idx = [0] * 0x10000
        value = src[0]
        idxl = [0] * 0x100

        for i in range(len(src)):
            idx[i] = idxl[src[i]]
            if value == src[i]:
                continue
            idxl[value] = i
            value = src[i]

        dst = 0
        length = 0
        srcStart = srcPos

        while True:
            fPos = desPos
            des[fPos] = 0

            for a in range(0x80, 0, -1):
                if srcPos >= srcLen:
                    des[fPos] |= a
                    des[desPos + 1] = 0
                    des[desPos + 2] = 0
                    print(datetime.now() - c, "(Compression)")
                    return srcPos, desPos

                sp2 = srcPos + 1
                dst2 = 0
                len2 = 0
                maxLen2 = min(0x110, srcLen - sp2)
                dictEnd2 = max(srcStart, sp2 - 0xFFF)
                j = 0

                while j < maxLen2:
                    if src[sp2] != src[sp2 + j]:
                        break
                    j += 1

                target = j
                progress = j - 1

                for i in range(sp2 - 1, dictEnd2 - 1, -1):
                    if src[sp2] == src[i]:
                        progress += 1
                    else:
                        if progress > 0:
                            i = idx[i]
                        progress = 0
                        continue

                    if progress > target:
                        continue

                    j = progress
                    if progress == target:
                        while j < maxLen2:
                            if src[sp2 + j] != src[i + j]:
                                break
                            j += 1

                    if j > len2:
                        dst2 = i
                        len2 = j

                        if j >= 0x10F:
                            break

                sp3 = srcPos + length
                dst3 = 0
                len3 = 0
                maxLen3 = min(0x110, srcLen - sp3)
                dictEnd3 = max(srcStart, sp3 - 0xFFF)
                j = 0

                while j < maxLen3:
                    if src[sp3] != src[sp3 + j]:
                        break
                    j += 1

                target = j
                progress = j - 1

                for i in range(sp3 - 1, dictEnd3 - 1, -1):
                    if maxLen3 <= 0:
                        break

                    if src[sp3] == src[i]:
                        progress += 1
                    else:
                        if progress > 0:
                            i = idx[i]
                        progress = 0
                        continue

                    if progress > target:
                        continue

                    j = progress
                    if progress == target:
                        while j < maxLen3:
                            if src[sp3 + j] != src[i + j]:
                                break
                            j += 1

                    if j > len3:
                        dst3 = i
                        len3 = j

                        if j >= 0x10F:
                            break

                if len2 == 0:
                    len2 = 1
                if len3 == 0:
                    len3 = 1

                if (1 + len2) >= (length + len3):
                    length = 1
                else:
                    if len < 2:
                        des[desPos + 1] = src[srcPos]
                        srcPos += 1
                        dst = dst2
                        length = len2
                    else:
                        des[fPos] |= a
                        if length <= 16:
                            des[desPos + 1] = ((srcPos - dst) >> 8) << 4 | (length - 1)
                            des[desPos + 2] = (srcPos - dst) & 0xFF
                        else:
                            des[desPos + 1] = ((srcPos - dst) >> 8) << 4
                            des[desPos + 2] = (srcPos - dst) & 0xFF
                            des[desPos + 3] = length - 16 - 1

                        srcPos += length
                        dst = dst3
                        length = len3

                desPos += 1

    @staticmethod
    def compressFormat1Old(src, srcPos, srcLen, des, desPos):
        c = datetime.now()

        dst = 0
        length = 0
        srcStart = srcPos

        while True:
            fPos = desPos
            des[fPos] = 0

            for a in range(0x80, 0, -1):
                if srcPos >= srcLen:
                    des[fPos] |= a
                    des[desPos + 1] = 0
                    des[desPos + 2] = 0
                    print(datetime.now() - c, "(Compression)")
                    return srcPos, desPos

                sp2 = srcPos + 1
                dst2 = 0
                len2 = 0
                maxLen2 = min(0x110, srcLen - sp2)
                dictEnd2 = max(srcStart, sp2 - 0xFFF)

                for i in range(sp2 - 1, dictEnd2 - 1, -1):
                    j = 0

                    while j < maxLen2:
                        if src[sp2 + j] != src[i + j]:
                            break
                        j += 1

                    if j > len2:
                        dst2 = i
                        len2 = j

                        if j >= 0x10F:
                            break

                sp3 = srcPos + length
                dst3 = 0
                len3 = 0
                maxLen3 = min(0x110, srcLen - sp3)
                dictEnd3 = max(srcStart, sp3 - 0xFFF)

                for i in range(sp3 - 1, dictEnd3 - 1, -1):
                    j = 0

                    while j < maxLen3:
                        if src[sp3 + j] != src[i + j]:
                            break
                        j += 1

                    if j > len3:
                        dst3 = i
                        len3 = j

                        if j >= 0x10F:
                            break

                if len2 == 0:
                    len2 = 1
                if len3 == 0:
                    len3 = 1

                if (1 + len2) >= (length + len3):
                    length = 1
                else:
                    if len < 2:
                        des[desPos + 1] = src[srcPos]
                        srcPos += 1
                        dst = dst2
                        length = len2
                    else:
                        des[fPos] |= a
                        if length <= 16:
                            des[desPos + 1] = ((srcPos - dst) >> 8) << 4 | (length - 1)
                            des[desPos + 2] = (srcPos - dst) & 0xFF
                        else:
                            des[desPos + 1] = ((srcPos - dst) >> 8) << 4
                            des[desPos + 2] = (srcPos - dst) & 0xFF
                            des[desPos + 3] = length - 16 - 1

                        srcPos += length
                        dst = dst3
                        length = len3

                desPos += 1

    @staticmethod
    def decompress16All(src, srcPos):
        entries = 0
        srcPos2 = srcPos

        while Bits.getInt32(src, srcPos2) != -1:
            entries += 1
            srcPos2 += 4

        des = bytearray(entries * 0x100)

        for desPos in range(0, len(des), 0x100):
            Compression.decompress16(src, Bits.getInt32(src, srcPos) & 0x1ffffff, des, desPos)
            srcPos += 4

        return des

    @staticmethod
    def decompress16(src, srcPos, des, desPos):
        bits = 0
        i = 0
        bitnum = 0
        n = 0
        z = 0xFEDCBA9876543210

        bits += (src[srcPos] << bitnum) + (src[srcPos + 1] << (8 + bitnum))
        srcPos += 2

        while True:
            if bits & 0x1 == 0x0:
                i = 0
                bits >>= 1
                bitnum -= 1
            elif bits & 0x7 == 0x1:
                i = 1
                bits >>= 3
                bitnum -= 3
            elif bits & 0xF == 0x5:
                i = 2
                bits >>= 4
                bitnum -= 4
            elif bits & 0xF == 0xD:
                i = 3
                bits >>= 4
                bitnum -= 4
            elif bits & 0xF == 0x3:
                i = 4
                bits >>= 4
                bitnum -= 4
            elif bits & 0xF == 0xB:
                i = 5
                bits >>= 4
                bitnum -= 4
            elif bits & 0xF == 0x7:
                i = 6
                bits >>= 4
                bitnum -= 4
            elif bits & 0x3F == 0xF:
                i = 7
                bits >>= 6
                bitnum -= 6
            elif bits & 0x3F == 0x2F:
                i = 8
                bits >>= 6
                bitnum -= 6
            elif bits & 0x3F == 0x1F:
                i = 9
                bits >>= 6
                bitnum -= 6
            elif bits & 0xFF == 0x3F:
                i = 10
                bits >>= 8
                bitnum -= 8
            elif bits & 0xFF == 0xBF:
                i = 11
                bits >>= 8
                bitnum -= 8
            elif bits & 0xFF == 0x7F:
                i = 12
                bits >>= 8
                bitnum -= 8
            elif bits & 0x3FF == 0xFF:
                i = 13
                bits >>= 10
                bitnum -= 10
            elif bits & 0x3FF == 0x2FF:
                i = 14
                bits >>= 10
                bitnum -= 10
            elif bits & 0x3FF == 0x1FF:
                i = 15
                bits >>= 10
                bitnum -= 10
            elif bits & 0x3FF == 0x3FF:
                return

            n = (0xF & (z >> (i << 2)))  # Get selected value.

            if i != 0xF:
                z = (z & ((-1) << ((i + 1) << 2))) | ((z & (((1 << (i << 2)) - 1)) << 4)) | n
            else:
                z = (z << 4) | n

            des[desPos] = n  # Write decompressed 4-bit.
            desPos += 1

            if bitnum < 0:
                bitnum += 16
                bits += (src[srcPos] << bitnum) + (src[srcPos + 1] << (8 + bitnum))
                srcPos += 2

    @staticmethod
    def compress16(src, srcPos, des, desPos):
        bitnum = 0
        bits = 0
        i = 0
        n = 0
        z = 0xFEDCBA9876543210

        while srcPos < len(src):
            while (z >> i) & 0xF != src[srcPos]:
                i += 4

            bits = bits | (Compression.bitTable[(i >> 1) + 1] << bitnum)
            bitnum += Compression.bitTable[i >> 1]

            while bitnum >= 8:
                des[desPos] = bits & 0xFF
                bits >>= 8
                bitnum -= 8
                desPos += 1

            n = 0xF & (z >> i)  # Get selected value.

            if i != 0x3C:  # Check 0xF because <<0x40 does nothing. (ex: no-op?)
                z = (z & ((1 << (i + 4)) - 1)) | ((z & ((1 << i) - 1)) << 4) | n
            else:
                z = (z << 4) | n

            srcPos += 1

        bits = bits | (Compression.bitTable[0x21] << bitnum)
        bitnum += Compression.bitTable[0x20]

        while bitnum > 0:
            des[desPos] = bits & 0xFF
            bits >>= 8
            bitnum -= 8
            desPos += 1

    @staticmethod
    def decompBtlBG(src, srcPos):
        des = bytearray(0x8000)
        desPos = 0
        bits = 0
        i = 0x60
        bitnum = 0

        bits += (src[srcPos] << bitnum) + (src[srcPos + 1] << (8 + bitnum))
        srcPos += 2

        for j in range(0x7800):
            case = bits & 7
            if case == 0 or case == 4:
                bits >>= 2
                bitnum -= 2
            elif case == 1:
                bits >>= 3
                bitnum -= 3
                i += 1 + (bits & 1)
                bits >>= 1
                bitnum -= 1
            elif case == 2:
                bits >>= 3
                bitnum -= 3
                if bits & 1 == 0:
                    bits >>= 1
                    bitnum -= 1
                    i += 11 + (bits & 0xF)
                    bits >>= 4
                    bitnum -= 4
                else:
                    bits >>= 1
                    bitnum -= 1
                    i -= 11 + (bits & 0xF)
                    bits >>= 4
                    bitnum -= 4
            elif case == 3:
                bits >>= 3
                bitnum -= 3
                i += 3 + (bits & 7)
                bits >>= 3
                bitnum -= 3
            elif case == 5:
                bits >>= 3
                bitnum -= 3
                i -= 1 + (bits & 1)
                bits >>= 1
                bitnum -= 1
            elif case == 6:
                bits >>= 3
                bitnum -= 3
                i = 0x60 + (bits & 0x7F)
                bits >>= 7
                bitnum -= 7
            elif case == 7:
                bits >>= 3
                bitnum -= 3
                i -= 3 + (bits & 7)
                bits >>= 3
                bitnum -= 3

            des[desPos] = i
            desPos += 1

            if bitnum < 0:
                bitnum += 16
                bits += (src[srcPos] << bitnum) + (src[srcPos + 1] << (8 + bitnum))
                srcPos += 2

        return des

    @staticmethod
    def decompress_text(src):
        total = 0
        total2 = 0
        c = datetime.now()

        asmpchar = Bits.getInt32(src, 0x38578) - 0x8000000
        asmptext = Bits.getInt32(src, 0x385DC) - 0x8000000
        chardata = Bits.getInt32(src, asmpchar) - 0x08000000
        charpntrs = Bits.getInt32(src, asmpchar + 4) - 0x08000000

        maxLetter = 0
        cTreeSize = 0
        maxDepth = 0
        for char1 in range(maxLetter + 1):
            if char1 & 0xFF == 0:
                chardata = Bits.getInt32(src, asmpchar + (char1 >> 8) * 8) - 0x08000000
                charpntrs = Bits.getInt32(src, asmpchar + (char1 >> 8) * 8 + 4) - 0x08000000

            if Bits.getInt16(src, charpntrs) == 0x8000:
                charpntrs += 2
                continue

            total2 += 1
            charTree = (chardata + Bits.getInt16(src, charpntrs)) << 3
            charpntrs += 2
            charSlot = charTree - 12
            depth = 0

            while True:
                while (src[charTree >> 3] >> (charTree & 7) & 1) == 0:
                    depth += 1
                    cTreeSize += 1

                letter = (Bits.getInt16(src, charSlot >> 3) >> (charSlot & 7)) & 0xFFF
                charSlot -= 12
                total += 1
                cTreeSize += 1

                if letter > maxLetter:
                    maxLetter = letter
                if depth > maxDepth:
                    maxDepth = depth

                if depth <= 0:
                    break

                depth -= 1

        chardata = Bits.getInt32(src, asmpchar) - 0x08000000
        charpntrs = Bits.getInt32(src, asmpchar + 4) - 0x08000000
        ctOffsets = [0] * (maxLetter + 1)
        cTree = [0] * cTreeSize
        nodeOffsets = [0] * maxDepth
        pos = 0

        for char1 in range(maxLetter + 1):
            if char1 & 0xFF == 0:
                chardata = Bits.getInt32(src, asmpchar + (char1 >> 8) * 8) - 0x08000000
                charpntrs = Bits.getInt32(src, asmpchar + (char1 >> 8) * 8 + 4) - 0x08000000

            if Bits.getInt16(src, charpntrs) == 0x8000:
                charpntrs += 2
                continue

            charTree = (chardata + Bits.getInt16(src, charpntrs)) << 3
            charpntrs += 2
            charSlot = charTree - 12
            depth = 0

            ctOffsets[char1] = pos
            while True:
                while (src[charTree >> 3] >> (charTree & 7) & 1) == 0:
                    nodeOffsets[depth] = pos
                    depth += 1
                    pos += 1

                cTree[pos] = -((Bits.getInt16(src, charSlot >> 3) >> (charSlot & 7)) & 0xFFF)
                charSlot -= 12
                pos += 1

                if depth <= 0:
                    break

                cTree[nodeOffsets[depth - 1]] = pos
                depth -= 1

        textTree = 0
        textLenAddr = 0
        des = bytearray(0x800000)
        desEntry = 0
        desPos = 0xC300

        for srcI in range(12461):
            Bits.setInt32(des, desEntry, desPos - 0xC300)
            desEntry += 4
            srcInd = srcI

            if srcInd & 0xFF == 0:
                textTree = Bits.getInt32(src, asmptext + ((srcInd >> 8) << 3)) - 0x08000000
                textLenAddr = Bits.getInt32(src, asmptext + ((srcInd >> 8) << 3) + 4) - 0x08000000
            else:
                cLen = src[textLenAddr]
                while cLen == 0xFF:
                    cLen = src[textLenAddr]
                    textTree += cLen
                    textLenAddr += 1

            initChar = 0
            textTree2 = textTree << 3

            while True:
                pos = ctOffsets[initChar]

                while cTree[pos] > 0:
                    if (src[textTree2 >> 3] >> (textTree2 & 7) & 1) == 0:
                        pos += 1
                    else:
                        pos = cTree[pos]
                    textTree2 += 1

                initChar = -cTree[pos]
                des[desPos] = initChar
                desPos += 1

                if initChar == 0:
                    break

        print(datetime.now() - c, "(Text Decompression!)")
        return des

    @staticmethod
    def comptext(src, dest):
        c = datetime.now()
        char1 = 0
        char2 = 0
        freq = [0] * 0x10000
        clen = [0] * 0x100
        clst = [0] * 0x10000

        srcEntry = 0

        while Bits.getInt32(src, srcEntry) != 0 or srcEntry == 0:
            srcPos = 0xC300 + Bits.getInt32(src, srcEntry)
            while True:
                char2 = src[srcPos]

                if char2 == 0:
                    break

                if freq[char1 * 0x100 + char2] == 0:
                    clst[char1 * 0x100 + clen[char1]] = char2
                    clen[char1] += 1

                freq[char1 * 0x100 + char2] += 1
                srcPos += 1
                char1 = char2

            srcEntry += 4

        bitLen = [0] * 0x10000
        bitCode = [0] * 0x10000
        addr2 = 0
        chrptlen = 0
        chrTbl = [0] * 0x8000
        chrPtrs = [0] * 0x200

        for c1 in range(0x100):
            if clen[c1] == 0:
                chrPtrs[(c1 << 1) + 1] = 0x80
                continue

            chrptlen = (c1 + 1) << 1
            for i in range(1, clen[c1]):
                x = clst[(c1 << 8) + i]
                j = i

                while j > 0 and freq[(c1 << 8) + clst[(c1 << 8) + j - 1]] > freq[(c1 << 8) + x]:
                    clst[(c1 << 8) + j] = clst[(c1 << 8) + j - 1]
                    j -= 1

                clst[(c1 << 8) + j] = x

            symbSort = [0] * 0x100
            symbBits = [0] * 0x100
            nodeHead = [0] * 0x100
            nodeTail = [0] * 0x100
            nodeFreq = [0] * 0x100
            nodeFreq[0] = 0x7FFFFFFF
            nodeFreq[1] = 0x7FFFFFFF
            nodeA = 0
            nodeI = 0
            symbI = 0

            if clen[c1] > 1:
                while symbI < clen[c1] or nodeA < nodeI - 1:
                    symfreq1 = freq[(c1 << 8) + clst[(c1 << 8) + symbI]]
                    symfreq2 = freq[(c1 << 8) + clst[(c1 << 8) + symbI + 1]]

                    if symbI + 1 < clen[c1] and symfreq2 <= nodeFreq[nodeA]:
                        symbSort[symbI] = symbI + 1
                        nodeHead[nodeI] = symbI
                        nodeTail[nodeI] = symbI + 1
                        nodeFreq[nodeI] = symfreq1 + symfreq2
                        symbI += 2
                    elif symbI < clen[c1] and symfreq1 <= nodeFreq[nodeA]:
                        symbSort[symbI] = nodeHead[nodeA]
                        nodeHead[nodeI] = symbI
                        nodeTail[nodeI] = nodeTail[nodeA]
                        nodeFreq[nodeI] = symfreq1 + nodeFreq[nodeA]
                        symbI += 1
                        nodeA += 1
                    elif nodeA < nodeI - 1 and (nodeFreq[nodeA + 1] < symfreq1 or symbI >= clen[c1]):
                        symbSort[nodeTail[nodeA]] = nodeHead[nodeA + 1]
                        nodeHead[nodeI] = nodeHead[nodeA]
                        nodeTail[nodeI] = nodeTail[nodeA + 1]
                        nodeFreq[nodeI] = nodeFreq[nodeA] + nodeFreq[nodeA + 1]
                        nodeA += 2
                    elif nodeFreq[nodeA] < symfreq1:
                        symbSort[nodeTail[nodeA]] = symbI
                        nodeHead[nodeI] = nodeHead[nodeA]
                        nodeTail[nodeI] = symbI
                        nodeFreq[nodeI] = nodeFreq[nodeA] + symfreq1
                        symbI += 1
                        nodeA += 1

                    symbBits[clst[(c1 << 8) + nodeHead[nodeI]]] += 1
                    nodeI += 1

            addr2 += (clen[c1] * 12 + 4) & -8
            chrPtrs[c1 << 1] = addr2 >> 3
            chrPtrs[(c1 << 1) + 1] = addr2 >> 11
            addr1 = addr2 - 12
            bitsL = 0
            bitC = 0

            for n in range(clen[c1], 0, -1):
                chrTbl[addr1 >> 3] |= clst[(c1 << 8) + nodeHead[nodeA]] << (addr1 & 7)
                chrTbl[(addr1 >> 3) + 1] |= clst[(c1 << 8) + nodeHead[nodeA]] >> (8 - (addr1 & 7))
                addr1 -= 12
                addr2 += symbBits[clst[(c1 << 8) + nodeHead[nodeA]]]
                chrTbl[addr2 >> 3] |= 1 << (addr2 & 7)
                bitsL += symbBits[clst[(c1 << 8) + nodeHead[nodeA]]]
                bitLen[(c1 << 8) + clst[(c1 << 8) + nodeHead[nodeA]]] = bitsL
                bitCode[(c1 << 8) + clst[(c1 << 8) + nodeHead[nodeA]]] = bitC

                while (bitC >> (bitsL - 1)) & 1 == 1:
                    bitsL -= 1
                    bitC ^= 1 << bitsL

                bitC |= 1 << (bitsL - 1)
                nodeHead[nodeA] = symbSort[nodeHead[nodeA]]

        val = 0
        bitnum = 0
        ctAddr = 0
        cstrstart = 0
        cText = bytearray(len(src))
        txtref1 = bytearray(0x200)
        tr1Addr = 0
        txtref2 = bytearray(0x8000)
        tr2Addr = 0
        srcEntry = 0
        char1 = 0