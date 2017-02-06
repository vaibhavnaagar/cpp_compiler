# -----------------------------------------------------------------------------
# cpp_parse.py
#
# Parser for C++.  Based on the grammar in ....
# -----------------------------------------------------------------------------

# Note: A character literal must be enclosed in quotes such as '+'. In addition, if literals are used, they must be declared in the corresponding lex file through the use of a special literals declaration.
# Literals.  Should be placed in module given to lex()
# literals = ['+','-','*','/' ]

import sys
import cpp_lex as lex
import ply.yacc as yacc

# Get the token map
tokens = lex.tokens

start = 'translation_unit'

#*----------------------------------------------------------------------
#* Context-dependent identifiers.
#*----------------------------------------------------------------------

def p_typedef_name(p):
# 	/* identifier */
	"""typedef_name : TYPEDEF_NAME
						"""
	pass


def p_namespace_name(p):
	"""namespace_name : original_namespace_name
						| namespace_alias
						"""
	pass


def p_original_namespace_name(p):
# 	/* identifier */
	"""original_namespace_name : NAMESPACE_NAME
						"""
	pass


def p_namespace_alias(p):
# 	/* identifier */
	"""namespace_alias : NAMESPACE_NAME
						"""
	pass


def p_class_name(p):
# 	/* identifier */
	"""class_name : CLASS_NAME
						| template_id
						"""
	pass


def p_enum_name(p):
# 	/* identifier */
	"""enum_name : ENUM_NAME
						"""
	pass


def p_template_name(p):
# 	/* identifier */
	"""template_name : TEMPLATE_NAME
						"""
	pass


# /*----------------------------------------------------------------------
#  * Lexical elements.
#  *----------------------------------------------------------------------*/
def p_identifier(p):
	"""identifier : IDENTIFIER
						"""
	pass


def p_literal(p):
	"""literal : integer_literal
						| character_literal
						| floating_literal
						| string_literal
						| boolean_literal
						"""
	pass


def p_integer_literal(p):
	"""integer_literal : INTEGER
						"""
	pass


def p_character_literal(p):
	"""character_literal : CHARACTER
						"""
	pass


def p_floating_literal(p):
	"""floating_literal : FLOATING
						"""
	pass


def p_string_literal(p):
	"""string_literal : STRING
						"""
	pass


def p_boolean_literal(p):
	"""boolean_literal : TRUE
						| FALSE
						"""
	pass


# /*----------------------------------------------------------------------
#  * Translation unit.
#  *----------------------------------------------------------------------*/
def p_translation_unit(p):
	"""translation_unit : declaration_seq_opt
						"""
	pass


# /*----------------------------------------------------------------------
#  * Expressions.
#  *----------------------------------------------------------------------*/
def p_primary_expression(p):
	"""primary_expression : literal
						| THIS
						| COLONCOLON identifier
						| COLONCOLON operator_function_id
						| COLONCOLON qualified_id
						| '(' expression ')'
						| id_expression
						"""
	pass


def p_id_expression(p):
	"""id_expression : unqualified_id
						| qualified_id
						"""
	pass


def p_unqualified_id(p):
	"""unqualified_id : identifier
						| operator_function_id
						| conversion_function_id
						| '~' class_name
						| template_id
						"""
	pass


def p_qualified_id(p):
	"""qualified_id : nested_name_specifier TEMPLATE_opt unqualified_id
						"""
	pass


def p_nested_name_specifier(p):
	"""nested_name_specifier : class_or_namespace_name COLONCOLON nested_name_specifier_opt
						"""
	pass


def p_class_or_namespace_name(p):
	"""class_or_namespace_name : class_name
						| namespace_name
						"""
	pass


