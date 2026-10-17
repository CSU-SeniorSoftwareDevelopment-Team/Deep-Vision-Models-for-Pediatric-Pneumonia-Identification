'''
User class to store user information
- held inside lists and dictionaries for easy access and management
'''
import ipaddress  
class User():
    def __init__(self, username, password ,ip , isManager = False ):


        # ----------------------------
        # internal / system variables
        # ---------------------------- 
        self.username       = username
        self.password       = password

        self.Manager        = isManager   # Special tag for a user that have access control over other users data ( default to false )
        
        
        #NET
        self.IP_address     = ip      # Bound VPN IP - Static IP
        self.port           = 0       # Port ( not used ? )
        self.idelTick       = 0       # Idel timer 
        self.loggedin       = False   # State tracking 
        self.soc            = None    # Net socket 


    # Safe wrappers for username, password, IP changes
    def ChangeName(self, name_):
        if self.username == str(name_):
            return False
        self.username = name_.strip().title().lower()
        return True



    def ChangePassword(self, pass_):
        if self.password == str(pass_):
            return False
        self.password = pass_.strip().title().lower()
        return True


    # this should not be accesable from the client side, this is a manager user item 
    def ChangeIP(self, a, b, c, d):
        new_ip = f"{str(a).strip()}.{str(b).strip()}.{str(c).strip()}.{str(d).strip()}"

        try:
            # ipaddress.ip_address throws a ValueError if it isn't a valid IPv4 or IPv6
            ipaddress.ip_address(new_ip)

            if self.IP_address == new_ip:
                return False

            self.IP_address = new_ip
            return True

        # thows error if its not a valid IP 
        except ValueError:
            return False
    