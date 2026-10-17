'''
User class to store user information
- held inside lists and dictionaries for easy access and management
'''
import ipaddress  
from datetime import datetime

class User():
    def __init__(self, username, password ,ip , isManager = False ):


        # ----------------------------
        # internal / system variables
        # ---------------------------- 
        self.username       = username
        self.password       = password

        self.Manager        = isManager   # Special tag for a user that have access control over other users data ( default to false )
        
        self.changelog      = {}      # Logs changes locally to the session 


        #NET
        self.IP_address     = ip      # Bound VPN IP - Static IP
        self.port           = 0       # Port ( not used ? )
        self.idelTick       = 0       # Idel timer 
        self.loggedin       = False   # State tracking 
        self.soc            = None    # Net socket 

  




    '''
    Local Session Change Log:
         > changes are saved to a dictionary that is cleared at the end of a users session 
    '''
    def add_change(self,time,change):
        self.changelog[time] = {
            "change": change,
        }
    def clearLog(self):
        self.changelog.clear()

    def displayLogDebug(self):
        print(self.changelog)


    '''
    Make changed:
        > Change password,name, and bound IP address for this user
    '''
    def ChangeName(self, name_):
        
        if self.loggedin == False: # this should be flagged by a security handler 
            return False

        cleaned_name = str(name_).strip()
        if self.username == cleaned_name:
            return False
        newName = cleaned_name.title()
        self.add_change(datetime.now(), f"Updated User name from {self.username} to {newName}")
        self.username = newName
        return True



    def ChangePassword(self, pass_):

        if self.loggedin == False: # this should be flagged by a security handler 
            return False

        new_password = str(pass_)
        if self.password == new_password:
            return False
        self.add_change(datetime.now(), "Updated User password *******")
        self.password = new_password
        return True


    # this should not be accesable from the client side, this is a manager user item 
    # or it should log out the user then apply this change 
    def ChangeIP(self, a, b, c, d):

        new_ip = f"{str(a).strip()}.{str(b).strip()}.{str(c).strip()}.{str(d).strip()}"
        try:
            # ipaddress.ip_address throws a ValueError if it isn't a valid IPv4 or IPv6
            ipaddress.ip_address(new_ip)

            if self.IP_address == new_ip:
                return False
            self.add_change(datetime.now(), f"Updated Users VPN IP: {new_ip}")
            self.IP_address = new_ip
            return True

        # throws error if its not a valid IP 
        except ValueError:
            return False
    