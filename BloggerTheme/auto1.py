import subprocess
import pyperclip

def run_apple_script(script):
    return subprocess.run(['osascript', '-e', script], capture_output=True, text=True).stdout.strip()

def get_safari_tabs():
    script = '''
    tell application "Safari"
        set tabList to {}
        repeat with w in windows
            repeat with t in tabs of w
                set end of tabList to (name of t) & "|" & (URL of t)
            end repeat
        end repeat
        return tabList
    end tell
    '''
    result = run_apple_script(script)
    tabs = []
    for line in result.split(', '):
        parts = line.split('|')
        if len(parts) == 2:
            tabs.append({'name': parts[0].strip(), 'URL': parts[1].strip()})
    return tabs

def format_tabs(tabs):
    return '\n'.join(f'[{tab["name"]}]({tab["URL"]})' for tab in tabs)

def main():
    tabs = get_safari_tabs()
    formatted_tabs = format_tabs(tabs)
    pyperclip.copy(formatted_tabs)
    print(f"Copied {len(tabs)} tab(s) to clipboard.")

if __name__ == "__main__":
    main()