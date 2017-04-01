import pprint, copy

### Scopes ###

global ScopeList, currentScope
ScopeList = { "NULL" : None, "global" : {"name":"global", "parent" : "NULL",}, }
currentScope = "global"
scope_ctr = 1

### Functions ###
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
"void": {"size" : 0, "equiv_type" : "void"},
}

### Specifiers ###

typedef_spec = ['typedef']
function_spec = ["inline","virtual","explicit" ]
friend_spec = ['friend']
storage_class_spec = ["register", 'static', 'extern', 'mutable', 'auto']
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

### Colors for logging ###
class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    cline = DARKCYAN + BOLD + "Line No.:"
    cerror = "::" + END + RED + BOLD + "ERROR:" + END

### SymTab class for SymbolTable ###

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

    def insertID(self, lineno, name, id_type, types=None, specifiers=[], num=1, value=None, stars=0, order=[], parameters=[], defined=False):
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
                "num"       : int(num),            # Number of such id
                "value"     : list(value) if type(value) is list else value,           # Mostly required for const type variable
                "star"      : int(stars),
                "order"     : list(order if order else []),          # order of array in case of array
                "parameters": copy.deepcopy(parameters if parameters else []),   # Used for functions only
                "is_defined": bool(defined),
        #        "size"      : size
            }
            check_datatype(lineno, currtable.symtab[str(name)]["type"], name, id_type)
            check_specifier(lineno, currtable.symtab[str(name)]["specifier"], name)
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

    @staticmethod
    def updateIDAttr(name, attribute, value):
        currtable = ScopeList[currentScope]["table"]
        currtable.symtab[str(name)].update({attribute : value})
        print("[Symbol Table] Updating attribute of identifier: ", name, " attribute: ", attribute, "value: ", value)

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

def check_datatype(lineno, types, name, id_type):
    """
    types: List of data types
    """
    input_type = ' '.join(types)
    currtable = ScopeList[currentScope]["table"]
    if input_type in simple_type_specifier:
        currtable.symtab[str(name)]["type"] = [simple_type_specifier[input_type]["equiv_type"]]
        if id_type not in ["function", "class"]:
            size = simple_type_specifier[input_type]["size"]
            if currtable.symtab[str(name)]["star"] > 0:
                size = 8
            SymTab.addIDAttr(name,"size", size * currtable.symtab[str(name)]["num"])
        return True
    else :
        print(color.cline, lineno, color.cerror + " Invalid string of data type - Taking the first element only")
        input_type = "" if len(types) == 0  else types[0]
        if input_type in simple_type_specifier:
            currtable.symtab[str(name)]["type"] = [simple_type_specifier[input_type]["equiv_type"]]
            if id_type not in ["function", "class"]:
                size = simple_type_specifier[input_type]["size"]
                if currtable.symtab[str(name)]["star"] > 0:
                    size = 8
                SymTab.addIDAttr(name,"size", size * currtable.symtab[str(name)]["num"])
            return True
        else :
            print(color.cline, lineno, color.cerror + " Invalid data type")
            return False
    pass

def check_specifier(lineno, specifier_list, name):
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
            print(color.cline, lineno, color.cerror + " Multiple speciers of one type - Ignoring all but first")

    currtable = ScopeList[currentScope]["table"]
    id_type = currtable.symtab[str(name)]["id_type"]

    if spec_dict["typedef_spec"]:
        if list(filter(lambda x: x!= "typedef",specifier_list)):
            print(color.cline, lineno, color.cerror + " No specifiers with typedef allowed - Ignoring all")
        spec_dict = {"typedef_spec" :"typedef"}

    if spec_dict["friend_spec"]:
        if id_type != "class" and id_type !="function" :
            print(color.cline, lineno, color.cerror + " Friend Specifier only allowed with class or function type of identifier")
            spec_dict["friend_spec"] = []

    if spec_dict["function_spec"]:
        if id_type != "function":
            print(color.cline, lineno, color.cerror + " Function Specifier only allowed with function type of identifier")
            spec_dict["function_spec"] = []
    dummy = []
    for attr in spec_dict:
        if spec_dict[attr]:
            dummy.append(spec_dict[attr][0])
            SymTab.addIDAttr(name,attr,spec_dict[attr][0])
    currtable.symtab[str(name)]["specifier"] = list(dummy)
    pass

