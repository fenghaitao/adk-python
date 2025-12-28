#!/usr/bin/env python3
"""Helper script to interact with acli rovodev and extract session info."""

import os
import sys
import pty
import select
import time
import re

def run_acli_with_commands(commands, timeout=90):
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
    prompt_seen = False
    waiting_for_response = False
    
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
                        last_data_time = time.time()
                        
                        # Detect when prompt appears (look for '> ' or '>' at end)
                        if '>' in data and not waiting_for_response:
                            prompt_seen = True
                            time.sleep(0.5)  # Wait for prompt to fully render
                            
                            if command_index < len(commands):
                                cmd = commands[command_index]
                                print(f"\n[Sending command: {cmd}]", file=sys.stderr)
                                os.write(master, (cmd + '\n').encode('utf-8'))
                                command_index += 1
                                waiting_for_response = True
                                last_data_time = time.time()
                        
                        # After sending command, wait for response to complete
                        if waiting_for_response and ('>' in data or 'Session ID' in data):
                            waiting_for_response = False
                
                except OSError:
                    break
            
            # If no data for 3 seconds and we've sent all commands, exit
            if command_index >= len(commands) and time.time() - last_data_time > 3:
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
