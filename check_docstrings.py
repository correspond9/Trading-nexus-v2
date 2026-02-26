with open('app/routers/admin.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all triple quotes
in_docstring = False
docstring_start = None
for i, line in enumerate(lines, 1):
    if '"""' in line:
        # Count occurrences
        count = line.count('"""')
        if count == 1:
            if in_docstring:
                print(f"Line {i}: CLOSING docstring started at line {docstring_start}")
                in_docstring = False
            else:
                print(f"Line {i}: OPENING docstring")
                docstring_start = i
                in_docstring = True
        elif count == 2:
            print(f"Line {i}: Complete docstring (open and close on same line)")

if in_docstring:
    print(f"ERROR: Unclosed docstring starting at line {docstring_start}")
else:
    print("All docstrings properly closed.")
