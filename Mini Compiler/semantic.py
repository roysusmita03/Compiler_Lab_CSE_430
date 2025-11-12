from symbol_table import SymbolTable
from mini_ast import *

class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors = []
        self.current_function = None

    def analyze(self, program):
        """Run semantic analysis on the entire program."""
        for fn in program.functions:
            self.visit_function(fn)
        return self.errors

    def visit_function(self, fn):
        """Visit function declaration."""
        self.current_function = fn.name
        self.symtab.insert(fn.ret_type, "Function", fn.name, fn.lineno)
        
        # Add parameters to symbol table
        for ptype, pname in fn.params:
            self.symtab.insert(ptype, "Parameter", pname, fn.lineno)
        
        # Visit function body
        self.visit_compound(fn.body, fn.ret_type)
        self.current_function = None

    def visit_compound(self, comp, return_type):
        """Visit compound statement."""
        # Process declarations and statements
        for item in comp.decls + comp.stmts:
            if isinstance(item, Decl):
                # Add variable declaration to symbol table
                self.symtab.insert(item.var_type, "Identifier", item.name, item.lineno)
            elif isinstance(item, Assign):
                # Process assignment (for initialized variables)
                self.visit_expr(item)
            elif isinstance(item, list):
                # Handle lists of declarations/assignments
                for subitem in item:
                    if isinstance(subitem, Decl):
                        self.symtab.insert(subitem.var_type, "Identifier", subitem.name, subitem.lineno)
                    elif isinstance(subitem, Assign):
                        self.visit_expr(subitem)
            else:
                # Process other statements
                self.visit_stmt(item, return_type)

    def visit_stmt(self, stmt, return_type):
        """Visit statement."""
        if isinstance(stmt, If):
            expr_type = self.visit_expr(stmt.cond)
            if expr_type not in ('int', 'Unknown'):
                self.errors.append(f"Condition expression must be integer, got {expr_type}")
            self.visit_stmt(stmt.then_stmt, return_type)
            if stmt.else_stmt:
                self.visit_stmt(stmt.else_stmt, return_type)
        
        elif isinstance(stmt, While):
            expr_type = self.visit_expr(stmt.cond)
            if expr_type not in ('int', 'Unknown'):
                self.errors.append(f"While condition must be integer, got {expr_type}")
            self.visit_stmt(stmt.body, return_type)
        
        elif isinstance(stmt, For):
            if stmt.init:
                if isinstance(stmt.init, list):
                    for item in stmt.init:
                        if isinstance(item, (Decl, Assign)):
                            self.visit_expr(item)
                else:
                    self.visit_expr(stmt.init)
            if stmt.cond:
                cond_type = self.visit_expr(stmt.cond)
                if cond_type not in ('int', 'Unknown'):
                    self.errors.append(f"For condition must be integer, got {cond_type}")
            if stmt.post:
                self.visit_expr(stmt.post)
            self.visit_stmt(stmt.body, return_type)
        
        elif isinstance(stmt, Return):
            if stmt.expr:
                expr_type = self.visit_expr(stmt.expr)
                if return_type != expr_type and expr_type != 'Unknown':
                    self.errors.append(f"Return type mismatch in function '{self.current_function}': expected {return_type}, got {expr_type}")
            else:
                if return_type != 'void':
                    self.errors.append(f"Function '{self.current_function}' must return a value")
        
        elif isinstance(stmt, ExprStmt):
            self.visit_expr(stmt.expr)
        
        elif isinstance(stmt, Compound):
            self.visit_compound(stmt, return_type)
        
        elif isinstance(stmt, Assign):
            # Handle assignment statements
            self.visit_expr(stmt)

    def visit_expr(self, expr):
        """Visit expression and return its type."""
        if expr is None:
            return 'void'
        
        if isinstance(expr, IntConst):
            return 'int'
        
        if isinstance(expr, FloatConst):
            return 'float'
        
        if isinstance(expr, VarRef):
            sym = self.symtab.lookup(expr.name)
            if not sym:
                self.errors.append(f"Undeclared variable '{expr.name}' at line {getattr(expr, 'lineno', 'unknown')}")
                self.symtab.insert('Unknown', 'Identifier', expr.name, 0)
                return 'Unknown'
            return sym.data_type
        
        if isinstance(expr, Assign):
            # Check if variable exists, if not add it
            lhs_sym = self.symtab.lookup(expr.name)
            if not lhs_sym:
                # Try to infer type from RHS
                rhs_type = self.visit_expr(expr.expr)
                self.symtab.insert(rhs_type if rhs_type != 'Unknown' else 'int', 'Identifier', expr.name, 0)
                lhs_sym = self.symtab.lookup(expr.name)
            
            rhs_type = self.visit_expr(expr.expr)
            
            if lhs_sym.data_type != rhs_type and 'Unknown' not in (lhs_sym.data_type, rhs_type):
                self.errors.append(f"Assignment type mismatch: {lhs_sym.data_type} = {rhs_type}")
            
            return lhs_sym.data_type
        
        if isinstance(expr, Binary):
            left_type = self.visit_expr(expr.left)
            right_type = self.visit_expr(expr.right)
            
            # Type checking for binary operations
            if expr.op in ('+', '-', '*', '/', '%'):
                if left_type == 'float' or right_type == 'float':
                    return 'float'
                return 'int'
            elif expr.op in ('<', '>', '<=', '>=', '==', '!='):
                return 'int'  # Boolean results as integers in C
            elif expr.op in ('&&', '||'):
                if left_type not in ('int', 'Unknown') or right_type not in ('int', 'Unknown'):
                    self.errors.append(f"Logical operators require integer operands")
                return 'int'
            
            return left_type  # Default to left type
        
        if isinstance(expr, Unary):
            expr_type = self.visit_expr(expr.expr)
            if expr.op in ('+', '-') and expr_type not in ('int', 'float', 'Unknown'):
                self.errors.append(f"Unary {expr.op} requires numeric operand")
            return expr_type
        
        if isinstance(expr, Call):
            func_sym = self.symtab.lookup(expr.name)
            if not func_sym:
                self.errors.append(f"Undeclared function '{expr.name}'")
                return 'Unknown'
            
            # Check arguments
            for arg in expr.args:
                self.visit_expr(arg)
            
            return func_sym.data_type
        
        return 'Unknown'

    def write_semantic_output(self, filename='semantic_report.txt'):
        """Write semantic analysis results to file."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Semantic Analyzer's Output:\n\n")
            
            if not self.errors:
                f.write("Result: SUCCESS - No semantic errors found.\n\n")
                f.write("Symbol Table Summary:\n")
                f.write("=" * 50 + "\n")
                
                # Count symbols by type
                functions = [s for s in self.symtab.table.values() if s.token_type == "Function"]
                variables = [s for s in self.symtab.table.values() if s.token_type == "Identifier"]
                parameters = [s for s in self.symtab.table.values() if s.token_type == "Parameter"]
                
                f.write(f"Functions: {len(functions)}\n")
                for func in functions:
                    f.write(f"  - {func.token_value}: returns {func.data_type}\n")
                
                f.write(f"\nParameters: {len(parameters)}\n")
                for param in parameters:
                    f.write(f"  - {param.token_value}: {param.data_type}\n")
                
                f.write(f"\nVariables: {len(variables)}\n")
                for var in variables:
                    f.write(f"  - {var.token_value}: {var.data_type}\n")
                
                f.write(f"\nTotal Symbols: {len(self.symtab.table)}\n")
            else:
                f.write("Result: FAILED - Semantic errors found.\n\n")
                f.write("Errors:\n")
                f.write("=" * 50 + "\n")
                for err in self.errors:
                    f.write(f"• {err}\n")
        
        print("Wrote semantic report to", filename)