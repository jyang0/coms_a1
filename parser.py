from dataclasses import dataclass, field
import dataclasses
from typing import List
import hw1
import tokenizer

from tokenizer import TokenType


@dataclass(frozen=True)
class Node:
	name: str
	children: List['Node'] = field(default_factory=list)
	terminal: bool = False
	content: str = ''

@dataclass
class ParseResult:
	next_i: int
	node: Node

@dataclass
class ChainResult:
	next_i: int
	nodes: List[Node]

def print_node_tree(node, depth):
	print('  ' * depth, end='')
	print(f'{node.name}', end='')
	if node.terminal:
		print(f'\t\t\tT[{node.content}]')
	else:
		print()
	for c in node.children:
		print_node_tree(c, depth + 1)

def parse_chained(tokens, i, *parsers):
	next_i = i
	nodes = []
	for p in parsers:
		parse_result = p(tokens, next_i)
		next_i = parse_result.next_i
		nodes.append(parse_result.node)
	return ChainResult(next_i=next_i, nodes=nodes)

def terminal_parser(name, token):
	def p(tokens, i):
		if i >= len(tokens):
			raise ValueError(f'failed to parse terminal {token}, reached end')
		if tokens[i] != token:
			raise ValueError(f'failed to parse terminal {token}, unexpected {tokens[i:i+5]}')
		return ParseResult(next_i=i+1, node=Node(name=name, terminal=True, content=tokens[i][1]))
	return p

def parse_RETURN_STMT(tokens, i):
	if i >= len(tokens):
		raise ValueError('failed to parse RETURN, reached end')
	if tokens[i] != (TokenType.KEYWORD, 'return'):
		raise ValueError(f'failed to parse RETURN, unexpected {tokens[i:i+4]}')

	chained = parse_chained(
		tokens,
		i,
		terminal_parser('RETURN', (TokenType.KEYWORD, 'return')),
		parse_EXPRESSION,
	)

	return ParseResult(next_i=chained.next_i, node=Node(name='RETURN_STMT', children=chained.nodes))

def parse_IF_STMT(tokens, i):
	if i >= len(tokens):
		raise ValueError('failed to parse IF, reached end')
	if tokens[i] != (TokenType.KEYWORD, 'if'):
		raise ValueError('failed to parse IF, unexpected')

	chained = parse_chained(
		tokens,
		i,
		terminal_parser('IF', (TokenType.KEYWORD, 'if')),
		parse_EXPRESSION,
		terminal_parser('START_BLOCK', (TokenType.START_BLOCK, '{')),
		parse_STATEMENTS,
		terminal_parser('END_BLOCK', (TokenType.END_BLOCK, '}')),
	)

	return ParseResult(next_i=chained.next_i, node=Node(name='IF_STMT', children=chained.nodes))

def parse_WHILE_STMT(tokens, i):
	if i + 3 >= len(tokens):
		raise ValueError('failed to parse WHILE, reached end')
	if tokens[i] != (TokenType.KEYWORD, 'while'):
		raise ValueError('failed to parse WHILE, unexpected')

	chained = parse_chained(
		tokens,
		i,
		terminal_parser('WHILE', (TokenType.KEYWORD, 'while')),
		parse_EXPRESSION,
		terminal_parser('START_BLOCK', (TokenType.START_BLOCK, '{')),
		parse_STATEMENTS,
		terminal_parser('END_BLOCK', (TokenType.END_BLOCK, '}')),
	)

	return ParseResult(next_i=chained.next_i, node=Node(name='WHILE_STMT', children=chained.nodes))


