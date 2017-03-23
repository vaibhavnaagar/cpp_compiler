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
import symtable as sym

orphan_children = []
i = 0
graph = pydot.Dot(graph_type='graph')
def add_children(n,name):
	global i
	global orphan_children
	if n > len(orphan_children):
		print("===========================================ERROR============================> " + name)
		for child in orphan_children:
			print(child.get_label())
		print(n)
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

# Get the token map
tokens = lex.cpp_scanner.tokens

precedence = (
				('nonassoc', 'SHIFT_THERE'),
				('nonassoc', 'SCOPE', 'ELSE', 'INC', 'DEC', '+', '-', '*', '&', '[', '{', '<', ':', 'STRING'),
				('nonassoc', 'REDUCE_HERE_MOSTLY'),
				('nonassoc', '(')
)

start = 'translation_unit'

def p_identifier(p):
	"identifier : IDENTIFIER"
	#print(yacc.YaccProduction.lineno(p,1))
	#print(p.slice[1].type)
	#print(p[:])
	create_child("identifier",p[1])
	
	pass


def p_id1(p):
	"id : identifier"
	add_children(len(list(filter(None, p[1:]))),"id")
	
	pass


def p_global_scope1(p):
	"global_scope : SCOPE"
	create_child("global_scope",p[1])
	
	
	pass


def p_id_scope(p):
	"id_scope : id SCOPE"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"id_scope")
	
	pass

#/*
 #*  A :: B :: C; is ambiguous How much is type and how much name ?
 #*  The %prec maximises the (type) length which is the 7.1-2 semantic constraint.
 #*/

def p_nested_id1(p):
	"nested_id : id                                  %prec SHIFT_THERE"
	add_children(len(list(filter(None, p[1:]))),"nested_id")
	
	pass

def p_nested_id2(p):
	"nested_id : id_scope nested_id"
	add_children(len(list(filter(None, p[1:]))),"nested_id")
	
	pass 

def p_scoped_id1(p):
	"scoped_id : nested_id"
	add_children(len(list(filter(None, p[1:]))),"scoped_id")
	
	pass

def p_scoped_id2(p):
	"scoped_id : global_scope nested_id"
	add_children(len(list(filter(None, p[1:]))),"scoped_id")
	
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
	
	pass

def p_built_in_type_id2(p):
	"built_in_type_id : built_in_type_id built_in_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"built_in_type_id")
	
	pass

