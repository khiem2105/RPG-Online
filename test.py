import rsa

key_pair = rsa.KeyPair()

s = "Hello world"
encode_string = rsa.encode(s, key_pair.pub_key)
print(encode_string)
decode_str = rsa.decode(encode_string, key_pair.priv_key)
print(decode_str)