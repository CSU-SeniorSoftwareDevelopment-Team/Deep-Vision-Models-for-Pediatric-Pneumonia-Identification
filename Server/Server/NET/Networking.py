import socket
import ssl
import threading 
import struct  
import time
# backend imports
from NET.protocol import MsgType

'''
# =========================================================================================
# AUTHOR:       Steven Andrews II
# ARCHITECTURE: Secure Hybrid Client-Server (Edge AI Installation)
# SECURITY:     TLS 1.3 / Application-Layer IP Whitelisting (Dynamic VPN Optimized) [ Near production grade ] 

# DESCRIPTION:  This module implements a secure, multi-threaded TCP server that listens for incoming connections,
#               authenticates users, and processes image data using a backend AI model. 
#               The server supports TLS encryption, IP whitelisting, and user session management.
#------------------------------------------
# TECHNICAL IMPLEMENTATION OUTLINE:
#------------------------------------------
#
#   1- CORE LISTENER ENGINE: 
#           Spools an asynchronous multi-threaded TCP socket loop 
#           onto a dedicated background daemon thread with port reuse enabled
            > The listener thread accepts incoming connections and spawns a new thread for each client to handle communication.
            > Each client thread is responsible for reading and processing packets from its respective client socket.
            
           The listener thread and client threads are designed to run concurrently, allowing multiple clients to connect and communicate with the server simultaneously.
#   
#   2- INBOUND NETWORK FILTRATION:
#           a. Socket-Level Health: Injects native Windows TCP Keep-Alives into raw sockets
#           b. Cryptographic Handshake: Wraps incoming sockets using an open TLS context
#           c. Network Layer Whitelisting: Rejects and immediately closes unauthorized 
#              IP addresses using an internal UserManager lookup to prevent leaks ( white listed IPs )
#   
#   3- HIGH-AVAILABILITY ROTATION: 
#           Supports thread-safe, atomic certificate swapping 
#           live via memory context updates without dropping the main listener thread
#            > The TLS context can be updated at runtime to swap certificates without interrupting existing connections.
#    
#   4- APPLICATION PROTOCOL LAYER: 
#           Supports quick protocol additions and set up / state tracking 
#            > An additional thread is spawned for each new connection to handle the application protocol layer
#            > Each thread is responsible for handling the application protocol layer for a single client connection
#
#    5- APPLICATION PROTOCOL COMMANDS:
#            Supported commands are defined in the shared protocol enum (NET/protocol.py) and include:
#            > LOGIN, LOGOUT, IMAGE, and more. Each command is handled in the Handler method, which processes incoming packets based on their message type.
#
# =========================================================================================
'''


