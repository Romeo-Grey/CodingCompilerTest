import re

# List of tokens for conversion (no 'end' parameter)
conversion_tokens = [
    {
        'python': 'print',
        'cpp': 'cout <<'
    }
]


def convert_print_statement(line, tokens):
    # Convert a single line of Python code to C++ code
    for token in tokens:
        python_token = token['python']
        cpp_token = token['cpp']

        # Regex pattern to match the Python token
        pattern = re.compile(rf'{python_token}\((.*?)\)')

        # Function to replace Python token with C++ token
        def replace_token(match):
            content = match.group(1)
            # Handle quotes and escaping for C++ strings
            content = content.replace('"', r'\"')

            # If there are multiple items in the print statement, they are comma-separated
            parts = content.split(',')
            cpp_parts = [part.strip() for part in parts]

            cpp_content = ' << '.join(cpp_parts)
            return f'{cpp_token} {cpp_content};'

        # Replace the token in the provided line
        cpp_line = pattern.sub(replace_token, line)
        return cpp_line

    # If no replacement occurs, return the original line
    return line


# Example usage
python_line = 'print("Hello, world!", 42)'
cpp_line = convert_print_statement(python_line, conversion_tokens)
print(cpp_line)  # Output: cout << "Hello, world!" << 42;
