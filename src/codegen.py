import symtable as st
import tac
from inspect import currentframe, getframeinfo

frameinfo = getframeinfo(currentframe())

class CodeGen:
    def __init__ (self, TAC):
        self.TAC = TAC
        self.label = 'L_'
        self.main = []              # Main section
        self.functions = []         # Fucntion definitions
        self.data = []              # Data section
        self.bss = []               # BSS section
        self.global_ids = dict()
        self.local_ids = dict()
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
        for i in range(10):  self.temp_regs.update({ '$t' + str(i) : None })

        # (saved values) - Callee saved (Preserved across procedure calls)
        self.saved_regs = dict()
        for i in range(8):  self.temp_regs.update({ '$s' + str(i) : None })

        self.pointer_regs = { "$gp" : None, "$sp" : None, "$fp" : None, "ra" : None }
        pass

    def get_global_ids(self, scope_name):
        table = st.ScopeList[scope_name]["table"].symtab
        for k in table:
            if table[k]["id_type"] not in ["function", "namespace", "class", "struct", "union",]:
                self.global_ids.update({ table[k]["tac_name"] : dict(register=None, location=None, type=st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"]) })

    def get_local_ids(self, scope_name):
        self.local_ids.clear()
        scope_q = [str(scope_name)]
        while len(scope_q) != 0:
            _scope = scope_q.pop(0)
            table = st.ScopeList[_scope]["table"].symtab
            for k in table:
                if table[k]["id_type"] not in ["function", "namespace", "class", "struct", "union",]:
                    self.local_ids.update({ table[k]["tac_name"] : dict(register=None, location=table[k]["offset"], type=st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"]) })
            for s in st.ScopeList:
                if s != "NULL":
                    if st.ScopeList[s].get("parent") == _scope:
                        scope_q.append(str(s))
        pass

    def get_register(self, name, ltype):
        # TODO: Do it !!
        return "$"

    def check_in_register(self, name):
        # TODO: Do it !!
        return None

    def parse_tac(self):
        inside_func = False
        is_main = False
        for quad in self.TAC.code:
            print(quad)
            if quad[0] in ["function"]:
                inside_func = True
                if quad[1] == "main":
                    is_main = True
                else:
                    is_main = False
                    # TODO:  Code for stack space ..............................................
                    self.functions.append([quad[1] + ":"])
                self.get_local_ids(quad[1])
            else:
                if not inside_func:     # TAC of Global scope
                    continue
                if quad[0] in ["end"]:
                    inside_func = False
                    if is_main:
                        is_main = False
                        # TODO:  exit syscall code ...............................................
                        pass
                    else:
                        self.functions.append(["jr", "\t$ra"])
                elif quad[0] in ["if","goto", "function", "param", "call", "ret"]:
                    pass
                else:   # Assignment
                    self.handle_assignment(quad, is_main)
                    pass
        pass

    def handle_assignment(self, quad, is_main):
        if is_main:
            code_list = self.main       # reference main code list
        else:
            code_list = self.functions  # reference functions code list

        # TODO: ADD code for pointers in the lvalue
        ltype = self.local_ids[quad[0]]["type"] if quad[0] in self.local_ids else self.global_ids[quad[0]]["type"]
        lvalue = self.get_register(quad[0], ltype)

        if quad[2] == '':   # simple assignment if quad is like ['var', '7', '', '']
            try:
                rvalue = eval(quad[1])
                var = False
            except:
                rvalue = quad[1]
                var = True
            if var:
                ptr = rvalue.rfind("*") + 1
                addr = rvalue.rfind("&") + 1
                reg = None
                if ptr > 0:
                    reg = self.deref_variable(rvalue[ptr:], code_list, ptr)
                elif addr > 0:
                    reg = self.load_address(rvalue[addr:], code_list)
                else:
                    reg = self.check_in_register(rvalue)
                if reg:
                    code_list.append(["move", lvalue + ",", reg])
                else:
                    self.load_variable(ltype, lvalue, rvalue, code_list)
            else:
                self.load_immediate(type(rvalue), lvalue, quad[1], code_list, ltype=ltype)
        else:
            pass
        pass

    def load_address(self, op, code_list):
        reg = self.get_register("NULL", None)
        code_list.append(["la", reg + ",", op])
        return reg

    def deref_variable(self, op, code_list, ptr):
        optype = self.local_ids[op]["type"] if op in self.local_ids else self.global_ids[op]["type"]
        reg = self.get_register(op, optype)
        #self.load_variable("pointer", reg, op, code_list)
        for p in range(ptr-1):
            self.load_variable("pointer", reg, "(" + reg + ")", code_list)
        self.load_variable(optype, reg, "(" + reg + ")", code_list)
        return reg

    def load_variable(self, ltype, op1, op2, code_list):
        # REVIEW: Assuming rtype has same type as of ltype

        if ltype in ["double"]:
            code_list.append(["l.d", op1 + ",", op2])
        elif ltype in ["float"]:
            code_list.append(["l.s", op1 + ",", op2])
        elif ltype in ["char"]:
            code_list.append(["lb", op1 + ",", rvalue])
        else:
            code_list.append(["lw", op1 + ",", op2])
        pass


    def load_immediate(self, rtype, op1, op2, code_list, ltype=None):
        if rtype in [int, str]:
            code_list.append(["li", op1 + ",", op2])
        elif rtype is float:
            if ltype is "double":
                code_list.append(["li.d", op1 + ",", op2])
            else:
                code_list.append(["li.s", op1 + ",", op2])
        else:
            print("Something is Wrong", frameinfo.filename, frameinfo.lineno)
        pass


    def gen_data_section(self):
        #print(".data ")
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
        		if table[k]["id_type"] not in ["function", "class", "struct", "namespace"] and table[k].get("value",None):

        			if table[k]["id_type"] == "array":
        				if st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "char":
        					#print(table[k]["tac_name"] + ":", ".ascii", '"' + table[k]["value"] + '"')
        					self.data.append([table[k]["tac_name"] + ":", ".ascii", '"' + table[k]["value"] + '"'])

        				elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] in ["float","long long int"]:
        					if len(set(table[k].get("value",0) )) <= 1:
        						#print(table[k]["tac_name"] + ":", ".float", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]")
        						self.data.append([table[k]["tac_name"] + ":", ".float", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]"])
        					else:
        						#print(table[k]["tac_name"] + ":", ".float", ', '.join(str(x) for x in table[k]["value"]) )
        						self.data.append([table[k]["tac_name"] + ":", ".float", ', '.join(str(x) for x in table[k]["value"])])
        				elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "double":
        					if len(set(table[k].get("value",0) )) <= 1:
        						#print(table[k]["tac_name"] + ":", ".double", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]")
        						self.data.append([table[k]["tac_name"] + ":", ".double", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]"])
        					else:
        						#print(table[k]["tac_name"] + ":", ".double", ', '.join(str(x) for x in table[k]["value"]) )
        						self.data.append([table[k]["tac_name"] + ":", ".double", ', '.join(str(x) for x in table[k]["value"])])
        				elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "int":
        					if len(set(table[k].get("value",0) )) <= 1:
        						#print(table[k]["tac_name"] + ":", ".word", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]")
        						self.data.append([table[k]["tac_name"] + ":", ".word", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]"])
        					else:
        						#print(table[k]["tac_name"] + ":", ".word", ', '.join(str(x) for x in table[k]["value"]) )
        						self.data.append([table[k]["tac_name"] + ":", ".word", ', '.join(str(x) for x in table[k]["value"])])
        				continue

        			if table[k].get('star',0) >0:
        				#print(table[k]["tac_name"] + ":", ".word", table[k]["value"])
        				self.data.append([table[k]["tac_name"] + ":", ".word", table[k]["value"]])
        			elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] in ["float","long long int"]:
        				#print(table[k]["tac_name"] + ":", ".float", table[k]["value"])
        				self.data.append([table[k]["tac_name"] + ":", ".float", table[k]["value"]])
        			elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "char":
        				#print(table[k]["tac_name"]+ ":", ".byte", "'" + table[k]["value"] + "'")
        				self.data.append([table[k]["tac_name"]+ ":", ".byte", "'" + table[k]["value"] + "'"])
        			elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "double":
        				#print(table[k]["tac_name"] + ":", ".double", table[k]["value"])
        				self.data.append([table[k]["tac_name"] + ":", ".double", table[k]["value"]])
        			elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "int":
        				#print(table[k]["tac_name"] + ":", ".word", table[k]["value"])
        				self.data.append([table[k]["tac_name"] + ":", ".word", table[k]["value"]])
        #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        #print(".bss ")
        for scope in scopes:
            table = st.ScopeList[scope]["table"].symtab
            for k in table.keys():
            	if table[k]["id_type"] not in ["function", "class", "struct", "namespace"] and table[k].get("value",None) == None:
                    if table[k]["id_type"] == "array":
                    	#print(table[k]["name"] + ":\t.space\t", table[k].get("size",0))
                    	self.bss.append([table[k]["tac_name"] + ":", ".space", table[k].get("size",0)])
                    elif table[k]["id_type"] == "temporary":
                    	self.bss.append([table[k]["tac_name"] + ":", ".word"])
                    else:
                    	if table[k].get('star',0) >0:
                    		#print(table[k]["tac_name"] + ":", ".word")
                    		self.bss.append([table[k]["tac_name"] + ":", ".word"])
                    	elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "char":
                    		#print(table[k]["tac_name"] + ":", ".ascii" )
                    		self.bss.append([table[k]["tac_name"] + ":", ".ascii"])
                    	elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] in ["float","long long int"]:
                    		#print(table[k]["tac_name"] + ":", ".float")
                    		self.bss.append([table[k]["tac_name"] + ":", ".float"])
                    	elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "double":
                    		#print(table[k]["tac_name"] + ":", ".double")
                    		self.bss.append([table[k]["tac_name"] + ":", ".double"])
                    	elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "int":
                    		#print(table[k]["tac_name"] + ":", ".word")
                    		self.bss.append([table[k]["tac_name"] + ":", ".word"])

        #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
        pass

    def print_sections(self):
        print(".data")
        for line in self.data:
            print(" ".join(str(e) for e in line))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
        print(".bss")
        for line in self.bss:
            print(" ".join(str(e) for e in line))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
        print(".main")
        for line in self.main:
            print(" ".join(str(e) for e in line))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
        print(".functions")
        for line in self.functions:
            print(" ".join(str(e) for e in line))
        pass
