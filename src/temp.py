import sys
import traceback

from prolog_structures import Rule, RuleBody, Term, Function, Variable, Atom, Number
from final import Interpreter, Not_unifiable

def list2str(l):
		return ('(' + (',' + ' ').join(
			list(map(str, l))) + ')')

if __name__ == '__main__':

	interpreter = Interpreter()

	def ancestor (x, y): return Function ("ancestor", [x, y])
	def father (x, y): return Function ("father", [x, y])
	def father_consts (x, y):  return father (Atom (x), Atom (y))
	f1 = Rule (father_consts ("rickard", "ned"), RuleBody([]))
	f2 = Rule (father_consts ("ned", "robb"), RuleBody([]))
	r1 = Rule (ancestor (Variable ("X"), Variable ("Y")), RuleBody([father (Variable ("X"), Variable ("Y"))]))
	r2 = Rule (ancestor (Variable ("X"), Variable ("Y")), \
					RuleBody([father (Variable ("X"), Variable ("Z")), ancestor (Variable ("Z"), Variable ("Y"))]))
	pstark = [f1,f2,r1,r2]

	# g = [ancestor (Variable("X"), Atom("robb"))]
	# print (f"Goal: {list2str(g)}")
	# g_ = interpreter.nondet_query (pstark, g)
	# print (f"Solution: {list2str(g_)}")
	# assert (g_ == [ancestor (Atom("ned"), Atom("robb"))] or
	# 				g_ == [ancestor (Atom("rickard"), Atom("robb"))])

	g = [ancestor (Variable("X"), Atom("robb"))]
	print (f"Goal: {list2str(g)}")
	g_ = interpreter.det_query (pstark, g)
	print (f"Solution g_: {list2str(g_)}")
	assert (len(g_) == 2)
	g1, g2 = g_[0], g_[1]
	print (f"Solution: {list2str(g1)}")
	print (f"Solution: {list2str(g2)}")
	assert (g1 == [ancestor (Atom("ned"), Atom("robb"))])
	assert (g2 == [ancestor (Atom("rickard"), Atom("robb"))])

	"""
	nil = Atom("nil")
	def cons (h, t): return Function ("cons", [h, t])
	def append (x, y, z): return Function ("append", [x, y, z])
	c1 = Rule (append (nil, Variable("Q"), Variable("Q")), RuleBody([]))
	c2 = Rule (append ((cons (Variable("H"), Variable("P"))), Variable("Q"), (cons (Variable("H"), Variable("R")))), \
	                RuleBody([append (Variable("P"), Variable("Q"), Variable("R"))]))
	pappend = [c1, c2]

	print (f"\nProgram: {list2str(pappend)}")
	g = [append (Variable("X"), Variable("Y"), \
			(cons (Number("1"), (cons (Number("2"), (cons (Number("3"), nil)))))))]
	print (f"Goal: {list2str(g)}")
	g_ = interpreter.nondet_query (pappend, g)
	print (f"Solution: {list2str(g_)}")
	print (
	g_ == [append (nil, (cons (Number("1"), (cons (Number("2"), (cons (Number("3"), nil)))))), \
							(cons (Number("1"), (cons (Number("2"), (cons (Number("3"), nil)))))))] or
	g_ == [append ((cons (Number("1"), nil)), (cons (Number("2"), (cons (Number("3"), nil)))), \
							(cons (Number("1"), (cons (Number("2"), (cons (Number("3"), nil)))))))] or
	g_ == [append ((cons (Number("1"), (cons (Number("2"), nil)))), (cons (Number("3"), nil)), \
							(cons (Number("1"), (cons (Number("2"), (cons (Number("3"), nil)))))))] or
	g_ == [append ((cons (Number("1"), (cons (Number("2"), (cons (Number("3"), nil)))))), nil, \
							(cons (Number("1"), (cons (Number("2"), (cons (Number("3"), nil)))))))] )
	"""