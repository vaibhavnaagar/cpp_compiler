#!/usr/bin/python3

# -----------------------------------------------------------------------------
# cpp_parser.py
#
# Parser for C++.  Based on the grammar written by -
# *  Author:         E.D.Willink             Ed.Willink@rrl.co.uk
# *  Date:           19-Nov-1999
# Template feature is removed from the grammar to remove reduce-reduce conflicts.
#-----------------------------------------------------------------------------
import sys
import cpp_lexer as lex
import ply.yacc as yacc
import pydot
import symtable as st
import pprint
import tac
from functools import reduce
import operator
import codegen as cg
# Symbol table
#SymbolTable = None

orphan_children = []
i = 0
graph = pydot.Dot(graph_type='graph')
def add_children(n,name):
	global i
	global orphan_children
	if n > len(orphan_children):
		#print("===========================================ERROR============================> " + name)
		#for child in orphan_children:
			#print(child.get_label())
		#print(n)
		pass
	node_a = pydot.Node(str(i),label=str(name))
	if n==0:
		return
	if n==1:
		if name == 'return' or name =="asm":
			graph.add_node(node_a)
			i+=1
			child = orphan_children[-1]
			graph.add_edge(pydot.Edge(node_a, child))
			orphan_children.remove(child)
			orphan_children.append(node_a)

	if n>1:
		graph.add_node(node_a)
		i+=1
		children = orphan_children[-n:]
		for child in children:
			if child == None:
				print("Error")
			graph.add_edge(pydot.Edge(node_a, child))
			orphan_children.remove(child)
		orphan_children.append(node_a)
	return

def create_child(label,name):
	global i
	global orphan_children
	node_a = pydot.Node(str(i),label=str(name))
	i+=1
	graph.add_node(node_a)
	orphan_children.append(node_a)
	return

def expression_semantic(lineno, p0, p1, p2, p3):
	if st.currentScope == "global":
		st.print_error(lineno, {}, 16,  p2)
		p0 = p1
		return p0
	if p3.get("is_decl", True) is False:	# When only a variable is present on Right of operator
		p0 = p1
		if p3["type"]:
			st.print_error(lineno, {}, 15, ' '.join([p1["name"], p2, p3["name"]]))
			return p0
		entry = SymbolTable.lookupComplete(p3["name"])
		if entry is None:
			st.print_error(lineno, p3, 1)
			return p0
		else:
			p3 = dict(entry)
			p3["is_decl"] = True
	if p1.get("is_decl", True) is False:	# When only a variable is present on left of operator
		p0 = p3
		if p1["type"]:
			st.print_error(lineno, {}, 15, ' '.join([p1["name"], p2, p3["name"]]))
			return p0
		entry = SymbolTable.lookupComplete(p1["name"])
		if entry is None:
			st.print_error(lineno, p1, 1)
			return p0
		else:
			p1 = dict(entry)
			p1["is_decl"] = True
	if p3.get("id_type") not in ["variable", "literal"]:		#  id_type should only be variable
		st.print_error(lineno, {}, 15, ' '.join([p1["name"], p2, p3["name"]]))
		p0 = p1
		return p0
	elif p1.get("id_type") not in ["variable", "literal"]:		#  id_type should only be variable
		st.print_error(lineno, {}, 15, ' '.join([p1["name"], p2, p3["name"]]))
		p0 = p3
		return p0
	if (p1["id_type"] == "literal") and (p3["id_type"] != "literal"):	# Try to get dictionary of variable
		p0 = p3
	else:
		p0 = p1

	if p1.get("real_id_type") in ["function", "class"] and p1["tac_name"] == p1["name"] + "_" + p1["myscope"]:
		s1 = "pop"
	else:
		s1 =  p1["tac_name"]

	if p3.get("real_id_type") in ["function", "class"] and p3["tac_name"] == p3["name"] + "_" + p3["myscope"]:
		s2 = "pop"
	else:
		s2 =  p3["tac_name"]

	p0["name"] = ' '.join([p1["name"], p2, p3["name"]])
	p0["type"],p0["star"] = st.expression_type(lineno, p1["type"], p1.get("star", 0) , p3["type"], p3.get("star", 0), op=str(p2))


	temp = st.ScopeList[st.currentScope]["tac"].getnewtemp()
	_scope = st.currentScope
	if len(st.function_list) > 0:
		_scope = st.function_list[-1]["name"]
	elif len(st.namespace_list) > 0:
		_scope = st.namespace_list[-1]["name"]

	p0["tac_name"] = temp + "_" + str(_scope)
	st.ScopeList[st.currentScope]["tac"].expression_emit(p0["tac_name"],s1,p2,s2,p0["type"])

	# Insert temporary
	SymbolTable.insertTemp(p0["tac_name"], "temporary", _scope, p0["type"])

	if p1.get("inc",False):
		st.ScopeList[st.currentScope]["tac"].expression_emit(p1["tac_name"],'',"++", '')
	if p3.get("inc",False):
		st.ScopeList[st.currentScope]["tac"].expression_emit(p3["tac_name"],'',"++", '')
	if p1.get("dec",False):
		st.ScopeList[st.currentScope]["tac"].expression_emit(p1["tac_name"],'',"--", '')
	if p3.get("dec",False):
		st.ScopeList[st.currentScope]["tac"].expression_emit(p3["tac_name"],'',"--", '')

	return p0

def array_assignment(p,inits,store_list):
	#pp = pprint.PrettyPrinter(indent=4)
	#pp.pprint( inits)
	if len(inits) == 0:
			store_list = [0]*len(store_list)
			return store_list

	elif len(inits) == 1:
			if inits[0]["id_type"] in ["literal", "variable"]:
				if st.expression_type(p.lineno(1), p[1]["type"], p[1].get("star", 0) , inits[0]["type"], inits[0].get("star", 0), op=str(p[2])):
					store_list = [inits[0]["value"]]*len(store_list)
			return store_list

	elif len(inits) == len(store_list):
		for i,exp in enumerate(inits):
			if type(exp) is list:
				st.print_error(p.lineno(1), {}, 22, p[1]["type"])
				return None
			else:
				if exp["id_type"] in ["literal", "variable"]:
					if st.expression_type(p.lineno(1), p[1]["type"], p[1].get("star", 0) , exp["type"], exp.get("star", 0), op=str(p[2])):
						store_list[i] = exp["value"]
		return store_list

	elif len(inits) == p[0]["order"][0]:
		size = len(store_list)/len(inits)
		for i,exp in enumerate(inits):
			if type(exp) is not list:
				st.print_error(p.lineno(1), {}, 22, p[1]["type"])
				return None
			else :
				store_list = array_assignment(p,exp,store_list[size*i,size*(i+1)])
				if not store_list:
					st.print_error(p.lineno(1), {}, 22, p[1]["type"])
					return None
	else:
		st.print_error(p.lineno(1), {}, 22, p[1]["type"])

# Get the token map
tokens = lex.cpp_scanner.tokens

precedence = (
				('nonassoc', 'SHIFT_THERE'),
				('nonassoc', 'SCOPE', 'ELSE', 'INC', 'DEC', '+', '-', '*', '&', '[', '{', '<', ':', 'STRING'),
				('nonassoc', 'REDUCE_HERE_MOSTLY'),
				('nonassoc', '('),
			)

start = 'translation_unit'

def p_identifier(p):
	"identifier : IDENTIFIER"
	create_child("identifier",p[1])
	entry = st.ScopeList[st.currentScope]["table"].lookup(p[1])
	if entry is not None:
		p[0] = dict(entry)
		p[0]["is_decl"] = True
	else:
		p[0] = {
			"name" : str(p[1]),
			"id_type" : "variable",
			"is_decl" : False,
			"type" : None,
			"specifier" : None,
			"star"	: 0,
			"num"	: 1,
			"value" : None,
			"order"	: [],
			"parameters" : None,
			"is_defined" : False,	# Used For functions only
			"myscope" : str(st.currentScope),
		}
	pass

def p_id1(p):
	"id : identifier"
	add_children(len(list(filter(None, p[1:]))),"id")
	p[0] = p[1]
	pass


def p_global_scope1(p):
	"global_scope : SCOPE"
	create_child("global_scope",p[1])
	p[0] = p[1]
	pass


def p_id_scope(p):
	"id_scope : id SCOPE"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"id_scope")
	if p[1]["is_decl"] is False:
		entry = None
			#entry = st.ScopeList[st.currentScope]["table"].lookup(p[1]["name"])
		if not st.is_ns_member:
			entry = SymbolTable.lookupComplete(p[1]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[1], 1)
			return
		else:
			p[1] = dict(entry)
			p[1]["is_decl"] = True
	if p[1]["id_type"] not in ["namespace", "class", "struct",]:
		st.print_error(p.lineno(1), {}, 39, p[1]["name"], "::")
		return
	st.is_ns_member = True
	st.scope_transitions.append(str(st.currentScope))
	st.currentScope = str(p[1]["name"])
	p[0] = p[1]
	pass

#/*
#*  A :: B :: C; is ambiguous How much is type and how much name ?
#*  The %prec maximises the (type) length which is the 7.1-2 semantic constraint.
#*/

def p_nested_id1(p):
	"nested_id : id                                  %prec SHIFT_THERE"
	add_children(len(list(filter(None, p[1:]))),"nested_id")
	p[0] = p[1]
	if st.is_namespace:
		st.is_namespace = False
		if p[0].get("is_decl") and (p[0].get("id_type") not in ["namespace",]):
			return
		else:
			p[0]["id_type"] = "namespace"
			st.namespace_list.append(p[0])
	pass

def p_nested_id2(p):
	"nested_id : id_scope nested_id"
	add_children(len(list(filter(None, p[1:]))),"nested_id")
	p[0] = p[2]
	if p[1] is None:
		return
	if (not p[0]["is_decl"]) and st.is_ns_member:
		st.print_error(p.lineno(1), {}, 40, p[0]["name"], "namespace", "::".join(st.scope_transitions[1:] + [p[1]["name"]]))
	st.is_ns_member = False
	st.currentScope = st.scope_transitions.pop()
	print("[PARSER] popped scope: ", st.currentScope, st.scope_transitions)
	pass

def p_scoped_id1(p):
	"scoped_id : nested_id"
	add_children(len(list(filter(None, p[1:]))),"scoped_id")
	p[0] = p[1]
	pass

def p_scoped_id2(p):
	"scoped_id : global_scope nested_id"
	add_children(len(list(filter(None, p[1:]))),"scoped_id")
	p[0] = p[2]
	pass

#/*
#*  destructor_id has to be held back to avoid a conflict with a one's complement as per 5.3.1-9,
#*  It gets put back only when scoped or in a declarator_id, which is only used as an explicit member name.
#*  Declarations of an unscoped destructor are always parsed as a one's complement.
#*/

def p_destructor_id1(p):
	"destructor_id : '~' id"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"destructor_id")
	pass


def p_special_function_id1(p):
	"special_function_id : conversion_function_id"
	add_children(len(list(filter(None, p[1:]))),"special_function_id")
	pass

def p_special_function_id2(p):
	"special_function_id : operator_function_id"
	add_children(len(list(filter(None, p[1:]))),"special_function_id")
	pass


def p_nested_special_function_id1(p):
	"nested_special_function_id : special_function_id"
	add_children(len(list(filter(None, p[1:]))),"nested_special_function_id")
	pass

def p_nested_special_function_id2(p):
	"nested_special_function_id : id_scope destructor_id"
	add_children(len(list(filter(None, p[1:]))),"nested_special_function_id")
	pass

def p_nested_special_function_id3(p):
	"nested_special_function_id : id_scope nested_special_function_id"
	add_children(len(list(filter(None, p[1:]))),"nested_special_function_id")
	pass

def p_scoped_special_function_id1(p):
	"scoped_special_function_id : nested_special_function_id"
	add_children(len(list(filter(None, p[1:]))),"scoped_special_function_id")
	pass

def p_scoped_special_function_id2(p):
	"scoped_special_function_id : global_scope nested_special_function_id"
	add_children(len(list(filter(None, p[1:]))),"scoped_special_function_id")
	pass

#/* declarator-id is all names in all scopes, except reserved words */

def p_declarator_id1(p):
	"declarator_id : scoped_id"
	add_children(len(list(filter(None, p[1:]))),"declarator_id")
	p[0] = p[1]
	pass

def p_declarator_id2(p):
	"declarator_id : scoped_special_function_id"
	add_children(len(list(filter(None, p[1:]))),"declarator_id")
	pass

def p_declarator_id3(p):
	"declarator_id : destructor_id"
	add_children(len(list(filter(None, p[1:]))),"declarator_id")
	pass

#/*  The standard defines pseudo-destructors in terms of type-name, which is class/enum/typedef, of which
# *  class-name is covered by a normal destructor. pseudo-destructors are supposed to support ~int() in
# *  templates, so the grammar here covers built-in names. Other names are covered by the lack of
# *  identifier/type discrimination.
# */

def p_built_in_type_id1(p):
	"built_in_type_id : built_in_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"built_in_type_id")
	p[0] = p[1]
	pass

def p_built_in_type_id2(p):
	"built_in_type_id : built_in_type_id built_in_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"built_in_type_id")
	pass

