# DeepImage Server - UML Class Diagram

## Class Diagram Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DEEPIMAGE SERVER ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐         ┌──────────────────────────┐
│      Backend (AI)        │         │      Frontend (UI)       │
├──────────────────────────┤         ├──────────────────────────┤
│ - model                  │◄────────┤ - backend                │
│ - device                 │         │ - network                │
│ - optimizer              │         │ - root (Tkinter)         │
│ - training_dataloader    │         │ - pages (dict)           │
└──────────────────────────┘         │ - theme (dict)           │
           △                         └──────────────────────────┘
           │                                    △
           │ uses                               │ uses
           │                                    │
           │                         ┌──────────┴──────────┐
           │                         │                     │
           │                  ┌─────────────────┐  ┌──────────────────┐
           │                  │   LoginPage     │  │   DashboardPage  │
           │                  ├─────────────────┤  ├──────────────────┤
           │                  │ - controller    │  │ - controller     │
           │                  │ - theme         │  │ - theme          │
           │                  │ - user_entry    │  │ - pages (dict)   │
           │                  │ - pass_entry    │  │ - canvas         │
           │                  ├─────────────────┤  ├──────────────────┤
           │                  │ + build_ui()    │  │ + build_ui()     │
           │                  │ + submit_login()│  │ + AddUser()      │
           │                  └─────────────────┘  │ + TrainModel()   │
           │                                       │ + trigger_logoff()
           │                                       └──────────────────┘
           │
    ┌──────┴────────────┐
    │                   │
┌───────────────┐  ┌──────────────────┐
│  Networking   │  │    UserManager   │
├───────────────┤  ├──────────────────┤
│ - backend     │  │ - users (dict)   │
│ - user_manager│◄─┤ - json_path      │
│ - socket      │  ├──────────────────┤
│ - context     │  │ + add_user()     │
│ - is_running  │  │ + remove_user()  │
├───────────────┤  │ + get_user()     │
│ + Start()     │  │ + LoadUsers()    │
│ + Stop()      │  │ + SaveAllUsers() │
│ + Handler()   │  └──────────────────┘
│ + Login()     │           △
│ + Logout()    │           │
│ + RunImage()  │           │ contains
└───────────────┘           │
           △                │
           │ uses           │
           │                │
           │         ┌──────────────────┐
           │         │      User        │
           │         ├──────────────────┤
           │         │ - username       │
           │         │ - password       │
           │         │ - IP_address     │
           │         │ - soc            │
           │         │ - loggedin       │
           │         │ - clientThread   │
           │         │ - changelog      │
           │         ├──────────────────┤
           │         │ + ChangeName()   │
           │         │ + ChangePassword()
           │         │ + ChangeIP()     │
           │         │ + add_change()   │
           │         │ + clearLog()     │
           └─────────┘ + displayLogDebug()
                     └──────────────────┘