def p_pseudo_destructor_id1(p):
	"pseudo_destructor_id : built_in_type_id SCOPE '~' built_in_type_id"
	create-children("None",p[2])
	create-children("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"pseudo_destructor_id")
	
	pass

def p_pseudo_destructor_id2(p):
	"pseudo_destructor_id : '~' built_in_type_id"
	create-children("None",p[1])
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
	
	pass

def p_literal1(p):
	"literal : INTEGER"
	create_child("literal - int",p[1])
	
	pass

def p_literal2(p):
	"literal : CHARACTER"
	create_child("literal - char",p[1])
	
	pass

def p_literal3(p):
	"literal : FLOATING"
	create_child("literal - float",p[1])
	
	pass

def p_literal4(p):
	"literal : string"
	add_children(len(list(filter(None, p[1:]))),"literal")
	
	pass

def p_literal5(p):
	"literal : boolean_literal"
	add_children(len(list(filter(None, p[1:]))),"literal")
	
	pass

def p_boolean_literal1(p):
	"boolean_literal : FALSE"
	create_child("boolean",p[1])
	
	pass

def p_boolean_literal2(p):
	"boolean_literal : TRUE"
	create_child("boolean",p[1])
	
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
	
	pass

def p_primary_expression2(p):
	"primary_expression : THIS"
	create_child("primary_expression",p[1])
	
	pass

def p_primary_expression3(p):
	"primary_expression : suffix_decl_specified_ids"
	add_children(len(list(filter(None, p[1:]))),"primary expression")
	
	pass

def p_primary_expression4(p):
	"primary_expression : abstract_expression               %prec REDUCE_HERE_MOSTLY"
	add_children(len(list(filter(None, p[1:]))),"primary expression")
	
	pass

#/*
# *  Abstract-expression covers the () and [] of abstract-declarators.
# */

def p_abstract_expression1(p):
	"abstract_expression : parenthesis_clause"
	add_children(len(list(filter(None, p[1:]))),"abstract_expression")
	
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
#    
	pass

#def p_mark_type1(p):
#    "mark_type1 : empty"
#    
	pass
'''
def p_postfix_expression1(p):
	"postfix_expression : primary_expression"
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	
	pass

def p_postfix_expression2(p):
	"postfix_expression : postfix_expression parenthesis_clause"
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	
	pass
'''
#def p_postfix_expression2(p):
#    "postfix_expression : postfix_expression parenthesis_clause mark_type1 '-'"
#    
	pass

#def p_postfix_expression3(p):
#    "postfix_expression : postfix_expression parenthesis_clause mark_type1 '+' type1_parameters mark '{' error"
#    
	pass

#def p_postfix_expression4(p):
#    "postfix_expression : postfix_expression parenthesis_clause mark_type1 '+' type1_parameters mark error"
#    
	pass

#def p_postfix_expression5(p):
#    "postfix_expression : postfix_expression parenthesis_clause mark_type1 '+' error"
#    
	pass
'''
def p_postfix_expression6(p):
	"postfix_expression : postfix_expression '[' expression_opt ']'"
	create_child("None","[")
	create_child("None","]")
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	
	pass

def p_postfix_expression7(p):
	"postfix_expression : postfix_expression '.' declarator_id"
	create_child("None",".")
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	
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
	
	pass

def p_postfix_expression12(p):
	"postfix_expression : postfix_expression DEC"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"postfix_expression")
	
	pass

def p_postfix_expression13(p):
	"postfix_expression : DYNAMIC_CAST '<' type_id '>' '(' expression ')'"
	add_children(len(list(filter(None, p[1:]))) - 5,p[1])
	
	pass

def p_postfix_expression14(p):
	"postfix_expression : STATIC_CAST '<' type_id '>' '(' expression ')'"
	add_children(len(list(filter(None, p[1:]))) -5,p[1])
	
	pass

def p_postfix_expression15(p):
	"postfix_expression : REINTERPRET_CAST '<' type_id '>' '(' expression ')'"
	add_children(len(list(filter(None, p[1:]))) -5 ,p[1])
	
	pass

def p_postfix_expression16(p):
	"postfix_expression : CONST_CAST '<' type_id '>' '(' expression ')'"
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
	
	pass

def p_expression_list1(p):
	"expression_list : assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"expression_list")
	
	pass

def p_expression_list2(p):
	"expression_list : expression_list ',' assignment_expression"
	
	add_children(len(list(filter(None, p[1:]))) - 1,"expression_list")
	
	pass

def p_unary_expression1(p):
	"unary_expression : postfix_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression2(p):
	"unary_expression : INC cast_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression3(p):
	"unary_expression : DEC cast_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression4(p):
	"unary_expression : ptr_operator cast_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression5(p):
	"unary_expression : suffix_decl_specified_scope star_ptr_operator cast_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression6(p):
	"unary_expression : '+' cast_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression7(p):
	"unary_expression : '-' cast_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression8(p):
	"unary_expression : '!' cast_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression9(p):
	"unary_expression : '~' cast_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression10(p):
	"unary_expression : SIZEOF unary_expression"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression11(p):
	"unary_expression : new_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression12(p):
	"unary_expression : global_scope new_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression13(p):
	"unary_expression : delete_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass

def p_unary_expression14(p):
	"unary_expression : global_scope delete_expression"
	add_children(len(list(filter(None, p[1:]))),"unary_expression")
	
	pass


def p_delete_expression(p):
	"delete_expression : DELETE cast_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,"delete")
	
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
	"new_initializer_opt : '(' expression_list_opt ')'"
	add_children(len(list(filter(None, p[1:]))),"new_initializer_opt")
	
	pass

#/*  cast-expression is generalised to support a [] as well as a () prefix. This covers the omission of DELETE[] which when
# *  followed by a parenthesised expression was ambiguous. It also covers the gcc indexed array initialisation for free.
# */

def p_cast_expression1(p):
	"cast_expression : unary_expression"
	add_children(len(list(filter(None, p[1:]))),"cast_expression")
	
	pass

def p_cast_expression2(p):
	"cast_expression : abstract_expression cast_expression"
	add_children(len(list(filter(None, p[1:]))),"cast_expression")
	
	pass

def p_pm_expression1(p):
	"pm_expression : cast_expression"
	add_children(len(list(filter(None, p[1:]))),"pm_expression")
	
	pass

def p_pm_expression2(p):
	"pm_expression : pm_expression DOT_STAR cast_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_pm_expression3(p):
	"pm_expression : pm_expression ARROW_STAR cast_expression"
	add_children(len(list(filter(None, p[1:]))) -1 ,p[2])
	
	pass

def p_multiplicative_expression1(p):
	"multiplicative_expression : pm_expression"
	add_children(len(list(filter(None, p[1:]))),"multiplicative_expression")
	
	pass

def p_multiplicative_expression2(p):
	"multiplicative_expression : multiplicative_expression star_ptr_operator pm_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_multiplicative_expression3(p):
	"multiplicative_expression : multiplicative_expression '/' pm_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 ,p[2])
	
	pass

def p_multiplicative_expression4(p):
	"multiplicative_expression : multiplicative_expression '%' pm_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_additive_expression1(p):
	"additive_expression : multiplicative_expression"
	add_children(len(list(filter(None, p[1:]))),"additive_expression")
	
	pass

def p_additive_expression2(p):
	"additive_expression : additive_expression '+' multiplicative_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 ,p[2])
	
	pass

def p_additive_expression3(p):
	"additive_expression : additive_expression '-' multiplicative_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 ,p[2])
	
	pass

def p_shift_expression1(p):
	"shift_expression : additive_expression"
	add_children(len(list(filter(None, p[1:]))),"shift_expression")
	
	pass

def p_shift_expression2(p):
	"shift_expression : shift_expression SHL additive_expression"
	add_children(len(list(filter(None, p[1:]))) -1 ,p[2])
	
	pass

def p_shift_expression3(p):
	"shift_expression : shift_expression SHR additive_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_relational_expression1(p):
	"relational_expression : shift_expression"
	add_children(len(list(filter(None, p[1:]))),"relational_expression")
	
	pass

def p_relational_expression2(p):
	"relational_expression : relational_expression '<' shift_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 ,p[2])
	
	pass

def p_relational_expression3(p):
	"relational_expression : relational_expression '>' shift_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 ,p[2])
	
	pass

def p_relational_expression4(p):
	"relational_expression : relational_expression LE shift_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_relational_expression5(p):
	"relational_expression : relational_expression GE shift_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_equality_expression1(p):
	"equality_expression : relational_expression"
	add_children(len(list(filter(None, p[1:]))),"equality_expression")
	
	pass

def p_equality_expression2(p):
	"equality_expression : equality_expression EQ relational_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_equality_expression3(p):
	"equality_expression : equality_expression NE relational_expression"
	add_children(len(list(filter(None, p[1:]))) - 1 , p[2])
	
	pass

def p_and_expression1(p):
	"and_expression : equality_expression"
	add_children(len(list(filter(None, p[1:]))),"and_expression")
	
	pass

def p_and_expression2(p):
	"and_expression : and_expression '&' equality_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_exclusive_or_expression1(p):
	"exclusive_or_expression : and_expression"
	add_children(len(list(filter(None, p[1:]))),"exclusive_or_expression")
	
	pass

def p_exclusive_or_expression2(p):
	"exclusive_or_expression : exclusive_or_expression '^' and_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_inclusive_or_expression1(p):
	"inclusive_or_expression : exclusive_or_expression"
	add_children(len(list(filter(None, p[1:]))),"inclusive_or_expression")
	
	pass

def p_inclusive_or_expression2(p):
	"inclusive_or_expression : inclusive_or_expression '|' exclusive_or_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_logical_and_expression1(p):
	"logical_and_expression : inclusive_or_expression"
	add_children(len(list(filter(None, p[1:]))),"logical_and_expression")
	
	pass

def p_logical_and_expression2(p):
	"logical_and_expression : logical_and_expression LOG_AND inclusive_or_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_logical_or_expression1(p):
	"logical_or_expression : logical_and_expression"
	add_children(len(list(filter(None, p[1:]))),"logical_or_expression")
	
	pass

def p_logical_or_expression2(p):
	"logical_or_expression : logical_or_expression LOG_OR logical_and_expression"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_conditional_expression1(p):
	"conditional_expression : logical_or_expression"
	add_children(len(list(filter(None, p[1:]))),"conditional_expression")
	
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
	
	pass

def p_assignment_expression2(p):
	"assignment_expression : logical_or_expression assignment_operator assignment_expression"
	add_children(len(list(filter(None, p[1:]))) -1 ,p[2])
	
	pass

def p_assignment_expression3(p):
	"assignment_expression : logical_or_expression '=' braced_initializer"
	add_children(len(list(filter(None, p[1:]))) - 1,p[2])
	
	pass

def p_assignment_expression4(p):
	"assignment_expression : throw_expression"
	add_children(len(list(filter(None, p[1:]))),"assignment_expression")
	
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
	
	pass

def p_expression1(p):
	"expression : assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"expression")
	
	pass

def p_expression2(p):
	"expression : expression_list ',' assignment_expression"
	
	add_children(len(list(filter(None, p[1:]))) - 1,"expression")
	
	pass

def p_constant_expression(p):
	"constant_expression : conditional_expression"
	add_children(len(list(filter(None, p[1:]))),"constant_expression")
	
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
	
	pass

def p_looped_statement1(p):
	"looped_statement : statement"
	add_children(len(list(filter(None, p[1:]))),"looped_statement")
	
	pass

def p_looped_statement2(p):
	"looped_statement : advance_search '+' looped_statement"
	create_children("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"looped_statement")
	
	pass

def p_looped_statement3(p):
	"looped_statement : advance_search '-'"
	create_children("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"looped_statement")
	
	pass

def p_statement1(p):
	"statement : control_statement"
	add_children(len(list(filter(None, p[1:]))),"statement")
	
	pass

def p_statement2(p):
	"statement : compound_statement"
	add_children(len(list(filter(None, p[1:]))),"statement")
	
	pass

def p_statement3(p):
	"statement : declaration_statement"
	add_children(len(list(filter(None, p[1:]))),"statement")
	
	pass

def p_statement4(p):
	"statement : try_block"
	add_children(len(list(filter(None, p[1:]))),"statement")
	
	pass

def p_control_statement1(p):
	"control_statement : labeled_statement"
	add_children(len(list(filter(None, p[1:]))),"control_statement")
	
	pass

def p_control_statement2(p):
	"control_statement : selection_statement"
	add_children(len(list(filter(None, p[1:]))),"control_statement")
	
	pass

def p_control_statement3(p):
	"control_statement : iteration_statement"
	add_children(len(list(filter(None, p[1:]))),"control_statement")
	
	pass

def p_control_statement4(p):
	"control_statement : jump_statement"
	add_children(len(list(filter(None, p[1:]))),"control_statement")
	
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
	
	pass

def p_compound_statement1(p):
	"compound_statement : '{' statement_seq_opt '}'"
	add_children(len(list(filter(None, p[1:])))- 2,"compound_statement")
	
	pass

def p_compound_statement2(p):
	"compound_statement : '{' statement_seq_opt looping_statement '#' bang error '}'"
	create_child("None",p[4])
	add_children(len(list(filter(None, p[1:]))) - 2,"compund_statement")
	
	pass

def p_statement_seq_opt1(p):
	"statement_seq_opt : empty"
	
	pass

def p_statement_seq_opt2(p):
	"statement_seq_opt : statement_seq_opt looping_statement"
	add_children(len(list(filter(None, p[1:]))),"statement_seq_opt")
	
	pass

def p_statement_seq_opt3(p):
	"statement_seq_opt : statement_seq_opt looping_statement '#' bang error ';'"
	create_child("None",p[3])
	create_child("None",p[6])
	add_children(len(list(filter(None, p[1:]))),"statement_seq_opt")
	
	pass

#/*
# *  The dangling else conflict is resolved to the innermost if.
# */

def p_selection_statement1(p):
	"selection_statement : IF '(' condition ')' looping_statement    %prec SHIFT_THERE"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))) -3,"selection_statement")
	
	pass

def p_selection_statement2(p):
	"selection_statement : IF '(' condition ')' looping_statement ELSE looping_statement"
	add_children(len(list(filter(None, p[1:]))) - 4,"Condition - If - Else")
	
	pass

def p_selection_statement3(p):
	"selection_statement : SWITCH '(' condition ')' looping_statement"
	add_children(len(list(filter(None, p[1:]))),p[1])
	
	pass

def p_condition_opt1(p):
	"condition_opt : empty"
	
	pass

def p_condition_opt2(p):
	"condition_opt : condition"
	add_children(len(list(filter(None, p[1:]))),"condition_opt")
	
	pass

def p_condition(p):
	"condition : parameter_declaration_list"
	add_children(len(list(filter(None, p[1:]))),"condition")
	
	pass

def p_iteration_statement1(p):
	"iteration_statement : WHILE '(' condition ')' looping_statement"
	add_children(len(list(filter(None, p[1:]))) - 3,"WHILE")
	
	pass

def p_iteration_statement2(p):
	"iteration_statement : DO looping_statement WHILE '(' expression ')' ';'"
	add_children(len(list(filter(None, p[1:]))) - 5,"DO - WHILE")
	
	pass

def p_iteration_statement3(p):
	"iteration_statement : FOR '(' for_init_statement condition_opt ';' expression_opt ')' looping_statement"
	add_children(len(list(filter(None, p[1:]))) - 4,"FOR")
	
	pass

def p_for_init_statement(p):
	"for_init_statement : simple_declaration"
	add_children(len(list(filter(None, p[1:]))),"for_init_statement")
	
	pass

def p_jump_statement1(p):
	"jump_statement : BREAK ';'"
	create_child("None", p[1])
	
	pass

def p_jump_statement2(p):
	"jump_statement : CONTINUE ';'"
	create_child("None", p[1])
	
	pass

def p_jump_statement3(p):
	"jump_statement : RETURN expression_opt ';'"
	if p[2] != '':
		add_children(1,"return")
	else:
		create_child("None", p[1])
	
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
	
	pass

#/*---------------------------------------------------------------------------------------------------
# * A.6 Declarations
# *---------------------------------------------------------------------------------------------------*/

def p_compound_declaration1(p):
	"compound_declaration : '{' nest declaration_seq_opt '}'"
	add_children(len(list(filter(None, p[1:]))) - 2,"compound_declaration")
	
	pass

def p_compound_declaration2(p):
	"compound_declaration : '{' nest declaration_seq_opt util looping_declaration '#' bang error '}'"
	create_child("None",p[5])
	add_children(len(list(filter(None, p[1:]))) - 2,"compound_declaration")
	
	pass

def p_declaration_seq_opt1(p):
	"declaration_seq_opt : empty"
	
	pass

def p_declaration_seq_opt2(p):
	"declaration_seq_opt : declaration_seq_opt util looping_declaration"
	print(p[:])
	add_children(len(list(filter(None, p[1:]))),"declaration_seq_opt")

	
	pass

def p_declaration_seq_opt3(p):
	"declaration_seq_opt : declaration_seq_opt util looping_declaration '#' bang error ';'"
	create_child("None",p[4])
	create_child("None",p[7])
	print("DECL 2 ")
	
	print(p[:])
	add_children(len(list(filter(None, p[1:]))),"declaration_seq_opt")
	
	pass

def p_looping_declaration(p):
	"looping_declaration : start_search1 looped_declaration"
	add_children(len(list(filter(None, p[1:]))),"looping_declaration")
	
	pass

def p_looped_declaration1(p):
	"looped_declaration : declaration"
	add_children(len(list(filter(None, p[1:]))),"looped_declaration")
	
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
	
	pass

def p_declaration2(p):
	"declaration : function_definition"
	add_children(len(list(filter(None, p[1:]))),"declaration")
	
	pass

def p_declaration5(p):
	"declaration : specialised_declaration"
	add_children(len(list(filter(None, p[1:]))),"declaration")
	
	pass

def p_specialised_declaration1(p):
	"specialised_declaration : linkage_specification"
	add_children(len(list(filter(None, p[1:]))),"specialised_declaration")
	
	pass

def p_specialised_declaration2(p):
	"specialised_declaration : namespace_definition"
	add_children(len(list(filter(None, p[1:]))),"specialised_declaration")
	
	pass


def p_block_declaration1(p):
	"block_declaration : simple_declaration"
	add_children(len(list(filter(None, p[1:]))),"block_declaration")
	
	pass

def p_block_declaration2(p):
	"block_declaration : specialised_block_declaration"
	add_children(len(list(filter(None, p[1:]))),"block_declaration")
	
	pass

def p_specialised_block_declaration1(p):
	"specialised_block_declaration : asm_definition"
	add_children(len(list(filter(None, p[1:]))),"specialised_block_declaration")
	
	pass

def p_specialised_block_declaration2(p):
	"specialised_block_declaration : namespace_alias_definition"
	add_children(len(list(filter(None, p[1:]))),"specialised_block_declaration")
	
	pass

def p_specialised_block_declaration3(p):
	"specialised_block_declaration : using_declaration"
	add_children(len(list(filter(None, p[1:]))),"specialised_block_declaration")
	
	pass

def p_specialised_block_declaration4(p):
	"specialised_block_declaration : using_directive"
	add_children(len(list(filter(None, p[1:]))),"specialised_block_declaration")
	
	pass

def p_simple_declaration1(p):
	"simple_declaration : ';'"
	
	pass

def p_simple_declaration2(p):
	"simple_declaration : init_declaration ';'"
	add_children(len(list(filter(None, p[1:]))) -1,"simple_declaration")
	
	pass

def p_simple_declaration3(p):
	"simple_declaration : init_declarations ';'"
	add_children(len(list(filter(None, p[1:]))) - 1,"simple_declaration")
	
	pass

def p_simple_declaration4(p):
	"simple_declaration : decl_specifier_prefix simple_declaration"
	add_children(len(list(filter(None, p[1:]))),"simple_declaration")
	
	pass

#/*  A decl-specifier following a ptr_operator provokes a shift-reduce conflict for
# *      * const name
# *  which is resolved in favour of the pointer, and implemented by providing versions
# *  of decl-specifier guaranteed not to start with a cv_qualifier.


def p_suffix_built_in_decl_specifier_raw1(p):
	"suffix_built_in_decl_specifier_raw : built_in_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"suffix_built_in_decl_specifier_raw ")
	
	pass

def p_suffix_built_in_decl_specifier_raw2(p):
	"suffix_built_in_decl_specifier_raw : suffix_built_in_decl_specifier_raw built_in_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"suffix_built_in_decl_specifier_raw ")
	
	pass

def p_suffix_built_in_decl_specifier_raw3(p):
	"suffix_built_in_decl_specifier_raw : suffix_built_in_decl_specifier_raw decl_specifier_suffix"
	add_children(len(list(filter(None, p[1:]))),"suffix_built_in_decl_specifier_raw ")
	
	pass

def p_suffix_built_in_decl_specifier1(p):
	"suffix_built_in_decl_specifier : suffix_built_in_decl_specifier_raw"
	add_children(len(list(filter(None, p[1:]))),"suffix_built_in_decl_specifier ")
	
	pass


def p_suffix_named_decl_specifier1(p):
	"suffix_named_decl_specifier : scoped_id"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifier")
	
	pass

def p_suffix_named_decl_specifier2(p):
	"suffix_named_decl_specifier : elaborate_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifier")
	
	pass

def p_suffix_named_decl_specifier3(p):
	"suffix_named_decl_specifier : suffix_named_decl_specifier decl_specifier_suffix"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifier")
	
	pass

def p_suffix_named_decl_specifier_bi1(p):
	"suffix_named_decl_specifier_bi : suffix_named_decl_specifier"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifier_bi")
	
	pass

def p_suffix_named_decl_specifier_bi2(p):
	"suffix_named_decl_specifier_bi : suffix_named_decl_specifier suffix_built_in_decl_specifier_raw"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifier_bi")
	
	pass

def p_suffix_named_decl_specifiers1(p):
	"suffix_named_decl_specifiers : suffix_named_decl_specifier_bi"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifiers")
	
	pass

def p_suffix_named_decl_specifiers2(p):
	"suffix_named_decl_specifiers : suffix_named_decl_specifiers suffix_named_decl_specifier_bi"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifiers")
	
	pass

def p_suffix_named_decl_specifiers_sf1(p):
	"suffix_named_decl_specifiers_sf : scoped_special_function_id"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifiers_sf")
	
	pass

def p_suffix_named_decl_specifiers_sf2(p):
	"suffix_named_decl_specifiers_sf : suffix_named_decl_specifiers"
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifiers_sf")
	
	pass

def p_suffix_named_decl_specifiers_sf3(p):
	"suffix_named_decl_specifiers_sf : suffix_named_decl_specifiers scoped_special_function_id"
	print(p[:])
	print(len(list(filter(None, p[1:]))))
	add_children(len(list(filter(None, p[1:]))),"suffix_named_decl_specifiers_sf")
	
	pass

def p_suffix_decl_specified_ids1(p):
	"suffix_decl_specified_ids : suffix_built_in_decl_specifier"
	add_children(len(list(filter(None, p[1:]))),"suffix_decl_specified_ids")
	
	pass

def p_suffix_decl_specified_ids2(p):
	"suffix_decl_specified_ids : suffix_built_in_decl_specifier suffix_named_decl_specifiers_sf"
	add_children(len(list(filter(None, p[1:]))),"suffix_decl_specified_ids")
	
	pass

def p_suffix_decl_specified_ids3(p):
	"suffix_decl_specified_ids : suffix_named_decl_specifiers_sf"
	add_children(len(list(filter(None, p[1:]))),"suffix_decl_specified_ids")
	
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
	
	pass

def p_decl_specifier_affix2(p):
	"decl_specifier_affix : function_specifier"
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_affix")
	
	pass

def p_decl_specifier_affix3(p):
	"decl_specifier_affix : FRIEND"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_affix")
	
	pass

def p_decl_specifier_affix4(p):
	"decl_specifier_affix : TYPEDEF"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_affix")
	
	pass

def p_decl_specifier_affix5(p):
	"decl_specifier_affix : cv_qualifier"
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_affix")
	
	pass

def p_decl_specifier_suffix(p):
	"decl_specifier_suffix : decl_specifier_affix"
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_suffix")
	
	pass

def p_decl_specifier_prefix1(p):
	"decl_specifier_prefix : decl_specifier_affix"
	add_children(len(list(filter(None, p[1:]))),"decl_specifier_prefix")
	
	pass


def p_storage_class_specifier1(p):
	'''storage_class_specifier : REGISTER
							   | STATIC
							   | MUTABLE'''
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"storage_class_specifier")
	
	pass

def p_storage_class_specifier2(p):
	"storage_class_specifier : EXTERN                  %prec SHIFT_THERE"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"storage_class_specifier")
	
	pass

def p_storage_class_specifier3(p):
	"storage_class_specifier : AUTO"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"storage_class_specifier")
	
	pass

def p_function_specifier1(p):
	"function_specifier : EXPLICIT"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"function_specifier")
	
	pass

def p_function_specifier2(p):
	"function_specifier : INLINE"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"function_specifier")
	
	pass

def p_function_specifier3(p):
	"function_specifier : VIRTUAL"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"function_specifier")
	
	pass

def p_type_specifier1(p):
	"type_specifier : simple_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"type_specifier")
	
	pass

def p_type_specifier2(p):
	"type_specifier : elaborate_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"type_specifier")
	
	pass

def p_type_specifier3(p):
	"type_specifier : cv_qualifier"
	add_children(len(list(filter(None, p[1:]))),"type_specifier")
	
	pass

def p_elaborate_type_specifier1(p):
	"elaborate_type_specifier : class_specifier"
	add_children(len(list(filter(None, p[1:]))),"elaborate_type_specifier")
	
	pass

def p_elaborate_type_specifier2(p):
	"elaborate_type_specifier : enum_specifier"
	add_children(len(list(filter(None, p[1:]))),"elaborate_type_specifier")
	
	pass

def p_elaborate_type_specifier3(p):
	"elaborate_type_specifier : elaborated_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"elaborate_type_specifier")
	
	pass


def p_simple_type_specifier1(p):
	"simple_type_specifier : scoped_id"
	add_children(len(list(filter(None, p[1:]))),"simple_type_specifier")
	
	pass

def p_simple_type_specifier2(p):
	"simple_type_specifier : built_in_type_specifier"
	add_children(len(list(filter(None, p[1:]))),"simple_type_specifier")
	
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
	
	pass

def p_elaborated_type_specifier1(p):
	"elaborated_type_specifier : elaborated_class_specifier"
	add_children(len(list(filter(None, p[1:]))),"elaborated_type_specifier")
	
	pass

def p_elaborated_type_specifier2(p):
	"elaborated_type_specifier : elaborated_enum_specifier"
	add_children(len(list(filter(None, p[1:]))),"elaborated_type_specifier")
	
	pass

def p_elaborated_type_specifier3(p):
	"elaborated_type_specifier : TYPENAME scoped_id"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"elaborated_type_specifier")
	
	pass

def p_elaborated_enum_specifier(p):
	"elaborated_enum_specifier : ENUM scoped_id               %prec SHIFT_THERE"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"elaborated_type_specifier")
	
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
	"enumerator_clause : '{' enumerator_list_ecarb"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"enumerator_clause")
	
	pass

def p_enumerator_clause2(p):
	"enumerator_clause : '{' enumerator_list enumerator_list_ecarb"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"enumerator_clause")
	
	pass

def p_enumerator_clause3(p):
	"enumerator_clause : '{' enumerator_list ',' enumerator_definition_ecarb"
	create_child("None",p[1])
	
	add_children(len(list(filter(None, p[1:]))) - 1,"enumerator_clause")
	
	pass

def p_enumerator_list_ecarb1(p):
	"enumerator_list_ecarb : '}'"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"enumerator_list_ecarb")
	
	pass

def p_enumerator_list_ecarb2(p):
	"enumerator_list_ecarb : bang error '}'"
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"enumerator_list_ecarb")
	
	pass

def p_enumerator_definition_ecarb1(p):
	"enumerator_definition_ecarb : '}'"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"enumerator_definition_ecarb")
	
	pass

def p_enumerator_definition_ecarb2(p):
	"enumerator_definition_ecarb : bang error '}'"
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"enumerator_definition_ecarb")
	
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
	"namespace_definition : NAMESPACE scoped_id compound_declaration"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"namespace_definition")
	
	pass

def p_namespace_definition2(p):
	"namespace_definition : NAMESPACE compound_declaration"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"namespace_definition")
	
	pass

def p_namespace_alias_definition(p):
	"namespace_alias_definition : NAMESPACE scoped_id '=' scoped_id ';'"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))) - 2,p[3])
	
	pass

def p_using_declaration1(p):
	"using_declaration : USING declarator_id ';'"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))) - 1,"using_declaration")
	
	pass
1111
def p_using_declaration2(p):
	"using_declaration : USING TYPENAME declarator_id ';'"
	create_child("None",p[1])
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))) - 1,"using_declaration")
	
	pass

def p_using_directive(p):
	"using_directive : USING NAMESPACE scoped_id ';'"
	create_child("None",p[1])
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))) - 1,"using_directive")
	
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
	
	pass

def p_init_declarations2(p):
	"init_declarations : init_declarations ',' init_declaration"
	
	add_children(len(list(filter(None, p[1:]))) - 1,"init_declarations")
	
	pass

def p_init_declaration(p):
	"init_declaration : assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"init_declaration")
	
	pass

def p_star_ptr_operator1(p):
	"star_ptr_operator : '*'"
	
	pass

def p_star_ptr_operator2(p):
	"star_ptr_operator : star_ptr_operator cv_qualifier"
	add_children(len(list(filter(None, p[1:]))),"star_ptr_operator")
	
	pass

def p_nested_ptr_operator1(p):
	"nested_ptr_operator : star_ptr_operator"
	add_children(len(list(filter(None, p[1:]))),"nested_ptr_operator")
	
	pass

def p_nested_ptr_operator2(p):
	"nested_ptr_operator : id_scope nested_ptr_operator"
	add_children(len(list(filter(None, p[1:]))),"nested_ptr_operator")
	
	pass

def p_ptr_operator1(p):
	"ptr_operator : '&'"
	create_child("ptr_operator",p[1])
	
	pass

def p_ptr_operator2(p):
	"ptr_operator : nested_ptr_operator"
	add_children(len(list(filter(None, p[1:]))),"ptr_operator")
	
	pass

def p_ptr_operator3(p):
	"ptr_operator : global_scope nested_ptr_operator"
	add_children(len(list(filter(None, p[1:]))),"ptr_operator")
	
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
	
	pass

def p_parenthesis_clause2(p):
	"parenthesis_clause : parameters_clause cv_qualifier_seq_opt exception_specification"
	add_children(len(list(filter(None, p[1:]))),"parenthesis_clause")
	
	pass

def p_parameters_clause(p):
	"parameters_clause : '(' parameter_declaration_clause ')'"
	add_children(len(list(filter(None, p[1:]))) - 2,"paremeters_clause")
	pass

def p_parameter_declaration_clause1(p):
	"parameter_declaration_clause : empty"
	
	pass

def p_parameter_declaration_clause2(p):
	"parameter_declaration_clause : parameter_declaration_list"
	add_children(len(list(filter(None, p[1:]))),"parameter_declaration_clause")
	
	pass

def p_parameter_declaration_clause3(p):
	"parameter_declaration_clause : parameter_declaration_list ELLIPSIS"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"parameter_declaration_clause")
	
	pass

def p_parameter_declaration_list1(p):
	"parameter_declaration_list : parameter_declaration"
	add_children(len(list(filter(None, p[1:]))),"parameter_declaration_list")
	
	pass

def p_parameter_declaration_list2(p):
	"parameter_declaration_list : parameter_declaration_list ',' parameter_declaration"
	
	add_children(len(list(filter(None, p[1:]))) -1,"parameter_declaration_list")
	
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
	
	pass

def p_parameter_declaration2(p):
	"parameter_declaration : special_parameter_declaration"
	add_children(len(list(filter(None, p[1:]))),"parameter_declaration")
	
	pass

def p_parameter_declaration3(p):
	"parameter_declaration : decl_specifier_prefix parameter_declaration"
	add_children(len(list(filter(None, p[1:]))),"parameter_declaration")
	
	pass


#/*  function_definition includes constructor, destructor, implicit int definitions too.
# *  A local destructor is successfully parsed as a function-declaration but the ~ was treated as a unary operator.
# *  constructor_head is the prefix ambiguity between a constructor and a member-init-list starting with a bit-field.
# */

def p_function_definition1(p):
	"function_definition : ctor_definition"
	add_children(len(list(filter(None, p[1:]))),"function_definition")
	
	pass

def p_function_definition2(p):
	"function_definition : func_definition"
	add_children(len(list(filter(None, p[1:]))),"function_definition")
	
	pass

def p_func_definition1(p):
	"func_definition : assignment_expression function_try_block"
	add_children(len(list(filter(None, p[1:]))),"func_definition")
	
	pass

def p_func_definition2(p):
	"func_definition : assignment_expression function_body"
	add_children(len(list(filter(None, p[1:]))),"func_definition")
	
	pass

def p_func_definition3(p):
	"func_definition : decl_specifier_prefix func_definition"
	add_children(len(list(filter(None, p[1:]))),"func_definition")
	
	pass

def p_ctor_definition1(p):
	"ctor_definition : constructor_head function_try_block"
	add_children(len(list(filter(None, p[1:]))),"ctor_definition")
	
	pass

def p_ctor_definition2(p):
	"ctor_definition : constructor_head function_body"
	add_children(len(list(filter(None, p[1:]))),"ctor_definition")
	
	pass

def p_ctor_definition3(p):
	"ctor_definition : decl_specifier_prefix ctor_definition"
	add_children(len(list(filter(None, p[1:]))),"ctor_definition")
	
	pass

def p_constructor_head1(p):
	"constructor_head : bit_field_init_declaration"
	add_children(len(list(filter(None, p[1:]))),"constructor_head")
	
	pass

def p_constructor_head2(p):
	"constructor_head : constructor_head ',' assignment_expression"
	
	add_children(len(list(filter(None, p[1:]))) - 1,"constructor_head")
	
	pass

def p_function_try_block(p):
	"function_try_block : TRY function_block handler_seq"
	create_child("None",p[1])
	add_children(len(list(filter(None, p[1:]))),"function_try_block")
	
	pass

def p_function_block(p):
	"function_block : ctor_initializer_opt function_body"
	add_children(len(list(filter(None, p[1:]))),"function_block")
	
	pass

def p_function_body(p):
	"function_body : compound_statement"
	add_children(len(list(filter(None, p[1:]))),"function_body")
	
	pass

#/*
# *  An = initializer looks like an extended assignment_expression.
# *  An () initializer looks like a function call.
# *  initializer is therefore flattened into its generalised customers.


def p_initializer_clause1(p):
	"initializer_clause : assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"initializer_clause")
	
	pass

def p_initializer_clause2(p):
	"initializer_clause : braced_initializer"
	add_children(len(list(filter(None, p[1:]))),"initializer_clause")
	
	pass

def p_braced_initializer1(p):
	"braced_initializer : '{' initializer_list '}'"
	add_children(len(list(filter(None, p[1:]))) - 2,"braced_initializer")
	
	pass

def p_braced_initializer2(p):
	"braced_initializer : '{' initializer_list ',' '}'"
	add_children(len(list(filter(None, p[1:]))) - 3,"braced_initializer")
	
	pass

def p_braced_initializer3(p):
	"braced_initializer : '{' '}'"
	create_child("None",p[1])
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"braced_initializer")
	
	pass

def p_braced_initializer4(p):
	"braced_initializer : '{' looping_initializer_clause '#' bang error '}'"
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))) - 2,"braced_initializer")
	
	pass

def p_braced_initializer5(p):
	"braced_initializer : '{' initializer_list ',' looping_initializer_clause '#' bang error '}'"
	
	create_child("None",p[5])
	add_children(len(list(filter(None, p[1:]))) - 3,"braced_initializer")
	
	pass

def p_initializer_list1(p):
	"initializer_list : looping_initializer_clause"
	add_children(len(list(filter(None, p[1:]))),"initializer_list")
	
	pass

def p_initializer_list2(p):
	"initializer_list : initializer_list ',' looping_initializer_clause"
	
	add_children(len(list(filter(None, p[1:])))  -1 ,"initializer_list")
	
	pass

def p_looping_initializer_clause(p):
	"looping_initializer_clause : start_search looped_initializer_clause"
	add_children(len(list(filter(None, p[1:]))),"looping_initializer_clause")
	
	pass

def p_looped_initializer_clause1(p):
	"looped_initializer_clause : initializer_clause"
	add_children(len(list(filter(None, p[1:]))),"looped_initializer_clause")
	
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
	
	pass

def p_elaborated_class_specifier2(p):
	"elaborated_class_specifier : class_key scoped_id colon_mark error"
	add_children(len(list(filter(None, p[1:]))),"elaborated_class_specifier")
	
	pass

def p_class_specifier_head1(p):
	"class_specifier_head : class_key scoped_id colon_mark base_specifier_list '{'"
	create_child("None",p[5])
	add_children(len(list(filter(None, p[1:]))),"class_specifier_head")
	
	pass

def p_class_specifier_head2(p):
	"class_specifier_head : class_key ':' base_specifier_list '{'"
	create_child("None",p[2])
	create_child("None",p[4])
	add_children(len(list(filter(None, p[1:]))),"class_specifier_head")
	
	pass

def p_class_specifier_head3(p):
	"class_specifier_head : class_key scoped_id '{'"
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"class_specifier_head")
	
	pass

def p_class_specifier_head4(p):
	"class_specifier_head : class_key '{'"
	print("c3")
	print(p[:])
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"class_specifier_head")
	
	pass

def p_class_key(p):
	'''class_key : CLASS
				 | STRUCT
				 | UNION'''
	create_child("class_key",p[1])
	
	pass

def p_class_specifier1(p):
	"class_specifier : class_specifier_head member_specification_opt '}'"
	create_child("None",p[3])
	print("c2")
	print(p[:])
	print(len(list(filter(None, p[1:]))))
	add_children(len(list(filter(None, p[1:]))),"class_specifier")
	
	pass

def p_class_specifier2(p):
	"class_specifier : class_specifier_head member_specification_opt util looping_member_declaration '#' bang error '}'"
	create_child("None",p[5])
	create_child("None",p[8])
	print("c1")
	print(p[:])
	add_children(len(list(filter(None, p[1:]))),"class_specifier")
	
	pass

def p_member_specification_opt1(p):
	"member_specification_opt : empty"
	
	pass

def p_member_specification_opt2(p):
	"member_specification_opt : member_specification_opt util looping_member_declaration"
	print(p[:])
	print(len(list(filter(None, p[1:]))))
	add_children(len(list(filter(None, p[1:]))),"member_specification_opt")
	
	pass

def p_member_specification_opt3(p):
	"member_specification_opt : member_specification_opt util looping_member_declaration '#' bang error ';'"
	create_child("None",p[4])
	add_children(len(list(filter(None, p[1:]))) - 1,"member_specification_opt")
	
	pass

def p_looping_member_declaration(p):
	"looping_member_declaration : start_search looped_member_declaration"
	add_children(len(list(filter(None, p[1:]))),"looping_member_declaration")
	
	pass

def p_looped_member_declaration1(p):
	"looped_member_declaration : member_declaration"
	add_children(len(list(filter(None, p[1:]))),"looped_member_declaration")
	
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
	
	pass

def p_member_declaration2(p):
	"member_declaration : simple_member_declaration"
	add_children(len(list(filter(None, p[1:]))),"member_declaration")
	
	pass

def p_member_declaration3(p):
	"member_declaration : function_definition"
	add_children(len(list(filter(None, p[1:]))),"member_declaration")
	
	pass

def p_member_declaration4(p):
	"member_declaration : using_declaration"
	add_children(len(list(filter(None, p[1:]))),"member_declaration")
	
	pass


def p_simple_member_declaration1(p):
	"simple_member_declaration : ';'"
	create_child("simple_member_declaration",p[1])
	
	pass

def p_simple_member_declaration2(p):
	"simple_member_declaration : assignment_expression ';'"
	add_children(len(list(filter(None, p[1:]))) - 1,"simple_member_declaration")
	
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
	
	pass

def p_simple_member_declaration5(p):
	"simple_member_declaration : decl_specifier_prefix simple_member_declaration"
	add_children(len(list(filter(None, p[1:]))),"simple_member_declaration")
	
	pass

def p_member_init_declarations1(p):
	"member_init_declarations : assignment_expression ',' member_init_declaration"
	
	add_children(len(list(filter(None, p[1:]))) -1 ,"member_init_declarations")
	
	pass

def p_member_init_declarations2(p):
	"member_init_declarations : constructor_head ',' bit_field_init_declaration"
	
	add_children(len(list(filter(None, p[1:]))) - 1,"member_init_declarations")
	
	pass

def p_member_init_declarations3(p):
	"member_init_declarations : member_init_declarations ',' member_init_declaration"
	
	add_children(len(list(filter(None, p[1:]))) - 1,"member_init_declarations")
	
	pass

def p_member_init_declaration1(p):
	"member_init_declaration : assignment_expression"
	add_children(len(list(filter(None, p[1:]))),"member_init_declaration")
	
	pass

def p_member_init_declaration2(p):
	"member_init_declaration : bit_field_init_declaration"
	add_children(len(list(filter(None, p[1:]))),"member_init_declaration")
	
	pass

def p_accessibility_specifier(p):
	"accessibility_specifier : access_specifier ':'"
	create_child("None",p[2])
	add_children(len(list(filter(None, p[1:]))),"accessibility_specifier")
	
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
	create_child("acces_specifier",p[1])
	
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
	"mem_initializer : mem_initializer_id '(' expression_list_opt ')'"
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
	print(p[:])
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
	"handler : CATCH '(' exception_declaration ')' compound_statement"
	add_children(len(list(filter(None, p[1:]))),"Catch - exception")
	
	pass

def p_exception_declaration(p):
	"exception_declaration : parameter_declaration"
	add_children(len(list(filter(None, p[1:]))),"exception_declaration")
	
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
	"exception_specification : THROW '(' ')'"
	create_child("None",p[1])
	create_child("None",p[2])
	create_child("None",p[3])
	add_children(len(list(filter(None, p[1:]))),"exception_specification")
	
	pass

def p_exception_specification2(p):
	"exception_specification : THROW '(' type_id_list ')'"
	create_child("None",p[1])
	create_child("None",p[2])
	create_child("None",p[4])
	add_children(len(list(filter(None, p[1:]))),"exception_specification")
	
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
	#add_children(0,"bang")
	
	pass
'''
#def p_mark(p):
#    "mark : empty"
#    
	pass
'''
def p_nest(p):
	"nest : empty"
	#add_children(0,"nest")
	
	pass

def p_start_search(p):
	"start_search : empty"
	#add_children(0,"start_search")
	
	pass

def p_start_search1(p):
	"start_search1 : empty"
	#add_children(0,"start_search")
	
	pass

def p_util(p):
	"util : empty"
	#add_children(0,"util")
	
	pass

def p_empty(p):
	'empty : '
	
	pass

# Error rule for syntax errors
def p_error(p):
	print("Syntax error in input !",p)
   # print("Syntax error in line !",lex.cpp_scanner.lexer.lineno)
# Build the parser

# Build the lexer and try it out
if __name__ == "__main__":
	#import logging
	#logging.basicConfig(
	#    level = logging.DEBUG,
	#    filename = "parselog.txt",
	#    filemode = "w",
	#    format = "%(filename)10s:%(lineno)4d:%(message)s"
	#)
	#log = logging.getLogger('ply')

	parser = yacc.yacc(errorlog=yacc.NullLogger())
	#if(len(sys.argv) == 2):
	#	filename = sys.argv[1]
	#else:
	#	filename = "../tests/test5	.cpp"
	#a = open(filename)
	#data = a.read()
	data = 	'''
	
	int main()
	{
	int x[5] = {1,1,1,1,1,1};
	for(i=0;i<8;i--)
	x = y;
	
	return ; 
	} 
	'''
	yacc.parse(data, lexer=lex.cpp_scanner.lexer)
	graph.write_jpeg('parse_tree.jpeg')
	graph.write_dot('parse_tree.dot')
	print(graph.to_string())
