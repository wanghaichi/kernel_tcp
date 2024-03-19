import difflib

# 旧代码文本
old_code = """
def foo():
    print("Hello, world!")

def bar():
    print("This is bar.")
"""

# 新代码文本
new_code = """
def foo():
    print("Hello, OpenAI!")

def baz():
    print("This is baz.")
"""

# 按行拆分旧代码和新代码
old_lines = old_code.strip().splitlines()
new_lines = new_code.strip().splitlines()

# 比较旧代码和新代码的差异
diff = difflib.ndiff(old_lines, new_lines)
for line in diff:
    print(line)

# 提取修改的行号
# changed_lines = []
# for line in diff:
#     if line.startswith('+') or line.startswith('-'):
#         line_number = line[1:].split(',')[0].strip()
#         changed_lines.append(int(line_number))

# # 输出修改的行号
# for line_number in changed_lines:
#     print(f"Line {line_number} has been modified.")