def expression_type(lineno, l1, s1, l2, s2, op=None):
    type1 = simple_type_specifier[' '.join(l1)]["equiv_type"]
    type2 = simple_type_specifier[' '.join(l2)]["equiv_type"]
    if op == "=":
        if type2 == "void" or type1 == "void":
            print(color.cline, lineno, color.cerror + " Incorrect data types for ",op," Ignoring operation")
            return None
        if s1 == s2:
            return l1,s1
        else:
            print(color.cline, lineno, color.cerror + " Different levels of dereferencing in the operands, Ignoring operation")
            return None
    if s1 != s2:
        print(color.cline, lineno, color.cerror + " Different levels of dereferencing in the operands, Ignoring operation")
        return l1,s1

    if op in ["%","<<",">>","%=","<<=",">>="]:
        if type1 in eq_integral_types[:-2] and type2 in eq_integral_types[:-2]:
            l = eq_integral_types[max(eq_integral_types.index(type1),eq_integral_types.index(type1))]
            return l.split(" "),s1
        else:
            print(color.cline, lineno, color.cerror + " Incorrect data types for ",op," Ignoring operation")
            return l1,s1

    if op in [ "^", "|" , "&", "+", "-", "/", "*", "^=", "|=" , "&=", "+=", "-=", "/=", "*="]:
        if type1 in eq_integral_types and type2 in eq_integral_types:
            l = eq_integral_types[max(eq_integral_types.index(type1),eq_integral_types.index(type1))]
            return l.split(" "),s1
        else:
            print(color.cline, lineno, color.cerror + " Incorrect data types for ",op," Ignoring operation")
            return l1,s1

    if op in ["<", '>', '<=', '>=', '==']:
        if type1 in eq_integral_types and type2 in eq_integral_types:
            return ["bool"],s1

    if op in ["&&","||"]:
        if type1 in [bool_types, eq_integral_types] and type2 in [bool_types, eq_integral_types]:
            return ["bool"],s1

    print(color.cline, lineno, color.cerror + " Incompatible data types of operands, Ignoring operation")
    return l1,s1


def flatten(lineno, l):
    """ flattens the an irregular list of lists and filters out the empty parentheses
    """
    for elt in l:
        if isinstance(elt, list):
            if len(elt) == 0:
                print_error(lineno, {}, 12, ')', "primary_expression")
            else:
                yield from flatten(elt)
        else:
            yield elt


def check_func_params(lineno, func, params, param_list, decl=True):
    """ Check if all params are consistent with the func's parameter type in function call
    """
    if len(params) != len(func["parameters"]):
        print_error(lineno, {}, 30, "few" if len(params) < len(func["parameters"]) else "many", func["name"])
        return False
    c2 = all(param["id_type"] in param_list for param in params)
    if decl:
        c3 = all([ param.get("is_decl", True) for param in params])
    else:
        c3 = all([ not param.get("is_decl", False) for param in params])
    if not (c2 and c3):
        print_error(lineno, {}, 33)
        return False
    no_err = True
    for p1, p2 in zip(params, func["parameters"]):
        if simple_type_specifier.get(' '.join(p1["type"])) and simple_type_specifier.get(' '.join(p2["type"])) :
            if simple_type_specifier[' '.join(p1["type"])]["equiv_type"] != simple_type_specifier[' '.join(p2["type"])]["equiv_type"] :
                no_err = False
                print_error(lineno, {}, 31, p1["name"], p2["name"])
            elif p1["id_type"] in [pt for pt in param_list if pt not in ["literal"]] and set(p1["specifier"]) != set(p2["specifier"]):
                no_err = False
                print_error(lineno, {}, 34, p1["name"], p2["name"])
            elif p1.get("order", []) != p2.get("order", []):
                no_err = False
                print_error(lineno, {}, 35, p1["name"], p2["name"])
            elif p1.get("star", 0) != p2.get("star", 0):
                no_err = False
                print_error(lineno, {}, 31, p1["name"], p2["name"])
        else:
            no_err = False
            print_error(lineno,{}, 32, p1["name"])
    return no_err


