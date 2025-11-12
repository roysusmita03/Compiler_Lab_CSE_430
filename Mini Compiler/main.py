from lexer import tokenize, write_tokens
from parser import Parser, ParserError
from semantic import SemanticAnalyzer
from ir_generator import IRGenerator
from asm_generator import generate_asm_from_ir
from mini_ast import pretty_print
import sys
import traceback

def read_input(filename='input.c'):
    """Read input C code file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {filename}")
        print("Please create an input.c file with your C code.")
        sys.exit(1)

def run_all():
    """Run all compiler phases."""
    print("Mini C Compiler - Starting compilation...")
    print("=" * 50)
    
    # 1. Read input
    try:
        code = read_input('input.c')
        print("Read input file")
        print(f"  Input size: {len(code)} characters")
    except Exception as e:
        print(f"Failed to read input: {e}")
        sys.exit(1)
    
    # 2. Lexical Analysis
    try:
        tokens = tokenize(code)
        write_tokens(tokens, 'lexical_output.txt')
        print("Lexical analysis completed")
        print(f"  Generated {len(tokens)} tokens")
    except Exception as e:
        print(f"Lexical analysis failed: {e}")
        sys.exit(1)
    
    # 3. Syntax Analysis
    try:
        parser = Parser(tokens)
        program = parser.parse()
        parser.write_syntax_output(program, 'syntax_output.txt')
        print("Syntax analysis completed")
        print(f"  Found {len(program.functions)} function(s)")
    except ParserError as e:
        print(f"Syntax analysis failed: {e}")
        with open('syntax_output.txt', 'w') as f:
            f.write(f"Syntax Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error in syntax analysis: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    # 4. Semantic Analysis
    try:
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(program)
        analyzer.symtab.dump('symbol_table_output.txt')
        analyzer.write_semantic_output('semantic_report.txt')
        
        if errors:
            print(f"Semantic analysis completed with {len(errors)} warnings")
        else:
            print("Semantic analysis completed - No errors found")
    except Exception as e:
        print(f"Semantic analysis failed: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    # 5. Generate AST dump
    try:
        with open('ast_dump.txt', 'w', encoding='utf-8') as f:
            for line in pretty_print(program):
                f.write(line + '\n')
        print("AST generated")
    except Exception as e:
        print(f"AST generation failed: {e}")
    
    # 6. Intermediate Code Generation
    try:
        irgen = IRGenerator(debug=False)
        irgen.generate(program)
        irgen.write_output('intermediate_code_output.txt')
        print("Intermediate code generation completed")
    except Exception as e:
        print(f"Intermediate code generation failed: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    # 7. Assembly Code Generation
    try:
        generate_asm_from_ir('intermediate_code_output.txt', 'assembly_output.asm')
        print("Assembly code generation completed")
    except Exception as e:
        print(f"Assembly code generation failed: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("  Compilation completed successfully!")
    print("\nGenerated output files:")
    print("  - lexical_output.txt")
    print("  - syntax_output.txt") 
    print("  - symbol_table_output.txt")
    print("  - semantic_report.txt")
    print("  - ast_dump.txt")
    print("  - intermediate_code_output.txt")
    print("  - assembly_output.asm")

if __name__ == '__main__':
    run_all()