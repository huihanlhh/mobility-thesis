def mergeBorder(lst1, lst2):
	""" we compare each coordinate of lst1 with lst2 and create new list out of the two
	the end point of repitition in lst1 would be the new start of the new list
	"""

	#because last coordinate equals first coordinate
	l1 = lst1[:-1]
	l2 = lst2[:-1]

	result = []
	repeat = False

	s1 = n1 = s2 = n2 = -1

	for index1 in range(len(l1)):
		if not repeat:
			try:
				s2 = l2.index(l1[index1])
				s1 = index1
				repeat = True

			except ValueError:
				pass
		else:
			try:
				l2.index(l1[index1])

			except ValueError:
				n1 = index1-1
				n2 = l2.index(l1[n1])
				repeat = False

	if s1 == s2 == n1 == n2 == -1:
		raise ValueError

	if n1 == -1:
		n1 = len(l1) - 1
	if n2 == -1:
		n2 = 0

	# n1 inclusive, s1 exclusive
	if (s1 <= n1):
		first = l1[n1:] + l1[:s1]
	else:
		first = l1[n1:s1]

	# n2 exclusive, s2 inclusive
	if (n2 <= s2):
		second = l2[s2:] + l2[:n2]
	else:
		second = l2[s2:n2]

	result = first + second + [first[0]]

	return result




