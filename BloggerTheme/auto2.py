import subprocess
import pyperclip

def run_apple_script(script):
    return subprocess.run(['osascript', '-e', script], capture_output=True, text=True).stdout.strip()

def get_current_safari_tab():
    script = '''
    tell application "Safari"
        set currentTab to current tab of front window
        return {name of currentTab, URL of currentTab}
    end tell
    '''
    result = run_apple_script(script)
    title, url = result.split(', ')
    return {'name': title.strip(), 'URL': url.strip()}

def format_tab(tab):
    return f'[{tab["name"]}]({tab["URL"]})'

def main():
    tab = get_current_safari_tab()
    formatted_tab = format_tab(tab)
    pyperclip.copy(formatted_tab)
    print(f"Copied current tab to clipboard: {formatted_tab}")

if __name__ == "__main__":
    main()