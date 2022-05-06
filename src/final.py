from hashlib import new
from prolog_structures import Rule, RuleBody, Term, Function, Variable, Atom, Number
from typing import List
from functools import reduce

import sys
import random

class Not_unifiable(Exception):
	pass

'''
Please read prolog_structures.py for data structures
that represent Prolog terms, rules, and goals.
'''
class Interpreter:
	def __init__(self):
		pass

	'''
	Example
	occurs_check (v, t) where v is of type Variable, t is of type Term.
	occurs_check (v, t) returns true if the Prolog Variable v occurs in t.
	Please see the lecture note Control in Prolog to revisit the concept of
	occurs-check.
	'''
	def occurs_check (self, v : Variable, t : Term) -> bool:
		if isinstance(t, Variable):
			return v == t
		elif isinstance(t, Function):
			for t in t.terms:
				if self.occurs_check(v, t):
					return True
			return False
		return False


	'''
	Problem 1
	variables_of_term (t) where t is of type Term.
	variables_of_clause (c) where c is of type Rule.

	The function should return the Variables contained in a term or a rule
	using Python set.

	The result must be saved in a Python set. The type of each element (a Prolog Variable)
	in the set is Variable.
	'''
	def variables_of_term (self, t : Term) -> set :
		variables = set()
		for term in t.terms:
			if isinstance(term, Variable):
				variables = variables.union({term})
		return variables

	def variables_of_clause (self, c : Rule) -> set :
		return self.variables_of_term(c.head)


	'''
	Problem 2
	substitute_in_term (s, t) where s is of type dictionary and t is of type Term
	substitute_in_clause (s, t) where s is of type dictionary and c is of type Rule,

	The value of type dict should be a Python dictionary whose keys are of type Variable
	and values are of type Term. It is a map from variables to terms.

	The function should return t_ obtained by applying substitution s to t.

	Please use Python dictionary to represent a subsititution map.
	'''
	def substitute_in_term (self, s : dict, t : Term) -> Term:
		if isinstance(t, Function):
			new_terms = []
			for term in t.terms:
				new_terms.append(self.substitute_in_term(s, term))
			return Function(t.relation, new_terms)
		elif isinstance(t, Variable):
			return s.get(t, t)

		return t

	def substitute_in_clause (self, s : dict, c : Rule) -> Rule:
		new_head = self.substitute_in_term(s, c.head)
		if c.body.terms:
			new_terms = []
			for term in c.body.terms:
				new_terms.append(self.substitute_in_term(s, term))
			return Rule(new_head, RuleBody(new_terms))
		else:
			return Rule(new_head, c.body)

	'''
	Problem 3
	unify (t1, t2) where t1 is of type term and t2 is of type Term.
	The function should return a substitution map of type dict,
	which is a unifier of the given terms. You may find the pseudocode
	of unify in the lecture note Control in Prolog useful.

	The function should raise the exception raise Not_unfifiable (),
	if the given terms are not unifiable.

	Please use Python dictionary to represent a subsititution map.
	'''
	def unify_helper(self, t1 : Term, t2 : Term, unifier : dict):
		X = self.substitute_in_term(unifier, t1)
		Y = self.substitute_in_term(unifier, t2)

		if isinstance(X, Variable) and not self.occurs_check(X, Y):
			s = dict({})
			s[X] = Y
			for key in unifier.keys():
				unifier[key] = self.substitute_in_term(s, unifier[key])
			unifier[X] = Y
			return unifier
		elif isinstance(Y, Variable) and not self.occurs_check(Y, X):
			s = dict({})
			s[Y] = X
			for key in unifier.keys():
				unifier[key] = self.substitute_in_term(s, unifier[key])
			unifier[Y] = X
			return unifier
		elif (type(X) is type(Y)) and (isinstance(X, Atom) or isinstance(X, Number) or isinstance(X, Variable)) and (X == Y):
			return unifier
		elif isinstance(X, Function) and isinstance(Y, Function) and X.relation == Y.relation and len(X.terms) == len(Y.terms):
			for i in range(0, len(X.terms)):
				unifier = self.unify_helper(X.terms[i], Y.terms[i], unifier)
			return unifier
		else:
			raise Not_unifiable()

	def unify (self, t1: Term, t2: Term) -> dict:
		return self.unify_helper(t1, t2, {})


	fresh_counter = 0
	def fresh(self) -> Variable:
		self.fresh_counter += 1
		return Variable("_G" + str(self.fresh_counter))
	def freshen(self, c: Rule) -> Rule:
		c_vars = self.variables_of_clause(c)
		theta = {}
		for c_var in c_vars:
			theta[c_var] = self.fresh()

		return self.substitute_in_clause(theta, c)


	'''
	Problem 4
	Following the Abstract interpreter pseudocode in the lecture note Control in Prolog to implement
	a nondeterministic Prolog interpreter.

	nondet_query (program, goal) where
		the first argument is a program which is a list of Rules.
		the second argument is a goal which is a list of Terms.

	The function returns a list of Terms (results), which is an instance of the original goal and is
	a logical consequence of the program. See the tests cases (in src/main.py) as examples.
	'''
	def nondet_query (self, program : List[Rule], pgoal : List[Term]) -> List[Term]:
		G = pgoal.copy()
		resolvent = G.copy()

		while len(resolvent) > 0:
			A = resolvent[random.randint(0, len(resolvent) - 1)]
			A1 = program[random.randint(0, len(program) - 1)]

			try:
				A1 = self.freshen(A1)
				unifier = self.unify(A, A1.head)
			except:
				break

			resolvent.remove(A)
			resolvent.extend(A1.body.terms)

			for index in range(len(G)):
				G[index] = self.substitute_in_term(unifier, G[index])
			for index in range(len(resolvent)):
				resolvent[index] = self.substitute_in_term(unifier, resolvent[index])

		if len(resolvent) == 0:
			return G
		else:
			return self.nondet_query(program, pgoal)


	'''
	Challenge Problem

	det_query (program, goal) where
		the first argument is a program which is a list of Rules.
		the second argument is a goal which is a list of Terms.

	The function returns a list of term lists (results). Each of these results is
	an instance of the original goal and is a logical consequence of the program.
	If the given goal is not a logical consequence of the program, then the result
	is an empty list. See the test cases (in src/main.py) as examples.
	'''

	def det_query (self, program : List[Rule], pgoal : List[Term]) -> List[List[Term]]:
		def dfs(resolvent : List[Term], goal: List[Term], solutions : List[List[Term]]):
			if not resolvent:
				solutions.append(goal)
				return True

			while (resolvent):
				chosen_goal = resolvent.pop(0)
				searched = False
				for rule in program:
					try:
						rule = self.freshen(rule)
						theta = self.unify(chosen_goal, rule.head)
						new_resolvent, new_goal = resolvent.copy(), goal.copy()

						chosen_goal = rule.body
						new_resolvent.extend(rule.body.terms)
						new_resolvent = self.substitute_in_term(theta, new_resolvent)
						new_goal = self.substitute_in_term(theta, new_goal)

						result = dfs(new_resolvent, new_goal, solutions)
						searched = result or searched
					except Not_unifiable:
						continue
				
				if not searched:
					return

		solutions = []
		dfs(pgoal.copy(), pgoal.copy(), solutions)
		return solutions
