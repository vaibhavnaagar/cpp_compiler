import pprint, copy
global ScopeList, currentScope
ScopeList = { "NULL" : None, "global" : {"name":"global", "parent" : "NULL",}, }
currentScope = "global"
scope_ctr = 1

### Funcions ###
function_list = []
is_func_decl = False
parameter_specifiers = ["register", "auto", "const", "volatile"]
parenthesis_ctr = 0

### Data Types ###

integral_types = ["int", "long", "literal_int", "short", "unsigned", "signed"]
number_literals = ["literal_int", "literal_float"]
number_types = ["int", "long", "short", "unsigned", "signed", "float", "double"]

char_types = ["char", "unsigned char", "char16_t","char32_t", "wchar_t" ]
eq_integral_types = ["short int","int","unsigned int","long int","unsigned long int","long long int","unsigned long long", "float", "double"]
bool_type = ["bool"]

simple_type_specifier = {
"literal_bool":{"size" : 1 , "equiv_type" : "bool"},
"bool": {"size" : 1 , "equiv_type" : "bool"},

"literal_char": {"size" : 1 , "equiv_type" : "char"  },
"char": {"size" : 1 , "equiv_type" : "char"  },
"signed char": {"size" : 1 , "equiv_type" : "char" },
"unsigned char": {"size" : 1 , "equiv_type" : "unsigned char"  },
"wchar_t": {"size" : 4 , "equiv_type" : "wchar_t"  },
"char16_t": {"size" : 2 , "equiv_type" : "char16_t"  },
"char32_t": {"size" : 4 , "equiv_type" : "char32_t"  },


"short": {"size" : 2 , "equiv_type" : "short int"   },
"short int" : {"size" : 2 , "equiv_type" : "short int"  },
"signed short" : {"size" : 2 , "equiv_type" : "short int"  },
"signed short int" : {"size" : 2 , "equiv_type" : "short int"  },

"unsigned short" : {"size" : 2 , "equiv_type" : "unsigned short int"  },
"unsigned short int" : {"size" : 2 , "equiv_type" : "unsigned short int"  },

"literal_int" : {"size" : 4 , "equiv_type" : "int"  },
"int" : {"size" : 4 , "equiv_type" : "int"  },
"signed" : {"size" : 4 , "equiv_type" : "int"  },
"signed int" : {"size" : 4 , "equiv_type" : "int"  },

"unsigned" : {"size" : 4 , "equiv_type" : "unsigned int"  },
"unsigned int" : {"size" : 4 , "equiv_type" : "unsigned int"  },

"long" : {"size" : 4 , "equiv_type" : "long int"  },
"long int" : {"size" : 4 , "equiv_type" : "long int"  },
"signed long" : {"size" : 4 , "equiv_type" : "long int"  },
"signed long int" : {"size" : 4 , "equiv_type" : "long int"  },

"unsigned long" : {"size" : 4 , "equiv_type" : "unsigned long int"  },
"unsigned long int" : {"size" : 4 , "equiv_type" : "unsigned long int"  },

"long long" : {"size" : 8 , "equiv_type" : "long long int"  },
"long long int" :  {"size" : 8 , "equiv_type" : "long long int"  },
"long long int" : {"size" : 8 , "equiv_type" : "long long int"  },
"signed long long" : {"size" : 8 , "equiv_type" : "long long int"  },
"signed long long int" : {"size" : 8 , "equiv_type" : "long long int"  },

"unsigned long long" : {"size" : 8 , "equiv_type" : "unsigned short int"  },
"unsigned long long int" : {"size" : 8 , "equiv_type" : "unsigned short int"  },

"literal_float": {"size" : 4 , "equiv_type" : "float"  },
"float": {"size" : 4 , "equiv_type" : "float"  },
"double": {"size" : 8 , "equiv_type" : "double"  },
#"long double": {"size" : 10 , "equiv_type" : "long double"}

}


typedef_spec = ['typedef']
function_spec = ["inline","virtual","explicit" ]
friend_spec = ['friend']
storage_class_spec = ["register", 'static', 'extern', 'mutable']
#typename_specifier = []
cv_qualifier = ['const','volatile','const volatile']

all_specifiers = {
"typedef_spec":typedef_spec,
"function_spec":function_spec,
"friend_spec":friend_spec,
"storage_class_spec":storage_class_spec,
"cv_qualifier":cv_qualifier
}

specifiers = {}

