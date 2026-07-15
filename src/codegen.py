class Scope:
    def __init__(self, name):
        self.name = name
        self.offsets = {}
        self.next_idx = 0

    def allocate(self, name, size=1):
        offset = self.next_idx
        self.offsets[name] = offset
        self.next_idx += size
        return offset
    
    def set_offset(self, name, offset):
        self.offsets[name] = offset

    def get_offset(self, name):
        return self.offsets[name]



class CodeGen:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.code = []
        self.label_counter = 0
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.total_global_cells = 0

    def emit(self, instruction):
        self.code.append(instruction)
    
    def new_label(self, prefix):
        self.label_counter += 1
        return f"L{prefix}{self.label_counter}"
    
    def emit_label(self, name):
        self.emit(f"{name}:")

    def fortran_label(self, n):
        return f"Lfortran{n}"
    
    def get_code(self):
        return "\n".join(self.code)
    
    
    
    
    def gen_CompilationUnit(self, node):
        self.setup_program_scope()
        
        if self.total_global_cells > 0:
            self.emit(f"pushn {self.total_global_cells}")

        self.emit("start")

        self.gen_Program(node.program)

        self.emit("stop")

        for func in node.functions:
            self.gen_Function(func)
    
    def gen_Program(self, node):
        for stmt in node.body:
            self.gen_node(stmt)
    
    def gen_Function(self, node):
        previous_scope = self.current_scope

        function_scope = self.setup_function_scope(node)
        self.current_scope = function_scope

        self.emit_label(node.name)

        k = function_scope.next_idx
        if k > 0:
            self.emit(f"pushn {k}")
        
        for stmt in node.body:
            self.gen_node(stmt)
        
        self.current_scope = previous_scope

    
    
    
    def setup_program_scope(self):
        symbols = self.symbol_table["program"]["symbols"]

        for name, info in symbols.items():
            kind = info["kind"]

            if kind == "function_ref":
                continue

            size = info.get("size", 1)

            self.global_scope.allocate(name, size)

        self.total_global_cells = self.global_scope.next_idx

    
    def setup_function_scope(self, func_def):
        func_info = self.symbol_table["functions"][func_def.name]

        scope = Scope(func_def.name)

        params = func_info["params"]
        num_params = len(params)

        for i, param in enumerate(params):
            name = param["name"]
            offset = -(num_params - i)
            scope.set_offset(name, offset)

        locals_symbols = func_info["locals"]

        for name, info in locals_symbols.items():
            kind = info["kind"]

            if kind == "param":
                continue

            size = info.get("size", 1)
            scope.allocate(name, size)

        return scope
    
    
    

    def gen_node(self, node):
        node_type = type(node).__name__

        if node_type == "Assign":
            self.gen_Assign(node)

        elif node_type == "Print":
            self.gen_Print(node)

        elif node_type == "Read":
            self.gen_Read(node)

        elif node_type == "If":
            self.gen_If(node)

        elif node_type == "DoLoop":
            self.gen_DoLoop(node)

        elif node_type == "Goto":
            self.gen_Goto(node)

        elif node_type == "Label":
            self.gen_Label(node)

        elif node_type == "Continue":
            self.gen_Continue(node)

        elif node_type == "Return":
            self.gen_Return(node)

        elif node_type == "Declaration":
            pass

        else:
            raise NotImplementedError(f"Unsupported statement node: {node_type}")
    



    def gen_Assign(self, node):
        target = node.target
        value = node.value

        target_type = type(target).__name__

        if target_type == "Var":
            self.gen_expr(value)
            self.emit_store_var(target.name)
        
        elif target_type == "ArrayAccess":
            self.gen_array_address(target)
            self.gen_expr(value)
            self.emit("store 0")

        else:
            raise NotImplementedError(f"Unsupported assignment target: {target_type}")
    
    def gen_Print(self, node):
        for item in node.items:
            item_type = type(item).__name__

            if item_type == "StringLiteral":
                self.gen_StringLiteral(item)
                self.emit("writes")

            else:
                self.gen_expr(item)

                if item.result_type == "real":
                    self.emit("writef")
                else:
                    self.emit("writei")

        self.emit("writeln")
    
    def gen_Read(self, node):
        for target in node.targets:
            self.gen_read_target(target)
    
    def gen_read_target(self, target):
        target_type = type(target).__name__

        if target_type == "Var":
            self.gen_read_var(target)
        
        elif target_type == "ArrayAccess":
            self.gen_read_array(target)

        else:
            raise NotImplementedError(f"Unsupported READ target: {target_type}")
    
    def gen_read_var(self, target):
        result_type = target.result_type

        self.emit("read")

        if result_type == "real":
            self.emit("atof")
        else:
            self.emit("atoi")

        self.emit_store_var(target.name)

    def gen_read_array(self, target):
        result_type = target.result_type

        self.gen_array_address(target)

        self.emit("read")

        if result_type == "real":
            self.emit("atof")
        else:
            self.emit("atoi")

        self.emit("store 0")
    
    def gen_If(self, node):
        has_else = hasattr(node, "else_body") and node.else_body

        if not has_else:
            end_label = self.new_label("ifend")

            self.gen_expr(node.condition)
            self.emit(f"jz {end_label}")

            for stmt in node.then_body:
                self.gen_node(stmt)

            self.emit_label(end_label)

        else:
            else_label = self.new_label("ifelse")
            end_label = self.new_label("ifend")

            self.gen_expr(node.condition)
            self.emit(f"jz {else_label}")

            for stmt in node.then_body:
                self.gen_node(stmt)

            self.emit(f"jump {end_label}")
            self.emit_label(else_label)

            for stmt in node.else_body:
                self.gen_node(stmt)

            self.emit_label(end_label)
    
    def gen_DoLoop(self, node):
        var_name = node.var

        self.gen_expr(node.start)

        self.emit_store_var(var_name)
        
        start_label = self.new_label("dostart")
        self.emit_label(start_label)
        
        end_label = self.new_label("doend")

        self.emit_load_var(var_name)
        self.gen_expr(node.end)
        self.emit("infeq")
        self.emit(f"jz {end_label}")

        for stmt in node.body:
            self.gen_node(stmt)

        self.emit_load_var(var_name)
        self.gen_expr(node.step)
        self.emit("add")

        self.emit_store_var(var_name)
        
        self.emit(f"jump {start_label}")
        
        self.emit_label(end_label)
    

    def gen_Goto(self, node):
        label = self.fortran_label(node.label)
        self.emit(f"jump {label}")
    
    def gen_Label(self, node):
        label = self.fortran_label(node.label)
        self.emit_label(label)
    
    def gen_Continue(self, node):
        pass

    def gen_Return(self, node):
        return_var_name = self.current_scope.name
        offset = self.current_scope.get_offset(return_var_name)

        self.emit(f"pushl {offset}")
        self.emit("return")
    
    
    
    
    def gen_expr(self, node):
        node_type = type(node).__name__

        if node_type == "IntLiteral":
            self.gen_IntLiteral(node)

        elif node_type == "RealLiteral":
            self.gen_RealLiteral(node)

        elif node_type == "LogicalLiteral":
            self.gen_LogicalLiteral(node)

        elif node_type == "StringLiteral":
            self.gen_StringLiteral(node)

        elif node_type == "Var":
            self.gen_Var(node)

        elif node_type == "ArrayAccess":
            self.gen_ArrayAccess(node)

        elif node_type == "FunctionCall":
            self.gen_FunctionCall(node)

        elif node_type == "BinOp":
            self.gen_BinOp(node)

        elif node_type == "UnaryOp":
            self.gen_UnaryOp(node)

        elif node_type == "Mod":
            self.gen_Mod(node)

        else:
            raise NotImplementedError(f"Unsupported expression node: {node_type}")
    
    
    
    
    def gen_IntLiteral(self, node):
        self.emit(f"pushi {node.value}")
    
    def gen_RealLiteral(self, node):
        self.emit(f"pushf {node.value}")
    
    def gen_LogicalLiteral(self, node):
        value = 1 if node.value else 0
        self.emit(f"pushi {value}")
    
    def gen_StringLiteral(self, node):
        self.emit(f'pushs "{node.value}"')
    
    def gen_Var(self, node):
        self.emit_load_var(node.name)
    
    def gen_ArrayAccess(self, node):
        self.gen_array_address(node)
        self.emit("load 0")
    
    def gen_array_address(self, node):
        name = node.name
        offset = self.current_scope.get_offset(name)

        if self.current_scope == self.global_scope:
            self.emit("pushgp")
        else:
            self.emit("pushfp")

        self.emit(f"pushi {offset}")
        self.emit("padd")

        self.gen_expr(node.index)
        self.emit("pushi 1")
        self.emit("sub")
        self.emit("padd")
    
    def gen_BinOp(self, node):
        op = node.op
        result_type = node.result_type

        self.gen_expr(node.left)
        self.gen_expr(node.right)

        if op == "+":
            self.emit("fadd" if result_type == "real" else "add")

        elif op == "-":
            self.emit("fsub" if result_type == "real" else "sub")

        elif op == "*":
            self.emit("fmul" if result_type == "real" else "mul")

        elif op == "/":
            self.emit("fdiv" if result_type == "real" else "div")
        
        elif op == "<":
            operand_type = node.left.result_type
            self.emit("finf" if operand_type == "real" else "inf")

        elif op == "<=":
            operand_type = node.left.result_type
            self.emit("finfeq" if operand_type == "real" else "infeq")

        elif op == ">":
            operand_type = node.left.result_type
            self.emit("fsup" if operand_type == "real" else "sup")

        elif op == ">=":
            operand_type = node.left.result_type
            self.emit("fsupeq" if operand_type == "real" else "supeq")
        
        elif op == "==":
            self.emit("equal")
        
        elif op == "!=":
            self.emit("equal")
            self.emit("not")
        
        elif op == "AND":
            self.emit("and")

        elif op == "OR":
            self.emit("or")
        
        else:
            raise NotImplementedError(f"Unsupported binary operator: {op}")
        
    def gen_UnaryOp(self, node):
        op = node.op
        result_type = node.result_type

        self.gen_expr(node.operand)

        if op == "NOT":
            self.emit("not")

        elif op == "-":
            if result_type == "real":
                self.emit("pushf -1.0")
                self.emit("fmul")
            else:
                self.emit("pushi -1")
                self.emit("mul")

        else:
            raise NotImplementedError(f"Unsupported unary operator: {op}")
    
    def gen_Mod(self, node):
        self.gen_expr(node.left)
        self.gen_expr(node.right)
        self.emit("mod")
    
    def gen_FunctionCall(self, node):
        for arg in node.args:
            self.gen_expr(arg)
        
        self.emit(f"pusha {node.name}")
        self.emit("call")
    


    def emit_load_var(self, name):
        offset = self.current_scope.get_offset(name)

        if self.current_scope == self.global_scope:
            self.emit(f"pushg {offset}")
        else:
            if offset >= 0:
                self.emit(f"pushl {offset}")
            else:
                self.emit("pushfp")
                self.emit(f"load {offset}")
    
    def emit_store_var(self, name):
        offset = self.current_scope.get_offset(name)

        if self.current_scope == self.global_scope:
            self.emit(f"storeg {offset}")
        else:
            if offset >= 0:
                self.emit(f"storel {offset}")
            else:
                raise NotImplementedError("Assignment to parameters is not supported")

        

def generate(ast, symbol_table):
    cg = CodeGen(symbol_table)
    cg.gen_CompilationUnit(ast)
    return cg.get_code()