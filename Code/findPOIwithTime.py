import sys, os, math, sqlite3, os.path
from bjPOI import read_csv
from math import sin, cos, sqrt, atan2, radians
import geopy.distance
from datetime import datetime




def find_distance(gps1, gps2):
    lat1, lon1, t1 = gps1
    lat2, lon2, t2 = gps2
    coord1 = (lat1,lon1)
    coord2 = (lat2,lon2)

    return (geopy.distance.distance(coord1,coord2).km)

def find_POIs(data_tup):
    start = datetime.now()
    global mintime                       # in seconds. Min Time, for a point to be considered as POI, if spent there
    global eps                           # Maximum distance between any two points within a Point of Interest

    index = 0
    
    valid = True
    pois_with_time = []

    while index < len(data_tup):        # check every point in the list
        currCord = data_tup[index]
        valid = True
        poi_cand = [currCord]           # start checking neighborhood
        i = index + 1                   # start from the next point after current point
        while i < len(data_tup):
            for point in poi_cand:      # check compatibility with every point in existing neighborhood
                if find_distance(point,data_tup[i]) > eps: # stop checking and return once the point exceeds distance
                    valid = False
                    break
            if valid:                   # if still valid, append the point to neighborhood
                poi_cand.append(data_tup[i])
                i+=1                    # continue looking at the next point
            else:                       # if not valid anymore, break from while loop.
                break
        if (poi_cand[-1][2] - poi_cand[0][2]) >= mintime:
            day = datetime.fromtimestamp(poi_cand[0][2]).isoweekday()
            time = datetime.fromtimestamp(poi_cand[0][2]).time()
            pois_with_time.append((poi_cand,day,time))
            print("Old: No. of points in POI:", len(poi_cand), "Starting from: Day", day, time)

        index = i
    end = datetime.now()
    print("Old: Total Num of POI:", len(pois_with_time))
    print("Runtime:", end-start)
    return pois_with_time

def find_POIs_jump(data_tup):
    start = datetime.now()
    global mintime
    global eps

    POIs = []

    ia = 0
    ib = 1
    #find a good B to start with
    while ib < len(data_tup) and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
        ib += 1

    while ia < len(data_tup) and ib < len(data_tup):
        if (data_tup[ib][2] - data_tup[ia][2]) < mintime:
            break
        # go to next group
        if find_distance(data_tup[ia],data_tup[ib]) > eps:
            ia = (ia+ib)//2+1
            while ib < len(data_tup)-1 and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
                ib += 1
        # start testing for POI
        else:
            isPOI = True
            for gps in data_tup[ia+1:ib]:
                if (find_distance(gps,data_tup[ia]) > eps) or (find_distance(gps,data_tup[ib]) > eps):
                    isPOI = False
                    break
            if isPOI:
                day = datetime.fromtimestamp(data_tup[ia][2]).isoweekday()
                time = datetime.fromtimestamp(data_tup[ia][2]).time()
                start_at = data_tup[ia][2]
                leave_at = data_tup[ib][2]
                #center = list(map(lambda l: sum(l)/len(l), list(zip(*data_tup[ia:ib+1]))))
                POIs.append((data_tup[ia:ib+1],day,time,start_at,leave_at))
                ia = ib+1
                while ib < len(data_tup)-1 and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
                    ib += 1
            else:
                ia = (ia+ib)//2+1
                while ib < len(data_tup)-1 and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
                    ib += 1
    end = datetime.now()
    print("Jump: Total num of POI jumped:", len(POIs))
    print("Runtime:",(end-start))
    
    for a in range(len(POIs)-1):
        poi_cand = POIs[a]
        POI = poi_cand[0]
        recall = 0
        for i in range(len(POI)-1):
            for j in range(i,len(POI)):
                if find_distance(POI[i],POI[j]) > eps:
                    recall += 1
        print("Length:",len(POI),"Accuracy:", (1-recall/(len(POI)**2)),"Starting from Day",poi_cand[1],poi_cand[2])
        if a < len(POIs) - 1:
            print("Time Difference: ", POIs[a+1][3] - POIs[a][4])



    return POIs