def p_postfix_expression(p):
	"""postfix_expression : primary_expression
						| postfix_expression '[' expression ']'
						| postfix_expression '(' expression_list_opt ')'
						| simple_type_specifier '(' expression_list_opt ')'
						| postfix_expression '.' TEMPLATE_opt COLONCOLON_opt id_expression
						| postfix_expression ARROW TEMPLATE_opt COLONCOLON_opt id_expression
						| postfix_expression '.' pseudo_destructor_name
						| postfix_expression ARROW pseudo_destructor_name
						| postfix_expression PLUSPLUS
						| postfix_expression MINUSMINUS
						| DYNAMIC_CAST '<' type_id '>' '(' expression ')'
						| STATIC_CAST '<' type_id '>' '(' expression ')'
						| REINTERPRET_CAST '<' type_id '>' '(' expression ')'
						| CONST_CAST '<' type_id '>' '(' expression ')'
						| TYPEID '(' expression ')'
						| TYPEID '(' type_id ')'
						"""
	pass


def p_expression_list(p):
	"""expression_list : assignment_expression
						| expression_list ',' assignment_expression
						"""
	pass


def p_pseudo_destructor_name(p):
	"""pseudo_destructor_name : COLONCOLON_opt nested_name_specifier_opt type_name COLONCOLON '~' type_name
						| COLONCOLON_opt nested_name_specifier_opt '~' type_name
						"""
	pass


def p_unary_expression(p):
	"""unary_expression : postfix_expression
						| PLUSPLUS cast_expression
						| MINUSMINUS cast_expression
						| unary_operator cast_expression
						| SIZEOF unary_expression
						| SIZEOF '(' type_id ')'
						| new_expression
						| delete_expression
						"""
	pass


def p_unary_operator(p):
	"""unary_operator : '*'
						| '&'
						| '+'
						| '-'
						| '!'
						| '~'
						"""
	pass


def p_new_expression(p):
	"""new_expression : COLONCOLON_opt NEW new_placement_opt new_type_id new_initializer_opt
						| COLONCOLON_opt NEW new_placement_opt '(' type_id ')' new_initializer_opt
						"""
	pass


def p_new_placement(p):
	"""new_placement : '(' expression_list ')'
						"""
	pass


def p_new_type_id(p):
	"""new_type_id : type_specifier_seq new_declarator_opt
						"""
	pass


def p_new_declarator(p):
	"""new_declarator : ptr_operator new_declarator_opt
						| direct_new_declarator
						"""
	pass


def p_direct_new_declarator(p):
	"""direct_new_declarator : '[' expression ']'
						| direct_new_declarator '[' constant_expression ']'
						"""
	pass


def p_new_initializer(p):
	"""new_initializer : '(' expression_list_opt ')'
						"""
	pass


def p_delete_expression(p):
	"""delete_expression : COLONCOLON_opt DELETE cast_expression
						| COLONCOLON_opt DELETE '[' ']' cast_expression
						"""
	pass


def p_cast_expression(p):
	"""cast_expression : unary_expression
						| '(' type_id ')' cast_expression
						"""
	pass


def p_pm_expression(p):
	"""pm_expression : cast_expression
						| pm_expression DOTSTAR cast_expression
						| pm_expression ARROWSTAR cast_expression
						"""
	pass


def p_multiplicative_expression(p):
	"""multiplicative_expression : pm_expression
						| multiplicative_expression '*' pm_expression
						| multiplicative_expression '/' pm_expression
						| multiplicative_expression '%' pm_expression
						"""
	pass


def p_additive_expression(p):
	"""additive_expression : multiplicative_expression
						| additive_expression '+' multiplicative_expression
						| additive_expression '-' multiplicative_expression
						"""
	pass


def p_shift_expression(p):
	"""shift_expression : additive_expression
						| shift_expression SL additive_expression
						| shift_expression SR additive_expression
						"""
	pass


def p_relational_expression(p):
	"""relational_expression : shift_expression
						| relational_expression '<' shift_expression
						| relational_expression '>' shift_expression
						| relational_expression LTEQ shift_expression
						| relational_expression GTEQ shift_expression
						"""
	pass


def p_equality_expression(p):
	"""equality_expression : relational_expression
						| equality_expression EQ relational_expression
						| equality_expression NOTEQ relational_expression
						"""
	pass


def p_and_expression(p):
	"""and_expression : equality_expression
						| and_expression '&' equality_expression
						"""
	pass