for spec_type in all_specifiers:
    for spec in all_specifiers[spec_type]:
        specifiers[spec] = spec_type


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
            return copy.deepcopy(self.symtab[str(lexeme)])
        return None

    def lookupComplete(self, lexeme):
        scope = ScopeList[currentScope]
        while scope is not None:
            entry = scope["table"].lookup(lexeme)
            if entry != None:
                return copy.deepcopy(entry)
            scope = ScopeList[scope["parent"]]
        return None

    def insertID(self, name, id_type, types=None, specifiers=[], num=1, value=None, stars=0, order=[], parameters=[], defined=False):
        currtable = ScopeList[currentScope]["table"]
        #print("[Symbol Table]", currtable.symtab)

        if currtable.lookup(str(name)):         # No need to check again
            print("[Symbol Table] Entry already exists")
        else:
            currtable.symtab[str(name)] = {
                "name"      : str(name),
                "id_type"   : str(id_type),
                "type"      : list([] if types is None else types),        # List of data_types
                "specifier" : list([] if specifiers is None else specifiers),    # List of type specifiers
                "star"      : int(stars),
                "num"       : int(num),            # Number of such id
                "value"     : list(value) if type(value) is list else value,           # Mostly required for const type variable
                "order"     : list(order if order else []),          # order of array in case of array
                "parameters": list(parameters if parameters else []),   # Used for functions only
                "is_defined": bool(defined),
        #        "size"      : size
            }
            check_datatype(currtable.symtab[str(name)]["type"], name)
            check_specifier(currtable.symtab[str(name)]["specifier"], name)
            warning = ''
            if types is None:
                warning = "(warning: Type is None)"
            print("[Symbol Table] ", warning, " Inserting new identifier: ", name, " type: ", types, "specifier: ", specifiers)
            #ScopeList[-1]["table"].numVar += 1

    @staticmethod
    def addIDAttr(name, attribute, value):
        currtable = ScopeList[currentScope]["table"]
        if attribute in currtable.symtab[str(name)].keys():
            if currtable.symtab[str(name)][str(attribute)] is not None:
                currtable.symtab[str(name)][str(attribute)] += list(value)
            else:
                currtable.symtab[str(name)][str(attribute)] = list(value) if value is list else value
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

def check_datatype(types,name):
    """
    types: List of data types
    """
    input_type = ' '.join(types)
    currtable = ScopeList[currentScope]["table"]
    if input_type in simple_type_specifier:
        currtable.symtab[str(name)]["type"] = [simple_type_specifier[input_type]["equiv_type"]]
        SymTab.addIDAttr(name,"size", simple_type_specifier[input_type]["size"]* currtable.symtab[str(name)]["num"])
        return True
    else :
        print(" Error - Invalid string of data type - Taking the first element only")
        input_type = "" if len(types) == 0  else types[0]
        if input_type in simple_type_specifier:
            currtable.symtab[str(name)]["type"] = [simple_type_specifier[input_type]["equiv_type"]]
            SymTab.addIDAttr(name,"size", simple_type_specifier[input_type]["size"] *currtable.symtab[str(name)]["num"])
            return True
        else :
            print("Error - Invalid data type")
            return False
    pass

def check_specifier(specifier_list,name):
    """
    specifier_list: List of identifier specifiers
    """
    spec_dict = {
    "typedef_spec" : [],
    "function_spec" : [],
    "friend_spec" : [],
    "storage_class_spec": [],
    "cv_qualifier" :[]
    }

    for spec in specifier_list:
        if not spec_dict[specifiers[spec]]:
            spec_dict[specifiers[spec]].append(spec)
        else:
            print("Error - Multiple speciers of one type - Ignoring all but first")

    currtable = ScopeList[currentScope]["table"]
    id_type = currtable.symtab[str(name)]["id_type"]


    if spec_dict["typedef_spec"]:
        if list(filter(lambda x: x!= "typedef",specifier_list)):
            print("Error - No specifiers with typedef allowed - Ignoring all")
        spec_dict = {"typedef_spec" :"typedef"}

    if spec_dict["friend_spec"]:
        if id_type != "class" and id_type !="function" :
            print(" Error - Friend Specifier only allowed with class or function type of identifier")
            spec_dict["friend_spec"] = []

    if spec_dict["function_spec"]:
        if id_type != "function":
            print(" Error - Function Specifier only allowed with function type of identifier")
            spec_dict["function_spec"] = []
    dummy = []
    for attr in spec_dict:
        if spec_dict[attr]:
            dummy.append(spec_dict[attr][0])
            SymTab.addIDAttr(name,attr,spec_dict[attr][0])
    currtable.symtab[str(name)]["specifier"] = list(dummy)
    pass