def p_pseudo_destructor_id1(p):
	"pseudo_destructor_id : built_in_type_id SCOPE '~' built_in_type_id"
	create_children("None",p[2])
	create_children("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"pseudo_destructor_id")
	pass

def p_pseudo_destructor_id2(p):
	"pseudo_destructor_id : '~' built_in_type_id"
	create_children("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"pseudo_destructor_id")
	pass


def p_nested_pseudo_destructor_id1(p):
	"nested_pseudo_destructor_id : pseudo_destructor_id"
	add_children(len(list(filter(None, p[1:]))),"nested_pseudo_destructor_id")
	pass

def p_nested_pseudo_destructor_id2(p):
	"nested_pseudo_destructor_id : id_scope nested_pseudo_destructor_id"
	add_children(len(list(filter(None, p[1:]))),"nested_pseudo_destructor_id")
	pass

def p_scoped_pseudo_destructor_id1(p):
	"scoped_pseudo_destructor_id : nested_pseudo_destructor_id"
	add_children(len(list(filter(None, p[1:]))),"scoped_pseudo_destructor_id")
	pass

def p_scoped_pseudo_destructor_id2(p):
	"scoped_pseudo_destructor_id : global_scope scoped_pseudo_destructor_id"
	add_children(len(list(filter(None, p[1:]))),"scoped_pseudo_destructor_id")
	pass

#/*---------------------------------------------------------------------------------------------------
# * A.2 Lexical conventions
# *---------------------------------------------------------------------------------------------------*/
#/*
# *  String concatenation is a phase 6, not phase 7 activity so does not really belong in the grammar.
# *  However it may be convenient to have it here to make this grammar fully functional.
# *  Unfortunately it introduces a conflict with the generalised parsing of extern "C" which
# *  is correctly resolved to maximise the string length as the token source should do anyway.
# */

def p_string(p):
	"string : STRING"
	create_child("string",p[1])
	p[0] = p[1]
	pass

def p_literal1(p):
	"literal : INTEGER"
	create_child("literal - int",p[1])
	p[0] = {
		"name"	: str(p[1]),
		"type"  : ["literal_int"],
		"id_type" : "literal",
		"value" : int(p[1]),
		"tac_name" : str(p[1])
	}
	pass

def p_literal2(p):
	"literal : CHARACTER"
	create_child("literal - char",p[1])
	p[0] = {
		"name"	: str(p[1][1:-1]),
		"type"  : ["literal_char"],
		"id_type" : "literal",
		"value" : str(p[1][1:-1]),
		"tac_name" : str(p[1])
	}
	pass

def p_literal3(p):
	"literal : FLOATING"
	create_child("literal - float",p[1])
	p[0] = {
		"name"	: str(p[1]),
		"type"  : ["literal_float"],
		"id_type" : "literal",
		"value" : float(p[1]),
		"tac_name" : str(p[1])
	}
	pass

def p_literal4(p):
	"literal : string"
	add_children(len(list(filter(None, p[1:]))),"literal")
	p[0] = {
		"name"	: str(p[1][1:-1]),
		"type"  : ["literal_string"],
		"id_type" : "literal",
		"value" : str(p[1][1:-1]),
		"tac_name" : str(p[1])
	}
	pass

def p_literal5(p):
	"literal : boolean_literal"
	add_children(len(list(filter(None, p[1:]))),"literal")
	p[0] = p[1]
	pass

def p_boolean_literal1(p):
	"boolean_literal : FALSE"
	create_child("boolean",p[1])
	p[0] = {
		"name"	: str(p[1]),
		"type"  : ["literal_bool"],
		"id_type" : "literal",
		"value" : 0,
		"tac_name" : str(p[1])
	}
	pass

def p_boolean_literal2(p):
	"boolean_literal : TRUE"
	create_child("boolean",p[1])
	p[0] = {
		"name"	: str(p[1]),
		"type"  : ["literal_bool"],
		"id_type" : "literal",
		"value" : 1,
		"tac_name" : str(p[1])
	}
	pass

#/*---------------------------------------------------------------------------------------------------
# * A.3 Basic concepts
# *---------------------------------------------------------------------------------------------------*/

def p_translation_unit(p):
	"translation_unit : declaration_seq_opt"
	add_children(len(list(filter(None, p[1:]))),"translation_unit")
	pass

#/*---------------------------------------------------------------------------------------------------
# * A.4 Expressions
# *---------------------------------------------------------------------------------------------------
# *  primary_expression covers an arbitrary sequence of all names with the exception of an unscoped destructor,
# *  which is parsed as its unary expression which is the correct disambiguation (when ambiguous).
# *  This eliminates the traditional A(B) meaning A B ambiguity, since we never have to tack an A onto
# *  the front of something that might start with (. The name length got maximised ab initio. The downside
# *  is that semantic interpretation must split the names up again.


def p_primary_expression1(p):
	"primary_expression : literal"
	add_children(len(list(filter(None, p[1:]))),"primary expression")
	p[0] = p[1]
	pass

def p_primary_expression2(p):
	"primary_expression : THIS"
	create_child("primary_expression",p[1])
	p[0] = p[1]
	pass

def p_primary_expression3(p):
	"primary_expression : suffix_decl_specified_ids"
	add_children(len(list(filter(None, p[1:]))),"primary expression")
	p[0] = p[1]
	pass

def p_primary_expression4(p):
	"primary_expression : abstract_expression               %prec REDUCE_HERE_MOSTLY"
	add_children(len(list(filter(None, p[1:]))),"primary expression")
	p[0] = p[1]
	pass

#/*
# *  Abstract-expression covers the () and [] of abstract-declarators.
# */

def p_abstract_expression1(p):
	"abstract_expression : parenthesis_clause"
	add_children(len(list(filter(None, p[1:]))),"abstract_expression")
	# Expressions like (a+b, 2*5, x=7+y, z-4) which are evaluated from left to right and
	# rightmost expression is considered
	p[0] = list(st.flatten(p.lineno(1), p[1]))
	if len(p[0]) == 0:
		st.print_error(p.lineno(1), {}, 12, ')', "primary_expression")
		p[0] = dict(name="0", type=["literal_int"], id_type="literal", value=0) # Assuming 0
	else:
		p[0] = p[0][-1]		# Get last expression
	pass

def p_abstract_expression2(p):
	"abstract_expression : '[' expression_opt ']'"
	create_child("None","[")
	create_child("None","]")
	add_children(len(list(filter(None, p[1:]))),"abstract_expression")
	pass

'''
#def p_type1_parameters1(p):
#    "type1_parameters : parameter_declaration_list ';'"
	pass

#def p_type1_parameters2(p):
#    "type1_parameters : type1_parameters parameter_declaration_list ';'"
	pass

#def p_mark_type1(p):
#    "mark_type1 : empty"
	pass
'''

def p_postfix_expression1(p):
	"postfix_expression : primary_expression"
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	p[0] = p[1]
	pass

def p_postfix_expression2(p):
	"postfix_expression : postfix_expression parenthesis_clause"
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	p[0] = p[1]
	if p[0]["id_type"] not in ["variable", "function","literal"]:
		st.print_error(p.lineno(1), p[0], 14, "()")
		return
	if p[0]["is_decl"]:
		if p[0]["id_type"] == "variable":	# Variable()
			st.print_error(p.lineno(1), p[0], 14, "()")
			return
		if p[0]["is_defined"]:				# Function Call
			for idx, param in enumerate(p[2]):
				if param.get("is_decl", True) is False:
					entry = SymbolTable.lookupComplete(param["name"])
					if entry is None:
						st.print_error(p.lineno(1), param, 1)
					else:
						p[2][idx] = dict(entry)
						p[2][idx]["is_decl"] = True
			if st.check_func_params(p.lineno(1), p[0], p[2], ["variable", "literal", "array"], decl=True):
				for param in p[2]:
					if param.get("real_id_type") in ["function", "class"] and param["tac_name"] == param["name"] + "_" + param["myscope"]:
						st.ScopeList[st.currentScope]["tac"].emit(["param","pop"])
					else:
						st.ScopeList[st.currentScope]["tac"].emit(["param",str(param["tac_name"])])
				st.ScopeList[st.currentScope]["tac"].emit(["call",p[1]["name"],",",str(len(p[2]))])

			p[0]["real_id_type"] = p[0]["id_type"]
			p[0]["id_type"] = "variable"

		else:								# Function definition
			if st.parenthesis_ctr > 1:		# parentheses in parameter definitions
				st.print_error(p.lineno(1), {}, 26)
				return
			if st.check_func_params(p.lineno(1), p[0], p[2], ["variable", "array", "parameter"], decl=False):
				p[0]["parameters"] = p[2]
			else:
				p[0]["parameters"] = []
	else:
		if p[0]["type"] is None:			# Function call (function from some parent scopes)
			entry = SymbolTable.lookupComplete(p[0]["name"])
			if entry is None:
				st.print_error(p.lineno(1), p[0], 1)
				return
			else:
				p[0] = dict(entry)
				p[0]["is_decl"] = True
				if p[0]["id_type"] not in ["function"]:
					st.print_error(p.lineno(1), p[0], 14, "()")
					return
				else:
					for idx, param in enumerate(p[2]):
						if param.get("is_decl", True) is False:
							entry = SymbolTable.lookupComplete(param["name"])
							if entry is None:
								st.print_error(p.lineno(1), param, 1)
							else:
								p[2][idx] = dict(entry)
								p[2][idx]["is_decl"] = True
					if st.check_func_params(p.lineno(1), p[0], p[2], ["variable", "array", "literal"], decl=True):
						for param in p[2]:
							if param.get("real_id_type") in ["function", "class"] and param["tac_name"] == param["name"] + "_" + param["myscope"]:
								st.ScopeList[st.currentScope]["tac"].emit(["param","pop"])
							else:
								st.ScopeList[st.currentScope]["tac"].emit(["param",str(param["tac_name"])])
						st.ScopeList[st.currentScope]["tac"].emit(["call",p[1]["name"],",",str(len(p[2]))])

					for param in p[0]["parameters"]:
						param["id_type"] = "variable" if param["id_type"] == "parameter" else param["id_type"]
					p[0]["real_id_type"] = p[0]["id_type"]
					p[0]["id_type"] = "variable"
		else:								# Function declaration or definition
			p[0]["id_type"] = "function"
			if st.parenthesis_ctr > 1:		# parentheses in parameter definitions
				st.print_error(p.lineno(1), {}, 26)
				return
			c1 = all(param["id_type"] in ["type_specifier", "variable", "array", "parameter"] for param in p[2])
			c2 = all([ not param.get("is_decl", False) for param in p[2]])
			c3 = all([ ' '.join(param["type"] if param.get("type") else []) in st.simple_type_specifier for param in p[2]])
			c4 = all([ set(param["specifier"] if param.get("specifier") else []).issubset(st.parameter_specifiers) for param in p[2]])
			c5 = all([ len(param["specifier"] if param.get("specifier") else []) == len(set(param.get("specifier") if param.get("specifier") else [])) for param in p[2]])
			if c1 and c2 and c3 and c4 and c5:
				params_name = []
				params = []
				for param in p[2]:
					if (param["id_type"] in ["variable", "array", "parameter"]) and (param["name"] in params_name):
						st.print_error(p.lineno(1), param, 4, param["type"])
					else:
						param["id_type"] = "variable" if param["id_type"] == "parameter" else param["id_type"]
						params += [param]
						params_name += [param["name"]]
				p[0]["parameters"] = params
			else:
				st.print_error(p.lineno(1), {}, 26)
	pass

'''
#def p_postfix_expression2(p):
#    "postfix_expression : postfix_expression parenthesis_clause mark_type1 '-'"
	pass

#def p_postfix_expression3(p):
#    "postfix_expression : postfix_expression parenthesis_clause mark_type1 '+' type1_parameters mark '{' error"
	pass

#def p_postfix_expression4(p):
#    "postfix_expression : postfix_expression parenthesis_clause mark_type1 '+' type1_parameters mark error"
	pass

#def p_postfix_expression5(p):
#    "postfix_expression : postfix_expression parenthesis_clause mark_type1 '+' error"
	pass
'''

def p_postfix_expression6(p):
	"postfix_expression : postfix_expression '[' expression_opt ']'"
	create_child("None","[")
	create_child("None","]")
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	p[0] = p[1]
	if p[1].get("is_decl") is None:		# If no identifier received
		if p[1]["id_type"] in ["type_specifier"] and st.is_func_decl is True:
			if p[3] is None:
				st.print_error(p.lineno(1), p[1], 11)
			elif type(p[3]) is list:
				st.print_error(p.lineno(1), {}, 12, ',', ']')
			elif not set(p[3]["type"]).issubset(st.integral_types):
				st.print_error(p.lineno(1), p[1], 8, p[3]["type"])
			elif (p[3]["type"] != ["literal_int"]) and ("const" not in p[3].get("specifier")):
				st.print_error(p.lineno(1), p[1], 9)
			else:
				if p[0].get("order"):
					p[0]["order"].append(p[3]["value"])
				else:
					p[0]["order"] = [p[3]["value"]]
		else:
			st.print_error(p.lineno(1), {}, 3, p[2])
		return
	if p[1]["is_decl"] is False:								# Identifier is not declared
		if p[1]["type"] is None:
			entry = SymbolTable.lookupComplete(p[1]["name"])
			if entry is None:
				st.print_error(p.lineno(1), p[1], 1)
				return
			else:
				p[0] = dict(entry)
				p[0]["is_decl"] = True
		else:
			if p[1]["id_type"] in ["function", "literal"]:
				st.print_error(p.lineno(1), p[1], 10, p[1]["id_type"])
				return
			if p[3] is None:
				st.print_error(p.lineno(1), p[1], 11)
			elif type(p[3]) is list:
				st.print_error(p.lineno(1), {}, 12, ',', ']')
			elif not set(p[3]["type"]).issubset(st.integral_types):
				st.print_error(p.lineno(1), p[1], 8, p[3]["type"])
			elif (p[3]["type"] != ["literal_int"]) and ("const" not in p[3].get("specifier")):
				st.print_error(p.lineno(1), p[1], 9)
			else:
				p[0]["id_type"] = "array"
				p[0]["order"].append(p[3]["value"])
				p[0]["num"] *= p[3]["value"]
	if p[0]["is_decl"] is True:				# Identifier is already declared, now expression_opt should have integral type
		if p[0]["id_type"] != "array":
			st.print_error(p.lineno(1), p[0], 7)
		elif len(p[0]["order"]) == 0:
			st.print_error(p.lineno(1), {}, 23, p[0]["name"])
		elif p[3] is None:
			st.print_error(p.lineno(1), p[1], 11)
		elif type(p[3]) is list:
			st.print_error(p.lineno(1), {}, 12, ',', ']')
		elif not set(p[3]["type"]).issubset(st.integral_types):
			st.print_error(p.lineno(1), p[1], 8, p[3]["type"])
		else:
			p[0]["order"] = p[0]["order"][1:]
			product = reduce((lambda x, y: x * y), p[0]["order"],1)
			p[0]["index"] = p[0].get("index",0) + product*p[3]["value"]
			if len(p[0]["order"]) == 0:
				size = st.simple_type_specifier[" ".join(p[0]["type"])]["size"]
				p[0]["tac_name"] =  "*(" + p[0]["tac_name"] + "+" + str(p[0]["index"]*size) + ")"
				p[0]["real_id_type"] = p[0]["id_type"]
				p[0]["id_type"] = "variable"		# Array is completely dereferenced to a single memory location
	pass

def p_postfix_expression7(p):
	"postfix_expression : postfix_expression '.' declarator_id"
	create_child("None",".")
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	p[0] = p[3]
	if (p[1].get("is_decl", True) is False) and  (p[1].get("id_type") in ["variable"]):
		entry = SymbolTable.lookupComplete(p[1]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[1], 1)
			return
		else:
			p[1] = dict(entry)
			p[1]["is_decl"] = True
	if p[1].get("id_type") not in ["object"]:
		st.print_error(p.lineno(1), {}, 54, "*"*p[1]["star"] + p[1]["name"])
		return
	if p[1].get("star", 0) == 1:
		st.print_error(p.lineno(1), {}, 56, p[0]["name"], "*"*p[1]["star"] + p[1]["name"])
	elif p[1].get("star", 0) > 1:
		st.print_error(p.lineno(1), {}, 54, "*"*p[1]["star"] + p[1]["name"])
	else:
		if p[1]["myscope"] in st.ScopeList.keys():
			entry = st.ScopeList[str(p[1]["myscope"])]["table"].lookup(p[0]["name"])
			if entry is None:
				st.print_error(p.lineno(1), {}, 55, p[0]["name"], p[1]["name"])
			else:
				if entry["access"] in ["private", "protected"]:
					st.print_error(p.lineno(1), {}, 59, " ".join([entry["id_type"]] + entry["type"] + [entry["name"]]), entry["access"])
				else:
					p[0] = dict(entry)
					p[0]["is_decl"] = True
		else:
			st.print_error(p.lineno(1), {}, 54, "*"*p[1]["star"] + p[1]["name"])
	pass

def p_postfix_expression8(p):
	"postfix_expression : postfix_expression '.' scoped_pseudo_destructor_id"
	create_child("None",".")
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	pass

def p_postfix_expression9(p):
	"postfix_expression : postfix_expression ARROW declarator_id"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	p[0] = p[3]
	if (p[1].get("is_decl", True) is False) and  (p[1].get("id_type") in ["variable"]):
		entry = SymbolTable.lookupComplete(p[1]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[1], 1)
			return
		else:
			p[1] = dict(entry)
			p[1]["is_decl"] = True
	if p[1].get("id_type") not in ["object"]:
		st.print_error(p.lineno(1), {}, 54, "*"*p[1]["star"] + p[1]["name"])
		return
	if p[1].get("star", 0) == 0:
		st.print_error(p.lineno(1), {}, 57, p[1]["name"])
	elif p[1].get("star", 0) > 1:
		st.print_error(p.lineno(1), {}, 58, p[0]["name"], "*"*p[1]["star"] + p[1]["name"])
	else:
		if p[1]["myscope"] in st.ScopeList.keys():
			entry = st.ScopeList[str(p[1]["myscope"])]["table"].lookup(p[0]["name"])
			if entry is None:
				st.print_error(p.lineno(1), {}, 55, p[0]["name"], p[1]["name"])
			else:
				if entry["access"] in ["private", "protected"]:
					st.print_error(p.lineno(1), {}, 59, " ".join([entry["id_type"]] + entry["type"] + [entry["name"]]), entry["access"])
				else:
					p[0] = dict(entry)
					p[0]["is_decl"] = True
		else:
			st.print_error(p.lineno(1), {}, 54, "*"*p[1]["star"] + p[1]["name"])
	pass

def p_postfix_expression10(p):
	"postfix_expression : postfix_expression ARROW scoped_pseudo_destructor_id"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	pass

def p_postfix_expression11(p):
	"postfix_expression : postfix_expression INC"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	p[0] = p[1]
	if p[0].get("is_decl", False) is False:
		entry = SymbolTable.lookupComplete(p[0]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[0], 1)
			return
		else:
			p[0] = dict(entry)
			p[0]["is_decl"] = True

	if (not set(p[0]["type"]).issubset(st.number_types)) or (p[0].get("id_type") not in ["variable", "array"]):		# Incomplete list
		st.print_error(p.lineno(1), p[0], 13)
		return

	p[0]["inc"] = True
	pass

def p_postfix_expression12(p):
	"postfix_expression : postfix_expression DEC"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	p[0] = p[1]
	if p[0].get("is_decl", False) is False:
		entry = SymbolTable.lookupComplete(p[0]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[0], 1)
			return
		else:
			p[0] = dict(entry)
			p[0]["is_decl"] = True

	if (not set(p[0]["type"]).issubset(st.number_types)) or (p[0].get("id_type") not in ["variable", "array"]):		# Incomplete list
		st.print_error(p.lineno(1), p[0], 13)
		return

	p[0]["dec"] = True
	pass

def p_postfix_expression13(p):
	"postfix_expression : DYNAMIC_CAST '<' type_id '>' '('  expression ')' "
	add_children(len(list(filter(None, p[1:]))) - 5,p[1])
	pass

def p_postfix_expression14(p):
	"postfix_expression : STATIC_CAST '<' type_id '>' '('  expression ')'  "
	add_children(len(list(filter(None, p[1:]))) -5,p[1])
	pass

def p_postfix_expression15(p):
	"postfix_expression : REINTERPRET_CAST '<' type_id '>' '('  expression ')' "
	add_children(len(list(filter(None, p[1:]))) -5 ,p[1])
	pass

def p_postfix_expression16(p):
	"postfix_expression : CONST_CAST '<' type_id '>' '('  expression ')' "
	add_children(len(list(filter(None, p[1:]))) - 5,p[1])
	pass

def p_postfix_expression17(p):
	"postfix_expression : TYPEID parameters_clause"
	add_children(len(list(filter(None, p[1:]))) - 1,p[1])
	pass

def p_expression_list_opt1(p):
	"expression_list_opt : empty"
	pass

def p_expression_list_opt2(p):
	"expression_list_opt : expression_list"
	add_children(len(list(filter(None, p[1:]))),"expression_list_opt")
	p[0] = p[1]
	pass

def p_expression_list1(p):
	"expression_list : assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"expression_list")
	if p[1].get("is_decl", True) is False:
		entry = SymbolTable.lookupComplete(p[1]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[1], 1)
			p[0] = []
			return
		else:
			p[1] = dict(entry)
			p[1]["is_decl"] = True
	if p[1]["id_type"] not in ["variable", "literal",]:
		st.print_error(p.lineno(1), {}, 15, p[1]["name"])
		p[0] = []
		return
	p[0] = [p[1]]		# list of expressions
	pass

def p_expression_list2(p):
	"expression_list : expression_list ',' assignment_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,"expression_list")
	if p[3].get("is_decl", True) is False:
		entry = SymbolTable.lookupComplete(p[3]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[3], 1)
			p[0] = p[1]
			return
		else:
			p[3] = dict(entry)
			p[3]["is_decl"] = True
	if p[3]["id_type"] not in ["variable", "literal",]:
		st.print_error(p.lineno(1), {}, 15, p[3]["name"])
		p[0] = p[1]
		return
	p[0] = p[1] + [p[3]]
	pass

def p_unary_expression1(p):
	"unary_expression : postfix_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[1]
	pass

def p_unary_expression2(p):
	"unary_expression : INC cast_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[2]

	if p[0].get("is_decl", False) is False:
		entry = SymbolTable.lookupComplete(p[0]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[0], 1)
			return
		else:
			p[0] = dict(entry)
			p[0]["is_decl"] = True

	if (not set(p[0]["type"]).issubset(st.number_types)) or (p[0].get("id_type") not in ["variable", "array"]):		# Incomplete list
		st.print_error(p.lineno(1), p[0], 13)
		return

	st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[1], '')
	pass

def p_unary_expression3(p):
	"unary_expression : DEC cast_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[2]
	if p[0].get("is_decl", False) is False:
		entry = SymbolTable.lookupComplete(p[0]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[0], 1)
			return
		else:
			p[0] = dict(entry)
			p[0]["is_decl"] = True

	if (not set(p[0]["type"]).issubset(st.number_types)) or (p[0].get("id_type") not in ["variable", "array"]):		# Incomplete list
		st.print_error(p.lineno(1), p[0], 13)
		return
	st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[1], '')
	pass

def p_unary_expression4(p):
	"unary_expression : ptr_operator cast_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[2]
	if ("is_decl" not in p[0].keys()) or ("id_type" not in p[0].keys()):
		st.print_error(p.lineno(1), p[2], 14, p[1])
	if (p[0].get("type") is None) and (p[0].get("is_decl") is False):
		entry = SymbolTable.lookupComplete(p[0]["name"])
		if entry:
			p[0] = dict(entry)
			p[0]["is_decl"] = True
	if p[0]["is_decl"] is True:
		if p[0]["id_type"] not in ["variable", "array", "function", "object"]:	# Then it is not pointer type
			st.print_error(p.lineno(1), p[2], 14, p[1])
		else:
			if p[1] == '*':
				if p[0]["star"] == 0:
					st.print_error(p.lineno(1), p[2], 14, p[1])
				else:
					p[0]["star"] -= 1
					p[0]["tac_name"] = "*" + p[0]["tac_name"]
			elif p[1] == '&':
				p[0]["star"] += 1
				p[0]["tac_name"] = "&" + p[0]["tac_name"]
	elif p[0]["is_decl"] is False:
		if p[1] == '&':
			st.print_error(p.lineno(1), p[2], 14, p[1])
		else:
			p[0]["star"] += 1
	else:
		st.print_error(p.lineno(1), p[2], 14, p[1])
	pass

def p_unary_expression5(p):
	"unary_expression : suffix_decl_specified_scope star_ptr_operator cast_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	pass

