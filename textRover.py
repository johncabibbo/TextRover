#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
#
# Filename: textRover.py
# Project: TextRover - File Text Search & Replace Tool
# Version: 1.0
# Description: Search and replace text/regex in files recursively
# Maintainer: Cloud Box 9 Inc.
# Last Modified Date: 2026-02-15
# -----------------------------------------------------------------------------

import os
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime

# Add CB9Lib to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # bundled CB9Lib (self-contained)

from CB9Lib import (
    header, footerMenu, clear_screen, pause,
    color_text, CYAN, GREEN, YELLOW, RED, MAGENTA, WHITE,
    BOLD, DIM, RESET, BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_RED,
    load_json_config, save_json_config,
    file_exists, folder_exists, ensure_folder,
    confirm
)

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
VERSION = "1.0"
SCRIPT_NAME = "TextRover"
CONFIG_FILE = Path(__file__).parent / "textRoverConfig.json"
DEFAULT_EXTENSIONS = [".txt", ".js", ".sh", ".inc", ".php"]

# Default configuration
DEFAULT_CONFIG = {
    "interactiveMode": False,
    "searchFolder": "",
    "searchPattern": "",
    "isRegex": False,
    "caseSensitive": True,
    "fileExtensions": DEFAULT_EXTENSIONS,
    "action": "display",
    "outputFile": "",
    "outputFileOption": True,
    "replaceWith": "",
    "replaceLine": "",
    "dryRun": False,
    "createBackup": True,
    "backupExtension": ".bak",
    "backupFolder": ""
}


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def get_terminal_width():
    """Get current terminal width."""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80


def print_separator(char="-"):
    """Print a separator line the width of the terminal."""
    width = get_terminal_width()
    print(color_text(char * width, CYAN))


def print_header_separator(char="="):
    """Print a header separator line."""
    width = get_terminal_width()
    print(color_text(char * width, BRIGHT_CYAN))


def display_header(subtitle=""):
    """Display the script header."""
    clear_screen()
    print_header_separator()
    title_text = f" {SCRIPT_NAME} v{VERSION}"
    if subtitle:
        title_text += f" [{subtitle}]"
    print(color_text(title_text, BRIGHT_CYAN, style=BOLD))
    print_header_separator()
    print()


def display_exit_screen():
    """Display the exit screen."""
    clear_screen()
    print_header_separator()
    print(color_text(f" {SCRIPT_NAME} v{VERSION}", BRIGHT_CYAN, style=BOLD))
    print_header_separator()
    print()
    print(color_text(f"{SCRIPT_NAME} exiting...", CYAN))
    print()
    print(color_text("Copyright 2026 Cloud Box 9 Inc. All rights reserved.", YELLOW))
    print()


def display_menu(options):
    """Display the footer menu and get user input."""
    print()
    print_separator()
    print(color_text(options, WHITE))
    print_separator()
    return input(color_text("Option: ", YELLOW))


def display_result(success, message):
    """Display a result message with appropriate color."""
    if success:
        print(color_text(f"SUCCESS: {message}", BRIGHT_GREEN))
    else:
        print(color_text(f"FAILED: {message}", BRIGHT_RED))


def press_any_key():
    """Wait for user to press any key."""
    print()
    print(color_text("Press Enter to Return to the Main Menu...", YELLOW))
    input()


# -----------------------------------------------------------------------------
# Input Functions (Hybrid Input System)
# -----------------------------------------------------------------------------
def get_input_with_arrows():
    """
    Get input with hybrid behavior:
    - ESC: Exit immediately
    - Arrows: Instant reaction (not fully implemented - would need curses)
    - Enter: Submit
    - Letters/Numbers: Wait for Enter
    """
    try:
        return input()
    except EOFError:
        return ""
    except KeyboardInterrupt:
        return "\x1b"  # ESC


def get_validated_path(prompt, must_exist=True):
    """Get and validate a path from user input."""
    while True:
        print(color_text(prompt, CYAN))
        path = input(color_text("Path: ", YELLOW)).strip()

        if not path:
            print(color_text("Path cannot be empty.", RED))
            continue

        path = os.path.expanduser(path)

        if must_exist and not os.path.exists(path):
            print(color_text(f"Path does not exist: {path}", RED))
            continue

        return path