def parse_IDENTIFIERS_LIST(tokens, i):
	if i >= len(tokens):
		raise ValueError('failed to parse parse_IDENTIFIERS_LIST, reached end too soon')
	nodes = [Node(name='IDENTIFIER', terminal=True, content=tokens[i][1])]
	end = i + 1
	while end + 1 < len(tokens) and tokens[end][0] == TokenType.COMMA and tokens[end+1][0] == TokenType.IDENTIFIER:
		nodes += [Node(name='IDENTIFIER', terminal=True, content=tokens[end+1][1])]
		end += 2
	return ParseResult(next_i=end, node=Node(name='IDENTIFIERS_LIST', children=nodes))

def parse_FUNC_DEF(tokens, i):
	if i + 3 >= len(tokens):
		raise ValueError('failed to parse FUNC_DEF, reached end too soon')
	chained = parse_chained(
		tokens,
		i,
		terminal_parser('LAMBDA', (TokenType.KEYWORD, 'lambda')),
		parse_IDENTIFIERS_LIST,
		terminal_parser('START_BLOCK', (TokenType.START_BLOCK, '{')),
		parse_STATEMENTS,
		terminal_parser('END_BLOCK', (TokenType.END_BLOCK, '}')),
	)
	return ParseResult(next_i=chained.next_i, node=Node(name='FUNC_DEF', children=chained.nodes))

def parse_EXPRESSIONS_LIST(tokens, i):
	if i >= len(tokens):
		raise ValueError('failed to parse parse_EXPRESSIONS_LIST, reached end too soon')

	next_end = i
	while next_end < len(tokens) and tokens[next_end][0] not in (TokenType.R_PARENS, TokenType.END_STMT, TokenType.COMMA):
		next_end += 1
	if next_end >= len(tokens):
		raise ValueError('unexpected end of EXPR LIST')
	if next_end == i:
		return ParseResult(next_i=i, node=Node(name='EXPRESSIONS_LIST', children=[]))
	expr = parse_EXPRESSION(tokens, i)

	if expr.next_i < len(tokens) and tokens[expr.next_i][0] == TokenType.COMMA:
		chained = parse_chained(
			tokens,
			expr.next_i,
			terminal_parser('COMMA', (TokenType.COMMA, ',')),
			parse_EXPRESSIONS_LIST,
		)
		return ParseResult(next_i=chained.next_i, node=Node(name='EXPRESSIONS_LIST', children=[expr.node] + chained.nodes))
	return ParseResult(next_i=expr.next_i, node=Node(name='EXPRESSIONS_LIST', children=[expr.node]))



def parse_FUNC_CALL(tokens, i):
	if i + 3 >= len(tokens):
		raise ValueError('failed to parse parse_FUNC_CALL, reached end too soon')
	if tokens[i][0] != TokenType.IDENTIFIER:
		raise ValueError('failed to parse FUNC_CALL, must begin with identifier')
	chained = parse_chained(
		tokens,
		i,
		terminal_parser('IDENTIFIER', tokens[i]),
		terminal_parser('L_PARENS', (TokenType.L_PARENS, '(')),
		parse_EXPRESSIONS_LIST,
		terminal_parser('R_PARENS', (TokenType.R_PARENS, ')')),
	)
	return ParseResult(next_i=chained.next_i, node=Node(name='FUNC_CALL', children=chained.nodes))


def parse_EXPRESSION(tokens, i):
	if i + 1 >= len(tokens):
		raise ValueError('failed to parse EXPRESSION, reached end too soon')

	next_i = i + 1
	if tokens[i][0] == TokenType.IDENTIFIER:
		if tokens[i+1][0] == TokenType.L_PARENS:
			fc = parse_FUNC_CALL(tokens, i)
			next_i = fc.next_i
			current = fc.node
		else:
			current = Node(name='IDENTIFIER', terminal=True, content=tokens[i][1])
	elif tokens[i][0] == TokenType.INT_LITERAL:
		current = Node(name='INT_LITERAL', terminal=True, content=tokens[i][1])
	elif tokens[i] == (TokenType.KEYWORD, 'lambda'):
		return parse_FUNC_DEF(tokens, i)
	else:
		raise ValueError(f'failed to parse EXPRESSION, got {tokens[i:i+5]}')

	if next_i < len(tokens) and tokens[next_i][0] == TokenType.OPERATOR:
		operator_node = Node(name='OPERATOR', terminal=True, content=tokens[next_i][1])
		next_result = parse_EXPRESSION(tokens, next_i + 1)
		return ParseResult(next_i=next_result.next_i, node=Node(name='EXPRESSION', children=[
			current,
			operator_node,
			next_result.node
			]
		))
	elif next_i < len(tokens) and tokens[next_i][0] in (TokenType.END_STMT, TokenType.START_BLOCK, TokenType.R_PARENS, TokenType.COMMA):
		return ParseResult(next_i=next_i, node=Node(name='EXPRESSION', children=[current]))
	else:
		raise ValueError('failed to parse EXPRESSION, unexpected next token')