def p_unary_expression6(p):
	"unary_expression : '+' cast_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[2]
	if (not set(p[0].get("type")).issubset(st.number_literals)) and ((p[0].get("id_type") != "variable") or ( not set(p[0].get("type")).issubset(st.number_types))):
		st.print_error(p.lineno(1), {}, 14, '-')
	st.ScopeList[st.currentScope]["tac"].expression_emit(p[2]["tac_name"],'',p[1]*3, '')
	p[0]["tac_name"] = p[2]["tac_name"]
	pass

def p_unary_expression7(p):
	"unary_expression : '-' cast_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[2]
	if (not set(p[0].get("type")).issubset(st.number_literals)) and ((p[0].get("id_type") != "variable") or ( not set(p[0].get("type")).issubset(st.number_types))):
		st.print_error(p.lineno(1), {}, 14, '-')
	elif p[0].get("value"):
		p[0]["value"] = -p[0]["value"]
		st.ScopeList[st.currentScope]["tac"].expression_emit(p[2]["tac_name"],'',p[1]*3, '')
		p[0]["tac_name"] = p[2]["tac_name"]
	pass

def p_unary_expression8(p):
	"unary_expression : '!' cast_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[2]
	st.ScopeList[st.currentScope]["tac"].expression_emit(p[2]["tac_name"],'',p[1], '')
	p[0]["truelist"] = p[2]["falselist"]
	p[0]["falselist"] = p[2]["truelist"]
	pass

def p_unary_expression9(p):
	"unary_expression : '~' cast_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[2]
	st.ScopeList[st.currentScope]["tac"].expression_emit(p[2]["tac_name"],'',p[1], '')
	pass

def p_unary_expression10(p):
	"unary_expression : SIZEOF unary_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[2]
	pass

def p_unary_expression11(p):
	"unary_expression : new_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[1]
	pass

def p_unary_expression12(p):
	"unary_expression : global_scope new_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[2]			# Don't know when this rule is called
	pass

def p_unary_expression13(p):
	"unary_expression : delete_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[1]
	pass

def p_unary_expression14(p):
	"unary_expression : global_scope delete_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	p[0] = p[2]			# Don't know when this rule is called
	pass


def p_delete_expression(p):
	"delete_expression : DELETE cast_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,"delete")
	p[0] = p[2]
	pass

def p_new_expression1(p):
	"new_expression : NEW new_type_id new_initializer_opt"
	add_children(len(list(filter(None, p[1:]))) - 1,"NEW")
	pass

def p_new_expression2(p):
	"new_expression : NEW parameters_clause new_type_id new_initializer_opt"
	add_children(len(list(filter(None, p[1:]))) -1,"NEW")
	pass

def p_new_expression3(p):
	"new_expression : NEW parameters_clause"
	add_children(len(list(filter(None, p[1:]))) - 1,"NEW")
	pass

def p_new_expression4(p):
	"new_expression : NEW parameters_clause parameters_clause new_initializer_opt"
	add_children(len(list(filter(None, p[1:]))) - 1,"NEW")
	pass

def p_new_type_id1(p):
	"new_type_id : type_specifier ptr_operator_seq_opt"
	add_children(len(list(filter(None, p[1:]))),"new_type_id")
	pass

def p_new_type_id2(p):
	"new_type_id : type_specifier new_declarator"
	add_children(len(list(filter(None, p[1:]))),"new_type_id")
	pass

def p_new_type_id3(p):
	"new_type_id : type_specifier new_type_id"
	add_children(len(list(filter(None, p[1:]))),"new_type_id")
	pass

def p_new_declarator1(p):
	"new_declarator : ptr_operator new_declarator"
	add_children(len(list(filter(None, p[1:]))),"new_declarator")
	pass

def p_new_declarator2(p):
	"new_declarator : direct_new_declarator"
	add_children(len(list(filter(None, p[1:]))),"new_declarator")
	pass

def p_direct_new_declarator1(p):
	"direct_new_declarator : '[' expression ']'"
	create_child("None",p[1])
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"direct_new_declarator")
	pass

def p_direct_new_declarator2(p):
	"direct_new_declarator : direct_new_declarator '[' constant_expression ']'"
	add_children(len(list(filter(None, p[1:]))),"direct_new_declarator")
	pass

def p_new_initializer_opt1(p):
	"new_initializer_opt : empty"
	pass

def p_new_initializer_opt2(p):
	"new_initializer_opt : '(' expression_list_opt ')' "
	add_children(len(list(filter(None, p[1:]))),"new_initializer_opt")
	pass

#/*  cast-expression is generalised to support a [] as well as a () prefix. This covers the omission of DELETE[] which when
# *  followed by a parenthesised expression was ambiguous. It also covers the gcc indexed array initialisation for free.
# */

def p_cast_expression1(p):
	"cast_expression : unary_expression"
	add_children(len(list(filter(None, p[1:]))),"cast_expression")
	p[0] = p[1]
	pass

def p_cast_expression2(p):
	"cast_expression : abstract_expression cast_expression"
	add_children(len(list(filter(None, p[1:]))),"cast_expression")
	pass

def p_pm_expression1(p):
	"pm_expression : cast_expression"
	add_children(len(list(filter(None, p[1:]))),"pm_expression")
	p[0] = p[1]
	pass

def p_pm_expression2(p):
	"pm_expression : pm_expression DOT_STAR cast_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = p[3]					# Taking pointed expression into account
	pass

def p_pm_expression3(p):
	"pm_expression : pm_expression ARROW_STAR cast_expression"
	add_children(len(list(filter(None, p[1:]))) -1 ,p[2])
	pass

def p_multiplicative_expression1(p):
	"multiplicative_expression : pm_expression"
	add_children(len(list(filter(None, p[1:]))),"multiplicative_expression")
	p[0] = p[1]
	pass

def p_multiplicative_expression2(p):
	"multiplicative_expression : multiplicative_expression star_ptr_operator pm_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	if p[1].get("id_type") in ["type_specifier", "class", "struct", "union"]:		# pointer type variable declaration
		p[0] = p[3]
		if "is_decl" not in p[0].keys():
			st.print_error(p.lineno(1), {}, 15, ' '.join([p[1]["name"], p[2], p[3]["name"]]))
			return
		if p[0]["is_decl"]:			# Identifier is already declared in the currentScope
			st.print_error(p.lineno(1), p[0], 4, p[1]["type"])
			return
		p[0]["star"] += 1
		p[0]["type"] = p[1]["type"]
		p[0]["specifier"] = p[1]["specifier"]
		if p[1]["id_type"] in ["class", "struct", "union"]:
			p[0]["id_type"] = "object"
			p[0]["myscope"] = p[1]["name"]

	else:											# normal multiplication
		if p[1].get("is_decl", True) is False:
			p[0] = p[3]
			key = "____" + str(p[1]["name"]) + "____"
			if key in st.ScopeList.keys():
				entry = SymbolTable.lookupComplete(key)
				if entry:
					if p[0]["is_decl"]:
						st.print_error(p.lineno(1), p[2], 4, p[1]["type"])	# error: conflicting declaration 'p[1] p[2]["name"]' / error:  redeclaration of 'p[2]["name"]'
					else:
						p[0]["star"] += 1
						p[0]["id_type"] = "object"
						p[0]["type"] = p[1]["type"]
						p[0]["specifier"] = p[1]["specifier"]
						p[0]["myscope"] = key
					return
		p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	pass

def p_multiplicative_expression3(p):
	"multiplicative_expression : multiplicative_expression '/' pm_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 ,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	pass

def p_multiplicative_expression4(p):
	"multiplicative_expression : multiplicative_expression '%' pm_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	pass

def p_additive_expression1(p):
	"additive_expression : multiplicative_expression"
	add_children(len(list(filter(None, p[1:]))),"additive_expression")
	p[0] = p[1]
	pass

def p_additive_expression2(p):
	"additive_expression : additive_expression '+' multiplicative_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 ,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	pass

def p_additive_expression3(p):
	"additive_expression : additive_expression '-' multiplicative_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 ,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	pass

def p_shift_expression1(p):
	"shift_expression : additive_expression"
	add_children(len(list(filter(None, p[1:]))),"shift_expression")
	p[0] = p[1]
	pass

def p_shift_expression2(p):
	"shift_expression : shift_expression SHL additive_expression"
	add_children(len(list(filter(None, p[1:]))) -1 ,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	pass

def p_shift_expression3(p):
	"shift_expression : shift_expression SHR additive_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	pass

def p_relational_expression1(p):
	"relational_expression : shift_expression"
	add_children(len(list(filter(None, p[1:]))),"relational_expression")
	p[0] = p[1]
	pass

def p_relational_expression2(p):
	"relational_expression : relational_expression '<' shift_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 ,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	p[0]["truelist"] = [st.ScopeList[st.currentScope]["tac"].getnext() -2 ]
	p[0]["falselist"] = [st.ScopeList[st.currentScope]["tac"].getnext() - 1]
	pass

def p_relational_expression3(p):
	"relational_expression : relational_expression '>' shift_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 ,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	p[0]["truelist"] = [st.ScopeList[st.currentScope]["tac"].getnext() -2]
	p[0]["falselist"] = [st.ScopeList[st.currentScope]["tac"].getnext()-1]
	pass

def p_relational_expression4(p):
	"relational_expression : relational_expression LE shift_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	p[0]["truelist"] = [st.ScopeList[st.currentScope]["tac"].getnext() - 2]
	p[0]["falselist"] = [st.ScopeList[st.currentScope]["tac"].getnext() - 1]
	pass

def p_relational_expression5(p):
	"relational_expression : relational_expression GE shift_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	p[0]["truelist"] = [st.ScopeList[st.currentScope]["tac"].getnext() - 2 ]
	p[0]["falselist"] = [st.ScopeList[st.currentScope]["tac"].getnext() - 1]
	pass

def p_equality_expression1(p):
	"equality_expression : relational_expression"
	add_children(len(list(filter(None, p[1:]))),"equality_expression")
	p[0] = p[1]
	pass

def p_equality_expression2(p):
	"equality_expression : equality_expression EQ relational_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	p[0]["truelist"] = [st.ScopeList[st.currentScope]["tac"].getnext() - 2]
	p[0]["falselist"] = [st.ScopeList[st.currentScope]["tac"].getnext() - 1]
	pass

def p_equality_expression3(p):
	"equality_expression : equality_expression NE relational_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 , p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	p[0]["truelist"] = [st.ScopeList[st.currentScope]["tac"].getnext() - 2]
	p[0]["falselist"] = [st.ScopeList[st.currentScope]["tac"].getnext() - 1]
	pass

def p_and_expression1(p):
	"and_expression : equality_expression"
	add_children(len(list(filter(None, p[1:]))),"and_expression")
	p[0] = p[1]
	pass

def p_and_expression2(p):
	"and_expression : and_expression '&' equality_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	pass

def p_exclusive_or_expression1(p):
	"exclusive_or_expression : and_expression"
	add_children(len(list(filter(None, p[1:]))),"exclusive_or_expression")
	p[0] = p[1]
	pass

def p_exclusive_or_expression2(p):
	"exclusive_or_expression : exclusive_or_expression '^' and_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	pass

def p_inclusive_or_expression1(p):
	"inclusive_or_expression : exclusive_or_expression"
	add_children(len(list(filter(None, p[1:]))),"inclusive_or_expression")
	p[0] = p[1]
	pass

def p_inclusive_or_expression2(p):
	"inclusive_or_expression : inclusive_or_expression '|' exclusive_or_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[3])
	pass

def p_logical_and_expression1(p):
	"logical_and_expression : inclusive_or_expression"
	add_children(len(list(filter(None, p[1:]))),"logical_and_expression")
	p[0] = p[1]
	pass

def p_logical_and_expression2(p):
	"logical_and_expression : logical_and_expression LOG_AND marker_M inclusive_or_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[4])
	st.ScopeList[st.currentScope]["tac"].backpatch(p[1]["truelist"], p[3]["quad"]  )
	p[0]["falselist"] = list(set(p[1]["falselist"] + p[4]["falselist"]))
	p[0]["truelist"] = p[4]["truelist"]
	pass

def p_logical_or_expression1(p):
	"logical_or_expression : logical_and_expression"
	add_children(len(list(filter(None, p[1:]))),"logical_or_expression")
	p[0] = p[1]
	pass

def p_logical_or_expression2(p):
	"logical_or_expression : logical_or_expression LOG_OR marker_M logical_and_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = expression_semantic(p.lineno(1), p[0], p[1], p[2], p[4])
	st.ScopeList[st.currentScope]["tac"].backpatch(p[1]["falselist"], p[3]["quad"] )
	p[0]["truelist"] = list(set(p[1]["truelist"] + p[4]["truelist"]))
	p[0]["falselist"] = p[4]["falselist"]
	pass

def p_conditional_expression1(p):
	"conditional_expression : logical_or_expression"
	add_children(len(list(filter(None, p[1:]))),"conditional_expression")
	p[0] = p[1]
	pass

def p_conditional_expression2(p):
	"conditional_expression : logical_or_expression '?' expression ':' assignment_expression"
	add_children(len(list(filter(None, p[1:]))) - 2,"Ternary - If then else")
	pass

#/*  assignment-expression is generalised to cover the simple assignment of a braced initializer in order to contribute to the
# *  coverage of parameter-declaration and init-declaration.
# */

def p_assignment_expression1(p):
	"assignment_expression : conditional_expression"
	add_children(len(list(filter(None, p[1:]))),"assignment_expression")
	p[0] = p[1]
	if p[0]["id_type"] == "function" and p[0]["is_defined"] is False:
		st.function_list.append(p[0])
	pass

def p_assignment_expression2(p):
	"assignment_expression : logical_or_expression assignment_operator assignment_expression"
	add_children(len(list(filter(None, p[1:]))) -1 ,p[2])
	if p[1].get("type", 1) is None:
		entry = SymbolTable.lookupComplete(p[1]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[1], 1)
			return
		else:
			p[1] = dict(entry)
			p[1]["is_decl"] = True
	p[0] = p[1]
	if (p[1].get("id_type") not in ["variable", "array"]) or (p[1].get("real_id_type") in ["function", "class"]):
		st.print_error(p.lineno(1), p[1], 17)
		return

	if p[0].get("is_decl", False) is False:
		p[0]["tac_name"] = p[0]["name"] + "_" + str(st.currentScope)

	if p[2] == '=':			# simple assignment
		if p[3].get("is_decl", True) is False:	# When only a variable is present in RHS
			entry = SymbolTable.lookupComplete(p[3]["name"])
			if entry is None:
				st.print_error(p.lineno(1), p[3], 1)
				return
			else:
				p[3] = dict(entry)
				p[3]["is_decl"] = True
				if p[3].get("real_id_type") in ["function", "class"] and p[3]["tac_name"] == p[3]["name"] + "_" + p[3]["myscope"]:
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],"pop")
				else:
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],p[3]["tac_name"])
					p[0]["tac_name"] = p[3]["tac_name"]

				if p[3].get("inc",False):
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"++", '')
				if p[3].get("dec",False):
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"--", '')
		if p[3].get("id_type") not in ["variable", "literal", "array"]:
			st.print_error(p.lineno(1), {}, 15, ' '.join([p[1]["name"], p[2], p[3]["name"]]))
			return
		if p[1]["id_type"] != p[3]["id_type"]:
			if (p[1]["id_type"] in ["array"]) and (set(p[1]["type"]).issubset(st.char_types)) and (' '.join(p[3]["type"]) in ["literal_string"]):
				if len(p[1]["order"]) > 1:
					st.print_error(p.lineno(1), {}, 60)
					return
				elif p[1]["num"] <= len(p[3]["value"]):
					st.print_error(p.lineno(1), {}, 61)
					return
				else:
					p[0]["value"] = p[3]["value"] + "\0"
			elif (p[1]["id_type"] == "variable") and (p[3]["id_type"] == "literal"):
				if p[1]["type"]:
					if (' '.join(p[3]["type"]) in ["literal_char"]) and ((len(p[3]["value"]) > 1) or (len(p[3]["value"]) == 0)):
						st.print_error(p.lineno(1), {}, 62)
						return
					elif ' '.join(p[3]["type"]) in ["literal_string"]:
						st.print_error(p.lineno(1), {}, 63, ' '.join(p[1]["type"]))
						return
					if st.expression_type(p.lineno(1), p[1]["type"], p[1].get("star", 0) , p[3]["type"], p[3].get("star", 0), op=str(p[2])):
						p[0]["value"] = p[3]["value"]
						if p[3].get("real_id_type") in ["function", "class"] and p[3]["tac_name"] == p[3]["name"] + "_" + p[3]["myscope"]:
							st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],"pop")
						else:
							st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],p[3]["tac_name"])
							p[0]["tac_name"] = p[3]["tac_name"]
						if p[3].get("inc",False):
							st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"++", '')
						if p[3].get("dec",False):
							st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"--", '')
			else:
				st.print_error(p.lineno(1), {}, 18, p[1]["id_type"], p[3]["id_type"])
		elif p[1]["id_type"] == p[3]["id_type"]:
			if p[1]["type"]:
				if st.expression_type(p.lineno(1), p[1]["type"], p[1].get("star", 0) , p[3]["type"], p[3].get("star", 0), op=str(p[2])):
					p[0]["value"] = p[3]["value"]
					if p[3].get("real_id_type") in ["function", "class"] and p[3]["tac_name"] == p[3]["name"] + "_" + p[3]["myscope"]:
						st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],"pop")
					else:
						st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],p[3]["tac_name"])
						p[0]["tac_name"] = p[3]["tac_name"]
					if p[3].get("inc",False):
						st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"++", '')
					if p[3].get("dec",False):
						st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"--", '')
		else:
			st.print_error(p.lineno(1), {}, 15, ' '.join([p[1]["name"], p[2], p[3]["name"]]))
	else:
		if p[3].get("is_decl", True) is False:	# When only a variable is present in RHS
			entry = SymbolTable.lookupComplete(p[3]["name"])
			if entry is None:
				st.print_error(p.lineno(1), p[3], 1)
				return
			else:
				p[3] = dict(entry)
				p[3]["is_decl"] = True
				if p[3].get("real_id_type") in ["function", "class"] and p[3]["tac_name"] == p[3]["name"] + "_" + p[3]["myscope"]:
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],"pop")
				else:
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],p[3]["tac_name"])
					p[0]["tac_name"] = p[3]["tac_name"]
				if p[3].get("inc",False):
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"++", '')
				if p[3].get("dec",False):
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"--", '')
		if p[3].get("id_type") not in ["variable", "literal"]:
			st.print_error(p.lineno(1), {}, 15, ' '.join([p[1]["name"], p[2], p[3]["name"]]))
			return
		if p[1].get("is_decl", True) is False:	# When only a variable is present in LHS
			if p[1]["type"]:
				st.print_error(p.lineno(1), {}, 15, ' '.join([p[1]["name"], p[2], p[3]["name"]]))
				return
			entry = SymbolTable.lookupComplete(p[1]["name"])
			if entry is None:
				st.print_error(p.lineno(1), p[1], 1)
				return
			else:
				p[0] = dict(entry)
				p[0]["is_decl"] = True
				if p[3].get("real_id_type") in ["function", "class"] and p[3]["tac_name"] == p[3]["name"] + "_" + p[3]["myscope"]:
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],"pop")
				else:
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],p[3]["tac_name"])
					p[0]["tac_name"] = p[3]["tac_name"]
				if p[3].get("inc",False):
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"++", '')
				if p[3].get("dec",False):
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"--", '')
		if (p[0].get("id_type") not in ["variable", "array"]) or (p[0].get("real_id_type") in ["function", "class"]):
			st.print_error(p.lineno(1), p[0], 17)
			return
		if st.expression_type(p.lineno(1), p[0]["type"], p[0].get("star", 0) , p[3]["type"], p[3].get("star", 0), op=str(p[2])):
			if "const" in p[0]["specifier"]:
				st.print_error(p.lineno(1), p[0], 19)
			else:
				if p[3].get("real_id_type") in ["function", "class"] and p[3]["tac_name"] == p[3]["name"] + "_" + p[3]["myscope"]:
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],"pop")
				else:
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[0]["tac_name"],'',p[2],p[3]["tac_name"])
					p[0]["tac_name"] = p[3]["tac_name"]
				if p[3].get("inc",False):
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"++", '')
				if p[3].get("dec",False):
					st.ScopeList[st.currentScope]["tac"].expression_emit(p[3]["tac_name"],'',"--", '')
	pass

