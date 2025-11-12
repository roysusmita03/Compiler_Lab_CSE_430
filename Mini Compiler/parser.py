from mini_ast import *

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0] if tokens else None

    def peek(self, kind=None):
        if self.pos >= len(self.tokens):
            return None
        t = self.tokens[self.pos]
        if kind is None:
            return t
        return t if t['TYPE'] == kind else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        else:
            self.current = {'TYPE': 'EOF', 'VALUE': 'EOF', 'LINE': 0, 'COLUMN': 0}
        return self.current

    def expect(self, kind, value=None):
        t = self.peek()
        if not t or t['TYPE'] != kind or (value is not None and t['VALUE'] != value):
            expected = f"{kind}('{value}')" if value else kind
            line = t['LINE'] if t else 'EOF'
            raise ParserError(f"Expected {expected} at line {line}, but got {t['TYPE']}('{t['VALUE']}')" if t else "EOF")
        self.advance()
        return t

    def match(self, kind, value=None):
        t = self.peek()
        if t and t['TYPE'] == kind and (value is None or t['VALUE'] == value):
            self.advance()
            return True
        return False

    def parse(self):
        functions = []
        while not self.match('EOF'):
            functions.append(self.parse_function())
        return Program(functions)

    def parse_function(self):
        ret_type = self.expect('KEYWORD')['VALUE']
        name_tok = self.expect('IDENTIFIER')
        name = name_tok['VALUE']
        
        self.expect('LEFT_PAREN')
        params = []
        
        if not self.peek('RIGHT_PAREN'):
            while True:
                ptype = self.expect('KEYWORD')['VALUE']
                pname = self.expect('IDENTIFIER')['VALUE']
                params.append((ptype, pname))
                if not self.match('COMMA'):
                    break
        
        self.expect('RIGHT_PAREN')
        body = self.parse_compound_stmt()
        return Function(ret_type, name, params, body, name_tok['LINE'])

    def parse_compound_stmt(self):
        self.expect('LEFT_BRACE')
        decls = []
        stmts = []
        
        while not self.match('RIGHT_BRACE'):
            t = self.peek()
            if not t or t['TYPE'] == 'EOF':
                raise ParserError("Unexpected end of file in compound statement")
            
            # Check for variable declarations
            if t['TYPE'] == 'KEYWORD' and t['VALUE'] in ('int', 'float', 'char', 'void'):
                decl_items = self.parse_decl()
                if isinstance(decl_items, list):
                    decls.extend(decl_items)
                else:
                    decls.append(decl_items)
            else:
                # Parse as statement
                stmt = self.parse_stmt()
                if stmt:
                    stmts.append(stmt)
        
        return Compound(decls, stmts)

    def parse_decl(self):
        """Parse variable declaration with optional initialization."""
        var_type = self.expect('KEYWORD')['VALUE']
        items = []
        
        # Parse first declaration
        name = self.expect('IDENTIFIER')['VALUE']
        lineno = self.current['LINE']
        
        # Create declaration
        decl = Decl(var_type, name, lineno)
        items.append(decl)
        
        # Check for initialization
        if self.match('ASSIGNMENT'):
            init_expr = self.parse_expr()
            assign = Assign(name, init_expr)
            items.append(assign)
        
        # Parse additional declarations separated by commas
        while self.match('COMMA'):
            name = self.expect('IDENTIFIER')['VALUE']
            
            # Create declaration
            decl = Decl(var_type, name, lineno)
            items.append(decl)
            
            # Check for initialization
            if self.match('ASSIGNMENT'):
                init_expr = self.parse_expr()
                assign = Assign(name, init_expr)
                items.append(assign)
        
        self.expect('SEMICOLON')
        
        return items if len(items) > 1 else items[0]

    def parse_stmt(self):
        t = self.peek()
        if not t:
            raise ParserError("Unexpected end of input in statement")
        
        if t['TYPE'] == 'KEYWORD':
            if t['VALUE'] == 'return':
                return self.parse_return()
            elif t['VALUE'] == 'if':
                return self.parse_if()
            elif t['VALUE'] == 'while':
                return self.parse_while()
            elif t['VALUE'] == 'for':
                return self.parse_for()
        
        if t['TYPE'] == 'LEFT_BRACE':
            return self.parse_compound_stmt()
        
        # Expression statement
        expr = self.parse_expr()
        self.expect('SEMICOLON')
        return ExprStmt(expr)

    def parse_return(self):
        self.expect('KEYWORD', 'return')
        # Check if there's an expression or just semicolon
        if self.peek('SEMICOLON'):
            expr = None
        else:
            expr = self.parse_expr()
        self.expect('SEMICOLON')
        return Return(expr)

    def parse_if(self):
        self.expect('KEYWORD', 'if')
        self.expect('LEFT_PAREN')
        cond = self.parse_expr()
        self.expect('RIGHT_PAREN')
        then_stmt = self.parse_stmt()
        else_stmt = self.parse_stmt() if self.match('KEYWORD', 'else') else None
        return If(cond, then_stmt, else_stmt)

    def parse_while(self):
        self.expect('KEYWORD', 'while')
        self.expect('LEFT_PAREN')
        cond = self.parse_expr()
        self.expect('RIGHT_PAREN')
        body = self.parse_stmt()
        return While(cond, body)

    def parse_for(self):
        """Parse for loop: for (init; cond; post) body"""
        self.expect('KEYWORD', 'for')
        self.expect('LEFT_PAREN')
        
        # Parse initialization (can be declaration, assignment, or empty)
        init = None
        if not self.peek('SEMICOLON'):
            # Check if it's a declaration (like 'int i = 0')
            if self.peek('KEYWORD') and self.peek()['VALUE'] in ('int', 'float', 'char'):
                init = self.parse_decl()
            else:
                # It's an expression (like 'i = 0')
                init = self.parse_expr()
        self.expect('SEMICOLON')
        
        # Parse condition (can be expression or empty)
        cond = None
        if not self.peek('SEMICOLON'):
            cond = self.parse_expr()
        self.expect('SEMICOLON')
        
        # Parse post iteration (can be expression or empty)
        post = None
        if not self.peek('RIGHT_PAREN'):
            post = self.parse_expr()
        self.expect('RIGHT_PAREN')
        
        # Parse body
        body = self.parse_stmt()
        return For(init, cond, post, body)

    def parse_expr(self):
        return self.parse_assignment()

    def parse_assignment(self):
        left = self.parse_logical_or()
        if self.match('ASSIGNMENT'):
            if not isinstance(left, VarRef):
                raise ParserError("Left side of assignment must be a variable")
            value = self.parse_expr()
            return Assign(left.name, value)
        return left

    def parse_logical_or(self):
        expr = self.parse_logical_and()
        while self.match('LOGICAL_OPERATOR', '||'):
            right = self.parse_logical_and()
            expr = Binary('||', expr, right)
        return expr

    def parse_logical_and(self):
        expr = self.parse_equality()
        while self.match('LOGICAL_OPERATOR', '&&'):
            right = self.parse_equality()
            expr = Binary('&&', expr, right)
        return expr

    def parse_equality(self):
        expr = self.parse_relational()
        while True:
            if self.match('RELATIONAL_OPERATOR', '=='):
                right = self.parse_relational()
                expr = Binary('==', expr, right)
            elif self.match('RELATIONAL_OPERATOR', '!='):
                right = self.parse_relational()
                expr = Binary('!=', expr, right)
            else:
                break
        return expr

    def parse_relational(self):
        expr = self.parse_additive()
        while True:
            if self.match('RELATIONAL_OPERATOR', '<'):
                right = self.parse_additive()
                expr = Binary('<', expr, right)
            elif self.match('RELATIONAL_OPERATOR', '>'):
                right = self.parse_additive()
                expr = Binary('>', expr, right)
            elif self.match('RELATIONAL_OPERATOR', '<='):
                right = self.parse_additive()
                expr = Binary('<=', expr, right)
            elif self.match('RELATIONAL_OPERATOR', '>='):
                right = self.parse_additive()
                expr = Binary('>=', expr, right)
            else:
                break
        return expr

    def parse_additive(self):
        expr = self.parse_term()
        while True:
            if self.match('ARITHMETIC_OPERATOR', '+'):
                right = self.parse_term()
                expr = Binary('+', expr, right)
            elif self.match('ARITHMETIC_OPERATOR', '-'):
                right = self.parse_term()
                expr = Binary('-', expr, right)
            else:
                break
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        while True:
            if self.match('ARITHMETIC_OPERATOR', '*'):
                right = self.parse_factor()
                expr = Binary('*', expr, right)
            elif self.match('ARITHMETIC_OPERATOR', '/'):
                right = self.parse_factor()
                expr = Binary('/', expr, right)
            elif self.match('ARITHMETIC_OPERATOR', '%'):
                right = self.parse_factor()
                expr = Binary('%', expr, right)
            else:
                break
        return expr

    def parse_factor(self):
        # Unary operators
        if self.match('ARITHMETIC_OPERATOR', '+'):
            expr = self.parse_factor()
            return Unary('+', expr)
        elif self.match('ARITHMETIC_OPERATOR', '-'):
            expr = self.parse_factor()
            return Unary('-', expr)
        elif self.match('LOGICAL_OPERATOR', '!'):
            expr = self.parse_factor()
            return Unary('!', expr)
        
        return self.parse_primary()

    def parse_primary(self):
        t = self.peek()
        if not t:
            raise ParserError("Unexpected end of input in expression")
        
        if t['TYPE'] == 'INTEGER_LITERAL':
            value = t['VALUE']
            self.advance()
            return IntConst(int(value))
        
        if t['TYPE'] == 'FLOAT_LITERAL':
            value = t['VALUE']
            self.advance()
            return FloatConst(float(value))
        
        if t['TYPE'] == 'IDENTIFIER':
            name = t['VALUE']
            self.advance()
            
            # Function call
            if self.match('LEFT_PAREN'):
                args = []
                if not self.peek('RIGHT_PAREN'):
                    while True:
                        args.append(self.parse_expr())
                        if not self.match('COMMA'):
                            break
                self.expect('RIGHT_PAREN')
                return Call(name, args)
            
            # Variable reference
            return VarRef(name)
        
        if self.match('LEFT_PAREN'):
            expr = self.parse_expr()
            self.expect('RIGHT_PAREN')
            return expr
        
        raise ParserError(f"Unexpected token {t['VALUE']} at line {t['LINE']}")

    # ... (generate_ast_tree and write_syntax_output methods remain the same)
    def generate_ast_tree(self, node, indent=0, is_last=True, prefix=""):
        """Generate AST tree with proper tree structure."""
        lines = []
        marker = "└── " if is_last else "├── "
        current_prefix = prefix + marker
        
        if isinstance(node, Program):
            lines.append("PROGRAM")
            for i, func in enumerate(node.functions):
                lines.extend(self.generate_ast_tree(
                    func, indent + 1, i == len(node.functions) - 1, 
                    prefix + ("    " if is_last else "│   ")
                ))
        
        elif isinstance(node, Function):
            lines.append(current_prefix + f"FUNCTION: {node.ret_type} {node.name}")
            child_prefix = prefix + ("    " if is_last else "│   ")
            
            if node.params:
                lines.append(child_prefix + "├── PARAMETERS")
                for i, (ptype, pname) in enumerate(node.params):
                    param_marker = "└── " if i == len(node.params) - 1 else "├── "
                    lines.append(child_prefix + "│   " + param_marker + f"{ptype} {pname}")
            
            lines.append(child_prefix + "└── BODY")
            lines.extend(self.generate_ast_tree(
                node.body, indent + 1, True, child_prefix + "    "
            ))
        
        elif isinstance(node, Compound):
            lines.append(current_prefix + "COMPOUND")
            child_prefix = prefix + ("    " if is_last else "│   ")
            
            # Combine declarations and statements for display
            all_items = []
            if node.decls:
                all_items.extend([("DECLARATION", item) for item in node.decls])
            if node.stmts:
                all_items.extend([("STATEMENT", item) for item in node.stmts])
            
            for i, (item_type, item) in enumerate(all_items):
                is_last_item = i == len(all_items) - 1
                if isinstance(item, list):
                    # Handle lists of items (from declarations with initialization)
                    for j, subitem in enumerate(item):
                        sub_is_last = j == len(item) - 1 and is_last_item
                        if isinstance(subitem, Decl):
                            lines.append(child_prefix + ("└── " if sub_is_last else "├── ") + f"DECL: {subitem.var_type} {subitem.name}")
                        elif isinstance(subitem, Assign):
                            lines.append(child_prefix + ("└── " if sub_is_last else "├── ") + "INIT_ASSIGN")
                            lines.extend(self.generate_ast_tree(subitem, indent + 1, sub_is_last, child_prefix + ("    " if sub_is_last else "│   ")))
                else:
                    lines.extend(self.generate_ast_tree(
                        item, indent + 1, is_last_item, 
                        child_prefix + ("    " if is_last_item else "│   ")
                    ))
        
        elif isinstance(node, Decl):
            lines.append(current_prefix + f"DECL: {node.var_type} {node.name}")
        
        elif isinstance(node, Assign):
            lines.append(current_prefix + f"ASSIGN: {node.name}")
            if node.expr:
                lines.extend(self.generate_ast_tree(node.expr, indent + 1, True, prefix + ("    " if is_last else "│   ")))
        
        elif isinstance(node, If):
            lines.append(current_prefix + "IF")
            child_prefix = prefix + ("    " if is_last else "│   ")
            lines.append(child_prefix + "├── CONDITION")
            lines.extend(self.generate_ast_tree(node.cond, indent + 1, False, child_prefix + "│   "))
            lines.append(child_prefix + "├── THEN")
            lines.extend(self.generate_ast_tree(node.then_stmt, indent + 1, node.else_stmt is None, child_prefix + "│   "))
            if node.else_stmt:
                lines.append(child_prefix + "└── ELSE")
                lines.extend(self.generate_ast_tree(node.else_stmt, indent + 1, True, child_prefix + "    "))
        
        elif isinstance(node, While):
            lines.append(current_prefix + "WHILE")
            child_prefix = prefix + ("    " if is_last else "│   ")
            lines.append(child_prefix + "├── CONDITION")
            lines.extend(self.generate_ast_tree(node.cond, indent + 1, False, child_prefix + "│   "))
            lines.append(child_prefix + "└── BODY")
            lines.extend(self.generate_ast_tree(node.body, indent + 1, True, child_prefix + "    "))
        
        elif isinstance(node, For):
            lines.append(current_prefix + "FOR")
            child_prefix = prefix + ("    " if is_last else "│   ")
            if node.init:
                lines.append(child_prefix + "├── INIT")
                if isinstance(node.init, list):
                    for init_item in node.init:
                        lines.extend(self.generate_ast_tree(init_item, indent + 1, False, child_prefix + "│   "))
                else:
                    lines.extend(self.generate_ast_tree(node.init, indent + 1, False, child_prefix + "│   "))
            if node.cond:
                lines.append(child_prefix + "├── CONDITION")
                lines.extend(self.generate_ast_tree(node.cond, indent + 1, node.post is None, child_prefix + "│   "))
            if node.post:
                lines.append(child_prefix + "├── POST")
                lines.extend(self.generate_ast_tree(node.post, indent + 1, True, child_prefix + "│   "))
            lines.append(child_prefix + "└── BODY")
            lines.extend(self.generate_ast_tree(node.body, indent + 1, True, child_prefix + "    "))
        
        elif isinstance(node, Return):
            lines.append(current_prefix + "RETURN")
            if node.expr:
                lines.extend(self.generate_ast_tree(node.expr, indent + 1, True, prefix + ("    " if is_last else "│   ")))
        
        elif isinstance(node, ExprStmt):
            lines.append(current_prefix + "EXPR_STMT")
            if node.expr:
                lines.extend(self.generate_ast_tree(node.expr, indent + 1, True, prefix + ("    " if is_last else "│   ")))
        
        elif isinstance(node, Binary):
            lines.append(current_prefix + f"BINARY: {node.op}")
            child_prefix = prefix + ("    " if is_last else "│   ")
            lines.append(child_prefix + "├── LEFT")
            lines.extend(self.generate_ast_tree(node.left, indent + 1, False, child_prefix + "│   "))
            lines.append(child_prefix + "└── RIGHT")
            lines.extend(self.generate_ast_tree(node.right, indent + 1, True, child_prefix + "    "))
        
        elif isinstance(node, Unary):
            lines.append(current_prefix + f"UNARY: {node.op}")
            if node.expr:
                lines.extend(self.generate_ast_tree(node.expr, indent + 1, True, prefix + ("    " if is_last else "│   ")))
        
        elif isinstance(node, VarRef):
            lines.append(current_prefix + f"VAR: {node.name}")
        
        elif isinstance(node, IntConst):
            lines.append(current_prefix + f"INT: {node.value}")
        
        elif isinstance(node, FloatConst):
            lines.append(current_prefix + f"FLOAT: {node.value}")
        
        elif isinstance(node, Call):
            lines.append(current_prefix + f"CALL: {node.name}")
            for arg in node.args:
                lines.extend(self.generate_ast_tree(arg, indent + 1, True, prefix + ("    " if is_last else "│   ")))
        
        else:
            lines.append(current_prefix + f"UNKNOWN({type(node).__name__})")
        
        return lines

    def write_syntax_output(self, program, filename='syntax_output.txt'):
        """Write syntax analysis output."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Syntax Analyzer's Output:\n\n")
            f.write("Result: SUCCESS - No syntax errors found.\n\n")
            f.write("Abstract Syntax Tree (AST):\n")
            f.write("=" * 50 + "\n")
            
            ast_lines = self.generate_ast_tree(program)
            for line in ast_lines:
                f.write(line + "\n")
        
        print("Wrote syntax output to", filename)