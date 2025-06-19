import os
from Parser import parser, lexer  # Ensure lexer is imported

class ASTBuilder:
    """
    Builds and manages the Abstract Syntax Tree (AST) from input code.
    """
    def __init__(self, output_dir='salida'):
        """
        Initializes the ASTBuilder.

        Args:
            output_dir (str): The directory to save output files (AST, trace).
        """
        self.ast = None
        self.tokens = [] # To store tokens if collected
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def build_ast(self, input_code: str):
        """
        Constructs the AST from the given input code.

        Args:
            input_code (str): The source code to parse.

        Returns:
            The constructed AST, or None if parsing fails.
        
        Raises:
            Exception: Propagates exceptions from the parser.
        """
        self.ast = None
        self.tokens = [] # Reset tokens for new build
        
        # Reset lexer state and feed input
        lexer.lineno = 1
        lexer.input(input_code)
        
        try:
            self.ast = parser.parse(lexer=lexer) # Use the global lexer instance

            if self.ast:
                lexer.input(input_code)
                while True:
                    tok = lexer.token()
                    if not tok:
                        break
                    self.tokens.append(tok)

            return self.ast
        except Exception as e:
            print(f"Error during AST construction: {str(e)}")
            self.ast = None
            raise

    def _write_node(self, file, node, indent):
        """
        Helper function to recursively write AST nodes to a file.
        """
        if node is None:
            return

        if isinstance(node, tuple):
            file.write('  ' * indent + f"{node[0]}:\n")
            for child_node in node[1:]:
                self._write_node(file, child_node, indent + 1)
        elif isinstance(node, list):
            for child_node in node:
                self._write_node(file, child_node, indent)
        else:
            file.write('  ' * indent + str(node) + '\n')

    def save_ast_to_file(self, filename="ast.txt"):
        """
        Saves the current AST to a text file.
        """
        if self.ast is None:
            print("No AST available to save.")
            return

        filepath = os.path.join(self.output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                self._write_node(f, self.ast, 0)
            print(f"AST saved to {filepath}")
        except IOError as e:
            print(f"Error saving AST to file {filepath}: {e}")

    def _print_node(self, node, indent):
        """
        Helper function to recursively print AST nodes to the console.
        """
        if node is None:
            return

        if isinstance(node, tuple):
            print('  ' * indent + f"{node[0]}:")
            for child_node in node[1:]:
                self._print_node(child_node, indent + 1)
        elif isinstance(node, list):
            for child_node in node:
                self._print_node(child_node, indent)
        else:
            print('  ' * indent + str(node))

    def print_ast(self):
        """
        Prints the current AST to the console.
        """
        if self.ast is None:
            print("No AST available to print.")
            return

        print("\n--- Abstract Syntax Tree (AST) ---")
        self._print_node(self.ast, 0)
        print("--- End of AST ---")

    def save_token_trace_to_file(self, filename="token_trace.txt"):
        """
        Saves the collected tokens to a text file.
        """
        if not self.tokens:
            print("No token trace available to save.")
            return

        filepath = os.path.join(self.output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("--- Token Trace ---\n")
                for tok in self.tokens:
                    f.write(f"Type: {tok.type}, Value: '{tok.value}', Line: {tok.lineno}, Pos: {tok.lexpos}\n")
                f.write("--- End of Token Trace ---\n")
            print(f"Token trace saved to {filepath}")
        except IOError as e:
            print(f"Error saving token trace to file {filepath}: {e}")

    def print_token_trace(self):
        """
        Prints the collected token trace to the console.
        """
        if not self.tokens:
            print("No token trace available to print.")
            return

        print("\n--- Token Trace ---")
        for tok in self.tokens:
            print(f"Type: {tok.type}, Value: '{tok.value}', Line: {tok.lineno}, Pos: {tok.lexpos}")
        print("--- End of Token Trace ---")

def build_and_display_ast(input_code: str, output_dir='salida'):
    """
    Convenience function to build and display the AST.
    """
    builder = ASTBuilder(output_dir=output_dir)
    
    print(f"\nBuilding AST for code:\n```\n{input_code}\n```")
    try:
        ast = builder.build_ast(input_code)
        if ast:
            builder.print_ast()
            builder.save_ast_to_file()
        else:
            print("AST construction failed.")
        return ast
    except Exception as e:
        print(f"An error occurred during AST processing: {e}")
        return None