def p_assignment_expression3(p):
	"assignment_expression : logical_or_expression '=' braced_initializer"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	p[0] = p[1]
	inits = p[3]["inits"]
	if (p[1].get("id_type") in ["variable"]) and (p[1].get("is_decl") is False) and p[1].get("type"):
		if p[3]["dim"] > 1:
			st.print_error(p.lineno(1), {}, 22, p[1]["type"])
		elif len(inits) == 0:
			st.print_error(p.lineno(1), {}, 20)
		elif len(inits) > 1:
			st.print_error(p.lineno(1), {}, 21, p[1]["name"])
		else:
			if inits[0]["id_type"] in ["literal", "variable"]:
				if st.expression_type(p.lineno(1), p[1]["type"], p[1].get("star", 0) , inits[0]["type"], inits[0].get("star", 0), op=str(p[2])):
					p[0]["value"] = inits[0]["value"]
			else:
				st.print_error(p.lineno(1), {}, 15, ' '.join([p[1]["name"], p[2], inits[0]["name"]]))
	elif (p[1].get("id_type") in ["array"]) and (p[1].get("is_decl") is False) and p[1].get("type"):
		if p[3]["dim"] > len(p[1]["order"]):
			st.print_error(p.lineno(1), {}, 22, p[1]["type"])
		else:
			p[0]["value"] = [0]*p[0]["num"]
			p[0]["value"] = array_assignment(p,inits,p[0]["value"])
			size = st.simple_type_specifier[" ".join(p[0]["type"])]["size"]
			for i in range(0,p[0]["num"]):
				st.ScopeList[st.currentScope]["tac"].expression_emit("*(" +p[0]["name"] + "_" + str(p[0]["myscope"])+ "+" +str(i*size) + ")",'',p[2],str(p[0]["value"][i]))

	else:
		st.print_error(p.lineno(1), p[1], 24)
	pass

def p_assignment_expression4(p):
	"assignment_expression : throw_expression"
	add_children(len(list(filter(None, p[1:]))),"assignment_expression")
	p[0] = p[1]
	pass

def p_assignment_operator(p):
	'''assignment_operator : '='
						   | ASS_ADD
						   | ASS_AND
						   | ASS_DIV
						   | ASS_MOD
						   | ASS_MUL
						   | ASS_OR
						   | ASS_SHL
						   | ASS_SHR
						   | ASS_SUB
						   | ASS_XOR'''

	p[0] = p[1]
	pass

#/*  expression is widely used and usually single-element, so the reductions are arranged so that a
# *  single-element expression is returned as is. Multi-element expressions are parsed as a list that
# *  may then behave polymorphically as an element or be compacted to an element. */

def p_expression_opt1(p):
	"expression_opt : empty"
	pass

def p_expression_opt2(p):
	"expression_opt : expression"
	add_children(len(list(filter(None, p[1:]))),"expression_opt")
	#print("E_opt",p[1])
	p[0] = p[1]
	pass

def p_expression1(p):
	"expression : assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"expression")
	p[0] = p[1]
	if p[0].get("is_decl", True) is False:		# variable not declared
		entry = SymbolTable.lookupComplete(p[0]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[0], 1)
			p[0] = None
			return
		else:
			p[0] = dict(entry)
			p[0]["is_decl"] = True
	if p[0]["id_type"] not in ["variable", "literal",]:
		st.print_error(p.lineno(1), {}, 15, p[0]["name"])
		p[0] = None
		return
	pass

def p_expression2(p):
	"expression : expression_list ',' assignment_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,"expression")
	if p[3].get("is_decl", True) is False:
		entry = SymbolTable.lookupComplete(p[3]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[3], 1)
			p[0] = p[1]
			return
		else:
			p[3] = dict(entry)
			p[3]["is_decl"] = True
	if p[3]["id_type"] not in ["variable", "literal",]:
		st.print_error(p.lineno(1), {}, 15, p[3]["name"])
		p[0] = p[1]
		return
	p[0] = p[1] + [p[3]]			# this "expression" will be list of expressions which are separated by comma
	pass

def p_constant_expression(p):
	"constant_expression : conditional_expression"
	add_children(len(list(filter(None, p[1:]))),"constant_expression")
	p[0] = p[1]
	pass

#/*  The grammar is repeated for when the parser stack knows that the next > must end a template.
# */

#/*---------------------------------------------------------------------------------------------------
# * A.5 Statements
# *---------------------------------------------------------------------------------------------------
# *  Parsing statements is easy once simple_declaration has been generalised to cover expression_statement.
# */

def p_looping_statement(p):
	"looping_statement : start_search looped_statement "
	add_children(len(list(filter(None, p[1:]))),"looping_statement")
	p[0] = p[2]
	pass

def p_looped_statement1(p):
	"looped_statement : statement"
	add_children(len(list(filter(None, p[1:]))),"looped_statement")
	p[0] = p[1]
	pass

def p_looped_statement2(p):
	"looped_statement : advance_search '+' looped_statement"
	create_children("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"looped_statement")
	p[0] = p[3]
	pass

def p_looped_statement3(p):
	"looped_statement : advance_search '-'"
	create_children("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"looped_statement")
	pass

def p_statement1(p):
	"statement : control_statement"
	add_children(len(list(filter(None, p[1:]))),"statement")
	p[0] = p[1]
	pass

def p_statement2(p):
	"statement : compound_statement"
	add_children(len(list(filter(None, p[1:]))),"statement")
	p[0] = p[1]
	pass

def p_statement3(p):
	"statement : declaration_statement"
	add_children(len(list(filter(None, p[1:]))),"statement")
	p[0] = p[1]
	pass

def p_statement4(p):
	"statement : try_block"
	add_children(len(list(filter(None, p[1:]))),"statement")
	p[0] = p[1]
	pass

def p_control_statement1(p):
	"control_statement : labeled_statement"
	add_children(len(list(filter(None, p[1:]))),"control_statement")
	p[0] = p[1]
	pass

def p_control_statement2(p):
	"control_statement : selection_statement"
	add_children(len(list(filter(None, p[1:]))),"control_statement")
	p[0] = p[1]
	pass

def p_control_statement3(p):
	"control_statement : iteration_statement"
	add_children(len(list(filter(None, p[1:]))),"control_statement")
	p[0] = p[1]
	pass

def p_control_statement4(p):
	"control_statement : jump_statement"
	add_children(len(list(filter(None, p[1:]))),"control_statement")
	p[0] = p[1]
	pass

def p_labeled_statement1(p):
	"labeled_statement : identifier ':' looping_statement"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"labeled_statement")
	pass

def p_labeled_statement2(p):
	"labeled_statement : CASE constant_expression ':' looping_statement"
	create_child("None",p[1])
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"labeled_statement")
	pass

def p_labeled_statement3(p):
	"labeled_statement : DEFAULT ':' looping_statement"
	create_child("None",p[1])
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"labeled_statement")
	p[0] = p[3]
	pass

def p_compound_statement1(p):
	"compound_statement : '{' m_new_scope statement_seq_opt '}'"
	add_children(len(list(filter(None, p[1:])))- 2,"compound_statement")
	stack_space = st.ScopeList[st.currentScope]["offset"]
	SymbolTable.endScope()
	try:
		print("[PARSER] popped function : %s" % st.function_list[0]["name"])
		SymbolTable.updateIDAttr(st.function_list[-1]["name"], "offset", stack_space)
		st.function_list.pop()
	except:
		pass
	p[0] = p[3]
	pass

def p_m_new_scope(p):
	"m_new_scope :"
	st.is_namespace = False
	if len(st.function_list) > 1:
		st.print_error(p.lineno(0), {}, 27)
	elif len(st.function_list) == 1 and st.function_list[0]["is_defined"] is False:
		f = st.function_list[0]
		f["parameters"] = f["parameters"] if f["parameters"] else []
		if any([param["id_type"] not in ["variable", "array"] for param in f["parameters"]]):
			st.print_error(p.lineno(0), {}, 28, f["name"])
			f["parameters"] = []
		f["is_defined"] = True
		if f["is_decl"] is False:
			SymbolTable.insertID(p.lineno(0), f["name"], f["id_type"], types=f["type"], specifiers=f["specifier"],
								num=f["num"], value=f["value"], stars=f["star"], order=f["order"], parameters=f["parameters"],
								defined=f["is_defined"], access=st.access_specifier, scope=f["myscope"])
		else:
			SymbolTable.updateIDAttr(f["name"], "is_defined", f["is_defined"])
		SymbolTable.addScope(f["name"], "function_scope")
		st.is_parameter = True
		st.parameter_offset = 0
		for param in f["parameters"]:		# Insert parameters in new scope created for this function
			param["myscope"] = f["name"]
			SymbolTable.insertID(p.lineno(0), param["name"], param["id_type"], types=param["type"], specifiers=param["specifier"],
								num=param["num"], value=param["value"], stars=param["star"], order=param["order"],
								parameters=param["parameters"], defined=param["is_defined"], scope=param["myscope"])
		st.is_parameter = False
		st.parameter_offset = 0
	elif len(st.namespace_list) > 0 and len(st.function_list) == 0:
		if st.namespace_list[-1]["name"] in st.ScopeList.keys():
			st.previous_scope = st.currentScope
			SymbolTable.changeScope(st.namespace_list[-1]["name"])	# Scope Extension
		else:
			SymbolTable.addScope(st.namespace_list[-1]["name"], "namespace_scope")
	else:
		SymbolTable.addScope(str(st.scope_ctr), "block_scope")
		st.scope_ctr += 1
	pass

def p_compound_statement2(p):
	"compound_statement : '{' m_new_scope statement_seq_opt marker_M looping_statement '#' bang error '}'"
	create_child("None",p[6])
	add_children(len(list(filter(None, p[1:]))) - 2,"compund_statement")
	print("[PARSER] This line should not be printed")
	SymbolTable.endScope()
	p[0] = p[3] if p[3] else {}
	p[0]["stmt_list"] = p[0].get("stmt_list",[])
	if p[5]:
		if ("stmt_list" in p[5]) :
			p[0]["stmt_list"] = p[5]["stmt_list"]
		elif ("loop_statement" in p[5]) :
			p[0]["stmt_list"] = p[5]["loop_statement"]["stmt_list"]
		p[0]["contlist"] = p[0].get("contlist",[]) + p[5].get("contlist",[])
		p[0]["breaklist"] = p[0].get("breaklist",[]) + p[5].get("breaklist",[])

	pass

def p_statement_seq_opt1(p):
	"statement_seq_opt : empty"
	pass

def p_statement_seq_opt2(p):
	"statement_seq_opt : statement_seq_opt marker_M looping_statement"
	add_children(len(list(filter(None, p[1:]))),"statement_seq_opt")
	p[0] = p[1] if p[1] else {}
	p[0]["stmt_list"] = p[0].get("stmt_list",[])
	if p[3]:
		if ("stmt_list" in p[3]) :
			p[0]["stmt_list"] = p[3]["stmt_list"]
		elif ("loop_statement" in p[3]) :
			if ("stmt_list" in p[3]) :
				p[0]["stmt_list"] = p[3]["loop_statement"]["stmt_list"]
		p[0]["contlist"] = p[0].get("contlist",[]) + p[3].get("contlist",[])
		p[0]["breaklist"] = p[0].get("breaklist",[]) + p[3].get("breaklist",[])
	pass

def p_statement_seq_opt3(p):
	"statement_seq_opt : statement_seq_opt marker_M looping_statement '#' bang error ';'"
	create_child("None",p[3])
	create_child("None",p[6])
	add_children(len(list(filter(None, p[1:]))),"statement_seq_opt")
	p[0] = p[1] if p[1] else {}
	p[0]["stmt_list"] = p[0].get("stmt_list",[])
	if p[3]:
		if ("stmt_list" in p[3]) :
			p[0]["stmt_list"] = p[3]["stmt_list"]
		elif ("loop_statement" in p[3]) :
			p[0]["stmt_list"] = p[3]["loop_statement"]["stmt_list"]
		p[0]["contlist"] = p[0].get("contlist",[]) + p[3].get("contlist",[])
		p[0]["breaklist"] = p[0].get("breaklist",[]) + p[3].get("breaklist",[])
	pass

#/*
# *  The dangling else conflict is resolved to the innermost if.
# */

def p_selection_statement1(p):
	"selection_statement : IF '(' condition ')' marker_M looping_statement    %prec SHIFT_THERE"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))) -4,"Condition - If")
	p[0] = dict()
	p[0]["type"] = "if"
	p[0]["condition"] = p[3]
	p[0]["loop_statement"] = p[6]
	st.ScopeList[st.currentScope]["tac"].backpatch(p[3]["truelist"], p[5]["quad"]  )
	st.ScopeList[st.currentScope]["tac"].backpatch(p[3]["truelist"], p[5]["quad"]  )
	temp_list = list(set(p[3]["falselist"] + p[6]["breaklist"]))
	st.ScopeList[st.currentScope]["tac"].backpatch(temp_list, st.ScopeList[st.currentScope]["tac"].nextquad  )
	p[0]["breaklist"] = p[6]["breaklist"]
	p[0]["contlist"] = p[6]["contlist"]




	pass

def p_selection_statement2(p):
	"selection_statement : IF '(' condition ')' marker_M looping_statement  ELSE marker_N marker_M looping_statement"
	add_children(len(list(filter(None, p[1:]))) - 6,"Condition - If - Else")
	p[0] = dict()
	p[0]["type"] = "if_else"
	p[0]["condition"] = p[3]
	p[0]["loop_statement"] = dict((k, [p[6][k], p[10].get(k)]) for k in p[6])
	p[0]["loop_statement"].update((k, [None, p[10][k]]) for k in p[10] if k not in p[6])
	st.ScopeList[st.currentScope]["tac"].backpatch(p[3]["truelist"], p[5]["quad"]  )
	st.ScopeList[st.currentScope]["tac"].backpatch(p[3]["falselist"], p[9]["quad"]  )
	st.ScopeList[st.currentScope]["tac"].backpatch(p[8]["nextlist"], st.ScopeList[st.currentScope]["tac"].nextquad  )


	p[0]["breaklist"] = list(set(p[6]["breaklist"] + p[10]["breaklist"]))
	p[0]["contlist"] = list(set(p[6]["contlist"] + p[10]["contlist"]))

	#temp_list = list(set(p[3]["falselist"] + p[6]["breaklist"]))
	#st.ScopeList[st.currentScope]["tac"].backpatch(temp_list, st.ScopeList[st.currentScope]["tac"].nextquad  )

	pass

def p_selection_statement3(p):
	"selection_statement : SWITCH '(' condition ')' marker_M looping_statement"
	add_children(len(list(filter(None, p[1:]))),p[1])
	p[0] = dict()
	p[0]["type"] = "switch"
	p[0]["condition"] = p[3]
	p[0]["loop_statement"] = 	p[6]
	pass

def p_condition_opt1(p):
	"condition_opt : empty"
	pass

def p_condition_opt2(p):
	"condition_opt : condition"
	add_children(len(list(filter(None, p[1:]))),"condition_opt")
	p[0] = p[1]
	pass

def p_condition(p):
	"condition : parameter_declaration_list"
	add_children(len(list(filter(None, p[1:]))),"condition")
	list_params = list()
	for param in p[1]:
		if param.get("is_decl", True) is False:
			if param.get("type") or param.get("specifier"):
				st.print_error(p.lineno(1),param,37)
				continue
			entry = SymbolTable.lookupComplete(param["name"])
			if entry is None:
				st.print_error(p.lineno(1), param, 1)
				continue
			else:
				param = dict(entry)
				param["is_decl"]  = True
		if param.get("id_type") in ["variable", "array", "literal" ] :
			list_params.append(dict(param))
		else:
			st.print_error(p.lineno(1),param,37)
	if len(list_params) == 0:
		st.print_error(p.lineno(1), {}, 12, ')', "primary_expression")
		p[0] = dict(name='0', type='literal_int', id_type='literal', value=0)
	elif len(list_params) > 1:
		st.print_error(p.lineno(1),param,38)
		p[0] = dict(name='0', type='literal_int', id_type='literal', value=0)
	else:
		p[0] = dict(list_params[-1])
	pass

def p_iteration_statement1(p):
	"iteration_statement : WHILE '(' marker_M condition ')' marker_M looping_statement"
	add_children(len(list(filter(None, p[1:]))) - 3,"WHILE")
	p[0] = dict()
	p[0]["type"] = "while"
	p[0]["condition"] = p[4]
	p[0]["loop_statement"] = p[7]
	st.ScopeList[st.currentScope]["tac"].backpatch(p[7]["contlist"], p[3]["quad"]  )
	st.ScopeList[st.currentScope]["tac"].backpatch(p[4]["truelist"], p[6]["quad"]  )
	st.ScopeList[st.currentScope]["tac"].emit(["goto",str(p[3]["quad"])])
	temp_list = p[4]["falselist"] + p[7]["breaklist"]
	st.ScopeList[st.currentScope]["tac"].backpatch(temp_list, st.ScopeList[st.currentScope]["tac"].nextquad  )
	p[0]["breaklist"] = []
	p[0]["contlist"] = []

	pass

