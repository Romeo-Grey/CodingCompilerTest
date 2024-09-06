x = input("Universal >")
currentToken = ""
tokens = [
    "print",
    "(",
    ")"
]



TokenList = []
inside_string = False

for i, letter in enumerate(x):
    if inside_string:
        currentToken += letter
        if letter == "\"":
            inside_string = False
            TokenList.append(currentToken)
            currentToken = ""
        continue

    if letter == "\"":
        inside_string = True
        currentToken += letter
        continue

    currentToken += letter

    if currentToken in tokens:
        TokenList.append(currentToken)
        currentToken = ""


def printcpp(TokenLine):  # Turn python print function into c++ format.
    printstring = ""
    for token in TokenLine:
        if token[0] == "\"" and token[-1] == "\"":
            return f"std::cout << \"{token[1:-1]}\";"
    return f"std::cout << \"{printstring}\";"


def PyToCPP(TokenLine):
    if TokenLine[0] == "print":
        print(printcpp(TokenLine))

    return 0


PyToCPP(TokenList)
