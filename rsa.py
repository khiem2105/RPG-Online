from key import *

encrypt = wrap_function("encrypt", ctypes.c_char_p, [ctypes.POINTER(ctypes.c_char), Key])
decrypt = wrap_function("decrypt", ctypes.c_char_p, [ctypes.POINTER(ctypes.c_char), Key])

def encode(s, pub_key):
    encrypt = wrap_function("encrypt", ctypes.c_char_p, [ctypes.POINTER(ctypes.c_char), Key])
    input_string = ctypes.create_string_buffer(str.encode(s))
    return encrypt(input_string, pub_key).decode('utf-8')

def decode(s, priv_key):
    decrypt = wrap_function("decrypt", ctypes.c_char_p, [ctypes.POINTER(ctypes.c_char), Key])
    input_string = ctypes.create_string_buffer(str.encode(s))
    return decrypt(input_string, priv_key).decode('utf-8')