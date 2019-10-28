from bjPOI import read_csv
from datetime import datetime
from datetime import date as dt
import numpy as np
import matplotlib.pyplot as plt
import math

MATCHING_DISTANCE = 0.1
MATCHING_TIME_FRAME = 3

def matchTime(t1, t2):
	return abs(datetime.fromtimestamp(t1).hour - datetime.fromtimestamp(t2).hour)<= MATCHING_TIME_FRAME # time difference no greater than 3 hours
	# return (0 <= datetime.fromtimestamp(t1).hour < 3 and 0 <= datetime.fromtimestamp(t2).hour < 3) or (3 <= datetime.fromtimestamp(t1).hour < 6 and 3 <= datetime.fromtimestamp(t2).hour < 6) or (6 <= datetime.fromtimestamp(t1).hour < 9 and 6 <= datetime.fromtimestamp(t2).hour < 9) or (9 <= datetime.fromtimestamp(t1).hour < 12 and 9 <= datetime.fromtimestamp(t2).hour < 12) or (12 <= datetime.fromtimestamp(t1).hour < 15 and 12 <= datetime.fromtimestamp(t2).hour < 15) or (15 <= datetime.fromtimestamp(t1).hour < 18 and 15 <= datetime.fromtimestamp(t2).hour < 18) or (18 <= datetime.fromtimestamp(t1).hour < 21 and 18 <= datetime.fromtimestamp(t2).hour < 21) or (21 <= datetime.fromtimestamp(t1).hour < 24 and 21 <= datetime.fromtimestamp(t2).hour < 24)
	# return (1 <= datetime.fromtimestamp(t1).hour < 4 and 1 <= datetime.fromtimestamp(t2).hour < 4) or (4 <= datetime.fromtimestamp(t1).hour < 7 and 4 <= datetime.fromtimestamp(t2).hour < 7) or (7 <= datetime.fromtimestamp(t1).hour < 10 and 7 <= datetime.fromtimestamp(t2).hour < 10) or (10 <= datetime.fromtimestamp(t1).hour < 13 and 10 <= datetime.fromtimestamp(t2).hour < 13) or (13 <= datetime.fromtimestamp(t1).hour < 16 and 13 <= datetime.fromtimestamp(t2).hour < 16) or (16 <= datetime.fromtimestamp(t1).hour < 19 and 16 <= datetime.fromtimestamp(t2).hour < 19) or (19 <= datetime.fromtimestamp(t1).hour < 22 and 19 <= datetime.fromtimestamp(t2).hour < 22) or ((22 <= datetime.fromtimestamp(t1).hour < 24 or datetime.fromtimestamp(t1).hour == 0)  and (20 <= datetime.fromtimestamp(t2).hour < 23 or datetime.fromtimestamp(t2).hour == 0))


