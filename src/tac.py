import symtable as st
labels = []
class TAC:
	def __init__(self,scopename,start):
		self.code = []
		self.startquad = start
		self.nextquad = self.startquad
		self.temp_count = 0
		self.scope = scopename
		self.labels = []

	def emit(self,elist):
		self.code.append(elist)
		self.nextquad += 1

	def getnext(self):
		return self.nextquad

	def backpatch(self,list,targetlabel):
		global labels
		labels.append(str(targetlabel))
		if list:
			for l in list:
				self.code[l-self.startquad][-1] = str(targetlabel)

	def mergelist(l1,l2):
		return list(set(l1 + l2))

	def getnewtemp(self):
		self.temp_count +=1
		return "_t" + str(self.temp_count)

	def print_code(self):
		for i,c in enumerate(self.code):
			#print(c)
			if c[0] in ["if","goto", "function", "end" , "param", "call", "ret", "cout"]:
				print(str(i) + ":  " + " ".join(c))
			else:
				print(str(i) , ":  " + str(c[0]) + " " + " := " + " ".join(c[1:]) )

	def expression_emit(self,d,e1,op,e2,etype=''):
		if op in ['+','-','*','/']:
			typ = str(etype[0]) if len(etype) >0 else "int"
			self.emit([d,e1,  typ + op,e2])
			return

		if op in ["^", "|" , "&", "%"]:
			self.emit([d,e1,op,e2])
			return

		if op in ['++', '--']:
			self.emit([d,e1,op,e2])
			return

		if op in ["<", '>', '<=', '>=', '==', '!=']:
			#self.emit([d,e1,op,e2])
			self.emit(['if',e1,op,e2,'goto',''])
			self.emit(['goto',""])
			return

		if op in ["&&","||", "!",]:
			return

		if op in ['=']:
			self.emit([d,e2,'',e1])
			d = e2
			return


		if op in ["%=","<<=",">>=","&=", "+=", "-=", "/=", "*=", "^=", "|=" , "&=",]:
			_scope = st.currentScope
			if len(st.function_list) > 0:
				_scope = st.function_list[-1]["name"]
			elif len(st.namespace_list) > 0:
				_scope = st.namespace_list[-1]["name"]
			t = self.getnewtemp() + "_" + str(_scope)
			st.ScopeList["global"]["table"].insertTemp(t, "temporary", _scope, ['int'])
			self.expression_emit(t,d,op[:-1],e2,etype)
			self.expression_emit(d,t,'','',etype)
			return

		if op in [ "+++" , "---", "~"]:
			self.emit([d,e1,op,e2])
			return
