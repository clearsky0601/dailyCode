from notion_client import Client
import os

notion_token = 'secret_8j9tcjr9gGF5pXCW9iDRaH0Q2QE7NLCNx4d6LfZaaBa'
notion_page_id = '111cef0dda3e80dba168c15a61a37fd0'

def main():
    client = Client(auth=notion_token)
    
    # 读取 useful_command.log 文件
    log_path = os.path.expanduser('~/.useful_commands.log')
    with open(log_path, 'r') as file:
        log_content = file.read()
    
    # 更新 Notion 页面
    client.blocks.children.append(
        notion_page_id,
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": log_content}}]
                }
            }
        ]
    )
    
    print("文件内容已成功同步到 Notion 页面")

if __name__ == '__main__':
    main()