from pycparser import c_ast

# -----------------------
# Constant Folding
# -----------------------

def fold_constants(ast):
    from pycparser import c_ast

    class Folder(c_ast.NodeVisitor):
        def __init__(self):
            self.constants = {}
            self.loop_vars = set()
            self.assigned = set()
            self.in_condition = False

        def visit_For(self, node):
            self._collect_loop_vars(node.init)
            self.visit(node.init)
            self._enter_condition()
            self.visit(node.cond)
            self._exit_condition()
            self.visit(node.next)
            self.visit(node.stmt)

        def visit_While(self, node):
            self._enter_condition()
            self.visit(node.cond)
            self._exit_condition()
            self.visit(node.stmt)

        def visit_If(self, node):
            self._enter_condition()
            self.visit(node.cond)
            self._exit_condition()
            self.visit(node.iftrue)
            self.visit(node.iffalse)

        def visit_Decl(self, node):
            if node.init:
                node.init = self._replace_expr(node.init)
                if (
                    isinstance(node.init, c_ast.Constant)
                    and node.name not in self.loop_vars
                    and node.name not in self.assigned
                    and not self.in_condition
                ):
                    self.constants[node.name] = node.init.value

        def visit_Assignment(self, node):
            node.rvalue = self._replace_expr(node.rvalue)
            if isinstance(node.lvalue, c_ast.ID):
                varname = node.lvalue.name
                self.assigned.add(varname)
                if (
                    isinstance(node.rvalue, c_ast.Constant)
                    and varname not in self.loop_vars
                    and not self.in_condition
                ):
                    # Only add to constants if never reassigned before
                    self.constants[varname] = node.rvalue.value

        def _replace_expr(self, expr):
            if isinstance(expr, c_ast.ID):
                if (
                    not self.in_condition
                    and expr.name in self.constants
                    and expr.name not in self.loop_vars
                    and expr.name not in self.assigned
                ):
                    return c_ast.Constant(type='int', value=self.constants[expr.name])
                return expr

            elif isinstance(expr, c_ast.BinaryOp):
                expr.left = self._replace_expr(expr.left)
                expr.right = self._replace_expr(expr.right)
                if isinstance(expr.left, c_ast.Constant) and isinstance(expr.right, c_ast.Constant):
                    return self._eval_binary(expr.left, expr.op, expr.right) or expr
            return expr

        def _eval_binary(self, left, op, right):
            try:
                result = eval(f"{left.value} {op} {right.value}")
                return c_ast.Constant(type='int', value=str(int(result)))
            except:
                return None

        def _enter_condition(self):
            self.in_condition = True

        def _exit_condition(self):
            self.in_condition = False

        def _collect_loop_vars(self, init):
            if isinstance(init, c_ast.DeclList):
                for decl in init.decls:
                    if isinstance(decl, c_ast.Decl):
                        self.loop_vars.add(decl.name)
            elif isinstance(init, c_ast.Assignment) and isinstance(init.lvalue, c_ast.ID):
                self.loop_vars.add(init.lvalue.name)

    # Run folder multiple times if needed (until stable)
    folder = Folder()
    prev_constants = {}

    while True:
        folder.visit(ast)
        if folder.constants == prev_constants:
            break
        prev_constants = dict(folder.constants)

# -----------------------
# Dead Code Elimination
# -----------------------

def remove_dead_code(ast):
    used_vars = set()

    class UsageCollector(c_ast.NodeVisitor):
        def visit_ID(self, node):
            used_vars.add(node.name)

    class DeadCodeCleaner(c_ast.NodeVisitor):
        def visit_Compound(self, node):
            new_block_items = []
            for stmt in node.block_items or []:
                if isinstance(stmt, c_ast.If) and isinstance(stmt.cond, c_ast.Constant):
                    if stmt.cond.value == '0':
                        continue
                    elif stmt.cond.value == '1' and isinstance(stmt.iftrue, c_ast.Compound):
                        new_block_items.extend(stmt.iftrue.block_items or [])
                        continue
                if isinstance(stmt, c_ast.While) and isinstance(stmt.cond, c_ast.Constant) and stmt.cond.value == '0':
                    continue
                if isinstance(stmt, c_ast.Decl) and stmt.name not in used_vars:
                    continue
                new_block_items.append(stmt)
                if isinstance(stmt, c_ast.Return):
                    break
            node.block_items = new_block_items

    UsageCollector().visit(ast)
    DeadCodeCleaner().visit(ast)

# -----------------------
# Strength Reduction
# -----------------------

