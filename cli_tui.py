#!/usr/bin/env python3
"""
Textual TUI application to control kiro-cli.

This provides a clean terminal interface for interacting with kiro-cli,
displaying the full kiro-cli screen without interference.

Architecture:
- ProcessContainer: Manages PTY and process lifecycle
- TerminalRestorer: Handles terminal state save/restore
- KiroCLIApp: Main Textual application with multi-agent support

Phase 2-4 enhancements:
- Multi-pane layout with agent sidebar
- Status panel with metrics
- Integrated chat interface
- Command history and search
- Session management
"""

from __future__ import annotations

import asyncio
import atexit
import fcntl
import json
import logging
import os
import pty
import pyte
import re
import select
import shlex
import shutil
import signal
import struct
import subprocess
import sys
import termios
import time
import traceback
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.events import Key
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    OptionList,
    RadioButton,
    RadioSet,
    RichLog,
    Static,
    TabbedContent,
    TabPane,
)
from textual.widgets.option_list import Option
from textual.screen import ModalScreen

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TerminalRestorer:
    """Context manager to save/restore terminal state around a fullscreen app."""

    def __enter__(self):
        # Save current terminal state only if running in an interactive terminal
        if sys.stdin.isatty():
            self.fd = sys.stdin.fileno()
            self._orig_termios = termios.tcgetattr(self.fd)
            try:
                result = subprocess.run(
                    ["stty", "-g"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    check=True,
                    text=True
                )
                self._orig_stty = result.stdout.strip()
            except subprocess.SubprocessError:
                self._orig_stty = None
        else:
            self.fd = None
            self._orig_termios = None
            self._orig_stty = None

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup_terminal()
        return False

    def _cleanup_terminal(self):
        """Restore terminal to original state and exit alternate screen."""
        # Exit alternate screen buffer (restores original terminal content)
        sys.stdout.write("\033[?1049l")
        sys.stdout.flush()

        # Restore low-level terminal attributes (input modes, special chars, etc.)
        if self.fd is not None and self._orig_termios is not None:
            try:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self._orig_termios)
            except Exception as e:
                logger.error(f"Failed to restore termios attributes: {e}")

        # Restore high-level terminal settings (echo, erase char, flow control)
        if self._orig_stty:
            try:
                subprocess.run(
                    ["stty"] + self._orig_stty.split(),
                    stderr=subprocess.DEVNULL,
                    check=False
                )
            except Exception as e:
                logger.error(f"Failed to restore stty settings: {e}")

        logger.info("Terminal state restored")


