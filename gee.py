import re, sys, string

debug = True
dict = { }
tokens = [ ]


#  Expression class and its subclasses
class Expression( object ):
	def __str__(self):
		return "" 
	
class BinaryExpr( Expression ):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right
		
	def __str__(self):
		return str(self.op) + " " + str(self.left) + " " + str(self.right)

class Number( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)

class VarRef( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)

class String( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)


def error( msg ):
	#print msg
	sys.exit(msg)

# The "parse" function. This builds a list of tokens from the input string,
# and then hands it to a recursive descent parser for the PAL grammar.

def match(matchtok):
	tok = tokens.peek( )
	if (tok != matchtok): error("Expecting "+ matchtok)
	tokens.next( )
	return tok
	
def factor( ):
	"""factor = number | string | ident |  "(" expression ")" """

	tok = tokens.peek( )
	if debug: print ("Factor: ", tok)
	if re.match(Lexer.number, tok):
		expr = Number(tok)
		tokens.next( )
		return expr
	if re.match(Lexer.string, tok):
		expr = String(tok)
		tokens.next( )
		return expr
	if re.match(Lexer.identifier, tok):
		expr = VarRef(tok)
		tokens.next( )
		return expr
	if tok == "(":
		tokens.next( )  # or match( tok )
		expr = addExpr( )
		tokens.peek( )
		tok = match(")")
		return expr
	error("Invalid operand")
	return

def relationalExpr( ):
	"""relationalExpr = addExpr [ relation addExpr ]"""

	tok = tokens.peek( )
	if debug: print("relationalExpr: ", tok)
	return


def andExpr( ):
	"""andExpr = relationalExpr { "and" relationalExpr }"""

	tok = tokens.peek( )
	if debug: print ("andExpr: ", tok)
	left = relationalExpr( )
	tok = tokens.peek( )
	while tok == "and":
		tokens.next()
		right = relationalExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left


def expr( ):
	"""expression = andExpr { "or" andExpr }"""
	
	tok = tokens.peek( )
	if debug: print ("expression: ", tok)
	left = andExpr( )
	tok = tokens.peek( )
	while tok == "or":
		tokens.next()
		right = andExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left
	return


