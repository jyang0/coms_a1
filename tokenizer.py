from enum import IntEnum
from enum import auto
from typing import List

import matcher

class TokenType(IntEnum):
	KEYWORD = auto()
	OPERATOR = auto()
	IDENTIFIER = auto()
	L_PARENS = auto()
	R_PARENS = auto()
	COLON = auto()
	COMMA = auto()
	SPACE = auto()
	NEWLINE = auto()
	STR_LITERAL = auto()
	INT_LITERAL = auto()
	# virtual tokens
	END_STMT = auto()
	START_BLOCK = auto()
	END_BLOCK = auto()

MATCHERS = {
 	# r'for|in|range|print|lambda',
	TokenType.KEYWORD: matcher.Or(
		matcher.StrMatch('if'),
		matcher.StrMatch('while'),
		matcher.StrMatch('lambda'),
		matcher.StrMatch('return'),
	),
	# r'[+]|[-]|[*]|[/]',
	TokenType.OPERATOR: matcher.Or(
		matcher.StrMatch('+='),
		matcher.StrMatch('-='),
		matcher.StrMatch('=='),
		matcher.StrMatch('!='),
		matcher.StrMatch('='),
		matcher.StrMatch('+'),
		matcher.StrMatch('-'),
		matcher.StrMatch('*'),
		matcher.StrMatch('/'),
		matcher.StrMatch('<'),
		matcher.StrMatch('>'),
	),
	# r'[a-z_]+',
	TokenType.IDENTIFIER: matcher.OnceOrMore(
		matcher.AnyCharIn('abcdefghijklmnopqrstuvwxyz_')
	),
	TokenType.L_PARENS: matcher.StrMatch('('),
	TokenType.R_PARENS: matcher.StrMatch(')'),
	TokenType.COLON: matcher.StrMatch(':'),
	TokenType.COMMA: matcher.StrMatch(','),
	# r"'[^']*'",
	TokenType.STR_LITERAL: matcher.SeqMatch(
		matcher.StrMatch("'"),
		matcher.ZeroOrMore(matcher.AnyCharNotIn("'")),
		matcher.StrMatch("'"),
	),
	# r"[0-9]+",
	TokenType.INT_LITERAL: matcher.OnceOrMore(
		matcher.AnyCharIn('0123456789')
	),
	TokenType.SPACE: matcher.Or(
		matcher.StrMatch(' '),
		matcher.StrMatch('\t'),
	),
	TokenType.NEWLINE: matcher.SeqMatch(
		matcher.ZeroOrMore(matcher.StrMatch("\r")),
		matcher.StrMatch("\n"),
	),
}

def tokenize(content: str) -> List[tuple[TokenType, str]]:
	result = []
	i = 0
	while i < len(content):
		# try parsing on every MATCHER starting at i, take longest
		matched_longest = ''
		matched_type = None

		for m in sorted(MATCHERS.keys()):
			matched, matched_len = MATCHERS[m](content, i, len(content))
			if matched and matched_len > len(matched_longest):
				matched_longest = content[i:i+matched_len]
				matched_type = m
		if not matched_type:
			raise ValueError(f'ERROR: tokenize failed starting at: {content[i:i+100]}')

		result.append((matched_type, matched_longest))
		i += len(matched_longest)


	return result