def parse_STATEMENT(tokens, i):
	if i >= len(tokens):
		raise ValueError('failed to parse STATEMENT, reached end')

	if tokens[i][0] == TokenType.KEYWORD:
		if tokens[i][1] not in ('if', 'return', 'while'):
			raise ValueError(f'failed to parse STATEMENTS, bad keyword {tokens[i]}')
	elif tokens[i][0] != TokenType.IDENTIFIER:
		raise ValueError('failed to parse STATEMENTS, want identifier or keyword')

	if tokens[i] == (TokenType.KEYWORD, 'if'):
		result = parse_IF_STMT(tokens, i)
	elif tokens[i] == (TokenType.KEYWORD, 'return'):
		result = parse_RETURN_STMT(tokens, i)
	elif tokens[i] == (TokenType.KEYWORD, 'while'):
		result = parse_WHILE_STMT(tokens, i)
	else:
		result = parse_EXPRESSION(tokens, i)
	return ParseResult(next_i=result.next_i, node=Node(name='STATEMENT', children=[result.node]))

def parse_END_STMT(tokens, i):
	if i >= len(tokens) or tokens[i][0] != TokenType.END_STMT:
		raise ValueError(f'failed to parse END_STMT: expected newline, got: {tokens[i:i+5]}')
	return ParseResult(next_i=i+1, node=Node(name='END_STMT', terminal=True, content=';'))

def parse_STATEMENTS(tokens, i):
	if i == len(tokens) or tokens[i][0] == TokenType.END_BLOCK:
		return ParseResult(next_i=i, node=Node(name='STATEMENTS', children=[]))

	if tokens[i][0] == TokenType.KEYWORD:
		if tokens[i][1] not in ('if', 'return', 'while'):
			raise ValueError(f'failed to parse STATEMENTS, bad keyword {tokens[i]}')
	elif tokens[i][0] != TokenType.IDENTIFIER:
		raise ValueError(f'failed to parse STATEMENTS, want identifier or keyword, got {tokens[i:i+10]}')

	chained = parse_chained(
		tokens,
		i,
		parse_STATEMENT,
		parse_END_STMT,
		parse_STATEMENTS,
	)

	return ParseResult(next_i=chained.next_i, node=Node(name='STATEMENTS', children=chained.nodes))


def parse_S(tokens, i):
	s = parse_STATEMENTS(tokens, i)
	return ParseResult(next_i=s.next_i, node=Node(name='S', children=[s.node]))

def clean_and_flatten_tree(node):
	# removes: END_STMTs
	# flatten the following recursive non-terminals: STATEMENTS, EXPRESSIONS_LIST, STATEMENTS_LIST
	
	node = dataclasses.replace(node, children=[
		clean_and_flatten_tree(c) for c in node.children
		if c.name not in ['END_STMT', 'START_BLOCK', 'END_BLOCK', 'L_PARENS', 'R_PARENS']
	])

	if node.name == 'STATEMENTS':
		if node.children:
			node = dataclasses.replace(node, children=[node.children[0]] + node.children[1].children)
	elif node.name == 'EXPRESSIONS_LIST':
		if len(node.children) == 3:
			node = dataclasses.replace(node, children=[node.children[0]] + node.children[2].children)
	elif node.name == 'EXPRESSION':
		if len(node.children) == 3 and node.children[2].name == 'EXPRESSION' and len(node.children[2].children) == 1:
			node = dataclasses.replace(node, children=node.children[:2] + node.children[2].children)
	elif node.name in ('FUNC_DEF', 'IF_STMT', 'RETURN_STMT', 'WHILE_STMT'):
		node = dataclasses.replace(node, children=node.children[1:])
	return node