def get_validated_choice(prompt, choices):
    """Get a validated choice from a list of options."""
    while True:
        print(color_text(prompt, CYAN))
        for i, choice in enumerate(choices, 1):
            print(f"  {color_text(str(i), YELLOW)}. {choice}")

        selection = input(color_text("Option: ", YELLOW)).strip()

        try:
            idx = int(selection) - 1
            if 0 <= idx < len(choices):
                return idx
        except ValueError:
            pass

        print(color_text("Invalid selection. Please try again.", RED))


def get_yes_no(prompt, default=True):
    """Get a yes/no response from user."""
    default_str = "Y/n" if default else "y/N"
    print(color_text(f"{prompt} [{default_str}]: ", CYAN), end="")
    response = input().strip().lower()

    if not response:
        return default
    return response in ('y', 'yes')


# -----------------------------------------------------------------------------
# File Operations
# -----------------------------------------------------------------------------
def find_matching_files(folder, extensions, recursive=True):
    """Find all files matching the specified extensions."""
    matching_files = []
    folder = Path(folder)

    if recursive:
        for ext in extensions:
            pattern = f"**/*{ext}"
            matching_files.extend(folder.glob(pattern))
    else:
        for ext in extensions:
            pattern = f"*{ext}"
            matching_files.extend(folder.glob(pattern))

    return sorted(matching_files)


def search_in_file(file_path, pattern, is_regex=False, case_sensitive=True):
    """
    Search for pattern in file.
    Returns list of tuples: (line_number, line_content, match_positions)
    """
    matches = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return None, str(e)

    flags = 0 if case_sensitive else re.IGNORECASE

    for line_num, line in enumerate(lines, 1):
        if is_regex:
            try:
                found = list(re.finditer(pattern, line, flags))
                if found:
                    positions = [(m.start(), m.end()) for m in found]
                    matches.append((line_num, line.rstrip('\n\r'), positions))
            except re.error as e:
                return None, f"Regex error: {e}"
        else:
            search_line = line if case_sensitive else line.lower()
            search_pattern = pattern if case_sensitive else pattern.lower()

            if search_pattern in search_line:
                # Find all occurrences
                positions = []
                start = 0
                while True:
                    pos = search_line.find(search_pattern, start)
                    if pos == -1:
                        break
                    positions.append((pos, pos + len(search_pattern)))
                    start = pos + 1

                matches.append((line_num, line.rstrip('\n\r'), positions))

    return matches, None


def create_backup(file_path, backup_ext=".bak", backup_folder=""):
    """Create a backup of a file.

    Args:
        file_path: Path to the file to backup
        backup_ext: Extension to add to backup file (default: .bak)
        backup_folder: Folder to store backups. If empty, uses same folder as original file.
    """
    try:
        file_path = Path(file_path)

        if backup_folder and backup_folder.strip():
            # Use specified backup folder
            backup_dir = Path(os.path.expanduser(backup_folder))
            # Create backup folder if it doesn't exist
            backup_dir.mkdir(parents=True, exist_ok=True)
            # Backup file goes in backup folder with same name + extension
            backup_path = backup_dir / (file_path.name + backup_ext)
        else:
            # Use same folder as original file
            backup_path = str(file_path) + backup_ext

        shutil.copy2(file_path, backup_path)
        return True, str(backup_path)
    except Exception as e:
        return False, str(e)


