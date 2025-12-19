class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children else []

    def print_tree(self, indent=0, node_number=1):
        # Check if the node value is one that generates a value
        if self.is_value_node():
            print(" " * indent + f"{node_number}: {self.value}")
            # Increment the node_number for child nodes
            for i, child in enumerate(self.children):
                # Each child gets a new node number based on its index
                child.print_tree(indent + 4, node_number + i + 1)
        else:
            print(" " * indent + self.value)
            # Print children without numbering for non-value nodes
            for child in self.children:
                child.print_tree(indent + 4)

    def is_value_node(self):
        # Define which node types generate values
        return self.value in ["IDENTIFIER", "NUMBER", "STRING", "EXPRESSION"]


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}  # Store variable types and other info
        self.errors = []

    def analyze(self, node):
        if node is None:
            return

        # Handle variable definitions (e.g., let a = 2;)
        if node.value == "VARIABLE_DEF":
            variable_name = node.children[1].value  # Assuming second child is the variable name
            if variable_name in self.symbol_table:
                self.errors.append(f"Error: Variable '{variable_name}' already defined.")
            else:
                self.symbol_table[variable_name] = "int"  # Assuming default type as 'int'

        # Handle variable assignments (e.g., a = 5;)
        elif node.value == "ASSIGNMENT":
            variable_name = node.children[0].value  # First child is the variable name
            expression = node.children[1]

            if variable_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{variable_name}' not defined.")
            else:
                expr_type = self.handle_expression(expression)
                if expr_type and expr_type != self.symbol_table[variable_name]:
                    self.errors.append(f"Error: Type mismatch in assignment to '{variable_name}'.")

        # Handle expressions directly (e.g., arithmetic or comparison operations)
        elif node.value == "EXPRESSION":
            self.handle_expression(node)

        # Handle if-statements
        elif node.value == "IF_STATEMENT":
            condition = node.children[0]
            if self.handle_expression(condition) != "bool":
                self.errors.append(f"Error: Condition in 'if' statement must be of type 'bool'.")
            for child in node.children[1:]:
                self.analyze(child)

        # Handle while-statements
        elif node.value == "WHILE_STATEMENT":
            condition = node.children[0]
            if self.handle_expression(condition) != "bool":
                self.errors.append(f"Error: Condition in 'while' statement must be of type 'bool'.")
            for child in node.children[1:]:
                self.analyze(child)

        # Handle function definitions
        elif node.value == "FUNCTION_DEF":
            function_name = node.children[0].value
            parameters = node.children[1].children
            return_type = node.children[2].value

            if function_name in self.symbol_table:
                self.errors.append(f"Error: Function '{function_name}' already defined.")
            else:
                self.symbol_table[function_name] = {
                    "type": return_type,
                    "parameters": [param.value for param in parameters]
                }

            for child in node.children[3:]:
                self.analyze(child)

        # Handle return statements
        elif node.value == "RETURN_STATEMENT":
            expression = node.children[0]
            return_type = self.handle_expression(expression)
            expected_return_type = self.symbol_table.get("return_type", "void")
            if return_type != expected_return_type:  # Check against expected return type
                self.errors.append(f"Error: Type mismatch in return statement. Expected '{expected_return_type}', got '{return_type}'.")

        # Continue analyzing each child node
        for child in node.children:
            self.analyze(child)

    def handle_expression(self, node):
        if node.value == "IDENTIFIER":
            variable_name = node.value
            if variable_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{variable_name}' not defined.")
                return None  # Return None if undeclared
            return self.symbol_table[variable_name]

        if len(node.children) == 3:  # Example: Binary expression
            left_operand = node.children[0]
            operator = node.children[1].value
            right_operand = node.children[2]

            left_type = self.handle_expression(left_operand)
            right_type = self.handle_expression(right_operand)

            if left_type is None or right_type is None:
                return None  # One of the operands is not defined

            if left_type != right_type:
                self.errors.append(f"Error: Type mismatch between '{left_operand.value}' and '{right_operand.value}'.")

            if operator in ["<", ">", "<=", ">=", "==", "!="]:
                return "bool"

            return left_type

        return None

    def print_errors(self):
        if not self.errors:
            print("No semantic errors found.")
        else:
            print("Semantic Errors:")
            for error in self.errors:
                print(error)


def parse_tree_from_file(filename, indent_size=4):
    """Parse the syntax tree from the given file using indentation."""
    with open(filename, 'r') as file:
        lines = file.readlines()

    stack = []
    root = None

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue  # Skip empty lines

        # Determine the current node's depth based on indentation (number of leading spaces)
        depth = (len(line) - len(stripped_line)) // indent_size

        # Create a new node
        new_node = Node(stripped_line)

        if depth == 0:
            # This is the root node
            root = new_node
            stack = [root]
        else:
            # Find the correct parent based on depth
            while len(stack) > depth:
                stack.pop()

            # Add the new node as a child of the current top node in the stack
            parent = stack[-1] if stack else None
            if parent:
                parent.children.append(new_node)
                stack.append(new_node)
            else:
                print(f"Warning: No parent found for depth level {depth}, skipping node {stripped_line}")

    return root


def main():
    # Read the parse tree from a file
    root = parse_tree_from_file("syntax\syntaxOutput.txt")
    
    analyzer = SemanticAnalyzer()
    analyzer.analyze(root)

    # Print the semantic errors, if any
    analyzer.print_errors()

    # Print the Abstract Syntax Tree with node numbers
    print("\nSementics:")
    root.print_tree()  # Print the AST starting from the root


if __name__ == "__main__":
    main()