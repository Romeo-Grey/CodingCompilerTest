import re
from collections import namedtuple

# Define a Token class to represent a token
Token = namedtuple('Token', ['type', 'value', 'position'])

# Define the set of keywords in Python
KEYWORDS = {
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
    'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in',
    'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield'
}

# Token specifications using regular expressions
TOKEN_SPECIFICATION = [
    ('NUMBER', r'\d+(\.\d*)?'),  # Integer or decimal number
    ('STRING', r'\".*?\"|\'.*?\''),  # String literals
    ('ASSIGN', r'='),  # Assignment operator
    ('END', r';'),  # Statement terminator
    ('ID', r'[A-Za-z_]\w*'),  # Identifiers (variables, functions)
    ('OP', r'[+\-*/%]'),  # Arithmetic operators
    ('CMP', r'==|!=|<=|>=|<|>'),  # Comparison operators
    ('LOGICAL', r'and|or|not'),  # Logical operators
    ('PAREN', r'[\(\)]'),  # Parentheses
    ('BRACE', r'[\{\}]'),  # Braces
    ('BRACKET', r'[\[\]]'),  # Brackets
    ('COMMA', r','),  # Comma
    ('DOT', r'\.'),  # Dot for member access
    ('COLON', r':'),  # Colon
    ('COMMENT', r'#.*'),  # Comment
    ('SKIP', r'[ \t]+'),  # Skip over spaces and tabs
    ('NEWLINE', r'\n'),  # New line
    ('MISMATCH', r'.'),  # Any other character
]

# Build the regular expression for all tokens
token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_SPECIFICATION)


def tokenize(code):
    tokens = []
    position = 0

    # Scan the code using the compiled regex
    for match in re.finditer(token_regex, code):
        token_type = match.lastgroup
        token_value = match.group(token_type)

        # Reclassify identifiers as keywords if they match a keyword
        if token_type == 'ID' and token_value in KEYWORDS:
            token_type = 'KEYWORD'

        # Convert number strings to integers or floats
        if token_type == 'NUMBER':
            token_value = float(token_value) if '.' in token_value else int(token_value)

        # Skip whitespace and comments
        if token_type == 'SKIP' or token_type == 'COMMENT':
            continue
        elif token_type == 'MISMATCH':
            raise SyntaxError(f"Unexpected character: {token_value}")

        tokens.append(Token(token_type, token_value, position))
        position += len(str(token_value))

    return tokens


# Example code to tokenize
code = """
if (x == 10) and (y != 20):
    z = x + y;
    print("Hello, world!")  # This is a comment
"""

tokens = tokenize(code)
for token in tokens:
    print(token)