def find_POIs_jump_new(data_tup):
    start = datetime.now()
    global mintime
    global eps

    POIs = []

    ia = 0
    ib = 1
    #find a good B to start with
    while ib < len(data_tup) and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
        ib += 1

    while ia < len(data_tup) and ib < len(data_tup):
        # end of trajectory
        if (data_tup[ib][2] - data_tup[ia][2]) < mintime:
            break
        # go to next group
        if find_distance(data_tup[ia],data_tup[ib]) > eps:
            ia = (ia+ib)//2+1
            while ib < len(data_tup)-1 and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
                ib += 1
        #start testing for POI
        else:
            isPOI = True
            A = data_tup[ia]
            B = data_tup[ib]
            maxPoint = A # the point that has the farthest distance from A and B
            maxDistance = find_distance(A,B) # farthest distance
            for i in range(ia+1,ib):
                gps = data_tup[i]
                distA = find_distance(gps,A)
                distB = find_distance(gps,B)
                if (distA > eps) or (distB > eps):
                    ia = (ia+ib)//2+1
                    while ib < len(data_tup)-1 and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
                        ib += 1
                    isPOI = False
                    break
                else:
                    if find_distance(gps,maxPoint) > eps:
                        ia = i
                        while ib < len(data_tup)-1 and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
                            ib += 1
                        isPOI = True
                        break
                    else:
                        if distA + distB > maxDistance:
                            maxDistance = distA + distB
                            maxPoint = data_tup[i]
            if isPOI: #keep finding until too far away
                more = ib + 1
                while more < len(data_tup):
                    #print(more)
                    point = data_tup[more]
                    distA = find_distance(point,A)
                    distB = find_distance(point,B)
                    if (distA > eps) or (distB > eps) or (find_distance(point,maxPoint) > eps):
                        day = datetime.fromtimestamp(data_tup[ia][2]).isoweekday()
                        time = datetime.fromtimestamp(data_tup[ia][2]).time()
                        POIs.append((data_tup[ia:more],day,time))
                        ia = more + 1
                        while ib < len(data_tup)-1 and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
                            ib += 1
                        break
                    else:
                        if distA + distB > maxDistance:
                            maxDistance = distA + distB
                            maxPoint = data_tup[more]
                        more+=1
    
    end = datetime.now()
    print("New Jump: Total num of POI jumped:", len(POIs))
    print("Runtime:",(end-start))
    
    for a in range(len(POIs)-1):
        poi_cand = POIs[a]
        POI = poi_cand[0]
        recall = 0
        for i in range(len(POI)-1):
            for j in range(i,len(POI)):
                if find_distance(POI[i],POI[j]) > eps:
                    recall += 1
        print("Length:",len(POI),"Accuracy:", (1-recall/(len(POI)*(len(POI)-1))),"Starting from Day",poi_cand[1],poi_cand[2])
        # if a < len(POIs) - 1:
        #     print("Time Difference: ", POIs[a+1][3] - POIs[a][4])



    return POIs   



def find_POIs_cluster(data_tup):
    start = datetime.now()
    global mintime
    global eps

    POIs = []

    ia = 0
    ib = 1
    #find a good B to start with
    while ib < len(data_tup) and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
        ib += 1

    while ia < len(data_tup) and ib < len(data_tup):
        if (data_tup[ib][2] - data_tup[ia][2]) < mintime:
            break
        # go to next group
        if find_distance(data_tup[ia],data_tup[ib]) > eps:
            ia = (ia+ib)//2+1
            while ib < len(data_tup)-1 and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
                ib += 1
        # start testing for POI
        else:
            isPOI = True
            for gps in data_tup[ia+1:ib]:
                if (find_distance(gps,data_tup[ia]) > eps) or (find_distance(gps,data_tup[ib]) > eps):
                    isPOI = False
                    break
            if isPOI:
                #center = list(map(lambda l: sum(l)/len(l), list(zip(*data_tup[ia:ib+1]))))
                POIs.extend(data_tup[ia:ib+1])
                ia = ib+1
                while ib < len(data_tup)-1 and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
                    ib += 1
            else:
                ia = (ia+ib)//2+1
                while ib < len(data_tup)-1 and (data_tup[ib][2] - data_tup[ia][2]) < mintime:
                    ib += 1
    
    index = 0
    
    valid = True
    pois_with_time = []

    while index < len(POIs):        # check every point in the list
        currCenter = POIs[index]
        valid = True
        poi_cand = [currCenter]           # start checking neighborhood
        i = index + 1                   # start from the next point after current point
        while i < len(POIs):
            for point in poi_cand:      # check compatibility with every point in existing neighborhood
                if find_distance(point,POIs[i]) > eps: # stop checking and return once the point exceeds distance
                    valid = False
                    break
            if valid:                   # if still valid, append the point to neighborhood
                poi_cand.append(POIs[i])
                i+=1                    # continue looking at the next point
            else:                       # if not valid anymore, break from while loop.
                break
        if (poi_cand[-1][2] - poi_cand[0][2]) >= mintime:
            day = datetime.fromtimestamp(poi_cand[0][2]).isoweekday()
            time = datetime.fromtimestamp(poi_cand[0][2]).time()
            pois_with_time.append((poi_cand,day,time))
            print("New: No. of points in POI:", len(poi_cand), "Starting from: Day", day, time)

        index = i

    end = datetime.now()
    print("New: Total num of POI clustered:", len(pois_with_time))
    print("Runtime:",(end-start))