def term( ):
	""" term = factor { ('*' | '/') factor } """

	tok = tokens.peek( )
	if debug: print ("Term: ", tok)
	left = factor( )
	tok = tokens.peek( )
	while tok == "*" or tok == "/":
		tokens.next()
		right = factor( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left

def addExpr( ):
	""" addExpr = term { ('+' | '-') term } """

	tok = tokens.peek( )
	if debug: print ("addExpr: ", tok)
	left = term( )
	tok = tokens.peek( )
	while tok == "+" or tok == "-":
		tokens.next()
		right = term( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left

#  Statement class and its subclasses
class Statement( object ):
	def __str__(self):
		return ""

class ifStatement( Statement ):
	def __init__(self, ifBlock, elseBlock, expr):
		self.ifBlock = ifBlock
		self.elseBlock = elseBlock
		self.expr = expr
		
	def __str__(self):
		return "if " + str(self.expr) + "\n" + str(self.ifBlock) + "else" + "\n" + str(self.elseBlock) + "endif" + "\n"

class whileStatement( Statement ):
	def __init__(self, whileBlock, expr):
		self.whileBlock = whileBlock
		self.expr = expr
		
	def __str__(self):
		return "while " + str(self.expr) + "\n" + str(self.whileBlock) + "endWhile" + "\n"

class assignStatement( Statement ):
	def __init__(self, id, expr):
		self.id = id
		self.expr = expr
		
	def __str__(self):
		return "= " +  str(self.id) + " " + str(self.expr) + "\n"

def parseStmtList(  ):
	""" stmtList = { Statement } """

	# list of statements will be stored here
	statementList = []
	tok = tokens.peek( )

	while tok not in [None,"~"]:
		# need to store each statement in a list
		stmt = parseStmt()
		statementList.append(stmt)
		tok = tokens.peek()
	return statementList

def parseStmt( ):
	"""statement = ifStatement |  whileStatement  |  assign"""

	tok = tokens.peek( )
	if debug: print ("statement: ", tok)

	if tok == "if":
		stmt = parseIfStmt()
	elif tok == "while":
		stmt = parseWhileStmt()
	elif re.match(Lexer.identifier, tok):
		stmt = parseAssignStmt()
	else:
		error("Not a valid statement!")
		return

	return stmt

def parseIfStmt( ):
	"""ifStatement = "if" expression block   [ "else" block ]"""

	tok = tokens.next()
	if debug: print ("if statement: ", tok)

	expr = expr()
	ifBlock = parseBlock()
	elseBlock = ""

	if tok == "else":
			if debug: print ("else statement: ", tok)
			elseBlock = parseBlock()
	
	stmt = ifStatement(ifBlock, elseBlock, expr)
	return stmt

def parseWhileStmt( ):
	"""whileStatement = "while"  expression  block"""
	
	tok = tokens.next()
	if debug: print ("while statement: ", tok)

	expr = expr()
	whileBlock = parseBlock()
	
	stmt = whileStatement(whileBlock, expr)
	return stmt


def parseAssignStmt( ):
	"""assign = ident "=" expression  eoln"""

	id = tokens.peek()
	if debug: print ("assign statement: ", id)

	tok = tokens.next()

	if tok == "=":
		tokens.next()
		expr = expr()
		stmt = assignStatement(id, expr)
		tok = tokens.next()
		if tok != ";":
			error("assign statement doesn't end with eol")
		return stmt
	else:
		error("assign statement doesn't have equal sign")
	return

def parseBlock( ):
	"""block = ":" eoln indent stmtList undent"""

	tok = tokens.peek( )
	if debug: print ("block: ", tok)

	if tok == ":":
		tok = tokens.next( )
		if tok != ";":
			error("Block is missing eol character")
		tok = tokens.next()
		if tok != "@":
			error("Block is missing indent")
		tok = tokens.next()
		stmts = parseStmtList()
		if tok != "~":
			error("Block is missing undent")
		return stmts
	else:
		error("Block is missing ':' character")
	return

def parse( text ):
	global tokens
	tokens = Lexer( text )
	stmtlist = parseStmtList( )
	#print(stmtlist)
	for stmt in stmtlist:
		print(stmt +"\n")
	return


# Lexer, a private class that represents lists of tokens from a Gee
# statement. This class provides the following to its clients:
#
#   o A constructor that takes a string representing a statement
#       as its only parameter, and that initializes a sequence with
#       the tokens from that string.
#
#   o peek, a parameterless message that returns the next token
#       from a token sequence. This returns the token as a string.
#       If there are no more tokens in the sequence, this message
#       returns None.
#
#   o removeToken, a parameterless message that removes the next
#       token from a token sequence.
#
#   o __str__, a parameterless message that returns a string representation
#       of a token sequence, so that token sequences can print nicely

class Lexer :
	
	
	# The constructor with some regular expressions that define Gee's lexical rules.
	# The constructor uses these expressions to split the input expression into
	# a list of substrings that match Gee tokens, and saves that list to be
	# doled out in response to future "peek" messages. The position in the
	# list at which to dole next is also saved for "nextToken" to use.
	
	special = r"\(|\)|\[|\]|,|:|;|@|~|;|\$"
	relational = "<=?|>=?|==?|!="
	arithmetic = "\+|\-|\*|/"
	#char = r"'."
	string = r"'[^']*'" + "|" + r'"[^"]*"'
	number = r"\-?\d+(?:\.\d+)?"
	literal = string + "|" + number
	#idStart = r"a-zA-Z"
	#idChar = idStart + r"0-9"
	#identifier = "[" + idStart + "][" + idChar + "]*"
	identifier = "[a-zA-Z]\w*"
	lexRules = literal + "|" + special + "|" + relational + "|" + arithmetic + "|" + identifier
	
	def __init__( self, text ) :
		self.tokens = re.findall( Lexer.lexRules, text )
		self.position = 0
		self.indent = [ 0 ]
	
	
	# The peek method. This just returns the token at the current position in the
	# list, or None if the current position is past the end of the list.
	
	def peek( self ) :
		if self.position < len(self.tokens) :
			return self.tokens[ self.position ]
		else :
			return None
	
	
	# The removeToken method. All this has to do is increment the token sequence's
	# position counter.
	
	def next( self ) :
		self.position = self.position + 1
		return self.peek( )
	
	
	# An "__str__" method, so that token sequences print in a useful form.
	
	def __str__( self ) :
		return "<Lexer at " + str(self.position) + " in " + str(self.tokens) + ">"



def chkIndent(line):
	ct = 0
	for ch in line:
		if ch != " ": return ct
		ct += 1
	return ct
		

def delComment(line):
	pos = line.find("#")
	if pos > -1:
		line = line[0:pos]
		line = line.rstrip()
	return line

def mklines(filename):
	inn = open(filename, "r")
	lines = [ ]
	pos = [0]
	ct = 0
	for line in inn:
		ct += 1
		line = line.rstrip( )+";"
		line = delComment(line)
		if len(line) == 0 or line == ";": continue
		indent = chkIndent(line)
		line = line.lstrip( )
		if indent > pos[-1]:
			pos.append(indent)
			line = '@' + line
		elif indent < pos[-1]:
			while indent < pos[-1]:
				del(pos[-1])
				line = '~' + line
		print (ct, "\t", line)
		lines.append(line)
	# print len(pos)
	undent = ""
	for i in pos[1:]:
		undent += "~"
	lines.append(undent)
	# print undent
	return lines



def main():
	"""main program for testing"""
	global debug
	ct = 0
	for opt in sys.argv[1:]:
		if opt[0] != "-": break
		ct = ct + 1
		if opt == "-d": debug = True
	if len(sys.argv) < 2+ct:
		print ("Usage:  %s filename" % sys.argv[0])
		return
	parse("".join(mklines(sys.argv[1+ct])))
	return


main()
