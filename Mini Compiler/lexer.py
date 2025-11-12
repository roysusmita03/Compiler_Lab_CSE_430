import re

# == Full C Keyword List ===
C_KEYWORDS = [
    "auto", "break", "case", "char", "const", "continue",
    "default", "do", "double", "else", "enum", "extern",
    "float", "for", "goto", "if", "inline", "int", "long",
    "register", "restrict", "return", "short", "signed",
    "sizeof", "static", "struct", "switch", "typedef",
    "union", "unsigned", "void", "volatile", "while", "_Bool",
    "_Complex", "_Imaginary"
]

# == Token Specification ===
token_specification = [
    ('COMMENT_MULTI',    r'/\*[\s\S]*?\*/'),
    ('COMMENT_SINGLE',   r'//[^\n]*'),
    ('KEYWORD',          r'\b(' + '|'.join(C_KEYWORDS) + r')\b'),
    ('IDENTIFIER',       r'[A-Za-z_]\w*'),
    ('FLOAT_LITERAL',    r'\d+\.\d+([eE][+-]?\d+)?'),
    ('INTEGER_LITERAL',  r'\d+'),
    ('CHAR_LITERAL',     r"'(\\['\"\\nrt]|[^'\\])'"),
    ('STRING_LITERAL',   r'"(\\["\\nrt]|[^"\\])*"'),
    ('RELATIONAL_OPERATOR', r'<=|>=|==|!=|<|>'),
    ('ASSIGNMENT',       r'='),
    ('ARITHMETIC_OPERATOR', r'[\+\-\*/%]'),
    ('LOGICAL_OPERATOR', r'&&|\|\||!'),
    ('BITWISE_OPERATOR', r'&|\||\^|~|<<|>>'),
    ('INCREMENT_OPERATOR', r'\+\+|--'),
    ('TERNARY_OPERATOR', r'\?|:'),
    ('SEMICOLON',        r';'),
    ('COMMA',            r','),
    ('DOT',              r'\.'),
    ('LEFT_PAREN',       r'\('),
    ('RIGHT_PAREN',      r'\)'),
    ('LEFT_BRACE',       r'\{'),
    ('RIGHT_BRACE',      r'\}'),
    ('LEFT_BRACKET',     r'\['),
    ('RIGHT_BRACKET',    r'\]'),
    ('NEWLINE',          r'\n'),
    ('WHITESPACE',       r'[ \t]+'),
    ('MISMATCH',         r'.'),
]

# === Combine into one regex ===
tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
token_re = re.compile(tok_regex)

def preprocess_code(code):
    """Remove redundant blank lines and trailing spaces."""
    code = re.sub(r'\n\s*\n+', '\n', code)
    code = re.sub(r'[ \t]+$', '', code, flags=re.MULTILINE)
    return code.strip()

def tokenize(code):
    """Perform lexical analysis."""
    code = preprocess_code(code)
    tokens = []
    line_num = 1
    line_start = 0

    for mo in token_re.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start + 1

        if kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()
            continue
        elif kind in ('WHITESPACE', 'COMMENT_SINGLE', 'COMMENT_MULTI'):
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f"Unexpected character {value!r} at line {line_num}")
        else:
            tokens.append({
                'TYPE': kind, 
                'VALUE': value, 
                'LINE': line_num, 
                'COLUMN': column
            })
    
    tokens.append({'TYPE': 'EOF', 'VALUE': 'EOF', 'LINE': line_num, 'COLUMN': 0})
    return tokens

def write_tokens(tokens, filename='lexical_output.txt'):
    """Write tokens to file."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Lexical Analyzer's Output:\n\n")
        f.write(f"{'TOKEN TYPE':<25} {'LEXEME':<20} {'LINE':<6} {'COLUMN':<6}\n")
        f.write("-" * 65 + "\n")
        for t in tokens:
            f.write(f"{t['TYPE']:<25} {t['VALUE']:<20} {t['LINE']:<6} {t['COLUMN']:<6}\n")
    print("Lexical Analysis Done - Output written to", filename)