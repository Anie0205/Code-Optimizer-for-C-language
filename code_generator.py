from pycparser import c_generator

def generate_code(ast):
    generator = c_generator.CGenerator()
    return generator.visit(ast)
