global ScopeList
ScopeList = [{"name":"Root", "parent" : "NULL",}]
 
class SymTab:
    def __init__(self):
        global ScopeList
        self.symtab = {}
       # self.numVar = 0
        self.scope =  {
                "name"       : ScopeList[-1]["name"],
                "parent"     : ScopeList[-1]["parent"],
                "tab"      : self,
            }
        ScopeList[-1]["tab"] = self
        
    def lookup(self,lexeme ):
        if lexeme in self.symtab:
            return self.symtab[lexeme]
        return None

    def lookupComplete(self,lexeme):
        global ScopeList
        for scope in reversed(ScopeList) :
            a = scope["tab"].lookup(lexeme) 
            if a != None:
                return a
        return None

    def insertVar(self,name,type):
        currtable = ScopeList[-1]["tab"]
        print(currtable)
        if currtable.lookup(name):
            print("Entry already exists")
        else:
            currtable.symtab[name] = {
                "name"      : name,
                "type"      : type,
            }
            #ScopeList[-1]["tab"].numVar += 1

    def addVarAttr(self,var,attribute,value):
        self.symtab[str(var)].update({attribute:value})

    def addScopeAttr(self,attribute,value):
        self.scope.update({attribute:value})



    def addScope(self,name):
        global ScopeList
        scope = {
                "name"       : name,
                "parent"     : ScopeList[-1]["name"],
                }
        ScopeList.append(scope)
        SymTab() 

'''
a = SymTab()
a.addScope("main")
print(ScopeList)
a.insertVar("x","int")
print(ScopeList[-1]["tab"].symtab)
ScopeList[-1]["tab"].symtab["x"].update({"size":"4"})
print(ScopeList[-1]["tab"].symtab)
print(a.symtab)
ScopeList[-1]["tab"].addVarAttr("x","value",10)
print(ScopeList[-1]["tab"].symtab)
ScopeList[-1]["tab"].addScopeAttr("type","function")
print(ScopeList[-1]["tab"].scope)
'''


    

'''
 a = SymTabEntry("x",5,"int","local")
    b = SymTabEntry("y",6,"int","local")
    b.entry.update(a.entry)
    print(b.entry)

#    def getLexeme(self):
#        return self.lexeme
#       self.name = name
#       self.parent = parent
#       self.attribute = attribute
#       self.tab = symtab
#  def getParent(self):
#      return self.parent
#
#  def getName(self):
#       return self.name
#   def getAttr(self):
#       return self.attribute
class SymTabEntry:
    def __init__(self, name, value, type, attribute):
        self.entry = {
                "name"      : name
                "value"     : value,
                "type"      : type,
                "attribute" : attribute,
            }

class Scope:
    def __init__(self, name, parent, attribute,symtab):
        self. =
     
     
     

         '''