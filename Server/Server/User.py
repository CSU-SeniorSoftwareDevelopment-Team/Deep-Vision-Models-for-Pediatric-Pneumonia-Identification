'''
User class to store user information
- held inside lists and dictionaries for easy access and management
'''

class User():
    def __init__(self, username, password ,ip  ):
        self.username       = username
        self.password       = password
        self.IP_address     = ip
        self.port           = 0
        self.idelTick       = 0  

        self.loggedin = False


