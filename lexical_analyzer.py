import re
from collections import defaultdict

# Define C language keywords
keywords = {
    'int', 'float', 'char', 'if', 'else', 'for', 'while', 'do', 'return',
    'void', 'break', 'continue', 'switch', 'case', 'default', 'sizeof'
}

# Define token regex patterns
token_specification = [
    ('KEYWORD',      r'\b(?:' + '|'.join(keywords) + r')\b'),
    ('IDENTIFIER',   r'\b[A-Za-z_]\w*\b'),
    ('CONSTANT',     r'\b\d+\.\d+|\b\d+|\'[^\']\''),
    ('LOGICAL_OP',   r'==|!=|<=|>=|<|>'),
    ('ARITH_OP',     r'[+\-*/=]'),
    ('PARENTHESIS',  r'[()\[\]{}]'),
    ('PUNCTUATION',  r'[;,]'),
    ('SKIP',         r'[ \t\n]+'),
    ('MISMATCH',     r'.'),
]

# Combine regex patterns
tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)

# Function to remove single-line and multi-line comments
def remove_comments(code):
    pattern = r'//.*?$|/\*.*?\*/'
    return re.sub(pattern, '', code, flags=re.MULTILINE | re.DOTALL)

# Function to tokenize and categorize tokens
def lexical_analysis(code):
    code = remove_comments(code)
    tokens = defaultdict(set)

    for match in re.finditer(tok_regex, code):
        kind = match.lastgroup
        value = match.group().strip()

        if kind in ['SKIP', 'MISMATCH']:
            continue
        if kind == 'KEYWORD':
            tokens['Keyword'].add(value)
        elif kind == 'IDENTIFIER':
            if value not in keywords:
                tokens['Identifier'].add(value)
        elif kind == 'CONSTANT':
            tokens['Constant'].add(value)
        elif kind == 'ARITH_OP':
            tokens['Arithmetic Operator'].add(value)
        elif kind == 'PUNCTUATION':
            tokens['Punctuation'].add(value)
        elif kind == 'PARENTHESIS':
            tokens['Parenthesis'].add(value)
        elif kind == 'LOGICAL Operator':
            tokens['Logical Operator'].add(value)

    return tokens

# === Load and analyze uploaded C file ===
file_path = r'D:\OneDrive\Pictures\SusmitaProject\LA.c'

with open(file_path, 'r') as file:
    c_code = file.read()

# Run lexical analysis
token_groups = lexical_analysis(c_code)

# Define output display order
output_order = [
    'Keyword', 'Identifier', 'Constant',
    'Arithmetic Operator', 'Punctuation',
    'Parenthesis', 'Logical Operator'
]

# Print tokens in formatted output
for token_type in output_order:
    if token_type in token_groups:
        values = sorted(token_groups[token_type])
        count = len(values)
        print(f"{token_type} ({count}): {', '.join(values)}")