```

---

## Detailed Class Specifications

### 1. **Backend** (Server/Backend/AI/Backend.py)
**Purpose**: Handles AI model training, inference, and image prediction using PyTorch ResNet50

**Attributes**:
- `model`: ResNet50 neural network model
- `device`: torch.device (CUDA or CPU)
- `optimizer`: SGD optimizer for training
- `loss_fn`: CrossEntropyLoss function
- `train_dataset`: PyTorch ImageFolder dataset
- `train_dataloader`: DataLoader for batching
- `transform`: Image preprocessing pipeline
- `model_path`: Path to saved model file
- `epochs`: Number of training epochs (default: 3)
- `batch_size`: Training batch size (default: 32)
- `learning_rate`: Learning rate (default: 0.001)
- `MaxPixles`: Maximum image pixels to prevent decompression bombs (10M)
- `Training`: Boolean flag indicating training in progress
- `Processing`: Boolean flag indicating image processing in progress
- `lock`: Boolean flag locking network during model save
- `threshold`: Confidence threshold for predictions (default: 70%)

**Methods**:
- `__init__()`: Initialize model, datasets, and training parameters
- `train_model(epochs=None, progress_callback=None, on_training_complete=None)`: Train the model
- `predict(sample)`: Predict class of a sample image
- `predict_from_buffer(image_bytes)`: Predict from network image buffer
- `loadModel()`: Load trained model from disk
- `saveModel()`: Save trained model to disk
- `get_class_name(class_index)`: Return class name for index

**Relationships**:
- Used by: Frontend, Networking
- Dependencies: PyTorch, torchvision, PIL, numpy, pandas

---

### 2. **Frontend** (Server/UI/Frontend.py)
**Purpose**: Main GUI application using Tkinter for user interaction

**Attributes**:
- `root`: Tkinter root window
- `backend`: Backend instance (dependency injection)
- `network`: Networking instance (dependency injection)
- `container`: Main frame container
- `pages`: Dictionary of page frames
- `theme`: Dictionary of color/styling configuration
- `net_indicator`: Canvas for network status indicator
- `state_indicator`: Canvas for server state indicator
- `user_count_label`: Label for active users count
- `system_ID`: Admin system ID
- `system_password`: Admin system password

**Methods**:
- `__init__(root, backend_, network_)`: Initialize frontend with dependencies
- `boot()`: Start Tkinter main event loop
- `create_indicator_bar()`: Create top status bar with indicators
- `show_page(page_name)`: Switch to specified page
- `update_network_status_loop()`: Update network/server status indicators
- `trigger_login_attempt(username, password)`: Validate admin login
- `MakeButton(parent, text, command, bg_color, hover_color, click_color)`: Create styled button
- `Update()`: Update UI state (called at 30 FPS)

**Relationships**:
- Contains: LoginPage, DashboardPage
- Uses: Backend, Networking, MsgType (enum)
- Dependency: tkinter

---

### 3. **LoginPage** (Server/UI/Pages/LoginPage.py)
**Purpose**: Login authentication page for server access

**Attributes**:
- `controller`: Frontend instance (parent controller)
- `theme`: Theme dictionary reference
- `user_entry`: Entry widget for username/server ID
- `pass_entry`: Entry widget for password

**Methods**:
- `__init__(parent, controller)`: Initialize login page
- `build_ui()`: Construct UI elements
- `submit_login(event=None)`: Handle login submission

**Relationships**:
- Parent: tk.Frame
- Uses: Frontend (controller)

---

### 4. **DashboardPage** (Server/UI/Pages/DashboardPage.py)
**Purpose**: Dashboard for admin to manage users, network, and model training

**Attributes**:
- `controller`: Frontend instance (parent controller)
- `theme`: Theme dictionary reference
- `main_canvas`: Scrollable canvas container
- `scrollbar`: Vertical scrollbar
- `IP_entry`: Entry for network IP configuration
- `user_id_entry`: Entry for new user ID
- `new_password_entry`: Entry for new user password
- `InputIP`: Entry for user VPN IP address
- `train_button`: Button to trigger model training
- `Applybtn`: Button to apply network settings

**Methods**:
- `__init__(parent, controller)`: Initialize dashboard
- `build_ui()`: Construct dashboard UI
- `AddUser()`: Create new user account
- `ApplySettings()`: Apply network configuration changes
- `TrainModel()`: Initiate model training
- `TrainingComplete()`: Callback when training completes
- `TrainingProgress(progress)`: Callback for training progress
- `trigger_logoff()`: Logout and return to login page
- `update_scroll_region()`: Update scrollable region
- `resize_content(event)`: Resize content with canvas
- `enable_mousewheel()`, `disable_mousewheel()`: Mousewheel scroll handling

**Relationships**:
- Parent: tk.Frame
- Uses: Frontend (controller), UserManager

---

### 5. **Networking** (Server/NET/Networking.py)
**Purpose**: Handles secure multi-threaded TCP server with TLS/SSL encryption

**Attributes**:
- `backend`: Backend instance (dependency injection)
- `user_manager`: UserManager instance (dependency injection)
- `IP`: Server IP address (100.105.179.38)
- `port`: Server port (8500)
- `server_socket`: Raw TCP socket
- `context`: SSL/TLS context
- `listener_thread`: Background thread for accepting connections
- `stop_signal`: Threading event to signal shutdown
- `is_running`: Boolean flag indicating server status
- `is_connected`: Boolean flag for connection status
- `numberOfActiveUsers`: Count of logged-in users
- `current_time`: Internal clock for periodic checks
- `keepalive_time`, `keepalive_interval`: TCP keepalive parameters
- `connection_amount`: Maximum allowed connections
- `UserTimeOut`: User session timeout (5000 ticks)

**Methods**:
- `__init__(backend, user_manager)`: Initialize networking with dependencies
- `Start()`: Start the server
- `Stop()`: Stop the server and disconnect all clients
- `Restart(new_settings=None)`: Restart server with optional new settings
- `Listener(context)`: Listen for incoming connections
- `Handler(client_socket, user_, addr)`: Handle individual client communication
- `Login(client_ip, client_socket, user_, payload)`: Process login command
- `Logout(client_ip, client_socket, user_, payload)`: Process logout command
- `RunImage(client_ip, client_socket, user_, payload)`: Process image prediction request
- `send_packet(client_socket, msg_type, payload_bytes)`: Send protocol packet
- `extractParts(sock, num_bytes)`: Extract bytes from socket
- `enable_windows_keepalive(sock)`: Enable TCP keepalive on socket
- `AddActiveUser(bool_=True)`: Increment/decrement active user count
- `ForceLogout(user)`: Force logout user due to timeout/security
- `Update()`: Periodic update for user timeout checking (30 FPS)

**Relationships**:
- Uses: Backend, UserManager, User, MsgType (enum)
- Dependencies: socket, ssl, threading, struct

---

### 6. **UserManager** (Server/Backend/USER/UserManager.py)
**Purpose**: Manages user accounts and persistence

**Attributes**:
- `users`: Dictionary of User objects (key: username, value: User)
- `json_path`: Path to user data JSON file (Backend/USER/users.json)

**Methods**:
- `__init__()`: Initialize user manager
- `LoadUsers()`: Load users from JSON file
- `SaveAllUsers()`: Save all users to JSON file
- `add_user(username, password, ip, isManager=False)`: Add new user
- `remove_user(name)`: Remove user by username
- `get_user(name)`: Get user by username
- `getUserByIP(ip)`: Get user by IP address

**Relationships**:
- Contains: Multiple User objects
- Used by: Networking, Frontend, Server

---

### 7. **User** (Server/Backend/USER/User.py)
**Purpose**: Represents individual user account with session management

**Attributes**:
- `username`: User login name
- `password`: User password
- `Manager`: Boolean flag for manager privileges
- `IP_address`: VPN/whitelisted IP address (static)
- `port`: Port number (unused)
- `loggedin`: Boolean login state
- `idelTick`: Idle timer for session timeout
- `soc`: Network socket for client communication
- `clientThread`: Thread handling client communication
- `changelog`: Dictionary of session changes

**Methods**:
- `__init__(username, password, ip, isManager=False)`: Initialize user
- `add_change(time, change)`: Log session change
- `clearLog()`: Clear session changelog
- `displayLogDebug()`: Print changelog
- `ChangeName(name_)`: Update username (requires login)
- `ChangePassword(pass_)`: Update password (requires login)
- `ChangeIP(a, b, c, d)`: Update IP address with validation

**Relationships**:
- Contained by: UserManager
- Used by: Networking
- Dependencies: ipaddress, datetime

---

### 8. **MsgType** (Server/NET/protocol.py)
**Purpose**: Enumeration of protocol message types

**Attributes**:
- `LOGIN = 1`: User login command
- `LOGOUT = 2`: User logout command
- `IMAGE = 3`: Image prediction request

**Relationships**:
- Used by: Networking, Frontend

---

## Architecture & Design Patterns

### 1. **Dependency Injection Pattern**
- Backend, Networking, and UserManager are created in main_loop() and injected into Frontend
- Enables loose coupling and easier testing

### 2. **Model-View-Controller (MVC) Pattern**
- **Model**: Backend (AI model, training, prediction)
- **View**: Frontend + LoginPage + DashboardPage (UI components)
- **Controller**: Frontend acts as controller, coordinating between views and model

### 3. **Observer Pattern**
- Frontend observes Backend state via flags: `Training`, `Processing`
- Network status indicators update automatically

### 4. **Threading Architecture**
- **Main Thread**: Tkinter event loop with periodic updates (30, 120, 300 FPS)
- **Listener Thread**: Accepts incoming network connections
- **Handler Threads**: One per connected client for concurrent communication
- **Training Thread**: Optional background thread for model training

### 5. **Secure Communication**
- TLS 1.3 encryption for all network communication
- IP whitelisting via UserManager lookup
- Session management with timeout
- User credentials validation

---

## Data Flow

### Training Flow:
```
DashboardPage.TrainModel() 
    → Frontend.backend.train_model()
    → Backend.train_model()
    → Updates: Training, Processing flags
    → Callback to DashboardPage.TrainingComplete()
