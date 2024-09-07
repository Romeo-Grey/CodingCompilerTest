import re
from collections import namedtuple

# Define a Token class to represent a token
Token = namedtuple('Token', ['type', 'value', 'position'])


# Define node classes for the AST
class NumberNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberNode({self.value})"


class VariableNode:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"VariableNode({self.name})"


class StringNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"StringNode({self.value})"


class BinOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinOpNode({self.left}, {self.op}, {self.right})"


class IfNode:
    def __init__(self, condition, true_branch, false_branch):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __repr__(self):
        return f"IfNode({self.condition}, {self.true_branch}, {self.false_branch})"


class AssignmentNode:
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

    def __repr__(self):
        return f"AssignmentNode({self.variable}, {self.value})"


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

    for match in re.finditer(token_regex, code):
        token_type = match.lastgroup
        token_value = match.group(token_type)

        if token_type == 'NUMBER':
            token_value = float(token_value) if '.' in token_value else int(token_value)

        if token_type == 'ID' and token_value in {'if', 'else', 'while'}:
            token_type = 'KEYWORD'  # Reclassify keywords if needed

        if token_type == 'SKIP':  # Skip whitespace
            continue
        elif token_type == 'MISMATCH':
            raise SyntaxError(f"Unexpected character: {token_value}")

        # Append token with its type and value
        tokens.append(Token(token_type, token_value, position))

        # Update position correctly
        position += len(token_value)

    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.index = -1
        self.advance()

    def advance(self):
        """Advance to the next token."""
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def expect(self, token_type):
        """Check if the current token matches the expected type."""
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token.type}")

    def parse(self):
        """Parse the tokens into an AST."""
        return self.program()

    def program(self):
        """Parse a sequence of statements."""
        statements = []
        while self.current_token:
            if self.current_token.type == 'KEYWORD' and self.current_token.value == 'if':
                statements.append(self.if_statement())
            else:
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
            # Handle new lines between statements
            while self.current_token and self.current_token.type == 'NEWLINE':
                self.advance()
        return statements

    def statement(self):
        """Parse a statement. Here, we'll handle basic assignments and expressions."""
        if self.current_token and self.current_token.type == 'ID' and self.tokens[self.index + 1].type == 'ASSIGN':
            var_name = self.current_token.value
            self.advance()  # Move past the variable name
            self.expect('ASSIGN')  # Expect '='
            expr = self.expression()
            self.expect('END')  # Expect ';'
            return AssignmentNode(var_name, expr)
        elif self.current_token and self.current_token.type == 'KEYWORD':
            # Add handling for other keywords if necessary
            raise SyntaxError(f"Unexpected keyword: {self.current_token.value}")
        else:
            return self.expression()

    def if_statement(self):
        """Parse an if statement like `if x == 10: ... else: ...`."""
        self.expect('KEYWORD')  # Expect 'if'

        # Parse the condition, which is an expression
        condition = self.expression()

        # After the condition, we expect a colon, not an assignment
        self.expect('COLON')  # Expect ':'

        # Parse the true branch (statements inside the block)
        true_branch = self.block()

        # Optionally parse an else block
        false_branch = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'else':
            self.expect('KEYWORD')  # Expect 'else'
            self.expect('COLON')  # Expect ':'
            false_branch = self.block()  # Parse the false branch

        return IfNode(condition, true_branch, false_branch)

    def block(self):
        """Parse a block of statements."""
        statements = []
        while self.current_token and self.current_token.type not in {'KEYWORD', 'NEWLINE'}:
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
            # Skip any new lines between statements
            while self.current_token and self.current_token.type == 'NEWLINE':
                self.advance()
        return statements

    def expression(self):
        """Parse an expression."""
        node = self.term()

        # Handle comparison operators (==, !=, <=, >=, <, >)
        while self.current_token and self.current_token.type == 'CMP':
            op = self.current_token.value
            self.advance()  # Move past the comparison operator
            right = self.term()  # Parse the right-hand side of the comparison
            node = BinOpNode(node, op, right)  # Construct a binary operation node

        return node

    def term(self):
        """Parse a term (numbers and variables)."""
        while self.current_token and self.current_token.type == 'NEWLINE':
            self.advance()

        token = self.current_token
        if token.type == 'NUMBER':
            self.advance()
            return NumberNode(token.value)
        elif token.type == 'ID':
            self.advance()
            return VariableNode(token.value)
        elif token.type == 'STRING':
            self.advance()
            return StringNode(token.value)
        elif token.type == 'PAREN' and token.value == '(':
            self.advance()
            expr = self.expression()
            self.expect('PAREN')  # Expect ')'
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {token}")


# Example code to tokenize and parse
code = """
if x == 10:
    y = "Hello";
else:
    y = 'World';
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()

# Output the AST
for node in ast:
    print(node)
