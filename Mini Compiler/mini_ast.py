class Program:
    def __init__(self, functions):
        self.functions = functions

class Function:
    def __init__(self, ret_type, name, params, body, lineno=0):
        self.ret_type = ret_type
        self.name = name
        self.params = params
        self.body = body
        self.lineno = lineno

class Compound:
    def __init__(self, decls, stmts):
        self.decls = decls
        self.stmts = stmts

class Decl:
    def __init__(self, var_type, name, lineno=0):
        self.var_type = var_type
        self.name = name
        self.lineno = lineno

class If:
    def __init__(self, cond, then_stmt, else_stmt=None):
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class While:
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

class For:
    def __init__(self, init, cond, post, body):
        self.init = init
        self.cond = cond
        self.post = post
        self.body = body

class Return:
    def __init__(self, expr):
        self.expr = expr

class ExprStmt:
    def __init__(self, expr):
        self.expr = expr

class Assign:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class Binary:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class Unary:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class VarRef:
    def __init__(self, name):
        self.name = name

class IntConst:
    def __init__(self, value):
        self.value = value

class FloatConst:
    def __init__(self, value):
        self.value = value

class Call:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Cast:
    def __init__(self, target_type, expr):
        self.target_type = target_type
        self.expr = expr

def pretty_print(node, indent=0):
    """Returns a list of formatted lines representing the AST tree."""
    lines = []
    prefix = ' ' * indent

    if isinstance(node, Program):
        lines.append(prefix + "Program:")
        for fn in node.functions:
            lines.extend(pretty_print(fn, indent + 2))
    
    elif isinstance(node, Function):
        lines.append(prefix + f"Function: {node.ret_type} {node.name}")
        for ptype, pname in node.params:
            lines.append(prefix + f"  Param: {ptype} {pname}")
        lines.extend(pretty_print(node.body, indent + 2))
    
    elif isinstance(node, Compound):
        lines.append(prefix + "Compound Block:")
        for d in node.decls:
            lines.extend(pretty_print(d, indent + 2))
        for s in node.stmts:
            lines.extend(pretty_print(s, indent + 2))
    
    elif isinstance(node, Decl):
        lines.append(prefix + f"Decl: {node.var_type} {node.name}")
    
    elif isinstance(node, If):
        lines.append(prefix + "If:")
        lines.append(prefix + "  Condition:")
        lines.extend(pretty_print(node.cond, indent + 4))
        lines.append(prefix + "  Then:")
        lines.extend(pretty_print(node.then_stmt, indent + 4))
        if node.else_stmt:
            lines.append(prefix + "  Else:")
            lines.extend(pretty_print(node.else_stmt, indent + 4))
    
    elif isinstance(node, While):
        lines.append(prefix + "While:")
        lines.append(prefix + "  Condition:")
        lines.extend(pretty_print(node.cond, indent + 4))
        lines.append(prefix + "  Body:")
        lines.extend(pretty_print(node.body, indent + 4))
    
    elif isinstance(node, For):
        lines.append(prefix + "For:")
        if node.init:
            lines.append(prefix + "  Init:")
            lines.extend(pretty_print(node.init, indent + 4))
        if node.cond:
            lines.append(prefix + "  Cond:")
            lines.extend(pretty_print(node.cond, indent + 4))
        if node.post:
            lines.append(prefix + "  Post:")
            lines.extend(pretty_print(node.post, indent + 4))
        lines.append(prefix + "  Body:")
        lines.extend(pretty_print(node.body, indent + 4))
    
    elif isinstance(node, Return):
        lines.append(prefix + "Return:")
        if node.expr:
            lines.extend(pretty_print(node.expr, indent + 2))
    
    elif isinstance(node, ExprStmt):
        lines.append(prefix + "ExprStmt:")
        if node.expr:
            lines.extend(pretty_print(node.expr, indent + 2))
    
    elif isinstance(node, Assign):
        lines.append(prefix + f"Assign: {node.name} =")
        lines.extend(pretty_print(node.expr, indent + 2))
    
    elif isinstance(node, Binary):
        lines.append(prefix + f"Binary: {node.op}")
        lines.append(prefix + "  Left:")
        lines.extend(pretty_print(node.left, indent + 4))
        lines.append(prefix + "  Right:")
        lines.extend(pretty_print(node.right, indent + 4))
    
    elif isinstance(node, Unary):
        lines.append(prefix + f"Unary: {node.op}")
        lines.extend(pretty_print(node.expr, indent + 2))
    
    elif isinstance(node, VarRef):
        lines.append(prefix + f"VarRef: {node.name}")
    
    elif isinstance(node, IntConst):
        lines.append(prefix + f"IntConst: {node.value}")
    
    elif isinstance(node, FloatConst):
        lines.append(prefix + f"FloatConst: {node.value}")
    
    elif isinstance(node, Call):
        lines.append(prefix + f"Call: {node.name}")
        for arg in node.args:
            lines.extend(pretty_print(arg, indent + 4))
    
    elif isinstance(node, Cast):
        lines.append(prefix + f"Cast: ({node.target_type})")
        lines.extend(pretty_print(node.expr, indent + 2))
    
    return lines