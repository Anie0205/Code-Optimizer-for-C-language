from pycparser import c_parser

def parse_code(source_code):
    parser = c_parser.CParser()
    ast = parser.parse(source_code)
    return ast
