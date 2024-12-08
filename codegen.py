from parser import *
import os
import dataclasses

ALWAYS_ALLOWED_SYMBOLS = ['print']

def codegen(node, content, symbols, symbol_defs, symbol_refs, depth):
	if node.name == 'S':
		codegen(node.children[0], content, symbols, symbol_defs, symbol_refs, depth)
	elif node.name == 'EXPRESSION' and len(node.children) == 3 and node.children[1].content == '=' and node.children[2].name == 'FUNC_DEF':
		params = list(identifier_node.content for identifier_node in node.children[2].children[0].children)
		if len(params) != len(set(params)):
			raise ValueError(f'Duplicate func params: {params} for {node.content}')
		old_symbols = set(symbols)
		old_symbol_defs = dict(symbol_defs)
		symbols.clear()
		symbol_defs.clear()
		symbols.add(node.children[0].content)
		symbols.update(params)

		content.append('def ')
		content.append(node.children[0].content)
		content.append('(')
		params = [p for p in params if p not in old_symbols]
		content.append(','.join(params))
		content.append('):\n')
		codegen(node.children[2].children[1], content, symbols, symbol_defs, symbol_refs, depth + 1)

		# remove dead vars
		remove_ranges = reversed(sorted([v for k, v in symbol_defs.items() if k not in symbol_refs]))
		for r in remove_ranges:
			del content[r[0]:r[1]]

		symbols.clear()
		symbols.update(old_symbols)
		symbols.add(node.children[0].content)
		symbol_defs.clear()
		symbol_defs.update(old_symbol_defs)
	elif node.name in ('STATEMENTS', 'EXPRESSION'):
		if node.name == 'EXPRESSION' and len(node.children) == 3 and node.children[0].name == 'INT_LITERAL' and node.children[2].name == 'INT_LITERAL':
			result = eval(f'{node.children[0].content} {node.children[1].content} {node.children[2].content}')
			node.children.pop()
			node.children.pop()
			node.children[0] = dataclasses.replace(node.children[0], content=f'{result}')
		if node.name == 'EXPRESSION' and len(node.children) == 3 and node.children[1].content == '=' and node.children[0].name == 'IDENTIFIER':
			range_start = len(content)
			content.append(node.children[0].content)
			content.append('=')
			codegen(node.children[2], content, symbols, symbol_defs, symbol_refs, depth)
			range_end = len(content)
			symbols.add(node.children[0].content)
			symbol_defs[node.children[0].content] = (range_start, range_end)
		else:
			for s in node.children:
				codegen(s, content, symbols, symbol_defs, symbol_refs, depth)
	elif node.name == 'STATEMENT':
		content.append(' ' * (depth * 4))
		codegen(node.children[0], content, symbols, symbol_defs, symbol_refs, depth)
		content.append('\n')
	elif node.name == 'WHILE_STMT':
		content.append('while ')
		codegen(node.children[0], content, symbols, symbol_defs, symbol_refs, depth)
		content.append(':\n')
		codegen(node.children[1], content, symbols, symbol_defs, symbol_refs, depth + 1)
	elif node.name == 'IF_STMT':
		content.append('if ')
		codegen(node.children[0], content, symbols, symbol_defs, symbol_refs, depth)
		content.append(':\n')
		codegen(node.children[1], content, symbols, symbol_defs, symbol_refs, depth + 1)
	elif node.name == 'RETURN_STMT':
		content.append('return ')
		codegen(node.children[0], content, symbols, symbol_defs, symbol_refs, depth)
	elif node.name == 'FUNC_CALL':
		codegen(node.children[0], content, symbols, symbol_defs, symbol_refs, depth)
		content.append('(')
		codegen(node.children[1], content, symbols, symbol_defs, symbol_refs, depth)
		if node.children[0].content == 'print' and node.children[1].children:
			content.append(', end=""')
		content.append(')')
	elif node.name in ('EXPRESSIONS_LIST', 'IDENTIFIERS_LIST'):
		for i in range(len(node.children)):
			codegen(node.children[i], content, symbols, symbol_defs, symbol_refs, depth)
			if i < len(node.children) - 1:
				content.append(', ')
	elif node.terminal:
		if node.name == 'IDENTIFIER' and node.content not in symbols and node.content not in ALWAYS_ALLOWED_SYMBOLS:
			raise ValueError(f'Encountered unknown identifier: {node}, known symbols: {symbols}')
		if node.name == 'IDENTIFIER':
			symbol_refs.add(node.content)
		content.append(node.content)
	else:
		raise ValueError(f'Unknown node {node.name}')

def gen_code(root_node):
	content = []
	symbols = set()
	symbol_defs = {}
	symbol_refs = set()
	codegen(root_node, content, symbols, symbol_defs, symbol_refs, 0)
	return ''.join(content)


def execute(lines, n):
	with open(f'__tmp_gen_{n}.py', 'w') as f:
		f.write(lines)
	cmd = f'python __tmp_gen_{n}.py'
	print(f'Now executing: {cmd}...\n')
	code = os.system(cmd)
	print()
	print(f'Execution finished with status: {code}')

def compile_and_execute(code, n=0):
	print('Tokenizing...')
	t = tokenizer.tokenize(code)

	print('Completed tokenization.')
	print('Parsing...')
	p = preprocess_tokens(t)
	result = parse_S(p, 0)
	if result.next_i != len(p):
		raise ValueError('ERROR did not reach end')
	flat_result = clean_and_flatten_tree(result.node)
	print('Completed parsing.')
	print('Generating code...')
	translated_code = gen_code(flat_result)
	print('Completed codegen.')
	execute(translated_code, n)

if __name__ == '__main__':
	compile_and_execute('''
fib = lambda n, unused:
  if n == 0:
    return n
  if n == 1:
    return n
  return fib(n-1, unused) + fib(n-2, unused)

print(fib(7, 1))
''')