def p_exclusive_or_expression(p):
	"""exclusive_or_expression : and_expression
						| exclusive_or_expression '^' and_expression
						"""
	pass


def p_inclusive_or_expression(p):
	"""inclusive_or_expression : exclusive_or_expression
						| inclusive_or_expression '|' exclusive_or_expression
						"""
	pass


def p_logical_and_expression(p):
	"""logical_and_expression : inclusive_or_expression
						| logical_and_expression ANDAND inclusive_or_expression
						"""
	pass


def p_logical_or_expression(p):
	"""logical_or_expression : logical_and_expression
						| logical_or_expression OROR logical_and_expression
						"""
	pass


def p_conditional_expression(p):
	"""conditional_expression : logical_or_expression
						| logical_or_expression  '?' expression ':' assignment_expression
						"""
	pass


def p_assignment_expression(p):
	"""assignment_expression : conditional_expression
						| logical_or_expression assignment_operator assignment_expression
						| throw_expression
						"""
	pass


def p_assignment_operator(p):
	"""assignment_operator : '='
						| MULEQ
						| DIVEQ
						| MODEQ
						| ADDEQ
						| SUBEQ
						| SREQ
						| SLEQ
						| ANDEQ
						| XOREQ
						| OREQ
						"""
	pass


def p_expression(p):
	"""expression : assignment_expression
						| expression ',' assignment_expression
						"""
	pass


def p_constant_expression(p):
	"""constant_expression : conditional_expression
						"""
	pass


# /*----------------------------------------------------------------------
#  * Statements.
#  *----------------------------------------------------------------------*/
def p_statement(p):
	"""statement : labeled_statement
						| expression_statement
						| compound_statement
						| selection_statement
						| iteration_statement
						| jump_statement
						| declaration_statement
						| try_block
						"""
	pass


def p_labeled_statement(p):
	"""labeled_statement : identifier ':' statement
						| CASE constant_expression ':' statement
						| DEFAULT ':' statement
						"""
	pass


def p_expression_statement(p):
	"""expression_statement : expression_opt ';'
						"""
	pass


def p_compound_statement(p):
	"""compound_statement : '{' statement_seq_opt '}'
						"""
	pass


def p_statement_seq(p):
	"""statement_seq : statement
						| statement_seq statement
						"""
	pass


def p_selection_statement(p):
	"""selection_statement : IF '(' condition ')' statement
						| IF '(' condition ')' statement ELSE statement
						| SWITCH '(' condition ')' statement
						"""
	pass


def p_condition(p):
	"""condition : expression
						| type_specifier_seq declarator '=' assignment_expression
						"""
	pass


def p_iteration_statement(p):
	"""iteration_statement : WHILE '(' condition ')' statement
						| DO statement WHILE '(' expression ')' ';'
						| FOR '(' for_init_statement condition_opt ';' expression_opt ')' statement
						"""
	pass


def p_for_init_statement(p):
	"""for_init_statement : expression_statement
						| simple_declaration
						"""
	pass


def p_jump_statement(p):
	"""jump_statement : BREAK ';'
						| CONTINUE ';'
						| RETURN expression_opt ';'
						| GOTO identifier ';'
						"""
	pass


def p_declaration_statement(p):
	"""declaration_statement : block_declaration
						"""
	pass


# /*----------------------------------------------------------------------
#  * Declarations.
#  *----------------------------------------------------------------------*/
def p_declaration_seq(p):
	"""declaration_seq : declaration
						| declaration_seq declaration
						"""
	pass


def p_declaration(p):
	"""declaration : block_declaration
						| function_definition
						| template_declaration
						| explicit_instantiation
						| explicit_specialization
						| linkage_specification
						| namespace_definition
						"""
	pass


def p_block_declaration(p):
	"""block_declaration : simple_declaration
						| asm_definition
						| namespace_alias_definition
						| using_declaration
						| using_directive
						"""
	pass


def p_simple_declaration(p):
	"""simple_declaration : decl_specifier_seq_opt init_declarator_list_opt ';'
						"""
	pass


