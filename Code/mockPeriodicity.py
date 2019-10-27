from datetime import datetime
from datetime import date as dt
import math

def mock_match(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return (x1==x2 and y1==y2)

def mock_EDR(t1, t2):
	m, n = len(t1), len(t2)
	matcher = [[0 for x in range(n+1)] for y in range(m+1)]
	backtrack = [[(-1,-1) for x in range(n+1)] for y in range(m+1)]
	maxscore = 0
	endposition = (0, 0)
	for i in range(1, m+1):
		for j in range(1, n+1):
			gapAbove = matcher[i-1][j]-2
			gapLeft = matcher[i][j-1]-2
			matching = matcher[i-1][j-1] + (5 if mock_match(t1[i-1],t2[j-1]) else -3)
			score = max(0, max(gapAbove, gapLeft, matching)) # if negative, convert to 0
			matcher[i][j] = score

			# set backtrack table
			if score == matching:
				backtrack[i][j] = (i-1, j-1)
			elif score == gapAbove:
				backtrack[i][j] = (i-1, j)
			elif score == gapLeft:
				backtrack[i][j] = (i, j-1)
			else:
				backtrack[i][j] = (-1, -1)

			# update maxscore
			if score > maxscore:
				maxscore = score
				endposition = (i, j)
	return maxscore

def main():
	fake_trajectories = []
	with open("../FakeTrajectories.csv", "r") as f:
		lines = f.readlines();
		last_trajectory = 0
		for line in lines[1:]:
			values = line.split(",")
			t_number = int(values[0])
			x = int(values[1])
			y = int(values[2])
			if t_number != last_trajectory:
				trajectory = []
				trajectory.append((x,y))
				fake_trajectories.append(trajectory)
				last_trajectory = t_number
			else:
				fake_trajectories[-1].append((x,y))

	for i in range(1, len(fake_trajectories)):
		print(mock_EDR(fake_trajectories[0], fake_trajectories[i]))

	# 0: base
	# 1: match * 60 + gap * 20 -> 300 (walk + stay)
	# 2: match * 40 + mismatch * 20 -> 200 (walk + digress)
	# 3: match * 20 + gap * 20 + match * 40 -> 260 (walk + stay + walk)
	# 4: match * 20 + mismatch * 20 + match * 20 -> 140 (walk + digress + walk)
	# 5: match * 20 + (gap + match) * 20 +  match * 20 -> 260 (walk + slow down + walk)
	# 6: match * 20 + gap * 10 + mismatch * 20 + match * 20 -> 120 (walk + stay + digress + walk)
	# 7: match * 20 + mimatch * 10 + match * 20 + mimatch * 10 -> 170 (walk + digress + walk + digress)

main()