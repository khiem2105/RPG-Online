"""This file contains useful functions that we cannot put anywhere else since they are useful 
in a bunch of different situations"""

def number_format(a):
    """Transforms the current number in something human and shorter
    for example here 1000 --> 1k"""
    x = 0
    letters = ['', 'K', 'M']
    while abs(a)>=1000:
        x += 1
        a /= 1000.0 
    return f'{a:.0f}{letters[x]}'

def str_to_dmg(txt):
    "change a str of dice to a list of nbr"
    i=0
    while txt[i] != "d": i+=1
    return [int(txt[:i]),int(txt[i+1:])]