# DeepImage - Distributed IoT Medical Image Processing Client

![Status](https://img.shields.io/badge/Status-Active%20Development-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Security](https://img.shields.io/badge/Security-TLS%201.2%2B-green)
![License](https://img.shields.io/badge/License-CSU-blue)

## Overview

**DeepImage** is a secure, distributed client application for medical image processing that connects to a remote server for AI-powered image analysis. The application leverages a neural network backend for deep learning inference and provides an intuitive GUI for user interaction.

Developed as a collaborative project by students at **Columbus State University** during the Fall 2026 semester, DeepImage demonstrates a real-world client-server architecture for computationally intensive image analysis tasks.

### Key Features

- **Zero-Trust Security**: TLS 1.2+ with private Root CA validation
- **Image Processing**: Load, preview, and submit medical images for server-side analysis
- **Real-time Results**: Display diagnostic predictions with confidence scores
- **Auto-Reconnection**: Automatic connection recovery with configurable intervals
- **Modern Dark UI**: Professional dark-themed interface with smooth interactions
- **Medical-Grade**: Designed for medical application standards and best practices

---

## Project Team

| Role | Name |
|------|------|
| **Team Lead** | Steven Andrews II |
| **Developer** | Steven Andrews II |
| **Developer** | Bhavik Patel |
| **Developer** | Jhonathan Falls |
| **Developer** | Ahumada Camillie |

**Institution**: Columbus State University  
**Duration**: 13 Weeks (August 2026 - December 2026)  
**Development Cycles**:
- **Cycle 1** (8 weeks): Base AI implementation and demo
- **Cycle 2** (5 weeks): Server-based deployment and service

---

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   DeepImage Client Application              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Frontend (GUI Layer)                   │    │
│  │  - LoginPage: User authentication                   │    │
│  │  - DashboardPage: Image processing workspace        │    │
│  │  - SettingsPage: Application settings               │    │
│  └─────────────────────────────────────────────────────┘    │
│                          △                                  │
│                          │ (Dependency Injection)           │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Networking Layer (TLS/SSL)                  │    │
│  │  - Secure TLS 1.2+ connection management            │    │
│  │  - Packet serialization/deserialization             │    │
│  │  - Server communication protocol                    │    │
│  │  - Connection state monitoring                      │    │
│  │  - Automatic reconnection logic                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Network Transport Layer                     │    │
│  │  - Raw TCP socket with keep-alives                  │    │
│  │  - TLS/SSL wrapper for encryption                   │    │
│  │  - VPN endpoint (Tailscale)                         │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                  │
└──────────────────────────┼──────────────────────────────────┘
                           │
                    (Over Tailscale VPN)
                           │
        ┌──────────────────▼──────────────────┐
        │    Remote DeepImage Server          │
        │    - AI Neural Network Backend      │
        │    - Image Processing Pipeline      │
        │    - User Authentication            │
        └─────────────────────────────────────┘
```

### Component Architecture

#### 1. **Networking Module** (`NET/Networking.py`)

Handles all server communication with zero-trust security principles.

**Key Responsibilities:**
- TLS 1.2+ connection establishment
- Certificate validation against local Root CA
- Packet header/payload protocol
- Connection state monitoring
- Automatic reconnection with configurable delays
- Windows TCP keep-alive management

**Connection Flow:**
```
1. Create TLS Context
   ├─ Load Root CA certificate
   └─ Set verification mode: CERT_REQUIRED
2. Create Raw TCP Socket
   ├─ Enable Windows Keep-Alives
   └─ Connect to server
3. Upgrade to TLS
   └─ Wrap socket with SSL context
4. Start Background Monitor Thread
   └─ Continuously listen for server messages
```

**Protocol Format:**
```
Message Structure:
┌──────────────────────────────────────────────────────┐
│ Header (8 bytes)          │ Payload (Variable)       │
├──────────────┬────────────┼──────────────────────────┤
│ Msg Type     │ Payload    │ Message Content          │
│ (4 bytes)    │ Length     │ (UTF-8 or Binary)        │
│              │ (4 bytes)  │                          │
└──────────────┴────────────┴──────────────────────────┘
```

**Message Types:**
| Type | Value | Direction | Purpose |
|------|-------|-----------|---------|
| `LOGIN` | 1 | Client → Server | User authentication |
| `LOGOUT` | 2 | Client → Server | Session termination |
| `IMAGE` | 3 | Bidirectional | Image submission/results |

#### 2. **Frontend Module** (`UI/Frontend.py`)

Manages the GUI and orchestrates page navigation.

**Responsibilities:**
- Initialize and manage all UI pages
- Route user interactions to appropriate handlers
- Maintain application theme and styling
- Monitor network connection status
- Display real-time network indicators

**Theme System:**
The application uses a comprehensive dark theme with accent colors for better visibility:
- Primary Background: `#171A21`
- Card/Panel Background: `#222733`
- Primary Text: `#E6EAF0`
- Accent Color: `#3984E8`
- Status Colors: Green (Online), Red (Offline), Yellow (Connecting)

#### 3. **UI Pages**

Each page is a `tk.Frame` subclass managed by Frontend:

**LoginPage** (`UI/Pages/LoginPage.py`)
- User ID and password entry fields
- Form validation and submission
- Focus management and keyboard shortcuts

**DashboardPage** (`UI/Pages/DashboardPage.py`)
- Image loading and preview
- Real-time image rendering
- Image submission to server
- Results display with diagnosis and confidence score
- Scrollable interface for all content

**SettingsPage** (`UI/Pages/SettingsPage.py`)
- Application settings and preferences
- Logout functionality
- Navigation back to dashboard

---

## Security Architecture

### Zero-Trust Model Implementation

**1. Secure Initialization**
```python
# TLS Context Configuration
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.verify_mode = ssl.CERT_REQUIRED      # Mandatory verification
context.check_hostname = True                 # Hostname validation
context.minimum_version = ssl.TLSVersion.TLSv1_2  # Enforce TLS 1.2+
context.load_verify_locations(cafile="NET/Certification/root_ca.crt")
```

**2. Root CA Validation**
- Mandatory local `root_ca.crt` file in `NET/Certification/`
- Server certificate must be signed by the Root CA
- Dynamic leaf certificates validated against permanent master trust anchor
- All untrusted and self-signed certificates are rejected
- Prevents Man-in-the-Middle (MITM) attacks

**3. Network Health Probing**
- TCP Keep-Alives applied BEFORE TLS wrapping
- Low-level socket configuration for connection persistence
- Automatic timeout detection and recovery
- Configurable reconnection delays (default: 5 seconds)

**4. Error Handling**
- Certificate verification errors trigger immediate disconnection
- Network dropouts are logged and handled gracefully
- Memory protection through proper socket cleanup
- Clear console feedback for debugging

---

## Installation & Setup

### Prerequisites

- **Python**: 3.8 or higher
- **Operating System**: Windows (due to Windows TCP Keep-Alive configuration)
- **Network**: Tailscale VPN access for secure server connectivity
- **Dependencies**: See `requirements.txt`

### Step 1: Clone Repository

```bash
git clone https://github.com/CSU-SeniorSoftwareDevelopment-Team/DeepImage.git
cd DeepImage/Deep_Image
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- `tkinter`: GUI framework (included with Python)
- `Pillow`: Image processing
- `ssl`: SSL/TLS support (built-in)
- `socket`: TCP/IP networking (built-in)
- `struct`: Binary packet serialization (built-in)

### Step 3: Certificate Setup

Place your Root CA certificate at:
```
Deep_Image/NET/Certification/root_ca.crt
```

**Certificate Requirements:**
- Must be in PEM format
- Must be the Root CA certificate (not leaf certificate)
- Must match the server's certificate chain

### Step 4: Configure Server Address

Edit `NET/Networking.py`:
```python
self.IP = '100.105.179.38'  # Replace with your server IP
self.port = 8500             # Replace if different
```

> **Note**: Contact Steven Andrews II for VPN endpoint configuration and server IP assignment.

### Step 5: Run Application

```bash
python Deep_Image.py
```

---

## Usage Guide

### User Workflow

#### 1. **Authentication**
```
1. Launch application
2. Login Page appears
3. Enter User ID and Password
4. Click "Authenticate" or press Enter
5. Wait for server response
   - OK: Enter Dashboard
   - NO: Return to Login (invalid credentials)
   - UPDATING: Show notification, return to Login
```

#### 2. **Image Processing**
```
1. Click "Load Image" button
2. Select image file from dialog
3. Preview displays in Image Preview canvas
4. Click "Send for Processing" to submit
5. Server processes and returns diagnosis
6. Results display with:
   - Diagnosis (predicted condition)
   - Confidence (percentage probability)
   - Status (OK or error code)
```

#### 3. **Settings & Logout**
```
1. Click "Settings" button on Dashboard
2. Access application settings
3. Click "Log Out" to return to login
   - Forces logout through server
   - Returns to Login Page
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Submit login credentials |
| `Mouse Wheel` | Scroll dashboard content |

---

## Configuration

### Network Parameters

Located in `Networking.__init__()`:

```python
self.IP                 = '100.105.179.38'  # Server IP address
self.port               = 8500              # Server port
self.reconnect_speed    = 5                 # Reconnection delay (seconds)
self.keepalive_time     = 5000              # Initial keep-alive (ms)
self.keepalive_interval = 1000              # Keep-alive interval (ms)
```

### UI Theme

Customize in `Frontend.__init__()`:

```python
self.theme = {
    "BG": "#171A21",              # Main background
    "CARD": "#222733",            # Card background
    "ACCENT": "#3984E8",          # Primary accent
    "SUCCESS": "#4CAF50",         # Success color
    "ERROR": "#E05252",           # Error color
    # ... more colors
}
```

### Update Loop Scheduling

Frame rates in `Deep_Image.py`:

```python
MED_FPS         = 30   # Network & UI updates
HIGH_FPS        = 120  # High-frequency UI tasks
ULTRA_HIGH_FPS  = 300  # Real-time tasks
```

---

## API Reference

### Networking Class

#### Public Methods

**`Start() -> bool`**
- Establishes TLS connection to server
- Spawns background monitoring thread
- Returns: `True` if successful, `False` otherwise

**`send_packet(msg_type: MsgType, payload_bytes: bytes) -> bool`**
- Sends protocol message to server
- Parameters:
  - `msg_type`: Message type (LOGIN, LOGOUT, IMAGE)
  - `payload_bytes`: Binary message content
- Returns: `True` if sent, `False` if disconnected

**`update()`**
- Called 30 FPS by main loop
- Checks connection state
- Attempts reconnection if needed

**`Stop()`**
- Gracefully closes connection
- Shuts down monitoring thread

**`process_message(msg_type: int, payload: bytes)`**
- Routes incoming messages to appropriate handlers

#### Message Handlers

**`handle_login_response(payload: bytes)`**
```
Responses:
- "OK": Login successful, set is_loggedin = True
- "NO": Invalid credentials, set is_loggedin = False
- "UPDATING": Server updating, show notification
```

**`handle_logout_response(payload: bytes)`**
```
Responses:
- "OK" / "NO": Standard logout
- "Force": Server-initiated logout
```

**`handle_image_payload(payload: bytes)`**
```
Responses:
- "UPDATING": Server updating, show notification
- "Force": Force user logout (edge case)
- "OK:diagnosis:confidence": Success response
```

### Frontend Class

**`show_page(page_name: str)`**
- Navigate to specified page
- Pages: "LoginPage", "DashboardPage", "SettingsPage"

**`trigger_login_attempt(username: str, password: str)`**
- Send login credentials to server

**`trigger_logoff()`**
- Initiate logout sequence

**`MakeButton(parent, text, command, bg_color, hover_color, click_color) -> tk.Button`**
- Create styled button with hover effects

---

## Connection Flow Diagram

```
User Launches App
        │
        ▼
┌─────────────────┐
│ Frontend boots  │
│ Creates Tkinter │
│ Creates Network │
└────────┬────────┘
         │
         ▼
    Start() → Networking attempts TLS connection
         │
         ├─ Create TLS Context
         ├─ Load Root CA
         ├─ Connect TCP socket
         ├─ Wrap with TLS
         ├─ Start NET() background thread
         │
         └─ Return to main loop
              │
              ▼
         ┌──────────────────────┐
         │ User sees Login Page │
         │ (is_connected = True)│
         └─────────┬────────────┘
                   │
        Enter credentials & press Enter
                   │
                   ▼
           send_packet(LOGIN, creds)
                   │
                   ▼
      ┌────────────────────────────┐
      │ Server responds with       │
      │ LOGIN message              │
      └────────┬───────────────────┘
               │
        NET() receives & decodes
               │
               ▼
        process_message(LOGIN, payload)
               │
               ▼
        handle_login_response()
               │
         Sets is_loggedin = True
               │
               ▼
        ┌──────────────────────────┐
        │ Frontend.update() detects │
        │ Switches to DashboardPage │
        └──────────────────────────┘
```

---

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to server
```
Solution:
1. Verify Tailscale VPN is connected
2. Check server IP in Networking.py
3. Confirm root_ca.crt exists and is valid
4. Check firewall allows port 8500
```

**Problem**: Certificate Verification Failed
```
Solution:
1. Verify root_ca.crt is in NET/Certification/
2. Ensure certificate is in PEM format
3. Confirm certificate matches server
4. Check certificate hasn't expired
```

**Problem**: Frequent Disconnections
```
Solution:
1. Check network stability
2. Increase keepalive_time and keepalive_interval
3. Check server logs for issues
4. Verify VPN connection is stable
```

### Image Processing Issues

**Problem**: Image fails to load
```
Solution:
1. Verify image format is supported (.png, .jpg, .jpeg, .bmp, .gif)
2. Check file permissions
3. Ensure image is not corrupted
4. Try smaller image file
```

**Problem**: Server returns error on submission
```
Solution:
1. Check server logs for processing errors
2. Verify image is valid medical format
3. Check server storage capacity
4. Confirm network connection is stable
```

### UI Issues

**Problem**: Text is cut off or UI elements overlap
```
Solution:
1. Resize application window
2. Check monitor DPI settings
3. Verify Tkinter installation is correct
4. Try on different resolution
```

---

## Development

### Project Structure

```
Deep_Image/
├── Deep_Image.py                    # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── NET/                            # Networking module
│   ├── Networking.py               # TLS client implementation
│   ├── protocol.py                 # Message type definitions
│   └── Certification/
│       └── root_ca.crt             # Root CA certificate
│
└── UI/                             # User interface module
    ├── Frontend.py                 # GUI orchestration
    └── Pages/
        ├── LoginPage.py            # Authentication UI
        ├── DashboardPage.py        # Processing workspace
        └── SettingsPage.py         # Settings interface
```

### Adding New Message Types

1. Add to `NET/protocol.py`:
```python
class MsgType(IntEnum):
    LOGIN  = 1
    LOGOUT = 2
    IMAGE  = 3
    CUSTOM = 4  # New message type
```

2. Add handler in `Networking.process_message()`:
```python
elif msg_type == MsgType.CUSTOM:
    self.handle_custom_message(payload)
```

3. Implement handler method:
```python
def handle_custom_message(self, payload):
    # Your implementation
    pass
```

### Adding New UI Pages

1. Create new page file in `UI/Pages/`:
```python
class NewPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.theme = controller.theme
        self.build_ui()
    
    def build_ui(self):
        # Your UI code
        pass
```

2. Register in `Frontend.__init__()`:
```python
for PageClass in (LoginPage, DashboardPage, SettingsPage, NewPage):
    # Page registration
```

3. Navigate from other pages:
```python
self.controller.show_page("NewPage")
```

---

## Security Considerations

### Certificate Chain

The application validates the complete certificate chain:
```
Client Root CA (trusted)
        ↓
Server Intermediate CA (optional)
        ↓
Server Leaf Certificate (verified)
```

### Secrets Management

- Do NOT commit `root_ca.crt` to public repositories
- Each team member receives unique Tailscale VPN credentials
- Server IP is team-specific and must be requested

### TLS Best Practices

- Minimum TLS 1.2 enforced
- Strong cipher suites enabled by default
- Certificate pinning via Root CA validation
- No hostname mismatch allowed (strict checking)

---

## Performance Optimization

### Update Loop Hierarchy

```
┌─ MEDIUM (30 FPS)  ─┐  Main application logic
│                    │  - Network state checks
│  ┌─ HIGH (120 FPS) │  - UI animations
│  │                 │  - Lightweight updates
│  │  ┌─ ULTRA HIGH  │  - Real-time tasks
│  │  │ (300 FPS)    │  - Critical timing
│  │  │              │
│  │  └──────────────┤
│  │                 │
│  └─────────────────┤
│                    │
└────────────────────┘
```

### Threading Model

- **Main Thread**: Tkinter event loop
- **Background Thread 1**: Network monitoring (NET loop)
- **Main Update Loop**: 30 FPS scheduler

This prevents UI blocking during network operations.

---

## Testing

### Connection Testing

```python
# In Python REPL
from NET.Networking import Networking

network = Networking()
print(f"Connected: {network.is_connected}")
print(f"Logged in: {network.is_loggedin}")

# Test message sending
from NET.protocol import MsgType
success = network.send_packet(MsgType.LOGIN, b"test:test")
print(f"Send success: {success}")
```

### UI Testing

```bash
# Run with debug logging
python Deep_Image.py

# Check console output for connection messages
# Verify UI transitions work correctly
```

---

## Future Enhancements

- [ ] Add explicit `FORCEDLOGOUT` message type (currently using IMAGE)
- [ ] Implement user preferences persistence
- [ ] Add image history/archive functionality
- [ ] Support batch image processing
- [ ] Real-time connection statistics display
- [ ] Multi-user session management
- [ ] Image format conversion utility
- [ ] Advanced filtering options
- [ ] Export results to PDF/CSV
- [ ] Dark/Light theme toggle

---

## Support & Contact

For issues, questions, or contributions:

1. **Check Documentation**: Review this README first
2. **Check Issues**: Look for similar issues in GitHub
3. **Contact Team Lead**: Steven Andrews II
4. **Submit Issues**: Use GitHub Issues for bug reports

---

## License

This project is developed for Columbus State University as part of the Senior Software Development course (Fall 2026).

---

## Changelog

### Version 1.0.0 (Initial Release - December 2026)
- TLS 1.2+ secure connection
- User authentication
- Image upload and processing
- Real-time results display
- Auto-reconnection functionality
- Dark-themed GUI

---

## Acknowledgments

Special thanks to:
- Columbus State University for the opportunity
- Tailscale for VPN infrastructure
- Python community for excellent libraries
- All team members for their dedication

---

**Last Updated**: December 2026  
**Status**: Active Development  
**Maintained By**: Steven Andrews II & Team
