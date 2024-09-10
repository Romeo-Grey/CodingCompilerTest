import re
from collections import namedtuple


# Define a Token class to represent a token
class Token:
    def __init__(self, token_type, value, position):
        self.type = token_type
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token(type='{self.type}', value={self.value!r}, position={self.position})"


# Define node classes for the AST
class NumberNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberNode({self.value})"


class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class ForNode:
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def __repr__(self):
        return f"ForNode({self.init}, {self.condition}, {self.update}, {self.body})"


def __repr__(self):
    return f"WhileNode({self.condition}, {self.body})"


class PrintNode:
    def __init__(self, expression):
        self.expression = expression


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
        self.variable = variable  # This should be a VariableNode object
        self.value = value

    def __repr__(self):
        return f"AssignmentNode({self.variable}, {self.value})"


# Token specifications using regular expressions
TOKEN_SPECIFICATION = [
    ('NUMBER', r'\d+(\.\d*)?'),  # Integer or decimal number
    ('STRING', r'\".*?\"|\'.*?\''),
    ('PRINT', r'print'),
    ('KEYWORD', r'if|else|then'),
    ('CMP', r'==|!=|<=|>=|<|>'),  # Comparison operators
    ('ASSIGN', r'='),  # Assignment operator
    ('END', r';'),  # Statement terminator
    ('ID', r'[A-Za-z_]\w*'),  # Identifiers
    ('OP', r'[+\-*/%]'),  # Arithmetic operators
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
        position += len(str(token_value))

    # Print tokens for debugging
    print("Tokens:", tokens)

    return tokens


class ProgramNode:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode({self.statements})"


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
            raise SyntaxError(f"Expected {token_type}, got {self.current_token.type if self.current_token else 'EOF'}")

    def parse(self):
        """Parse the tokens into an AST."""
        return self.program()

    def program(self):
        """Parse a sequence of statements."""
        statements = []
        while self.current_token:
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
            while self.current_token and self.current_token.type == 'NEWLINE':
                self.advance()
        return statements

    def statement(self):
        if self.current_token and self.current_token.type == 'ID':
            var_name = self.current_token.value
            self.advance()
            if self.current_token and self.current_token.type == 'ASSIGN':
                self.advance()
                expr = self.expression()
                return AssignmentNode(var_name, expr)
            else:
                return VariableNode(var_name)
        elif self.current_token and self.current_token.type == 'PRINT':
            return self.print_statement()
        elif self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'if':
            return self.if_statement()
        return self.expression()

    def print_statement(self):
        self.expect('PRINT')
        expr = self.expression()
        return PrintNode(expr)

    def generate_print(self, node):
        value = self.generate(node.expression)
        print(f"Debug: Generating PRINT instruction for {value}")
        self.instructions.append(f"PRINT {value}")

    def if_statement(self):
        self.expect('KEYWORD')  # Expect 'if'
        condition = self.condition()
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'then':
            self.advance()  # Skip 'then' keyword
        true_branch = self.block()
        false_branch = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'else':
            self.advance()  # Skip 'else' keyword
            false_branch = self.block()
        return IfNode(condition, true_branch, false_branch)

    def condition(self):
        """Parse a condition (e.g., `x == 10` or just `x`)."""
        left = self.expression()

        if self.current_token and self.current_token.type == 'CMP':
            op = self.current_token.value
            self.advance()  # Move past the comparison operator
            right = self.expression()
            return BinOpNode(left, op, right)
        else:
            # If there's no comparison operator, return the expression as is
            return left

    def block(self):
        """Parse a block of statements."""
        statements = []
        while self.current_token and self.current_token.type not in {'KEYWORD', 'NEWLINE', 'END'}:
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
            while self.current_token and self.current_token.type == 'NEWLINE':
                self.advance()
        return statements

    def expression(self):
        """Parse an expression."""
        node = self.term()

        while self.current_token and self.current_token.type in {'OP', 'CMP'}:
            op = self.current_token.value
            self.advance()
            right = self.term()
            node = BinOpNode(node, op, right)

        return node

    def logical_expression(self):
        """Parse a logical expression like 'x and y'."""
        left = self.term()
        op = self.current_token.value
        self.advance()  # Move past the logical operator
        right = self.term()
        return BinOpNode(left, op, right)

    def comparison_expression(self):
        """Parse a comparison expression like 'x == y'."""
        left = self.term()
        op = self.current_token.value
        self.advance()  # Move past the comparison operator
        right = self.term()
        return BinOpNode(left, op, right)

    def term(self):
        """Parse a term (numbers, variables, and strings)."""
        while self.current_token and self.current_token.type == 'NEWLINE':
            self.advance()

        token = self.current_token

        if token.type == 'NUMBER':
            self.advance()
            return NumberNode(token.value)
        elif token.type == 'ID':
            var_name = token.value
            self.advance()
            if self.current_token and self.current_token.type == 'ASSIGN':
                self.advance()
                value = self.expression()
                return AssignmentNode(var_name, value)
            else:
                return VariableNode(var_name)
        elif token.type == 'STRING':
            self.advance()
            return StringNode(token.value)
        elif token.type == 'PAREN' and token.value == '(':
            self.advance()
            expr = self.expression()
            self.expect('PAREN')
            return expr
        elif token.type == 'LOGICAL':
            return self.logical_expression()
        elif token.type == 'CMP':
            return self.comparison_expression()
        elif token.type == 'BRACKET' and token.value == '[':
            self.advance()
            expr = self.expression()
            self.expect('BRACKET')
            return expr
        elif token.type == 'BRACE' and token.value == '{':
            self.advance()
            statements = self.block()
            self.expect('BRACE')
            return statements
        elif token.type == 'KEYWORD' and token.value == 'else':
            # Ignore 'else' keyword when encountered here
            self.advance()
            return None
        else:
            raise SyntaxError(f"Unexpected token in term: {token}")


class SymbolTable:
    def __init__(self):
        self.variables = {}
        self.parent = None

    def set(self, name, value_type):
        if name in self.variables:
            raise Exception(f"Variable '{name}' already declared.")
        self.variables[name] = value_type

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise Exception(f"Variable '{name}' not found.")

    def __repr__(self):
        return f"SymbolTable(variables={self.variables})"


class SemanticAnalyzer:
    def __init__(self):
        self.variables = {}

    def analyze(self, node):
        """Perform semantic analysis on the AST."""
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.analyze(stmt)
        elif isinstance(node, AssignmentNode):
            self.analyze_assignment(node)
        elif isinstance(node, BinOpNode):
            self.analyze_binop(node)
        elif isinstance(node, WhileNode):
            self.analyze_while(node)
        elif isinstance(node, ForNode):
            self.analyze_for(node)

        elif isinstance(node, IfNode):
            self.analyze_if(node)
        elif isinstance(node, VariableNode):
            self.analyze_variable(node)
        elif isinstance(node, NumberNode):
            return
        elif isinstance(node, StringNode):
            return
        else:
            raise Exception(f"Unknown node type: {type(node)}")

    def analyze_assignment(self, node):
        """Check that the assigned value is valid."""
        var_name = node.variable  # Corrected from 'node.var_name' to 'node.variable'
        expr = node.value  # Corrected from 'node.expr' to 'node.value'

        # Analyze the expression part
        self.analyze(expr)

        # Determine the type of the assigned value
        if isinstance(expr, NumberNode):
            self.variables[var_name] = 'number'
            print(f"Assigning number to variable '{var_name}'")
        elif isinstance(expr, StringNode):
            self.variables[var_name] = 'string'
            print(f"Assigning string to variable '{var_name}'")
        elif isinstance(expr, BinOpNode):
            # Determine the type of the binary operation result
            left_type = self.get_expression_type(expr.left)
            right_type = self.get_expression_type(expr.right)
            if left_type != right_type:
                raise Exception(f"Type mismatch in binary operation: {left_type} {expr.op} {right_type}")
            self.variables[var_name] = left_type
            print(f"Assigning binary operation result to variable '{var_name}'")
        else:
            print(f"Assigning expression to variable '{var_name}'")

    def get_expression_type(self, expr):
        """Get the type of the expression."""
        if isinstance(expr, VariableNode):
            return self.variables.get(expr.name, 'unknown')
        elif isinstance(expr, NumberNode):
            return 'number'
        elif isinstance(expr, StringNode):
            return 'string'
        else:
            return 'unknown'

    def analyze_binop(self, node):
        """Check that both sides of the binary operation are compatible."""
        left = node.left
        right = node.right
        op = node.op

        # Analyze both sides
        self.analyze(left)
        self.analyze(right)

        # Check types for simple compatibility
        if isinstance(left, VariableNode) and left.name in self.variables:
            left_type = self.variables[left.name]
        elif isinstance(left, NumberNode):
            left_type = 'number'
        elif isinstance(left, StringNode):
            left_type = 'string'
        else:
            left_type = 'unknown'

        if isinstance(right, VariableNode) and right.name in self.variables:
            right_type = self.variables[right.name]
        elif isinstance(right, NumberNode):
            right_type = 'number'
        elif isinstance(right, StringNode):
            right_type = 'string'
        else:
            right_type = 'unknown'

        if left_type != right_type:
            raise Exception(f"Type mismatch in binary operation: {left_type} {op} {right_type}")
        else:
            print(f"Binary operation '{op}' between {left_type} and {right_type} is valid.")

    def analyze_if(self, node):
        """Analyze the condition and the branches of the if statement."""
        print("Analyzing if statement")
        self.analyze(node.condition)
        print("Analyzing true branch")
        self.analyze(node.true_branch)
        if node.false_branch:
            print("Analyzing false branch")
            self.analyze(node.false_branch)

    def analyze_while(self, node):
        self.analyze(node.condition)
        self.analyze(node.body)

    def analyze_for(self, node):
        self.analyze(node.init)
        self.analyze(node.condition)
        self.analyze(node.update)
        self.analyze(node.body)

    def analyze_variable(self, node):
        """Check that the variable is declared."""
        name = node.name  # Corrected from 'node.name' to 'node.name'

        if name not in self.variables:
            raise NameError(f"Variable '{name}' is not defined")
        else:
            print(f"Variable '{name}' is declared and used correctly.")


class IntermediateCodeGenerator:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.instructions = []

    def new_temp(self):
        self.temp_count += 1
        return f"T{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def generate(self, node):
        if isinstance(node, list):
            for stmt in node:
                self.generate(stmt)
        elif isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.generate(stmt)
        elif isinstance(node, AssignmentNode):
            self.generate_assignment(node)
        elif isinstance(node, BinOpNode):
            return self.generate_binop(node)
        elif isinstance(node, NumberNode):
            return str(node.value)
        elif isinstance(node, PrintNode):
            self.generate_print(node)
        elif isinstance(node, IfNode):
            self.generate_if(node)
        elif isinstance(node, VariableNode):
            return node.name
        else:
            raise Exception(f"Unknown node type: {type(node)}")

    def generate_assignment(self, node):
        value = self.generate(node.value)
        self.instructions.append(f"STORE {value} {node.variable}")

    def generate_binop(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)
        result = self.new_temp()
        self.instructions.append(f"{node.op} {left} {right} {result}")
        return result

    def generate_print(self, node):
        value = self.generate(node.expression)
        self.instructions.append(f"PRINT {value}")

    def generate_if(self, node):
        condition = self.generate(node.condition)
        true_label = self.new_label()
        false_label = self.new_label()
        end_label = self.new_label()

        self.instructions.append(f"IF {condition} GOTO {true_label}")
        self.instructions.append(f"GOTO {false_label}")

        self.instructions.append(f"{true_label}:")
        self.generate(node.true_branch)
        self.instructions.append(f"GOTO {end_label}")

        self.instructions.append(f"{false_label}:")
        if node.false_branch:
            self.generate(node.false_branch)

        self.instructions.append(f"{end_label}:")

    def get_code(self):
        return "\n".join(self.instructions)


code = """
x = 5
y = x + 10
print y
if x < 10 then
    print x
else
    print y

"""

# Step 1: Tokenize the input code
tokens = tokenize(code)

# Check if tokens are generated correctly
print("Tokens:", tokens)

# Step 2: Parse the tokens into an AST
parser = Parser(tokens)  # Ensure your Parser class is defined and works with tokens
ast = parser.parse()  # This should return the AST, which is stored in `ast`

# Check if the AST is generated correctly
print("\nGenerated AST:")
for node in ast:
    print(node)

# Step 3: Generate intermediate code from the AST
ir_gen = IntermediateCodeGenerator()
for node in ast:
    ir_gen.generate(node)

# Step 4: Print the intermediate code
print("\nIntermediate Code:")
print(ir_gen.get_code())
