import symtable as st
class TAC:
	def __init__(self,scopename,start):
		self.code = []
		self.startquad = start
		self.nextquad = self.startquad
		self.temp_count = 0
		self.scope = scopename

	def emit(self,elist):
		self.code.append(elist)
		self.nextquad += 1

	def getnext(self):
		return self.nextquad

	def backpatch(self,list,targetlabel):
		if list:
			for l in list:
				self.code[l-self.startquad][-1] = str(targetlabel)

	def mergelist(l1,l2):
		return list(set(l1 + l2))

	def getnewtemp(self):
		self.temp_count +=1
		return "0_t" + str(self.temp_count)

	def print_code(self):
		for i,c in enumerate(self.code):
			if c[0] in ["if","goto", "function", "end" , "param", "call", "ret"]:
				print(str(i) + ":  " + " ".join(c))
			else:
				print(str(i) , ":  " + str(c[0]) + " " + " := " + " ".join(c[1:]) )

	def expression_emit(self,d,e1,op,e2,etype=''):
		if op in ['+','-','*','/']:
			self.emit([d,e1, str(etype[0]) + op,e2])
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
			self.expression_emit(d,d,op[:-1],e2,etype)
			return

		if op in [ "+++" , "---", "~"]:
			self.emit([d,e1,op,e2])
			return
