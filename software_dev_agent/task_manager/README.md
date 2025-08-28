# Task Manager Application

This Task Manager application is a simple command-line tool that allows users to add, list, complete, and remove tasks. Tasks are persisted on disk using JSON.

## Features

1. **Add Task**: Add tasks with a description, optional due date, and priority.
2. **List Tasks**: List and filter tasks by status or sort them by various keys.
3. **Complete Task**: Mark tasks as completed.
4. **Remove Task**: Remove tasks from the task list.
5. **Data Persistence**: Tasks persist between sessions on the local file system.

## Requirements

- Python 3.8 or higher

## Installation and Setup

1. Clone the repository or download the project files.
2. Ensure Python 3.8+ is installed on your system.

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Usage

Run the application via the CLI:

```bash
python -m task_manager.src.cli <command> [options]
```

### Commands

- `add "Task description" [--due YYYY-MM-DD] [--priority low|medium|high]`
- `list [--status pending|completed] [--sort created|due|priority]`
- `complete <task_id>`
- `remove <task_id>`

### Example
```bash
$ python -m task_manager.src.cli add "Buy groceries" --due 2024-02-15 --priority high
Task added: #1 - Buy groceries

$ python -m task_manager.src.cli list
1. [PENDING] Buy groceries (Due: 2024-02-15, Priority: High)

$ python -m task_manager.src.cli complete 1
Task #1 marked as completed

$ python -m task_manager.src.cli list --status completed
1. [COMPLETED] Buy groceries (Completed: 2024-02-14)
```