def replace_text_in_file(file_path, pattern, replacement, is_regex=False,
                         case_sensitive=True, replace_line=False, dry_run=False,
                         create_backup_file=True, backup_ext=".bak", backup_folder=""):
    """
    Replace text in a file.
    If replace_line=True, replaces the entire line containing the match.
    Returns: (success, message, changes_made)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return False, f"Error reading file: {e}", 0

    changes_made = 0
    new_lines = []
    flags = 0 if case_sensitive else re.IGNORECASE

    for line in lines:
        if replace_line:
            # Check if line contains pattern
            if is_regex:
                try:
                    if re.search(pattern, line, flags):
                        new_lines.append(replacement)
                        changes_made += 1
                    else:
                        new_lines.append(line)
                except re.error as e:
                    return False, f"Regex error: {e}", 0
            else:
                search_line = line if case_sensitive else line.lower()
                search_pattern = pattern if case_sensitive else pattern.lower()

                if search_pattern in search_line:
                    new_lines.append(replacement)
                    changes_made += 1
                else:
                    new_lines.append(line)
        else:
            # Replace just the matched text
            if is_regex:
                try:
                    new_line, count = re.subn(pattern, replacement, line, flags=flags)
                    changes_made += count
                    new_lines.append(new_line)
                except re.error as e:
                    return False, f"Regex error: {e}", 0
            else:
                if case_sensitive:
                    count = line.count(pattern)
                    new_line = line.replace(pattern, replacement)
                else:
                    # Case-insensitive replace
                    count = len(re.findall(re.escape(pattern), line, re.IGNORECASE))
                    new_line = re.sub(re.escape(pattern), replacement, line, flags=re.IGNORECASE)

                changes_made += count
                new_lines.append(new_line)

    if changes_made == 0:
        return True, "No matches found", 0

    if dry_run:
        return True, f"DRY RUN: Would make {changes_made} replacement(s)", changes_made

    # Create backup if requested
    if create_backup_file:
        backup_success, backup_msg = create_backup(file_path, backup_ext, backup_folder)
        if not backup_success:
            return False, f"Failed to create backup: {backup_msg}", 0

    # Write changes
    try:
        new_content = '\n'.join(new_lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, f"Made {changes_made} replacement(s)", changes_made
    except Exception as e:
        return False, f"Error writing file: {e}", 0


# -----------------------------------------------------------------------------
# Action Functions
# -----------------------------------------------------------------------------
def action_display_to_screen(config, files_with_matches):
    """Display matches to screen."""
    display_header("Search Results")

    if not files_with_matches:
        print(color_text("No matches found.", YELLOW))
    else:
        total_matches = 0
        for file_path, matches in files_with_matches:
            rel_path = os.path.relpath(file_path, config['searchFolder'])
            print(color_text(f"\n{rel_path}", BRIGHT_CYAN, style=BOLD))

            for line_num, line_content, positions in matches:
                total_matches += len(positions)
                # Highlight matches in line
                print(f"  {color_text(str(line_num), YELLOW):>6}: {line_content[:100]}{'...' if len(line_content) > 100 else ''}")

        print()
        print_separator()
        print(color_text(f"Total: {len(files_with_matches)} file(s), {total_matches} match(es)", BRIGHT_GREEN))

    press_any_key()


def action_write_to_file(config, files_with_matches):
    """Write matches to a text file."""
    display_header("Writing to File")

    # Check if output file writing is enabled
    output_file_option = config.get('outputFileOption', True)
    if not output_file_option:
        print(color_text("Output file writing is disabled in config (outputFileOption = false).", YELLOW))
        press_any_key()
        return

    output_file = config.get('outputFile', '')
    if not output_file:
        output_file = get_validated_path("Enter output file path:", must_exist=False)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"TextRover Search Results\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Search Folder: {config['searchFolder']}\n")
            f.write(f"Search Pattern: {config['searchPattern']}\n")
            f.write(f"Is Regex: {config['isRegex']}\n")
            f.write(f"Case Sensitive: {config['caseSensitive']}\n")
            f.write("=" * 80 + "\n\n")

            if not files_with_matches:
                f.write("No matches found.\n")
            else:
                total_matches = 0
                for file_path, matches in files_with_matches:
                    rel_path = os.path.relpath(file_path, config['searchFolder'])
                    f.write(f"\nFile: {rel_path}\n")
                    f.write("-" * 40 + "\n")

                    for line_num, line_content, positions in matches:
                        total_matches += len(positions)
                        f.write(f"  Line {line_num}: {line_content}\n")

                f.write("\n" + "=" * 80 + "\n")
                f.write(f"Total: {len(files_with_matches)} file(s), {total_matches} match(es)\n")

        display_result(True, f"Results written to: {output_file}")
    except Exception as e:
        display_result(False, f"Error writing file: {e}")

    press_any_key()


def action_replace_text(config, files_with_matches):
    """Replace matched text in files."""
    display_header("Replace Text")

    if not files_with_matches:
        print(color_text("No matches found. Nothing to replace.", YELLOW))
        press_any_key()
        return

    replacement = config.get('replaceWith', '')
    if config.get('interactiveMode') or not replacement:
        print(color_text("Enter replacement text (leave empty to delete matches):", CYAN))
        replacement = input(color_text("Replace with: ", YELLOW))

    dry_run = config.get('dryRun', False)
    create_backup_file = config.get('createBackup', True)
    backup_ext = config.get('backupExtension', '.bak')
    backup_folder = config.get('backupFolder', '')

    if dry_run:
        print(color_text("\n*** DRY RUN MODE - No files will be modified ***\n", BRIGHT_YELLOW, style=BOLD))

    print(color_text(f"\nProcessing {len(files_with_matches)} file(s)...\n", CYAN))

    total_changes = 0
    files_modified = 0

    for file_path, matches in files_with_matches:
        rel_path = os.path.relpath(file_path, config['searchFolder'])

        success, message, changes = replace_text_in_file(
            file_path, config['searchPattern'], replacement,
            is_regex=config['isRegex'],
            case_sensitive=config['caseSensitive'],
            replace_line=False,
            dry_run=dry_run,
            create_backup_file=create_backup_file,
            backup_ext=backup_ext,
            backup_folder=backup_folder
        )

        if success:
            if changes > 0:
                print(color_text(f"  {rel_path}: {message}", BRIGHT_GREEN))
                total_changes += changes
                files_modified += 1
        else:
            print(color_text(f"  {rel_path}: {message}", BRIGHT_RED))

    print()
    print_separator()
    if dry_run:
        print(color_text(f"DRY RUN: Would modify {files_modified} file(s) with {total_changes} change(s)", BRIGHT_YELLOW))
    else:
        print(color_text(f"Modified {files_modified} file(s) with {total_changes} change(s)", BRIGHT_GREEN))

    press_any_key()


def action_replace_line(config, files_with_matches):
    """Replace entire lines containing matches."""
    display_header("Replace Entire Line")

    if not files_with_matches:
        print(color_text("No matches found. Nothing to replace.", YELLOW))
        press_any_key()
        return

    replacement = config.get('replaceLine', '')
    if config.get('interactiveMode') or not replacement:
        print(color_text("Enter replacement line (leave empty to delete lines):", CYAN))
        replacement = input(color_text("Replace line with: ", YELLOW))

    dry_run = config.get('dryRun', False)
    create_backup_file = config.get('createBackup', True)
    backup_ext = config.get('backupExtension', '.bak')
    backup_folder = config.get('backupFolder', '')

    if dry_run:
        print(color_text("\n*** DRY RUN MODE - No files will be modified ***\n", BRIGHT_YELLOW, style=BOLD))

    print(color_text(f"\nProcessing {len(files_with_matches)} file(s)...\n", CYAN))

    total_changes = 0
    files_modified = 0

    for file_path, matches in files_with_matches:
        rel_path = os.path.relpath(file_path, config['searchFolder'])

        success, message, changes = replace_text_in_file(
            file_path, config['searchPattern'], replacement,
            is_regex=config['isRegex'],
            case_sensitive=config['caseSensitive'],
            replace_line=True,
            dry_run=dry_run,
            create_backup_file=create_backup_file,
            backup_ext=backup_ext,
            backup_folder=backup_folder
        )

        if success:
            if changes > 0:
                print(color_text(f"  {rel_path}: {message}", BRIGHT_GREEN))
                total_changes += changes
                files_modified += 1
        else:
            print(color_text(f"  {rel_path}: {message}", BRIGHT_RED))

    print()
    print_separator()
    if dry_run:
        print(color_text(f"DRY RUN: Would modify {files_modified} file(s), {total_changes} line(s) replaced", BRIGHT_YELLOW))
    else:
        print(color_text(f"Modified {files_modified} file(s), {total_changes} line(s) replaced", BRIGHT_GREEN))

    press_any_key()


# -----------------------------------------------------------------------------
# Search Execution
# -----------------------------------------------------------------------------
def execute_search(config):
    """Execute the search based on configuration."""
    display_header("Searching...")

    search_folder = config['searchFolder']
    pattern = config['searchPattern']
    extensions = config['fileExtensions']
    is_regex = config['isRegex']
    case_sensitive = config['caseSensitive']

    # Validate
    if not search_folder or not folder_exists(search_folder):
        print(color_text(f"Error: Search folder does not exist: {search_folder}", RED))
        press_any_key()
        return None

    if not pattern:
        print(color_text("Error: Search pattern is empty", RED))
        press_any_key()
        return None

    # Find files
    print(color_text(f"Searching in: {search_folder}", CYAN))
    print(color_text(f"Extensions: {', '.join(extensions)}", CYAN))
    print(color_text(f"Pattern: {pattern}", CYAN))
    print(color_text(f"Regex: {is_regex}, Case Sensitive: {case_sensitive}", CYAN))
    print()

    matching_files = find_matching_files(search_folder, extensions)
    print(color_text(f"Found {len(matching_files)} file(s) to search...", CYAN))

    files_with_matches = []

    for file_path in matching_files:
        matches, error = search_in_file(file_path, pattern, is_regex, case_sensitive)

        if error:
            print(color_text(f"  Error in {file_path}: {error}", RED))
            continue

        if matches:
            files_with_matches.append((file_path, matches))

    print(color_text(f"\nFound matches in {len(files_with_matches)} file(s)", BRIGHT_GREEN))

    return files_with_matches


# -----------------------------------------------------------------------------
# Interactive Mode
# -----------------------------------------------------------------------------
def run_interactive_mode():
    """Run in interactive mode, prompting for all settings."""
    config = DEFAULT_CONFIG.copy()
    config['interactiveMode'] = True

    while True:
        display_header("Interactive Mode")

        # Get search folder
        print(color_text("Step 1: Enter the folder to search", BRIGHT_CYAN, style=BOLD))
        config['searchFolder'] = get_validated_path("", must_exist=True)
        print()

        # Get search pattern
        print(color_text("Step 2: Enter search pattern", BRIGHT_CYAN, style=BOLD))
        print(color_text("Enter the text or regex pattern to search for:", CYAN))
        config['searchPattern'] = input(color_text("Pattern: ", YELLOW)).strip()

        if not config['searchPattern']:
            print(color_text("Pattern cannot be empty.", RED))
            continue
        print()

        # Is regex?
        print(color_text("Step 3: Pattern type", BRIGHT_CYAN, style=BOLD))
        config['isRegex'] = get_yes_no("Is this a regular expression?", default=False)
        print()

        # Case sensitive?
        print(color_text("Step 4: Case sensitivity", BRIGHT_CYAN, style=BOLD))
        config['caseSensitive'] = get_yes_no("Case sensitive search?", default=True)
        print()

        # File extensions
        print(color_text("Step 5: File extensions", BRIGHT_CYAN, style=BOLD))
        print(color_text(f"Default extensions: {', '.join(DEFAULT_EXTENSIONS)}", DIM))
        use_default = get_yes_no("Use default extensions?", default=True)

        if use_default:
            config['fileExtensions'] = DEFAULT_EXTENSIONS
        else:
            print(color_text("Enter extensions separated by commas (e.g., .py,.js,.txt):", CYAN))
            ext_input = input(color_text("Extensions: ", YELLOW)).strip()
            config['fileExtensions'] = [e.strip() if e.strip().startswith('.') else f".{e.strip()}"
                                        for e in ext_input.split(',') if e.strip()]
        print()

        # Action selection
        print(color_text("Step 6: Select action", BRIGHT_CYAN, style=BOLD))
        actions = [
            "Display matches to screen",
            "Write matches to a text file",
            "Replace/delete matched text",
            "Replace entire lines containing matches"
        ]
        action_idx = get_validated_choice("What do you want to do with matches?", actions)
        action_map = ['display', 'write', 'replace', 'replace_line']
        config['action'] = action_map[action_idx]
        print()

        # Safety options for replace actions
        if config['action'] in ('replace', 'replace_line'):
            print(color_text("Step 7: Safety options", BRIGHT_CYAN, style=BOLD))
            config['dryRun'] = get_yes_no("Dry run mode (preview only, no changes)?", default=True)
            config['createBackup'] = get_yes_no("Create backup before modifying files?", default=True)
            print()

        # Execute
        files_with_matches = execute_search(config)

        if files_with_matches is not None:
            if config['action'] == 'display':
                action_display_to_screen(config, files_with_matches)
            elif config['action'] == 'write':
                action_write_to_file(config, files_with_matches)
            elif config['action'] == 'replace':
                action_replace_text(config, files_with_matches)
            elif config['action'] == 'replace_line':
                action_replace_line(config, files_with_matches)

        # Continue?
        display_header("Interactive Mode")
        if not get_yes_no("Run another search?", default=True):
            break

    return True


# -----------------------------------------------------------------------------
# Config Mode
# -----------------------------------------------------------------------------
def run_from_config():
    """Run using settings from config file."""
    if not file_exists(str(CONFIG_FILE)):
        print(color_text(f"Config file not found: {CONFIG_FILE}", RED))
        print(color_text("Creating default config file...", YELLOW))
        save_json_config(str(CONFIG_FILE), DEFAULT_CONFIG)
        print(color_text(f"Created: {CONFIG_FILE}", GREEN))
        print(color_text("Please edit the config file and run again.", CYAN))
        press_any_key()
        return False

    config = load_json_config(str(CONFIG_FILE))
    if not config:
        print(color_text("Error loading config file", RED))
        press_any_key()
        return False

    # Merge with defaults for any missing keys
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value

    # Check for interactive mode
    if config.get('interactiveMode', False):
        return run_interactive_mode()

    # Execute search
    files_with_matches = execute_search(config)

    if files_with_matches is not None:
        action = config.get('action', 'display')

        if action == 'display':
            action_display_to_screen(config, files_with_matches)
        elif action == 'write':
            action_write_to_file(config, files_with_matches)
        elif action == 'replace':
            action_replace_text(config, files_with_matches)
        elif action == 'replace_line':
            action_replace_line(config, files_with_matches)

    return True


# -----------------------------------------------------------------------------
# Main Menu
# -----------------------------------------------------------------------------
def show_current_config():
    """Display current configuration."""
    display_header("Current Configuration")

    if not file_exists(str(CONFIG_FILE)):
        print(color_text("No config file found.", YELLOW))
    else:
        config = load_json_config(str(CONFIG_FILE))
        if config:
            print(color_text("Configuration Settings:", BRIGHT_CYAN, style=BOLD))
            print()
            for key, value in config.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                print(f"  {color_text(key, CYAN):.<35} {color_text(str(value), WHITE)}")

    press_any_key()


def edit_config():
    """Edit configuration interactively."""
    display_header("Edit Configuration")

    if not file_exists(str(CONFIG_FILE)):
        config = DEFAULT_CONFIG.copy()
    else:
        config = load_json_config(str(CONFIG_FILE))
        if not config:
            config = DEFAULT_CONFIG.copy()

    # Merge with defaults
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value

    while True:
        display_header("Edit Configuration")

        settings = [
            ("interactiveMode", "Interactive Mode", "bool"),
            ("searchFolder", "Search Folder", "path"),
            ("searchPattern", "Search Pattern", "text"),
            ("isRegex", "Is Regex", "bool"),
            ("caseSensitive", "Case Sensitive", "bool"),
            ("fileExtensions", "File Extensions", "list"),
            ("action", "Action (display/write/replace/replace_line)", "choice"),
            ("outputFile", "Output File (for write action)", "text"),
            ("replaceWith", "Replace With", "text"),
            ("replaceLine", "Replace Line With", "text"),
            ("dryRun", "Dry Run Mode", "bool"),
            ("createBackup", "Create Backup", "bool"),
            ("backupExtension", "Backup Extension", "text"),
        ]

        print(color_text("Current Settings:", BRIGHT_CYAN, style=BOLD))
        print()

        for i, (key, label, _) in enumerate(settings, 1):
            value = config.get(key, '')
            if isinstance(value, list):
                value = ', '.join(value)
            print(f"  {color_text(str(i), YELLOW):>3}. {label:.<40} {color_text(str(value), WHITE)}")

        choice = display_menu("[1-13] Edit Setting  [S] Save  [Q] Cancel")

        if choice.lower() == 'q':
            break
        elif choice.lower() == 's':
            save_json_config(str(CONFIG_FILE), config)
            print(color_text(f"\nConfiguration saved to: {CONFIG_FILE}", BRIGHT_GREEN))
            press_any_key()
            break
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(settings):
                    key, label, field_type = settings[idx]

                    print(f"\nEditing: {color_text(label, BRIGHT_CYAN)}")
                    print(f"Current value: {color_text(str(config[key]), YELLOW)}")

                    if field_type == 'bool':
                        config[key] = get_yes_no("New value?", default=config[key])
                    elif field_type == 'path':
                        new_val = input(color_text("New path (or Enter to keep): ", YELLOW)).strip()
                        if new_val:
                            config[key] = os.path.expanduser(new_val)
                    elif field_type == 'list':
                        print(color_text("Enter values separated by commas:", CYAN))
                        new_val = input(color_text("New value: ", YELLOW)).strip()
                        if new_val:
                            config[key] = [v.strip() for v in new_val.split(',') if v.strip()]
                    elif field_type == 'choice':
                        choices = ['display', 'write', 'replace', 'replace_line']
                        idx = get_validated_choice("Select action:", choices)
                        config[key] = choices[idx]
                    else:
                        new_val = input(color_text("New value (or Enter to keep): ", YELLOW))
                        if new_val:
                            config[key] = new_val
            except ValueError:
                pass


def main_menu():
    """Display and handle main menu."""
    while True:
        display_header("Main Menu")

        print(color_text(" 1.", YELLOW), "Run Interactive Mode")
        print(color_text(" 2.", YELLOW), "Run from Config File")
        print(color_text(" 3.", YELLOW), "View Current Config")
        print(color_text(" 4.", YELLOW), "Edit Config")
        print(color_text(" 5.", YELLOW), "Create/Reset Default Config")

        choice = display_menu("[1-5] Select  [Q/Esc] Quit")

        if choice.lower() in ('q', '\x1b', ''):
            break
        elif choice == '1':
            run_interactive_mode()
        elif choice == '2':
            run_from_config()
        elif choice == '3':
            show_current_config()
        elif choice == '4':
            edit_config()
        elif choice == '5':
            display_header("Create Default Config")
            if get_yes_no("This will overwrite existing config. Continue?", default=False):
                save_json_config(str(CONFIG_FILE), DEFAULT_CONFIG)
                print(color_text(f"\nCreated default config: {CONFIG_FILE}", BRIGHT_GREEN))
            press_any_key()


# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
def main():
    """Main entry point."""
    try:
        # Check for command-line arguments
        if len(sys.argv) > 1:
            arg = sys.argv[1].lower()
            if arg in ('-h', '--help'):
                print(f"{SCRIPT_NAME} v{VERSION}")
                print("Usage: textRover.py [options]")
                print()
                print("Options:")
                print("  -h, --help      Show this help message")
                print("  -i, --interactive  Run in interactive mode")
                print("  -c, --config    Run from config file (default)")
                print()
                print(f"Config file: {CONFIG_FILE}")
                return
            elif arg in ('-i', '--interactive'):
                run_interactive_mode()
                display_exit_screen()
                return
            elif arg in ('-c', '--config'):
                display_header("Running from Config")
                run_from_config()
                display_exit_screen()
                return

        # Default: show main menu
        main_menu()
        display_exit_screen()

    except KeyboardInterrupt:
        display_exit_screen()


if __name__ == "__main__":
    main()