class Networking(object):
    def __init__(self, backend , user_manager):
        self.user_manager           = user_manager # Dependency injection for user management
        self.backend                = backend      # Backend AI hookup 

        # Network Configuration
        self.IP                     = '100.105.179.38'      # LISTEN ON ALL INTERFACES (0.0.0.0) ( TEAM NOTE: Steven Andrews II )
        self.port                   = 8500                  # should never change, but can be changed if needed ( make sure to change it in the server as well - TEAM NOTE: Steven Andrews II )
        
        # settingsfor TCP keep-alive probes - these are used to detect dead connections and prevent resource leaks

        self.keepalive_time         = 1000          # Time in seconds before sending the first keep-alive probe
        self.keepalive_interval     = 1000          # Time in seconds between keep-alive probes
        self.connection_amount      = 10            # maximum number of connections allowed
        self.UserTimeOut            = 5000
        # start a timer


        # load the users from the JSON file into the user manager
        user_manager.LoadUsers() 
        

        # Internal state variables
        self.current_time = time.time()                     # internal clock for the networking class to check its internal state for periodic checks, chamges, and logic. 
        self.context                = None                  # TLS context - created in Start() 
        self.stop_signal            = threading.Event()     # Event to signal the listener thread to stop
        self.listener_thread        = None                  # Listener thread for handling incoming connections
        
        self.is_connected           = False                 # indicator 
        self.is_running             = False                 # indicator for the background thread
        self.numberOfActiveUsers    = 0                     # user tracker  

        # Start the server
        self.Start()    
        print(" [Networking] Initialized")


        


    '''
        Stop: Stops the server and disconnects all clients!

        This function is designed to be called when the server needs to shut down forcably. 
        It will notify all connected clients, close their sockets, and terminate all listener threads.

        This will force all users to log out and clear their session data. Use with cautio

        
        >Dev note: I need to add a slow shutdown to allow the clients to gracefully log out before the server closes their sockets
       
        > Right now clients will be forced to log out and will not
          be able to save their session data if the server is
          stopped while they are connected.

        Additional Note : 
        Actual better implementation would be to send a "server is shutting down" message to all clients and allow them to gracefully log out before closing their sockets.
        this way the server knows that the clients have logged out and can safely close their sockets without losing any data or running into a race conditions or bugs
        especially with lock out bugs on the client side. 
       
        *** ( this is a demo, so this is not a production grade implementation  ) *** 

    '''
    def Stop(self):
        if not self.is_running:
            return True

        print("Stopping server...")

        try:
            # Tell the server to stop accepting new connections
            self.is_running = False

            # Notify all connected users
            response = b"Force"

            users = list(self.user_manager.users.values())

            for user in users:
                if user.loggedin:
                    try:
                        self.send_packet(
                            user.soc,
                            MsgType.LOGOUT,
                            response
                        )
                    except Exception as e:
                        print(f"Failed to notify client: {e}")

                    user.loggedin = False

            # Signal all listener threads to terminate
            self.stop_signal.set()

            # Close the server socket to unblock accept() - Need to close the socket to unblock any accept() calls in the listener thread
            if self.server_socket:
                try:
                    self.server_socket.close()
                except OSError:
                    pass

                self.server_socket = None

            # Close client sockets to unblock recv() - Need to close the sockets to unblock any recv() calls in the Handler threads
            for user in users:
                if user.soc:
                    try:
                        user.soc.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass

                    try:
                        user.soc.close()
                    except OSError:
                        pass

            # ( loops and grabs )  Collect threads that need to terminate
            threads = []

            if self.listener_thread:
                threads.append(self.listener_thread)

            for user in users:
                if getattr(user, "clientThread", None):
                    threads.append(user.clientThread)

            # Wait for threads to finish
            for thread in threads:
                if thread and thread.is_alive():
                    if thread != threading.current_thread():
                        thread.join(timeout=5)

                        if thread.is_alive():
                            print(f"Warning: Thread {thread.name} did not terminate.")

            self.listener_thread = None

            print("Server stopped successfully.")
            return True

        except Exception as e:
            print(f"Failed to stop server: {e}")
            return False


    '''
        Restart: Restarts the server with optional new settings
    '''
    def Restart(self, new_settings=None):
        if not self.Stop():
            print("Cannot restart: server failed to stop.")
            return False

        if new_settings is not None:
            # thse settings would be applied to this class and then distributed to the other classes that need them ( backend, user manager )
            pass  

        # Reset shutdown state
        self.stop_signal.clear()

        return self.Start()



    '''
        Start:      Starts the server and begins listening for incoming connections.
        Returns:    True if the server started successfully, False otherwise.
    '''
    def Start(self):
        if self.is_running:
            return True

        # Setup raw TCP soc with / port reuse option
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.IP, self.port))
            self.server_socket.listen( self.connection_amount ) # maximum number of connections allowed
            
            self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            
            # load cert and key 
            # the client verifies the servers Cert / do not check the cert from the client 
            self.context.load_cert_chain(certfile="NET/Certification/server.crt", keyfile="NET/Certification/server.key")
            self.context.verify_mode = ssl.CERT_NONE 
            
            # spool the main listener loop onto a background thread
            self.is_running = True
            self.listener_thread = threading.Thread(target=self.Listener, args=(self.context,), daemon=True)
            self.listener_thread.start()
            
            
            print(f"Server successfully started on port {self.port}. Listening for connections...")
            return True
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            self.is_running = False
            return False





    '''
        Listener: 
                    Listens for incoming connections and handles them in separate 
                    threads by spooling a thread per new connection 
        
        Parameters: 
            context (ssl.SSLContext) - The SSL context for secure connections.
        Returns: None
    '''
    def Listener(self, context):
        while self.is_running and not self.stop_signal.is_set():
            try:
                raw_client_sock, addr = self.server_socket.accept()
                
                # Windows network health probe 
                self.enable_windows_keepalive(raw_client_sock)
                
                # TLS secure handshake
                try: 
                    secure_client_sock = context.wrap_socket(
                                                                raw_client_sock,
                                                                server_side=True
                      
                     )

                except Exception as tls_err:
                    print(f"TLS Handshake failed from {addr}: {tls_err}")
                    raw_client_sock.close()
                    continue
                
                # check user IP white list 
                # search through users 
                client_ip, client_port = addr
                user_ = self.user_manager.getUserByIP(client_ip)
                if not user_:
                   print("Invalid IP detected")
                   secure_client_sock.close()
                   continue # skip creating a listener thread 

                # bind the soc to the user - this allows us to send data arbitraily through the User object
                user_.soc = secure_client_sock

                # thread the client handler to allow multiple clients to connect simultaneously
                user_.clientThread = threading.Thread(
                    target=self.Handler,
                    args=(secure_client_sock, user_, addr),
                    daemon=True
                )

                user_.clientThread.start()
                
            except Exception:
                # This will catch socket breaks when Stop() 
                break

    


    '''
        Handler: Handles communication with a connected client.
        Parameters: 
            client_socket (socket.socket) - The socket representing the client connection.
            addr (tuple) - The address of the connected client.
        Returns: None
    '''
    def Handler(self, client_socket, user_ ,  addr):
        client_ip, client_port = addr
        print(f"Connection established from client address: {client_ip}:{client_port}")
        
        while self.is_running and not self.stop_signal.is_set():
            try:
                # read the fixed 8-byte header
                header = self.extractParts(client_socket, 8)
                if not header:
                    print(f"Client disconnected gracefully: {client_ip}")
                    break
                
                # Unpack the packet header to get the message type and payload length 
                raw_msg_type, payload_length = struct.unpack('!II', header)
                
                try:
                    msg_type = MsgType(raw_msg_type)
                except ValueError:
                    print(f"Server received invalid message integer ({raw_msg_type}) from {client_ip}")
                    self.extractParts(client_socket, payload_length) # Dump bad data - read the rest of the buffer / clears it on read
                    continue # fault tollerant 
                
                # Read exact expected packet payload size
                payload = self.extractParts(client_socket, payload_length)
                if payload is None:
                    print(f"Connection dropped during payload extraction from: {client_ip}")
                    break   # connection dropped
                
                #---------------------------------------------------------------------------------
                # parse the commands using the shared enum protocols
                #---------------------------------------------------------------------------------
                if msg_type == MsgType.LOGIN:
                    print(f"Received LOGIN command from {client_ip}")
                    user_.idelTick = 0 # any new data resets the Idel ticks 
                    self.Login(client_ip,client_socket,user_,payload)

                elif msg_type == MsgType.LOGOUT:
                    print(f"Received LOGOUT command from {client_ip}")
                    user_.idelTick = 0 
                    self.Logout(client_ip,client_socket,user_,payload)
                
                elif msg_type == MsgType.IMAGE:
                    print(f"Received IMAGE data from {client_ip}, length: {payload_length} bytes")
                    user_.idelTick = 0 
                    self.RunImage(client_ip,client_socket,user_,payload)
 
                #---------------------------------------------------------------------------------

            except (ConnectionResetError, ConnectionAbortedError, OSError):
                print(f"Connection to client {client_ip} was forcibly lost.")
                break
            except Exception as e:
                print(f"Error handling client data stream from {client_ip}: {e}")
                break

        # client connection when loop ends
        try:
            client_socket.close()
        except Exception:
            pass

    '''
        User tracking data
        parameters: 
            bool_(boolean) = (false = remove, default = add)
    '''
    def AddActiveUser(self,bool_ = True):
        if bool_ == True: 
            self.numberOfActiveUsers += 1
        else:
            if self.numberOfActiveUsers > 0:
                self.numberOfActiveUsers -= 1
        


    '''
        Forced logout - time out or security 
            parameters: 
                user - user object ( contains socket data and user state data )
    '''
    def ForceLogout(self, user):
        self.AddActiveUser(False)
        # tell the client that the server logged them out - this should force the client app
        # to bring them back to the login page 
        response = f"Force"
        if user.soc != None:
            self.send_packet(user.soc,MsgType.LOGOUT,response.encode('utf-8'))
            try:
                   user.soc.shutdown(socket.SHUT_RDWR)
            except OSError:
                   pass

            try:
                   user.soc.close()
            except OSError:
                   pass
            user.soc = None # ditching the socket reference
            
        user.clearLog() # clear local logs 
        user.loggedin = False




    '''
    Payload Transmission: Wrapper for sending a packet to the client with the specified message type and payload.
    '''
    def send_packet(self, client_socket, msg_type: MsgType, payload_bytes: bytes):
        if not self.is_running or not client_socket:
            return False
        try:
            # Create the exact same 8-byte header the client expects
            header = struct.pack('!II', msg_type, len(payload_bytes))
            client_socket.sendall(header + payload_bytes)
            return True
        except (OSError, ConnectionError) as e:
            print(f"Send failed to client: {e}")
            return False




    ''' enable_windows_keepalive:
        Enables Windows Keep-Alives on a socket.
        
        Parameters: 
        sock (socket.socket)        - The socket on which to enable keep-alives.
        
        Returns: None
    '''
    def enable_windows_keepalive(self, sock ):
        # Enable TCP keep-alive
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, self.keepalive_time, self.keepalive_interval))





    ''' extractParts: Extracts the header from packet data 
    Parameters:     num_bytes (int) - The number of bytes to extract from the socket.
                    Sock (socket) - The socket object from which to extract the bytes.

    Returns:        bytes - The extracted bytes from the socket, or None if the connection is closed.
    '''
    def extractParts(self,sock, num_bytes):
        buffer = bytearray()
        while len(buffer) < num_bytes:
            packet = sock.recv(num_bytes - len(buffer))
            if not packet:
                return None
            buffer.extend(packet)
        return bytes(buffer)




    '''
        update: 
        Internal clock for the networking class to check its internal state for periodic checks, chamges, and logic.
        This function is locked by the scheduler to 30 FPS 

        Parameters: None
        Returns: None
    '''
    def Update(self):
       
        # force user to logout if inactive for (UserTimeOut) min ( User security )
        for user_ in self.user_manager.users.values():
            user_.idelTick += 1
            if user_.idelTick > self.UserTimeOut:
                self.ForceLogout(user_)
                user_.idelTick  = 0




    #==============================================================================
    # APPLICATION PROTOCOL LAYER
    #==============================================================================

    def Login(self, client_ip,client_socket, user_, payload):
        incoming_string = payload.decode('utf-8')
        username, password = incoming_string.split(':')
       
        if self.backend.lock == True:
                response = f"UPDATING"
                self.send_packet(client_socket,MsgType.LOGIN,response.encode('utf-8'))
                print(f"Authentication failed: Update underway")
                return False

        if username == user_.username and password == user_.password:
            self.AddActiveUser()
            user_.loggedin = True
            response = f"OK"
            self.send_packet(client_socket,MsgType.LOGIN,response.encode('utf-8'))
            print(f"Authentication success for user '{username}' from {client_ip}")
            return True
        else:
            response = f"NO"
            self.send_packet(client_socket,MsgType.LOGIN,response.encode('utf-8'))
            print(f"Authentication failed: Invalid credentials from {client_ip}")
        return False


    def Logout(self, client_ip,client_socket, user_, payload):

        if  user_.loggedin == True: # logged in already
            self.AddActiveUser(False)
            response = f"OK"
            self.send_packet(client_socket,MsgType.LOGOUT,response.encode('utf-8'))
            user_.clearLog() # clear local change logs
            print(f"Logout requested")
            return True
        else:
            response = f"NO"
            self.send_packet(client_socket,MsgType.LOGOUT,response.encode('utf-8'))
            print(f"Unauthorized Logout requested {user_.username}")
        user_.loggedin = False # force all users to log
        return False



    def RunImage(self, client_ip, client_socket, user_, payload):

         # system is updating
         if self.backend.lock == True:
            response = f"UPDATING"
            self.send_packet(client_socket,MsgType.IMAGE,response.encode('utf-8'))
            return False

         if user_.loggedin == False : # not logged in yet - can not run if not loged in  
            return False

         # grab results and pass them back 
         label, confidence  = self.backend.predict_from_buffer(payload)
         response = f"OK:{label}:{confidence}"
         self.send_packet(client_socket,MsgType.IMAGE,response.encode('utf-8'))
         return True