def p_decl_specifier(p):
	"""decl_specifier : storage_class_specifier
						| type_specifier
						| function_specifier
						| FRIEND
						| TYPEDEF
						"""
	pass


def p_decl_specifier_seq(p):
	"""decl_specifier_seq : decl_specifier_seq_opt decl_specifier
						"""
	pass


def p_storage_class_specifier(p):
	"""storage_class_specifier : AUTO
						| REGISTER
						| STATIC
						| EXTERN
						| MUTABLE
						"""
	pass


def p_function_specifier(p):
	"""function_specifier : INLINE
						| VIRTUAL
						| EXPLICIT
						"""
	pass


def p_type_specifier(p):
	"""type_specifier : simple_type_specifier
						| class_specifier
						| enum_specifier
						| elaborated_type_specifier
						| cv_qualifier
						"""
	pass


def p_simple_type_specifier(p):
	"""simple_type_specifier : COLONCOLON_opt nested_name_specifier_opt type_name
						| CHAR
						| WCHAR_T
						| BOOL
						| SHORT
						| INT
						| LONG
						| SIGNED
						| UNSIGNED
						| FLOAT
						| DOUBLE
						| VOID
						"""
	pass


def p_type_name(p):
	"""type_name : class_name
						| enum_name
						| typedef_name
						"""
	pass


def p_elaborated_type_specifier(p):
	"""elaborated_type_specifier : class_key COLONCOLON_opt nested_name_specifier_opt identifier
						| ENUM COLONCOLON_opt nested_name_specifier_opt identifier
						| TYPENAME COLONCOLON_opt nested_name_specifier identifier
						| TYPENAME COLONCOLON_opt nested_name_specifier identifier '<' template_argument_list '>'
						"""
	pass


def p_enum_specifier(p):
	"""enum_specifier : ENUM identifier_opt '{' enumerator_list_opt '}'
						"""
	pass


def p_enumerator_list(p):
	"""enumerator_list : enumerator_definition
						| enumerator_list ',' enumerator_definition
						"""
	pass


def p_enumerator_definition(p):
	"""enumerator_definition : enumerator
						| enumerator '=' constant_expression
						"""
	pass


def p_enumerator(p):
	"""enumerator : identifier
						"""
	pass


def p_namespace_definition(p):
	"""namespace_definition : named_namespace_definition
						| unnamed_namespace_definition
						"""
	pass


def p_named_namespace_definition(p):
	"""named_namespace_definition : original_namespace_definition
						| extension_namespace_definition
						"""
	pass


def p_original_namespace_definition(p):
	"""original_namespace_definition : NAMESPACE identifier '{' namespace_body '}'
						"""
	pass


def p_extension_namespace_definition(p):
	"""extension_namespace_definition : NAMESPACE original_namespace_name '{' namespace_body '}'
						"""
	pass


def p_unnamed_namespace_definition(p):
	"""unnamed_namespace_definition : NAMESPACE '{' namespace_body '}'
						"""
	pass


def p_namespace_body(p):
	"""namespace_body : declaration_seq_opt
						"""
	pass


def p_namespace_alias_definition(p):
	"""namespace_alias_definition : NAMESPACE identifier '=' qualified_namespace_specifier ';'
						"""
	pass


def p_qualified_namespace_specifier(p):
	"""qualified_namespace_specifier : COLONCOLON_opt nested_name_specifier_opt namespace_name
						"""
	pass


def p_using_declaration(p):
	"""using_declaration : USING TYPENAME_opt COLONCOLON_opt nested_name_specifier unqualified_id ';'
						| USING COLONCOLON unqualified_id ';'
						"""
	pass


def p_using_directive(p):
	"""using_directive : USING NAMESPACE COLONCOLON_opt nested_name_specifier_opt namespace_name ';'
						"""
	pass


def p_asm_definition(p):
	"""asm_definition : ASM '(' string_literal ')' ';'
						"""
	pass


def p_linkage_specification(p):
	"""linkage_specification : EXTERN string_literal '{' declaration_seq_opt '}'
						| EXTERN string_literal declaration
						"""
	pass


