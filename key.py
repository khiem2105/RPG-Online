import ctypes

#Load the C lib
rsa_lib = ctypes.CDLL("./Crypto/rsa_lib.so")

#wrapping function
def wrap_function(func_name, restype, argtypes, lib=rsa_lib):
    func = lib.__getattr__(func_name)
    func.restype = restype
    func.argtypes = argtypes

    return func

class Key(ctypes.Structure):
    _fields_ = [('value1', ctypes.c_int64), ('value2', ctypes.c_int64)]

    def __init__(self, value1, value2):
        initKey = wrap_function("initKey", Key, [ctypes.c_int64, ctypes.c_int64])
        self = initKey(value1, value2)

    def __repr__(self):
        return f"n: {self.value1}, other value: {self.value2}"


class KeyPair(ctypes.Structure):
    _fields_ = [('priv_key', Key), ('pub_key', Key)]

    def __init__(self):
        generatekey = wrap_function("generateKey", KeyPair, None)
        key_pair = generatekey()
        # print(key_pair)
        self.priv_key = key_pair.priv_key
        self.pub_key = key_pair.pub_key

    def __repr__(self):
        return f"pub_key: {self.pub_key.value1}, {self.pub_key.value2}; priv_key: {self.priv_key.value1}, {self.priv_key.value2}"