def print_error(lineno, id1, errno, *args):
    if errno == 1:
        print(color.cline, lineno, color.cerror + " \'%s\' was not declared in this scope" % id1.get("name"))
    elif errno == 2:
        print(color.cline, lineno, color.cerror + " declaration does not declare anything")
    elif errno == 3:
        print(color.cline, lineno, color.cerror + " expected unqualified-id before \'%s\'" % args[0])
    elif errno == 4:
        if id1["type"] == args[0]:
            print(color.cline, lineno, color.cerror + " ", "redeclaration of \'%s\'" % id1["name"])
        else:
            print(color.cline, lineno, color.cerror + " ", "conflicting declaration \'%s\', previously declared as \'%s\'" % (id1["name"], id1["type"]))
    elif errno == 5:
        print(color.cline, lineno, color.cerror + " uninitialized const \'%s\'" % id1["name"])
    elif errno == 6:
        print(color.cline, lineno, color.cerror + " ", "conflicting declaration \'%s\', previously declared as \'%s\'" % (id1["name"], id1["specifier"]))
    elif errno == 7:
        print(color.cline, lineno, color.cerror + " \'%s\' is not of array type" % id1["name"])
    elif errno == 8:
        print(color.cline, lineno, color.cerror + " index type: \'%s\' for array \'%s\' is not of integral type" % (args[0], id1["name"]))
    elif errno == 9:
        print(color.cline, lineno, color.cerror + " index type is not const expression for array \'%s\'" % id1["name"])
    elif errno == 10:
        print(color.cline, lineno, color.cerror + " invalid conversion of \'%s\' from \'%s\' to array" % (id1["name"], args[0]))
    elif errno == 11:
        print(color.cline, lineno, color.cerror + " storage size of \'%s\' isn’t known" % id1["name"])
    elif errno == 12:
        print(color.cline, lineno, color.cerror + " expected  \'%s\' before \'%s\'" % (args[1], args[0]))
    elif errno == 13:
        print(color.cline, lineno, color.cerror + " lvalue  \'%s\' cannot be incremented or decremented " % args[0])
    elif errno == 14:
        print(color.cline, lineno, color.cerror + " \'%s\' cannot be associated with \'%s\'" % (args[0], id1["name"]))
    elif errno == 15:
        print(color.cline, lineno, color.cerror + " invalid syntax or expression \'%s\'" % args[0])
    elif errno == 16:
        print(color.cline, lineno, color.cerror + " \'%s\' operations are not allowed in global scope" % args[0])
    elif errno == 17:
        print(color.cline, lineno, color.cerror + " \'%s\' is not an lvalue, thus cannot be assigned" % id1["name"])
    elif errno == 18:
        print(color.cline, lineno, color.cerror + " \'%s\' cannot be assigned \'%s\'" % (args[0], args[1]))
    elif errno == 19:
        print(color.cline, lineno, color.cerror + " const identifier \'%s\' cannot be modified" % id1["name"])
    elif errno == 20:
        print(color.cline, lineno, color.cerror + " empty braced declaration for variables are not allowed")
    elif errno == 21:
        print(color.cline, lineno, color.cerror + " scalar object \'%s\' requires one element in initializer" % args[0])
    elif errno == 22:
        print(color.cline, lineno, color.cerror + " braces around scalar initializer for type \'%s\'" % args[0])
    elif errno == 23:
        print(color.cline, lineno, color.cerror + " invalid types for array \'%s\' subscript" % args[0])
    elif errno == 24:
        print(color.cline, lineno, color.cerror + " braced array \'%s\' subscript" % args[0])
    elif errno == 25:
        print(color.cline, lineno, color.cerror + " incorrect braced declaration \'%s\' subscript" % args[0])
    elif errno == 26:
        print(color.cline, lineno, color.cerror + " incorrect function parameter definitions")
    elif errno == 27:
        print(color.cline, lineno, color.cerror + " function definition is not allowed here")
    elif errno == 28:
        print(color.cline, lineno, color.cerror + " In function \'%s\' parameter name omitted" % args[0])
    elif errno == 29:
        print(color.cline, lineno, color.cerror + " redeclaration of function \'%s\'" % args[0])
    elif errno == 30:
        print(color.cline, lineno, color.cerror + " Too \'%s\' arguments for function \'%s\'" % (args[0], args[1]))
    elif errno == 31:
        print(color.cline, lineno, color.cerror + " parameter type mismatch between \'%s\' and \'%s\'" % (args[0], args[1]))
    elif errno == 32:
        print(color.cline, lineno, color.cerror + " invalid type of parameter \'%s\'" % args[0])
    elif errno == 33:
        print(color.cline, lineno, color.cerror + " invalid parameters")
    elif errno == 34:
        print(color.cline, lineno, color.cerror + " parameter specifier mismatch between \'%s\' and \'%s\'" % (args[0], args[1]))
    elif errno == 35:
        print(color.cline, lineno, color.cerror + " parameter of array type mismatch between \'%s\' and \'%s\'" % (args[0], args[1]))
    elif errno == 36:
        print(color.cline, lineno, color.cerror + " Return type mismatch of function \'%s\' whose return type is \'%s\'" % (args[0], args[1]))
    elif errno == 37:
        print(color.cline, lineno, color.cerror + " incorrect condition in conditional statement")
    elif errno == 38:
        print(color.cline, lineno, color.cerror + " Multiple parameters in conditional statement, Ignoring all but last valid one")
    pass

def print_table():
    pp = pprint.PrettyPrinter(indent=4)
    for scope in ScopeList.keys():
        if scope != "NULL":
            print("Scope Name:", scope)
            if ScopeList[scope]["table"].symtab:
                pp.pprint(ScopeList[scope]["table"].symtab)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

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