def match(gps1, gps2):
    lat1, lon1, t1 = gps1
    lat2, lon2, t2 = gps2
    coord1 = (lat1,lon1)
    coord2 = (lat2,lon2)

    r = 6371
    dlat = (lat2-lat1) * (math.pi/180)
    dlon = (lon2-lon1) * (math.pi/180)

    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(lat1 * (math.pi/180)) * math.cos(lat2 * (math.pi/180)) * math.sin(dlon/2) * math.sin(dlon/2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = r * c

    return d <= MATCHING_DISTANCE and matchTime(t1, t2)

def trajectory_by_day(fname):
	trajectories = {}
	for i in range(1,8):
		trajectories[i] = []
	trajectory = read_csv(fname)
	print("Read CSV file")
	start = False
	last_date = dt.min
	last_day = 0
	for data_tup in trajectory:
		day = datetime.fromtimestamp(data_tup[2]).isoweekday()
		if day == last_day:
			date = dt.fromtimestamp(data_tup[2])
			if date == last_date:
				trajectories[day][-1].append(data_tup)
			else:
				one_trajectory = [data_tup]
				trajectories[day].append(one_trajectory)
				last_date = date
		else:
			date = dt.fromtimestamp(data_tup[2])
			one_trajectory = [data_tup]
			trajectories[day].append(one_trajectory)
			last_date = date
			last_day = day

	return trajectories

# gap -2, match +5, mismatch -3
def EDR(t1, t2, mt, ms, gap):
	m, n = len(t1), len(t2)
	matcher = [[0 for x in range(n+1)] for y in range(m+1)]
	backtrack = [[(-1,-1) for x in range(n+1)] for y in range(m+1)]
	maxscore = 0
	endposition = (0, 0)
	for i in range(1, m+1):
		for j in range(1, n+1):
			gapAbove = matcher[i-1][j]+gap
			gapLeft = matcher[i][j-1]+gap
			matching = matcher[i-1][j-1] + (mt if match(t1[i-1],t2[j-1]) else ms)
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

	tempi, tempj = endposition
	while backtrack[tempi][tempj] != (-1, -1):
		tempi, tempj = backtrack[tempi][tempj]

	# calculate time duration of both subtrajectories
	start1 = datetime.fromtimestamp(t1[tempi][2]).isoformat()
	end1 =datetime.fromtimestamp(t1[endposition[0]-1][2]).isoformat()
	start2 = datetime.fromtimestamp(t2[tempj][2]).isoformat()
	end2 =datetime.fromtimestamp(t2[endposition[1]-1][2]).isoformat()
	timeduration1 = t1[endposition[0]-1][2] - t1[tempi][2] # in seconds
	timeduration2 = t2[endposition[1]-1][2] - t2[tempj][2] # in seconds

	return (maxscore, start1, end1, timeduration1, start2, end2, timeduration2)

def EDR_all(traj_dict, fileout, day, mt, ms, gap):
	trajectories = traj_dict[day]
	duration_score_set = []
	duration_score_set.append([])
	duration_score_set.append([])
	# with open (fileout, "w") as f:
	for i in range(len(trajectories)-1):
		for j in range(i+1, len(trajectories)-1):
			score, start1, end1, duration1, start2, end2, duration2 = EDR(trajectories[i], trajectories[j], mt, ms, gap)
			# line = "Score: " + str(score) + " Duration 1: " + str(duration1) + "s (from " + str(start1) + " to " + str(end1) + ") Duration 2: " + str(duration2) + "s (from " + str(start2) + " to " + str(end2) + ")\n"
			# print(line)
			# f.write(line)
			duration_score_set[0].append(min(duration1, duration2))
			duration_score_set[1].append(score)
	return duration_score_set

def wrapper(filein, plotout, mt, ms, gap):
	traj_dict = trajectory_by_day(filein)
	all_duration_score_set = []
	all_duration_score_set.append([])
	all_duration_score_set.append([])
	monday = EDR_all(traj_dict, "../Result/Periodicity/000/Monday_532.csv",1, mt, ms, gap)
	all_duration_score_set[0].extend(monday[0])
	all_duration_score_set[1].extend(monday[1])
	tuesday = EDR_all(traj_dict, "../Result/Periodicity/000/Tuesday_532.csv",2, mt, ms, gap)
	all_duration_score_set[0].extend(tuesday[0])
	all_duration_score_set[1].extend(tuesday[1])
	wednesday = EDR_all(traj_dict, "../Result/Periodicity/000/Wednesday_532.csv",3, mt, ms, gap)
	all_duration_score_set[0].extend(wednesday[0])
	all_duration_score_set[1].extend(wednesday[1])
	thursday = EDR_all(traj_dict, "../Result/Periodicity/000/Thursday_532.csv",4, mt, ms, gap)
	all_duration_score_set[0].extend(thursday[0])
	all_duration_score_set[1].extend(thursday[1])
	friday = EDR_all(traj_dict, "../Result/Periodicity/000/Friday_532.csv",5, mt, ms, gap)
	all_duration_score_set[0].extend(friday[0])
	all_duration_score_set[1].extend(friday[1])
	saturday = EDR_all(traj_dict, "../Result/Periodicity/000/Saturday_532.csv",6, mt, ms, gap)
	all_duration_score_set[0].extend(saturday[0])
	all_duration_score_set[1].extend(saturday[1])
	sunday = EDR_all(traj_dict, "../Result/Periodicity/000/Sunday_532.csv",7, mt, ms, gap)
	all_duration_score_set[0].extend(sunday[0])
	all_duration_score_set[1].extend(sunday[1])

	data = np.asarray(all_duration_score_set)
	x,y = data
	plt.scatter(x,y)
	string = "Person " + str(filein[-7:-4]) + ", Score Scale(" + str(mt) + "," + str(ms) + "," + str(gap) + ")"
	plt.title(string)
	plt.xlabel('Duration')
	plt.ylabel('Score')
	plt.savefig(plotout)


def main():
	wrapper("../Data/DataByPerson/000.csv", "../Result/Periodicity/000/distribution532.png",5, -3, -2)
	# traj_dict = trajectory_by_day("../Data/DataByPerson/000.csv")
	# for key in traj_dict:
	# 	print(key, len(traj_dict[key]))
	# for t in trajectories:
	# 	print(len(t))
	# print(EDR(trajectories[0], trajectories[1]))
	# print(trajectories[0][0], trajectories[0][-1], trajectories[1][0], trajectories[1][-1])

	
if __name__ == "__main__":
	main()

