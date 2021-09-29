# Gee-Parser-mislam22

CSC 512 Compiler Construction

Project 1


Gee Parser
Due: 11:59 PM, Oct 1
Submit Project: parser
Source File: gee.py.txt
Grammar File: grammar.txt 

Test Files: t0.gee.txt t1.gee.txt t2.gee.txt 
        max.gee.txt fact.gee.txt test.gee.txt
Output: max-out.txt fact-out.txt test-out.txt
See Questions at the bottom.
The Gee programming language is:

A small but interesting programming language;
Designed for class projects in language implementation;
Intended to expose new ways of thinking about programming.
Different from typical statically-typed languages.
The purpose of the project is to parse the input according to the grammar and produce a printed representation of the abstract syntax tree. Sample data and output are given above.

Parser
Your task is to construct the remaining recursive descent routines to complete the parser for the Gee implementation grammar. You are free to modify the grammar provided you do not change the syntax of Gee.

Specially, you must:

Build parse routines for the expression nonterminals:
expression, andExpr, relationalExpr
(as specified in the grammar). Note that currently addExpr is called in 2 places: factor and parse.
Build classes for ident (VarRef) and string (String) and add the necessary logic to factor.
Modify function "parse( text )" by commenting out (or deleting) the code that calls addExpr and its associated print (i.e., lines 3-4 in the function body), and uncomment the call to parseStmtList and its print (i.e., lines 6-7 in the function body). After doing this the expression tests will no lnger work.
Build parse routines for the following statements (nonterminals):
StmtList, Statement, assign, while, if, block
Note that the code for parseStmtList is incorrect in that it processes a statement, instead of creating a list of statements and putting that into a subclass of Statement and returning an object containing the list.
The output of the parser is a printed representation of the abstract syntax tree. The abstract syntax is defined by a collection of classes. Each class in the abstract syntax must have an appropriate constructor and a __str__ function for displaying the abstract syntax.

Statements should be printed one per line; this can be accomplshed by appending a "\n" to the string returned by __str__ . Expressions (including assignment) should print in Polish prefix with a space separating each element from the next.

A Gee program file must end with an end of line. To check, either execute : cat filename or in your editor, make sure you can move the cursor to the line below the last line of text.

Requirements
You must use Python 3, not Python 2. The biggest change is that all print statements must be converted to:
print ( ... ).
Each parse function corresponding to a nonterminal must return an object of either Expression or Statement.
Questions
Q: Why does the test case test.gee print an else 3 times when only 2 of the Ifs have an else?
I chose an abstract syntax which stores an if-then as an if-then-else with an empty Block. For me it simplifies the next assignment.
Q: Are we expected to be able to run tests t1, t2, t3?
Only as part of a larger program, since an expression is not a statement.