def preprocess_tokens(tokens: List[tuple[TokenType, str]]) -> List[tuple[TokenType, str]]:
	new_tokens = []
	depth = 0
	i = 0
	is_line_start = True
	# skip leading newlines
	while i < len(tokens) and tokens[i][0] == TokenType.NEWLINE:
		i += 1

	while i < len(tokens):
		if tokens[i][0] == TokenType.NEWLINE:
			new_tokens.append((TokenType.END_STMT, ';'))
			i += 1
			is_line_start = True

			while i < len(tokens) and tokens[i][0] == TokenType.NEWLINE:
				i += 1

		elif tokens[i][0] == TokenType.COLON:
			# must be followed by newline
			if i + 1 >= len(tokens) or tokens[i+1][0] != TokenType.NEWLINE:
				raise ValueError('colon must be followed by newline')
			new_tokens.append((TokenType.START_BLOCK, '{'))
			i += 2
			depth += 1
			is_line_start = True
		elif tokens[i][0] == TokenType.SPACE:
			if is_line_start:
				# count leading spaces
				j = i + 1
				while j < len(tokens) and tokens[j][0] == TokenType.SPACE:
					j += 1
				count = j - i
				if count == depth * 2:
					# all good, keep depth
					pass
				elif depth and count == (depth - 1) * 2:
					depth -= 1
					new_tokens.append((TokenType.END_BLOCK, '}'))
					new_tokens.append((TokenType.END_STMT, ';'))
				else:
					raise ValueError(f'bad number of leading spaces at {tokens[i:i+10]}')
				i += count
			else:
				i += 1
			is_line_start = False
		else:
			if is_line_start:
				for d in range(depth):
					new_tokens.append((TokenType.END_BLOCK, '}'))
					new_tokens.append((TokenType.END_STMT, ';'))
					depth -= 1
			new_tokens.append(tokens[i])
			i += 1
			is_line_start = False
	if new_tokens and new_tokens[-1][0] != TokenType.END_STMT:
		new_tokens.append((TokenType.END_STMT, ';'))
	return new_tokens

def test_preprocess():
	t = tokenizer.tokenize(hw1.SAMPLE_PROGRAMS[0][1])
	p = preprocess_tokens(t)
	for l in p:
		print(l)

def test_fib():
	t = tokenizer.tokenize('''
fib = lambda n, unused:
  if n == 0:
    return n
  if n == 1:
    return n
  return fib(n-1) + fib(n-2)

print(fib(5, 1))
''')
	p = preprocess_tokens(t)
	for l in p:
		print(l)
	result = parse_S(p, 0)
	if result.next_i != len(p):
		print('ERROR did not reach end')
	flat_result = clean_and_flatten_tree(result.node)
	print_node_tree(flat_result, 0)

def test_print_square():
	t = tokenizer.tokenize('''
print_square = lambda n:
  i = 0
  while i < n:
    j = 0
    while j < n:
      print(1)
      j += 1
    i += 1

print_square(4)
''')
	p = preprocess_tokens(t)
	for l in p:
		print(l)
	result = parse_S(p, 0)
	if result.next_i != len(p):
		print('ERROR did not reach end')
	flat_result = clean_and_flatten_tree(result.node)
	print_node_tree(flat_result, 0)


if __name__ == '__main__':
	test_fib()
