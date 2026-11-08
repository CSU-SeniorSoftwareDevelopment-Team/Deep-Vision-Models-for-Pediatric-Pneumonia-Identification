import socket
import ssl
import threading 
import struct  
import time
from NET.protocol import MsgType
from tkinter import messagebox
'''
# =========================================================================================
# AUTHOR:       Steven Andrews II
# ARCHITECTURE: Distributed IoT Client (VPN Endpoint)
# SECURITY:     TLS 1.3 / Private Root CA Validation (Zero-Trust Model)
# 
# ----------------------------------- 
# TECHNICAL IMPLEMENTATION OUTLINE:
# ----------------------------------- 
#   1-  SECURE INITIALIZATION: 
#       >   Configures a high-security default client context enforcing
#           strict certificate verification modes while safely bypassing domain hostname checking
#   
#   2-  ZERO-TRUST ROOT VERIFICATION: 
#      
#       >   Mandates a local 'root_ca.crt' file. Authenticates 
#           the server by validating its dynamic over-the-air leaf certificate signature against 
#           the permanent master Root CA trust stamp
#   
#   3- NETWORK HEALTH PROBE:
#     
#       >   Applies low-level Windows TCP Keep-Alives to the raw socket 
#           BEFORE wrapping with SSL to ensure the TLS engine propagates idle tunnel persistence
        >   Monitors server / connection state 
#   
#   4- ERROR HANDLING: 
#      
#       >   Intercepts network dropouts and bad certificate alerts to close 
#           sockets cleanly and protect local medical application memory
# =========================================================================================
'''

