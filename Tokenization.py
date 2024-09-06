import re
import argparse

conversion_tokens = [
    {
        'python': 'print',
        'cpp': 'cout <<'
    }
]


def CppConvert(line, tokens):
    # Convert a single line of Python code to C++ code
    for token in tokens:
        python_token = token['python']
        cpp_token = token['cpp']

        # Regex pattern to match the Python token
        pattern = re.compile(rf'{python_token}\((.*?)\)')

        # Function to replace Python token with C++ token
        def replace_token(match):
            content = match.group(1)

            parts = content.split(',')
            cpp_parts = [part.strip() for part in parts]

            # Join parts with ' << ' and add a semicolon
            cpp_content = ' << '.join(cpp_parts)
            return f'{cpp_token} {cpp_content};'

        # Replace the token in the provided line
        cpp_line = pattern.sub(replace_token, line)
        return cpp_line

    # If no replacement occurs, return the original line
    return f"Error {line} could not be turned into C++ because of limited tokenization"


def convert_file(input_file, output_file, tokens):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()
        cpp_lines = [CppConvert(line.strip(), tokens) for line in lines]

    with open(output_file, 'w') as outfile:
        outfile.write("#include <iostream>\nusing namespace std;\n\nint main() {\n")
        outfile.write('\n'.join(cpp_lines))
        outfile.write('\n}\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str)
    parser.add_argument('output_file', type=str)
    args = parser.parse_args()
    convert_file(args.input_file, args.output_file, conversion_tokens)
    if __name__ == '__main__':
        main()