def poi_by_day(pois):
    Monday = []
    Tuesday = []
    Wednesday = []
    Thursday = []
    Friday = []
    Saturday = []
    Sunday = []

    for poi in pois:
        if poi[1] == 1:
            Monday.append(poi)
        elif poi[1] == 2:
            Tuesday.append(poi)
        elif poi[1] == 3:
            Wednesday.append(poi)
        elif poi[1] == 4:
            Thursday.append(poi)
        elif poi[1] == 5:
            Friday.append(poi)
        elif poi[1] == 6:
            Saturday.append(poi)
        else:
            Sunday.append(poi)

    return {"Monday": Monday, "Tuesday": Tuesday, "Wednesday": Wednesday, "Thursday": Thursday, "Friday": Friday, "Saturday": Saturday, "Sunday": Sunday}

# MAIN STARTS HERE
# User defined variables
def main():
    global mintime
    #global k
    global eps

    traces_directory = "../Data_CSV/075"
    mintime = 600                    # in seconds. Min Time, for a point to be considered as POI, if spent there
    # k = 75                     # No of neighboring points to be checked for a point to be POI
    eps = 0.1                    # Considered radius of a POI


    print ("Minimum time period                    : ", mintime, "s")
    # print ("No of neighbor points to be considered : ", k)
    print ("Eps Radius of POI                      : ", eps, "km")

    if not os.path.exists(traces_directory):
        print ("Given directory does not exists")
        quit()

    trace_files = os.listdir(traces_directory)

    if len(trace_files) == 0:
        print ("No trace files are present in mentioned directory")
        quit()


    # - Open all the trace files and read the data
    
    # all_trajectories_pois = []
    # all_trajectories_pois_jumped = []
    # count = 0

    # for trace_f in trace_files:
    #     print(trace_f)
    #     oneTrace = read_csv(os.path.join(traces_directory,trace_f))
    #     pois_jumped = find_POIs_jump(oneTrace)
    #     all_trajectories_pois_jumped.extend(pois_jumped) #list of pois jumped
    #     pois = find_POIs(oneTrace)
    #     all_trajectories_pois.extend(pois) #list of pois
    
    all_trajectories_pois = read_csv("../Data_CSV/075/20110902093233.csv")
    find_POIs_jump_new(all_trajectories_pois)
    # find_POIs_cluster(all_trajectories_pois)
    # find_POIs(all_trajectories_pois)



    
    # print("POIs of one person:",len(all_trajectories_pois))
    # print("POIs of one person jumped:",len(all_trajectories_pois_jumped))

    # poi_day = poi_by_day(all_trajectories_pois)

    # print("POI by day:")
    # for day in poi_day:
    #     print(day, len(poi_day[day]))


    # - Identify and search for the edges which can be directly
    #   deduced from data list

    # dijkstras_switch = dijkstras_switch.replace('dijkstras=', '')
    # find_edges()

    # - Create database, add all the mobility map information in database
    # - Using Djikstra's algorithm, create missing edges on the map and save
    # database_functions()

    # conn.close()


if __name__ == "__main__":
    main()