# /*----------------------------------------------------------------------
#  * Declarators.
#  *----------------------------------------------------------------------*/
def p_init_declarator_list(p):
	"""init_declarator_list : init_declarator
						| init_declarator_list ',' init_declarator
						"""
	pass


def p_init_declarator(p):
	"""init_declarator : declarator initializer_opt
						"""
	pass


def p_declarator(p):
	"""declarator : direct_declarator
						| ptr_operator declarator
						"""
	pass


def p_direct_declarator(p):
	"""direct_declarator : declarator_id
						| direct_declarator '('parameter_declaration_clause ')' cv_qualifier_seq_opt exception_specification_opt
						| direct_declarator '[' constant_expression_opt ']'
						| '(' declarator ')'
						"""
	pass


def p_ptr_operator(p):
	"""ptr_operator : '*' cv_qualifier_seq_opt
						| '&'
						| COLONCOLON_opt nested_name_specifier '*' cv_qualifier_seq_opt
						"""
	pass


def p_cv_qualifier_seq(p):
	"""cv_qualifier_seq : cv_qualifier cv_qualifier_seq_opt
						"""
	pass


def p_cv_qualifier(p):
	"""cv_qualifier : CONST
						| VOLATILE
						"""
	pass


def p_declarator_id(p):
	"""declarator_id : COLONCOLON_opt id_expression
						| COLONCOLON_opt nested_name_specifier_opt type_name
						"""
	pass


def p_type_id(p):
	"""type_id : type_specifier_seq abstract_declarator_opt
						"""
	pass


def p_type_specifier_seq(p):
	"""type_specifier_seq : type_specifier type_specifier_seq_opt
						"""
	pass


def p_abstract_declarator(p):
	"""abstract_declarator : ptr_operator abstract_declarator_opt
						| direct_abstract_declarator
						"""
	pass


def p_direct_abstract_declarator(p):
	"""direct_abstract_declarator : direct_abstract_declarator_opt '(' parameter_declaration_clause ')' cv_qualifier_seq_opt exception_specification_opt
						| direct_abstract_declarator_opt '[' constant_expression_opt ']'
						| '(' abstract_declarator ')'
						"""
	pass


def p_parameter_declaration_clause(p):
	"""parameter_declaration_clause : parameter_declaration_list_opt ELLIPSIS_opt
						| parameter_declaration_list ',' ELLIPSIS
						"""
	pass


def p_parameter_declaration_list(p):
	"""parameter_declaration_list : parameter_declaration
						| parameter_declaration_list ',' parameter_declaration
						"""
	pass


def p_parameter_declaration(p):
	"""parameter_declaration : decl_specifier_seq declarator
						| decl_specifier_seq declarator '=' assignment_expression
						| decl_specifier_seq abstract_declarator_opt
						| decl_specifier_seq abstract_declarator_opt '=' assignment_expression
						"""
	pass


def p_function_definition(p):
	"""function_definition : decl_specifier_seq_opt declarator ctor_initializer_opt function_body
						| decl_specifier_seq_opt declarator function_try_block
						"""
	pass


def p_function_body(p):
	"""function_body : compound_statement
						"""
	pass


def p_initializer(p):
	"""initializer : '=' initializer_clause
						| '(' expression_list ')'
						"""
	pass


def p_initializer_clause(p):
	"""initializer_clause : assignment_expression
						| '{' initializer_list COMMA_opt '}'
						| '{' '}'
						"""
	pass


def p_initializer_list(p):
	"""initializer_list : initializer_clause
						| initializer_list ',' initializer_clause
						"""
	pass


# /*----------------------------------------------------------------------
#  * Classes.
#  *----------------------------------------------------------------------*/
def p_class_specifier(p):
	"""class_specifier : class_head '{' member_specification_opt '}'
						"""
	pass


def p_class_head(p):
	"""class_head : class_key identifier_opt base_clause_opt
						| class_key nested_name_specifier identifier base_clause_opt
						"""
	pass


def p_class_key(p):
	"""class_key : CLASS
						| STRUCT
						| UNION
						"""
	pass


