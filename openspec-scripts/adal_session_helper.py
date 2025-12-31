#!/usr/bin/env python3
"""Helper script to interact with adal and extract session info."""

import os
import sys
import pty
import select
import time
import re

def run_adal_with_commands(commands, timeout=120):
    """Run adal with commands sent to interactive session."""
    adal_path = os.environ.get('ADAL_CMD', 'adal')
    
    # Create a pseudo-terminal
    master, slave = pty.openpty()
    
    # Set terminal size to avoid "Terminal window too small" errors
    # Use a larger size for better compatibility: 120 columns x 40 rows
    import fcntl
    import termios
    import struct
    winsize = struct.pack('HHHH', 40, 120, 0, 0)  # rows, cols, xpixel, ypixel
    fcntl.ioctl(slave, termios.TIOCSWINSZ, winsize)
    
    # Fork the process
    pid = os.fork()
    
    if pid == 0:  # Child process
        os.close(master)
        os.dup2(slave, 0)  # stdin
        os.dup2(slave, 1)  # stdout
        os.dup2(slave, 2)  # stderr
        os.close(slave)
        
        # Set TERM for better compatibility
        os.environ['TERM'] = 'xterm-256color'
        
        # Execute adal without any arguments to avoid the stripAnsi bug
        os.execlp(adal_path, adal_path)
    
    # Parent process
    os.close(slave)
    
    print(f"[DEBUG] Started adal process (PID: {pid})", file=sys.stderr)
    
    output = []
    command_index = 0
    start_time = time.time()
    last_data_time = start_time
    last_output = ""  # Track recent output (last 2000 chars) for pattern matching
    seen_response_marker = False  # Track if we've seen ⏺ marker for current response
    seen_response_end_marker = False  # Track if we've seen ⏹ (response end) marker
    data_received_count = 0  # Track how much data we've received
    all_commands_sent_time = None  # Track when all commands were sent
    
    try:
        while time.time() - start_time < timeout:
            # Check if there's data to read
            ready, _, _ = select.select([master], [], [], 0.1)
            
            if ready:
                try:
                    data = os.read(master, 1024).decode('utf-8', errors='ignore')
                    if data:
                        data_received_count += len(data)
                        output.append(data)
                        
                        # Write to stdout - this should appear on screen
                        sys.stdout.write(data)
                        sys.stdout.flush()
                        
                        # Keep last 2000 chars for pattern matching
                        last_output = (last_output + data)[-2000:]
                        
                        # Track if we see the response marker (⏺) or response content
                        # Be more lenient in detecting responses
                        response_indicators = [
                            '⏺', "I'm AdaL", "Hey there", "Hello", "Hi",
                            "Sure", "I can", "I'll", "Let me", "Here",
                            "Loading statistics",  # /stats response
                            "Session ID:",  # /stats output
                            data_received_count > 500  # If we received substantial data
                        ]
                        if any(indicator in data if isinstance(indicator, str) else indicator for indicator in response_indicators):
                            if not seen_response_marker:
                                print(f"[DEBUG] Response marker/content detected!", file=sys.stderr)
                            seen_response_marker = True
                            # Always update last_data_time when we see response content
                            last_data_time = time.time()
                        
                        # Track if we see the response end marker (⏹)
                        if '⏹' in data or 'response complete' in data.lower():
                            if not seen_response_end_marker:
                                print(f"[DEBUG] Response end marker detected!", file=sys.stderr)
                            seen_response_end_marker = True
                            last_data_time = time.time()
                        
                        # Only update last_data_time if this is not just cursor blinking or spinner
                        is_cursor_blink = (
                            data.strip() == '' or 
                            (len(data) < 200 and '█' in data and data.count('\n') < 3) or
                            (len(data) < 100 and 'Generating...' in data) or  # Ignore spinner updates
                            (len(data) < 100 and 'Loading...' in data) or  # Ignore loading spinner
                            (len(data) < 100 and 'Tuning' in data) or  # Ignore tuning messages
                            (len(data) < 150 and 'Branch:' in data) or  # Ignore branch status updates
                            (len(data) < 150 and '? to toggle' in data)  # Ignore help text updates
                        )
                        
                        if not is_cursor_blink:
                            last_data_time = time.time()
                
                except OSError:
                    break
            
            # Check if we should send the next command
            idle_time = time.time() - last_data_time
            
            # Debug: show we're waiting for response (every 10 seconds)
            if command_index > 0 and command_index < len(commands) and not seen_response_marker:
                if int(idle_time) % 10 == 0 and idle_time - int(idle_time) < 0.2:
                    print(f"[DEBUG] Still waiting for response to command {command_index}/{len(commands)}, idle={idle_time:.1f}s", file=sys.stderr)
            
            if command_index < len(commands):
                # Strip ANSI escape codes for better matching
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                cleaned_output = ansi_escape.sub('', last_output)
                cleaned_output = cleaned_output.replace('█', '')
                
                # Check for adal's prompt pattern (simplified)
                # Look for the > prompt indicator with more lenient matching
                has_separator = '─' in cleaned_output or '━' in cleaned_output or '—' in cleaned_output
                # Look for prompt in various formats
                has_prompt_pattern = (
                    '\r\n>' in cleaned_output or 
                    '\n>' in cleaned_output or
                    '\n >' in cleaned_output or
                    '>\n' in cleaned_output[-100:]  # Check end of output
                )
                # Be more lenient: prompt detected if we see separator OR prompt pattern
                has_prompt = has_separator or (has_prompt_pattern and idle_time >= 0.3)
                
                # Response is complete when we see the prompt and have been idle
                response_complete = False
                
                # Check if the last command we sent was /stats
                last_cmd_was_stats = (command_index > 0 and 
                                     commands[command_index - 1].strip().lower() == '/stats')
                
                if command_index > 0:
                    if last_cmd_was_stats:
                        # /stats shows a modal with stats information
                        # Look for various indicators that stats were displayed
                        has_session_id = (
                            'Session ID:' in cleaned_output or 
                            'session_id' in cleaned_output.lower() or
                            'conversation_id' in cleaned_output.lower() or
                            'Session Statistics' in cleaned_output
                        )
                        # Look for any indication we can close or continue
                        has_close_indicator = (
                            'esc' in cleaned_output.lower() or
                            'close' in cleaned_output.lower() or
                            'press' in cleaned_output.lower()
                        )
                        
                        # Debug every 5 seconds when waiting for /stats modal
                        if not has_session_id and idle_time >= 5.0:
                            if int(idle_time) % 5 == 0 and idle_time - int(idle_time) < 0.2:
                                print(f"[DEBUG] Waiting for /stats response: session_id={has_session_id}, close_indicator={has_close_indicator}, idle={idle_time:.1f}s", file=sys.stderr)
                                print(f"[DEBUG] Last 300 chars: ...{cleaned_output[-300:]}", file=sys.stderr)
                        
                        # If we see stats info, send ESC to close modal (if needed) or just wait for prompt
                        if has_session_id and has_close_indicator and idle_time >= 0.5:
                            # Send ESC key to close the modal
                            os.write(master, b'\x1b')  # ESC key
                            print(f"[DEBUG] Sent ESC to close /stats modal", file=sys.stderr)
                            last_data_time = time.time()  # Reset idle timer after sending ESC
                            time.sleep(0.5)
                        
                        # Response is complete when we see the prompt again
                        # Either after closing modal or if stats just displayed inline
                        response_complete = (
                            (has_session_id and has_prompt and idle_time >= 0.5) or
                            (has_prompt and idle_time >= 4.0)  # Fallback if stats doesn't show
                        )
                    else:
                        # Regular response: wait for actual AI response to complete
                        # Must see both start marker AND end marker, plus prompt
                        response_complete = (
                            (seen_response_marker and seen_response_end_marker and has_prompt and idle_time >= 1.0) or
                            (seen_response_marker and has_prompt and idle_time >= 10.0) or  # Fallback if no end marker
                            (has_prompt and idle_time >= 15.0)  # Last resort: just wait very long
                        )
                        
                        # Debug every 5 seconds when waiting for response completion
                        if seen_response_marker and not response_complete and idle_time >= 5.0:
                            if int(idle_time) % 5 == 0 and idle_time - int(idle_time) < 0.2:  # Every 5 seconds
                                print(f"[DEBUG] Waiting for completion: start_marker=True, end_marker={seen_response_end_marker}, prompt={has_prompt}, idle={idle_time:.1f}s", file=sys.stderr)
                                # Show if we have separator and prompt pattern
                                print(f"[DEBUG] has_separator={has_separator}, has_prompt_pattern={has_prompt_pattern}", file=sys.stderr)
                                # Show last 200 chars to debug prompt detection
                                print(f"[DEBUG] Last 200 chars: ...{cleaned_output[-200:]}", file=sys.stderr)
                
                # For first command, send immediately when prompt detected
                # For subsequent commands, wait for response to complete
                if command_index == 0:
                    ready_to_send = has_prompt and idle_time >= 0.3
                else:
                    # Wait for response to be complete
                    ready_to_send = response_complete
                
                if ready_to_send:
                    cmd = commands[command_index]
                    print(f"\n[DEBUG] ==================== SENDING COMMAND {command_index + 1}/{len(commands)} ====================", file=sys.stderr)
                    print(f"[DEBUG] Command: '{cmd}'", file=sys.stderr)
                    print(f"[DEBUG] last_cmd_was_stats={last_cmd_was_stats if command_index > 0 else 'N/A'}", file=sys.stderr)
                    print(f"[DEBUG] Conditions: start_marker={seen_response_marker}, end_marker={seen_response_end_marker}, prompt={has_prompt}, idle={idle_time:.1f}s", file=sys.stderr)
                    # Send command with newline and flush
                    cmd_bytes = f"{cmd}\r\n".encode('utf-8')
                    bytes_written = os.write(master, cmd_bytes)
                    print(f"[DEBUG] Wrote {bytes_written} bytes to terminal", file=sys.stderr)
                    prev_command_index = command_index
                    command_index += 1
                    print(f"[DEBUG] command_index: {prev_command_index} -> {command_index}", file=sys.stderr)
                    last_data_time = time.time()  # Reset idle timer
                    seen_response_marker = False  # Reset for next response
                    seen_response_end_marker = False  # Reset for next response
                    
                    # Track when all commands are sent
                    if command_index >= len(commands):
                        all_commands_sent_time = time.time()
                        print(f"[DEBUG] All {len(commands)} commands sent!", file=sys.stderr)
                    
                    time.sleep(0.3)  # Brief pause after sending
                    
                    # After sending first command, wait and check if adal is responding
                    if command_index == 1:
                        print(f"[DEBUG] Waiting for adal to respond to '{cmd}'...", file=sys.stderr)
            
            # If no data for 5 seconds and we've sent all commands, exit
            if command_index >= len(commands):
                if all_commands_sent_time and (time.time() - all_commands_sent_time) > 8:
                    print(f"[DEBUG] Emergency timeout: 8s since all commands sent, exiting", file=sys.stderr)
                    break
                if idle_time > 5:
                    print(f"[DEBUG] All commands sent and idle for {idle_time:.1f}s, exiting", file=sys.stderr)
                    break
            
            # Check if process is still alive
            try:
                pid_status, _ = os.waitpid(pid, os.WNOHANG)
                if pid_status != 0:
                    print(f"[DEBUG] Child process exited (status={pid_status})", file=sys.stderr)
                    break
            except ChildProcessError:
                print(f"[DEBUG] Child process terminated", file=sys.stderr)
                break
            except OSError as e:
                print(f"[DEBUG] OSError checking process: {e}", file=sys.stderr)
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
    
    # Insert /stats at the beginning to capture session info early
    if '/stats' not in commands:
        commands.insert(0, '/stats')
    
    print(f"Running adal with commands: {commands}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    output = run_adal_with_commands(commands)
    
    print("\n" + "=" * 60, file=sys.stderr)
    print("Session complete", file=sys.stderr)
