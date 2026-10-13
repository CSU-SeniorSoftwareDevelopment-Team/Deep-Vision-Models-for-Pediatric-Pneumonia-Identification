import User

class UserManager(object):
    def __init__(self):

        self.users = {}  # Dictionary to store user data





    '''
    Add a new user to the user manager.

    param username: The username of the new user.
    param password: The password of the new user.
    param ip: The IP address of the new user.
    param port: The port number of the new user.
    
    return: True if the user was added successfully, False if the user already exists.
    '''
    def add_user(self, username, password, ip ):
       if username in self.users:
              print(f"User {username} already exists.")
              return False
        
       self.users[username] = User.User(username, password, ip)
       return True





    '''
     Remove a user from the user manager.
     param name: The username of the user to be removed.
    
     return: True if the user was removed successfully, False if the user does not exist.
    '''
    def remove_user(self, name):
        if name in self.users:
            del self.users[name]
            return True
        else:
            print(f"User {name} does not exist.")
            return False


    def get_user(self, name):
        return self.users.get(name, None)




    '''
    Get a user by their IP address.

    param ip: The IP address of the user to be retrieved.

    return: The User object if found, None otherwise.
    '''
    def getUserByIP(self, ip):
        for user in self.users.values():
            if user.IP_address == ip:
                return user
        return None


