#!/usr/bin/python3

import sys
import ply.lex as lex
from ply.lex import TOKEN

reserved = {
	'asm': 'ASM', 'auto': 'AUTO', 'bool': 'BOOL', 'break': 'BREAK', 'case': 'CASE', 'catch': 'CATCH',
	'char': 'CHAR', 'class': 'CLASS', 'const': 'CONST', 'const_cast': 'CONST_CAST', 'continue': 'CONTINUE',
	'default': 'DEFAULT', 'delete': 'DELETE', 'do': 'DO', 'double': 'DOUBLE', 'dynamic_cast': 'DYNAMIC_CAST',
	'else': 'ELSE', 'enum': 'ENUM', 'explicit': 'EXPLICIT', 'extern': 'EXTERN', 'false': 'FALSE',
	'float': 'FLOAT', 'for': 'FOR', 'friend': 'FRIEND', 'goto': 'GOTO', 'if': 'IF', 'inline': 'INLINE', 'int': 'INT',
	'long': 'LONG', 'mutable': 'MUTABLE', 'namespace': 'NAMESPACE', 'new': 'NEW', 'operator': 'OPERATOR', 'private': 'PRIVATE',
	'protected': 'PROTECTED', 'public': 'PUBLIC', 'register': 'REGISTER', 'reinterpret_cast': 'REINTERPRET_CAST',
	'return': 'RETURN', 'short': 'SHORT', 'signed': 'SIGNED', 'sizeof': 'SIZEOF', 'static': 'STATIC', 'static_cast': 'STATIC_CAST',
	'struct': 'STRUCT', 'switch': 'SWITCH', 'this': 'THIS', 'throw': 'THROW', 'true': 'TRUE',
	'try': 'TRY', 'typedef': 'TYPEDEF', 'typeid': 'TYPEID', 'typename': 'TYPENAME', 'union': 'UNION', 'unsigned': 'UNSIGNED',
	'using': 'USING', 'virtual': 'VIRTUAL', 'void': 'VOID', 'volatile': 'VOLATILE', 'wchar_t': 'WCHAR_T', 'while': 'WHILE'
}


class MyLexer(object):
	
	tokens = [
		'IDENTIFIER', 'INTEGER', 'FLOATING', 'CHARACTER' ,'STRING', 'ELLIPSIS', 'SCOPE', 'DOT_STAR', 'ASS_ADD',
		'ASS_SUB', 'ASS_MUL', 'ASS_DIV', 'ASS_MOD', 'ASS_XOR', 'ASS_AND', 'ASS_OR', 'ASS_SHR', 'ASS_SHL', 'SHL', 'SHR',
		'EQ','NE', 'LE', 'GE', 'LOG_AND' ,'LOG_OR','INC','DEC','ARROW_STAR','ARROW',

	#	'LPAREN', 'RPAREN','LBRACKET', 'RBRACKET','LBRACE', 'RBRACE','COMMA', 'PERIOD', 'SEMI', 'COLON',

] + list(reserved.values())

	literals = ['+','-',';',':','?','.','*','/','&','!','~','%','^','|','=',',','<','>','\'','\"','\\','@','$','[',']','{','}','(',')']

	decimal = r'[0-9]+'
	hexa = r'0[xX][0-9a-fA-F]+'
	octa = r'0[0-7]+'
	binary = r'0[bB][01]+'
	suffix = r'(ll|LL|[uU][lL]?|[lL][uU]?)?'
	integer = r'(' + hexa + r'|' + octa + r'|' + binary + r'|' + decimal + r')' + suffix

	fracconst = r'(([0-9]*\.[0-9]+)|([0-9]+\.))'
	exppart = r'[eE][-\+]?[0-9]+'
	floatsuffix = r'([fFlL])?'
	floating = fracconst + r'(' + exppart + r')?' + floatsuffix + r'|[0-9]+(' + exppart + r')' + floatsuffix


	simple_escape_seq = r"\\'" + r'\\"|\\\?|\\\\|\\a|\\b|\\f|\\n|\\r|\\t|\\v'
	octal_escape_seq = r'\\[0-7]{1,3}'
	hex_escape_seq = r'\\x[0-9A-Fa-f]+'
	escape_seq = r'(' + simple_escape_seq + r')|(' + octal_escape_seq + r')|('  + hex_escape_seq + r')'
	univ_char_name = r'(\\u[0-9A-Fa-f]{3})|(\\U[0-9A-Fa-f]{6})'

	chartext = r"[^\n'\\]|(\\.)"
	character =  r"L?'(" + chartext + r")*'"

	stringtext = r'([^"\n\\])|(\\.)'
	string = r'L?"(' + chartext + r')*"'


	@TOKEN(floating)
	def t_FLOATING(self,t):
		return t
	@TOKEN(integer)
	def t_INTEGER(self,t):
		return t
	@TOKEN(character)
	def t_CHARACTER(self,t):
		return t
	@TOKEN(string)
	def t_STRING(self,t):
		return t

	def t_comment(self,t):
		r'(/\*(.|\n)*?\*/)|//.*\n'
		t.lexer.lineno += t.value.count('\n')
		pass

	def t_NEWLINE(self,t):
		r'\n+'
		t.lexer.lineno += t.value.count("\n")
		

	# Preprocessor directive (ignored)
	def t_preprocessor(self,t):
		'\#[^\n]*\n'
		pass

	def t_IDENTIFIER(self,t):
		r'[a-zA-Z_]([a-zA-Z_0-9]|(\\u[0-9A-Fa-f]{3})|(\\U[0-9A-Fa-f]{6}))*'
		print(t.value)
		t.type = reserved.get(t.value,'IDENTIFIER')    # Check for reserved words
		return t


	t_ignore = ' \t\r\f\v'

	#print(t_ignore)

	#Operators
	t_ELLIPSIS = r'\.\.\.'
	t_SCOPE = r'::'
	t_DOT_STAR = r'\.\*'
	t_ASS_ADD = r'\+='
	t_ASS_SUB = r'-='
	t_ASS_MUL = r'\*='
	t_ASS_DIV = r'/='
	t_ASS_MOD = r'%='
	t_ASS_XOR = r'xor_eq|\^='
	t_ASS_AND = r'and_eq|&='
	t_ASS_OR = r'or_eq|\|='
	t_ASS_SHR = r'>>='
	t_ASS_SHL = r'<<='
	t_SHL = r'<<'
	t_SHR = r'>>'
	t_NE = r'\!='
	t_LE = r'<='
	t_GE = r'>='
	t_LOG_OR = r'\|\|'
	t_INC = r'\+\+'
	t_DEC = r'--'
	t_ARROW_STAR = r'->\*'
	t_ARROW = r'->'
	t_EQ = r'=='


	def t_error(self,t):
		print("Illegal character '%s'" % t.value[0])
		t.lexer.skip(0)

	def build(self,**kwargs):
		self.lexer = lex.lex(module=self, **kwargs)

	# Test it output
	def test(self,data):
		self.lexer.input(data)
		while True:
			tok = self.lexer.token()
			if not tok:
				break
			print(tok)


# Build the lexer and try it out
cpp_scanner = MyLexer()
cpp_scanner.build()
if __name__ == "__main__":
	if(len(sys.argv) == 2):
		filename = sys.argv[1]
		a = open(filename)
		data = a.read()
		cpp_scanner.test(data)
	else:
		lex.runmain(cpp_scanner.lexer)