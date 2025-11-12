from mini_ast import *

class IRGenerator:
    def __init__(self, debug=True):
        self.temp_count = 0
        self.label_count = 0
        self.code = []
        self.debug = debug

    def new_temp(self):
        """Generate a new temporary variable."""
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        """Generate a new label."""
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, line):
        """Emit a line of intermediate code."""
        self.code.append(line)
        if self.debug:
            print(f"[IRGEN] {line}")

    def generate(self, program):
        """Generate intermediate code for the entire program."""
        self.code = []
        
        # Emit header only once
        self.emit("# Intermediate Code Generation Output")
        self.emit("# ===================================")
        
        for func in program.functions:
            self.gen_function(func)
        
        return self.code

    def gen_function(self, func):
        """Generate code for a function."""
        self.emit("")
        self.emit(f"# Function: {func.ret_type} {func.name}")
        self.emit(f"FUNC_{func.name}:")
        
        # Generate code for parameters
        for i, (ptype, pname) in enumerate(func.params):
            self.emit(f"    PARAM {pname}")
        
        # Generate code for function body
        self.gen_compound(func.body)
        
        # Add return if not present
        if not any(isinstance(stmt, Return) for stmt in func.body.stmts):
            if func.ret_type == 'void':
                self.emit("    RETURN")
            else:
                self.emit("    RETURN 0")
        
        self.emit(f"END_FUNC_{func.name}:")
        self.emit("")

    def gen_compound(self, compound):
        """Generate code for compound statement."""
        # Process all items (declarations and statements mixed)
        all_items = compound.decls + compound.stmts
        
        for item in all_items:
            if isinstance(item, Decl):
                self.emit(f"    # Declare {item.var_type} {item.name}")
            elif isinstance(item, Assign):
                self.gen_stmt(item)
            elif isinstance(item, list):
                # Handle lists from declarations with initialization
                for subitem in item:
                    if isinstance(subitem, Decl):
                        self.emit(f"    # Declare {subitem.var_type} {subitem.name}")
                    elif isinstance(subitem, Assign):
                        self.gen_stmt(subitem)
            else:
                self.gen_stmt(item)

    def gen_stmt(self, stmt):
        """Generate code for a statement."""
        if isinstance(stmt, Compound):
            self.gen_compound(stmt)
        
        elif isinstance(stmt, Assign):
            # Generate code for assignment: x = expr
            value = self.gen_expr(stmt.expr)
            self.emit(f"    {stmt.name} = {value}")
        
        elif isinstance(stmt, ExprStmt):
            # Generate code for expression statement
            value = self.gen_expr(stmt.expr)
            if value and value != "":  # Only emit if expression has a value
                self.emit(f"    # Expression: {value}")
        
        elif isinstance(stmt, Return):
            if stmt.expr:
                value = self.gen_expr(stmt.expr)
                self.emit(f"    RETURN {value}")
            else:
                self.emit("    RETURN")
        
        elif isinstance(stmt, If):
            self.gen_if(stmt)
        
        elif isinstance(stmt, While):
            self.gen_while(stmt)
        
        elif isinstance(stmt, For):
            self.gen_for(stmt)
        
        else:
            self.emit(f"    # Unknown statement: {type(stmt).__name__}")

    def gen_if(self, stmt):
        """Generate code for if statement."""
        cond_val = self.gen_expr(stmt.cond)
        else_label = self.new_label()
        end_label = self.new_label()
        
        # If condition is false, jump to else or end
        self.emit(f"    IF {cond_val} == 0 GOTO {else_label}")
        
        # Then branch
        self.gen_stmt(stmt.then_stmt)
        
        # Jump to end after then branch
        if stmt.else_stmt:
            self.emit(f"    GOTO {end_label}")
        
        # Else branch
        self.emit(f"{else_label}:")
        if stmt.else_stmt:
            self.gen_stmt(stmt.else_stmt)
            self.emit(f"{end_label}:")
        else:
            # If no else, use else_label as end label
            self.emit(f"    # End if")

    def gen_while(self, stmt):
        """Generate code for while loop."""
        start_label = self.new_label()
        end_label = self.new_label()
        
        self.emit(f"{start_label}:")
        
        # Evaluate condition
        cond_val = self.gen_expr(stmt.cond)
        self.emit(f"    IF {cond_val} == 0 GOTO {end_label}")
        
        # Loop body
        self.gen_stmt(stmt.body)
        
        # Jump back to condition check
        self.emit(f"    GOTO {start_label}")
        self.emit(f"{end_label}:")

    def gen_for(self, stmt):
        """Generate code for for loop: for (init; cond; post) body"""
        start_label = self.new_label()
        body_label = self.new_label()
        end_label = self.new_label()
        
        # Initialization
        if stmt.init:
            if isinstance(stmt.init, list):
                # Handle declaration with initialization: int i = 0
                for item in stmt.init:
                    if isinstance(item, Assign):
                        self.gen_stmt(item)
            else:
                # Handle expression initialization: i = 0
                self.gen_stmt(stmt.init)
        
        self.emit(f"{start_label}:")
        
        # Condition
        if stmt.cond:
            cond_val = self.gen_expr(stmt.cond)
            self.emit(f"    IF {cond_val} == 0 GOTO {end_label}")
        else:
            # If no condition, it's an infinite loop
            pass
        
        # Loop body
        self.emit(f"    GOTO {body_label}")
        self.emit(f"{body_label}:")
        self.gen_stmt(stmt.body)
        
        # Post iteration
        if stmt.post:
            self.gen_expr(stmt.post)
        
        # Jump back to condition check
        self.emit(f"    GOTO {start_label}")
        self.emit(f"{end_label}:")

    def gen_expr(self, expr):
        """Generate code for expression and return temporary holding result."""
        if expr is None:
            return ""
        
        if isinstance(expr, IntConst):
            return str(expr.value)
        
        elif isinstance(expr, FloatConst):
            return str(expr.value)
        
        elif isinstance(expr, VarRef):
            return expr.name
        
        elif isinstance(expr, Assign):
            # For assignment in expression context
            value = self.gen_expr(expr.expr)
            self.emit(f"    {expr.name} = {value}")
            return expr.name
        
        elif isinstance(expr, Binary):
            left_val = self.gen_expr(expr.left)
            right_val = self.gen_expr(expr.right)
            temp = self.new_temp()
            
            # Handle different binary operations
            if expr.op == '+':
                self.emit(f"    {temp} = {left_val} + {right_val}")
            elif expr.op == '-':
                self.emit(f"    {temp} = {left_val} - {right_val}")
            elif expr.op == '*':
                self.emit(f"    {temp} = {left_val} * {right_val}")
            elif expr.op == '/':
                self.emit(f"    {temp} = {left_val} / {right_val}")
            elif expr.op == '%':
                self.emit(f"    {temp} = {left_val} % {right_val}")
            elif expr.op == '&&':
                self.emit(f"    {temp} = {left_val} && {right_val}")
            elif expr.op == '||':
                self.emit(f"    {temp} = {left_val} || {right_val}")
            elif expr.op == '==':
                self.emit(f"    {temp} = {left_val} == {right_val}")
            elif expr.op == '!=':
                self.emit(f"    {temp} = {left_val} != {right_val}")
            elif expr.op == '<':
                self.emit(f"    {temp} = {left_val} < {right_val}")
            elif expr.op == '>':
                self.emit(f"    {temp} = {left_val} > {right_val}")
            elif expr.op == '<=':
                self.emit(f"    {temp} = {left_val} <= {right_val}")
            elif expr.op == '>=':
                self.emit(f"    {temp} = {left_val} >= {right_val}")
            else:
                self.emit(f"    {temp} = {left_val} {expr.op} {right_val}")
            
            return temp
        
        elif isinstance(expr, Unary):
            operand_val = self.gen_expr(expr.expr)
            temp = self.new_temp()
            
            if expr.op == '+':
                self.emit(f"    {temp} = +{operand_val}")
            elif expr.op == '-':
                self.emit(f"    {temp} = -{operand_val}")
            elif expr.op == '!':
                self.emit(f"    {temp} = !{operand_val}")
            else:
                self.emit(f"    {temp} = {expr.op}{operand_val}")
            
            return temp
        
        elif isinstance(expr, Call):
            # Push arguments
            for arg in expr.args:
                arg_val = self.gen_expr(arg)
                self.emit(f"    PARAM {arg_val}")
            
            # Call function and get return value
            temp = self.new_temp()
            self.emit(f"    {temp} = CALL {expr.name}")
            return temp
        
        elif isinstance(expr, Cast):
            operand_val = self.gen_expr(expr.expr)
            temp = self.new_temp()
            self.emit(f"    {temp} = ({expr.target_type}) {operand_val}")
            return temp
        
        else:
            return "unknown_expr"

    def write_output(self, filename="intermediate_code_output.txt"):
        """Write intermediate code to file."""
        with open(filename, "w", encoding="utf-8") as f:
            f.write("Intermediate Code Generation Output:\n")
            f.write("=" * 50 + "\n\n")
            for line in self.code:
                f.write(line + "\n")
        print(f"Intermediate code written to {filename}")