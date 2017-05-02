import symtable as st
import tac
from inspect import currentframe, getframeinfo
from collections import OrderedDict


frameinfo = getframeinfo(currentframe())
literal_decl = []

class CodeGen:
    def __init__ (self, TAC):
        self.TAC = TAC
        self.label = 'L_'
        self.labels = list(set(tac.labels))
       # print("tttttttttttttttttttttt", self.labels)
        self.main = []              # Main section
        self.functions = []         # Fucntion definitions
        self.data = []              # Data section
        self.bss = []               # BSS section
        self.global_ids = OrderedDict()
        self.local_ids = OrderedDict()
        self.map_type = {str : "char", float : "float", int : "int"}
        self.syscall = {
                    "print_int"     : "1",
                    "print_float"   : "2",
                    "print_double"  : "3",
                    "print_string"  : "4",
                    "read_int"      : "5",
                    "read_float"    : "6",
                    "read_double"   : "7",
                    "read_string"   : "8",
                    "sbrk"          : "9",  # Heap allocation
                    "exit"          : "10",
        }
        self.relops = {
                    "=="    : ["beq", "c.eq.s", "bc1t", "=="],
                    "<"     : ["blt", "c.lt.s", "bc1t", ">"],
                    "<="    : ["ble", "c.le.s", "bc1t", ">="],
                    ">"     : ["bgt", "c.le.s", "bc1f", "<"],
                    ">="    : ["bge", "c.lt.s", "bc1f", "<="],
                    "!="    : ["bne", "c.eq.s", "bc1f", "!="],
        }
        self.reg_dict()
        self.get_global_ids("global")

    def reg_dict(self):
        # (values) from expression evaluation and function results
        self.value_regs = { "$v0" : None, "$v1" : None }

        # (arguments) First four parameters for subroutine (Not preserved across procedure calls)
        self.arg_regs  = { "$a0" : None, "$a1" : None, "$a2" : None, "$a3" : None }

        # reserved for use by the interrupt/trap handler
        self.trap_regs = { "$k0" : None, "$k1" : None }

        # (temporaries) Caller saved if needed. Subroutines can use w/out saving (Not preserved across procedure calls)
        self.temp_regs = dict()
        for i in range(10):  self.temp_regs.update({ '$t' + str(i) : [] })

        # (saved values) - Callee saved (Preserved across procedure calls)
        self.saved_regs = dict()
        for i in range(8):  self.temp_regs.update({ '$s' + str(i) : [] })

        self.pointer_regs = { "$gp" : None, "$sp" : None, "$fp" : None, "ra" : None }

        self.general_regs = {**self.temp_regs, **self.saved_regs}

        # Floating point registers
        self.float_regs = dict()
        for i in range(1,24):  self.float_regs.update({ '$f' + str(i) : [] })

        # Used-Unused Regs
        self.unused_gen_regs = list(self.general_regs.keys())
        self.used_gen_regs = []

        self.unused_float_regs = list(self.float_regs.keys())
        self.used_float_regs = []

        pass

    def get_global_ids(self, scope_name):
        table = st.ScopeList[scope_name]["table"].symtab
        for k in table:
            if table[k]["id_type"] not in [ "function","namespace", "class", "struct", "union",]:
                self.global_ids.update({ table[k]["tac_name"] : dict(register=None, location=table[k]["tac_name"], offset=0, type=st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"]) })
            if table[k]["id_type"]  in [ "function"]:
                self.global_ids.update({ table[k]["name"] : dict(register=None, location=table[k]["tac_name"], offset=table[k]["offset"], type=st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"]) })

    def get_local_ids(self, scope_name):
        self.local_ids.clear()
        scope_q = [str(scope_name)]
        while len(scope_q) != 0:
            _scope = scope_q.pop(0)
            table = st.ScopeList[_scope]["table"].symtab
            for k in table:
                offset=(table[k]["offset"] - table[k]["size"])  if table[k]["offset"] > 0 else table[k]["offset"]
                if table[k]["id_type"] not in ["function", "namespace", "class", "struct", "union",]:
                    loc = table[k]["tac_name"] if scope_name == "main" else "($sp)"
                    self.local_ids.update({ table[k]["tac_name"] : dict(register=None, location=loc, offset=table[k]["offset"] , size=table[k]["size"], type=st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"]) })
            for s in st.ScopeList:
                if s != "NULL":
                    if st.ScopeList[s].get("parent") == _scope:
                        scope_q.append(str(s))
        size = 0
        for i in reversed(self.local_ids):
            size = self.local_ids[i]["offset"]
            break
        for j in self.local_ids:
            if self.local_ids[j]['location'] == "($sp)":
                if self.local_ids[j]["offset"] < 0:
                    self.local_ids[j]["location"] = str(size - self.local_ids[j]["offset"] ) + "($sp)"
                else:
                    self.local_ids[j]["location"] = str(size - self.local_ids[j]["offset"] + self.local_ids[j]["size"] ) + "($sp)"
        #print(size)
        #print(self.local_ids)
        #print("\n\n")
        pass


    def check_in_register(self, name):
        if name in self.local_ids:
            return self.local_ids[name].get("register",None)

        if name in self.global_ids:
            return self.global_ids[name].get("register",None)
        return None

    def get_register2(self, name, ltype, code_list, forbid_list=[]):

        pass

    def get_register(self, name, ltype, code_list, forbid_list=[]):
        """if self.check_in_register(name) :
            reg = self.check_in_register(name)
            self.spill_register(reg,code_list,[name])
            if ltype in ["double", "float"]:
                self.used_float_regs.remove(reg)
                self.used_float_regs.append(reg)
            else:
                self.used_gen_regs.remove(reg)
                self.used_gen_regs.append(reg)

            return reg
        else :"""
        if ltype in ["double", "float"]:
            if len(self.unused_float_regs) > 0:
                reg = self.unused_float_regs[0]
                self.unused_float_regs.remove(reg)
                self.used_float_regs.append(reg)

            else:
                print("Float Register FULL !!", frameinfo.lineno)
                for l in self.used_float_regs:
                    if l not in forbid_list:
                        reg = l
                        if l in self.unused_float_regs:
                            self.unused_float_regs.remove(l)
                        self.used_float_regs.remove(reg)
                        self.used_float_regs.append(reg)
                        self.spill_register(reg,code_list)
                        break
            if name != "NULL":
                self.float_regs[reg] = [name]
        else:
            if len(self.unused_gen_regs) > 0:
                reg = self.unused_gen_regs[0]
                self.unused_gen_regs.remove(reg)
                self.used_gen_regs.append(reg)
            else:
                print("INT Register FULL !!", frameinfo.lineno)

                for l in self.used_gen_regs:
                    if l not in forbid_list:
                        reg = l
                        if l in self.unused_gen_regs:
                            self.unused_gen_regs.remove(l)
                        self.used_gen_regs.remove(reg)
                        self.used_gen_regs.append(reg)
                        self.spill_register(reg,code_list)
                        break
            if name != "NULL":
                self.general_regs[reg] = [name]

        if name != "NULL":
            if name in self.local_ids:
                self.local_ids[name]["register"] = reg
                loc = self.local_ids[name]["location"]

            elif name in self.global_ids:
                self.global_ids[name]["register"] = reg
                loc = self.global_ids[name]["location"]
            else:
                loc = name

            self.load_variable(ltype,ltype,reg, loc ,code_list)
        #print("GET REGISTER: ", reg,name, len(self.unused_gen_regs), "used: ", len(self.used_gen_regs))
        return reg


    def spill_register(self, reg, code_list, skip=[]):
        print("SPILL register FULL !!", frameinfo.lineno)

        if reg in self.general_regs:
            for var in self.general_regs[reg]:
                print("spill_register", reg, var)
                if var not in skip and var != "NULL":
                    if self.local_ids.get(var,None):
                        loc = self.local_ids[var]["location"]
                    else:
                        loc = self.global_ids[var]["location"]
                    code_list.append(["sw", reg + ",", loc])


        elif reg in self.float_regs:
            for var in self.float_regs[reg]:
                if var not in skip:
                    if self.local_ids.get(var,None):
                        loc = self.local_ids[var]["location"]
                    else:
                        loc = self.global_ids[var]["location"]
                    code_list.append(["s.s", reg + ",", loc])

        else:
            print("Wrong Register Name",reg,self.general_regs)

        return

    def callee_seq(self,size,code_list):
        code_list.append(["addi", "$sp" + ",", "$sp" + ",", "-" + str(size)])            #Allocate space for local data
        code_list.append(["sw", "$ra" + ",", "0($sp)"])                             #Store return address
        code_list.append(["sw", "$fp" + ",", "-4($sp)"])                         #Store Stack pointer
        code_list.append(["addu", "$fp" + ",", "$0" + ",","$sp"])                    #Update frame pointer
        return


    def return_seq(self,code_list):
        self.clear_regs()
        code_list.append(["lw", "$ra" + ",", "0($sp)"])                             #Restore return address
        code_list.append(["lw", "$fp" + ",", "-4($sp)"])                             #Restore frame pointer
        #code_list.append(["addi", "$sp" + ",", "$sp" + ",", str(size)])             #Restore stack pointer

        return

    def clear_regs(self):
        for reg in self.general_regs:
            if reg in self.used_gen_regs:
                self.general_regs[reg] = []
                self.used_gen_regs.remove(reg)
                self.unused_gen_regs.append(reg)
        for reg in self.float_regs:
            if reg in self.used_float_regs:
                self.float_regs[reg] = []
                self.used_float_regs.remove(reg)
                self.unused_float_regs.append(reg)
        return

    def caller_seq(self,name,code_list):

        return

    def push_params(self,name,code_list):

        return

    def parse_tac(self):
        inside_func = False
        is_main = False
        param_start =False
        for i, quad in enumerate(self.TAC.code):
          #  print(self.general_regs)
            if quad[0] in ["function"]:
                inside_func = True
                self.get_local_ids(quad[1])
                #print(quad,self.local_ids)
                #print(quad,self.local_ids,"\n\n")


                if quad[1] == "main":
                    code_list = self.main       # reference main code list
                    is_main = True
                else:
                    code_list = self.functions  # reference functions code list
                    is_main = False
                    size = 0
                    for j in reversed(self.local_ids):
                        size = self.local_ids[j]["offset"]
                        break
                    code_list.append([quad[1] + ":"])
                    self.callee_seq(size,code_list)

            else:
                if not inside_func:     # TAC of Global scope
                    continue
                if str(i) in self.labels:
                    self.labels.remove(str(i))
                    code_list.append([self.label + str(i) + ":"])
                if quad[0] in ["end"]:
                    inside_func = False
                    size = 0
                    for i in reversed(self.local_ids):
                        size = self.local_ids[i]["offset"]
                        break
                    self.return_seq(code_list)
                    if is_main:
                        is_main = False
                        code_list.append(["li", "$v0" + ",", self.syscall["exit"]])
                        code_list.append(["syscall"])
                    else:
                        code_list.append(["jr", "$ra"])
                elif quad[0] == "param":
                    if param_start == False:
                        param_start = True
                        code_list.append(["addu", "$fp" + ",", "$sp" + ",","$0"])
                        #if not is_main:
                        #    code_list.append(["addi", "$sp" + ",", "$sp" + ",","-8"])

                        code_list.append(["addi", "$a0" + ",", "$sp" + ",","-8"])                    #Preserve frame pointer
                    reg = self.get_register(quad[2],quad[1],code_list)
                    if quad[1] in ["float", "double"]:
                        code_list.append(["swc1", reg + ",", "0($a0)"])                    #Push Parameters
                    else:
                        code_list.append(["sw", reg + ",", "0($a0)"])                    #Push Parameters
                    code_list.append(["addi", "$a0" + ",", "$a0" + ",","-4"])
                    pass

                elif quad[0] == "call":
                    param_start = False
                    """for reg in self.general_regs:
                        self.spill_register(reg,code_list)
                    for reg in self.float_regs:
                        self.spill_register(reg,code_list)                     # Write all registers back
                    """
                    #if int(quad[3])%2 == 1:
                    #    code_list.append(["addi", "$a0" + ",", "$a0" + ",", "-4"])                    #Padding as $sp is always multiple of 8
                    code_list.append(["addu", "$sp" + ",", "$a0" + ",","$0"])
                    #code_list.append(["addi", "$sp" + ",", "$a0" + ",","-4"])
                    code_list.append(["jal", quad[1]])                    #Update frame pointer
                    pass

                elif quad[1] == "^retval":
                    code_list.append(["addu", "$sp" + ",", "$fp" + ",","$0"])
                    self.handle_assignment(quad, code_list)
                    pass

                elif quad[0] == "ret":
                    qtype = self.local_ids[quad[1]]["type"] if quad[1] in self.local_ids else self.global_ids[quad[1]]["type"]
                    reg = self.get_register(quad[1], qtype, code_list)
                    if qtype in ["float", "double"]:
                        code_list.append(["mov.s", "$f0" + ",", reg])                    #Update frame pointer
                    else:
                        code_list.append(["addu", "$v1" + ",", reg + ",","$0"])                    #Update frame pointer
                    self.return_seq(code_list)
                    if is_main:
                        code_list.append(["li", "$v0" + ",", self.syscall["exit"]])
                        code_list.append(["syscall"])
                    else:
                        code_list.append(["jr", "$ra"])

                elif quad[0] == "cout":
                    print("COUT: ", quad)
                    self.print_stdout(quad[1], quad[2], code_list)
                elif quad[0] == "if":
                    self.op_codes(self.label + str(quad[5]), None, quad[1], quad[2], quad[3], code_list)
                elif quad[0] == "goto":
                    line = eval(quad[1])
                    while self.TAC.code[line][0] == "goto":
                        print(quad)
                        line = eval(self.TAC.code[line][1])
                    label = self.label + str(line)
                    code_list.append(["b", label])
                else:   # Assignment
                    self.handle_assignment(quad, code_list)
                self.unused_gen_regs += self.used_gen_regs
                self.used_gen_regs = list()
                self.unused_float_regs += self.used_float_regs
                self.used_float_regs = list()
        pass

    def handle_assignment(self, quad, code_list):

        op, lvalue, optype = self.eval_lvalue(quad[0], code_list)
        ltype = self.local_ids[op]["type"] if op in self.local_ids else self.global_ids[op]["type"]
        if lvalue is None:
            lvalue = self.get_register(quad[0], ltype, code_list)


        if quad[2] == '':   # simple assignment if quad is like ['var', '7', '', '']

            if quad[1] == '^retval':
                if ltype in ["float", "double"]:
                    rvalue, var, reg = quad[1],True,"$f0"
                else:
                    rvalue, var, reg = quad[1],True,"$v1"
            else:
                rvalue, var, reg = self.eval_operand(quad[1], code_list)
            if var:
                if quad[1] == "^retval":
                    rtype = ltype
                else:
                    rtype = self.local_ids[rvalue]["type"] if rvalue in self.local_ids else self.global_ids[rvalue]["type"]
                if reg:
                    if optype == "write_back":
                        self.write_back(ltype, lvalue, rtype, reg, code_list)
                    else:
                        self.move_variable(ltype, rtype, lvalue, reg, code_list)
                        self.write_back(ltype, op, ltype, lvalue, code_list)
                else:
                    if optype == "write_back":
                        reg = self.get_register(rvalue, rtype, code_list)
                        self.write_back(ltype, lvalue, rtype, reg, code_list)
                    else:
                        if rvalue in self.local_ids:
                            loc = self.local_ids[rvalue]["location"]
                        else:
                            loc = self.global_ids[rvalue]["location"]
                        self.load_variable(ltype, rtype, lvalue, loc, code_list)
                        self.write_back(ltype, op, ltype, lvalue, code_list)

            else:
                if optype == "write_back":
                    reg = self.get_register("NULL", self.map_type[type(rvalue)], code_list)
                    self.load_immediate(ltype, type(rvalue), reg, rvalue, code_list)
                    self.write_back(ltype, lvalue, ltype, reg, code_list)
                else:
                    self.load_immediate(ltype, type(rvalue), lvalue, rvalue, code_list)
                    self.write_back(ltype, op, ltype, lvalue, code_list)
        else:
            if optype == "write_back":
                print("Something is Wrong", frameinfo.filename, frameinfo.lineno)

            if quad[2] == "++":
                self.add_int(ltype, lvalue, ltype, lvalue, "int", "1", code_list, imm="get_r2")
            elif quad[2] == "--":
                self.add_int(ltype, lvalue, ltype, lvalue, "int", "-1", code_list, imm="get_r2")
            else:
                self.op_codes(lvalue, ltype, quad[1], quad[2], quad[3], code_list)
            self.write_back(ltype, op, ltype, lvalue, code_list)
        pass

    def write_back(self, ltype, lvalue, rtype, rvalue, code_list):
        #print("write_back", ltype, lvalue, rtype, rvalue)
        reg = str(rvalue)
        if ltype in ["float", "double"]:
            if rtype not in ["float", "double"]:    # $s or $t type register
                reg = self.get_register("NULL", "float", code_list)
                self.move_variable("float", rtype, reg, rvalue, code_list)
            loc = lvalue
            if "$" not in lvalue:
                if lvalue in self.local_ids:
                    loc = self.local_ids[lvalue]["location"]
                else:
                    loc = self.global_ids[lvalue]["location"]
            code_list.append(["s.s", reg + ",", loc])
            self.used_float_regs.remove(reg)
            self.unused_float_regs.append(reg)
        else:
            if rtype in ["float", "double"]:
                reg = self.get_register("NULL", "int", code_list)
                self.move_variable("int", rtype, reg, rvalue, code_list)
            loc = lvalue
            #print(reg, lvalue)
            if "$" not in lvalue:
                if lvalue in self.local_ids:
                    loc = self.local_ids[lvalue]["location"]
                else:
                    loc = self.global_ids[lvalue]["location"]
            code_list.append(["sw", reg + ",", loc])
            self.used_gen_regs.remove(reg)
            self.unused_gen_regs.append(reg)
        #print("============================", ltype, lvalue, rtype, rvalue, len(self.unused_gen_regs))
        pass

    def eval_lvalue(self, op, code_list):
        ptr = op.rfind("*") + 1
        arr = op.rfind("$") + 1
        if ptr > 0:
            otype = "write_back"
            op = op[ptr:]
            reg = self.get_register(op, "int", code_list)
            for p in range(ptr-1):
                self.load_variable("pointer", "pointer", reg, "(" + reg + ")", code_list)
            reg = "(" + reg + ")"
        elif arr > 0:
            otype = "write_back"
            op = op[arr:]
            op, offset = op.split("+")
            reg = self.load_address(op, code_list)
            if offset in self.local_ids or  offset in self.global_ids:
                oreg = self.get_register(offset, "int", code_list)
                code_list.append(["addu", reg + ",", reg + ",", oreg])
            else:
                code_list.append(["addi", reg + ",", reg + ",", offset])
            reg = "(" + reg + ")"
        else:
            otype = ""
            reg = None
        return op, reg, otype

    def op_codes(self, lvalue, ltype, op1, op, op2, code_list):
        e_op1, var1, reg1 = self.eval_operand(op1, code_list)
        e_op2, var2, reg2 = self.eval_operand(op2, code_list)
        if var1 and var2:   # Both operands are variables
            imm = ""
            rtype1 = self.local_ids[e_op1]["type"] if e_op1 in self.local_ids else self.global_ids[e_op1]["type"]
            rtype2 = self.local_ids[e_op2]["type"] if e_op2 in self.local_ids else self.global_ids[e_op2]["type"]
            if reg1 is None:
                reg1 = self.get_register(e_op1, rtype1, code_list)
                #self.load_variable(rtype1, rtype1, reg1, e_op1, code_list)
            if reg2 is None:
                reg2 = self.get_register(e_op2, rtype2, code_list)
                #self.load_variable(rtype2, rtype2, reg2, e_op2, code_list)
        elif (var1 is False) and (var2 is False):
            imm = "get_r1r2"
            reg1 = e_op1
            reg2 = e_op2
            rtype1 = self.map_type[type(e_op1)]
            rtype2 = self.map_type[type(e_op2)]
        else:
            if var1:
                imm = "get_r2"
                reg2 = e_op2
                rtype2 = self.map_type[type(e_op2)]
                rtype1 = self.local_ids[e_op1]["type"] if e_op1 in self.local_ids else self.global_ids[e_op1]["type"]
                if reg1 is None:
                    reg1 = self.get_register(e_op1, rtype1, code_list)
                    #self.load_variable(rtype1, rtype1, reg1, e_op1, code_list)
            else:
                imm = "get_r1"
                reg1 = e_op1
                rtype1 = self.map_type[type(e_op1)]
                rtype2 = self.local_ids[e_op2]["type"] if e_op2 in self.local_ids else self.global_ids[e_op2]["type"]
                if reg2 is None:
                    reg2 = self.get_register(e_op2, rtype2, code_list)
                    #self.load_variable(rtype2, rtype2, reg2, e_op2, code_list)
        if op == "int+":
            # addi lvalue, reg1, op2
            self.add_int(ltype, lvalue, rtype1, reg1, rtype2, reg2, code_list, imm=imm)
        elif op == "float+":
            self.float_arithmetic("add.s", ltype, lvalue, rtype1, reg1, rtype2, reg2, code_list, imm=imm)
        elif op == "int*":
            self.int_arithmetic("mul", ltype, lvalue, rtype1, reg1, rtype2, reg2, code_list, imm=imm)
        elif op == "float*":
            self.float_arithmetic("mul.s", ltype, lvalue, rtype1, reg1, rtype2, reg2, code_list, imm=imm)
        elif op == "int/":
            self.int_arithmetic("div", ltype, lvalue, rtype1, reg1, rtype2, reg2, code_list, imm=imm)
        elif op == "float/":
            self.float_arithmetic("div.s", ltype, lvalue, rtype1, reg1, rtype2, reg2, code_list, imm=imm)
        elif op == "int-":
            self.int_arithmetic("sub", ltype, lvalue, rtype1, reg1, rtype2, reg2, code_list, imm=imm)
        elif op == "float-":
            self.float_arithmetic("sub.s", ltype, lvalue, rtype1, reg1, rtype2, reg2, code_list, imm=imm)
        elif op in ["<", ">", "<=", ">=", "==", "!=" ]:
            if rtype1 in ["float", "double"] or rtype2 in ["float", "double"]:
                self.float_branch_instr(rtype1, reg1, op, rtype2, reg2, lvalue, code_list, imm=imm)
            else:
                self.int_branch_instr(rtype1, reg1, op, rtype2, reg2, lvalue, code_list, imm=imm)
        else:
            print("Something is Wrong", frameinfo.filename, frameinfo.lineno)
        pass

    def float_branch_instr(self, optype1, op1, relop, optype2, op2, label, code_list, imm=""):
        if relop == '':
            print("Something is Wrong", frameinfo.filename, frameinfo.lineno)
        reg1 = op1
        reg2 = op2
        if imm in ["get_r1", "get_r1r2"]: # rvalue1 not in register
            optype1 = "float"
            reg1 = self.get_register("NULL", "float", code_list)
            self.load_immediate("float", optype1, reg1, op1, code_list)
        if imm in ["get_r2", "get_r1r2"]: # rvalue2 not in register
            optype2 = "float"
            reg2 = self.get_register("NULL", "float", code_list)
            self.load_immediate("float", optype2, reg2, op2, code_list)

        if optype1 not in ["float", "double"]:
            reg1 = self.get_register("NULL", "float", code_list)
            self.move_variable("float", optype1, reg1, op1, code_list)

        if optype2 not in ["float", "double"]:
            reg2 = self.get_register("NULL", "float", code_list)
            self.move_variable("float", optype2, reg2, op2, code_list)

        opcode1 = self.relops[relop][1]
        opcode2 = self.relops[relop][2]
        code_list.append([opcode1, reg1 + ",", reg2])
        code_list.append([opcode2, label])
        pass

    def int_branch_instr(self, optype1, op1, relop, optype2, op2, label, code_list, imm=""):
        if relop == '':
            print("Something is Wrong", frameinfo.filename, frameinfo.lineno)
        reg1 = op1
        reg2 = op2
        opcode = self.relops[relop][0]
        if imm == "get_r1r2":
            reg1 = self.get_register("NULL", "int", code_list)
            self.load_immediate("int", optype1, reg1, op1, code_list)
        elif imm == "get_r1":
            # swap
            reg1, reg2 = reg2, reg1
            opcode = self.relops[self.relops[relop][3]][0]  # Anti-opcode

        code_list.append([opcode, str(reg1) + ",", str(reg2) + ",", label])
        pass

    def int_arithmetic(self, opcode, ltype, lvalue, rtype1, rvalue1, rtype2, rvalue2, code_list, imm=""):
        reg1 = rvalue1
        reg2 = rvalue2
        #print(imm, lvalue, reg1, reg2, type(rtype2))
        if imm in ["get_r1", "get_r1r2"]: # rvalue1 not in register
            reg1 = self.get_register("NULL", "int", code_list)
            self.load_immediate("int", rtype1, reg1, rvalue1, code_list)
        if imm in ["get_r2", "get_r1r2"]: # rvalue2 not in register
            reg2 = self.get_register("NULL", "int", code_list)
            self.load_immediate("int", rtype2, reg2, rvalue2, code_list)

        if ltype in ["float", "double"]:    # lvalue must be $f type register
            reg = self.get_register("NULL", "int", code_list)
            code_list.append([opcode, reg + ",", reg1 + ",", reg2])
            code_list.append(["mtc1", reg + ",", lvalue])
            code_list.append(["cvt.s.w", lvalue + ",", lvalue])
        else:                               # lvalue must be $s or $t type register
            code_list.append([opcode, lvalue + ",", reg1 + ",", reg2])
        pass

    def add_int(self, ltype, lvalue, rtype1, rvalue1, rtype2, rvalue2, code_list, imm=""):
        reg1 = rvalue1
        reg2 = rvalue2
        if imm == "get_r1r2":
            reg1 = self.get_register("NULL", "int", code_list)
            self.load_immediate("int", rtype1, reg1, rvalue1, code_list)
        elif imm == "get_r1":
            # swap
            reg1, reg2 = reg2, reg1

        opcode = "add" if imm == ""  else "addi"
        if ltype in ["float", "double"]:    # lvalue must be $f type register
            reg = self.get_register("NULL", "int", code_list)
            code_list.append([opcode, reg + ",", reg1 + ",", reg2])
            code_list.append(["mtc1", reg + ",", lvalue])
            code_list.append(["cvt.s.w", lvalue + ",", lvalue])
        else:                               # lvalue must be $s or $t type register
            code_list.append([opcode, lvalue + ",", str(reg1) + ",", str(reg2)])
        pass

    def float_arithmetic(self, opcode, ltype, lvalue, rtype1, rvalue1, rtype2, rvalue2, code_list, imm=""):
        reg1 = rvalue1
        reg2 = rvalue2

        if imm in ["get_r1", "get_r1r2"]: # rvalue1 not in register
            reg1 = self.get_register("NULL", "float", code_list)
            self.load_immediate("float", rtype1, reg1, rvalue1, code_list)
            rtype1 = "float"
        if imm in ["get_r2", "get_r1r2"]: # rvalue2 not in register
            reg2 = self.get_register("NULL", "float", code_list)
            self.load_immediate("float", rtype2, reg2, rvalue2, code_list)
            rtype2 = "float"

        if rtype1 not in ["float", "double"]:
            reg1 = self.get_register("NULL", "float", code_list)
            self.move_variable("float", rtype1, reg1, rvalue1, code_list)

        if rtype2 not in ["float", "double"]:
            reg2 = self.get_register("NULL", "float", code_list)
            self.move_variable("float", rtype2, reg2, rvalue2, code_list)

        if ltype in ["float", "double"]:    # lvalue must be $f type register
            code_list.append([opcode, lvalue + ",", reg1 + ",", reg2])
        else:                               # lvalue must be $s or $t type register
            reg = self.get_register("NULL", "float", code_list)
            code_list.append([opcode, reg + ",", reg1 + ",", reg2])
            code_list.append(["cvt.w.s", reg + ",", reg])
            code_list.append(["mfc1", lvalue + ",", reg])
        pass

    def eval_operand(self, op, code_list):
        reg = None
        try:
            op = eval(op)
            var = False
        except:
            op = op
            var = True
            ptr = op.rfind("*") + 1
            addr = op.rfind("&") + 1
            arr = op.rfind("$") + 1
            if ptr > 0:
                op = op[ptr:]
                reg = self.deref_variable(op, code_list, ptr)
            elif addr > 0:
                op = op[addr:]
                reg = self.load_address(op, code_list)
            elif arr > 0:
                op = op[arr:]
                op, offset = op.split("+")
                reg = self.deref_array(op, offset, code_list)
            else:
                reg = None
        return op, var, reg

    def deref_array(self, arr, offset, code_list):
        atype = self.local_ids[arr]["type"] if arr in self.local_ids else self.global_ids[arr]["type"]
        treg = self.load_address(arr, code_list)
        oreg = self.get_register(offset, "int", code_list)
        code_list.append(["addu", treg + ",", treg + ",", oreg])
        reg = str(treg)
        treg = "(" + treg + ")"
        if atype in ["float", "double"]:
            reg = self.get_register("NULL", atype, code_list)
        self.load_variable(atype, atype, reg, treg, code_list)
        return reg

    def move_variable(self, ltype, rtype, reg1, reg2, code_list):
        if ltype != rtype:
            # REVIEW: double type not handled
            if ltype in ["float", "double"]:                          # $f type regiser
                code_list.append(["mtc1", reg2 + ",", reg1])
                code_list.append(["cvt.s.w", reg1 + ",", reg1])
            elif rtype in ["float", "double"]:
                code_list.append(["cvt.w.s", reg2 + ",", reg2])
                code_list.append(["mfc1", reg1 + ",", reg2])
            else:
                code_list.append(["move", reg1 + ",", reg2])
        else:
            if ltype in ["float", "double"]:
                code_list.append(["mov.s", reg1 + ",", reg2])
            #elif ltype in ["double"]:
            #    code_list.append(["mov.d", reg1 + ",", reg2])
            else:
                code_list.append(["move", reg1 + ",", reg2])
        pass

    def load_address(self, op, code_list):
        reg = self.get_register("NULL", "int", code_list)
        code_list.append(["la", reg + ",", op])
        return reg

    def deref_variable(self, op, code_list, ptr):
        optype = self.local_ids[op]["type"] if op in self.local_ids else self.global_ids[op]["type"]
        reg = self.get_register(op, "int", code_list)
        for p in range(ptr-1):
            self.load_variable("pointer", "pointer", reg, "(" + reg + ")", code_list)
        reg2 = reg
        if optype in ["float", "double"]:
            reg2 = get_register(op, optype, code_list)
        self.load_variable(optype, optype, reg2, "(" + reg + ")", code_list)
        return reg2

    def load_variable(self, ltype, rtype, op1, op2, code_list):
        if (ltype != rtype) and not (ltype in ["pointer"]):
            reg = self.get_register(op2, rtype, code_list)
            self.load_variable(rtype, rtype, reg, op2, code_list)
            self.move_variable(ltype, rtype, op1, reg, code_list)
        else:
            if ltype in ["double"]:
                code_list.append(["l.d", op1 + ",", op2])
            elif ltype in ["float"]:                        # $f type regiser
                code_list.append(["l.s", op1 + ",", op2])
            elif ltype in ["char"]:
                code_list.append(["lb", op1 + ",", op2])
            else:
                code_list.append(["lw", op1 + ",", op2])
        pass

    def load_immediate(self, ltype, rtype, op1, op2, code_list):
        #print("--------------------", str(op2), ltype, rtype, op1, op2)
        if ltype in ["float", "double"]:    # $f type regiser
            if rtype in [int, "int"]:
                op2 = float(op2)
            elif rtype in [str, "char"]:
                op2 = float(ord(op2))
            if ltype == "double":
                code_list.append(["li.d", op1 + ",", str(op2)])
            else:
                code_list.append(["li.s", op1 + ",", str(op2)])
        else:                               # $s,$t type register
            #print("load_immediate", rtype, op2)
            if rtype in [str, "char"]:
                code_list.append(["li", op1 + ",", "'" + str(op2) + "'"])
            else:
                op2 = int(op2) if rtype is float else op2
                #print(["li", op1 + ",", str(op2)])
                code_list.append(["li", op1 + ",", str(op2)])
        pass

    def print_stdout(self, ptype, op, code_list):
        key = "string" if ptype == "char" else ptype
        code_list.append(["li", "$v0" + ",", self.syscall["print_" + key]])
        if ptype in ["int"]:
            """reg = self.check_in_register(op)
            if reg:
                code_list.append(["move", "$a0" + ",", reg])
            else:"""
            if op in self.local_ids:
                loc = self.local_ids[op]["location"]
            else:
                loc = self.global_ids[op]["location"]

            code_list.append(["lw", "$a0" + ",", loc])
        elif ptype in ["float"]:
            op = self.get_register(op, ptype, code_list)
            code_list.append(["mov.s", "$f12" + ",", op])
        elif ptype in ["double"]:
            op = self.get_register(op, ptype, code_list)
            code_list.append(["mov.d", "$f12" + ",", op])       # Not sure
        elif ptype in ["char"]:

            """reg = self.check_in_register(op)
            if reg:
                skip = list(self.general_regs[reg])
                skip.remove(op)
                self.spill_register(reg, code_list, skip)
            """
            if op in self.local_ids:
                loc = self.local_ids[op]["location"]
            else:
                loc = self.global_ids[op]["location"]
            code_list.append(["la", "$a0" + ",", loc])
        elif ptype in ["string"]:
            code_list.append(["la", "$a0" + ",", op])           # op should be memory address
        code_list.append(["syscall"])
        pass

    def gen_data_section(self):
        scope_q = ["main"]
        scopes = ["global"]
        while len(scope_q) != 0:
            _scope = scope_q.pop(0)
            scopes.append(_scope)
            for s in st.ScopeList:
                if s != "NULL":
                    if st.ScopeList[s].get("parent") == _scope:
                        scope_q.append(str(s))
        for scope in scopes:
        	#if scope != "NULL":
        	table = st.ScopeList[scope]["table"].symtab
        	for k in table.keys():

        		if (table[k]["id_type"] not in ["function", "class", "struct", "namespace"]) and (table[k].get("value",None) != None):

        			#print(table[k])
        			if table[k]["id_type"] == "array":
        				if st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "char":
        					self.data.append([table[k]["tac_name"] + ":", ".ascii", '"' + table[k]["value"] + '"'])

        				elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] in ["float","long long int"]:
        					if len(set(table[k].get("value",0) )) <= 1:
        						self.data.append([table[k]["tac_name"] + ":", ".float", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]"])
        					else:
        						self.data.append([table[k]["tac_name"] + ":", ".float", ', '.join(str(x) for x in table[k]["value"])])
        				elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "double":
        					if len(set(table[k].get("value",0) )) <= 1:
        						self.data.append([table[k]["tac_name"] + ":", ".double", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]"])
        					else:
        						self.data.append([table[k]["tac_name"] + ":", ".double", ', '.join(str(x) for x in table[k]["value"])])
        				elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "int":
        					if len(set(table[k].get("value",0) )) <= 1:
        						self.data.append([table[k]["tac_name"] + ":", ".word", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]"])
        					else:
        						self.data.append([table[k]["tac_name"] + ":", ".word", ', '.join(str(x) for x in table[k]["value"])])
        				continue

        			if table[k].get('star',0) >0:
        				self.data.append([table[k]["tac_name"] + ":", ".word", table[k]["value"]])
        			elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] in ["float","long long int"]:
        				self.data.append([table[k]["tac_name"] + ":", ".float", table[k]["value"]])
        			elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "char":
        				self.data.append([table[k]["tac_name"]+ ":", ".byte", "'" + table[k]["value"] + "'"])
        			elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "double":
        				self.data.append([table[k]["tac_name"] + ":", ".double", table[k]["value"]])
        			elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "int":
        				self.data.append([table[k]["tac_name"] + ":", ".word", table[k]["value"]])

        for scope in scopes:
            table = st.ScopeList[scope]["table"].symtab
            for k in table.keys():
            	if table[k]["id_type"] not in ["function", "class", "struct", "namespace"] and table[k].get("value",None) == None:
                    if table[k]["id_type"] == "array":
                    	self.bss.append([table[k]["tac_name"] + ":", ".space", table[k].get("size",0)])
                    elif table[k]["id_type"] == "temporary":
                    	self.bss.append([table[k]["tac_name"] + ":", ".word", 0])
                    else:
                    	if table[k].get('star',0) >0:
                    		self.bss.append([table[k]["tac_name"] + ":", ".word", 0])
                    	elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "char":
                    		self.bss.append([table[k]["tac_name"] + ":", ".ascii", '"A"'])
                    	elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] in ["float","long long int"]:
                    		self.bss.append([table[k]["tac_name"] + ":", ".float", 0.0])
                    	elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "double":
                    		self.bss.append([table[k]["tac_name"] + ":", ".double", 0.0])
                    	elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "int":
                    		self.bss.append([table[k]["tac_name"] + ":", ".word", 0])

        for lit in literal_decl:
            self.data.append([lit[0] + ":", ".asciiz", '"' + lit[1] + '"'])
        pass

    def print_sections(self):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
        with open('c1.asm', 'w') as fi:
            print(".text", file=fi)
            print(".globl   main", file=fi)
            print("main:\n", file=fi)
            for line in self.main:
                print(" ".join(str(e) for e in line), file=fi)
            print("\n\n",file=fi)
            for line in self.functions:
                print(" ".join(str(e) for e in line),file=fi)

            print("\n\n.data\n", file=fi)
            for line in self.data:
                print(" ".join(str(e) for e in line), file=fi)
            #print("\n\n")
            #print(".bss\n")
            for line in self.bss:
                print(" ".join(str(e) for e in line), file=fi)
            #print(".functions\n")

        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")

        pass