def p_iteration_statement2(p):
	"iteration_statement : DO marker_M looping_statement marker_N WHILE '(' marker_M condition ')'  ';'"
	add_children(len(list(filter(None, p[1:]))) - 5,"DO - WHILE")
	p[0] = dict()
	p[0]["type"] = "do_while"
	p[0]["condition"] = p[8]
	p[0]["loop_statement"] = p[3]
	st.ScopeList[st.currentScope]["tac"].backpatch(p[4]["nextlist"], p[7]["quad"]  )
	st.ScopeList[st.currentScope]["tac"].backpatch(p[3]["contlist"], p[7]["quad"]  )
	st.ScopeList[st.currentScope]["tac"].backpatch(p[8]["truelist"], p[2]["quad"]  )
	temp_list = p[8]["falselist"] + p[3]["breaklist"]
	st.ScopeList[st.currentScope]["tac"].backpatch(temp_list, st.ScopeList[st.currentScope]["tac"].nextquad  )
	p[0]["breaklist"] = []
	p[0]["contlist"] = []
	pass

def p_iteration_statement3(p):
	"iteration_statement : FOR '(' for_init_statement marker_M condition_opt ';' marker_M expression_opt marker_N ')' marker_M looping_statement"
	add_children(len(list(filter(None, p[1:]))) - 4,"FOR")
	p[0] = dict()
	p[0]["type"] = "for"
	p[0]["for_init"] = p[3]
	p[0]["condition"] = p[5]
	p[0]["update_expr"] = p[8]
	p[0]["loop_statement"] = p[12]
	st.ScopeList[st.currentScope]["tac"].emit(["goto",str(p[7]["quad"])])
	st.ScopeList[st.currentScope]["tac"].backpatch(p[12]["contlist"], p[7]["quad"]  )
	st.ScopeList[st.currentScope]["tac"].backpatch(p[9]["nextlist"], p[4]["quad"]  )
	st.ScopeList[st.currentScope]["tac"].backpatch(p[5]["truelist"], p[11]["quad"]  )
	temp_list = p[5]["falselist"] + p[12]["breaklist"]
	st.ScopeList[st.currentScope]["tac"].backpatch(temp_list, st.ScopeList[st.currentScope]["tac"].nextquad  )
	p[0]["breaklist"] = []
	p[0]["contlist"] = []
	pass

def p_for_init_statement(p):
	"for_init_statement : simple_declaration"
	add_children(len(list(filter(None, p[1:]))),"for_init_statement")
	p[0] = p[1]
	pass

def p_jump_statement1(p):
	"jump_statement : BREAK ';'"
	create_child("None", p[2])
	p[0] = dict()
	p[0]["breaklist"] = [st.ScopeList[st.currentScope]["tac"].getnext()]
	st.ScopeList[st.currentScope]["tac"].emit(["goto",""])
	p[0]["contlist"] = []
	pass

def p_jump_statement2(p):
	"jump_statement : CONTINUE ';'"
	create_child("None", p[2])
	p[0] = dict()
	p[0]["contlist"] = [st.ScopeList[st.currentScope]["tac"].getnext()]
	st.ScopeList[st.currentScope]["tac"].emit(["goto",""])
	p[0]["breaklist"] = []
	pass

def p_jump_statement3(p):
	"jump_statement : RETURN expression_opt ';'"
	p[0] = dict()
	if p[2] != '':
		add_children(1,"return")
	else:
		create_child("None", p[1])
	if len(st.function_list) == 0:
		#st.print_error(p.lineno(1), {}, 15, )
		return
	func = st.function_list[0]
	if p[2] is None:
		if ' '. join(func["type"]) != "void":
			st.print_error(p.lineno(1), {}, 36, func["name"], ' '. join(func["type"]))
		return
	if type(p[2]) is list:
		expr = p[2][-1]
	else:
		expr = p[2]
	if (st.simple_type_specifier[' '.join(expr["type"])]["equiv_type"] != st.simple_type_specifier[' '.join(func["type"])]["equiv_type"]) \
	 	or (expr.get("order", []) != func.get("order", [])) or (expr.get("star", 0) != func.get("star", 0)):
		st.print_error(p.lineno(1), {}, 36, func["name"], ' '. join(func["type"]))
	else:
		if expr.get("real_id_type") in ["function", "class"] and expr["tac_name"] == expr["name"] + "_" + expr["myscope"]:
			st.ScopeList[st.currentScope]["tac"].emit(["ret","pop"])
		else:
			st.ScopeList[st.currentScope]["tac"].emit(["ret",str(expr["tac_name"])])

	p[0]["stmt_list"] = [p[1:]]
	pass

def p_jump_statement4(p):
	"jump_statement : GOTO identifier ';'"
	create_child("None",p[1])
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"jump_statement")
	pass

def p_declaration_statement(p):
	"declaration_statement : block_declaration"
	add_children(len(list(filter(None, p[1:]))),"declaration_statement")
	p[0] = p[1]
	pass

#/*---------------------------------------------------------------------------------------------------
# * A.6 Declarations
# *---------------------------------------------------------------------------------------------------*/

def p_compound_declaration1(p):
	"compound_declaration : '{' m_new_scope nest declaration_seq_opt '}'"
	add_children(len(list(filter(None, p[1:]))) - 2,"compound_declaration")
	SymbolTable.endScope()
	if st.previous_scope != "":
		st.currentScope = st.previous_scope
		st.previous_scope = ""
	try:
		print("[PARSER] popped namespace : %s" % st.namespace_list[-1]["name"])
		st.namespace_list.pop()
	except:
		pass
	p[0] = p[4]
	pass

def p_compound_declaration2(p):
	"compound_declaration : '{' m_new_scope nest declaration_seq_opt util looping_declaration '#' bang error '}'"
	create_child("None",p[5])
	add_children(len(list(filter(None, p[1:]))) - 2,"compound_declaration")
	print("[PARSER] This line should not be printed")
	SymbolTable.endScope()
	pass

def p_declaration_seq_opt1(p):
	"declaration_seq_opt : empty"
	pass

def p_declaration_seq_opt2(p):
	"declaration_seq_opt : declaration_seq_opt util looping_declaration"
	add_children(len(list(filter(None, p[1:]))),"declaration_seq_opt")
	p[0] = p[1] if p[1] else {}
	if p[1]:
		p[0]["stmt_list"] += p[3]["stmt_list"]
	else:
		p[0]["stmt_list"] = p[3]["stmt_list"]
	pass

def p_declaration_seq_opt3(p):
	"declaration_seq_opt : declaration_seq_opt util looping_declaration '#' bang error ';'"
	create_child("None",p[4])
	create_child("None",p[7])
	add_children(len(list(filter(None, p[1:]))),"declaration_seq_opt")
	pass

def p_looping_declaration(p):
	"looping_declaration : start_search1 looped_declaration"
	add_children(len(list(filter(None, p[1:]))),"looping_declaration")
	p[0] = p[2]
	pass

def p_looped_declaration1(p):
	"looped_declaration : declaration"
	add_children(len(list(filter(None, p[1:]))),"looped_declaration")
	p[0] = p[1]
	pass

def p_looped_declaration2(p):
	"looped_declaration : advance_search '+' looped_declaration"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"looped_declaration")
	pass

def p_looped_declaration3(p):
	"looped_declaration : advance_search '-'"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"looped_declaration")
	pass

def p_declaration1(p):
	"declaration : block_declaration"
	add_children(len(list(filter(None, p[1:]))),"declaration")
	p[0] = p[1]
	pass

def p_declaration2(p):
	"declaration : function_definition"
	add_children(len(list(filter(None, p[1:]))),"declaration")
	p[0] = p[1]
	pass

def p_declaration5(p):
	"declaration : specialised_declaration"
	add_children(len(list(filter(None, p[1:]))),"declaration")
	p[0] = p[1]
	pass

def p_specialised_declaration1(p):
	"specialised_declaration : linkage_specification"
	add_children(len(list(filter(None, p[1:]))),"specialised_declaration")
	p[0] = p[1]
	pass

def p_specialised_declaration2(p):
	"specialised_declaration : namespace_definition"
	add_children(len(list(filter(None, p[1:]))),"specialised_declaration")
	p[0] = p[1]
	pass


def p_block_declaration1(p):
	"block_declaration : simple_declaration"
	add_children(len(list(filter(None, p[1:]))),"block_declaration")
	p[0] = p[1]
	pass

def p_block_declaration2(p):
	"block_declaration : specialised_block_declaration"
	add_children(len(list(filter(None, p[1:]))),"block_declaration")
	p[0] = p[1]
	pass

def p_specialised_block_declaration1(p):
	"specialised_block_declaration : asm_definition"
	add_children(len(list(filter(None, p[1:]))),"specialised_block_declaration")
	p[0] = p[1]
	pass

def p_specialised_block_declaration2(p):
	"specialised_block_declaration : namespace_alias_definition"
	add_children(len(list(filter(None, p[1:]))),"specialised_block_declaration")
	p[0] = p[1]
	pass

def p_specialised_block_declaration3(p):
	"specialised_block_declaration : using_declaration"
	add_children(len(list(filter(None, p[1:]))),"specialised_block_declaration")
	p[0] = p[1]
	pass

def p_specialised_block_declaration4(p):
	"specialised_block_declaration : using_directive"
	add_children(len(list(filter(None, p[1:]))),"specialised_block_declaration")
	p[0] = p[1]
	pass

def p_simple_declaration1(p):
	"simple_declaration : ';'"
	p[0] = dict()
	p[0]["contlist"] = []
	p[0]["truelist"] = []
	p[0]["falselist"] = []
	p[0]["breaklist"] = []
	pass

def p_simple_declaration2(p):
	"simple_declaration : init_declaration ';'"
	add_children(len(list(filter(None, p[1:]))) -1,"simple_declaration")
	p[0] = dict()
	p[0]["contlist"] = []
	p[0]["truelist"] = []
	p[0]["falselist"] = []
	p[0]["breaklist"] = []


	if p[1]:
		if "is_decl" not in p[1].keys():	# i.e. built_in_type_specifier ; (Illegal statement)
			if p[1]["id_type"] in ["type_specifier",]:
				st.print_error(p.lineno(1), p[1], 2)	# error: declaration does not declare anything
		else:
			if p[1]["is_decl"]:
				if p[1]["id_type"] == "function" and p[1]["is_defined"] is False and p[1]["is_decl"] is True:
					st.print_error(p.lineno(1), {}, 29, p[1]["name"]) # function redeclaration
					st.function_list.pop()
			elif (p[1]["id_type"] in ["object"]) or (p[1]["type"] is not None):
				if p[1]["id_type"] in ["function"]:
					st.function_list.pop()
				SymbolTable.insertID(p.lineno(1), p[1]["name"], p[1]["id_type"], types=p[1]["type"], specifiers=p[1]["specifier"],
				 					num=p[1]["num"], value=p[1]["value"], stars=p[1]["star"], order=p[1]["order"],
									parameters=p[1]["parameters"], defined=p[1]["is_defined"], scope=p[1]["myscope"])
			elif SymbolTable.lookupComplete(p[1]["name"]) is None:
				st.print_error(p.lineno(1), p[1], 1)
				if p[1]["id_type"] in ["function"]:
					st.function_list.pop()
				pass
			else:
				pass
			p[0]["stmt_list"] = [p[1]]
	pass

def p_simple_declaration3(p):
	"simple_declaration : init_declarations ';'"
	add_children(len(list(filter(None, p[1:]))) - 1,"simple_declaration")
	p[0] = dict()
	p[0]["contlist"] = []
	p[0]["truelist"] = []
	p[0]["falselist"] = []
	p[0]["stmt_list"] = []
	if p[1]:
		for decl in p[1]:
			if "is_decl" not in decl.keys():
				if decl["id_type"] in ["type_specifier",]:
					st.print_error(p.lineno(1), decl, 2)
			else:
				if decl["is_decl"]:
					if decl["id_type"] == "function" and decl["is_defined"] is False and decl["is_decl"] is True:
						st.print_error(p.lineno(1), {}, 29, decl["name"])	# function redeclaration
				elif (decl["id_type"] in ["object"]) or (decl["type"] is not None):
					SymbolTable.insertID(p.lineno(1), decl["name"], decl["id_type"], types=decl["type"], specifiers=decl["specifier"],
					 					num=decl["num"], value=decl["value"], stars=decl["star"], order=decl["order"],
										parameters=decl["parameters"], defined=decl["is_defined"], scope=decl["myscope"])
				elif SymbolTable.lookupComplete(decl["name"]) is None:
					st.print_error(p.lineno(1), decl, 1)
					pass
				else:
					pass
			p[0]["stmt_list"] += [decl]
		#if not p[0]:
		#	p[0] = []
	pass

def p_simple_declaration4(p):
	"simple_declaration : decl_specifier_prefix simple_declaration"
	add_children(len(list(filter(None, p[1:]))),"simple_declaration")
	if len(p[2]) == 0:			# i.e. decl_specifier_prefix ;
		st.print_error(p.lineno(1), {}, 2)
	else:
		for decl in p[2]:
			if decl.get("is_decl") is True:		# already declared before
				st.print_error(p.lineno(1), decl, 6)
			elif decl.get("is_decl") is False:
				SymbolTable.addIDAttr(decl["name"], "specifier", [p[1]])
				if (decl["id_type"] in ["variable", "array"]) and ("const" == p[1]) and (decl["value"] is None):
					st.print_error(p.lineno(1), decl, 5)
					SymbolTable.addIDAttr(decl["name"], "value", 0)			# DEFAULT value of const variable is 0
	p[0] = p[2]
	pass

#/*  A decl-specifier following a ptr_operator provokes a shift-reduce conflict for
# *      * const name
# *  which is resolved in favour of the pointer, and implemented by providing versions
# *  of decl-specifier guaranteed not to start with a cv_qualifier.


def p_suffix_built_in_decl_specifier_raw1(p):
	"suffix_built_in_decl_specifier_raw : built_in_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"suffix_built_in_decl_specifier_raw ")
	p[0] = dict(name=str(p[1]), id_type="type_specifier", type=[p[1]], specifier=[])
	pass

def p_suffix_built_in_decl_specifier_raw2(p):
	"suffix_built_in_decl_specifier_raw : suffix_built_in_decl_specifier_raw built_in_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"suffix_built_in_decl_specifier_raw ")
	p[0] = dict(name=' '.join([p[1]["name"], str(p[2])]), id_type="type_specifier", type=p[1]["type"] + [p[2]], specifier=p[1]["specifier"])
	pass

def p_suffix_built_in_decl_specifier_raw3(p):
	"suffix_built_in_decl_specifier_raw : suffix_built_in_decl_specifier_raw decl_specifier_suffix"
	add_children(len(list(filter(None, p[1:]))),"suffix_built_in_decl_specifier_raw ")
	p[0] = dict(name=' '.join([p[1]["name"], str(p[2])]), id_type="type_specifier", type=p[1]["type"], specifier=p[1]["specifier"] + [p[2]])
	pass

def p_suffix_built_in_decl_specifier1(p):
	"suffix_built_in_decl_specifier : suffix_built_in_decl_specifier_raw"
	add_children(len(list(filter(None, p[1:]))),"suffix_built_in_decl_specifier ")
	p[0] = p[1]
	pass


def p_suffix_named_decl_specifier1(p):
	"suffix_named_decl_specifier : scoped_id"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifier")
	p[0] = p[1]
	pass

def p_suffix_named_decl_specifier2(p):
	"suffix_named_decl_specifier : elaborate_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifier")
	p[0] = p[1]
	pass

def p_suffix_named_decl_specifier3(p):
	"suffix_named_decl_specifier : suffix_named_decl_specifier decl_specifier_suffix"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifier")
	p[0] = p[1]
	p[0]["specifier"] += [p[2]]
	pass

def p_suffix_named_decl_specifier_bi1(p):
	"suffix_named_decl_specifier_bi : suffix_named_decl_specifier"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifier_bi")
	p[0] = p[1]
	pass

def p_suffix_named_decl_specifier_bi2(p):
	"suffix_named_decl_specifier_bi : suffix_named_decl_specifier suffix_built_in_decl_specifier_raw"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifier_bi")
	p[0] = p[1]
	p[0]["type"] += p[2]["type"]
	p[0]["specifier"] += p[2]["specifier"]
	pass

def p_suffix_named_decl_specifiers1(p):
	"suffix_named_decl_specifiers : suffix_named_decl_specifier_bi"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifiers")
	p[0] = p[1]
	pass

def p_suffix_named_decl_specifiers2(p):
	"suffix_named_decl_specifiers : suffix_named_decl_specifiers suffix_named_decl_specifier_bi"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifiers")
	p[0] = p[2]
	if p[1]["is_decl"] and p[1]["id_type"] in ["class", "struct", "union",]:
		if p[0]["is_decl"]:
			st.print_error(p.lineno(1), p[2], 4, p[1]["type"])	# error: conflicting declaration 'p[1] p[2]["name"]' / error:  redeclaration of 'p[2]["name"]'
		else:
			p[0]["id_type"] = "object"
			p[0]["type"] = p[1]["type"]
			p[0]["specifier"] = p[1]["specifier"]
			p[0]["myscope"] = p[1]["name"]
	else:
		key = "____" + str(p[1]["name"]) + "____"
		if key in st.ScopeList.keys():
			entry = SymbolTable.lookupComplete(key)
			if entry is None:
				if p[1]["is_decl"]:
					st.print_error(p.lineno(1), {}, 12, ";", p[1]["name"])
				else:
					st.print_error(p.lineno(1), p[1], 1)
			else:
				if p[0]["is_decl"]:
					st.print_error(p.lineno(1), p[2], 4, p[1]["type"])	# error: conflicting declaration 'p[1] p[2]["name"]' / error:  redeclaration of 'p[2]["name"]'
				else:
					p[0]["id_type"] = "object"
					p[0]["type"] = p[1]["type"]
					p[0]["specifier"] = p[1]["specifier"]
					p[0]["myscope"] = key
		else:
			if p[1]["is_decl"]:
				st.print_error(p.lineno(1), {}, 12, ";", p[1]["name"])
			else:
				st.print_error(p.lineno(1), p[1], 1)
	pass

def p_suffix_named_decl_specifiers_sf1(p):
	"suffix_named_decl_specifiers_sf : scoped_special_function_id"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifiers_sf")
	pass

def p_suffix_named_decl_specifiers_sf2(p):
	"suffix_named_decl_specifiers_sf : suffix_named_decl_specifiers"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifiers_sf")
	p[0] = p[1]
	pass

def p_suffix_named_decl_specifiers_sf3(p):
	"suffix_named_decl_specifiers_sf : suffix_named_decl_specifiers scoped_special_function_id"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifiers_sf")
	pass

def p_suffix_decl_specified_ids1(p):
	"suffix_decl_specified_ids : suffix_built_in_decl_specifier"
	add_children(len(list(filter(None, p[1:]))),"suffix_decl_specified_ids")
	p[0] = p[1]
	pass

