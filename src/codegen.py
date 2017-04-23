import symtable as st
import tac

class CodeGen:
	def __init__(self,tac_file):
		self.reg = {
			'%eax': 0,
			'%ebx': 0,
			'%ecx': 0,
			'%edx': 0,
			'%esi': 0,
			'%edi': 0
		}
		self.bitops = {
			'&' : "andl",
			'|' : "orl",
			'^' : "xorl"
		}
		self.shiftop = {
			'>>': "shrl",
			'<<': "shll"
		}

def gen_data():
	print(".data ")
	for scope in st.ScopeList.keys():
		if scope != "NULL":
			table = st.ScopeList[scope]["table"].symtab
			for k in table.keys():
				if table[k]["id_type"] not in ["function", "class", "struct"] and table[k].get("value",None):

					if table[k]["id_type"] == "array":
						if st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "char":
							print(table[k]["tac_name"] + ":", ".ascii", '"' + table[k]["value"] + '"')

						elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] in ["float","long long int"]:
							if len(set(table[k].get("value",0) )) <= 1:
								print(table[k]["tac_name"] + ":", ".float", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]")
							else:
								print(table[k]["tac_name"] + ":", ".float", ', '.join(str(x) for x in table[k]["value"]) )
						elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "double":
							if len(set(table[k].get("value",0) )) <= 1:
								print(table[k]["tac_name"] + ":", ".double", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]")
							else:
								print(table[k]["tac_name"] + ":", ".double", ', '.join(str(x) for x in table[k]["value"]) )
						elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "int":
							if len(set(table[k].get("value",0) )) <= 1:	
								print(table[k]["tac_name"] + ":", ".word", str(table[k]["value"][0]) + '[:' + str(len(table[k]["value"])) + "]")
							else:
								print(table[k]["tac_name"] + ":", ".word", ', '.join(str(x) for x in table[k]["value"]) )

					elif scope == "global":
						if table[k].get('star',0) >0:
							print(table[k]["tac_name"] + ":", ".word", table[k]["value"]) 

						elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] in ["float","long long int"]:
							print(table[k]["tac_name"] + ":", ".float", table[k]["value"])
	
						elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "char":
							print(table[k]["tac_name"]+ ":", ".byte", "'" + table[k]["value"] + "'")
						
						elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "double":
							print(table[k]["tac_name"] + ":", ".double", table[k]["value"]) 

						elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "int":
							print(table[k]["tac_name"] + ":", ".word", table[k]["value"]) 
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print(".bss ")
	table = st.ScopeList["global"]["table"].symtab
	for k in table.keys():
		if table[k]["id_type"] not in ["function", "class", "struct"] and table[k].get("value",None) == None:
			if table[k]["id_type"] == "array":
				print(table[k]["name"] + ":\t.space\t", table[k].get("size",0))
			else:
				if table[k].get('star',0) >0:
							print(table[k]["tac_name"] + ":", ".word") 
				elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "char":
					print(table[k]["tac_name"] + ":", ".ascii" )

				elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] in ["float","long long int"]:
						print(table[k]["tac_name"] + ":", ".float") 

				elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "double":
					print(table[k]["tac_name"] + ":", ".double") 

				elif st.simple_type_specifier[" ".join(table[k]["type"])]["equiv_type"] == "int":
					print(table[k]["tac_name"] + ":", ".word") 

	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")


