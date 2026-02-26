import ast
try:
    with open('app/routers/admin.py', 'r') as f:
        ast.parse(f.read())
    print("OK")
except SyntaxError as e:
    print(f"ERROR at line {e.lineno}: {e.msg}")