def p_suffix_decl_specified_ids2(p):
	"suffix_decl_specified_ids : suffix_built_in_decl_specifier suffix_named_decl_specifiers_sf"
	add_children(len(list(filter(None, p[1:]))),"suffix_decl_specified_ids")
	if p[2]["is_decl"]:			# Identifier is already declared in the currentScope
		if (p[2]["id_type"] == "function") and (p[2]["is_defined"] is False):
			if set(p[1]["type"]) != set(p[2]["type"]) :
				st.print_error(p.lineno(1), p[2], 4, p[1]["type"])
			elif set(p[1]["specifier"]) != set(p[2]["specifier"]):
				st.print_error(p.lineno(1), p[2], 6)
			p[0] = p[2]
		elif st.is_func_decl is True:
			p[0] = {
				"name" : str(p[2]["name"]),
				"id_type" : "parameter",
				"is_decl" : False,
				"type" : list(p[1]["type"]),
				"specifier" : list(p[1]["specifier"]),
				"star"	: 0,
				"num"	: 1,
				"value" : None,
				"order"	: [],
				"parameters" : None,
				"is_defined" : False,	# Used For functions only
			}
		else:
			st.print_error(p.lineno(1), p[2], 4, p[1]["type"])	# error: conflicting declaration 'p[1] p[2]["name"]' / error:  redeclaration of 'p[2]["name"]'
			p[0] = p[2]				# Considering first declaration only
	else:
		p[0] = p[2]
		p[0]["type"] = p[1]["type"]		# List of data_types
		p[0]["specifier"] = p[1]["specifier"]
	pass

def p_suffix_decl_specified_ids3(p):
	"suffix_decl_specified_ids : suffix_named_decl_specifiers_sf"
	add_children(len(list(filter(None, p[1:]))),"suffix_decl_specified_ids")
	p[0] = p[1]
	pass

def p_suffix_decl_specified_scope1(p):
	"suffix_decl_specified_scope : suffix_named_decl_specifiers SCOPE"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"suffix_decl_specified_scope")
	pass

def p_suffix_decl_specified_scope2(p):
	"suffix_decl_specified_scope : suffix_built_in_decl_specifier suffix_named_decl_specifiers SCOPE"
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"suffix_decl_specified_scope")
	pass

def p_suffix_decl_specified_scope3(p):
	"suffix_decl_specified_scope : suffix_built_in_decl_specifier SCOPE"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"suffix_decl_specified_scope")
	pass

def p_decl_specifier_affix1(p):
	"decl_specifier_affix : storage_class_specifier"
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_affix")
	p[0] = p[1]
	pass

def p_decl_specifier_affix2(p):
	"decl_specifier_affix : function_specifier"
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_affix")
	p[0] = p[1]
	pass

def p_decl_specifier_affix3(p):
	"decl_specifier_affix : FRIEND"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_affix")
	p[0] = p[1]
	pass

def p_decl_specifier_affix4(p):
	"decl_specifier_affix : TYPEDEF"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_affix")
	p[0] = p[1]
	pass

def p_decl_specifier_affix5(p):
	"decl_specifier_affix : cv_qualifier"
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_affix")
	p[0] = p[1]
	pass

def p_decl_specifier_suffix(p):
	"decl_specifier_suffix : decl_specifier_affix"
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_suffix")
	p[0] = p[1]
	pass

def p_decl_specifier_prefix1(p):
	"decl_specifier_prefix : decl_specifier_affix"
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_prefix")
	p[0] = p[1]
	pass


def p_storage_class_specifier1(p):
	'''storage_class_specifier : REGISTER
							   | STATIC
							   | MUTABLE'''
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"storage_class_specifier")
	p[0] = p[1]
	pass

def p_storage_class_specifier2(p):
	"storage_class_specifier : EXTERN                  %prec SHIFT_THERE"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"storage_class_specifier")
	p[0] = p[1]
	pass

def p_storage_class_specifier3(p):
	"storage_class_specifier : AUTO"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"storage_class_specifier")
	p[0] = p[1]
	pass

def p_function_specifier1(p):
	"function_specifier : EXPLICIT"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"function_specifier")
	p[0] = p[1]
	pass

def p_function_specifier2(p):
	"function_specifier : INLINE"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"function_specifier")
	p[0] = p[1]
	pass

def p_function_specifier3(p):
	"function_specifier : VIRTUAL"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"function_specifier")
	p[0] = p[1]
	pass

def p_type_specifier1(p):
	"type_specifier : simple_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"type_specifier")
	p[0] = p[1]
	pass

def p_type_specifier2(p):
	"type_specifier : elaborate_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"type_specifier")
	p[0] = p[1]
	pass

def p_type_specifier3(p):
	"type_specifier : cv_qualifier"
	add_children(len(list(filter(None, p[1:]))),"type_specifier")
	p[0] = p[1]
	pass

def p_elaborate_type_specifier1(p):
	"elaborate_type_specifier : class_specifier"
	add_children(len(list(filter(None, p[1:]))),"elaborate_type_specifier")
	p[0] = p[1]
	pass

def p_elaborate_type_specifier2(p):
	"elaborate_type_specifier : enum_specifier"
	add_children(len(list(filter(None, p[1:]))),"elaborate_type_specifier")
	p[0] = p[1]
	pass

def p_elaborate_type_specifier3(p):
	"elaborate_type_specifier : elaborated_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"elaborate_type_specifier")
	p[0] = p[1]
	pass


def p_simple_type_specifier1(p):
	"simple_type_specifier : scoped_id"
	add_children(len(list(filter(None, p[1:]))),"simple_type_specifier")
	p[0] = p[1]
	pass

def p_simple_type_specifier2(p):
	"simple_type_specifier : built_in_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"simple_type_specifier")
	p[0] = p[1]
	pass

def p_built_in_type_specifier(p):
	'''built_in_type_specifier : CHAR
							   | WCHAR_T
							   | BOOL
							   | SHORT
							   | INT
							   | LONG
							   | SIGNED
							   | UNSIGNED
							   | FLOAT
							   | DOUBLE
							   | VOID'''
	create_child("built_in_type_specifier",p[1])
	p[0] = p[1]
	pass

def p_elaborated_type_specifier1(p):
	"elaborated_type_specifier : elaborated_class_specifier"
	add_children(len(list(filter(None, p[1:]))),"elaborated_type_specifier")
	p[0] = p[1]
	pass

def p_elaborated_type_specifier2(p):
	"elaborated_type_specifier : elaborated_enum_specifier"
	add_children(len(list(filter(None, p[1:]))),"elaborated_type_specifier")
	p[0] = p[1]
	pass

def p_elaborated_type_specifier3(p):
	"elaborated_type_specifier : TYPENAME scoped_id"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"elaborated_type_specifier")
	p[0] = p[2]		# Not using
	pass

def p_elaborated_enum_specifier(p):
	"elaborated_enum_specifier : ENUM scoped_id               %prec SHIFT_THERE"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"elaborated_enum_specifier")
	pass

def p_enum_specifier1(p):
	"enum_specifier : ENUM scoped_id enumerator_clause"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"enum_specifier")
	pass

def p_enum_specifier2(p):
	"enum_specifier : ENUM enumerator_clause"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"enum_specifier")
	pass

def p_enumerator_clause1(p):
	"enumerator_clause : '{' m_new_scope enumerator_list_ecarb"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"enumerator_clause")
	pass

def p_enumerator_clause2(p):
	"enumerator_clause : '{' m_new_scope enumerator_list enumerator_list_ecarb"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"enumerator_clause")
	pass

def p_enumerator_clause3(p):
	"enumerator_clause : '{' m_new_scope enumerator_list ',' enumerator_definition_ecarb"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))) - 1,"enumerator_clause")
	pass

def p_enumerator_list_ecarb1(p):
	"enumerator_list_ecarb : '}'"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"enumerator_list_ecarb")
	SymbolTable.endScope()
	pass

def p_enumerator_list_ecarb2(p):
	"enumerator_list_ecarb : bang error '}'"
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"enumerator_list_ecarb")
	SymbolTable.endScope()
	pass

def p_enumerator_definition_ecarb1(p):
	"enumerator_definition_ecarb : '}'"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"enumerator_definition_ecarb")
	SymbolTable.endScope()
	pass

def p_enumerator_definition_ecarb2(p):
	"enumerator_definition_ecarb : bang error '}'"
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"enumerator_definition_ecarb")
	SymbolTable.endScope()
	pass

def p_enumerator_definition_filler1(p):
	"enumerator_definition_filler : empty"
	pass

def p_enumerator_definition_filler2(p):
	"enumerator_definition_filler : bang error ','"
	add_children(len(list(filter(None, p[1:]))) -1 ,"enumerator_definiton_filler")
	pass

def p_enumerator_list_head1(p):
	"enumerator_list_head : enumerator_definition_filler"
	add_children(len(list(filter(None, p[1:]))),"enumerator_list_head")
	pass

def p_enumerator_list_head2(p):
	"enumerator_list_head : enumerator_list ',' enumerator_definition_filler"
	add_children(len(list(filter(None, p[1:]))) -1,"enumerator_list_head")
	pass

def p_enumerator_list(p):
	"enumerator_list : enumerator_list_head enumerator_definition"
	add_children(len(list(filter(None, p[1:]))),"enumerator_list")
	pass

def p_enumerator_definition1(p):
	"enumerator_definition : enumerator"
	add_children(len(list(filter(None, p[1:]))),"enumerator_definition")
	pass

def p_enumerator_definition2(p):
	"enumerator_definition : enumerator '=' constant_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 ,p[2])
	pass

def p_enumerator(p):
	"enumerator : identifier"
	add_children(len(list(filter(None, p[1:]))),"enumerator")
	pass

def p_namespace_definition1(p):
	"namespace_definition : NAMESPACE m_namespace scoped_id compound_declaration"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"namespace_definition")
	p[0] = p[4]
	if p[3].get("is_decl") and (p[3].get("id_type") not in ["namespace",]):
		st.print_error(p.lineno(2), p[3], 4, None)
		return
	if not p[3].get("is_decl"):
		SymbolTable.insertID(p.lineno(1), p[3]["name"], p[3]["id_type"], types=[], specifiers=[],
							num=p[3]["num"], value=p[3]["value"], stars=p[3]["star"], order=p[3]["order"],
							parameters=p[3]["parameters"], defined=True, access=st.access_specifier, scope=p[3]["myscope"])
	pass

def p_m_namespace(p):
	"m_namespace :"
	st.is_namespace = True
	pass

def p_namespace_definition2(p):
	"namespace_definition : NAMESPACE m_namespace compound_declaration"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"namespace_definition")
	p[0] = p[3]
	pass

def p_namespace_alias_definition(p):
	"namespace_alias_definition : NAMESPACE m_namespace scoped_id '=' scoped_id ';'"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))) - 2,p[4])
	# pop scoped_id from namespace_list, okay !
	pass

def p_using_declaration1(p):
	"using_declaration : USING declarator_id ';'"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))) - 1,"using_declaration")
	p[0] = p[2]
	if p[2].get("is_decl"):
		if p[2]["name"] in st.ScopeList[st.currentScope]["table"].symtab.keys():
			st.print_error(p.lineno(1), {}, 41, p[2]["name"])
			return
		else:
			if p[2] in ["namespace",]:
				st.print_error(p.lineno(1), {}, 42, "namespace", p[2]["name"])
				return
			SymbolTable.insertID(p.lineno(1), p[2]["name"], p[2]["id_type"], types=p[2]["type"], specifiers=p[2]["specifier"],
			 					num=p[2]["num"], value=p[2]["value"], stars=p[2]["star"], order=p[2]["order"],
								parameters=p[2]["parameters"], defined=p[2]["is_defined"], access=p[2]["access"], scope=p[2]["myscope"])
	else:
		st.print_error(p.lineno(1), p[2], 1)
	pass

def p_using_declaration2(p):
	"using_declaration : USING TYPENAME declarator_id ';'"
	create_child("None",p[1])
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))) - 1,"using_declaration")
	pass

def p_using_directive(p):
	"using_directive : USING NAMESPACE m_namespace scoped_id ';'"
	create_child("None",p[1])
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))) - 1,"using_directive")
	p[0] = p[4]
	try:
		st.namespace_list.pop()
	except:
		pass
	if not p[0].get("is_decl"):
		entry = SymbolTable.lookupComplete(p[0]["name"])
		if entry is None:
			st.print_error(p.lineno(1), p[0], 1)
			return
		else:
			p[0] = dict(entry)
			p[0]["is_decl"] = True
	if p[0]["id_type"] not in ["namespace",]:
		st.print_error(p.lineno(1), {}, 39, p[0]["name"], ";")
	else:
		st.augment_scope(p.lineno(1), st.currentScope, p[0]["name"])
	pass

def p_asm_definition(p):
	"asm_definition : ASM '(' string ')' ';'"
	#create_child("None",p[1])
	#create_child("None",p[2])
	#create_child("None",p[4])
	#create_child("None",p[5])
	if p[3] != '':
		add_children(1,"ASM")
	else:
		create_child("None", p[1])
	pass

def p_linkage_specification1(p):
	"linkage_specification : EXTERN string looping_declaration"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"linkage_specification")
	pass

def p_linkage_specification2(p):
	"linkage_specification : EXTERN string compound_declaration"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"linkage_specification")
	pass

#*---------------------------------------------------------------------------------------------------
# * A.7 Declarators
# *---------------------------------------------------------------------------------------------------*/

def p_init_declarations1(p):
	"init_declarations : assignment_expression ',' init_declaration"
	add_children(len(list(filter(None, p[1:]))) -1,"init_declarations")
	if p[1].get("inc",False):
		st.ScopeList[st.currentScope]["tac"].expression_emit(p[1]["tac_name"],'',"++", '')
	if p[1].get("dec",False):
		st.ScopeList[st.currentScope]["tac"].expression_emit(p[1]["tac_name"],'',"--", '')
	if p[3].get("is_decl"):
		st.print_error(p.lineno(1), p[3], 4, p[1]["type"])
	else:
		if p[3]["type"] is not None:
			st.print_error(p.lineno(1), {}, 3, p[3]["type"])
		p[3]["id_type"] = p[1]["id_type"]
		p[3]["myscope"] = p[1]["myscope"]
		p[3]["star"] = p[1]["star"]
		p[3]["type"] = p[1]["type"]			# Consider first type only
		p[3]["specifier"] = p[1]["specifier"]
	p[0] = [p[1], p[3]]			# List of declarations
	pass

def p_init_declarations2(p):
	"init_declarations : init_declarations ',' init_declaration"
	add_children(len(list(filter(None, p[1:]))) - 1,"init_declarations")
	if p[3].get("is_decl"):
		st.print_error(p.lineno(1), p[3], 4, p[1][0]["type"])
	else:
		if p[3]["type"] is not None:
			st.print_error(p.lineno(1), {}, 3, p[3]["type"])
		p[3]["id_type"] = p[1][0]["id_type"]
		p[3]["myscope"] = p[1][0]["myscope"]
		p[3]["star"] = p[1][0]["star"]
		p[3]["type"] = p[1][0]["type"]		# Assign type of new init_declaration from first element of list of declarations
		p[3]["specifier"] = p[1][0]["specifier"]
	p[0] = p[1] + [p[3]]				# List of declarations
	pass

def p_init_declaration(p):
	"init_declaration : assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"init_declaration")
	p[0] = p[1]
	if p[1].get("inc",False):
		st.ScopeList[st.currentScope]["tac"].expression_emit(p[1]["tac_name"],'',"++", '')
	if p[1].get("dec",False):
		st.ScopeList[st.currentScope]["tac"].expression_emit(p[1]["tac_name"],'',"--", '')
	pass

def p_star_ptr_operator1(p):
	"star_ptr_operator : '*'"
	p[0] = p[1]
	pass

def p_star_ptr_operator2(p):
	"star_ptr_operator : star_ptr_operator cv_qualifier"
	add_children(len(list(filter(None, p[1:]))),"star_ptr_operator")
	pass

def p_nested_ptr_operator1(p):
	"nested_ptr_operator : star_ptr_operator"
	add_children(len(list(filter(None, p[1:]))),"nested_ptr_operator")
	p[0] = p[1]
	pass

def p_nested_ptr_operator2(p):
	"nested_ptr_operator : id_scope nested_ptr_operator"
	add_children(len(list(filter(None, p[1:]))),"nested_ptr_operator")
	pass

def p_ptr_operator1(p):
	"ptr_operator : '&'"
	create_child("ptr_operator",p[1])
	p[0] = p[1]
	pass

def p_ptr_operator2(p):
	"ptr_operator : nested_ptr_operator"
	add_children(len(list(filter(None, p[1:]))),"ptr_operator")
	p[0] = p[1]
	pass

def p_ptr_operator3(p):
	"ptr_operator : global_scope nested_ptr_operator"
	add_children(len(list(filter(None, p[1:]))),"ptr_operator")
	p[0] = p[2]
	pass

def p_ptr_operator_seq1(p):
	"ptr_operator_seq : ptr_operator"
	add_children(len(list(filter(None, p[1:]))),"ptr_operator_seq")
	pass

def p_ptr_operator_seq2(p):
	"ptr_operator_seq :  ptr_operator ptr_operator_seq"
	add_children(len(list(filter(None, p[1:]))),"ptr_operator_seq")
	pass

def p_ptr_operator_seq_opt1(p):
	"ptr_operator_seq_opt : empty               %prec SHIFT_THERE"
	pass

def p_ptr_operator_seq_opt2(p):
	"ptr_operator_seq_opt : ptr_operator ptr_operator_seq_opt"
	add_children(len(list(filter(None, p[1:]))),"ptr_operator_seq_opt")
	pass

def p_cv_qualifier_seq_opt1(p):
	"cv_qualifier_seq_opt : empty"
	pass

def p_cv_qualifier_seq_opt2(p):
	"cv_qualifier_seq_opt : cv_qualifier_seq_opt cv_qualifier"
	add_children(len(list(filter(None, p[1:]))),"cv_qualifier_seq_opt")
	pass

def p_cv_qualifier(p):
	'''cv_qualifier : CONST
					| VOLATILE'''
	create_child("cv_qualifier",p[1])
	p[0] = p[1]
	pass

def p_type_id1(p):
	"type_id : type_specifier abstract_declarator_opt"
	add_children(len(list(filter(None, p[1:]))),"type_id")
	pass

def p_type_id2(p):
	"type_id : type_specifier type_id"
	add_children(len(list(filter(None, p[1:]))),"type_id")
	pass

def p_abstract_declarator_opt1(p):
	"abstract_declarator_opt : empty"
	pass

def p_abstract_declarator_opt2(p):
	"abstract_declarator_opt : ptr_operator abstract_declarator_opt"
	add_children(len(list(filter(None, p[1:]))),"abstract_declarator_opt")
	pass

def p_abstract_declarator_opt3(p):
	"abstract_declarator_opt : direct_abstract_declarator"
	add_children(len(list(filter(None, p[1:]))),"abstract_declarator_opt")
	pass

def p_direct_abstract_declarator_opt1(p):
	"direct_abstract_declarator_opt : empty"
	pass

def p_direct_abstract_declarator_opt2(p):
	"direct_abstract_declarator_opt : direct_abstract_declarator"
	add_children(len(list(filter(None, p[1:]))),"direct_abstract_declarator_opt")
	pass

