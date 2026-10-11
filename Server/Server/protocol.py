from enum import IntEnum


'''
Incoming message mapping / expected values:
'''
class MsgType(IntEnum):
    LOGIN  = 1
    LOGOUT = 2
    IMAGE  = 3