def expression_type(l1,s1,l2,s2,op=None):
    if op == "=":
        if s1 == s2:
            return l1,s1
        else :
            return None
    if s1 != s2:
        print("Error - Different levels of dereferencing in the operands, Ignoring operation")
        return l1,s1

    type1 = simple_type_specifier[' '.join(l1)]["equiv_type"]
    type2 = simple_type_specifier[' '.join(l2)]["equiv_type"]

    if op in ["%","<<",">>","%=","<<=",">>="]:
        if type1 in eq_integral_types[:-2] and type2 in eq_integral_types[:-2]:
            l = eq_integral_types[max(eq_integral_types.index(type1),eq_integral_types.index(type1))]
            return l.split(" "),s1

        else:
            print("Error - Incorrect data types for ",op," Ignoring operation")
            return l1,s1

    if op in [ "^", "|" , "&", "+", "-", "/", "*", "^=", "|=" , "&=", "+=", "-=", "/=", "*="]:
        if type1 in eq_integral_types and type2 in eq_integral_types:
            l = eq_integral_types[max(eq_integral_types.index(type1),eq_integral_types.index(type1))]
            return l.split(" "),s1

        else:
            print("Error - Incorrect data types for ",op," Ignoring operation")
            return l1,s1

    if op in ["<", '>', '<=', '>=']:
        if type1 in eq_integral_types and type2 in eq_integral_types:
            return ["bool"],s1

    if op in ["&&","||"]:
        if type1 in [bool_types, eq_integral_types] and type2 in [bool_types, eq_integral_types]:
            return ["bool"],s1

    print("Error - Incompatible data types of operands, Ignoring operation")
    return l1,s1

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
        print("Line No.:", lineno, ": Error: index type: ", args[0], " for array \'", id1["name"], "\' is not of integral type")
    elif errno == 9:
        print("Line No.:", lineno, ": Error: index type is not const expression for array \'", id1["name"], "\'")
    elif errno == 10:
        print("Line No.:", lineno, ": Error: invalid conversion of ", id1["name"], "from ", args[0], " to array")
    elif errno == 11:
        print("Line No.:", lineno, ": Error: storage size of \'", id1["name"], "\' isn’t known")
    elif errno == 12:
        print("Line No.:", lineno, ": Error: expected  \'", args[1], "\' before \'", args[0], "\'")
    elif errno == 13:
        print("Line No.:", lineno, ": Error: lvalue  \'", id1["name"], "\' cannot be incremented or decremented ")
    elif errno == 14:
        print("Line No.:", lineno, ": Error: \'", args[0], "\' cannot be associated with \'", id1["name"], "\'")
    elif errno == 15:
        print("Line No.:", lineno, ": Syntax Error: invalid expression \'", args[0], "\'")
    elif errno == 16:
        print("Line No.:", lineno, ": Error: \'", args[0], "\' operations are not allowed in global scope")
    elif errno == 17:
        print("Line No.:", lineno, ": Error: \'", id1["name"], "\' is not an lvalue, thus cannot be assigned")
    elif errno == 18:
        print("Line No.:", lineno, ": Error: \'", args[0], "\' cannot be assigned \'", args[1], "\'")
    elif errno == 19:
        print("Line No.:", lineno, ": Error: const identifier \'", id1["name"], "\' cannot be modified")
    elif errno == 20:
        print("Line No.:", lineno, ": Error: empty braced declaration for variables are not allowed")
    elif errno == 21:
        print("Line No.:", lineno, ": Error: scalar object \'", args[0], "\' requires one element in initializer")
    elif errno == 22:
        print("Line No.:", lineno, ": Error: braces around scalar initializer for type \'", args[0], "\'")
    elif errno == 23:
        print("Line No.:", lineno, ": Error: invalid types for array \'", args[0], "\' subscript")
    elif errno == 24:
        print("Line No.:", lineno, ": Error: braced array \'", args[0], "\' subscript")
    elif errno == 25:
        print("Line No.:", lineno, ": Error: incorrect braced declaration \'", args[0], "\' subscript")
    elif errno == 26:
        print("Line No.:", lineno, ": Error: incorrect function parameter definitions")
    elif errno == 27:
        print("Line No.:", lineno, ": Error: incorrect condition in conditional statement ")
    elif errno == 28:
        print("Line No.:", lineno, ": Error: Multiple parameters in conditional statement, Ignoring all but last valid one ")
    
    pass

def print_table():
    pp = pprint.PrettyPrinter(indent=4)
    for scope in ScopeList.keys():
        if scope != "NULL":
            if ScopeList[scope]["table"].symtab:
                pp.pprint(ScopeList[scope]["table"].symtab)

if __name__ == '__main__':
    """a = SymTab()
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
        pass"""
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