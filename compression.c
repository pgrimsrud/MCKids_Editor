#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

#define BUFFER_SIZE 100000

int bitPtr = 0;
int bytePtr = 0;

int occurrence_length = 0;

void increment_bit_ptr() {
    bitPtr++;
    if (bitPtr == 8) {
        bytePtr++;
        bitPtr = 0;
    }
}

char read_bit(char *buffer) {
    char bit = buffer[bytePtr] >> (7 - bitPtr) & 0x01;
    increment_bit_ptr();
    return bit;
}

int read_bits(char *buffer, int bits) {
    int value = 0;
    for (int i = 0; i < bits; i++) {
        value += read_bit(buffer) << (bits - i - 1);
    }
    return value;
}

void write_bit(char* buffer, int bit) {
    buffer[bytePtr] += bit << (7 - bitPtr);
    increment_bit_ptr();
}

void write_bits(char* buffer, int value, int bits) {
    for (int i = 0; i < bits; i++) {
        write_bit(buffer, (value >> (bits - 1 - i)) & 0x01);
    }
}

static PyObject* fast_decompress(PyObject *self, PyObject *args) {
    Py_buffer data;
    char* buffer;
    int bufferPtr = 0;
    int offset_size, length_size;
    PyObject *output;
    int offset, length;

    bitPtr = 0;
    bytePtr = 0;

    if (!PyArg_ParseTuple(args, "y*ii", &data, &offset_size, &length_size)) {
        return NULL;
    }

    buffer = (char*) malloc(BUFFER_SIZE);

    while (bufferPtr < BUFFER_SIZE) {
        if (read_bit(data.buf) == 1) {
            buffer[bufferPtr++] = (char) read_bits(data.buf, 8);
        } else {
            offset = read_bits(data.buf, offset_size);
            length = read_bits(data.buf, length_size);
            if (offset == 0 && length == 0) {
                break;
            }
            length += 3;
            for (int i = 0; i < length; i++) {
                buffer[bufferPtr] = buffer[bufferPtr - offset];
                bufferPtr++;
            }
        }
    }

    output = Py_BuildValue("y#", buffer, bufferPtr);
    free(buffer);

    return output;
}

static PyObject* fast_compression_length(PyObject *self, PyObject *args) {
    Py_buffer data;
    int offset_size, length_size;
    bitPtr = 0;
    bytePtr = 0;
    int offset, length;
    int bufferPtr = 0;

    if (!PyArg_ParseTuple(args, "y*ii", &data, &offset_size, &length_size)) {
        return NULL;
    }

    while (bufferPtr < BUFFER_SIZE) {
        if (read_bit(data.buf) == 1) {
            read_bits(data.buf, 8);
        } else {
            offset = read_bits(data.buf, offset_size);
            length = read_bits(data.buf, length_size);
            if (offset == 0 && length == 0) {
                break;
            }
        }
    }
    return Py_BuildValue("i", bytePtr + (bitPtr > 0 ? 1 : 0));
}

int find_previous_occurrence(Py_buffer buffer, int ptr, int max_offset, int max_length) {
    int found_offset = 0;
    occurrence_length = 0;

    for (int i = 1; i < min(buffer.len, max_offset); i++) {
        int length = 0;
        while(
            (buffer.len > ptr + length) &&
            (length + 1 < max_length) &&
            (ptr + length - i >= 0) &&
            (((char*)buffer.buf)[ptr + length] == ((char*)buffer.buf)[ptr + length - i])
        ) {
            length++;
        }

        if (length >= 3 && length > occurrence_length) {
            occurrence_length = length;
            found_offset = i;
        }
    }

    return found_offset;
}


static PyObject* fast_compress(PyObject *self, PyObject *args) {
    Py_buffer data;
    int offset_size, length_size;
    bitPtr = 0;
    bytePtr = 0;
    int bufferPtr = 0;
    char* buffer;
    PyObject *output;

    if (!PyArg_ParseTuple(args, "y*ii", &data, &offset_size, &length_size)) {
        return NULL;
    }

    buffer = malloc(5120);
    for (int i = 0; i < 5120; i++) {
        buffer[i] = 0;
    }
    int max_offset = (1 << offset_size);
    int max_length = (1 << length_size) + 3;

    while (bufferPtr < data.len) {
        int offset = find_previous_occurrence(data, bufferPtr, max_offset, max_length);
        if (offset > 0) {
            write_bit(buffer, 0);
            write_bits(buffer, offset, offset_size);
            write_bits(buffer, occurrence_length - 3, length_size);
            bufferPtr += occurrence_length;
        } else {
            write_bit(buffer, 1);
            int byte = ((char*)data.buf)[bufferPtr];
            write_bits(buffer, byte, 8);
            bufferPtr++;
        }
    }

    write_bit(buffer, 0);
    write_bits(buffer, 0, offset_size);
    write_bits(buffer, 0, length_size);

    output = Py_BuildValue("y#", buffer, bytePtr + min(bitPtr, 1));
    free(buffer);
    return output;
}

static PyMethodDef CompressionMethods[] = {
    {"fast_decompress", fast_decompress, METH_VARARGS, "Decompress M.C. Kids data."},
    {"fast_compression_length", fast_compression_length, METH_VARARGS, "Check compression length for M.C. Kids data."},
    {"fast_compress", fast_compress, METH_VARARGS, "Compress M.C. Kids data."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef compression_ext = {
    PyModuleDef_HEAD_INIT,
    "fast_compression",
    "M.C. Kids compression and decompression written in C.",
    -1,
    CompressionMethods
};

PyMODINIT_FUNC PyInit_fast_compression(void) {
    Py_Initialize();
    return PyModule_Create(&compression_ext);
}
