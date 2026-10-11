import socket
import ssl
import threading 
import struct  
import time
from protocol import MsgType
class Networking(object):
    def __init__(self):
        self.IP                     = '0.0.0.0'     # LISTEN ON ALL INTERFACES (0.0.0.0) ( TEAM NOTE: Steven Andrews II )
        self.port                   = 8500          # should never change, but can be changed if needed ( make sure to change it in the server as well - TEAM NOTE: Steven Andrews II )
        self.is_connected           = False         # indicator 
        self.is_running             = False         # indicator for the background thread
        self.keepalive_time         = 5000          # Time in seconds before sending the first keep-alive probe
        self.keepalive_interval     = 1000          # Time in seconds between keep-alive probes
        self.connection_amount      = 10            # maximum number of connections allowed
        # start a timer


        self.users = {}  # Dictionary to keep track of connected users and their associated sockets
        self.users["Steven"] = User.User("Steven", "password", "127.0.0.1", 8500)



        self.current_time = time.time() 
        self.Start()
        print(" [Networking] Initialized")





    '''
        Start: Starts the server and begins listening for incoming connections.
        Returns: True if the server started successfully, False otherwise.
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
            
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            
            # make sure server.crt and server.key files exist in your folder
            # if you don't have them, in the files - this app will not work, crashing the server and client. 
            context.load_cert_chain(certfile="server.crt", keyfile="server.key")

            
            # spool the main listener loop onto a background thread
            listener_thread = threading.Thread(target=self.Listener, args=(context,), daemon=True)
            listener_thread.start()
            self.is_running = True # running indicator for the background thread
            
            print(f"Server successfully started on port {self.port}. Listening for connections...")
            return True
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            self.is_running = False
            return False





    '''
        Listener: Listens for incoming connections and handles them in separate threads.
        Parameters: 
            context (ssl.SSLContext) - The SSL context for secure connections.
        Returns: None
    '''
    def Listener(self, context):
        while self.is_running:
            try:
                raw_client_sock, addr = self.server_socket.accept()
                
                # Windows network health probe 
                self.enable_windows_keepalive(raw_client_sock)
                
                # TLS secure handshake
                secure_client_sock = context.wrap_socket(raw_client_sock, server_side=True)
                
                # thread the client handler to allow multiple clients to connect simultaneously
                client_thread = threading.Thread(
                    target=self.Handler, 
                    args=(secure_client_sock, addr), 
                    daemon=True
                )
                client_thread.start()
                
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
    def Handler(self, client_socket, addr):
        client_ip, client_port = addr
        print(f"Connection established from client address: {client_ip}:{client_port}")
        
        while self.is_running:
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
                    self.extractParts(client_socket, payload_length) # Dump bad data - this works / keep it
                    continue
                
                # Read exact expected packet payload size
                payload = self.extractParts(client_socket, payload_length)
                if payload is None:
                    print(f"Connection dropped during payload extraction from: {client_ip}")
                    break
                

                # parse th commands using the shared enum protocols
                if msg_type == MsgType.LOGIN:
                    print(f"Received LOGIN command from {client_ip}")
                elif msg_type == MsgType.LOGOUT:
                    print(f"Received LOGOUT command from {client_ip}")
                elif msg_type == MsgType.IMAGE:
                    print(f"Received IMAGE data from {client_ip}, length: {payload_length} bytes")
                    

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
        pass