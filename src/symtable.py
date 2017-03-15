global ScopeList, currentScope
ScopeList = { "NULL" : None, "global" : {"name":"global", "parent" : "NULL",}, }
currentScope = "global"

class SymTab:
    def __init__(self):
        global ScopeList
        self.symtab = {}
       # self.numVar = 0

       # I think, there is no need of this self.scope
        self.scope =  {
                "name"       : ScopeList[currentScope]["name"],
                "parent"     : ScopeList[currentScope]["parent"],
                "table"      : self,                          # No need, I guess
            }
        ScopeList[currentScope]["table"] = self

    def lookup(self, lexeme):
        if lexeme in self.symtab:
            return self.symtab[lexeme]
        return None

    def lookupComplete(self, lexeme):
        scope = ScopeList[currentScope]
        while scope is not None:
            entry = scope["table"].lookup(lexeme)
            if entry != None:
                return entry
            scope = ScopeList[scope["parent"]]
        return None

    def insertID(self, name, id_type):
        currtable = ScopeList[currentScope]["table"]
        #print("[Symbol Table]", currtable.symtab)
        if currtable.lookup(name):
            print("[Symbol Table] Entry already exists")
        else:
            currtable.symtab[name] = {
                "name"      : name,
                "type"      : id_type,
            }
            print("[Symbol Table] Inserting new identifier: ", name, " type: ", id_type)
            #ScopeList[-1]["table"].numVar += 1

    def addVarAttr(self,var,attribute,value):
        self.symtab[str(var)].update({attribute:value})

    def addScopeAttr(self,attribute,value):
        self.scope.update({attribute:value})

    def addScope(self,name):
        global ScopeList, currentScope
        new_scope = {
                "name"       : name,
                "parent"     : ScopeList[currentScope]["name"],
                "table"      : None
                }
        ScopeList[name] =  new_scope
        currentScope = name
        SymTab()
        print("[Symbol Table](addScope)", name)

    def endScope(self):
        """
        Changes current scope to parent scope  when '}' is received
        """
        global currentScope
        currentScope = ScopeList[currentScope]["parent"]
        print("[Symbol Table](endScope)", currentScope)
        if ScopeList[currentScope] is None:
            print("[Symbol Table] Error: This line should not be printed")

    #def deleteScope(self):
    #    """
    #    Deletes current scope (present at the last of list)
    #    """
    #    print("Removing Scope %s", ScopeList[-1]["name"])
    #    del ScopeList[-1]


if __name__ == '__main__':
    a = SymTab()
    a.insertID("v", "CHAR")
    a.addScope("main")
    print(ScopeList)
    a.insertID("x","INT")
    print(ScopeList[currentScope]["table"].symtab)
    ScopeList[currentScope]["table"].symtab["x"].update({"size":"4"})
    a.insertID("x", "BOOL")
    print(ScopeList[currentScope]["table"].symtab)
    print(a.symtab)
    ScopeList[currentScope]["table"].addVarAttr("x","value",10)
    print(ScopeList[currentScope]["table"].symtab)
    ScopeList[currentScope]["table"].addScopeAttr("type","function")
    print(ScopeList[currentScope]["table"].scope)
    a.endScope()
    a.insertID("w", "FLOAT")
    a.endScope()
    if not a.lookupComplete("y"):
        print("Not Exist")
        pass




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
#       self.table = symtab
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
