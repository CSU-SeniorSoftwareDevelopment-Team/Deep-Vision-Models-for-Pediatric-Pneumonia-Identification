from Backend.USER.User import User
import json
class UserManager(object):
    def __init__(self):

        self.users = {}  # Dictionary to store user data

        self.json_path = "Backend/USER/users.json"  # Path to the JSON file for saving/loading users


    """
        Load users from a JSON file. If the file does not exist, 
        it safely skips loading without crashing
    """
    def LoadUsers(self):
        print(f"-------------------------------------------------")
        try:
            with open(self.json_path, "r") as f:      
                json_data = json.load(f)
                
            for user_data in json_data:
                username = user_data['username']
                password = user_data['password']
                ip = user_data['ip']
                isManager = user_data.get('isManager', False)
                
                self.add_user(username, password, ip, isManager)
                
            print(f"-------------------------------------------------")
        except FileNotFoundError:
            print(f"Warning: {self.json_path} not found. Starting with an empty user list.")
            
        except json.JSONDecodeError:
            print(f"Error: {self.json_path} is empty or corrupted. Starting fresh.")




    """
        Save users to the JSON file.
    """
    def SaveAllUsers(self):
        user_list = []
        for user in self.users.values():
            user_list.append({
                'username': user.username,
                'password': user.password,
                'ip': user.IP_address,    
                'isManager': user.Manager  
            })
        # dump constructed list to json file
        with open(self.json_path, "w") as f:
            json.dump(user_list, f, indent=4)


    '''
    Add a new user to the user manager.

    param username: The username of the new user.
    param password: The password of the new user.
    param ip: The IP address of the new user.
    param port: The port number of the new user.
    
    return: True if the user was added successfully, False if the user already exists.
    '''
    def add_user(self, username, password, ip , isManager = False):
       if username in self.users:
              print(f"User {username} already exists.")
              return False
        
       self.users[username] = User(username, password, ip , isManager) # Instantiate a new User object and add it to the users dictionary
       print(f"Loaded user: {username} : {ip} ")

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


