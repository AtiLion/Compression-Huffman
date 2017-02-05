#!/usr/bin/python

import sys
import os.path

# The node that will be used in the tree for lookup
class huffman_node:
    def __init__(self, value, frequency, val_left = None, val_right = None):
        self.value = value
        self.frequency = frequency
        self.val_left = val_left
        self.val_right = val_right
        self.active = True
        self.bits = []
        self.parent = None

# Used for char lookup
class char_node:
    def __init__(self, _chr):
        self.frequency = 1
        self._chr = _chr

dictionary_char = {}
huffman_tree = {}
huffman_header = ""

############################################## START OF DECOMPRESSION #################################################

# Decompress the file
def decompress(file_input, file_output):
    print "Decompressing..."
    with open(file_input, "r") as obj_read_file:
        with open(file_output, "w") as obj_write_file:
            read_chr = obj_read_file.read(1).decode("UTF-8") # Get header length

            for a in range(1, ord(read_chr) / 2):
                tmp_chr_enc = obj_read_file.read(1).decode("UTF-8")
                tmp_chr_dec = obj_read_file.read(1).decode("UTF-8")
                dictionary_char[tmp_chr_enc] = tmp_chr_dec
            while True:
                read_chr = obj_read_file.read(1).decode("UTF-8")

                if not read_chr:
                    break

                if read_chr in dictionary_char:
                    write_chr = dictionary_char[read_chr]
                else:
                    write_chr = read_chr

                obj_write_file.write(write_chr)
            obj_write_file.close()
        obj_read_file.close()

############################################## START OF COMPRESSION ###################################################

# Compress the file
def compress(file_input, file_output):
    global huffman_header

    print "Reading file..."
    with open(file_input, "r") as obj_file:
        # Let's add all the characters and their frequency into a table
        while True:
            _chr = obj_file.read(1).decode("UTF-8")

            if not _chr:
                break
            if _chr in dictionary_char:
                dictionary_char[_chr].frequency += 1
            else:
                dictionary_char[_chr] = char_node(_chr)
        obj_file.close()

    # Let's generate the tree and header
    print "Generating tree..."
    generateTree()
    print "Generating header..."
    generateHeader()

    # Time to write all the data to the other file
    print "Writing file..."
    with open(file_input, "r") as obj_read_file:
        with open(file_output, "wb") as obj_write_file:
            obj_write_file.write(bytes(huffman_header))
            while True:
                read_chr = obj_read_file.read(1).decode("UTF-8")

                if not read_chr:
                    break

                write_chr = bytearray(int(a) for a in huffman_tree[read_chr].bits)

                obj_write_file.write(write_chr)
            obj_write_file.close()
        obj_read_file.close()

# The tree will give us easier accessability and faster writing
def generateTree():
    # First let's import the char nodes into the tree
    for key, value in dictionary_char.items():
        huffman_tree[key] = huffman_node(key, value.frequency)

    # Next we start combining the nodes
    moves_left = calc_moves()

    while moves_left > 0:
        node_low_1 = None
        node_low_2 = None

        for key, value in huffman_tree.items():
            if not value.active:
                continue

            if node_low_2 != value and (node_low_1 is None or node_low_1.frequency > value.frequency):
                node_low_1 = value
            if node_low_1 != value and (node_low_2 is None or node_low_2.frequency > value.frequency):
                node_low_2 = value

        tmp_freq = node_low_1.frequency + node_low_2.frequency
        tmp_val = node_low_2.value + node_low_1.value

        huffman_tree[tmp_val] = huffman_node(tmp_val, tmp_freq, node_low_2, node_low_1)
        node_low_1.active = False
        node_low_1.parent = huffman_tree[tmp_val]
        node_low_1.bits = [1]
        node_low_2.active = False
        node_low_2.parent = huffman_tree[tmp_val]
        node_low_2.bits = [0]
        moves_left -= 1

    # Now we finish off the bits
    for key, value in huffman_tree.items():
        if len(key) > 1:
            continue

        binCode = [str(value.bits[0])]
        parent = value.parent

        while not parent is None and len(parent.bits) > 0:
            binCode.insert(0, str(parent.bits[0]))
            parent = parent.parent
        value.bits = binCode

# The header will be used to decompress the file later on
def generateHeader():
    global huffman_header

    huffman_header += chr(len(dictionary_char) * 2) # Header length will be used as the header offset

    for key, value in dictionary_char.items():
        huffman_header += str(bytearray(int(a) for a in huffman_tree[key].bits)) + key

# Calculates the moves it has to do
def calc_moves():
    return len(huffman_tree) - 2

############################################### MAIN CODE ##########################################################

if len(sys.argv) < 3:
    print "Usage: huffman.py <compress/decompress> <input_file> [output_file]"
    sys.exit(0)
if sys.argv[1] != "compress" and sys.argv[1] != "decompress":
    print "Please select either compress or decompress!"
    sys.exit(0)
if not os.path.isfile(sys.argv[2]):
    print "Select a valid file!"
    sys.exit(0)
if len(sys.argv) > 3:
    if sys.argv[2] == sys.argv[3]:
        print "Output file cannot be the same as input file!"
        sys.exit(0)
    else:
        if sys.argv[1] == "compress":
            compress(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == "decompress":
            decompress(sys.argv[2], sys.argv[3])
else:
    if sys.argv[1] == "compress":
        compress(sys.argv[2], sys.argv[2] + ".compressed")
    elif sys.argv[1] == "decompress":
        decompress(sys.argv[2], sys.argv[2] + ".decompressed")
print "Done!"