def p_direct_abstract_declarator1(p):
	"direct_abstract_declarator : direct_abstract_declarator_opt parenthesis_clause"
	add_children(len(list(filter(None, p[1:]))),"direct_abstract_declarator")
	pass

def p_direct_abstract_declarator2(p):
	"direct_abstract_declarator :  direct_abstract_declarator_opt '[' ']'"
	create_child("None",p[2])
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"direct_abstract_declarator")
	pass

def p_direct_abstract_declarator3(p):
	"direct_abstract_declarator : direct_abstract_declarator_opt '[' constant_expression ']'"
	create_child("None",p[2])
	create_child("None",p[4])
	add_children(len(list(filter(None, p[1:]))),"direct_abstract_declarator")
	pass

def p_parenthesis_clause1(p):
	"parenthesis_clause : parameters_clause cv_qualifier_seq_opt"
	add_children(len(list(filter(None, p[1:]))),"parenthesis_clause")
	p[0] = p[1]
	pass

def p_parenthesis_clause2(p):
	"parenthesis_clause : parameters_clause cv_qualifier_seq_opt exception_specification"
	add_children(len(list(filter(None, p[1:]))),"parenthesis_clause")
	p[0] = p[1]
	pass

def p_parameters_clause(p):
	"parameters_clause : '(' m_open_paren parameter_declaration_clause ')' "
	add_children(len(list(filter(None, p[1:]))) - 2,"paremeters_clause")
	p[0] = p[3] if p[3] else []
	st.parenthesis_ctr -= 1
	if st.parenthesis_ctr == 0:
		st.is_func_decl = False
	pass

def p_m_open_paren(p):
	"m_open_paren :"
	if st.parenthesis_ctr == 0:
		st.is_func_decl = True
	st.parenthesis_ctr += 1
	pass

def p_parameter_declaration_clause1(p):
	"parameter_declaration_clause : empty"
	pass

def p_parameter_declaration_clause2(p):
	"parameter_declaration_clause : parameter_declaration_list"
	add_children(len(list(filter(None, p[1:]))),"parameter_declaration_clause")
	p[0] = p[1]
	pass

def p_parameter_declaration_clause3(p):
	"parameter_declaration_clause : parameter_declaration_list ELLIPSIS"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"parameter_declaration_clause")
	p[0] = p[1]
	pass

def p_parameter_declaration_list1(p):
	"parameter_declaration_list : parameter_declaration"
	add_children(len(list(filter(None, p[1:]))),"parameter_declaration_list")
	p[0] = [p[1]]	# List of parameters
	pass

def p_parameter_declaration_list2(p):
	"parameter_declaration_list : parameter_declaration_list ',' parameter_declaration"
	add_children(len(list(filter(None, p[1:]))) -1,"parameter_declaration_list")
	p[0] = p[1] + [p[3]]
	pass

def p_abstract_pointer_declaration1(p):
	"abstract_pointer_declaration : ptr_operator_seq"
	add_children(len(list(filter(None, p[1:]))),"abstract_pointer_declaration")
	pass

def p_abstract_pointer_declaration2(p):
	"abstract_pointer_declaration : multiplicative_expression star_ptr_operator ptr_operator_seq_opt"
	add_children(len(list(filter(None, p[1:]))),"abstract_pointer_declaration")
	pass

def p_abstract_parameter_declaration1(p):
	"abstract_parameter_declaration : abstract_pointer_declaration"
	add_children(len(list(filter(None, p[1:]))),"abstract_parameter_declaration")
	pass

def p_abstract_parameter_declaration2(p):
	"abstract_parameter_declaration : and_expression '&'"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"abstract_parameter_declaration")
	pass

def p_abstract_parameter_declaration3(p):
	"abstract_parameter_declaration : and_expression '&' abstract_pointer_declaration"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"abstract_parameter_declaration")
	pass

def p_special_parameter_declaration1(p):
	"special_parameter_declaration : abstract_parameter_declaration"
	add_children(len(list(filter(None, p[1:]))),"special_parameter_declaration")
	pass

def p_special_parameter_declaration2(p):
	"special_parameter_declaration : abstract_parameter_declaration '=' assignment_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	pass

def p_special_parameter_declaration3(p):
	"special_parameter_declaration : ELLIPSIS"
	create_child("special_parameter_declaration",p[1])
	pass

def p_parameter_declaration1(p):
	"parameter_declaration : assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"parameter_declaration")
	p[0] = p[1]
	pass

def p_parameter_declaration2(p):
	"parameter_declaration : special_parameter_declaration"
	add_children(len(list(filter(None, p[1:]))),"parameter_declaration")
	p[0] = p[1]
	pass

def p_parameter_declaration3(p):
	"parameter_declaration : decl_specifier_prefix parameter_declaration"
	add_children(len(list(filter(None, p[1:]))),"parameter_declaration")
	p[0] = p[2]
	if p[0]["specifier"]:
		p[0]["specifier"] += [p[1]]
	else:
		p[0]["specifier"] = [p[1]]
	pass


#/*  function_definition includes constructor, destructor, implicit int definitions too.
# *  A local destructor is successfully parsed as a function-declaration but the ~ was treated as a unary operator.
# *  constructor_head is the prefix ambiguity between a constructor and a member-init-list starting with a bit-field.
# */

def p_function_definition1(p):
	"function_definition : ctor_definition"
	add_children(len(list(filter(None, p[1:]))),"function_definition")
	p[0] = p[1]
	pass

def p_function_definition2(p):
	"function_definition : func_definition"
	add_children(len(list(filter(None, p[1:]))),"function_definition")
	p[0] = p[1]
	pass

def p_func_definition1(p):
	"func_definition : assignment_expression function_try_block"
	add_children(len(list(filter(None, p[1:]))),"func_definition")
	p[0] = p[1] if p[1] else {}
	p[0]["stmt_list"] = p[0].get("stmt_list",[]) + p[2]["stmt_list"]
	pass

def p_func_definition2(p):
	"func_definition : assignment_expression marker_F function_body"
	add_children(len(list(filter(None, p[1:]))),"func_definition")

	p[0] = p[1] if p[1] else {}
	p[0]["stmt_list"] = p[0].get("stmt_list",[]) + p[3]["stmt_list"]
	st.ScopeList[st.currentScope]["tac"].emit(["end", p[0]["name"]])
	pass

def p_func_definition3(p):
	"func_definition : decl_specifier_prefix func_definition"
	add_children(len(list(filter(None, p[1:]))),"func_definition")
	p[0] = p[1] if p[1] else {}
	p[0]["stmt_list"] = p[0].get("stmt_list",[]) + p[2]["stmt_list"]
	pass

def p_ctor_definition1(p):
	"ctor_definition : constructor_head function_try_block"
	add_children(len(list(filter(None, p[1:]))),"ctor_definition")
	p[0] = p[1] if p[1] else {}
	if p[1]:
		p[0]["stmt_list"] += p[2]["stmt_list"]
	else:
		p[0]["stmt_list"] = p[2]["stmt_list"]
	pass

def p_ctor_definition2(p):
	"ctor_definition : constructor_head function_body"
	add_children(len(list(filter(None, p[1:]))),"ctor_definition")
	p[0] = p[1] if p[1] else {}
	if p[1]:
		p[0]["stmt_list"] += p[2]["stmt_list"]
	else:
		p[0]["stmt_list"] = p[2]["stmt_list"]
	pass

def p_ctor_definition3(p):
	"ctor_definition : decl_specifier_prefix ctor_definition"
	add_children(len(list(filter(None, p[1:]))),"ctor_definition")
	p[0] = p[1] if p[1] else {}
	if p[1]:
		p[0]["stmt_list"] += p[2]["stmt_list"]
	else:
		p[0]["stmt_list"] = p[2]["stmt_list"]
	pass

def p_constructor_head1(p):
	"constructor_head : bit_field_init_declaration"
	add_children(len(list(filter(None, p[1:]))),"constructor_head")
	p[0] = p[1]
	pass

def p_constructor_head2(p):
	"constructor_head : constructor_head ',' assignment_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,"constructor_head")
	pass

def p_function_try_block(p):
	"function_try_block : TRY function_block handler_seq"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"function_try_block")
	p[0] = p[2] if p[2] else {}
	if p[1]:
		p[0]["stmt_list"] += p[3]["stmt_list"]
	else:
		p[0]["stmt_list"] = p[3]["stmt_list"]
	pass

def p_function_block(p):
	"function_block : ctor_initializer_opt function_body"
	add_children(len(list(filter(None, p[1:]))),"function_block")
	p[0] = p[1] if p[1] else {}
	if p[1]:
		p[0]["stmt_list"] += p[2]["stmt_list"]
	else:
		p[0]["stmt_list"] = p[2]["stmt_list"]
	pass

def p_function_body(p):
	"function_body : compound_statement"
	add_children(len(list(filter(None, p[1:]))),"function_body")
	p[0] = p[1]
	pass

#/*
# *  An = initializer looks like an extended assignment_expression.
# *  An () initializer looks like a function call.
# *  initializer is therefore flattened into its generalised customers.


def p_initializer_clause1(p):
	"initializer_clause : assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"initializer_clause")
	p[0] = dict(inits=[p[1]], is_checked=False, dim=0)
	pass

def p_initializer_clause2(p):
	"initializer_clause : braced_initializer"
	add_children(len(list(filter(None, p[1:]))),"initializer_clause")
	p[0] = p[1]			# It is a dictionary with keys inits and is_checked
	p[0]["is_checked"] = True	# Well! It should be True in p[1] already
	pass

def p_braced_initializer1(p):
	"braced_initializer : '{' m_new_scope initializer_list '}'"
	add_children(len(list(filter(None, p[1:]))) - 2,"braced_initializer")
	SymbolTable.endScope()
	p[0] = p[3]
	pass

def p_braced_initializer2(p):
	"braced_initializer : '{' m_new_scope initializer_list ',' '}'"
	add_children(len(list(filter(None, p[1:]))) - 3,"braced_initializer")
	SymbolTable.endScope()
	p[0] = p[3]
	p[0]["dim"] += 1
	pass

def p_braced_initializer3(p):
	"braced_initializer : '{' '}'"
	create_child("None",p[1])
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"braced_initializer")
	p[0] = dict(inits=[], is_checked=True, dim=1)	# Empty list "inits" will indicate to initialize all elements like in array
	pass

def p_braced_initializer4(p):
	"braced_initializer : '{' m_new_scope looping_initializer_clause '#' bang error '}'"
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))) - 2,"braced_initializer")
	SymbolTable.endScope()
	print("[PARSER] This line should not be printed")
	pass

def p_braced_initializer5(p):
	"braced_initializer : '{' m_new_scope initializer_list ',' looping_initializer_clause '#' bang error '}'"
	create_child("None",p[5])
	add_children(len(list(filter(None, p[1:]))) - 3,"braced_initializer")
	SymbolTable.endScope()
	print("[PARSER] This line should not be printed")
	pass

def p_initializer_list1(p):
	"initializer_list : looping_initializer_clause"
	add_children(len(list(filter(None, p[1:]))),"initializer_list")
	if p[1]["is_checked"]:
		p[0] = p[1]
		return
	# If p[1]["is_checked"] is False then there must be only one element in "inits" keys
	exp = p[1]["inits"][0]
	if exp.get("id_type") in ["type_specifier", "array", "function"]:
		st.print_error(p.lineno(1), {}, 15, exp["name"])
		p[0] = dict(inits=[dict(name="0", id_type="literal", value=0, type=["literal_int"])], is_checked=True, dim=0)	# Default 0
		return
	if exp.get("is_decl", True) is False:
		if exp["type"]:		# i.e.  {int x}
			st.print_error(p.lineno(1), {}, 15, ' '.join(exp["type"].append(exp["name"])))
			p[0] = dict(inits=[dict(name="0", id_type="literal", value=0, type=["literal_int"])], is_checked=True, dim=0)	# Default 0
			return
		entry = dict(SymbolTable.lookupComplete(exp["name"]))
		if entry is None:
			st.print_error(lineno, exp["name"], 1)
			p[0] = dict(inits=[dict(name="0", id_type="literal", value=0, type=["literal_int"])], is_checked=True, dim=0)	# Default 0
			return
		else:
			entry["is_decl"] = True
			p[0] = dict(inits=[entry], is_checked=True, dim=0)
	else:		# Either literal or declared expression
		p[0] = dict(inits=[exp], is_checked=True, dim=0)
	pass

def p_initializer_list2(p):
	"initializer_list : initializer_list ',' looping_initializer_clause"
	add_children(len(list(filter(None, p[1:])))  -1 ,"initializer_list")
	p[0] = p[1]		# p[1]["is_checked"] should be True
	if p[3]["is_checked"]:
		p[0]["inits"] += p[3]["inits"]
		p[0]["dim"] = max(p[1]["dim"], p[3]["dim"])
		return
	# If p[3]["is_checked"] is False then there must be only one element in "inits" keys
	exp = p[3]["inits"][0]
	if exp.get("id_type") in ["type_specifier", "array", "function"]:
		st.print_error(p.lineno(1), {}, 15, exp["name"])
		p[0]["inits"] += [dict(name="0", id_type="literal", value=0, type=["literal_int"])] 	# Default 0
		return
	if exp.get("is_decl", True) is False:
		if exp["type"]:		# i.e.  {int x}
			st.print_error(p.lineno(1), {}, 15, ' '.join(exp["type"].append(exp["name"])))
			p[0]["inits"] += [dict(name="0", id_type="literal", value=0, type=["literal_int"])]		# Default 0
			return
		entry = dict(SymbolTable.lookupComplete(exp["name"]))
		if entry is None:
			st.print_error(lineno, exp["name"], 1)
			p[0]["inits"] += [dict(name="0", id_type="literal", value=0, type=["literal_int"])]		# Default 0
			return
		else:
			entry["is_decl"] = True
			p[0]["inits"] += [entry]
	else:		# Either literal or declared expression
		p[0]["inits"] += [exp]
	pass

def p_looping_initializer_clause(p):
	"looping_initializer_clause : start_search looped_initializer_clause"
	add_children(len(list(filter(None, p[1:]))),"looping_initializer_clause")
	p[0] = p[2]
	pass

def p_looped_initializer_clause1(p):
	"looped_initializer_clause : initializer_clause"
	add_children(len(list(filter(None, p[1:]))),"looped_initializer_clause")
	p[0] = p[1]		# p[1] will be dict in which inits could be list in cases like { x, {y}}
	pass

def p_looped_initializer_clause2(p):
	"looped_initializer_clause : advance_search '+' looped_initializer_clause"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"looped_initializer_clause")
	pass

def p_looped_initializer_clause3(p):
	"looped_initializer_clause : advance_search '-'"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"looped_initializer_clause")
	pass

#/*---------------------------------------------------------------------------------------------------
# * A.8 Classes
# *---------------------------------------------------------------------------------------------------

def p_colon_mark(p):
	"colon_mark : ':'"
	create_child("colon_mark",p[1])
	pass

def p_elaborated_class_specifier1(p):
	"elaborated_class_specifier : class_key scoped_id                    %prec SHIFT_THERE"
	add_children(len(list(filter(None, p[1:]))),"elaborated_class_specifier")
	p[0] = p[2]
	key = "____" + str(p[0]["name"]) + "____"
	if key in st.ScopeList.keys():
		entry = SymbolTable.lookupComplete(key)
		if entry is None:
			st.print_error(p.lineno(1), {}, 44, p[0]["name"], str(p[1]))
			return
		else:
			if entry["id_type"] != p[1]:
				st.print_error(p.lineno(1), {}, 44, p[0]["name"], str(p[1]))
			p[0] = dict(entry)
			p[0]["is_decl"] = True
	else:
		st.print_error(p.lineno(1), {}, 44, p[0]["name"], str(p[1]))
	pass

def p_elaborated_class_specifier2(p):
	"elaborated_class_specifier : class_key scoped_id colon_mark error"
	add_children(len(list(filter(None, p[1:]))),"elaborated_class_specifier")
	p[0] = p[2]
	pass

def p_class_specifier_head1(p):
	"class_specifier_head : class_key scoped_id colon_mark base_specifier_list '{'"
	create_child("None",p[5])
	add_children(len(list(filter(None, p[1:]))),"class_specifier_head")
	SymbolTable.addScope(str(st.scope_ctr), "class_scope")
	st.scope_ctr += 1
	pass

def p_class_specifier_head2(p):
	"class_specifier_head : class_key ':' base_specifier_list '{'"
	create_child("None",p[2])
	create_child("None",p[4])
	add_children(len(list(filter(None, p[1:]))),"class_specifier_head")
	SymbolTable.addScope(str(st.scope_ctr), "class_scope")
	st.scope_ctr += 1
	pass

def p_class_specifier_head3(p):
	"class_specifier_head : class_key scoped_id '{'"
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"class_specifier_head")
	p[0] = p[2]
	new_name = "____" + str(p[2]["name"]) + "____"
	if new_name in st.ScopeList.keys():
		st.print_error(p.lineno(1), {}, 43, p[0]["name"], st.ScopeList[st.currentScope]["table"].symtab[new_name]["id_type"])
		SymbolTable.addScope(str(st.scope_ctr), "block_scope")
		st.scope_ctr += 1
	else:
		p[0]["name"] = new_name
		p[0]["id_type"] = str(p[1])
		p[0]["is_defined"] = True
		p[0]["is_decl"] = True
		SymbolTable.insertID(p.lineno(1), p[0]["name"], p[0]["id_type"], types=[], specifiers=[],
							num=1, value=None, stars=0, order=[],
							parameters=[], defined=p[0]["is_defined"], access=st.access_specifier, scope=str(st.currentScope))
		SymbolTable.addScope(new_name, str(p[1]) + "_scope")
	pass

def p_class_specifier_head4(p):
	"class_specifier_head : class_key '{'"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"class_specifier_head")
	new_name = "____" + str(st.scope_ctr) + "____"
	SymbolTable.addScope(new_name, "class_scope")
	st.scope_ctr += 1
	p[0] = dict(name=new_name, id_type=str(p[1]), is_defined=True, is_decl=True, num=1, type=[], specifier=[], value=None, star=0, order=[], parameters=[], access="public")
	pass

def p_class_key(p):
	'''class_key : CLASS
				 | STRUCT
				 | UNION'''
	create_child("class_key",p[1])
	p[0] = p[1]
	pass

def p_class_specifier1(p):
	"class_specifier : class_specifier_head member_specification_opt '}'"
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"class_specifier")
	SymbolTable.endScope()
	st.access_specifier = "public"
	p[0] = p[1]
	pass

def p_class_specifier2(p):
	"class_specifier : class_specifier_head member_specification_opt util looping_member_declaration '#' bang error '}'"
	create_child("None",p[5])
	create_child("None",p[8])
	add_children(len(list(filter(None, p[1:]))),"class_specifier")
	SymbolTable.endScope()
	st.access_specifier = "public"
	p[0] = p[1]
	pass

