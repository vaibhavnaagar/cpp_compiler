import symtable as st
import tac

class CodeGen:
    def __init__ (self, TAC):
        self.TAC = TAC
        self.label = 'L'
        self.main = []
        self.functions = []
        self.data = []
        self.bss = []
        self.id_dict = dict()
        self.reg_dict()
        self.make_id_dict()

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

    def make_id_dict(self):
        for scope in st.ScopeList.keys():
            if scope != "NULL":
                if st.ScopeList[scope]["table"].symtab:
                    for k in st.ScopeList[scope]["table"].symtab.keys():
                        self.id_dict.update({ k : None })
        pass

    def get_reg(self):
        pass

    def parse_tac(self):
        for quad in self.TAC.code:
            print(quad)
            if quad[0] in ["if","goto", "begin", "end" , "param", "call", "ret"]:
                pass
            else:   # Assignment
                self.handle_assignment(quad)
            pass
        pass

    def handle_assignment(self, quad):
        # ['var', '7', '', '']
        if quad[2] == '':   # simple assignment
            try:
                rvalue = eval(quad[1])
                var = False
            except:
                rvalue = quad[1]
                var = True
            if type(rvalue) is int:
                pass
            elif type(rvalue) is float:
                pass
            elif type(rvalue) is str and var is False:
                pass
            else:   # Variable at RHS
                pass
        else:
            pass
        pass

    def gen_data_section(self):
    	#print(".data ")
    	for scope in ["global", "main"]:
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
    	for scope in ["global", "main"]:
            table = st.ScopeList[scope]["table"].symtab
            for k in table.keys():
            	if table[k]["id_type"] not in ["function", "class", "struct", "namespace"] and table[k].get("value",None) == None:
            		if table[k]["id_type"] == "array":
            			#print(table[k]["name"] + ":\t.space\t", table[k].get("size",0))
            			self.bss.append([table[k]["name"] + ":\t.space\t", table[k].get("size",0)])
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
        pass