class Networking(object):
    def __init__(self):
        self.IP                     = '100.105.179.38'   # this needs to be the VPN - Ask Steven To set this up for each person in the group for testing - Tailscale VPN to traverse NAT and firewalls

        self.port                   = 8500               # should never change, but can be changed if needed ( make sure to change it in the server as well - TEAM NOTE: Steven Andrews II )
        self.reconnect_speed        = 5                  # Time in seconds to wait before attempting to reconnect after a disconnection
        self.keepalive_time         = 5000               # Time in seconds before sending the first keep-alive probe
        self.keepalive_interval     = 1000               # Time in seconds between keep-alive probes
        self.soc                    = None               # socket object for the connection
 
        # state and toggles 
        self.is_connected           = False              # Netwrok service indicator / is connected to TCP soc
        self.is_loggedin            = False              # is user logged in / login accepted 
        self.is_running             = False              # Master netwrok indicator 
        self.forcedLogOut           = False              # Forces the logout to login page ( frontend toggle )


        self.prediction_result = {}                      # placeholder for the last prediction result received from the server


        # start a timer

        self.current_time = time.time() 

        self.Start() # Start the connection and monitor loop in a background thread



    '''Start: 
                   Starts the networking connection to the server and spools the monitor loop onto a background thread.
       Parameters: 
                   None
       Returns:    
                   True if the connection was successful, False otherwise.
    '''
    def Start(self):
        """Creates a verified TLS connection to the central server."""

        try:
            # Create a TLS client context
            context = ssl.create_default_context(
                ssl.Purpose.SERVER_AUTH
            )

            # Require a trusted server cert
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True

            # Require TLS 1.2 or newer
            context.minimum_version = ssl.TLSVersion.TLSv1_2

            # Load the universal Root CA cert
            context.load_verify_locations(
                cafile="NET/Certification/root_ca.crt"
            )

        except FileNotFoundError:
            print("CRITICAL: root_ca.crt is missing. Cannot connect securely.")
            return False

        except ssl.SSLError as e:
            print(f"CRITICAL: Failed to load Root CA: {e}")
            return False

        raw_socket = None

        try:
            raw_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )
            self.enable_windows_keepalive(raw_socket)
            raw_socket.connect((self.IP, self.port))

            # Upgrade the TCP connection to TLS server_hostname 
            # must match the IP SAN in server.crt
            self.soc = context.wrap_socket(
                raw_socket,
                server_hostname=self.IP
            )

            # Connection is now established and the
            # server certificate has been verified against root_ca.crt
            self.is_connected = False
            self.is_running = True

            # Start the background networking monitor.
            monitor_thread = threading.Thread(
                target=self.NET,
                daemon=True
            )
            monitor_thread.start()

            print(
                f"Secure TLS connection established with "
                f"{self.IP}:{self.port}"
            )

            return True

        except ssl.SSLCertVerificationError as e:
            print(f"TLS CERTIFICATE VERIFICATION FAILED: {e}")

        except ssl.SSLError as e:
            print(f"TLS CONNECTION FAILED: {e}")

        except (ConnectionError, OSError) as e:
            print(f"NETWORK CONNECTION FAILED: {e}")

        except Exception as e:
            print(f"Failed to initiate connection: {e}")

        # Clean up if connection or TLS setup fails
        if raw_socket:
            try:
                raw_socket.close()
            except Exception:
                pass

        self.soc = None
        self.is_connected = False
        self.is_running = False

        return False





    ''' NET: Handles the network connection in a background thread. It continuously monitors the connection state and processes incoming data.
        Parameters: None
        Returns: None
    '''
    def NET(self):

        connection = self.soc
        print("Connection State: Connected")

        try:
            while self.is_running:

                try:
                    # Read the 8-byte packet header
                    header = self.extractParts(8, connection)
                    if not header:
                        print("Connection State: Disconnected (Remote host closed connection)")
                        break
                    msg_type, payload_length = struct.unpack('!II', header)

                    # Read payload
                    payload = self.extractParts(payload_length, connection)
                    if payload is None:
                        print("Connection State: Disconnected during payload transfer")
                        break

                    # Process received message
                    self.process_message(msg_type, payload)
                    self.is_connected = True

                except socket.timeout:
                    print("Connection State: Idle (Timeout reached)")
                    continue

                except (ConnectionResetError, ConnectionAbortedError, OSError, ssl.SSLError) as e:
                    print(f"Connection State: Disconnected ({e})")
                    break

                except Exception as e:
                    print(f"Connection State: Error encountered: {e}")
                    break

        #  reset connection state when the monitor exits
        finally:
            
            self.is_connected = False
            self.is_running = False

            # kill old connection 
            if connection:
                try:
                    connection.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    connection.close()
                except Exception:
                    pass

      
            # DO NOT - set self.soc to None if it has already been replaced by a new connection 
            # bug fix - auto client logout on forced logoff
            if self.soc is connection:
                self.soc = None
            print("Connection State: Monitoring stopped. Reconnection available.")



    ''' extractParts: Extracts the header from packet data 
    Parameters: num_bytes (int) - The number of bytes to extract from the socket.
    Returns: bytes - The extracted bytes from the socket, or None if the connection is closed.
    '''

    def extractParts(self, num_bytes, sock=None):

        if sock is None:
            sock = self.soc

        if sock is None:
            return None

        buffer = bytearray()

        while len(buffer) < num_bytes:

            packet = sock.recv(num_bytes - len(buffer))

            if not packet:
                self.is_running = False
                self.is_connected = False
                self.forcedLogOut = True
                return None

            buffer.extend(packet)

        return bytes(buffer)




    ''' Send: 
        Sends a message wrapper to the server. If the connection is down, it will print an error message and return False.
        Parameters: message (str) - The message to send to the server.
        Returns: True if the message was sent successfully, False otherwise.
    '''
    def send_packet(self, msg_type: MsgType, payload_bytes: bytes):
        if not self.is_connected or not self.soc:
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
        update: 
        Internal clock for the networking class to check its internal state for periodic checks, chamges, and logic.
        This function is locked by the scheduler to 30 FPS 

        Parameters: None
        Returns: None
    '''

    def update(self):
        # Attempt reconnection when both connection states are down
        if not self.is_running and not self.is_connected:

            if time.time() - self.current_time >= self.reconnect_speed:

                print("Network disconnected. Attempting reconnection...")

                self.current_time = time.time()

                self.Start()


    #=======================================================================
    # Application protocol layer 
    #=======================================================================

    
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

        #Tells the client to exit the dashboard and logout, must wait until sends an ok signal to log back in
        # future update : add a forced logoff message type to the protocol to avoid using the image payload for this purpose
        #3lif msg_type == MsgType.UPDATE:
        #    self.handle_image_payload(payload)


    def handle_login_response(self,payload):
        response = payload.decode('utf-8')
        if response == "OK":
            self.is_loggedin = True
        if response == "NO" or response == "UPDATING":
            self.is_loggedin = False
        if  response == "UPDATING":
            messagebox.showinfo("Update", "The system is currently updating. Please try again later.")
            self.is_loggedin = False


    def handle_logout_response(self,payload):
        response = payload.decode('utf-8')
        if response == "OK" or response == "NO":
            self.forcedLogOut = True
            self.is_loggedin = False
        if response == "Force":
            self.forcedLogOut = True
            self.is_loggedin = False
        

   
    def handle_image_payload(self,payload):
        response = payload.decode('utf-8')
        
        if response =="UPDATING":
            messagebox.showinfo("Update", "The system is currently updating. Please try again later.")
            return
        
        results = response.split(":")

        if len(results) == 3:
            if results[0] == "OK": 
                self.prediction_result = {
                    "status": results[0],
                    "diagnosis": results[1],
                    "confidence": float(results[2])*100  # Convert to percentage
                }
            
                