def p_member_specification(p):
	"""member_specification : member_declaration member_specification_opt
						| access_specifier ':' member_specification_opt
						"""
	pass


def p_member_declaration(p):
	"""member_declaration : decl_specifier_seq_opt member_declarator_list_opt ';'
						| function_definition SEMICOLON_opt
						| qualified_id ';'
						| using_declaration
						| template_declaration
						"""
	pass


def p_member_declarator_list(p):
	"""member_declarator_list : member_declarator
						| member_declarator_list ',' member_declarator
						"""
	pass


def p_member_declarator(p):
	"""member_declarator : declarator pure_specifier_opt
						| declarator constant_initializer_opt
						| identifier_opt ':' constant_expression
						"""
	pass


# /*
#  * This rule need a hack for working around the ``= 0'' pure specifier.
#  * 0 is returned as an ``INTEGER'' by the lexical analyzer but in this
#  * context is different.
#  */
def p_pure_specifier(p):
	"""pure_specifier : '=' '0'
						"""
	pass


def p_constant_initializer(p):
	"""constant_initializer : '=' constant_expression
						"""
	pass


# /*----------------------------------------------------------------------
#  * Derived classes.
#  *----------------------------------------------------------------------*/
def p_base_clause(p):
	"""base_clause : ':' base_specifier_list
						"""
	pass


def p_base_specifier_list(p):
	"""base_specifier_list : base_specifier
						| base_specifier_list ',' base_specifier
						"""
	pass


def p_base_specifier(p):
	"""base_specifier : COLONCOLON_opt nested_name_specifier_opt class_name
						| VIRTUAL access_specifier_opt COLONCOLON_opt nested_name_specifier_opt class_name
						| access_specifier VIRTUAL_opt COLONCOLON_opt nested_name_specifier_opt class_name
						"""
	pass


def p_access_specifier(p):
	"""access_specifier : PRIVATE
						| PROTECTED
						| PUBLIC
						"""
	pass


# /*----------------------------------------------------------------------
#  * Special member functions.
#  *----------------------------------------------------------------------*/
def p_conversion_function_id(p):
	"""conversion_function_id : OPERATOR conversion_type_id
						"""
	pass


def p_conversion_type_id(p):
	"""conversion_type_id : type_specifier_seq conversion_declarator_opt
						"""
	pass


def p_conversion_declarator(p):
	"""conversion_declarator : ptr_operator conversion_declarator_opt
						"""
	pass


def p_ctor_initializer(p):
	"""ctor_initializer : ':' mem_initializer_list
						"""
	pass


def p_mem_initializer_list(p):
	"""mem_initializer_list : mem_initializer
						| mem_initializer ',' mem_initializer_list
						"""
	pass


def p_mem_initializer(p):
	"""mem_initializer : mem_initializer_id '(' expression_list_opt ')'
						"""
	pass


def p_mem_initializer_id(p):
	"""mem_initializer_id : COLONCOLON_opt nested_name_specifier_opt class_name
						| identifier
						"""
	pass


# /*----------------------------------------------------------------------
#  * Overloading.
#  *----------------------------------------------------------------------*/
def p_operator_function_id(p):
	"""operator_function_id : OPERATOR operator
						"""
	pass


def p_operator(p):
	"""operator : NEW
						| DELETE
						| NEW '[' ']'
						| DELETE '[' ']'
						| '+'
						| '_'
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
						| ADDEQ
						| SUBEQ
						| MULEQ
						| DIVEQ
						| MODEQ
						| XOREQ
						| ANDEQ
						| OREQ
						| SL
						| SR
						| SREQ
						| SLEQ
						| EQ
						| NOTEQ
						| LTEQ
						| GTEQ
						| ANDAND
						| OROR
						| PLUSPLUS
						| MINUSMINUS
						| ','
						| ARROWSTAR
						| ARROW
						| '(' ')'
						| '[' ']'
						"""
	pass


# /*----------------------------------------------------------------------
#  * Templates.
#  *----------------------------------------------------------------------*/
def p_template_declaration(p):
	"""template_declaration : EXPORT_opt TEMPLATE '<' template_parameter_list '>' declaration
						"""
	pass


