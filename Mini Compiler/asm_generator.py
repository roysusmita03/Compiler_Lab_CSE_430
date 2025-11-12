import re

class AssemblyGenerator:
    def __init__(self):
        self.reg_count = 0
        self.label_count = 0
        self.asm_code = []
        
        # Operation mapping from IR to assembly
        self.op_map = {
            '+': 'ADD',
            '-': 'SUB', 
            '*': 'MUL',
            '/': 'DIV',
            '%': 'MOD',
            '&&': 'AND',
            '||': 'OR',
            '==': 'CMP_EQ',
            '!=': 'CMP_NE',
            '<': 'CMP_LT',
            '>': 'CMP_GT',
            '<=': 'CMP_LE',
            '>=': 'CMP_GE'
        }

    def new_reg(self):
        """Generate a new register name."""
        self.reg_count += 1
        return f"R{self.reg_count}"

    def new_asm_label(self):
        """Generate a new assembly label."""
        self.label_count += 1
        return f"LABEL{self.label_count}"

    def emit(self, line):
        """Emit an assembly instruction."""
        self.asm_code.append("    " + line)

    def emit_label(self, line):
        """Emit a label (without indentation)."""
        self.asm_code.append(line)

    def comment(self, text):
        """Emit a comment."""
        self.emit(f"; {text}")

    def generate_asm(self, ir_lines):
        """Generate assembly code from intermediate code."""
        self.asm_code = []
        
        self.emit_label("; Assembly Code Generation Output")
        self.emit_label("; ===============================")
        self.emit_label("")
        
        # Skip the header lines from IR
        skip_header = True
        
        # Process each IR line
        for line in ir_lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip IR header lines
            if skip_header:
                if line.startswith('# Intermediate Code Generation Output'):
                    continue
                elif line.startswith('# ==================================='):
                    continue
                elif line.startswith('#'):
                    # Skip other header comments
                    continue
                else:
                    skip_header = False
            
            # Process comments
            if line.startswith('#'):
                self.comment(line[1:].strip())
                continue
            
            # Process different IR instructions
            if self.process_function(line):
                continue
            elif self.process_label(line):
                continue
            elif self.process_return(line):
                continue
            elif self.process_if(line):
                continue
            elif self.process_goto(line):
                continue
            elif self.process_param(line):
                continue
            elif self.process_call(line):
                continue
            elif self.process_assignment(line):
                continue
            else:
                self.comment(f"Unprocessed: {line}")

        return self.asm_code

    def process_function(self, line):
        """Process function definition."""
        if line.startswith('FUNC_') and line.endswith(':'):
            func_name = line[:-1]
            self.emit_label("")
            self.emit_label(f"{func_name}:")
            self.emit("PUSH BP")
            self.emit("MOV BP, SP")
            return True
        elif line.startswith('END_FUNC_'):
            func_name = line[:-1] if line.endswith(':') else line
            self.emit("POP BP")
            self.emit("RET")
            return True
        return False

    def process_label(self, line):
        """Process label definition."""
        if line.endswith(':') and not line.startswith('FUNC_') and not line.startswith('END_FUNC_'):
            self.emit_label(line)
            return True
        return False

    def process_return(self, line):
        """Process return statement."""
        match = re.match(r'RETURN\s*(.*)$', line.strip())
        if match:
            value = match.group(1).strip()
            if value:
                # Return with value
                self.emit(f"MOV R0, {value}")  # R0 is return value register
            self.emit("POP BP")
            self.emit("RET")
            return True
        return False

    def process_if(self, line):
        """Process conditional jump."""
        match = re.match(r'IF\s+(\S+)\s+==\s+0\s+GOTO\s+(\S+)', line)
        if match:
            condition = match.group(1)
            label = match.group(2)
            
            # Compare condition with 0 and jump if equal (false)
            self.emit(f"CMP {condition}, 0")
            self.emit(f"JE {label}")
            return True
        return False

    def process_goto(self, line):
        """Process unconditional jump."""
        match = re.match(r'GOTO\s+(\S+)', line)
        if match:
            label = match.group(1)
            self.emit(f"JMP {label}")
            return True
        return False

    def process_param(self, line):
        """Process parameter passing."""
        match = re.match(r'PARAM\s+(\S+)', line)
        if match:
            param = match.group(1)
            self.emit(f"PUSH {param}")
            return True
        return False

    def process_call(self, line):
        """Process function call."""
        match = re.match(r'(\S+)\s*=\s*CALL\s+(\S+)', line)
        if match:
            result_var = match.group(1)
            func_name = match.group(2)
            
            self.emit(f"CALL {func_name}")
            self.emit(f"MOV {result_var}, R0")  # Get return value from R0
            return True
        return False

    def process_assignment(self, line):
        """Process assignment and binary operations."""
        # Simple assignment: x = y
        simple_match = re.match(r'(\S+)\s*=\s*(\S+)$', line)
        if simple_match:
            dest = simple_match.group(1)
            src = simple_match.group(2)
            self.emit(f"MOV {dest}, {src}")
            return True
        
        # Binary operation: t1 = a + b
        bin_match = re.match(r'(\S+)\s*=\s*(\S+)\s*([+\-*/%])\s*(\S+)', line)
        if bin_match:
            dest = bin_match.group(1)
            left = bin_match.group(2)
            op = bin_match.group(3)
            right = bin_match.group(4)
            
            asm_op = self.op_map.get(op, op.upper())
            
            if asm_op.startswith('CMP_'):
                # Comparison operations
                cmp_label = self.new_asm_label()
                end_label = self.new_asm_label()
                self.emit(f"CMP {left}, {right}")
                self.emit(f"MOV {dest}, 1")  # Set to true
                self.emit(f"{asm_op[4:]} {cmp_label}")  # JE, JNE, etc.
                self.emit(f"MOV {dest}, 0")
                self.emit_label(f"{cmp_label}:")
            else:
                # Arithmetic operations
                self.emit(f"MOV {dest}, {left}")
                self.emit(f"{asm_op} {dest}, {right}")
            
            return True
        
        # Logical operations: t1 = a && b
        logical_match = re.match(r'(\S+)\s*=\s*(\S+)\s*(&&|\|\|)\s*(\S+)', line)
        if logical_match:
            dest = logical_match.group(1)
            left = logical_match.group(2)
            op = logical_match.group(3)
            right = logical_match.group(4)
            
            false_label = self.new_asm_label()
            end_label = self.new_asm_label()
            
            if op == '&&':
                # AND operation
                self.emit(f"CMP {left}, 0")
                self.emit(f"JE {false_label}")
                self.emit(f"CMP {right}, 0")
                self.emit(f"JE {false_label}")
                self.emit(f"MOV {dest}, 1")
                self.emit(f"JMP {end_label}")
                self.emit_label(f"{false_label}:")
                self.emit(f"MOV {dest}, 0")
                self.emit_label(f"{end_label}:")
            else:  # OR operation
                self.emit(f"CMP {left}, 0")
                self.emit(f"JNE {end_label}")
                self.emit(f"CMP {right}, 0")
                self.emit(f"JNE {end_label}")
                self.emit(f"MOV {dest}, 0")
                self.emit(f"JMP {end_label}")
                self.emit_label(f"{end_label}:")
                self.emit(f"MOV {dest}, 1")
            
            return True
        
        return False

    def write_assembly(self, filename='assembly_output.asm'):
        """Write assembly code to file."""
        with open(filename, 'w', encoding='utf-8') as f:
            # Write header
            f.write("; Assembly Code Generation Output\n")
            f.write("; ===============================\n")
            f.write("\n.DATA\n")
            f.write("    ; Variable declarations would go here\n")
            f.write("\n.CODE\n")
            f.write("START:\n")
            f.write("    ; Main program entry point\n")
            f.write("    CALL FUNC_main\n")
            f.write("    HLT\n")
            f.write("\n")
            
            # Write generated assembly code
            for line in self.asm_code:
                f.write(line + "\n")
        
        print(f"Assembly code written to {filename}")

def generate_asm_from_ir(ir_filename='intermediate_code_output.txt', 
                        asm_filename='assembly_output.asm'):
    """Generate assembly code from IR file."""
    try:
        # Read IR code
        with open(ir_filename, 'r', encoding='utf-8') as f:
            ir_lines = f.readlines()
        
        # Generate assembly
        generator = AssemblyGenerator()
        asm_code = generator.generate_asm(ir_lines)
        generator.write_assembly(asm_filename)
        
        print(f"Successfully generated assembly code from {ir_filename}")
        
    except FileNotFoundError:
        print(f"Error: Could not find {ir_filename}")
    except Exception as e:
        print(f"Error during assembly generation: {e}")

if __name__ == '__main__':
    generate_asm_from_ir()