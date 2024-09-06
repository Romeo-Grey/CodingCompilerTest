import re
import argparse

conversion_tokens = [
    {
        'python': 'print',
        'cpp': 'cout <<'
    }
]


def CppConvert(line, tokens):
    for token in tokens:
        python_token = token['python']
        cpp_token = token['cpp']

        pattern = re.compile(rf'{python_token}\((.*?)\)')

        def replace_token(match):
            content = match.group(1)

            parts = content.split(',')
            cpp_parts = [part.strip() for part in parts]

            cpp_content = ' << '.join(cpp_parts)
            return f'{cpp_token} {cpp_content};'

        line = pattern.sub(replace_token, line)

    return line


def convert_file(input_file, output_file, tokens):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()
        cpp_lines = [CppConvert(line.strip(), tokens) for line in lines]

    with open(output_file, 'w') as outfile:
        outfile.write("#include <iostream>\nusing namespace std;\n\nint main() {\n")
        outfile.write('\n'.join(f"    {line}" for line in cpp_lines))
        outfile.write('\n    return 0;\n}\n')


def main():
    parser = argparse.ArgumentParser()
    # Uncomment the following lines to use command-line arguments
    parser.add_argument('input_file', type=str)
    parser.add_argument('output_file', type=str)
    args = parser.parse_args()

    convert_file("PythonFileToConvert.py", "CPPFile.cpp", conversion_tokens)


if __name__ == '__main__':
    main()
