import socket
import ssl
import threading 
import struct  
import time
from protocol import MsgType

'''
CLIENT SIDE NETWORKING:
TCP-TLS Client side communication for low speed applications 
'''
class Networking(object):
    def __init__(self):
        self.IP                     = '127.0.0.1'   # this needs to be the VPN - Ask Steven To set this up for each person in the group for testing - Tailscale VPN to traverse NAT and firewalls
        self.port                   = 8500          # should never change, but can be changed if needed ( make sure to change it in the server as well - TEAM NOTE: Steven Andrews II )
        self.is_connected           = False         # indicator 
        self.is_loggedin            = False
        self.is_running             = False         # indicator for the background thread
        self.keepalive_time         = 5000          # Time in seconds before sending the first keep-alive probe
        self.keepalive_interval     = 1000          # Time in seconds between keep-alive probes
        self.soc                    = None          # socket object for the connection

        # start a timer

        self.current_time = time.time() 

        self.Start() # Start the connection and monitor loop in a background thread



    '''Start: Starts the networking connection to the server and spools the monitor loop onto a background thread.
       Parameters: None
       Returns: True if the connection was successful, False otherwise.
    '''
    def Start(self):
        """Creates the connection and spools the monitor loop onto a background thread."""
        context                     = ssl.create_default_context()
        context.check_hostname      = False
        context.verify_mode         = ssl.CERT_NONE  # Bypass verification for self-signed test certs

        try:
            # Note: Steven Andrews II - This is a critical step to ensure that the connection 
            # remains alive even if the application is idle for a long time
            #-------------------------------------------------------------------------------------------
            # create raw socket and apply Windows Keep-Alives
            # Wrap the raw socket with SSL context to create a secure connection
            #
            # enable Windows Keep-Alives on the raw socket before wrapping it with SSL 
            # - this is important because the SSL layer will not propagate the keep-alive settings to the socket without this step!
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.enable_windows_keepalive(raw_socket)

            self.soc = context.wrap_socket(raw_socket, server_hostname=self.IP)
            self.soc.connect((self.IP, self.port))

            self.is_connected = True
            self.is_running = True
            # start thread - background thread to monitor the connection state and process incoming data
            monitor_thread = threading.Thread(target=self.NET, daemon=True)
            monitor_thread.start()
            
            print(f"Successfully connected to {self.IP}:{self.port} and spooled monitor thread.")
            
            return True
            
        except Exception as e:
            print(f"Failed to initiate connection: {e}")
            self.is_connected = False
            self.is_running   = False
            return False
    




    ''' NET: Handles the network connection in a background thread. It continuously monitors the connection state and processes incoming data.
        Parameters: None
        Returns: None
    '''
    def NET(self):
        
        print("Connection State: Connected")
    
        while True:
            try:
                header = self.extractParts(8)
                # zero-byte read means remote host disconnected 
                if not header:
                    print("Connection State: Disconnected (Closed by remote host)")
                    self.is_connected = False
                    break
                

                # Extract payload and message type for parsing the data 
                msg_type, payload_length = struct.unpack('!II', header)
                payload = self.extractParts(payload_length)
                if payload is None:
                    print("Connection State: Disconnected during payload transfer")
                    self.is_connected = False
                    break
                # parse data based on the message type and payload
                self.process_message(msg_type, payload)

                # update connection state
                self.is_connected = True
              
            # Edge cases ( i hate this part update it later ) - useful for debugging and testing the connection state
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                print("Connection State: Disconnected (Connection forcibly reset/lost)")
                self.is_connected = False
                break
            except socket.timeout:
                print("Connection State: Idle (Timeout reached, still alive)")
                continue
            except Exception as e:
                print(f"Connection State: Error encountered: {e}")
                self.is_connected = False
                break

        # Clean up locally when loop terminates
        try:
            self.soc.close()
        except Exception:
            pass
   



    ''' extractParts: Extracts the header from packet data 
    Parameters: num_bytes (int) - The number of bytes to extract from the socket.
    Returns: bytes - The extracted bytes from the socket, or None if the connection is closed.
    '''
    def extractParts(self, num_bytes):
        buffer = bytearray() 
        while len(buffer) < num_bytes: # Extract payload data from the socket until the specified number of bytes is reached

            packet = self.soc.recv(num_bytes - len(buffer))
            if not packet:
                return None  # Connection closed
            buffer.extend(packet)
        return bytes(buffer) # Return the extracted bytes as a bytes object




    ''' Send: 
        Sends a message wrapper to the server. If the connection is down, it will print an error message and return False.
        Parameters: message (str) - The message to send to the server.
        Returns: True if the message was sent successfully, False otherwise.
    '''
    def send_packet(self, msg_type: MsgType, payload_bytes: bytes):
        if not self.is_connected or not self.soc:
            print("Network is down...")
            return False
        try:
            # Pack the Enum value and the payload size into exactly 8 bytes
            header = struct.pack('!II', int(msg_type), len(payload_bytes))
            
            # Blast the header and the payload together down the TLS socket
            self.soc.sendall(header + payload_bytes)
            return True
        except (OSError, ConnectionError) as e:
            print(f"Send failed. Network just died: {e}")
            self.is_connected = False
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



    ''' Stop: Stops the networking connection and the background thread.
        Parameters: None
        Returns: None
    '''
    def Stop(self):
        print("Stopping connection and network thread...")
        self.is_connected = False
        if self.soc:
            try:
                # SHUT_RDWR tells the OS to stop all sends and receives immediately.
                # This breaks the blocking .recv() loop in the background thread.
                self.soc.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            
            try:
                self.soc.close()
            except Exception:
                pass
            
            self.soc = None


    ''' 
        process_message: Processes incoming messages based on their type. [ Parser for incoming messages ]
        
        Parameters: 
        msg_type (int) - The type of the incoming message.
        payload (bytes) - The payload of the incoming message.
        
        Returns:
        None
    '''
    def process_message(self, msg_type, payload):
        if msg_type == MsgType.LOGIN:
            self.handle_login_response(payload)
        elif msg_type == MsgType.LOGOUT:
            self.handle_logout_response(payload)
        elif msg_type == MsgType.IMAGE:
            self.handle_image_payload(payload)


    def handle_login_response(self,payload):
        response = payload.decode('utf-8')
        if response == "OK":
            self.is_loggedin = True
        if response == "NO":
            self.is_loggedin = False

    def handle_logout_response(self,payload):
        response = payload.decode('utf-8')
        if response == "OK":
            self.is_loggedin = False

    def handle_image_payload(self,payload):
        response = payload.decode('utf-8')
        print(response)

    '''
        update: 
        Internal clock for the networking class to check its internal state for periodic checks, chamges, and logic.
        This function is locked by the scheduler to 30 FPS 

        Parameters: None
        Returns: None
    '''
    def update(self):
        # tries to reconnect/start background thread if the connection is down
        if self.is_running == False:
           if time.time() - self.current_time >  5:
              self.Start()
              self.current_time = time.time()

