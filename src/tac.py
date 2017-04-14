import symtable as st
class TAC:
	def __init__(self,scopename):
		self.code = []
		self.nextquad = 1
		self.temp_count = 0
		self.scope = scopename

	def emit(self,d,s1,op,s2):
		self.code.append([d,s1,op,s2])
		self.nextquad += 1

	def getnext():
		return nextquad

	def backpatch(self,list,targetlabel):
		for l in list:
			self.code[l][-1] = str(targetlabel)

	def mergelist(l1,l2):
		return list(set(l1 + l2))
	def getnewtemp(self):
		self.temp_count +=1
		return "t" + str(self.temp_count)

	def print_code(self):
		for i,c in enumerate(self.code):
			print(str(i) + ":  " + str(c[0]) + " " + " := " + " " + str(c[1]) + " " + str(c[2]) + " " + str(c[3]) )

	def expression_emit(self,d,e1,op,e2,etype=''):
		if op in ['+','-','*','/']:
			self.emit(d,e1, str(etype[0]) + op,e2)
			return
		
		if op in ["^", "|" , "&", "&&","||","%"]:
			self.emit(d,e1,op,e2)
			return

		if op in ['++', '--']:
			self.emit(d,e1,op,e2)
			return
		
		if op in ["<", '>', '<=', '>=', '==', '!=']:
			self.emit(d,e1,op,e2)
			return

		
		if op in ['=']:
			self.emit(d,e2,'',e1)
			d = e2
			return

		
		if op in ["%=","<<=",">>=","&=", "+=", "-=", "/=", "*=", "^=", "|=" , "&=",]:
			self.expression_emit(d,d,op[:-1],e2,etype)
			return

			



