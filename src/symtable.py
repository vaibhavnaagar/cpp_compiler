global ScopeList, currentScope
ScopeList = { "NULL" : None, "global" : {"name":"global", "parent" : "NULL",}, }
currentScope = "global"
scope_ctr = 1
integral_types = ["INT", "LONG", "literal_int", "SHORT", "UNSIGNED", "SIGNED"]

class SymTab:
    def __init__(self):
        global ScopeList
        self.symtab = dict()
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
            return self.symtab[str(lexeme)]
        return None

    def lookupComplete(self, lexeme):
        scope = ScopeList[currentScope]
        while scope is not None:
            entry = scope["table"].lookup(lexeme)
            if entry != None:
                return entry
            scope = ScopeList[scope["parent"]]
        return None

    def insertID(self, name, id_type, types=None, specifiers=[], num=1, value=None):
        currtable = ScopeList[currentScope]["table"]
        #print("[Symbol Table]", currtable.symtab)
        #check_datatype(data_type)

        if currtable.lookup(str(name)):         # No need to check again
            print("[Symbol Table] Entry already exists")
        else:
            currtable.symtab[str(name)] = {
                "name"      : str(name),
                "id_type"   : str(id_type),
                "type"      : list([] if types is None else types),        # List of data_types
                "specifier" : list([] if specifiers is None else specifiers),    # List of type specifiers
                "num"       : int(num),            # Number of such id
                "value"     : value,           # Mostly required for const type variable
        #        "size"      : size
            }
            warning = ''
            if types is None:
                warning = "(warning: Type is None)"
            print("[Symbol Table] ", warning, " Inserting new identifier: ", name, " type: ", types, "specifier: ", specifiers)
            #ScopeList[-1]["table"].numVar += 1

    def addIDAttr(self, name, attribute, value):
        currtable = ScopeList[currentScope]["table"]
        if attribute in currtable.symtab[str(name)].keys():
            if currtable.symtab[str(name)][str(attribute)] is not None:
                currtable.symtab[str(name)][str(attribute)] += list(value)
            else:
                currtable.symtab[str(name)][str(attribute)] = list(value)
        else:
            currtable.symtab[str(name)].update({attribute : value})
        print("[Symbol Table] Adding attribute of identifier: ", name, " attribute: ", attribute, "value: ", value)


    def addScopeAttr(self,attribute,value):
        self.scope.update({attribute:value})

    def addScope(self,name):
        global ScopeList, currentScope
        new_scope = {
                "name"       : str(name),
                "parent"     : ScopeList[currentScope]["name"],
                "table"      : None
                }
        ScopeList[str(name)] =  new_scope
        currentScope = str(name)
        SymTab()
        print("[Symbol Table](addScope) Adding New Scope: ", name)

    def endScope(self):
        """
        Changes current scope to parent scope  when '}' is received
        """
        global currentScope
        print("[Symbol Table](endScope) End Scope of: ", currentScope, end='')
        currentScope = ScopeList[currentScope]["parent"]
        print(" Current Scope: ", currentScope)
        if ScopeList[currentScope] is None:
            print("[Symbol Table] Error: This line should not be printed")

    #def deleteScope(self):
    #    """
    #    Deletes current scope (present at the last of list)
    #    """
    #    print("Removing Scope %s", ScopeList[-1]["name"])
    #    del ScopeList[-1]


# Helper functions

def check_datatype(types):
    """
    types: List of data types
    """
    if True:
        pass


def print_error(lineno, id1, errno, *args):
    if errno == 1:
        print("Line No.:", lineno, ": Error: ", id1.get("name"), "was not declared in this scope")
    elif errno == 2:
        print("Line No.:", lineno, ": Error: declaration does not declare anything")
    elif errno == 3:
        print("Line No.:", lineno, ": Error: expected unqualified-id before \'", args[0], "\'")
    elif errno == 4:
        if id1["type"] == args[0]:
            print("Line No.:", lineno, ": Error: ", "redeclaration of ", id1["name"])
        else:
            print("Line No.:", lineno, ": Error: ", "conflicting declaration ", id1["name"], ", previously declared as", id1["type"])
    elif errno == 5:
        print("Line No.:", lineno, ": Error: uninitialized const \'", id1["name"], "\'")
    elif errno == 6:
        print("Line No.:", lineno, ": Error: ", "conflicting declaration ", id1["name"], ", previously declared as", id1["specifier"])
    elif errno == 7:
        print("Line No.:", lineno, ": Error: ", id1["name"], "is not of array type")
    elif errno == 8:
        print("Line No.:", lineno, ": Error: index type: ", args[0] " for array \'", id1["name"], "\' is not of integral type")
    elif errno == 9:
        print("Line No.:", lineno, ": Error: index type is not const expression for array \'", id1["name"], "\'")
    pass



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
