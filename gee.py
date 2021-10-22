import re, sys, string

debug = False
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

	def value(self, state):
		left = self.left.value(state)
		right = self.right.value(state)
		if self.op == '+':
			return left + right
		if self.op == '-':
			return left - right
		if self.op == '*':
			return left * right
		if self.op == '/':
			return left / right
		if self.op == '<':
			return left < right
		if self.op == '>':
			return left > right
		if self.op == '!=':
			return left != right
		if self.op == '==':
			return left == right
		if self.op == 'and':
			return left and right
		if self.op == 'or':
			return left or right

class Number( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)

	def value(self, state):
		return int(self.value)

class VarRef( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)
	
	def value(self, state):
		return state[self.value]

class String( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)

	def value(self, state):
		return self.value


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
		exprsn = Number(tok)
		tokens.next( )
		return exprsn
	if re.match(Lexer.string, tok):
		exprsn = String(tok)
		tokens.next( )
		return exprsn
	if re.match(Lexer.identifier, tok):
		exprsn = VarRef(tok)
		tokens.next( )
		return exprsn
	if tok == "(":
		tokens.next( )  # or match( tok )
		exprsn = addExpr( )
		tokens.peek( )
		tok = match(")")
		return exprsn
	error("Invalid operand")
	return

def relationalExpr( ):
	"""relationalExpr = addExpr [ relation addExpr ]"""

	tok = tokens.peek( )
	if debug: print("relationalExpr: ", tok)

	left = addExpr( )
	tok = tokens.peek( )
	while re.match(Lexer.relational, tok):
		tokens.next()
		right = addExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left


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

# list of statements
class StatementList(object):
	def __init__(self):
		self.statementList = []

	def appendStatement(self, statement):
		self.statementList.append(statement)

	def __str__(self):
		printStr = ''
		for statement in self.statementList:
			printStr += str(statement)
		return printStr
	
	def meaning(self, state):
		for statement in self.StatementList:
			statement.meaning(state)
		return state

#  Statement class and its subclasses
class Statement( object ):
	def __str__(self):
		return ""

class ifStatement( Statement ):
	def __init__(self, ifBlock, elseBlock, exprsn):
		self.ifBlock = ifBlock
		self.elseBlock = elseBlock
		self.exprsn = exprsn
		
	def __str__(self):
		return "if " + str(self.exprsn) + "\n" + str(self.ifBlock) + "else" + "\n" + str(self.elseBlock) + "endif" + "\n"

	def meaning(self, state):
		if self.exprsn.value(state):
			self.ifBlock.meaning(state)
		else:
			if self.elseBlock != "":
				self.elseBlock.meaning(state)
		return state

class whileStatement( Statement ):
	def __init__(self, whileBlock, exprsn):
		self.whileBlock = whileBlock
		self.exprsn = exprsn
		
	def __str__(self):
		return "while " + str(self.exprsn) + "\n" + str(self.whileBlock) + "endWhile" + "\n"

	def meaning(self, state):
		while self.exprsn.value(state):
			self.whileBlock.meaning(state)
		return state

class assignStatement( Statement ):
	def __init__(self, id, exprsn):
		self.id = id
		self.exprsn = exprsn
		
	def __str__(self):
		return "= " +  str(self.id) + " " + str(self.exprsn) + "\n"
	
	def meaning(self, state):
		state[self.id] = self.exprsn.value(state)
		return state

def parseStmtList(  ):
	""" stmtList = { Statement } """

	statementList = StatementList()
	tok = tokens.peek( )

	while tok not in [None,"~"]:
		# need to store each statement in a list
		stmt = parseStmt()
		statementList.appendStatement(stmt)
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

	exprsn = expr()
	ifBlock = parseBlock()
	elseBlock = ""

	tok = tokens.peek()
	
	if tok == "else":
		tok = tokens.next()
		if debug: print ("else statement: ", tok)
		elseBlock = parseBlock()
	
	stmt = ifStatement(ifBlock, elseBlock, exprsn)
	return stmt

def parseWhileStmt( ):
	"""whileStatement = "while"  expression  block"""
	
	tok = tokens.next()
	if debug: print ("while statement: ", tok)

	exprsn = expr()
	whileBlock = parseBlock()
	
	stmt = whileStatement(whileBlock, exprsn)
	return stmt


def parseAssignStmt( ):
	"""assign = ident "=" expression  eoln"""

	id = tokens.peek()
	if debug: print ("assign statement: ", id)

	tok = tokens.next()

	if tok == "=":
		tokens.next()
		exprsn = expr()
		stmt = assignStatement(id, exprsn)
		tok = tokens.peek()
		if tok != ";":
			error("assign statement doesn't end with eol")
		tokens.next()
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
		tok = tokens.peek()
		if tok != "~":
			error("Block is missing undent")
		tokens.next()
		return stmts
	else:
		error("Block is missing ':' character")
	return

def parse( text ):
	global tokens
	tokens = Lexer( text )
	stmtlist = parseStmtList( )
	print(stmtlist)
	semantic(stmtlist)

def semantic( statementList ):
	state = {}
	state = statementList.meaning(state)
	print('\n\n' + printState(state) + '\n')
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


def printState(stateDict):
	string = "{"
	for key, value in stateDict.items():
		string += "<" + str(key) + ", " + str(value) + ">, " 

	return string[:-2] + "}"

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
