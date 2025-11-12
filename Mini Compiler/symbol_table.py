from collections import OrderedDict

class SymbolInfo:
    def __init__(self, token_no, data_type, token_type, token_value, line_of_code, dimension=1, address=0):
        self.token_no = token_no
        self.data_type = data_type
        self.token_type = token_type
        self.token_value = token_value
        self.line_of_code = line_of_code
        self.dimension = dimension
        self.address = address

class SymbolTable:
    def __init__(self):
        self.table = OrderedDict()
        self.token_counter = 0

    def insert(self, data_type, token_type, token_value, line_no, dimension=1, address=0):
        """Insert or update symbol table entry."""
        if token_value not in self.table:
            self.token_counter += 1
            self.table[token_value] = SymbolInfo(
                self.token_counter, data_type, token_type, token_value, [line_no], dimension, address
            )
        else:
            if line_no not in self.table[token_value].line_of_code:
                self.table[token_value].line_of_code.append(line_no)

    def lookup(self, name):
        """Look up a symbol by name."""
        return self.table.get(name)

    def display(self):
        """Print the table in formatted style."""
        header = f"{'TOKEN#':<8}{'DATA TYPE':<12}{'TOKEN_TYPE':<15}{'TOKEN_VALUE':<15}{'LINE OF CODE':<20}{'DIMENSION':<10}{'ADDRESS':<10}"
        print(header)
        print('-' * len(header))
        
        for sym in self.table.values():
            line_codes = ' '.join(map(str, sym.line_of_code))
            print(f"{sym.token_no:<8}{sym.data_type:<12}{sym.token_type:<15}{sym.token_value:<15}{line_codes:<20}{sym.dimension:<10}{sym.address:<10}")

    def display_detailed(self):
        """Print detailed symbol table information."""
        print("\n" + "="*80)
        print("SYMBOL TABLE ANALYSIS")
        print("="*80)
        
        if not self.table:
            print("Symbol table is empty")
            return
        
        functions = {k: v for k, v in self.table.items() if v.token_type == "Function"}
        parameters = {k: v for k, v in self.table.items() if v.token_type == "Parameter"}
        variables = {k: v for k, v in self.table.items() if v.token_type == "Identifier"}
        
        print(f"\nFUNCTIONS ({len(functions)}):")
        for name, info in functions.items():
            print(f"  {name}: returns {info.data_type}, declared at line {info.line_of_code}")
        
        print(f"\nPARAMETERS ({len(parameters)}):")
        for name, info in parameters.items():
            print(f"  {name}: {info.data_type}, used at lines {info.line_of_code}")
        
        print(f"\nVARIABLES ({len(variables)}):")
        for name, info in variables.items():
            print(f"  {name}: {info.data_type}, used at lines {info.line_of_code}")
        
        print(f"\nTOTAL SYMBOLS: {len(self.table)}")

    def dump(self, filename='symbol_table_output.txt'):
        """Save the formatted table to a text file."""
        with open(filename, 'w', encoding='utf-8') as f:
            header = f"{'TOKEN#':<8}{'DATA TYPE':<12}{'TOKEN_TYPE':<15}{'TOKEN_VALUE':<15}{'LINE OF CODE':<20}{'DIMENSION':<10}{'ADDRESS':<10}\n"
            f.write(header)
            f.write('-' * len(header) + '\n')
            
            for sym in self.table.values():
                line_codes = ' '.join(map(str, sym.line_of_code))
                f.write(f"{sym.token_no:<8}{sym.data_type:<12}{sym.token_type:<15}{sym.token_value:<15}{line_codes:<20}{sym.dimension:<10}{sym.address:<10}\n")
        
        print(f"Symbol Table written to {filename}")