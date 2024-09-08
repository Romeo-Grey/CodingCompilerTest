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
    ('STRING', r'\".*?\"|\'.*?\''),
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
        """Parse a statement."""
        if self.current_token and self.current_token.type == 'ID':
            var_name = self.current_token.value
            self.advance()  # Move past variable ID

            if self.current_token and self.current_token.type == 'ASSIGN':
                self.advance()  # Move past '='
                expr = self.expression()
                if self.current_token and self.current_token.type == 'END':
                    self.advance()  # Move past ';'
                return AssignmentNode(var_name, expr)
            else:
                # If not an assignment, it might be an expression or an error
                return VariableNode(var_name)

        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'if':
            return self.if_statement()

        # If no specific statement type matched, handle expressions directly
        return self.expression()

    def if_statement(self):
        """Parse an if statement like `if x == 10: ... else: ...`."""
        self.expect('KEYWORD')  # Expect 'if'

        # Parse the condition
        condition = self.condition()

        self.expect('COLON')  # Expect ':'

        # Parse the true branch
        true_branch = self.block()

        # Optionally parse an else block
        false_branch = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'else':
            self.expect('KEYWORD')  # Expect 'else'
            self.expect('COLON')  # Expect ':'
            false_branch = self.block()  # Parse the false branch

        return IfNode(condition, true_branch, false_branch)

    def condition(self):
        """Parse a condition (e.g., `x == 10`)."""
        left = self.expression()

        # Check for comparison operator
        if self.current_token.type == 'CMP':
            op = self.current_token.value
            self.advance()
        else:
            raise SyntaxError(
                f"Expected comparison operator, got {self.current_token.type if self.current_token else 'EOF'}")

        right = self.expression()
        return BinOpNode(left, op, right)

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

        # Handle binary operations (e.g., +, -, *, /)
        while self.current_token and self.current_token.type in {'OP', 'CMP'}:
            op = self.current_token.value
            self.advance()  # Move past the operator
            right = self.term()  # Parse the right-hand side
            node = BinOpNode(node, op, right)  # Construct a binary operation node

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
            # Check for assignment after variable
            var_name = token.value
            self.advance()  # Move past the variable ID
            if self.current_token and self.current_token.type == 'ASSIGN':
                self.advance()  # Move past '='
                value = self.expression()  # Get the value being assigned
                return AssignmentNode(var_name, value)  # Return an assignment node
            else:
                return VariableNode(var_name)  # If no assignment, it's just a variable
        elif token.type == 'STRING':
            self.advance()
            return StringNode(token.value)
        elif token.type == 'PAREN' and token.value == '(':
            self.advance()
            expr = self.expression()
            self.expect('PAREN')  # Expect ')'
            return expr
        elif token.type == 'LOGICAL':  # Handling logical operators like "and", "or", "not"
            self.advance()
            return self.logical_expression()  # Assuming there's a method for logical expressions
        elif token.type == 'CMP':  # Handling comparison operators like '==', '!=', etc.
            self.advance()
            return self.comparison_expression()  # Assuming a method for comparisons
        elif token.type == 'BRACKET' and token.value == '[':  # Handle array or list access
            self.advance()
            expr = self.expression()  # Parse expression within brackets
            self.expect('BRACKET')  # Expect closing ']'
            return expr
        elif token.type == 'BRACE' and token.value == '{':  # Handle block or dictionary-like structures
            self.advance()
            statements = self.block()  # Parse block inside braces
            self.expect('BRACE')  # Expect closing '}'
            return statements
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
        self.instructions = []

    def new_temp(self):
        """Generate a new temporary variable name."""
        self.temp_count += 1
        return f"T{self.temp_count}"

    def generate(self, node):
        """Generate intermediate code for the given AST node."""
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.generate(stmt)
        elif isinstance(node, AssignmentNode):
            self.generate_assignment(node)
        elif isinstance(node, BinOpNode):
            self.generate_binop(node)
        elif isinstance(node, NumberNode):
            pass  # Numbers are handled directly in operations
        elif isinstance(node, VariableNode):
            pass  # Variables are used directly in operations
        else:
            raise Exception(f"Unknown node type: {type(node)}")

    def generate_assignment(self, node):
        """Generate intermediate code for an assignment."""
        var_name = node.variable
        expr = node.value
        temp = self.new_temp()  # Create a temporary variable for the result

        # Generate intermediate code for the expression
        self.generate(expr)

        # Store the result of the expression into the variable
        self.instructions.append(f"STORE {temp} {var_name}")

    def generate_binop(self, node):
        """Generate intermediate code for a binary operation."""
        left = node.left
        right = node.right
        op = node.op

        # Create temporary variables for the operands and result
        temp1 = self.new_temp()
        temp2 = self.new_temp()
        result_temp = self.new_temp()

        # Generate code for the left operand
        self.generate(left)
        self.instructions.append(f"LOAD {left} {temp1}")

        # Generate code for the right operand
        self.generate(right)
        self.instructions.append(f"LOAD {right} {temp2}")

        # Generate code for the binary operation
        self.instructions.append(f"{op} {temp1} {temp2} {result_temp}")

        # Store the result in a temporary variable
        self.instructions.append(f"STORE {result_temp} {result_temp}")

    def get_temp_var_for_value(self, value_node):
        """Generate a temporary variable for a value node."""
        if isinstance(value_node, NumberNode):
            return f"NUM_{value_node.value}"
        elif isinstance(value_node, VariableNode):
            return f"VAR_{value_node.name}"
        raise Exception("Invalid node for temporary variable")

    def generate_temp_var(self):
        """Generate a new temporary variable name."""
        self.temp_count += 1
        return f"T{self.temp_count}"

    def get_code(self):
        """Return the generated intermediate code."""
        return "\n".join(self.instructions)


# Example usage
ir_gen = IntermediateCodeGenerator()
# Assuming `ast` is the Abstract Syntax Tree generated from the parser
ast = [
    AssignmentNode("x", NumberNode(5)),
    AssignmentNode("y", BinOpNode(VariableNode("x"), "+", NumberNode(10)))
]

# Generate intermediate code
for node in ast:
    ir_gen.generate(node)

# Print intermediate code
print("\nIntermediate Code:")
print(ir_gen.get_code())

# Example code to tokenize, parse, and analyze
# Tokenize the input code
code = """
x = 5
y = x + 10

"""

tokens = tokenize(code)  # Step 1: Tokenization
parser = Parser(tokens)  # Step 2: Parsing
ast = parser.parse()  # This generates the AST

# Print the AST for debugging
print("\nGenerated AST:")
for node in ast:
    print(node)

# Step 3: Run semantic analysis on the generated AST
semantic_analyzer = SemanticAnalyzer()
print("\nRunning semantic analysis...")
for node in ast:
    semantic_analyzer.analyze(node)