def p_template_parameter_list(p):
	"""template_parameter_list : template_parameter
						| template_parameter_list ',' template_parameter
						"""
	pass


def p_template_parameter(p):
	"""template_parameter : type_parameter
						| parameter_declaration
						"""
	pass


def p_type_parameter(p):
	"""type_parameter : CLASS identifier_opt
						| CLASS identifier_opt '=' type_id
						| TYPENAME identifier_opt
						| TYPENAME identifier_opt '=' type_id
						| TEMPLATE '<' template_parameter_list '>' CLASS identifier_opt
						| TEMPLATE '<' template_parameter_list '>' CLASS identifier_opt '=' template_name
						"""
	pass


def p_template_id(p):
	"""template_id : template_name '<' template_argument_list '>'
						"""
	pass


def p_template_argument_list(p):
	"""template_argument_list : template_argument
						| template_argument_list ',' template_argument
						"""
	pass


def p_template_argument(p):
	"""template_argument : assignment_expression
						| type_id
						| template_name
						"""
	pass


def p_explicit_instantiation(p):
	"""explicit_instantiation : TEMPLATE declaration
						"""
	pass


def p_explicit_specialization(p):
	"""explicit_specialization : TEMPLATE '<' '>' declaration
						"""
	pass


# /*----------------------------------------------------------------------
#  * Exception handling.
#  *----------------------------------------------------------------------*/
def p_try_block(p):
	"""try_block : TRY compound_statement handler_seq
						"""
	pass


def p_function_try_block(p):
	"""function_try_block : TRY ctor_initializer_opt function_body handler_seq
						"""
	pass


def p_handler_seq(p):
	"""handler_seq : handler handler_seq_opt
						"""
	pass


def p_handler(p):
	"""handler : CATCH '(' exception_declaration ')' compound_statement
						"""
	pass


def p_exception_declaration(p):
	"""exception_declaration : type_specifier_seq declarator
						| type_specifier_seq abstract_declarator
						| type_specifier_seq
						| ELLIPSIS
						"""
	pass


def p_throw_expression(p):
	"""throw_expression : THROW assignment_expression_opt
						"""
	pass


def p_exception_specification(p):
	"""exception_specification : THROW '(' type_id_list_opt ')'
						"""
	pass


def p_type_id_list(p):
	"""type_id_list : type_id
						| type_id_list ',' type_id
						"""
	pass


# /*----------------------------------------------------------------------
#  * Epsilon (optional) definitions.
#  *----------------------------------------------------------------------*/
def p_declaration_seq_opt(p):
# 	/* epsilon */
	"""declaration_seq_opt :  declaration_seq
						"""
	pass


def p_TEMPLATE_opt(p):
# 	/* epsilon */
	"""TEMPLATE_opt :  TEMPLATE
						"""
	pass


def p_nested_name_specifier_opt(p):
# 	/* epsilon */
	"""nested_name_specifier_opt :  nested_name_specifier
						"""
	pass


def p_expression_list_opt(p):
# 	/* epsilon */
	"""expression_list_opt :  expression_list
						"""
	pass


def p_COLONCOLON_opt(p):
# 	/* epsilon */
	"""COLONCOLON_opt :  COLONCOLON
						"""
	pass


def p_new_placement_opt(p):
# 	/* epsilon */
	"""new_placement_opt :  new_placement
						"""
	pass


def p_new_initializer_opt(p):
# 	/* epsilon */
	"""new_initializer_opt :  new_initializer
						"""
	pass


def p_new_declarator_opt(p):
# 	/* epsilon */
	"""new_declarator_opt :  new_declarator
						"""
	pass


def p_expression_opt(p):
# 	/* epsilon */
	"""expression_opt :  expression
						"""
	pass


def p_statement_seq_opt(p):
# 	/* epsilon */
	"""statement_seq_opt :  statement_seq
						"""
	pass


def p_condition_opt(p):
# 	/* epsilon */
	"""condition_opt :  condition
						"""
	pass


