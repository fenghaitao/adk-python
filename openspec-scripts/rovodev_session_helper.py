#!/usr/bin/env python3
"""Helper script to interact with acli rovodev and extract session info."""

import os
import sys
import pty
import select
import time
import re

def run_acli_with_commands(commands, timeout=600):
    """Run acli rovodev with commands sent to interactive session."""
    acli_path = os.environ.get('ACLI_CMD', os.path.expanduser('~/acli'))
    
    # Create a pseudo-terminal
    master, slave = pty.openpty()
    
    # Fork the process
    pid = os.fork()
    
    if pid == 0:  # Child process
        os.close(master)
        os.dup2(slave, 0)  # stdin
        os.dup2(slave, 1)  # stdout
        os.dup2(slave, 2)  # stderr
        os.close(slave)
        
        # Execute acli
        os.execv(acli_path, [acli_path, 'rovodev', 'run', '--yolo'])
    
    # Parent process
    os.close(slave)
    
    output = []
    command_index = 0
    start_time = time.time()
    last_data_time = start_time
    last_output = ""  # Track recent output (last 500 chars) for pattern matching
    
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
                        
                        # Keep last 500 chars for pattern matching
                        last_output = (last_output + data)[-500:]
                        
                        # Only update last_data_time if this is not just cursor blinking
                        # Cursor blink patterns: just whitespace, or contains '> █' in small chunks
                        # Also ignore box drawing and formatting characters
                        is_cursor_blink = (
                            data.strip() == '' or 
                            (len(data) < 200 and '█' in data and data.count('\n') < 3)
                        )
                        
                        if not is_cursor_blink:
                            last_data_time = time.time()
                
                except OSError:
                    break
            
            # Check if we should send the next command
            idle_time = time.time() - last_data_time
            
            if command_index < len(commands):
                # Look for the prompt pattern '│ > ' or '\n> '
                # The prompt may not be at the very end due to footer text
                cleaned_output = last_output.replace('█', '')
                has_prompt = ('│ > ' in cleaned_output or '\n> ' in cleaned_output)
                
                # For first command, send immediately when prompt appears (no idle wait)
                # For subsequent commands, wait 5 seconds of idle time
                if command_index == 0:
                    required_idle = 0.0  # Send immediately
                else:
                    required_idle = 5.0  # Wait for idle
                
                if has_prompt and idle_time >= required_idle:
                    cmd = commands[command_index]
                    os.write(master, (cmd + '\n').encode('utf-8'))
                    command_index += 1
                    last_data_time = time.time()  # Reset idle timer
            
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
    
    full_output = ''.join(output)
    
    # Try to extract session ID from output
    session_id = None
    
    # Look for UUID pattern (session IDs are UUIDs)
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    
    # Look for "Session ID:" or "Current session:" patterns
    session_patterns = [
        r'Session ID:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        r'Current session:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        r'session:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
    ]
    
    for pattern in session_patterns:
        match = re.search(pattern, full_output, re.IGNORECASE)
        if match:
            session_id = match.group(1)
            break
    
    # If not found in labeled output, look for any UUID in the sessions output
    if not session_id and '/sessions' in ' '.join(commands):
        matches = re.findall(uuid_pattern, full_output)
        if matches:
            # Take the last UUID found (most likely the current session)
            session_id = matches[-1]
    
    return full_output, session_id

if __name__ == '__main__':
    commands = sys.argv[1:] if len(sys.argv) > 1 else ['/help', '/exit']
    
    print(f"Running acli with commands: {commands}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    output, session_id = run_acli_with_commands(commands)
    
    print("\n" + "=" * 60, file=sys.stderr)
    print("Session complete", file=sys.stderr)
    
    if session_id:
        print(f"\n✅ Extracted Session ID: {session_id}", file=sys.stderr)
        # Print ONLY session ID to stdout for easy capture
        print(session_id)
    else:
        print("\n⚠️  Could not extract session ID", file=sys.stderr)
