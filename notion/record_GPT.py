#!/usr/bin/env python

from notion_client import Client
import pyperclip
import sys
from datetime import datetime
import re
notion_token = 'secret_8j9tcjr9gGF5pXCW9iDRaH0Q2QE7NLCNx4d6LfZaaBa'
notion_database_id = '10dcef0dda3e806c97bbca362447a5fb'

def create_rich_text(text):
    rich_text = []
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`|~~.*?~~|\[.*?\]\(.*?\))', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            rich_text.append({"type": "text", "text": {"content": part[2:-2]}, "annotations": {"bold": True}})
        elif part.startswith('*') and part.endswith('*'):
            rich_text.append({"type": "text", "text": {"content": part[1:-1]}, "annotations": {"italic": True}})
        elif part.startswith('`') and part.endswith('`'):
            rich_text.append({"type": "text", "text": {"content": part[1:-1]}, "annotations": {"code": True}})
        elif part.startswith('~~') and part.endswith('~~'):
            rich_text.append({"type": "text", "text": {"content": part[2:-2]}, "annotations": {"strikethrough": True}})
        elif part.startswith('[') and '](' in part and part.endswith(')'):
            link_text, link_url = re.match(r'\[(.*?)\]\((.*?)\)', part).groups()
            rich_text.append({"type": "text", "text": {"content": link_text, "link": {"url": link_url}}})
        else:
            rich_text.append({"type": "text", "text": {"content": part}})
    return rich_text

def parse_markdown(content):
    blocks = []
    lines = content.split('\n')
    code_block = False
    code_language = ''
    code_content = []

    def split_code_block(code, max_length=1900):
        return [code[i:i+max_length] for i in range(0, len(code), max_length)]

    for line in lines:
        if line.startswith('```'):
            if code_block:
                code_content_str = '\n'.join(code_content)
                code_parts = split_code_block(code_content_str)
                for part in code_parts:
                    blocks.append({
                        "type": "code",
                        "code": {
                            "language": code_language.lower() or "plain text",
                            "rich_text": [{"type": "text", "text": {"content": part}}]
                        }
                    })
                code_block = False
                code_language = ''
                code_content = []
            else:
                code_block = True
                code_language = line[3:].strip()
        elif code_block:
            code_content.append(line)
        elif line.startswith('# '):
            blocks.append({
                "type": "heading_1",
                "heading_1": {
                    "rich_text": create_rich_text(line[2:])
                }
            })
        elif line.startswith('## '):
            blocks.append({
                "type": "heading_2",
                "heading_2": {
                    "rich_text": create_rich_text(line[3:])
                }
            })
        elif line.startswith('### '):
            blocks.append({
                "type": "heading_3",
                "heading_3": {
                    "rich_text": create_rich_text(line[4:])
                }
            })
        elif line.startswith('> '):
            blocks.append({
                "type": "quote",
                "quote": {
                    "rich_text": create_rich_text(line[2:])
                }
            })
        elif line.startswith('- ') or line.startswith('* '):
            blocks.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": create_rich_text(line[2:])
                }
            })
        elif re.match(r'^\d+\. ', line):
            blocks.append({
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": create_rich_text(re.sub(r'^\d+\. ', '', line))
                }
            })
        elif line.startswith('- [ ] ') or line.startswith('- [x] '):
            checked = line.startswith('- [x] ')
            blocks.append({
                "type": "to_do",
                "to_do": {
                    "rich_text": create_rich_text(line[6:]),
                    "checked": checked
                }
            })
        elif line.strip() == '---':
            blocks.append({"type": "divider", "divider": {}})
        else:
            blocks.append({
                "type": "paragraph",
                "paragraph": {
                    "rich_text": create_rich_text(line)
                }
            })

    return blocks

def create_notion_page(client, database_id, title, content):
    try:
        blocks = parse_markdown(content)
        new_page = client.pages.create(
            parent={"database_id": database_id},
            properties={"Title": {"title": [{"text": {"content": title}}]}},
            children=blocks[:100]  # Notion API限制每次最多添加100个块
        )
        
        # 如果有超过100个块，分批添加剩余的块
        for i in range(100, len(blocks), 100):
            client.blocks.children.append(
                block_id=new_page["id"],
                children=blocks[i:i+100]
            )
        
        print(f"成功创建新页面: {new_page['url']}")
    except Exception as e:
        print(f"创建页面时出错: {str(e)}")
        print("尝试以纯文本形式创建页面...")
        try:
            new_page = client.pages.create(
                parent={"database_id": database_id},
                properties={"Title": {"title": [{"text": {"content": title}}]}},
                children=[{"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": content[:2000]}}]}}]
            )
            for i in range(2000, len(content), 2000):
                client.blocks.children.append(
                    block_id=new_page["id"],
                    children=[{"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": content[i:i+2000]}}]}}]
                )
            print(f"成功以纯文本形式创建新页面: {new_page['url']}")
        except Exception as e:
            print(f"以纯文本形式创建页面时也出错: {str(e)}")

def main():
    client = Client(auth=notion_token)

    if len(sys.argv) < 2:
        print("请提供标题作为命令行参数")
        return
    title = sys.argv[1]

    topic = input("请输入Topic (按回车跳过): ").strip()
    tags = input("请输入Tags (用逗号分隔, 按回车跳过): ").strip()

    content = pyperclip.paste()

    create_notion_page(client, notion_database_id, title, content)

if __name__ == '__main__':
    main()