import subprocess

def get_clipboard():
    # 使用pbpaste命令获取剪切板内容
    p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    # 读取输出并解码为字符串
    clipboard_content = p.communicate()[0].decode('utf-8')
    return clipboard_content

if __name__ == "__main__":
    content = get_clipboard()
    print("当前剪切板内容为：")
    print(content)
