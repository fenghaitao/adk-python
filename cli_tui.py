#!/usr/bin/env python3
"""
Textual TUI application to control multiple CLI agents.

This provides a clean terminal interface for interacting with various CLI
agents (kiro-cli, adk, qodercli, etc.), displaying their output and enabling
interactive control through a multi-pane layout.

Architecture:
- CLIController: Main Textual application managing agent lifecycle
- InteractiveTerminal: Terminal emulation widget using pyte
- AgentSelector: Widget for selecting and switching between agents
- StatusPanel: Real-time metrics display
- WorkflowTab: Automated workflow execution interface
- ChatTab: AI assistant integration

Features:
- Multi-agent support with easy switching
- PTY-based process management for proper terminal emulation
- Workflow automation for propose/apply operations
- Session management and history
- Integrated chat interface
"""

from __future__ import annotations

import asyncio
import fcntl
import json
import logging
import os
import pty
import pyte
import re
import select
import shutil
import signal
import struct
import subprocess
import sys
import termios
import time
from datetime import datetime
from pathlib import Path

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

# Setup logging - redirect to file to avoid interfering with TUI
log_dir = Path.home() / ".cli_controller" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"cli_tui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=str(log_file),
    filemode='a'
)
logger = logging.getLogger(__name__)
logger.info(f"Logging initialized: {log_file}")


