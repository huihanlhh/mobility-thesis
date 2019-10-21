from bjcoordinates import bjcoordinates
import csv
from collections import defaultdict
from datetime import datetime, tzinfo

west = 115.4237
east = 117.507
north = 41.0607
south = 39.4395


def read_csv(fname):
	values = []
	with open(fname) as f:
		reader = csv.DictReader(f)
		for row in reader:
			lon = float(row["longtitude"])
			lat = float(row["latitude"])

			if (pointinbj(lon,lat)):
				timeStamp = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S").timestamp() + 8 * 3600 # timestamp, float, round to seconds from 1970/01/01; converted to BJ time
				values.append((lat,lon,timeStamp))
	f.close()
	
	return values


def pointinbj(x,y,poly = bjcoordinates):
	if x < west or x > east or y < south or y > north:
		return False

	n = len(poly)
	is_inside = False

	x1,y1 = poly[0]
	for i in range(n+1):
		x2,y2 = poly[i % n]
		if y > min(y1,y2):
			if y <= max(y1,y2):
				if x <= max(x1,x2):
					if y1 != y2:
						xints = (y-y1)*(x2-x1)/(y2-y1)+x1
					if x1 == x2 or x <= xints:
						is_inside = not is_inside
		x1,y1 = x2,y2

	return is_inside

if __name__ == '__main__':
	read_csv("../Data_CSV/181/20080314025755.csv")