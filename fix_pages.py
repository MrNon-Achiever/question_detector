"""
页码修正工具 - 简洁版
将目录.md中所有点号后面的页码减去26（仅对>26的页码生效）

使用方法:
    python fix_pages.py
"""
import re

with open('目录.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 匹配：一个或多个点 + 空白 + 数字
def fix_page(match):
    dots = match.group(1)  # 点号部分
    space = match.group(2) # 空白部分
    num = int(match.group(3))  # 数字部分
    if num > 26:
        num -= 26
    return f"{dots}{space}{num}"

# 正则：(\.+)(\s+)(\d+)
new_content = re.sub(r'(\.+)(\s+)(\d+)', fix_page, content)

with open('目录.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("完成！所有页码已减去26")
