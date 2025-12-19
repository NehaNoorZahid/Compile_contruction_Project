

class SyntaxTreeNode:
    def __init__(self, value, token_value=None):
        self.value = value
        self.token_value = token_value  # Store the token value if provided
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def pretty_print(self, level=0):
        # Print the current node with its token value if it exists
        if self.token_value:
            ret = " " * (level * 4) + f"{self.value} (Value: {self.token_value})\n"  # 4 spaces per level for indentation
        else:
            ret = " " * (level * 4) + f"{self.value}\n"  # 4 spaces per level for indentation
        # Print all child nodes
        for child in self.children:
            ret += child.pretty_print(level + 1)  # Increment level for child nodes
        return ret


def read_tokens_from_file(file_path):
    tokens = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) >= 2:
                    token_type = parts[0]
                    value = parts[1]
                    line_no = int(parts[2]) if len(parts) == 3 else 0
                    tokens.append((token_type, value, line_no))
        tokens.append(("$", "$", 0))  # End-of-file marker
    except Exception as e:
        print(f"Error reading file: {e}")
    return tokens


# Define the parsing table based on your grammar
parsing_table = {
    # Top-level rules for statements
    ("S", "VARIABLE_KEY"): ["VARIABLE_DEF", "STATEMENT"],
    ("S", "PRINT"): ["STATEMENTS", "STATEMENT"],
    ("S", "FUNCTION"): ["FUNCTION_DEF", "FUNCTION_CALL","STATEMENTS" or "FUNCTION_DEF"],
    ("S", "IF"): ["STATEMENTS", "STATEMENT"],
    ("S", "WHILE"): ["STATEMENTS", "STATEMENT"],
    ("S", "FOR"): ["STATEMENTS", "STATEMENT"],
    ("S", "UTILITY_KEYWORDS"): ["STATEMENTS", "STATEMENT"],
    ("S", "IDENTIFIER"): ["STATEMENTS", "STATEMENT"],
    ("S", "}"): ["ε"],  # End of statements in a block

    # Rules for statements block and continuation
    ("STATEMENTS", "VARIABLE_KEY"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS", "UTILITY_KEYWORDS"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS", "IF"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS", "WHILE"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS", "FOR"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS", "PRINT"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS", "IDENTIFIER"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS", "FUNCTION"): ["FUNCTION_DEF", "FUNCTION_CALL","STATEMENTS"],
    ("STATEMENTS", "}"): ["ε"], 
    ("STATEMENTS", "$"): ["ε"], # End of statements block

    # Continue with more statements
    ("STATEMENTS_TAIL", "VARIABLE_KEY"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS_TAIL", "UTILITY_KEYWORDS"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS_TAIL", "IF"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS_TAIL", "WHILE"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS_TAIL", "FOR"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS_TAIL", "PRINT"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS_TAIL", "IDENTIFIER"): ["STATEMENT", "STATEMENTS_TAIL"],
    ("STATEMENTS_TAIL", "}"): ["ε"],  # End of statements tail
    ("STATEMENTS_TAIL", "$"): ["ε"],  # End of input

    # Rules for a single statement
    ("STATEMENT", "VARIABLE_KEY"): ["VARIABLE_DEF","STATEMENT"],
    ("STATEMENT", "UTILITY_KEYWORDS"): ["UTILITY_CALL"],
    ("STATEMENT", "IF"): ["IF_STATEMENT"],
    ("STATEMENT", "WHILE"): ["WHILE_LOOP"],
    ("STATEMENT", "PRINT"): ["PRINT", "(", "EXPRESSION", ")", ";"],
    ("STATEMENT", "FOR"): ["FOR_LOOP"],
    ("STATEMENT", "IDENTIFIER"): ["IDENTIFIER", "(", "EXPRESSION", ")", ";"],
    ("STATEMENT","MDM"):["*"],
    ("STATEMENT", "$"): ["ε"],  
   
    ("FUNCTION_DEF", "FUNCTION"): ["FUNCTION", "IDENTIFIER", "(","PARAMS", ")", "{", "STATEMENTS", "}"],
    ("PARAMS", ")"): ["ε"],  
    ("PARAMS", "IDENTIFIER"): ["IDENTIFIER", "PARAMS_TAIL"],  # At least one parameter
    ("PARAMS_TAIL", "IDENTIFIER"): ["IDENTIFIER", "PARAMS_TAIL"],  # Additional parameters
    ("PARAMS_TAIL", ","): [",", "PARAMS"],  # Comma to separate parameters
    ("PARAMS_TAIL", ")"): ["ε"], 
    ("FUNCTION_CALL", "IDENTIFIER"): ["CALL_FUNCTION"],
    ("CALL_FUNCTION", "IDENTIFIER"): ["IDENTIFIER","(","ARGUMENTS",")"],
    ("FUNCTION_CALL", "$"): ["ε"],
    ("ARGUMENTS", "IDENTIFIER"): ["IDENTIFIER","ARGUMENT_TAIL"], 
    ("ARGUMENT_TAIL", "IDENTIFIER"): ["IDENTIFIER", "ARGUMENT_TAIL"],  # Additional parameters
    ("ARGUMENT_TAIL", ","): [",", "ARGUMENT"], 
    ("ARGUMENTS", ")"): ["ε"],       
    # ("FUNCTION_CALL", "IDENTIFIER"): ["IDENTIFIER", "(", "ARGUMENTS", ")"],

    # Rules for if-else statement
    ("IF_STATEMENT", "IF"): ["IF", "(", "CONDITION", ")", "{", "STATEMENTS", "}", "ELSE_STATEMENT"],

    # Rules for else statement
    ("ELSE_STATEMENT", "ELSE"): ["ELSE", "{", "STATEMENTS", "}"],
    ("ELSE_STATEMENT", "}"): ["ε"],  # No else case

    # Rules for while loop
    ("WHILE_LOOP", "WHILE"): ["WHILE", "(", "CONDITION", ")", "{", "STATEMENTS", "}"],

    # Rules for for loop
    ("FOR_LOOP", "FOR"): ["FOR", "(", "VARIABLE_DEF", "CONDITION", ";", "UPDATE", ")", "{", "STATEMENTS", "}"],

    # Rules for variable definition and assignment
    ("VARIABLE_DEF", "VARIABLE_KEY"): ["VARIABLE_KEY", "IDENTIFIER", "VARIABLE_TAIL", ";"],
    ("VARIABLE_TAIL", ","): [",", "IDENTIFIER", "VARIABLE_TAIL"],  # Handle additional variables
    ("VARIABLE_TAIL", "AP"): ["AP", "EXPRESSION"],  # Handle assignment to a single variable
    ("VARIABLE_TAIL", ";"): ["ε"],  # No additional variable or assignment (ends with a semicolon)

    ("VARIABLE_ASSIGN", "IDENTIFIER"): ["IDENTIFIER", "AP", "EXPRESSION", ";"],
    
    # Rules for utility calls (e.g., custom keywords or functions)
    ("UTILITY_CALL", "UTILITY_KEYWORDS"): ["IDENTIFIER", "(", "EXPRESSION", ")", ";"],

    # Rules for expressions
    ("EXPRESSION", "IDENTIFIER"): ["IDENTIFIER","EXPRESSION"],
    ("EXPRESSION", "INT_DATATYPE"): ["INT_DATATYPE"],
    ("EXPRESSION", "STRING_CONST"): ["STRING_CONST","EXPRESSION"],
    ("EXPRESSION", "("): ["(", "EXPRESSION", ")"],
    ("EXPRESSION", "AS"): ["EXPRESSION", "AS", "EXPRESSION"],
    ("EXPRESSION", "EXPRESSION"): ["EXPRESSION", "OPERATOR", "EXPRESSION"],
    ("EXPRESSION", "$"): ["ε"],
    ("EXPRESSION", ","): [",","EXPRESSION"],
    ("EXPRESSION", "MDM"): ["MDM", "EXPRESSION"],
    ("EXPRESSION", ")"): ["ε"],


    # Handling operators and arithmetic operators
    ("AS", "+"): ["+"],
    ("AS", "-"): ["-"],
    ("MDM", "*"): ["*"],
    ("MDM", "/"): ["/"],
    ("MDM", "%"): ["%"],
    ("INC_DEC","++"):["++"],
    ("INC_DEC","--"):["--"],

    # Rules for condition checks
    ("CONDITION", "IDENTIFIER"): ["IDENTIFIER", "ROP", "EXPRESSION"],
    ("CONDITION", "INT_DATATYPE"): ["EXPRESSION", "ROP", "EXPRESSION"],

    # Rules for update statements in loops
    ("UPDATE", "IDENTIFIER"): ["IDENTIFIER","INC_DEC"],
    ("UPDATE", "++"): ["++","IDENTIFIER",";"],
    ("UPDATE", "--"): ["--","IDENTIFIER",";"],

    # Handling terminal tokens (mapping from lexer)
    ("PRINT", "show"): ["show"],  # Map "show" to PRINT token in lexer
    ("VARIABLE_KEY"): ["let"],  # Map "let" to VARIABLE_KEY token in lexer
    ("AP", "="): ["="],  # Map "=" to AP token in lexer
    ("UTILITY_KEYWORDS", "UTILITY_KEYWORDS"): ["custom_keyword"],  
}

def ll1_parser(tokens):
    stack = ["$", "S"]
    index = 0
    current_token = tokens[index][0]  # Token type

    # Create the root of the syntax tree
    root = SyntaxTreeNode("S")
    node_stack = [root]

    while stack:
        top = stack[-1]
        print(f"Stack: {stack}, Current Token: {current_token}")  # Debugging: print stack and current token

        # Check for end of parsing
        if top == "$" and current_token == "$":
            print("Parsing successful!")
            break

        # Expand non-terminal using the parsing table rule
        elif (top, current_token) in parsing_table:
            stack.pop()
            rule = parsing_table[(top, current_token)]

            # Print the expanded rule immediately after starting from 'S'
            if top == "S":
                print(f"Expanding {top}: {rule} due to current token '{current_token}'")

            # Debugging: Print the rule being expanded
            print(f"Expanding: {top} with rule: {rule}")

            current_node = node_stack.pop()

            # Push children onto stack in reverse order to maintain the correct order in the tree
            for symbol in reversed(rule):
                if symbol != "ε":  # Handle epsilon transitions by skipping
                    stack.append(symbol)
                    new_child = SyntaxTreeNode(symbol)
                    current_node.add_child(new_child)
                    node_stack.append(new_child)

        # Match terminal symbol
        elif top == current_token:
            token_value = tokens[index][1]  # Get the actual token value
            print(f"Matching: {top} with value '{token_value}'")  # Debugging: print matched token
            stack.pop()
            index += 1
            current_token = tokens[index][0] if index < len(tokens) else "$"
            
            # Update the current node with the matched token value
            current_node = node_stack.pop()
            current_node.value = f"{top}"  # Set the value to the symbol
            current_node.token_value = token_value  # Store the token value in the node

        else:
            print(f"Parsing error: stack top {top} does not match current token {current_token}")
            break

    return root


def save_to_file(tree_string, file_path):
    try:
        with open(file_path, 'w') as file:
            file.write(tree_string)
        print(f"Syntax tree saved to {file_path}")
    except Exception as e:
        print(f"Error saving to file: {e}")


if __name__ == "__main__":
    tokens = read_tokens_from_file("token.txt")
    syntax_tree = ll1_parser(tokens)

    # Pretty print the syntax tree
    pretty_tree = syntax_tree.pretty_print()
    print(pretty_tree)

    # Save the pretty-printed tree to a file
    save_to_file(pretty_tree, "syntaxOutput.txt")

