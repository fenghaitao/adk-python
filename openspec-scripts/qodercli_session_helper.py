#!/usr/bin/env python3
"""Helper script to interact with qodercli and extract session info."""

import os
import sys
import pty
import select
import time
import re

def run_qodercli_with_commands(commands, timeout=600):
    """Run qodercli with commands sent to interactive session."""
    qodercli_path = os.environ.get('QODERCLI_CMD', 'qodercli')
    
    # Create a pseudo-terminal
    master, slave = pty.openpty()
    
    # Set terminal size to avoid "Terminal window too small" errors
    # Set to a reasonable size: 100 columns x 30 rows
    import fcntl
    import termios
    import struct
    winsize = struct.pack('HHHH', 30, 100, 0, 0)  # rows, cols, xpixel, ypixel
    fcntl.ioctl(slave, termios.TIOCSWINSZ, winsize)
    
    # Fork the process
    pid = os.fork()
    
    if pid == 0:  # Child process
        os.close(master)
        os.dup2(slave, 0)  # stdin
        os.dup2(slave, 1)  # stdout
        os.dup2(slave, 2)  # stderr
        os.close(slave)
        
        # Execute qodercli with --dangerously-skip-permissions flag
        os.execlp(qodercli_path, qodercli_path, '--dangerously-skip-permissions')
    
    # Parent process
    os.close(slave)
    
    output = []
    command_index = 0
    start_time = time.time()
    last_data_time = start_time
    last_output = ""  # Track recent output (last 2000 chars) for pattern matching
    
    try:
        while time.time() - start_time < timeout:
            # Check if there's data to read
            ready, _, _ = select.select([master], [], [], 0.1)
            
            if ready:
                try:
                    data = os.read(master, 1024).decode('utf-8', errors='ignore')
                    if data:
                        output.append(data)
                        sys.stdout.write(data)
                        sys.stdout.flush()
                        
                        # Keep last 2000 chars for pattern matching
                        last_output = (last_output + data)[-2000:]
                        
                        # Only update last_data_time if this is not just cursor blinking or spinner
                        is_cursor_blink = (
                            data.strip() == '' or 
                            (len(data) < 200 and '█' in data and data.count('\n') < 3) or
                            (len(data) < 100 and 'Generating...' in data)  # Ignore spinner updates
                        )
                        
                        if not is_cursor_blink:
                            last_data_time = time.time()
                
                except OSError:
                    break
            
            # Check if we should send the next command
            idle_time = time.time() - last_data_time
            
            if command_index < len(commands):
                # Strip ANSI escape codes for better matching
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                cleaned_output = ansi_escape.sub('', last_output)
                cleaned_output = cleaned_output.replace('█', '')
                
                # Check for various prompt patterns
                # Also check if we see the bullet point "●" which indicates response is complete
                has_prompt = (
                    '│ > ' in cleaned_output or 
                    '\n> ' in cleaned_output or 
                    cleaned_output.strip().endswith('> ') or
                    cleaned_output.strip().endswith('>') or
                    'Type your message' in cleaned_output  # qodercli specific
                )
                
                # For subsequent commands, check if response is complete
                # For regular responses: ● marker + prompt box
                # For /status command: look for "Session ID" in output
                response_complete = False
                if command_index > 0:
                    # Check if previous command was /status
                    if command_index > 1 and len(commands) > command_index - 1:
                        prev_cmd = commands[command_index - 1].strip().lower()
                        if prev_cmd == '/status':
                            # Wait for "Session ID" to appear in status screen
                            response_complete = 'Session ID' in cleaned_output
                        else:
                            # Regular response: bullet + prompt box
                            response_complete = '● ' in cleaned_output and '│ > ' in cleaned_output
                    else:
                        # First response after prompt
                        response_complete = '● ' in cleaned_output and '│ > ' in cleaned_output
                
                # For first command, send immediately when prompt detected
                # For subsequent commands, send when we see response complete OR after idle time
                if command_index == 0:
                    ready_to_send = has_prompt
                else:
                    # Send if response is clearly complete, or after 1 second of real idle
                    ready_to_send = response_complete or (has_prompt and idle_time >= 1.0)
                
                if ready_to_send:
                    cmd = commands[command_index]
                    # Send command with newline and flush
                    os.write(master, f"{cmd}\r\n".encode('utf-8'))
                    command_index += 1
                    last_data_time = time.time()  # Reset idle timer
                    time.sleep(0.5)  # Brief pause after sending
            
            # If no data for 10 seconds and we've sent all commands, exit
            if command_index >= len(commands) and idle_time > 10:
                break
            
            # Check if process is still alive
            try:
                pid_status, _ = os.waitpid(pid, os.WNOHANG)
                if pid_status != 0:
                    break
            except ChildProcessError:
                break
    
    finally:
        os.close(master)
        try:
            os.kill(pid, 9)
            os.waitpid(pid, 0)
        except:
            pass
    
    return ''.join(output)

if __name__ == '__main__':
    commands = sys.argv[1:] if len(sys.argv) > 1 else ['/help', '/exit']
    
    print(f"Running qodercli with commands: {commands}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    output = run_qodercli_with_commands(commands)
    
    print("\n" + "=" * 60, file=sys.stderr)
    print("Session complete", file=sys.stderr)
