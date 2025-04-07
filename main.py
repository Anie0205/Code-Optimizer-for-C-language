from pycparser import c_parser, c_generator
from optimizer import optimize_c_ast

def main():
    with open("test_cases/CF_input.c", "r") as f:
        code = f.read()

    parser = c_parser.CParser()
    ast = parser.parse(code)

    optimize_c_ast(ast)

    generator = c_generator.CGenerator()
    optimized_code = generator.visit(ast)

    with open("test_cases/CF_output.c", "w") as f:
        f.write(optimized_code)

if __name__ == "__main__":
    main()