def strength_reduction(ast):
    class StrengthReducer(c_ast.NodeVisitor):
        def visit_BinaryOp(self, node):
            self.generic_visit(node)
            if node.op in ['*', '/']:
                if isinstance(node.left, c_ast.ID) and isinstance(node.right, c_ast.Constant):
                    var, const = node.left, node.right
                elif isinstance(node.right, c_ast.ID) and isinstance(node.left, c_ast.Constant):
                    var, const = node.right, node.left
                else:
                    return
                try:
                    val = int(const.value)
                    if val > 0 and (val & (val - 1)) == 0:
                        shift = val.bit_length() - 1
                        node.op = '<<' if node.op == '*' else '>>'
                        node.left, node.right = var, c_ast.Constant(type='int', value=str(shift))
                except:
                    pass
    StrengthReducer().visit(ast)

# -----------------------
# Common Subexpression Elimination
# -----------------------

def eliminate_common_subexpressions(ast):
    class CSEVisitor(c_ast.NodeVisitor):
        def __init__(self):
            self.expr_map = {}
            self.counter = 0
            self.declared_vars = set()

        def visit_Compound(self, node):
            if not node.block_items:
                return
            new_block = []
            for stmt in node.block_items:
                inserts = []
                if isinstance(stmt, c_ast.Decl) and isinstance(stmt.init, c_ast.BinaryOp):
                    key = hash_expr(stmt.init)
                    deps = get_dependencies(stmt.init)
                    if all(dep in self.declared_vars for dep in deps):
                        if key in self.expr_map:
                            stmt.init = c_ast.ID(name=self.expr_map[key])
                        else:
                            temp_name = f"_t{self.counter}"
                            self.counter += 1
                            self.expr_map[key] = temp_name
                            inserts.append(make_decl(temp_name, stmt.init))
                            stmt.init = c_ast.ID(name=temp_name)
                if isinstance(stmt, c_ast.Decl):
                    self.declared_vars.add(stmt.name)
                new_block.extend(inserts)
                new_block.append(stmt)
            node.block_items = new_block

    CSEVisitor().visit(ast)

def hash_expr(expr):
    if isinstance(expr, c_ast.BinaryOp):
        return f"{hash_expr(expr.left)} {expr.op} {hash_expr(expr.right)}"
    elif isinstance(expr, c_ast.Constant):
        return expr.value
    elif isinstance(expr, c_ast.ID):
        return expr.name
    return str(expr)

def get_dependencies(expr):
    deps = set()
    class Walker(c_ast.NodeVisitor):
        def visit_ID(self, node): deps.add(node.name)
        def visit_BinaryOp(self, node):
            self.visit(node.left)
            self.visit(node.right)
    Walker().visit(expr)
    return deps

def make_decl(name, init_expr):
    return c_ast.Decl(
        name=name,
        quals=[],
        storage=[],
        funcspec=[],
        type=c_ast.TypeDecl(
            declname=name,
            quals=[],
            align=None,
            type=c_ast.IdentifierType(['int'])
        ),
        align=None,
        init=init_expr,
        bitsize=None
    )

# -----------------------
# Loop Invariant Code Motion
# -----------------------

def loop_invariant_code_motion(ast):
    class LICMVisitor(c_ast.NodeVisitor):
        def __init__(self):
            self.counter = 0
            self.loop_vars = set()

        def visit_For(self, node):
            if isinstance(node.init, c_ast.DeclList):
                for decl in node.init.decls:
                    self.loop_vars.add(decl.name)
            elif isinstance(node.init, c_ast.Assignment):
                if isinstance(node.init.lvalue, c_ast.ID):
                    self.loop_vars.add(node.init.lvalue.name)

            if isinstance(node.stmt, c_ast.Compound):
                self._process_loop_body(node.stmt)

            self.loop_vars.clear()

        def _process_loop_body(self, node):
            if not node.block_items:
                return
            new_items = []
            for stmt in node.block_items:
                if isinstance(stmt, c_ast.Decl) and isinstance(stmt.init, c_ast.BinaryOp):
                    if not self._depends_on_loop_vars(stmt.init):
                        temp_name = f"_t{self.counter}"
                        self.counter += 1
                        new_items.append(make_decl(temp_name, stmt.init))
                        stmt.init = c_ast.ID(name=temp_name)
                new_items.append(stmt)
            node.block_items = new_items

        def _depends_on_loop_vars(self, expr):
            class Checker(c_ast.NodeVisitor):
                def __init__(self, loop_vars):
                    self.loop_vars = loop_vars
                    self.found = False
                def visit_ID(self, node):
                    if node.name in self.loop_vars:
                        self.found = True
            checker = Checker(self.loop_vars)
            checker.visit(expr)
            return checker.found

    LICMVisitor().visit(ast)

# -----------------------
# Optimize C AST
# -----------------------

def optimize_c_ast(ast):
    fold_constants(ast)
    eliminate_common_subexpressions(ast)
    strength_reduction(ast)
    loop_invariant_code_motion(ast)
    remove_dead_code(ast)
