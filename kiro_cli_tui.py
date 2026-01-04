#!/usr/bin/env python3
"""
Textual TUI application to control kiro-cli.

This provides a clean terminal interface for interacting with kiro-cli,
displaying the full kiro-cli screen without interference.
"""

from __future__ import annotations

import asyncio
import os
import pty
import select
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, RichLog, Static


class KiroCLIController(App):
    """Textual TUI for controlling kiro-cli with clean display."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #terminal-output {
        height: 1fr;
        background: black;
        color: white;
        border: none;
        padding: 0;
        margin: 0;
    }

    #input-bar {
        height: 3;
        background: $surface;
        border-top: solid $primary;
        layout: horizontal;
        padding: 0 1;
    }

    #command-input {
        width: 1fr;
        margin-right: 1;
    }

    #send-button {
        width: auto;
    }

    #status-bar {
        height: 1;
        background: $primary;
        color: $text;
        text-align: center;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+d", "quit", "Quit"),
        ("f1", "start_kiro", "Start"),
        ("f2", "stop_kiro", "Stop"),
    ]

    # Reactive variables
    kiro_cli_running = reactive(False)
    status_message = reactive("Ready - Press F1 to start Kiro CLI")

    def __init__(self):
        super().__init__()
        self.kiro_cli_process = None
        self.master_fd = None

    def compose(self) -> ComposeResult:
        """Compose the UI with minimal interference."""
        yield Header(show_clock=False)
        
        # Status bar
        yield Static(self.status_message, id="status-bar")
        
        # Terminal output (full screen)
        yield RichLog(id="terminal-output", auto_scroll=True, markup=False)
        
        # Input bar at bottom
        with Container(id="input-bar"):
            yield Input(
                placeholder="Type commands here...",
                id="command-input"
            )
            yield Button("Send", id="send-button", variant="primary")

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.query_one("#command-input").focus()

    def watch_kiro_cli_running(self, running: bool) -> None:
        """Update status when kiro-cli status changes."""
        if running:
            self.status_message = "Kiro CLI Running - Type commands below"
        else:
            self.status_message = "Ready - Press F1 to start Kiro CLI"

    def watch_status_message(self, message: str) -> None:
        """Update status bar display."""
        if self.is_mounted:
            try:
                self.query_one("#status-bar").update(message)
            except Exception:
                pass

    @on(Button.Pressed, "#send-button")
    def send_input_command(self) -> None:
        """Send command from input field."""
        input_widget = self.query_one("#command-input")
        command = input_widget.value.strip()
        if command:
            self.send_command(command)
            input_widget.value = ""

    @on(Input.Submitted, "#command-input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field."""
        command = event.value.strip()
        if command:
            self.send_command(command)
            event.input.value = ""

    def action_start_kiro(self) -> None:
        """Start kiro-cli."""
        self.start_kiro_cli_process()

    def action_stop_kiro(self) -> None:
        """Stop kiro-cli."""
        self.stop_kiro_cli_process()

    def start_kiro_cli_process(self) -> None:
        """Start the kiro-cli process with PTY."""
        if self.kiro_cli_running:
            return

        try:
            # Use the correct kiro-cli path
            kiro_cli_cmd = "/nfs/site/home/hfeng1/coder/.local/bin/kiro-cli"
            
            # Verify the command exists
            if not Path(kiro_cli_cmd).exists():
                self.log_output(f"ERROR: {kiro_cli_cmd} not found")
                return

            # Create PTY with proper size
            self.master_fd, slave_fd = pty.openpty()
            
            # Set terminal size
            import fcntl
            import termios
            import struct
            
            # Use a reasonable fixed size to avoid display issues
            rows, cols = 40, 120
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

            # Start kiro-cli process
            self.kiro_cli_process = subprocess.Popen(
                [kiro_cli_cmd],
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                cwd=str(Path.cwd()),
                preexec_fn=os.setsid,
                env=dict(os.environ, TERM='xterm-256color')
            )
            
            os.close(slave_fd)
            self.kiro_cli_running = True
            
            # Start reading output
            self.read_output()
            
        except Exception as e:
            self.log_output(f"ERROR: Failed to start Kiro CLI: {e}")
            if self.master_fd:
                os.close(self.master_fd)
                self.master_fd = None

    def stop_kiro_cli_process(self) -> None:
        """Stop the kiro-cli process."""
        if not self.kiro_cli_running:
            return

        try:
            if self.kiro_cli_process:
                # Send quit command
                self.send_command("quit", log=False)
                time.sleep(0.5)
                
                # Terminate process
                self.kiro_cli_process.terminate()
                try:
                    self.kiro_cli_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.kiro_cli_process.kill()
                    self.kiro_cli_process.wait()

            if self.master_fd:
                os.close(self.master_fd)
                self.master_fd = None

            self.kiro_cli_running = False
            self.log_output("Kiro CLI stopped")

        except Exception as e:
            self.log_output(f"ERROR: {e}")

    def send_command(self, command: str, log: bool = True) -> None:
        """Send command to kiro-cli."""
        if not self.kiro_cli_running or not self.master_fd:
            self.log_output("ERROR: Kiro CLI is not running")
            return

        try:
            os.write(self.master_fd, f"{command}\r\n".encode('utf-8'))
        except Exception as e:
            self.log_output(f"ERROR: Failed to send command: {e}")

    def log_output(self, text: str) -> None:
        """Add text to terminal output."""
        if self.is_mounted:
            try:
                terminal = self.query_one("#terminal-output")
                terminal.write(text)
            except Exception:
                pass

    @work(exclusive=True)
    async def read_output(self) -> None:
        """Read output from kiro-cli process."""
        terminal = self.query_one("#terminal-output")
        
        while self.kiro_cli_running and self.master_fd:
            try:
                # Check if data is available
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                
                if ready:
                    data = os.read(self.master_fd, 4096).decode('utf-8', errors='ignore')
                    if data:
                        # Write raw output to terminal
                        terminal.write(data, expand=True)
                
                # Check if process is still alive
                if self.kiro_cli_process and self.kiro_cli_process.poll() is not None:
                    self.kiro_cli_running = False
                    self.log_output("\n[Process ended]")
                    break
                    
                await asyncio.sleep(0.05)
                
            except OSError:
                break
            except Exception as e:
                self.log_output(f"ERROR: {e}")
                break

    def on_unmount(self) -> None:
        """Cleanup when app is closed."""
        self.stop_kiro_cli_process()


def main():
    """Run the Kiro CLI TUI application."""
    app = KiroCLIController()
    app.run()


if __name__ == "__main__":
    main()