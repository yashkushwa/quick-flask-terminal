
#!/usr/bin/env python3
import os
import pty
import select
import subprocess
import termios
import struct
import fcntl
import signal
import sys
from threading import Thread
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Store active terminals
terminals = {}

def set_winsize(fd, row, col):
    winsize = struct.pack("HHHH", row, col, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

def read_terminal_output(terminal_id):
    master_fd = terminals[terminal_id]["fd"]
    while True:
        try:
            ready, _, _ = select.select([master_fd], [], [], 0.1)
            if ready:
                data = os.read(master_fd, 1024)
                if data:
                    socketio.emit(f'terminal_output_{terminal_id}', {'output': data.decode('utf-8', errors='replace')})
                else:
                    socketio.emit(f'terminal_output_{terminal_id}', {'output': '\r\nSession terminated\r\n'})
                    break
        except (OSError, IOError) as e:
            socketio.emit(f'terminal_output_{terminal_id}', {'output': f'\r\nError: {str(e)}\r\n'})
            break
        except Exception as e:
            socketio.emit(f'terminal_output_{terminal_id}', {'output': f'\r\nUnexpected error: {str(e)}\r\n'})
            break

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    # Clean up terminals when client disconnects
    for terminal_id in list(terminals.keys()):
        try:
            os.close(terminals[terminal_id]["fd"])
            if terminals[terminal_id]["process"].poll() is None:
                terminals[terminal_id]["process"].kill()
        except:
            pass
        del terminals[terminal_id]

@socketio.on('create_terminal')
def handle_create_terminal(data):
    terminal_id = data.get('terminal_id', 'default')
    rows = data.get('rows', 24)
    cols = data.get('cols', 80)
    
    # Close existing terminal if it exists
    if terminal_id in terminals:
        try:
            os.close(terminals[terminal_id]["fd"])
            if terminals[terminal_id]["process"].poll() is None:
                terminals[terminal_id]["process"].kill()
        except:
            pass
    
    # Create new terminal
    shell = os.environ.get('SHELL', '/bin/bash')
    master_fd, slave_fd = pty.openpty()
    
    # Set terminal size
    set_winsize(master_fd, rows, cols)
    
    # Start shell process
    process = subprocess.Popen(
        shell, 
        preexec_fn=os.setsid,
        stdin=slave_fd, 
        stdout=slave_fd, 
        stderr=slave_fd, 
        universal_newlines=True
    )
    
    # Close slave_fd as it's being used by the child process
    os.close(slave_fd)
    
    # Store terminal information
    terminals[terminal_id] = {
        "fd": master_fd,
        "process": process
    }
    
    # Start thread to read output
    Thread(target=read_terminal_output, args=(terminal_id,), daemon=True).start()
    
    # Send an initial prompt
    os.write(master_fd, b"\n")
    
    return {'success': True, 'terminal_id': terminal_id}

@socketio.on('resize_terminal')
def handle_resize_terminal(data):
    terminal_id = data.get('terminal_id', 'default')
    rows = data.get('rows', 24)
    cols = data.get('cols', 80)
    
    if terminal_id in terminals:
        set_winsize(terminals[terminal_id]["fd"], rows, cols)
        return {'success': True}
    return {'success': False, 'error': 'Terminal not found'}

@socketio.on('terminal_input')
def handle_terminal_input(data):
    terminal_id = data.get('terminal_id', 'default')
    input_data = data.get('input', '')
    
    if terminal_id in terminals:
        try:
            os.write(terminals[terminal_id]["fd"], input_data.encode())
            return {'success': True}
        except Exception as e:
            print(f"Error writing to terminal: {str(e)}")
            return {'success': False, 'error': str(e)}
    return {'success': False, 'error': 'Terminal not found'}

@socketio.on('destroy_terminal')
def handle_destroy_terminal(data):
    terminal_id = data.get('terminal_id', 'default')
    
    if terminal_id in terminals:
        try:
            os.close(terminals[terminal_id]["fd"])
            if terminals[terminal_id]["process"].poll() is None:
                terminals[terminal_id]["process"].kill()
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            del terminals[terminal_id]
    
    return {'success': True}

def cleanup_terminals():
    for terminal_id in list(terminals.keys()):
        try:
            os.close(terminals[terminal_id]["fd"])
            if terminals[terminal_id]["process"].poll() is None:
                terminals[terminal_id]["process"].kill()
        except:
            pass

def signal_handler(sig, frame):
    cleanup_terminals()
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        port = 8080
        print(f"Terminal server starting on port {port}...")
        socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
    finally:
        cleanup_terminals()