# Agent configuration
AGENTS = {
    'acli': {
        'name': 'Atlassian CLI',
        'command': str(Path.home() / 'acli') + ' rovodev run --yolo',
        'description': 'Atlassian command-line interface',
        'color': 'green',
    },
    'adk-python': {
        'name': 'Adk Python',
        'command': str(Path(__file__).parent / '.venv' / 'bin' / 'adk'),
        'description': 'Agent Development Kit Python (OpenSpec workflow)',
        'color': 'blue',
    },
    'copilot-cli': {
        'name': 'Copilot CLI',
        'command': 'copilot',
        'description': 'GitHub Copilot CLI',
        'color': 'yellow',
    },
    'dspy-openspec': {
        'name': 'DSPy OpenSpec',
        'command': str(Path(__file__).parent / '.venv' / 'bin' / 'dspy-openspec') + ' --model iflow/qwen3-coder-plus --verbose',
        'description': 'DSPy-based OpenSpec agent',
        'color': 'purple',
    },
    'kiro-cli': {
        'name': 'Kiro CLI',
        'command': str(Path.home() / '.local' / 'bin' / 'kiro-cli') + ' chat --trust-all-tools',
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

# ADK environment configuration (from common-config.sh)
ADK_ENV_CONFIG = {
    'CONTEXT_ENABLE_CONDENSATION': 'true',
    'CONTEXT_MAX_TOKENS': '200000',
    'CONTEXT_KEEP_SYSTEM_MESSAGES': '2',
    'CONTEXT_KEEP_RECENT_TURNS': '3',
    'CONTEXT_SUMMARIZATION_MODEL': 'iflow/qwen3-coder-plus',
    'CONTEXT_SUMMARY_PROMPT_TYPE': 'vscode',
    'BUILTIN_MCP_SERVER': 'no',
    'OPENSPEC_MODEL': 'iflow/qwen3-coder-plus',
}

# ADK samples directory for agent imports
ADK_SAMPLES_DIR = Path(__file__).parent / 'contributing' / 'samples'


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
                yield Input(value="/tmp/hfeng1/demo/adk_openspec_project", id="workflow-workdir")
                yield Button("📁", id="browse-workdir", variant="primary")
            
            # Proposal file/text input (for ADK)
            yield Label("Proposal (file path or text):", classes="workflow-label")
            yield Input(value="openspec-prompts/proposal-wdt.md", id="workflow-proposal")
            
            # Device hint (for ADK)
            yield Label("Device Hint (optional):", classes="workflow-label")
            yield Input(placeholder="wdt", id="workflow-device-hint")
            
            yield Label("Session Name (optional):", classes="workflow-label")
            yield Input(placeholder="auto-generated", id="workflow-session")
            
            yield Label("Change ID (for Apply):", classes="workflow-label")
            yield Input(placeholder="001-implement-wdt", id="workflow-changeid")
            
            # MCP Port (for ADK)
            yield Label("MCP Port (for ADK):", classes="workflow-label")
            yield Input(value="8051", id="workflow-mcp-port")
            
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


class ChatTab(Static):
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
        
        # Initialize pyte terminal emulator with history buffer
        # HistoryScreen maintains a scrollback buffer (default 1000 lines)
        self.term_screen = pyte.HistoryScreen(120, 40, history=5000)
        self.term_stream = pyte.Stream(self.term_screen)
        
        # Track last rendered content to avoid duplicate rendering
        self._last_content = ""
        self._last_update_time = 0.0
        self._update_throttle = 0.05  # Minimum 50ms between updates

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
        """Update the RichLog display with current terminal content including history."""
        # Throttle updates to reduce flickering
        current_time = time.time()
        if current_time - self._last_update_time < self._update_throttle:
            return
        
        lines = []
        
        # Get history lines (scrollback buffer)
        # history.top is a deque of lines, each line is a dict mapping column -> char
        for line_dict in self.term_screen.history.top:
            line_chars = []
            # line_dict is a dictionary with column indices as keys
            for col in range(self.term_screen.columns):
                if col in line_dict:
                    char = line_dict[col]
                    if hasattr(char, 'data'):
                        line_chars.append(str(char.data))
                    else:
                        line_chars.append(str(char))
                else:
                    line_chars.append(' ')
            lines.append(''.join(line_chars).rstrip())
        
        # Get visible lines from current screen
        for y in range(self.term_screen.lines):
            line_chars = []
            for x in range(self.term_screen.columns):
                char = self.term_screen.buffer[y][x]
                # Handle character with attributes
                if hasattr(char, 'data'):
                    line_chars.append(str(char.data))
                else:
                    line_chars.append(str(char))
            
            line = ''.join(line_chars).rstrip()
            lines.append(line)
        
        content = '\n'.join(lines)
        
        # Only update if content has changed
        if content != self._last_content:
            # Check if we can just append (content starts with old content)
            if self._last_content and content.startswith(self._last_content):
                # Just append the new part
                new_content = content[len(self._last_content):]
                if new_content:
                    self.write(new_content)
            else:
                # Full refresh needed - clear and rewrite
                self.clear()
                self.write(content)
            
            self._last_content = content
            self._last_update_time = current_time

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

    #workflow-workdir, #workflow-session, #workflow-changeid, #workflow-proposal, #workflow-device-hint, #workflow-mcp-port {
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

    ChatTab {
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
                    yield ChatTab()
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
            chat_tab = self.query_one(ChatTab)
            chat_tab.add_message("user", message)
            chat_input.value = ""
            
            # Send to kiro-cli
            self.send_command(message)

    @on(Input.Submitted, "#chat-input")
    def on_chat_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in chat input."""
        message = event.value.strip()
        if message:
            chat_tab = self.query_one(ChatTab)
            chat_tab.add_message("user", message)
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
        proposal_input = self.query_one("#workflow-proposal", Input).value.strip()
        device_hint = self.query_one("#workflow-device-hint", Input).value.strip()
        session_name = self.query_one("#workflow-session", Input).value.strip()
        change_id = self.query_one("#workflow-changeid", Input).value.strip()
        mcp_port = self.query_one("#workflow-mcp-port", Input).value.strip()
        
        # Use the currently selected agent from the agent panel
        workflow_agent = self.current_agent
        
        # ADK agent type is always "initial"
        adk_agent_type = "initial"
        
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
        
        # For ADK propose/full mode, proposal is required
        if workflow_agent == 'adk-python' and action != "apply" and not proposal_input:
            self.log_output("❌ Proposal is required for ADK Propose mode")
            return
        
        # Store change ID if provided
        if change_id:
            self.workflow_change_id = change_id
        
        # Build ADK-specific config
        adk_config = {
            'agent_type': adk_agent_type,
            'proposal': proposal_input,
            'device_hint': device_hint,
            'mcp_port': mcp_port or '8051',
        }
        
        # Start workflow
        self.run_workflow(workdir, session_name, change_id, workflow_agent, adk_config)

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

    def start_agent_in_workdir(self, workdir: str, extra_args: list = None) -> None:
        """Start agent process in a specific working directory.
        
        Args:
            workdir: Working directory path
            extra_args: Additional command-line arguments for the agent
        """
        if self.agent_running:
            self.log_output("Agent already running")
            return

        if self.current_agent not in AGENTS:
            self.log_output(f"ERROR: Unknown agent: {self.current_agent}")
            return

        try:
            agent_info = AGENTS[self.current_agent]
            agent_cmd = agent_info['command']
            
            # Build full command with extra args
            cmd_parts = agent_cmd.split()
            
            # Special handling for qodercli: add -w flag for working directory
            if self.current_agent == 'qodercli':
                cmd_parts.extend(['-w', workdir])
            
            if extra_args:
                cmd_parts.extend(extra_args)
            
            # Verify agent command exists
            if not Path(cmd_parts[0]).exists():
                # Try which command
                result = subprocess.run(
                    ['which', cmd_parts[0]],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    self.log_output(f"ERROR: {cmd_parts[0]} not found")
                    return
                cmd_parts[0] = result.stdout.strip()

            # Create PTY with proper size
            self.master_fd, slave_fd = pty.openpty()
            
            # Set terminal size
            rows, cols = 40, 120
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

            # Start agent process in the specified working directory
            self.log_output(f"🔧 Starting process in directory: {workdir}")
            self.log_output(f"🔧 Command: {' '.join(cmd_parts)}")
            
            self.agent_process = subprocess.Popen(
                cmd_parts,
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
                # Send appropriate quit command based on agent
                # DSPy OpenSpec is non-interactive, so just terminate
                if self.current_agent == 'dspy-openspec':
                    pass  # No quit command needed for non-interactive agents
                elif self.current_agent in ['kiro-cli', 'qodercli']:
                    self.send_command("/quit", log=False)
                else:
                    self.send_command("/exit", log=False)
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
        """Wait for the prompt to appear as the last line in the terminal.
        
        Different agents use different prompts:
        - kiro-cli: '!>'
        - acli/rovodev: '> ' (may appear as '| > ')
        
        Args:
            timeout: Maximum time to wait in seconds
        
        Returns:
            True if prompt found, False if timeout
        """
        start_time = asyncio.get_event_loop().time()
        terminal = self.query_one("#terminal-output", InteractiveTerminal)
        
        # Wait for the prompt to appear as the last line
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                # Get the current terminal screen content
                lines = []
                for y in range(terminal.term_screen.lines):
                    line_chars = []
                    for x in range(terminal.term_screen.columns):
                        char = terminal.term_screen.buffer[y][x]
                        if hasattr(char, 'data'):
                            line_chars.append(char.data)
                        else:
                            line_chars.append(char)
                    line = ''.join(line_chars).strip()
                    if line:  # Only add non-empty lines
                        lines.append(line)
                
                # Check if the last non-empty line contains a prompt
                if lines:
                    last_line = lines[-1]
                    # Check for various prompt patterns
                    if (last_line == '!>' or  # kiro-cli
                        last_line.endswith('> ') or  # acli/rovodev
                        '| > ' in last_line):  # acli/rovodev with pipe
                        self.log_output("✅ Prompt detected, ready for input")
                        return True
                
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.error(f"Error waiting for prompt: {e}")
                await asyncio.sleep(0.2)
        
        self.log_output("⚠️ Timeout waiting for prompt")
        return False

    async def extract_change_id_from_terminal(self) -> str:
        """Extract change ID from terminal output (for acli/rovodev).
        
        Looks for patterns like:
        - "Change ID: 001-implement-wdt"
        - "change-id: 001-implement-wdt"
        - Lines containing change IDs in format: NNN-description
        
        Returns:
            Change ID string or empty string if not found
        """
        try:
            terminal = self.query_one("#terminal-output", InteractiveTerminal)
            
            # Search through terminal history for change ID
            # Look at the last 100 lines
            lines_to_check = min(100, terminal.term_screen.lines)
            
            for y in range(terminal.term_screen.lines - lines_to_check, terminal.term_screen.lines):
                if y < 0:
                    continue
                    
                line_chars = []
                for x in range(terminal.term_screen.columns):
                    char = terminal.term_screen.buffer[y][x]
                    if hasattr(char, 'data'):
                        line_chars.append(char.data)
                    else:
                        line_chars.append(char)
                line = ''.join(line_chars).strip()
                
                # Look for change ID patterns
                # Pattern 1: "Change ID: 001-implement-wdt"
                if "change" in line.lower() and "id" in line.lower():
                    import re
                    match = re.search(r'\b(\d{3}-[a-z0-9-]+)\b', line, re.IGNORECASE)
                    if match:
                        return match.group(1)
                
                # Pattern 2: Just a line with the change ID format
                import re
                match = re.search(r'\b(\d{3}-[a-z0-9-]+)\b', line, re.IGNORECASE)
                if match:
                    # Verify it looks like a real change ID (has at least one dash after the number)
                    candidate = match.group(1)
                    if len(candidate) > 4:  # At least "001-x"
                        return candidate
            
            return ""
        except Exception as e:
            logger.error(f"Error extracting change ID: {e}")
            return ""

    @work(exclusive=False, thread=True)
    def read_output(self) -> None:
        """Read output from agent process."""
        terminal = self.query_one("#terminal-output", InteractiveTerminal)
        
        while self.agent_running and self.master_fd is not None:
            try:
                # Check if master_fd is still valid before using it
                if self.master_fd is None:
                    break
                
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
                    
            except Exception as e:
                logger.error(f"Error reading output: {e}")
                break

    def send_command(self, command: str, log: bool = True) -> None:
        """Send command to agent."""
        if not self.agent_running or not self.master_fd:
            self.log_output("ERROR: Agent is not running")
            return

        try:
            # Send command with carriage return and newline
            command_bytes = f"{command}\r\n".encode('utf-8')
            bytes_written = os.write(self.master_fd, command_bytes)
            logger.info(f"Sent command: {repr(command)}, bytes written: {bytes_written}")
            
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
            logger.error(f"Failed to send command: {e}", exc_info=True)

    @work(exclusive=True)
    async def run_workflow(self, workdir: str, session_name: str, change_id: str, agent: str = "kiro-cli", adk_config: dict = None) -> None:
        """Execute workflow automation.
        
        Args:
            workdir: Working directory path
            session_name: Session name for saving
            change_id: Change ID for apply operations
            agent: Agent to use ('kiro-cli', 'dspy-openspec', or 'adk-python')
            adk_config: ADK-specific configuration (agent_type, proposal, device_hint, mcp_port)
        """
        self.workflow_running = True
        workflow_tab = self.query_one(WorkflowTab)
        workflow_tab.workflow_status = "Running"
        adk_config = adk_config or {}
        
        try:
            # Resolve working directory
            if not workdir.startswith('/'):
                workdir = str(Path.cwd() / workdir)
            
            workdir_path = Path(workdir)
            if not workdir_path.exists():
                workdir_path.mkdir(parents=True, exist_ok=True)
                self.log_output(f"📁 Created working directory: {workdir}")
            
            # Generate session name if not provided
            if not session_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if agent == "dspy-openspec":
                    agent_prefix = "dspy"
                elif agent == "adk-python":
                    agent_prefix = "adk"
                else:
                    agent_prefix = "kiro"
                if self.workflow_mode.startswith("propose"):
                    session_name = f"{agent_prefix}-propose-session_{timestamp}.json"
                else:
                    session_name = f"{agent_prefix}-apply-session_{timestamp}.json"
            
            self.log_output("="*50)
            self.log_output(f"🚀 Starting Workflow: {self.workflow_mode}")
            self.log_output(f"Agent: {agent}")
            self.log_output(f"Working Directory: {workdir}")
            self.log_output(f"Session Name: {session_name}")
            if change_id:
                self.log_output(f"Change ID: {change_id}")
            if agent == 'adk-python' and adk_config:
                self.log_output(f"ADK Agent Type: {adk_config.get('agent_type', 'initial')}")
                self.log_output(f"ADK Proposal: {adk_config.get('proposal', 'N/A')}")
            self.log_output("="*50)
            
            # Step 1: Setup workspace
            workflow_tab.update_step(0, "running")
            await self.workflow_setup_workspace(workdir_path, self.workflow_mode, agent, adk_config)
            workflow_tab.update_step(0, "complete")
            
            # Step 2: Run agent workflow based on agent type
            workflow_tab.update_step(1, "running")
            
            if agent == 'adk-python':
                # Run ADK-specific workflow
                await self.run_adk_workflow(workdir_path, session_name, change_id, adk_config)
            elif agent == 'dspy-openspec':
                # DSPy OpenSpec workflow (existing code)
                await self._run_dspy_workflow(workdir_path, session_name, change_id, adk_config)
            else:
                # Interactive agents like kiro-cli
                await self._run_interactive_workflow(workdir_path, session_name, change_id, agent)
            
            workflow_tab.update_step(1, "complete")
            
            # Step 3: Session is now saved
            workflow_tab.update_step(2, "complete")
            
            # Step 4: Analyze session
            workflow_tab.update_step(3, "running")
            await self.workflow_analyze_session(workdir_path, session_name, agent)
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
            # Stop the agent after workflow completes
            if self.agent_running:
                self.log_output("🚪 Stopping agent...")
                self.stop_agent_process()

    async def _run_dspy_workflow(self, workdir: Path, session_name: str, change_id: str, adk_config: dict) -> None:
        """Run DSPy OpenSpec workflow."""
        if not self.agent_running:
            self.log_output("🚀 Starting dspy-openspec...")
            self.current_agent = 'dspy-openspec'
            
            # Build command arguments
            extra_args = None
            if self.workflow_mode.startswith("propose"):
                proposal_text = adk_config.get('proposal', "Propose to model a simple watchdog timer for Simics platform simulation")
                device_hint = adk_config.get('device_hint', "wdt")
                extra_args = ['proposal', proposal_text]
                if device_hint:
                    extra_args.extend(['--device', device_hint])
            elif self.workflow_mode == "apply":
                extra_args = ['apply', '--id', change_id]
            
            self.log_output(f"📝 DSPy command: dspy-openspec {' '.join(extra_args or [])}")
            
            # Start in the working directory with extra args
            self.start_agent_in_workdir(str(workdir), extra_args)
            
            # DSPy is non-interactive, just wait for it to complete
            self.log_output("⏳ Waiting for DSPy OpenSpec to complete...")
        
        # Wait for process to complete
        while self.agent_running and self.agent_process:
            if self.agent_process.poll() is not None:
                self.agent_running = False
                self.log_output("✅ DSPy OpenSpec completed!")
                break
            await asyncio.sleep(1.0)

    async def _run_interactive_workflow(self, workdir: Path, session_name: str, change_id: str, agent: str) -> None:
        """Run interactive agent workflow (kiro-cli, acli, qodercli)."""
        if not self.agent_running:
            self.log_output(f"🚀 Starting {agent}...")
            self.current_agent = agent
            
            # Start in the working directory
            self.start_agent_in_workdir(str(workdir), None)
            
            # Wait for agent to be ready
            # acli/qodercli may take longer to start than kiro-cli
            self.log_output(f"⏳ Waiting for {agent} to be ready...")
            timeout = 20.0 if agent in ['acli', 'qodercli'] else 15.0
            prompt_found = await self.wait_for_prompt(timeout=timeout)
            if not prompt_found:
                self.log_output(f"⚠️  Prompt not detected, but continuing anyway...")
        
        # Run agent workflow
        await self.workflow_run_agent(workdir, session_name, change_id, agent)

    async def run_adk_workflow(self, workdir: Path, session_name: str, change_id: str, adk_config: dict) -> None:
        """Run ADK Python OpenSpec workflow using PTY (similar to DSPy).
        
        This starts the ADK agent with PTY so output is shown in terminal.
        
        Args:
            workdir: Working directory path
            session_name: Session name for saving
            change_id: Change ID for apply operations
            adk_config: ADK-specific configuration
        """
        agent_type = adk_config.get('agent_type', 'initial')
        proposal = adk_config.get('proposal', '')
        device_hint = adk_config.get('device_hint', '')
        mcp_port = adk_config.get('mcp_port', '8051')
        
        # Prepare agent directories
        proposal_dir = workdir / f"adk_openspec_proposal_{agent_type}_agent"
        apply_dir = workdir / "adk_openspec_apply_agent"
        
        # Resolve proposal text
        proposal_text = proposal
        if proposal and Path(proposal).exists():
            self.log_output(f"📄 Reading proposal from file: {proposal}")
            proposal_text = Path(proposal).read_text()
        elif proposal and (Path(__file__).parent / proposal).exists():
            proposal_path = Path(__file__).parent / proposal
            self.log_output(f"📄 Reading proposal from file: {proposal_path}")
            proposal_text = proposal_path.read_text()
        
        resolved_change_id = change_id
        
        # Run proposal if not in apply-only mode
        if self.workflow_mode != "apply":
            self.log_output(f"🧩 Running /proposal with {agent_type} agent...")
            
            # Prepare proposal agent directory
            self._prepare_adk_agent_dir(
                proposal_dir, 
                f"openspec_integration.proposal_{agent_type}_agent",
                f"proposal_{agent_type}_agent"
            )
            
            # Build proposal command
            single_line_proposal = proposal_text.replace('\n', '\\n')
            proposal_cmd = f"/proposal {single_line_proposal}"
            if device_hint:
                proposal_cmd += f" --device {device_hint}"
            
            session_id = f"proposal_{change_id or datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.log_output(f"📝 Proposal command: {proposal_cmd[:100]}...")
            self.log_output(f"📁 Agent directory: {proposal_dir}")
            
            # Start ADK agent with PTY (like DSPy)
            if not self.agent_running:
                self.log_output("🚀 Starting ADK proposal agent...")
                self.current_agent = 'adk-python'
                
                # Build ADK command with arguments
                extra_args = ['run', str(proposal_dir), '--save_session', '--session_id', session_id]
                
                # Set environment variables for this agent
                old_env = os.environ.copy()
                os.environ.update(ADK_ENV_CONFIG)
                os.environ['MCP_PORT'] = mcp_port
                
                try:
                    self.start_agent_in_workdir(str(workdir), extra_args)
                    
                    # Wait for agent to be ready
                    self.log_output("⏳ Waiting for ADK agent to be ready...")
                    await asyncio.sleep(2.0)
                    
                    # Send proposal command
                    self.log_output(f"📝 Sending proposal command...")
                    self.send_command(proposal_cmd)
                    
                    # Wait for agent to complete
                    self.log_output("⏳ Waiting for ADK agent to complete...")
                    while self.agent_running and self.agent_process:
                        if self.agent_process.poll() is not None:
                            self.agent_running = False
                            self.log_output("✅ ADK proposal agent completed!")
                            break
                        await asyncio.sleep(1.0)
                    
                    # Try to extract change_id from terminal output
                    # Note: This is best-effort since output is in terminal
                    self.log_output("📋 Check terminal output for change_id")
                    
                finally:
                    # Restore environment
                    os.environ.clear()
                    os.environ.update(old_env)
        
        # Run apply if requested
        if self.workflow_mode in ["apply", "simple-full", "multi-delta-full"] and resolved_change_id:
            self.log_output(f"🔧 Running /apply for {resolved_change_id}...")
            
            # Prepare apply agent directory
            self._prepare_adk_agent_dir(
                apply_dir,
                "openspec_integration.apply_agent",
                "apply_agent"
            )
            
            apply_session_id = f"apply_{resolved_change_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Start ADK apply agent with PTY
            if not self.agent_running:
                self.log_output("🚀 Starting ADK apply agent...")
                self.current_agent = 'adk-python'
                
                extra_args = ['run', str(apply_dir), '--save_session', '--session_id', apply_session_id]
                
                # Set environment variables
                old_env = os.environ.copy()
                os.environ.update(ADK_ENV_CONFIG)
                os.environ['MCP_PORT'] = mcp_port
                
                try:
                    self.start_agent_in_workdir(str(workdir), extra_args)
                    
                    # Wait for agent to be ready
                    self.log_output("⏳ Waiting for ADK agent to be ready...")
                    await asyncio.sleep(2.0)
                    
                    # Send apply command
                    apply_cmd = f"/apply --id {resolved_change_id}"
                    self.log_output(f"📝 Sending apply command: {apply_cmd}")
                    self.send_command(apply_cmd)
                    
                    # Wait for agent to complete
                    self.log_output("⏳ Waiting for ADK agent to complete...")
                    while self.agent_running and self.agent_process:
                        if self.agent_process.poll() is not None:
                            self.agent_running = False
                            self.log_output("✅ ADK apply agent completed!")
                            break
                        await asyncio.sleep(1.0)
                    
                finally:
                    # Restore environment
                    os.environ.clear()
                    os.environ.update(old_env)


    def _prepare_adk_agent_dir(self, target_dir: Path, import_path: str, agent_name: str) -> None:
        """Prepare ADK agent directory with agent.py wrapper.
        
        Args:
            target_dir: Target directory for the agent
            import_path: Python import path for the agent (e.g., openspec_integration.apply_agent)
            agent_name: Name of the agent (e.g., apply_agent)
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Create agent.py that imports from samples
        samples_dir = ADK_SAMPLES_DIR
        agent_py_content = f'''import sys, os
sys.path.insert(0, '{samples_dir}')
from {import_path} import root_agent
'''
        (target_dir / 'agent.py').write_text(agent_py_content)
        self.log_output(f"✅ Created agent wrapper: {target_dir / 'agent.py'}")
        
        # Symlink instruction file if it exists
        instruction_src = samples_dir / 'openspec_integration' / f'{agent_name}_instruction.md'
        instruction_dst = target_dir / f'{agent_name}_instruction.md'
        if instruction_src.exists() and not instruction_dst.exists():
            instruction_dst.symlink_to(instruction_src)
            self.log_output(f"✅ Symlinked instruction file: {instruction_dst}")

    def _extract_change_id(self, output: str) -> str:
        """Extract change_id from ADK agent output.
        
        Args:
            output: Agent output text
            
        Returns:
            Extracted change_id or empty string
        """
        # Look for JSON pattern: "change_id": "xxx"
        match = re.search(r'"change_id"\s*:\s*"([^"]+)"', output)
        if match:
            return match.group(1)
        return ""

    async def workflow_setup_workspace(self, workdir: Path, mode: str, agent: str = "kiro-cli", adk_config: dict = None) -> None:
        """Setup workspace for workflow."""
        self.log_output("⚙️  Setting up workspace...")
        adk_config = adk_config or {}
        
        # Copy powers folder if needed (for all agents)
        powers_dir = workdir / "powers"
        if not powers_dir.exists():
            # Look for powers in the same directory as cli_tui.py (adk-python repo)
            script_dir = Path(__file__).parent
            repo_powers = script_dir / "powers"
            if repo_powers.exists():
                shutil.copytree(repo_powers, powers_dir)
                self.log_output(f"✅ Copied powers: {repo_powers} -> {powers_dir}")
            else:
                self.log_output(f"⚠️  powers folder not found at {repo_powers}, skipping copy")
        
        # Copy openspec-memories if needed for propose mode
        if mode.startswith("propose") or mode.endswith("-full"):
            memories_dir = workdir / "openspec-memories"
            if not memories_dir.exists():
                # Look for memories in the same directory as cli_tui.py (adk-python repo)
                script_dir = Path(__file__).parent
                repo_memories = script_dir / "openspec-memories"
                if repo_memories.exists():
                    shutil.copytree(repo_memories, memories_dir)
                    self.log_output(f"✅ Copied openspec-memories: {repo_memories} -> {memories_dir}")
                else:
                    self.log_output(f"⚠️  openspec-memories not found at {repo_memories}, skipping copy")
        
        # Check/copy MCP config for apply mode (kiro-cli only)
        if agent == 'kiro-cli' and mode in ["apply", "simple-full", "multi-delta-full"]:
            mcp_config = workdir / ".kiro" / "settings" / "mcp.json"
            if not mcp_config.exists():
                # Look for MCP config in the same directory as cli_tui.py (adk-python repo)
                script_dir = Path(__file__).parent
                repo_mcp = script_dir / ".kiro" / "settings" / "mcp.json"
                if repo_mcp.exists():
                    mcp_config.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(repo_mcp, mcp_config)
                    self.log_output(f"✅ Copied MCP config: {mcp_config}")
        
        self.log_output("✅ Workspace setup complete")

    async def workflow_run_agent(self, workdir: Path, session_name: str, change_id: str, agent: str = "kiro-cli") -> None:
        """Run interactive agent with appropriate prompt.
        
        Args:
            workdir: Working directory path
            session_name: Session name for saving
            change_id: Change ID for apply operations
            agent: Agent to use ('kiro-cli', 'acli', 'qodercli', etc.)
        """
        if agent not in ["kiro-cli", "acli", "qodercli"]:
            # Non-interactive agents are handled in run_workflow
            return
        
        self.log_output(f"🤖 Running {agent}...")
        
        # Both agents use relative path to powers (symlink created in workspace setup)
        power_base = "powers"
        
        # Construct prompt based on mode
        # Both kiro-cli and acli use the same prompt format:
        # "Read <POWER.md> and [propose|apply] ..."
        if self.workflow_mode == "propose-simple":
            power_md = f"{power_base}/openspec-propose/POWER.md"
            prompt = f"Read {power_md} and propose to model a simple watchdog timer for Simics platform simulation by following the instructions in POWER.md"
        elif self.workflow_mode == "propose-multi-delta":
            power_md = f"{power_base}/openspec-propose-multiple-spec-deltas/POWER.md"
            prompt = f"Read {power_md} and propose to model a complex watchdog timer device for Simics platform simulation by following the instructions in POWER.md. This is a complex device with 50+ requirements that should be decomposed into multiple capabilities with separate spec deltas."
        elif self.workflow_mode == "apply":
            power_md = f"{power_base}/openspec-apply/POWER.md"
            prompt = f"Read {power_md} and apply change {change_id} by following the instructions in POWER.md"
        elif self.workflow_mode == "simple-full":
            power_md = f"{power_base}/openspec-propose/POWER.md"
            prompt = f"Read {power_md} and propose to model a simple watchdog timer for Simics platform simulation by following the instructions in POWER.md"
        elif self.workflow_mode == "multi-delta-full":
            power_md = f"{power_base}/openspec-propose-multiple-spec-deltas/POWER.md"
            prompt = f"Read {power_md} and propose to model a complex watchdog timer device for Simics platform simulation by following the instructions in POWER.md. This is a complex device with 50+ requirements that should be decomposed into multiple capabilities with separate spec deltas."
        else:
            power_md = f"{power_base}/openspec-propose/POWER.md"
            prompt = f"Read {power_md} and propose to model a simple watchdog timer for Simics platform simulation by following the instructions in POWER.md"
        
        # Display prompt in chat window
        chat_tab = self.query_one(ChatTab)
        chat_tab.add_message("user", prompt)
        
        # Send prompt to agent
        self.send_command(prompt)
        
        # Give a moment for the command to be processed
        await asyncio.sleep(0.5)
        
        self.log_output("✅ Prompt sent, waiting for agent to complete...")
        self.log_output("⏳ Agent is working... (this may take several minutes)")
        
        # Wait for the agent to complete and return to prompt
        self.log_output("⏳ Waiting for agent to finish (looking for prompt)...")
        prompt_found = await self.wait_for_prompt(timeout=3600.0)  # 1 hour timeout
        
        if prompt_found:
            self.log_output("✅ Agent completed!")
            
            # Extract change ID from terminal output if in propose mode
            if self.workflow_mode.startswith("propose"):
                self.log_output("📋 Extracting change ID from output...")
                change_id = await self.extract_change_id_from_terminal()
                if change_id:
                    self.workflow_change_id = change_id
                    self.log_output(f"✅ Captured change ID: {change_id}")
                    
                    # If full workflow, continue with apply
                    if self.workflow_mode.endswith("-full"):
                        self.log_output("")
                        self.log_output("================================")
                        self.log_output("⏸️  Ready for Apply Step")
                        self.log_output("================================")
                        self.log_output("")
                        self.log_output(f"Change ID: {change_id}")
                        self.log_output("Continuing with apply in 3 seconds...")
                        await asyncio.sleep(3.0)
                        
                        # Send apply command with same format
                        power_md = f"{power_base}/openspec-apply/POWER.md"
                        apply_prompt = f"Read {power_md} and apply change {change_id} by following the instructions in POWER.md"
                        chat_tab.add_message("user", apply_prompt)
                        self.send_command(apply_prompt)
                        
                        # Wait for apply to complete
                        self.log_output("⏳ Waiting for apply to complete...")
                        await asyncio.sleep(0.5)
                        apply_prompt_found = await self.wait_for_prompt(timeout=3600.0)
                        
                        if apply_prompt_found:
                            self.log_output("✅ Apply completed!")
                        else:
                            self.log_output("⚠️  Timeout waiting for apply to complete")
            
            # For kiro-cli, save session
            if agent == "kiro-cli":
                # Wait a bit for the terminal to settle before sending the save command
                self.log_output("⏳ Waiting for terminal to settle...")
                await asyncio.sleep(3.0)
                
                self.log_output("💾 Preparing to save session...")
                
                # Determine session directory and save path
                if self.workflow_mode.startswith("propose"):
                    session_dir = workdir / "kiro-propose"
                else:
                    session_dir = workdir / "kiro-apply"
                
                session_dir.mkdir(parents=True, exist_ok=True)
                session_path = session_dir / session_name
                
                # Send /chat save command
                save_command = f"/chat save {session_path}"
                
                # Display in chat window
                chat_tab.add_message("user", save_command)
                
                # Send to kiro-cli
                self.log_output(f"💾 Issuing save command: {save_command}")
                self.send_command(save_command, log=False)
                
                # Wait for save to complete and prompt to return
                self.log_output("⏳ Waiting for save to complete...")
                save_prompt_found = await self.wait_for_prompt(timeout=30.0)
                
                if save_prompt_found:
                    self.log_output(f"✅ Session saved to: {session_path}")
                else:
                    self.log_output(f"⚠️  Save command sent, but prompt not detected")
                    self.log_output(f"   Session should be at: {session_path}")
        else:
            self.log_output("⚠️  Timeout waiting for agent to complete")
            if agent == "kiro-cli":
                self.log_output("   You can manually save with: /chat save <path>")

    async def workflow_analyze_session(self, workdir: Path, session_name: str, agent: str = "kiro-cli") -> None:
        """Analyze the workflow session."""
        self.log_output("📊 Analyzing session...")
        
        # For ADK, session files are in agent directories
        if agent == 'adk-python':
            # ADK sessions are saved in the agent directories
            agent_type = "initial"  # Default
            if self.workflow_mode.startswith("propose"):
                session_dir = workdir / f"adk_openspec_proposal_{agent_type}_agent"
            else:
                session_dir = workdir / "adk_openspec_apply_agent"
            
            # Find session files in the directory
            session_files = list(session_dir.glob("*.session.json"))
            if session_files:
                session_file = max(session_files, key=lambda f: f.stat().st_mtime)  # Most recent
                self.log_output(f"📄 Found ADK session: {session_file}")
                
                # Generate human-readable dump using view_session.py
                script_dir = Path(__file__).parent
                view_script = script_dir / "view_session.py"
                if view_script.exists():
                    try:
                        result = subprocess.run(
                            [sys.executable, str(view_script), str(session_file)],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if result.returncode == 0:
                            analysis_file = session_file.with_suffix('.txt')
                            analysis_file.write_text(result.stdout)
                            self.log_output(f"✅ Analysis saved: {analysis_file}")
                    except Exception as e:
                        self.log_output(f"⚠️  Analysis error: {e}")
            else:
                self.log_output(f"⚠️  No ADK session files found in {session_dir}")
            
            self.log_output("✅ Analysis complete")
            return
        
        # For kiro-cli, session files are in kiro-propose/kiro-apply directories
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
            # Run view_kiro_session.py from the same directory as cli_tui.py
            script_dir = Path(__file__).parent
            view_script = script_dir / "view_kiro_session.py"
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
                if self.workflow_mode.startswith("propose") or self.workflow_mode.endswith("-full"):
                    for line in result.stdout.split('\n'):
                        if "change" in line.lower() and "-" in line:
                            # Simple heuristic to find change IDs like "001-implement-wdt"
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