def p_member_specification_opt1(p):
	"member_specification_opt : empty"
	pass

def p_member_specification_opt2(p):
	"member_specification_opt : member_specification_opt util looping_member_declaration"
	add_children(len(list(filter(None, p[1:]))),"member_specification_opt")
	p[0] = p[1] if p[1] else {}
	p[0]["stmt_list"] = p[0].get("stmt_list",[]) + p[3]["stmt_list"]
	pass

def p_member_specification_opt3(p):
	"member_specification_opt : member_specification_opt util looping_member_declaration '#' bang error ';'"
	create_child("None",p[4])
	add_children(len(list(filter(None, p[1:]))) - 1,"member_specification_opt")
	pass

def p_looping_member_declaration(p):
	"looping_member_declaration : start_search looped_member_declaration"
	add_children(len(list(filter(None, p[1:]))),"looping_member_declaration")
	p[0] = p[2]
	pass

def p_looped_member_declaration1(p):
	"looped_member_declaration : member_declaration"
	add_children(len(list(filter(None, p[1:]))),"looped_member_declaration")
	p[0] = p[1]
	pass

def p_looped_member_declaration2(p):
	"looped_member_declaration : advance_search '+' looped_member_declaration"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"looped_member_declaration")
	pass

def p_looped_member_declaration3(p):
	"looped_member_declaration : advance_search '-'"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"looped_member_declaration")
	pass

def p_member_declaration1(p):
	"member_declaration : accessibility_specifier"
	add_children(len(list(filter(None, p[1:]))),"member_declaration")
	p[0] = p[1]
	pass

def p_member_declaration2(p):
	"member_declaration : simple_member_declaration"
	add_children(len(list(filter(None, p[1:]))),"member_declaration")
	p[0] = p[1]
	pass

def p_member_declaration3(p):
	"member_declaration : function_definition"
	add_children(len(list(filter(None, p[1:]))),"member_declaration")
	p[0] = p[1]
	pass

def p_member_declaration4(p):
	"member_declaration : using_declaration"
	add_children(len(list(filter(None, p[1:]))),"member_declaration")
	p[0] = p[1]
	pass


def p_simple_member_declaration1(p):
	"simple_member_declaration : ';'"
	create_child("simple_member_declaration",p[1])
	p[0] = []
	pass

def p_simple_member_declaration2(p):
	"simple_member_declaration : assignment_expression ';'"
	add_children(len(list(filter(None, p[1:]))) - 1,"simple_member_declaration")
	p[0] = []
	if p[1]:
		if "is_decl" not in p[1].keys():	# i.e. built_in_type_specifier ; (Illegal statement)
			if p[1]["id_type"] in ["type_specifier",]:
				st.print_error(p.lineno(1), p[1], 2)	# error: declaration does not declare anything
		else:
			if p[1]["is_decl"]:
				if p[1]["id_type"] == "function" and p[1]["is_defined"] is False and p[1]["is_decl"] is True:
					st.print_error(p.lineno(1), {}, 29, p[1]["name"]) # function redeclaration
					st.function_list.pop()
			elif p[1]["type"] is not None:
				if p[1]["id_type"] in ["function"]:
					st.function_list.pop()
				SymbolTable.insertID(p.lineno(1), p[1]["name"], p[1]["id_type"], types=p[1]["type"], specifiers=p[1]["specifier"],
				 					num=p[1]["num"], value=p[1]["value"], stars=p[1]["star"], order=p[1]["order"],
									parameters=p[1]["parameters"], defined=p[1]["is_defined"], access=st.access_specifier, scope=p[1]["myscope"])
			elif SymbolTable.lookupComplete(p[1]["name"]) is None:
				st.print_error(p.lineno(1), p[1], 1)
				if p[1]["id_type"] in ["function"]:
					st.function_list.pop()
				#SymbolTable.insertID(p.lineno(1), p[1]["name"], p[1]["id_type"], types=p[1]["type"], specifiers=p[1]["specifier"],
				# 					num=p[1]["num"], value=p[1]["value"], stars=p[1]["star"], order=p[1]["order"],
				#					parameters=p[1]["parameters"], defined=p[1]["is_defined"])
				pass
			else:
				pass
			p[0] = [p[1]]
	pass

def p_simple_member_declaration3(p):
	"simple_member_declaration : constructor_head ';'"
	#create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))) -1,"simple_member_declaration")
	pass

def p_simple_member_declaration4(p):
	"simple_member_declaration : member_init_declarations ';'"
	#create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))) - 1,"simple_member_declaration")
	p[0] = []
	if p[1]:
		for decl in p[1]:
			if "is_decl" not in decl.keys():
				if decl["id_type"] in ["type_specifier",]:
					st.print_error(p.lineno(1), decl, 2)
			else:
				if decl["is_decl"]:
					if decl["id_type"] == "function" and decl["is_defined"] is False and decl["is_decl"] is True:
						st.print_error(p.lineno(1), {}, 29, decl["name"])	# function redeclaration
				elif decl["type"] is not None:
					SymbolTable.insertID(p.lineno(1), decl["name"], decl["id_type"], types=decl["type"], specifiers=decl["specifier"],
					 					num=decl["num"], value=decl["value"], stars=decl["star"], order=decl["order"],
										parameters=decl["parameters"], defined=decl["is_defined"], access=st.access_specifier, scope=decl["myscope"])
				elif SymbolTable.lookupComplete(decl["name"]) is None:
					st.print_error(p.lineno(1), decl, 1)
					#SymbolTable.insertID(p.lineno(1), decl["name"], decl["id_type"], types=decl["type"], specifiers=decl["specifier"],
					# 					num=decl["num"], value=decl["value"], stars=decl["star"], order=decl["order"],
					#					parameters=decl["parameters"], defined=decl["is_defined"])
					pass
				else:
					pass
			p[0] += [decl]
		if not p[0]:
			p[0] = []
	pass

def p_simple_member_declaration5(p):
	"simple_member_declaration : decl_specifier_prefix simple_member_declaration"
	add_children(len(list(filter(None, p[1:]))),"simple_member_declaration")
	if len(p[2]) == 0:			# i.e. decl_specifier_prefix ;
		st.print_error(p.lineno(1), {}, 2)
	else:
		for decl in p[2]:
			if decl.get("is_decl") is True:		# already declared before
				st.print_error(p.lineno(1), decl, 6)
			elif decl.get("is_decl") is False:
				SymbolTable.addIDAttr(decl["name"], "specifier", [p[1]])
				if (decl["id_type"] in ["variable", "array"]) and ("const" == p[1]) and (decl["value"] is None):
					st.print_error(p.lineno(1), decl, 5)
					SymbolTable.addIDAttr(decl["name"], "value", 0)			# DEFAULT value of const variable is 0
	p[0] = p[2]
	pass

def p_member_init_declarations1(p):
	"member_init_declarations : assignment_expression ',' member_init_declaration"
	add_children(len(list(filter(None, p[1:]))) -1 ,"member_init_declarations")
	if p[3].get("is_decl"):
		st.print_error(p.lineno(1), p[3], 4, p[1]["type"])
	else:
		if p[3]["type"] is not None:
			st.print_error(p.lineno(1), {}, 3, p[3]["type"])
		p[3]["type"] = p[1]["type"]			# Consider first type only
		p[3]["specifier"] = p[1]["specifier"]
	p[0] = [p[1], p[3]]			# List of declarations
	pass

def p_member_init_declarations2(p):
	"member_init_declarations : constructor_head ',' bit_field_init_declaration"
	add_children(len(list(filter(None, p[1:]))) - 1,"member_init_declarations")
	pass

def p_member_init_declarations3(p):
	"member_init_declarations : member_init_declarations ',' member_init_declaration"
	add_children(len(list(filter(None, p[1:]))) - 1,"member_init_declarations")
	if p[3].get("is_decl"):
		st.print_error(p.lineno(1), p[3], 4, p[1][0]["type"])
	else:
		if p[3]["type"] is not None:
			st.print_error(p.lineno(1), {}, 3, p[3]["type"])
		p[3]["type"] = p[1][0]["type"]		# Assign type of new init_declaration from first element of list of declarations
		p[3]["specifier"] = p[1][0]["specifier"]
	p[0] = p[1] + [p[3]]				# List of declarations
	pass

def p_member_init_declaration1(p):
	"member_init_declaration : assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"member_init_declaration")
	p[0] = p[1]
	pass

def p_member_init_declaration2(p):
	"member_init_declaration : bit_field_init_declaration"
	add_children(len(list(filter(None, p[1:]))),"member_init_declaration")
	p[0] = p[1]
	pass

def p_accessibility_specifier(p):
	"accessibility_specifier : access_specifier ':'"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"accessibility_specifier")
	p[0] = p[1]
	st.access_specifier = str(p[1])
	pass

def p_bit_field_declaration1(p):
	"bit_field_declaration : assignment_expression ':' bit_field_width"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"bit_field_declaration")
	pass

def p_bit_field_declaration2(p):
	"bit_field_declaration : ':' bit_field_width"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"bit_field_declaration")
	pass

def p_bit_field_width1(p):
	"bit_field_width : logical_or_expression"
	add_children(len(list(filter(None, p[1:]))),"bit_field_width")
	pass

def p_bit_field_width2(p):
	"bit_field_width : logical_or_expression '?' bit_field_width ':' bit_field_width"
	add_children(len(list(filter(None, p[1:]))) -2,"Ternary If Then Else")
	pass

def p_bit_field_init_declaration1(p):
	"bit_field_init_declaration : bit_field_declaration"
	add_children(len(list(filter(None, p[1:]))),"bit_field_init_declaration")
	pass

def p_bit_field_init_declaration2(p):
	"bit_field_init_declaration : bit_field_declaration '=' initializer_clause"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	pass

#/*---------------------------------------------------------------------------------------------------
# * A.9 Derived classes
# *---------------------------------------------------------------------------------------------------*/

def p_base_specifier_list1(p):
	"base_specifier_list : base_specifier"
	add_children(len(list(filter(None, p[1:]))),"base_specifier_list")
	pass

def p_base_specifier_list2(p):
	"base_specifier_list : base_specifier_list ',' base_specifier"
	add_children(len(list(filter(None, p[1:]))) -1,"base_specifier_list")
	pass

def p_base_specifier1(p):
	"base_specifier : scoped_id"
	add_children(len(list(filter(None, p[1:]))),"base_specifier")
	pass

def p_base_specifier2(p):
	"base_specifier : access_specifier base_specifier"
	add_children(len(list(filter(None, p[1:]))),"base_specifier")
	pass

def p_base_specifier3(p):
	"base_specifier : VIRTUAL base_specifier"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"base_specifier")
	pass

def p_access_specifier(p):
	'''access_specifier : PRIVATE
						| PROTECTED
						| PUBLIC'''
	create_child("access_specifier",p[1])
	p[0] = p[1]
	pass

#/*---------------------------------------------------------------------------------------------------
# * A.10 Special member functions
# *---------------------------------------------------------------------------------------------------*/

def p_conversion_function_id(p):
	"conversion_function_id : OPERATOR conversion_type_id"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"conversion_function_id")
	pass

def p_conversion_type_id1(p):
	"conversion_type_id : type_specifier ptr_operator_seq_opt"
	add_children(len(list(filter(None, p[1:]))),"conversion_type_id")
	pass

def p_conversion_type_id2(p):
	"conversion_type_id : type_specifier conversion_type_id"
	add_children(len(list(filter(None, p[1:]))),"conversion_type_id")
	pass

def p_ctor_initializer_opt1(p):
	"ctor_initializer_opt : empty"
	pass

def p_ctor_initializer_opt2(p):
	"ctor_initializer_opt : ctor_initializer"
	add_children(len(list(filter(None, p[1:]))),"ctor_initializer_opt")
	pass

def p_ctor_initializer1(p):
	"ctor_initializer : ':' mem_initializer_list"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"ctor_initializer")
	pass

def p_ctor_initializer2(p):
	"ctor_initializer : ':' mem_initializer_list bang error"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"ctor_initializer")
	pass

def p_mem_initializer_list1(p):
	"mem_initializer_list : mem_initializer"
	add_children(len(list(filter(None, p[1:]))),"mem_initializer_list")
	pass

def p_mem_initializer_list2(p):
	"mem_initializer_list : mem_initializer_list_head mem_initializer"
	add_children(len(list(filter(None, p[1:]))),"mem_initializer_list")
	pass

def p_mem_initializer_list_head1(p):
	"mem_initializer_list_head : mem_initializer_list ','"
	add_children(len(list(filter(None, p[1:]))) - 1,"mem_initializer_list_head")
	pass

def p_mem_initializer_list_head2(p):
	"mem_initializer_list_head : mem_initializer_list bang error ','"
	add_children(len(list(filter(None, p[1:]))) -1,"mem_initializer_list_head")
	pass

def p_mem_initializer(p):
	"mem_initializer : mem_initializer_id '(' expression_list_opt ')' "
	create_child("None",p[2])
	create_child("None",p[4])
	add_children(len(list(filter(None, p[1:]))),"mem_initializer")
	pass

def p_mem_initializer_id(p):
	"mem_initializer_id : scoped_id"
	add_children(len(list(filter(None, p[1:]))),"mem_initializer_id")
	pass

#/*---------------------------------------------------------------------------------------------------
# * A.11 Overloading
# *---------------------------------------------------------------------------------------------------*/

def p_operator_function_id(p):
	"operator_function_id : OPERATOR operator"
	create_child("None",p[1])
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"operator_function_id")
	pass

def p_operator(p):
	'''operator : NEW
				| DELETE
				| '+'
				| '-'
				| '*'
				| '/'
				| '%'
				| '^'
				| '&'
				| '|'
				| '~'
				| '!'
				| '='
				| '<'
				| '>'
				| ASS_ADD
				| ASS_SUB
				| ASS_MUL
				| ASS_DIV
				| ASS_MOD
				| ASS_XOR
				| ASS_AND
				| ASS_OR
				| SHL
				| SHR
				| ASS_SHR
				| ASS_SHL
				| EQ
				| NE
				| LE
				| GE
				| LOG_AND
				| LOG_OR
				| INC
				| DEC
				| ','
				| ARROW_STAR
				| ARROW
				| '(' ')'
				| '[' ']'
				'''
	if p[1] == ',':
		pass
	elif p[1] =='(' or p[1] == '[':
		pass
	else:
		p[0] = p[1]
	pass

#/*---------------------------------------------------------------------------------------------------
# * A.12 Templates
# *---------------------------------------------------------------------------------------------------*/


#/*---------------------------------------------------------------------------------------------------
# * A.13 Exception Handling
# *---------------------------------------------------------------------------------------------------*/

def p_try_block(p):
	"try_block : TRY compound_statement handler_seq"
	add_children(len(list(filter(None, p[1:]))),"try_block")
	pass

def p_handler_seq1(p):
	"handler_seq : handler"
	add_children(len(list(filter(None, p[1:]))),"handler_seq")
	pass

def p_handler_seq2(p):
	"handler_seq : handler handler_seq"
	add_children(len(list(filter(None, p[1:]))),"handler_seq")
	pass

def p_handler(p):
	"handler : CATCH '('  exception_declaration ')' marker_M compound_statement"
	add_children(len(list(filter(None, p[1:]))),"Catch - exception")
	pass

def p_exception_declaration(p):
	"exception_declaration : parameter_declaration"
	add_children(len(list(filter(None, p[1:]))),"exception_declaration")
	p[0] = p[1]
	pass

def p_throw_expression1(p):
	"throw_expression : THROW"
	create_child("throw_expression",p[1])
	pass

def p_throw_expression2(p):
	"throw_expression : THROW assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"throw_expression")
	pass

def p_exception_specification1(p):
	"exception_specification : THROW '('  ')'  "
	create_child("None",p[1])
	pass

def p_exception_specification2(p):
	"exception_specification : THROW '(' type_id_list ')' "
	add_children(len(list(filter(None, p[1:]))) - 3,"THROW")
	pass

def p_type_id_list1(p):
	"type_id_list : type_id"
	add_children(len(list(filter(None, p[1:]))),"type_id_list")
	pass

def p_type_id_list2(p):
	"type_id_list : type_id_list ',' type_id"
	add_children(len(list(filter(None, p[1:]))) - 1,"type_id_list")
	pass

#/*---------------------------------------------------------------------------------------------------
# * Back-tracking and context support
#*---------------------------------------------------------------------------------------------------*/

def p_advance_search(p):
	"advance_search : error"
	#add_children(len(list(filter(None, p[1:]))),"advance_search")
	pass

def p_bang(p):
	"bang : empty"
	pass
#def p_mark(p):
#    "mark : empty"
	pass
def p_nest(p):
	"nest : empty"
	pass

def p_start_search(p):
	"start_search : empty"
	pass

def p_start_search1(p):
	"start_search1 : empty"
	pass

def p_util(p):
	"util : empty"
	pass

def p_empty(p):
	'empty : '
	pass
def p_marker_N(p):
	"marker_N : empty"
	p[0] = dict()
	p[0]["nextlist"] = [st.ScopeList[st.currentScope]["tac"].getnext()]
	st.ScopeList[st.currentScope]["tac"].emit(["goto",""])
	pass


def p_marker_M(p):
	'marker_M : empty'
	p[0] = dict()
	p[0]["quad"] = st.ScopeList[st.currentScope]["tac"].getnext()
	pass

def p_marker_F(p):
	"marker_F : empty"
	func = st.function_list[-1]
	st.ScopeList[st.currentScope]["tac"].emit(["function", func["name"], ":" ] )
	for param in func["parameters"]:
		st.ScopeList[st.currentScope]["tac"].emit(["param",str(param["name"]) + "_" + str(func["name"])])

# Error rule for syntax errors
def p_error(p):
	print(st.color.cerror, p)

# Build the parser
if __name__ == "__main__":
	# Create SymbolTable
	global SymbolTable
	SymbolTable = st.SymTab()
	#import logging
	#logging.basicConfig(
	#    level = logging.DEBUG,
	#    filename = "parselog.txt",
	#    filemode = "w",
	#    format = "%(filename)10s:%(lineno)4d:%(message)s"
	#)
	#log = logging.getLogger('ply')

	#sys.exit()
	#parser = yacc.yacc(errorlog=yacc.NullLogger())
	parser = yacc.yacc(debug=True)
	#if(len(sys.argv) == 2):
	#	filename = sys.argv[1]
	#else:
	filename = "../tests/sample_test.cpp"
	a = open(filename)
	data = a.read()
	#data = '''
	yacc.parse(data, lexer=lex.cpp_scanner.lexer, tracking=True)
	graph.write_jpeg('parse_tree.jpeg')
	graph.write_dot('parse_tree.dot')
	f = open("parse_tree.dat","w")
	f.write(graph.to_string())
	print("================================================================================================\n\n")
	asm = cg.CodeGen(st.ScopeList["global"]["tac"])
	asm.gen_data_section()
	asm.parse_tac()
	asm.print_sections()
	st.print_tac()
	#st.print_table()
	print("================================================================================================\n\n")
	pass
