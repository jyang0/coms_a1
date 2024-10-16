



def StrMatch(s):
	def matcher(target, start, end):
		i = start
		for c in s:
			if i >= end or target[i] != c:
				return False, 0
			i += 1
		return True, len(s)
	return matcher


def Or(*m):
	def matcher(target, start, end):
		for mm in m:
			matched, result = mm(target, start, end)
			if matched:
				return True, result
		return False, 0
	return matcher


def AnyCharIn(chars):
	def matcher(target, start, end):
		if start < end and target[start] in chars:
			return True, 1
		return False, 0
	return matcher

def AnyCharNotIn(chars):
	def matcher(target, start, end):
		if start < end and target[start] not in chars:
			return True, 1
		return False, 0
	return matcher

def OnceOrMore(m):
	def matcher(target, start, end):
		matched, result = m(target, start, end)
		if not matched:
			return False, 0
		matched, next_result = m(target, start + result, end)
		while matched:
			result += next_result
			matched, next_result = m(target, start + result, end)
		return True, result
	return matcher

def ZeroOrMore(m):
	def matcher(target, start, end):
		matched, result = m(target, start, end)
		if not result:
			return True, 0
		matched, next_result = m(target, start + result, end)
		while matched:
			result += next_result
			matched, next_result = m(target, start + result, end)
		return True, result
	return matcher

def SeqMatch(*m):
	def matcher(target, start, end):
		i = start
		for mm in m:
			matched, result = mm(target, i, end)
			if not matched:
				return False, 0
			i += result
		return True, i - start
	return matcher