def p_decl_specifier_seq_opt(p):
# 	/* epsilon */
	"""decl_specifier_seq_opt :  decl_specifier_seq
						"""
	pass


def p_init_declarator_list_opt(p):
# 	/* epsilon */
	"""init_declarator_list_opt :  init_declarator_list
						"""
	pass


def p_identifier_opt(p):
# 	/* epsilon */
	"""identifier_opt :  identifier
						"""
	pass


def p_enumerator_list_opt(p):
# 	/* epsilon */
	"""enumerator_list_opt :  enumerator_list
						"""
	pass


def p_TYPENAME_opt(p):
# 	/* epsilon */
	"""TYPENAME_opt :  TYPENAME
						"""
	pass


def p_initializer_opt(p):
# 	/* epsilon */
	"""initializer_opt :  initializer
						"""
	pass


def p_cv_qualifier_seq_opt(p):
# 	/* epsilon */
	"""cv_qualifier_seq_opt :  cv_qualifier_seq
						"""
	pass


def p_exception_specification_opt(p):
# 	/* epsilon */
	"""exception_specification_opt :  exception_specification
						"""
	pass


def p_constant_expression_opt(p):
# 	/* epsilon */
	"""constant_expression_opt :  constant_expression
						"""
	pass


def p_abstract_declarator_opt(p):
# 	/* epsilon */
	"""abstract_declarator_opt :  abstract_declarator
						"""
	pass


def p_type_specifier_seq_opt(p):
# 	/* epsilon */
	"""type_specifier_seq_opt :  type_specifier_seq
						"""
	pass


def p_direct_abstract_declarator_opt(p):
# 	/* epsilon */
	"""direct_abstract_declarator_opt :  direct_abstract_declarator
						"""
	pass


def p_parameter_declaration_list_opt(p):
# 	/* epsilon */
	"""parameter_declaration_list_opt :  parameter_declaration_list
						"""
	pass


def p_ELLIPSIS_opt(p):
# 	/* epsilon */
	"""ELLIPSIS_opt :  ELLIPSIS
						"""
	pass


def p_ctor_initializer_opt(p):
# 	/* epsilon */
	"""ctor_initializer_opt :  ctor_initializer
						"""
	pass


def p_COMMA_opt(p):
# 	/* epsilon */
	"""COMMA_opt :  ','
						"""
	pass


def p_member_specification_opt(p):
# 	/* epsilon */
	"""member_specification_opt :  member_specification
						"""
	pass


def p_base_clause_opt(p):
# 	/* epsilon */
	"""base_clause_opt :  base_clause
						"""
	pass


def p_member_declarator_list_opt(p):
# 	/* epsilon */
	"""member_declarator_list_opt :  member_declarator_list
						"""
	pass


def p_SEMICOLON_opt(p):
# 	/* epsilon */
	"""SEMICOLON_opt :  ';'
						"""
	pass


def p_pure_specifier_opt(p):
# 	/* epsilon */
	"""pure_specifier_opt :  pure_specifier
						"""
	pass


def p_constant_initializer_opt(p):
# 	/* epsilon */
	"""constant_initializer_opt :  constant_initializer
						"""
	pass


def p_access_specifier_opt(p):
# 	/* epsilon */
	"""access_specifier_opt :  access_specifier
						"""
	pass


def p_VIRTUAL_opt(p):
# 	/* epsilon */
	"""VIRTUAL_opt :  VIRTUAL
						"""
	pass


def p_conversion_declarator_opt(p):
# 	/* epsilon */
	"""conversion_declarator_opt :  conversion_declarator
						"""
	pass


def p_EXPORT_opt(p):
# 	/* epsilon */
	"""EXPORT_opt :  EXPORT
						"""
	pass


def p_handler_seq_opt(p):
# 	/* epsilon */
	"""handler_seq_opt :  handler_seq
						"""
	pass


def p_assignment_expression_opt(p):
# 	/* epsilon */
	"""assignment_expression_opt :  assignment_expression
						"""
	pass


def p_type_id_list_opt(p):
# 	/* epsilon */
	"""type_id_list_opt :  type_id_list
						"""
	pass
