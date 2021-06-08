import ctypes

md5_lib = ctypes.CDLL("./Hash/md5_lib.so")

def md5_hash(s):
    hash_func = md5_lib.md5
    hash_func.restype = ctypes.c_char_p
    hash_func.argtypes = [ctypes.POINTER(ctypes.c_char)]

    input_string = ctypes.create_string_buffer(str.encode(s))
    return hash_func(input_string).decode('utf-8')