```

### Prediction Flow:
```
Client sends IMAGE
    → Networking.Listener() accepts connection
    → Networking.Handler() processes command
    → Networking.RunImage()
    → Backend.predict_from_buffer()
    → Backend.predict()
    → Response sent back to client
```

### User Management Flow:
```
DashboardPage.AddUser()
    → UserManager.add_user()
    → User object created
    → UserManager.SaveAllUsers()
    → JSON file updated
```

---

## External Dependencies

| Module | Purpose | Classes Used |
|--------|---------|--------------|
| torch | Deep learning framework | Backend |
| torchvision | Computer vision utilities | Backend |
| PIL | Image processing | Backend |
| numpy, pandas | Data manipulation | Backend |
| tkinter | GUI framework | Frontend, LoginPage, DashboardPage |
| socket, ssl | Network communication | Networking |
| threading | Multi-threading | Networking, Backend |
| json | Data serialization | UserManager |
| ipaddress | IP validation | User, DashboardPage |
| pathlib | File path handling | Backend |

---

## Key Security Features

1. **TLS/SSL Encryption**: All network communication encrypted
2. **IP Whitelisting**: Only whitelisted VPN IPs allowed
3. **Session Timeout**: Automatic logout after inactivity
4. **User Credentials**: Username and password validation
5. **Manager Privileges**: Support for privileged user accounts
6. **Decompression Bomb Protection**: Image pixel limit check
7. **Thread-Safe Operations**: Atomic operations for user tracking

---

## Scalability & Performance Considerations

1. **Multi-threaded Design**: Handles multiple simultaneous clients
2. **Lazy Model Loading**: Model loads once on backend initialization
3. **Batch Processing**: Uses DataLoader for efficient training
4. **Memory Management**: GPU/CPU memory tracking and reporting
5. **Keepalive Probes**: Detects and cleans up dead connections
6. **Confidence Threshold**: Reduces false positives in predictions