class ProcessContainer:
    """Manages PTY-based process execution for kiro-cli.
    
    Provides better process lifecycle management and error handling.
    """

    def __init__(
        self,
        cmd: str,
        exit_callback: Optional[Callable] = None,
    ) -> None:
        self.read_buf_len = 32768
        self.script_cmd = cmd
        self.output_queue: asyncio.Queue = asyncio.Queue()
        self.input_queue: asyncio.Queue = asyncio.Queue()
        self.exit_callback = exit_callback
        # Initialize attributes that will be set later
        self.process = None
        self.process_buffer = bytearray()
        self.master_fd = None
        self.slave_fd = None

    def cleanup(self):
        """Clean up resources when process exits or errors occur."""
        try:
            if self.master_fd:
                try:
                    os.close(self.master_fd.fileno())
                    logger.debug("Master file descriptor closed")
                except Exception as e:
                    logger.warning(f"Error closing master file descriptor: {str(e)}")

            if self.slave_fd:
                try:
                    os.close(self.slave_fd.fileno())
                    logger.debug("Slave file descriptor closed")
                except Exception as e:
                    logger.warning(f"Error closing slave file descriptor: {str(e)}")

            if self.process and self.process.returncode is None:
                try:
                    self.process.kill()
                    logger.info("Process terminated")
                except Exception as e:
                    logger.warning(f"Error killing process: {str(e)}")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def process_monitor(self):
        """Monitor the process and call exit_callback when it terminates."""
        try:
            logger.debug("Starting process monitor")
            while True:
                if self.process is None:
                    logger.error("Process is None in process_monitor")
                    break

                if self.process.returncode is not None:
                    logger.info(
                        f"Process exited with return code {self.process.returncode}"
                    )
                    break

                await asyncio.sleep(1)

            if self.exit_callback:
                try:
                    logger.debug("Calling exit callback")
                    self.exit_callback()
                except Exception as e:
                    logger.error(f"Error in exit callback: {str(e)}")
        except asyncio.CancelledError:
            logger.info("Process monitor task cancelled")
            raise
        except Exception as e:
            logger.error(f"Error monitoring process: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            self.cleanup()

    async def open_terminal(self):
        """Open a pseudo-terminal and start the subprocess."""
        try:
            logger.debug("Opening terminal")
            try:
                master_fd, slave_fd = pty.openpty()
            except OSError as e:
                logger.error(f"Failed to open pseudo-terminal: {str(e)}")
                raise

            # Set terminal size
            rows, cols = 40, 120
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

            argv = shlex.split(self.script_cmd)

            try:
                self.process = await asyncio.create_subprocess_exec(
                    *argv,
                    stdin=slave_fd,
                    stdout=slave_fd,
                    stderr=slave_fd,
                    bufsize=0,
                    close_fds=True,
                )
                logger.debug(f"Process started with PID {self.process.pid}")
            except (OSError, ValueError) as e:
                os.close(master_fd)
                os.close(slave_fd)
                logger.error(f"Failed to create subprocess: {str(e)}")
                raise

            try:
                self.slave_fd = os.fdopen(slave_fd, "w+b", 0, closefd=True)
                self.master_fd = os.fdopen(master_fd, "w+b", 0, closefd=True)
            except OSError as e:
                if self.process:
                    self.process.kill()
                os.close(master_fd)
                os.close(slave_fd)
                logger.error(f"Failed to open file descriptors: {str(e)}")
                raise

            logger.debug("Terminal opened successfully")
        except Exception as e:
            logger.error(f"Unexpected error opening terminal: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def start(self):
        """Start the process and set up listeners."""
        try:
            logger.info(f"Starting process with command: {self.script_cmd}")
            await self.open_terminal()

            # Create tasks with proper error handling
            asyncio.create_task(self.input_listener())
            asyncio.create_task(self.output_listener())
            asyncio.create_task(self.process_monitor())
            atexit.register(lambda: self.cleanup())

            logger.info("Process started successfully")
        except Exception as e:
            logger.error(f"Unexpected error starting process: {str(e)}")
            self.cleanup()
            raise

    async def input_listener(self):
        """Listen for input operations and process them."""
        try:
            logger.debug("Starting input listener")
            while True:
                try:
                    data = await self.input_queue.get()
                    if data is None:
                        break
                    
                    if isinstance(data, str):
                        # Send string to process
                        self.master_fd.write(data.encode())
                    elif isinstance(data, dict):
                        # Handle special operations
                        if data.get('type') == 'disconnect':
                            logger.info("Disconnecting")
                            break
                        elif data.get('type') == 'sigint':
                            if self.process and self.process.returncode is None:
                                logger.debug("Sending SIGINT to process")
                                self.process.send_signal(signal.SIGINT)
                except Exception as e:
                    logger.error(f"Error processing input: {str(e)}")
        except asyncio.CancelledError:
            logger.info("Input listener task cancelled")
            raise
        except Exception as e:
            logger.error(f"Fatal error in input listener: {str(e)}")
            logger.error(traceback.format_exc())

    async def output_listener(self):
        """Listen for output from the process."""
        def process_output_callback(loop):
            """Callback for processing output from the process."""
            try:
                data = self.master_fd.read(self.read_buf_len)
                if not data:
                    logger.warning("No data read from master file descriptor")
                    self.output_queue.put_nowait({'type': 'disconnect'})
                    loop.remove_reader(self.master_fd)
                    return

                self.process_buffer += data

                try:
                    decoded_output = self.process_buffer.decode()
                    self.output_queue.put_nowait(decoded_output)
                    self.process_buffer.clear()
                except UnicodeDecodeError as e:
                    logger.debug(
                        f"Incomplete unicode sequence, "
                        f"buffer size: {len(self.process_buffer)} bytes"
                    )
                    decoded_output = self.process_buffer[:e.start].decode()
                    self.process_buffer = self.process_buffer[e.start:]
                    if len(decoded_output):
                        self.output_queue.put_nowait(decoded_output)
            except OSError as e:
                logger.error(f"OSError in output callback: {str(e)}")
                self.output_queue.put_nowait({'type': 'disconnect'})
                loop.remove_reader(self.master_fd)
            except Exception as e:
                logger.error(f"Unexpected error in output callback: {str(e)}")
                loop.remove_reader(self.master_fd)

        logger.debug("Starting output listener")
        loop = asyncio.get_running_loop()
        loop.add_reader(self.master_fd, process_output_callback, loop)

    async def send_command(self, command: str):
        """Send command to the process."""
        await self.input_queue.put(f"{command}\r\n")

    def stop(self):
        """Stop the process."""
        if self.process and self.process.returncode is None:
            try:
                self.process.terminate()
            except Exception as e:
                logger.error(f"Error terminating process: {e}")

# Agent configuration
AGENTS = {
    'acli': {
        'name': 'Atlassian CLI',
        'command': 'acli',
        'description': 'Atlassian command-line interface',
        'color': 'green',
    },
    'adk-python': {
        'name': 'Adk Python',
        'command': str(Path.home() / 'adk-python' / '.venv' / 'bin' / 'adk'),
        'description': 'Agent Development Kit Python',
        'color': 'blue',
    },
    'copilot-cli': {
        'name': 'Copilot CLI',
        'command': 'copilot',
        'description': 'GitHub Copilot CLI',
        'color': 'yellow',
    },
    'kiro-cli': {
        'name': 'Kiro CLI',
        'command': str(Path.home() / '.local' / 'bin' / 'kiro-cli'),
        'description': 'Main Kiro CLI agent',
        'color': 'cyan',
    },
    'qodercli': {
        'name': 'Qoder CLI',
        'command': 'qodercli --dangerously-skip-permissions',
        'description': 'Qoder CLI for code operations',
        'color': 'magenta',
    },
}


class AgentSelector(Static):
    """Widget for selecting and managing agents."""

    def compose(self) -> ComposeResult:
        """Compose the agent selector."""
        yield Label("🤖 Agents", classes="section-title")
        
        options = []
        for agent_id, agent_info in AGENTS.items():
            status = "○"  # Not running
            options.append(
                Option(f"{status} {agent_info['name']}", id=agent_id)
            )
        
        yield OptionList(*options, id="agent-list")
        
        yield Label("", id="agent-description")


class StatusPanel(Static):
    """Widget for displaying agent status and metrics."""

    cpu_usage = reactive("0%")
    memory_usage = reactive("0 MB")
    uptime = reactive("00:00:00")
    command_count = reactive(0)

    def compose(self) -> ComposeResult:
        """Compose the status panel."""
        yield Label("📊 Status", classes="section-title")
        yield Label(f"CPU: {self.cpu_usage}", id="cpu-label")
        yield Label(f"Memory: {self.memory_usage}", id="mem-label")
        yield Label(f"Uptime: {self.uptime}", id="uptime-label")
        yield Label(f"Commands: {self.command_count}", id="cmd-count-label")

    def watch_cpu_usage(self, value: str) -> None:
        """Update CPU display."""
        if self.is_mounted:
            try:
                self.query_one("#cpu-label").update(f"CPU: {value}")
            except Exception:
                pass

    def watch_memory_usage(self, value: str) -> None:
        """Update memory display."""
        if self.is_mounted:
            try:
                self.query_one("#mem-label").update(f"Memory: {value}")
            except Exception:
                pass

    def watch_uptime(self, value: str) -> None:
        """Update uptime display."""
        if self.is_mounted:
            try:
                self.query_one("#uptime-label").update(f"Uptime: {value}")
            except Exception:
                pass

    def watch_command_count(self, value: int) -> None:
        """Update command count display."""
        if self.is_mounted:
            try:
                self.query_one("#cmd-count-label").update(f"Commands: {value}")
            except Exception:
                pass


class DirectoryPickerScreen(ModalScreen[str]):
    """Modal screen for selecting a directory."""

    BINDINGS = [
        ("escape", "dismiss_picker", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the directory picker dialog."""
        yield Label("📁 Select Workspace Directory")
        yield DirectoryTree(str(Path.home()), id="directory-tree")
        yield Button("Select", id="picker-select", variant="primary")
        yield Button("Cancel", id="picker-cancel")

    def on_mount(self) -> None:
        """Focus the tree when mounted."""
        self.query_one(DirectoryTree).focus()

    @on(Button.Pressed, "#picker-select")
    def select_directory(self) -> None:
        """Select the currently highlighted directory."""
        tree = self.query_one(DirectoryTree)
        if tree.cursor_node:
            selected_path = str(tree.cursor_node.data.path)
            self.dismiss(selected_path)
        else:
            self.dismiss(str(Path.home()))

    @on(Button.Pressed, "#picker-cancel")
    def cancel_picker(self) -> None:
        """Cancel directory selection."""
        self.dismiss(None)

    def action_dismiss_picker(self) -> None:
        """Dismiss the picker with Escape key."""
        self.dismiss(None)

    @on(DirectoryTree.DirectorySelected)
    def directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Handle double-click on directory."""
        self.dismiss(str(event.path))


class WorkflowTab(Static):
    """Widget for workflow automation interface."""

    workflow_status = reactive("Ready")
    current_step = reactive(0)
    change_id = reactive("")

    def compose(self) -> ComposeResult:
        """Compose the workflow interface."""
        with VerticalScroll():
            yield Label("🔄 Workflow Automation", classes="section-title")
            
            # Proposal method selector
            yield Label("Proposal Method:", classes="workflow-label")
            with RadioSet(id="proposal-method"):
                yield RadioButton("Simple", id="method-simple", value=True)
                yield RadioButton("Multi-delta-specs", id="method-multi-delta")
            
            # Action selector
            yield Label("Action:", classes="workflow-label")
            with RadioSet(id="workflow-action"):
                yield RadioButton("Propose", id="action-propose", value=True)
                yield RadioButton("Apply", id="action-apply")
                yield RadioButton("Full (Propose+Apply)", id="action-full")
            
            # Configuration inputs
            yield Label("Working Directory:", classes="workflow-label")
            with Horizontal(id="workdir-container"):
                yield Input(value="/home/hfeng1/demo/adk_openspec_project", id="workflow-workdir")
                yield Button("📁", id="browse-workdir", variant="primary")
            
            yield Label("Session Name (optional):", classes="workflow-label")
            yield Input(placeholder="auto-generated", id="workflow-session")
            
            yield Label("Change ID (for Apply):", classes="workflow-label")
            yield Input(placeholder="001-implement-wdt", id="workflow-changeid")
            
            # Action button
            yield Button("🚀 Run Workflow", id="run-workflow", variant="primary")
            
            # Progress tracker
            yield Label("─" * 30, classes="separator")
            yield Label("Workflow Progress:", classes="workflow-label")
            yield Label("⬜ Setup workspace", id="step-setup")
            yield Label("⬜ Run agent", id="step-run")
            yield Label("⬜ Save session", id="step-save")
            yield Label("⬜ Analyze results", id="step-analyze")
            
            # Status display
            yield Label("─" * 30, classes="separator")
            yield Label(f"Status: {self.workflow_status}", id="workflow-status-label")
            yield Label(f"Change ID: {self.change_id or 'None'}", id="workflow-changeid-label")

    def watch_workflow_status(self, value: str) -> None:
        """Update workflow status display."""
        if self.is_mounted:
            try:
                self.query_one("#workflow-status-label").update(f"Status: {value}")
            except Exception:
                pass

    def watch_change_id(self, value: str) -> None:
        """Update change ID display."""
        if self.is_mounted:
            try:
                self.query_one("#workflow-changeid-label").update(f"Change ID: {value or 'None'}")
            except Exception:
                pass

    def update_step(self, step: int, status: str) -> None:
        """Update workflow step status."""
        step_ids = ["#step-setup", "#step-run", "#step-save", "#step-analyze"]
        step_names = ["Setup workspace", "Run agent", "Save session", "Analyze results"]
        
        if 0 <= step < len(step_ids) and self.is_mounted:
            try:
                label = self.query_one(step_ids[step])
                if status == "complete":
                    label.update(f"✅ {step_names[step]}")
                elif status == "running":
                    label.update(f"⏳ {step_names[step]}")
                elif status == "error":
                    label.update(f"❌ {step_names[step]}")
                else:
                    label.update(f"⬜ {step_names[step]}")
            except Exception:
                pass


class ChatInterface(Static):
    """Widget for AI chat interface."""

    def compose(self) -> ComposeResult:
        """Compose the chat interface."""
        yield Label("💬 AI Assistant", classes="section-title")
        yield RichLog(id="chat-history", markup=True, auto_scroll=True)
        with Horizontal(id="chat-input-bar"):
            yield Input(placeholder="Ask AI for help...", id="chat-input")
            yield Button("Send", id="chat-send", variant="primary")

    def add_message(self, role: str, message: str) -> None:
        """Add a message to chat history."""
        chat = self.query_one("#chat-history")
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if role == "user":
            chat.write(f"[bold cyan][{timestamp}] You:[/] {message}")
        elif role == "assistant":
            chat.write(f"[bold green][{timestamp}] AI:[/] {message}")
        elif role == "system":
            chat.write(f"[dim][{timestamp}] System:[/] {message}")


class InteractiveTerminal(RichLog):
    """Interactive terminal widget with proper ANSI terminal emulation using pyte."""

    BINDINGS = [
        ("pageup", "page_up", "Page Up"),
        ("pagedown", "page_down", "Page Down"),
    ]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('markup', False)
        kwargs.setdefault('highlight', False)
        kwargs.setdefault('auto_scroll', True)
        super().__init__(*args, **kwargs)
        self.can_focus = True
        self.master_fd = None
        
        # Initialize pyte terminal emulator
        self.term_screen = pyte.Screen(120, 40)
        self.term_stream = pyte.Stream(self.term_screen)
        
        # Track last rendered content to avoid duplicate rendering
        self._last_content = ""

    def set_master_fd(self, master_fd):
        """Set the PTY master file descriptor for sending input."""
        self.master_fd = master_fd
        # Reset screen when starting new session
        self.term_screen.reset()
        self.clear()
        self._last_content = ""

    def process_output(self, data: str):
        """Process terminal output through pyte emulator."""
        try:
            self.term_stream.feed(data)
            self._update_display()
        except Exception as e:
            logger.error(f"Error processing terminal output: {e}")

    def _update_display(self):
        """Update the RichLog display with current terminal content."""
        lines = []
        
        # Get visible lines from screen
        for y in range(self.term_screen.lines):
            line_chars = []
            for x in range(self.term_screen.columns):
                char = self.term_screen.buffer[y][x]
                # Handle character with attributes
                if hasattr(char, 'data'):
                    line_chars.append(char.data)
                else:
                    line_chars.append(char)
            
            line = ''.join(line_chars).rstrip()
            lines.append(line)
        
        content = '\n'.join(lines)
        
        # Only update if content has changed
        if content != self._last_content:
            self.clear()
            self.write(content)
            self._last_content = content

    def on_key(self, event: Key) -> None:
        """Handle keyboard input and send to PTY."""
        # Let app-level bindings handle these keys first
        if event.key in ['ctrl+c', 'ctrl+d', 'ctrl+q', 'ctrl+t', 'ctrl+h', 'ctrl+p', 'f1', 'f2', 'f3']:
            return  # Don't handle, let it bubble up to app
            
        if not self.master_fd:
            return

        try:
            # Map special keys to terminal control sequences
            key_map = {
                'enter': '\r',
                'backspace': '\x7f',
                'tab': '\t',
                'escape': '\x1b',
                'space': ' ',
                'left': '\x1b[D',
                'right': '\x1b[C',
                'up': '\x1b[A',
                'down': '\x1b[B',
                'home': '\x1b[H',
                'end': '\x1b[F',
                'delete': '\x1b[3~',
                'slash': '/',
                'question_mark': '?',
            }

            # Check if it's a control character
            if event.key.startswith('ctrl+'):
                char = event.key.split('+')[1]
                if len(char) == 1:
                    # Control character: Ctrl+A = \x01, etc.
                    ctrl_char = chr(ord(char.lower()) - ord('a') + 1)
                    os.write(self.master_fd, ctrl_char.encode())
                    event.stop()
                    return
            
            # Map special keys
            if event.key in key_map:
                os.write(self.master_fd, key_map[event.key].encode())
                event.stop()
            elif len(event.key) == 1:
                # Regular character
                os.write(self.master_fd, event.key.encode())
                event.stop()
        except Exception as e:
            logger.error(f"Error sending key to PTY: {e}")


class CLIController(App):
    """Textual TUI for controlling multiple agents with advanced features."""

    TITLE = "CLIController"

    CSS = """
    Screen {
        layout: grid;
        grid-size: 4 3;
        grid-gutter: 1;
    }

    .section-title {
        background: $primary;
        color: $text;
        padding: 0 1;
        text-align: center;
        text-style: bold;
    }

    /* Sidebar - Left column */
    #sidebar {
        column-span: 1;
        row-span: 3;
        background: $surface;
        border: solid $primary;
    }

    AgentSelector {
        height: 60%;
        border-bottom: solid $primary;
    }

    StatusPanel {
        height: 40%;
    }

    #agent-list {
        height: 1fr;
        margin: 1 0;
    }

    #agent-description {
        padding: 0 1;
        margin-top: 1;
        color: $text-muted;
        text-align: center;
    }

    /* Main content - Middle columns */
    #main-content {
        column-span: 2;
        row-span: 3;
        background: $background;
        border: solid $primary;
    }

    #tabs-container {
        height: 1fr;
    }

    #terminal-scroll {
        height: 1fr;
        background: $background;
        border: none;
        padding: 0;
        margin: 0;
    }

    #terminal-output {
        height: auto;
        background: $background;
        color: $text;
        border: none;
        padding: 0;
        margin: 0;
    }

    InteractiveTerminal {
        height: auto;
        background: $background;
        color: $text;
        border: none;
        padding: 0;
        margin: 0;
    }

    /* Chat panel - Right column */
    #chat-panel {
        column-span: 1;
        row-span: 3;
        background: $surface;
        border: solid $primary;
        layout: vertical;
    }

    #chat-tabs {
        height: 100%;
    }

    WorkflowTab {
        height: 100%;
        padding: 1;
    }

    .workflow-label {
        margin-top: 1;
        color: $text-muted;
    }

    .separator {
        color: $text-muted;
        margin: 1 0;
    }

    #proposal-method, #workflow-action {
        margin-bottom: 1;
    }

    #run-workflow {
        margin: 1 0;
        width: 100%;
    }

    #workdir-container {
        height: 3;
        margin-bottom: 1;
    }

    #workdir-container Input {
        width: 1fr;
    }

    #workdir-container Button {
        width: 5;
        min-width: 5;
    }

    #workflow-workdir, #workflow-session, #workflow-changeid {
        margin-bottom: 1;
    }

    #step-setup, #step-run, #step-save, #step-analyze {
        padding: 0 1;
        margin: 0;
    }

    #workflow-status-label, #workflow-changeid-label {
        padding: 0 1;
        margin: 0;
        color: $text-muted;
    }

    ChatInterface {
        height: 1fr;
    }

    #chat-history {
        height: 1fr;
        margin: 1;
        border: solid $primary-lighten-1;
    }

    #chat-input-bar {
        height: 3;
        padding: 0 1;
    }

    #chat-input {
        width: 1fr;
        margin-right: 1;
    }

    #chat-send {
        width: auto;
    }

    #status-bar {
        height: 1;
        background: $primary;
        color: $text;
        text-align: center;
    }

    /* History list styling */
    #history-list {
        height: 1fr;
        margin: 1;
    }

    #history-search {
        margin: 1;
    }

    /* Status panel labels */
    #cpu-label, #mem-label, #uptime-label, #cmd-count-label {
        padding: 0 1;
        margin-top: 1;
    }

    /* Tab styling */
    TabbedContent {
        height: 1fr;
    }

    TabPane {
        height: 1fr;
    }
    """

    BINDINGS = [
        ("ctrl+c", "request_quit", "Quit"),
        ("ctrl+d", "request_quit", "Quit"),
        ("ctrl+q", "request_quit", "Quit"),
        ("ctrl+t", "toggle_chat", "Toggle Chat"),
        ("ctrl+h", "toggle_history", "History"),
        ("f1", "start_agent", "Start"),
        ("f2", "stop_agent", "Stop"),
        ("f3", "switch_theme", "Theme"),
    ]

    # Reactive variables
    agent_running = reactive(False)
    status_message = reactive("Ready - Press F1 to start agent")
    current_agent = reactive("kiro-cli")
    chat_visible = reactive(True)
    theme_mode = reactive("dark")

    def __init__(self):
        super().__init__()
        self.agent_process = None
        self.master_fd = None
        self.start_time = None
        self.command_count = 0
        self.session_data = {
            'commands': [],
            'chat_history': [],
            'start_time': None,
        }
        # Workflow state
        self.workflow_running = False
        self.workflow_mode = "propose-simple"
        self.workflow_change_id = None
        
        # Setup log file
        self.log_file_path = Path.home() / ".cli_controller" / "logs" / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_file = open(self.log_file_path, 'a', encoding='utf-8')
        logger.info(f"Log file initialized: {self.log_file_path}")

    def compose(self) -> ComposeResult:
        """Compose the UI with multi-pane layout."""
        yield Header(show_clock=True)
        
        # Sidebar with agents and status
        with VerticalScroll(id="sidebar"):
            yield AgentSelector()
            yield StatusPanel()
        
        # Main content area with tabs for different agents
        with Container(id="main-content"):
            with TabbedContent(id="tabs-container"):
                with TabPane("Terminal", id="terminal-tab"):
                    with VerticalScroll(id="terminal-scroll"):
                        yield InteractiveTerminal(id="terminal-output")
        
        # Chat panel on the right with tabs
        with Container(id="chat-panel"):
            with TabbedContent(id="chat-tabs"):
                with TabPane("Chat", id="chat-tab"):
                    yield ChatInterface()
                with TabPane("Workflow", id="workflow-tab"):
                    yield WorkflowTab()

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Set kiro-cli as default selected agent
        try:
            agent_list = self.query_one("#agent-list", OptionList)
            agent_list.highlighted = 3  # kiro-cli is 4th in alphabetical order (0-indexed: 3)
        except Exception as e:
            logger.error(f"Error setting default agent: {e}")
        
        # Set Workflow tab as default in right panel
        try:
            chat_tabs = self.query_one("#chat-tabs", TabbedContent)
            chat_tabs.active = "workflow-tab"
        except Exception as e:
            logger.error(f"Error setting default tab: {e}")
        
        # Focus on terminal
        try:
            self.query_one("#terminal-output").focus()
        except Exception:
            pass
        
        self.load_session()
        self.update_metrics()

    def watch_agent_running(self, running: bool) -> None:
        """Update status when agent status changes."""
        if running:
            agent_name = AGENTS[self.current_agent]['name']
            self.status_message = f"{agent_name} Running - Type commands below"
            self.start_time = datetime.now()
        else:
            self.status_message = "Ready - Press F1 to start agent"
            self.start_time = None

    def watch_status_message(self, message: str) -> None:
        """Update footer with status message."""
        # Status shown in footer
        pass

    def watch_chat_visible(self, visible: bool) -> None:
        """Toggle chat panel visibility."""
        if self.is_mounted:
            try:
                chat_panel = self.query_one("#chat-panel")
                chat_panel.display = visible
            except Exception:
                pass

    @on(Button.Pressed, "#chat-send")
    def send_chat_message(self) -> None:
        """Send message to kiro-cli."""
        chat_input = self.query_one("#chat-input")
        message = chat_input.value.strip()
        if message:
            chat_interface = self.query_one(ChatInterface)
            chat_interface.add_message("user", message)
            chat_input.value = ""
            
            # Send to kiro-cli
            self.send_command(message)

    @on(Input.Submitted, "#chat-input")
    def on_chat_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in chat input."""
        message = event.value.strip()
        if message:
            chat_interface = self.query_one(ChatInterface)
            chat_interface.add_message("user", message)
            event.input.value = ""
            # Send to kiro-cli
            self.send_command(message)

    @on(Button.Pressed, "#browse-workdir")
    @work
    async def browse_working_directory(self) -> None:
        """Open directory picker for working directory."""
        current_value = self.query_one("#workflow-workdir", Input).value.strip()
        if not current_value:
            current_value = "."
        
        result = await self.push_screen_wait(DirectoryPickerScreen(current_value))
        if result:
            self.query_one("#workflow-workdir", Input).value = result

    @on(Button.Pressed, "#run-workflow")
    def on_run_workflow_clicked(self) -> None:
        """Handle run workflow button click."""
        if self.workflow_running:
            self.log_output("⚠️ Workflow already running")
            return
        
        # Get workflow configuration
        proposal_set = self.query_one("#proposal-method", RadioSet)
        action_set = self.query_one("#workflow-action", RadioSet)
        workdir = self.query_one("#workflow-workdir", Input).value.strip()
        session_name = self.query_one("#workflow-session", Input).value.strip()
        change_id = self.query_one("#workflow-changeid", Input).value.strip()
        
        # Determine proposal method
        proposal_method = "simple"
        if proposal_set.pressed_button:
            if proposal_set.pressed_button.id == "method-multi-delta":
                proposal_method = "multi-delta"
        
        # Determine action
        action = "propose"
        if action_set.pressed_button:
            action_map = {
                "action-propose": "propose",
                "action-apply": "apply",
                "action-full": "full"
            }
            action = action_map.get(action_set.pressed_button.id, "propose")
        
        # Combine to determine workflow mode
        if action == "apply":
            self.workflow_mode = "apply"
        elif action == "full":
            self.workflow_mode = f"{proposal_method}-full"
        else:  # propose
            self.workflow_mode = f"propose-{proposal_method}"
        
        # Validate inputs
        if not workdir:
            self.log_output("❌ Working directory is required")
            return
        
        if action == "apply" and not change_id:
            self.log_output("❌ Change ID is required for Apply mode")
            return
        
        # Store change ID if provided
        if change_id:
            self.workflow_change_id = change_id
        
        # Start workflow
        self.run_workflow(workdir, session_name, change_id)

    @on(RadioSet.Changed, "#proposal-method")
    def on_proposal_method_changed(self, event: RadioSet.Changed) -> None:
        """Handle proposal method selection change."""
        # Just for logging/debugging if needed
        if event.pressed and event.pressed.id:
            method = "simple" if event.pressed.id == "method-simple" else "multi-delta"
            logger.debug(f"Proposal method changed to: {method}")
    
    @on(RadioSet.Changed, "#workflow-action")
    def on_workflow_action_changed(self, event: RadioSet.Changed) -> None:
        """Handle workflow action selection change."""
        # Just for logging/debugging if needed
        if event.pressed and event.pressed.id:
            action = event.pressed.id.replace("action-", "")
            logger.debug(f"Workflow action changed to: {action}")

    @on(OptionList.OptionSelected, "#agent-list")
    def agent_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle agent selection."""
        agent_id = event.option.id
        if agent_id and agent_id in AGENTS:
            self.current_agent = agent_id
            agent_info = AGENTS[agent_id]
            
            # Update description
            desc_label = self.query_one("#agent-description")
            desc_label.update(agent_info['description'])

    def action_start_agent(self) -> None:
        """Start the selected agent."""
        self.start_agent_process()

    def action_stop_agent(self) -> None:
        """Stop the running agent."""
        self.stop_agent_process()

    def action_toggle_chat(self) -> None:
        """Toggle chat panel visibility."""
        self.chat_visible = not self.chat_visible

    def action_switch_theme(self) -> None:
        """Switch between light and dark themes."""
        if self.theme_mode == "dark":
            self.theme = "textual-light"
            self.theme_mode = "light"
        else:
            self.theme = "textual-dark"
            self.theme_mode = "dark"

    def action_request_quit(self) -> None:
        """Handle quit request - cleanup and exit."""
        self.stop_agent_process()
        self.save_session()
        self.exit()

    def start_agent_process(self) -> None:
        """Start the selected agent process with PTY."""
        if self.agent_running:
            return

        try:
            agent_info = AGENTS[self.current_agent]
            agent_cmd = agent_info['command']
            
            # Verify the command exists
            if not Path(agent_cmd.split()[0]).exists():
                # Try which command
                result = subprocess.run(
                    ['which', agent_cmd.split()[0]],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    self.log_output(f"ERROR: {agent_cmd} not found")
                    return
                agent_cmd = result.stdout.strip()

            # Create PTY with proper size
            self.master_fd, slave_fd = pty.openpty()
            
            # Set terminal size
            rows, cols = 40, 120
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

            # Start agent process
            self.agent_process = subprocess.Popen(
                agent_cmd.split(),
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                cwd=str(Path.cwd()),
                preexec_fn=os.setsid,
                env=dict(os.environ, TERM='xterm-256color')
            )
            
            os.close(slave_fd)
            self.agent_running = True
            self.command_count = 0
            
            self.log_output(f"Started {agent_info['name']}")
            
            # Set master_fd in terminal widget for input
            terminal = self.query_one("#terminal-output", InteractiveTerminal)
            terminal.set_master_fd(self.master_fd)
            terminal.focus()
            
            # Update agent list
            self.update_agent_status()
            
            # Start reading output
            self.read_output()
            
            # Save session
            self.session_data['start_time'] = datetime.now().isoformat()
            self.save_session()
            
        except Exception as e:
            self.log_output(f"ERROR: Failed to start agent: {e}")
            if self.master_fd:
                os.close(self.master_fd)
                self.master_fd = None

    async def start_agent_in_workdir(self, workdir: str) -> None:
        """Start agent process in a specific working directory."""
        if self.agent_running:
            self.log_output("Agent already running")
            return

        if self.current_agent not in AGENTS:
            self.log_output(f"ERROR: Unknown agent: {self.current_agent}")
            return

        try:
            agent_info = AGENTS[self.current_agent]
            agent_cmd = agent_info['command']
            
            # Verify agent command exists
            if not Path(agent_cmd.split()[0]).exists():
                # Try which command
                result = subprocess.run(
                    ['which', agent_cmd.split()[0]],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    self.log_output(f"ERROR: {agent_cmd} not found")
                    return
                agent_cmd = result.stdout.strip()

            # Create PTY with proper size
            self.master_fd, slave_fd = pty.openpty()
            
            # Set terminal size
            rows, cols = 40, 120
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

            # Start agent process in the specified working directory
            self.agent_process = subprocess.Popen(
                agent_cmd.split(),
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                cwd=workdir,  # Start in the specified directory
                preexec_fn=os.setsid,
                env=dict(os.environ, TERM='xterm-256color')
            )
            
            os.close(slave_fd)
            self.agent_running = True
            self.command_count = 0
            
            self.log_output(f"Started {agent_info['name']} in {workdir}")
            
            # Set master_fd in terminal widget for input
            terminal = self.query_one("#terminal-output", InteractiveTerminal)
            terminal.set_master_fd(self.master_fd)
            terminal.focus()
            
            # Update agent list
            self.update_agent_status()
            
            # Start reading output
            self.read_output()
            
            # Save session
            self.session_data['start_time'] = datetime.now().isoformat()
            self.save_session()
            
        except Exception as e:
            self.log_output(f"ERROR: Failed to start agent: {e}")
            if self.master_fd:
                os.close(self.master_fd)
                self.master_fd = None

    def stop_agent_process(self) -> None:
        """Stop the running agent process."""
        if not self.agent_running:
            return

        try:
            if self.agent_process:
                # Send quit command
                self.send_command("quit", log=False)
                time.sleep(0.5)
                
                # Terminate process
                self.agent_process.terminate()
                try:
                    self.agent_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.agent_process.kill()
                    self.agent_process.wait()

            if self.master_fd:
                os.close(self.master_fd)
                self.master_fd = None

            self.agent_running = False
            
            agent_info = AGENTS[self.current_agent]
            self.log_output(f"{agent_info['name']} stopped")
            
            # Clear master_fd from terminal widget
            try:
                terminal = self.query_one("#terminal-output", InteractiveTerminal)
                terminal.set_master_fd(None)
            except Exception:
                pass
            
            # Update agent list
            self.update_agent_status()
            
            # Save session
            self.save_session()

        except Exception as e:
            self.log_output(f"ERROR: {e}")

    def update_agent_status(self) -> None:
        """Update agent list with current status."""
        if not self.is_mounted:
            return
            
        try:
            agent_list = self.query_one("#agent-list")
            agent_list.clear_options()
            
            for agent_id, agent_info in AGENTS.items():
                if agent_id == self.current_agent and self.agent_running:
                    status = "●"  # Running
                else:
                    status = "○"  # Not running
                
                agent_list.add_option(
                    Option(f"{status} {agent_info['name']}", id=agent_id)
                )
        except Exception as e:
            logger.error(f"Error updating agent status: {e}")

    async def wait_for_prompt(self, timeout: float = 10.0) -> bool:
        """Wait for the '>' prompt to appear in the terminal.
        
        Returns:
            True if prompt found, False if timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                terminal = self.query_one("#terminal-output", InteractiveTerminal)
                # Get the current terminal screen content
                for y in range(terminal.term_screen.lines):
                    line_chars = []
                    for x in range(terminal.term_screen.columns):
                        char = terminal.term_screen.buffer[y][x]
                        if hasattr(char, 'data'):
                            line_chars.append(char.data)
                        else:
                            line_chars.append(char)
                    line = ''.join(line_chars).strip()
                    # Check if line starts with '>'
                    if line.startswith('>'):
                        self.log_output("✅ Prompt detected, ready for input")
                        return True
                
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.error(f"Error waiting for prompt: {e}")
                await asyncio.sleep(0.2)
        
        self.log_output("⚠️ Timeout waiting for prompt")
        return False

    def send_command(self, command: str, log: bool = True) -> None:
        """Send command to agent."""
        if not self.agent_running or not self.master_fd:
            self.log_output("ERROR: Agent is not running")
            return

        try:
            os.write(self.master_fd, f"{command}\r\n".encode('utf-8'))
            
            if log:
                self.command_count += 1
                
                # Update command count in status panel
                status_panel = self.query_one(StatusPanel)
                status_panel.command_count = self.command_count
                
                # Save to session
                self.session_data['commands'].append({
                    'command': command,
                    'timestamp': datetime.now().isoformat(),
                })
                
        except Exception as e:
            self.log_output(f"ERROR: Failed to send command: {e}")

    @work(exclusive=True)
    async def run_workflow(self, workdir: str, session_name: str, change_id: str) -> None:
        """Execute workflow automation."""
        self.workflow_running = True
        workflow_tab = self.query_one(WorkflowTab)
        workflow_tab.workflow_status = "Running"
        
        try:
            # Resolve working directory
            if not workdir.startswith('/'):
                workdir = str(Path.cwd() / workdir)
            
            workdir_path = Path(workdir)
            if not workdir_path.exists():
                self.log_output(f"❌ Working directory not found: {workdir}")
                workflow_tab.workflow_status = "Error"
                return
            
            # Generate session name if not provided
            if not session_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if self.workflow_mode.startswith("propose"):
                    session_name = f"kiro-propose-session_{timestamp}.json"
                else:
                    session_name = f"kiro-apply-session_{timestamp}.json"
            
            self.log_output("="*50)
            self.log_output(f"🚀 Starting Workflow: {self.workflow_mode}")
            self.log_output(f"Working Directory: {workdir}")
            self.log_output(f"Session Name: {session_name}")
            if change_id:
                self.log_output(f"Change ID: {change_id}")
            self.log_output("="*50)
            
            # Step 1: Setup workspace
            workflow_tab.update_step(0, "running")
            await self.workflow_setup_workspace(workdir_path, self.workflow_mode)
            workflow_tab.update_step(0, "complete")
            
            # Step 2: Start kiro-cli if not running
            if not self.agent_running:
                self.log_output("🚀 Starting kiro-cli in chat mode...")
                self.current_agent = 'kiro-cli'
                
                # Start in the working directory
                await self.start_agent_in_workdir(workdir)
                
                # Wait for the '>' prompt to appear
                self.log_output("⏳ Waiting for kiro-cli to be ready...")
                await self.wait_for_prompt(timeout=15.0)
            
            # Step 3: Send prompt through chat interface
            workflow_tab.update_step(1, "running")
            await self.workflow_run_agent(workdir_path, session_name, change_id)
            
            # User needs to wait for agent to complete before proceeding
            self.log_output("⏳ Waiting for agent to complete...")
            self.log_output("   Watch the terminal for progress...")
            self.log_output("   You can manually save the session later with /chat save")
            
            workflow_tab.update_step(1, "complete")
            
            # Note: Removed automatic session save - user will do it manually
            # The user can save with: /chat save {session_dir}/{session_name}
            # and then analyze manually if needed
            
            workflow_tab.update_step(2, "complete")
            workflow_tab.update_step(3, "complete")
            
            workflow_tab.workflow_status = "Complete"
            self.log_output("✅ Workflow completed successfully")
            
            # If this was propose mode, show the change ID
            if self.workflow_change_id:
                workflow_tab.change_id = self.workflow_change_id
                self.log_output(f"\n📋 Change ID captured: {self.workflow_change_id}")
            
        except Exception as e:
            workflow_tab.workflow_status = "Error"
            self.log_output(f"❌ Workflow error: {e}")
            logger.error(f"Workflow error: {e}", exc_info=True)
        finally:
            self.workflow_running = False

    async def workflow_setup_workspace(self, workdir: Path, mode: str) -> None:
        """Setup workspace for workflow."""
        self.log_output("⚙️  Setting up workspace...")
        
        # Create openspec-memories symlink if needed for propose mode
        if mode.startswith("propose"):
            memories_link = workdir / "openspec-memories"
            if not memories_link.exists():
                # Look for memories in parent directory
                repo_memories = workdir.parent / "openspec-memories"
                if repo_memories.exists():
                    memories_link.symlink_to(repo_memories)
                    self.log_output(f"✅ Created symlink: {memories_link} -> {repo_memories}")
                else:
                    self.log_output(f"⚠️  openspec-memories not found, skipping symlink creation")
        
        # Check/copy MCP config for apply mode
        if mode in ["apply", "full"]:
            mcp_config = workdir / ".kiro" / "settings" / "mcp.json"
            if not mcp_config.exists():
                repo_mcp = workdir.parent / ".kiro" / "settings" / "mcp.json"
                if repo_mcp.exists():
                    mcp_config.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy(repo_mcp, mcp_config)
                    self.log_output(f"✅ Copied MCP config: {mcp_config}")
        
        self.log_output("✅ Workspace setup complete")

    async def workflow_run_agent(self, workdir: Path, session_name: str, change_id: str) -> None:
        """Run agent with appropriate prompt based on workflow mode."""
        self.log_output("🤖 Sending prompt to kiro-cli...")
        
        # Construct prompt based on mode
        if self.workflow_mode == "propose-simple":
            prompt = "Read powers/openspec-propose/POWER.md and create a new OpenSpec change by following the instructions in POWER.md"
        elif self.workflow_mode == "propose-multi-delta":
            prompt = "Read powers/openspec-propose-multiple-spec-deltas/POWER.md and create a new OpenSpec change by following the instructions in POWER.md"
        elif self.workflow_mode == "apply":
            prompt = f"Read powers/openspec-apply/POWER.md and apply change {change_id} by following the instructions in POWER.md"
        elif self.workflow_mode == "simple-full":
            prompt = "Read powers/openspec-propose/POWER.md and create a new OpenSpec change by following the instructions in POWER.md"
        elif self.workflow_mode == "multi-delta-full":
            prompt = "Read powers/openspec-propose-multiple-spec-deltas/POWER.md and create a new OpenSpec change by following the instructions in POWER.md"
        else:
            prompt = "Read powers/openspec-propose/POWER.md and create a new OpenSpec change by following the instructions in POWER.md"
        
        # Display prompt in chat window
        chat_interface = self.query_one(ChatInterface)
        chat_interface.add_message("user", prompt)
        
        # Send prompt to kiro-cli
        self.send_command(prompt)
        
        # Give a moment for the command to be processed
        await asyncio.sleep(0.5)
        
        self.log_output("✅ Prompt sent, waiting for agent to complete...")
        self.log_output("⏳ Agent is working... (this may take several minutes)")
        
        # Note: The user will need to monitor progress in the terminal
        # and manually proceed when the agent is done

    async def workflow_analyze_session(self, workdir: Path, session_name: str) -> None:
        """Analyze the workflow session."""
        self.log_output("📊 Analyzing session...")
        
        # Determine session directory based on mode
        if self.workflow_mode.startswith("propose"):
            session_dir = workdir / "kiro-propose"
        else:
            session_dir = workdir / "kiro-apply"
        
        session_file = session_dir / session_name
        
        if not session_file.exists():
            self.log_output(f"⚠️  Session file not found: {session_file}")
            return
        
        # Create analysis file
        analysis_file = session_file.with_suffix('.txt')
        
        try:
            # Run view_kiro_session.py
            view_script = workdir.parent / "view_kiro_session.py"
            if not view_script.exists():
                self.log_output(f"⚠️  view_kiro_session.py not found: {view_script}")
                return
            
            result = subprocess.run(
                [sys.executable, str(view_script), str(session_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                analysis_file.write_text(result.stdout)
                self.log_output(f"✅ Analysis saved: {analysis_file}")
                
                # Extract key metrics
                if "Conversation Turns:" in result.stdout:
                    for line in result.stdout.split('\n'):
                        if "Conversation Turns:" in line or "Total Time:" in line:
                            self.log_output(f"  {line.strip()}")
                
                # Try to extract change ID from analysis for propose mode
                if self.workflow_mode.startswith("propose") or self.workflow_mode == "full":
                    for line in result.stdout.split('\n'):
                        if "change" in line.lower() and "-" in line:
                            # Simple heuristic to find change IDs like "001-implement-wdt"
                            import re
                            match = re.search(r'\b(\d{3}-[a-z-]+)\b', line)
                            if match:
                                self.workflow_change_id = match.group(1)
                                workflow_tab = self.query_one(WorkflowTab)
                                workflow_tab.change_id = self.workflow_change_id
                                break
            else:
                self.log_output(f"⚠️  Analysis failed: {result.stderr}")
        
        except Exception as e:
            self.log_output(f"⚠️  Analysis error: {e}")
        
        self.log_output("✅ Analysis complete")

    def simulate_ai_response(self, user_message: str) -> None:
        """Simulate AI response (placeholder for real AI integration)."""
        chat = self.query_one(ChatInterface)
        
        # Simple rule-based responses for now
        message_lower = user_message.lower()
        
        if "help" in message_lower:
            response = (
                "I can help you with:\n"
                "• Starting/stopping agents (F1/F2)\n"
                "• Running commands in agents\n"
                "• Switching between agents\n"
                "• Theme switching (F3)"
            )
        elif "error" in message_lower or "problem" in message_lower:
            response = (
                "I can see you're experiencing an issue. "
                "Try checking:\n"
                "1. Is the agent running? (press F1)\n"
                "2. Check the terminal output for errors"
            )
        elif "command" in message_lower:
            response = (
                "You can send commands using:\n"
                "• Type directly in the terminal\n"
                "• Press Enter to send"
            )
        else:
            response = (
                "I'm here to help! Ask me about:\n"
                "• How to use the interface\n"
                "• Troubleshooting agent issues\n"
                "• Available commands and shortcuts"
            )
        
        chat.add_message("assistant", response)
        
        # Save to session
        self.session_data['chat_history'].append({
            'user': user_message,
            'assistant': response,
            'timestamp': datetime.now().isoformat(),
        })

    @work(exclusive=False, thread=True)
    def update_metrics(self) -> None:
        """Update system metrics periodically."""
        import psutil
        
        status_panel = None
        if self.is_mounted:
            try:
                status_panel = self.query_one(StatusPanel)
            except Exception:
                pass
        
        while True:
            if not self.is_mounted:
                break
                
            try:
                # CPU usage
                cpu = psutil.cpu_percent(interval=1)
                if status_panel:
                    status_panel.cpu_usage = f"{cpu:.1f}%"
                
                # Memory usage
                if self.agent_process:
                    try:
                        process = psutil.Process(self.agent_process.pid)
                        mem = process.memory_info().rss / 1024 / 1024  # MB
                        if status_panel:
                            status_panel.memory_usage = f"{mem:.1f} MB"
                    except (psutil.NoSuchProcess, AttributeError):
                        pass
                
                # Uptime
                if self.start_time:
                    uptime = datetime.now() - self.start_time
                    hours = int(uptime.total_seconds() // 3600)
                    minutes = int((uptime.total_seconds() % 3600) // 60)
                    seconds = int(uptime.total_seconds() % 60)
                    if status_panel:
                        status_panel.uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
            
            time.sleep(1)

    def load_session(self) -> None:
        """Load session data from file."""
        session_file = Path.home() / ".kiro_cli_session.json"
        try:
            if session_file.exists():
                with open(session_file, 'r') as f:
                    self.session_data = json.load(f)
                logger.info("Session loaded")
        except Exception as e:
            logger.error(f"Error loading session: {e}")

    def save_session(self) -> None:
        """Save session data to file."""
        session_file = Path.home() / ".kiro_cli_session.json"
        try:
            with open(session_file, 'w') as f:
                json.dump(self.session_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving session: {e}")

    def log_output(self, text: str) -> None:
        """Write text to log file only."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_file.write(f"[{timestamp}] {text}\n")
            self.log_file.flush()
        except Exception as e:
            logger.error(f"Failed to write to log file: {e}")

    @work(exclusive=True)
    async def read_output(self) -> None:
        """Read output from agent process."""
        terminal = self.query_one("#terminal-output", InteractiveTerminal)
        
        while self.agent_running and self.master_fd:
            try:
                # Check if data is available
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                
                if ready:
                    data = os.read(self.master_fd, 4096).decode('utf-8', errors='ignore')
                    if data:
                        # Process through pyte terminal emulator
                        terminal.process_output(data)
                
                # Check if process is still alive
                if self.agent_process and self.agent_process.poll() is not None:
                    self.agent_running = False
                    terminal.process_output("\n[Process ended]\n")
                    self.update_agent_status()
                    break
                    
                await asyncio.sleep(0.05)
                
            except OSError:
                break
            except Exception as e:
                logger.error(f"Error reading output: {e}")
                break

    def on_unmount(self) -> None:
        """Cleanup when app is closed."""
        self.stop_agent_process()
        self.save_session()
        
        # Close log file
        try:
            if hasattr(self, 'log_file') and self.log_file:
                self.log_file.close()
                logger.info(f"Log file closed: {self.log_file_path}")
        except Exception as e:
            logger.error(f"Error closing log file: {e}")


def main():
    """Run the CLI TUI application."""
    app = CLIController()
    app.run()


if __name__ == "__main__":
    main()