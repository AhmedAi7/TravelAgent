import datetime
from datetime import datetime
from math import sin, cos, sqrt, atan2, radians
import re

DaysOfWeek = ["sat","sun", "mon", "tue", "wed", "thu", "fri"]
def GetDaysList (FDay,SDay):
    output=[]
    Append=False
    for i in DaysOfWeek:
        if (i==FDay):
            Append=True
        if (Append==True):
            output.append(i)
        if (i==SDay):
            Append=False
    return output

def Join (List1,List2,result):
    result=[]
    for i in List1:
        for j in List2:
            if i==j:
                result.append(i)
    if len(result)>0:
        return True
    return False

def AddToRange(List,After):
    ind= DaysOfWeek.index(List[1])
    if(After):
        if (ind!=6):
            List[1]=DaysOfWeek[ind+1]
            print("A day is added after your range")
            print("Range Now is from "+List[0]+" to "+List[1])
            After=False
            return True
        else:
            After=False
    ind= DaysOfWeek.index(List[0])
    if (not After):
        if (ind !=0):
            List[0]=DaysOfWeek[ind-1]
            print("A day is added Before your range")
            print("Range Now is from "+List[0]+" to "+List[1])
            After=True
            return True
        else:
            After=True
    return False

def GetDuration(Day1,Time1,Day2,Time2):
    NumofDays=DaysOfWeek.index(Day2)-DaysOfWeek.index(Day1)
    T1=Time1.split(':')
    T2=Time2.split(':')
    H1=T1[0]
    M1=T1[1]
    H2=T2[0]
    M2=T2[0]
    H=int(H1)-int(H2)
    M=int(M1)-int(M2)
    return abs(H+(M/60)+(NumofDays*24))

def Greater (Time1,Time2): #return if Time2>Time1 in same Day
        T1=Time1.split(':')
        T2=Time2.split(':')
        H1=int(T1[0])
        M1=int(T1[1])
        H2=int(T2[0])
        M2=int(T2[1])
        if (H2>H1 or (H2==H1 and M2>=M1)) :
            return True

def AfterTime(Day1,Time1,Day2,Time2): #return if Time2 > Time1
    if (DaysOfWeek.index(Day2)>DaysOfWeek.index(Day1)):
        return True
    elif(Day1==Day2):
        T1=Time1.split(':')
        T2=Time2.split(':')
        H1=int(T1[0])
        M1=int(T1[1])
        H2=int(T2[0])
        M2=int(T2[1])
        if (H2>H1 or (H2==H1 and M2>=M1)) :
            return True
    return False

class Controler:
    def __init__(self):
        self.Flights= []
        self.CLat={} #City Latitude vlaue
        self.CLong={} #City Longitude Value
        self.LoadCities()
        self.LoadFlights()

    def GetFlights (self,City,DaysofFlight,day,time): #return list of flights from a city
        Output = []
        for i in self.Flights:
            if (day in DaysofFlight and i.day in DaysofFlight and AfterTime(day,time,i.day,i.deprature) and i.Cfrom==City):
                #print("##"+day+" 1day "+day+" 1time "+time+" 2day "+i.day+" 2time "+i.deprature)
                Output.append(i)
        return Output

    def GetFlightByNum (self,Num):
        for i in self.Flights:
            if(i.num == Num):
                return i
        return None
    
    def CalcH(self,city,goal):   # Calculate H value 
        S = 926 # approximate Flight speed
        R = 6373.0 # approximate radius of earth in km
        lat1 = radians(self.CLat[city])
        lon1 = radians(self.CLong[city])
        lat2 = radians(self.CLat[goal])
        lon2 = radians(self.CLong[goal])
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance/S #return estimated time 


    def LoadFlights (self):
        try:
            f = open("Flights.csv")
        except:
            return
        for line in f :
            line=line.replace("\n","")
            arr=line.split('-') 
            days=arr[5].split(',')
            for i in days :
                tmpFlight=Flight(arr[4],arr[0],arr[1],arr[2],arr[3],i)
                self.Flights.append(tmpFlight)

    def LoadCities (self):
        try:
            f = open("City.csv")
        except:
            return
        for line in f :
            line=line.replace("\n","")
            arr=line.split(',') 
            self.CLat[arr[0]]=float(arr[1])
            self.CLong[arr[0]]=float(arr[2])

class Flight: 
    #Initialize the class
    def __init__(self, num,Cfrom,Cto,deprature,arrival,day):
        self.num=num
        self.Cfrom=Cfrom
        self.Cto=Cto
        self.arrival=arrival
        self.deprature=deprature
        self.day=day
        
    # Compare flights
    def __eq__(self, other):
        return self.num == other.num

    #Print a Flight Details
    def Print(self):
        return(str(self.num)+" from "+str(self.Cfrom)+" to "+str(self.Cto)+". Departure time "+str(self.deprature)+" and arrival time "+str(self.arrival)+" Day of Deprature: "+str(self.day))

class Node:
    # Initialize the class
    def __init__(self, Name:str, parent:str,controler):
        self.Name = Name
        self.parent = parent
        self.controler=controler
        self.g = 0 #Duration to start node
        self.h = 0 #Duration to end node
        self.Path=[] #Path of flights 
        self.goal=None #Goal City
        if self.parent is not None: #append path of parent in child node
            self.goal=self.parent.goal
            for i in self.parent.Path:
                self.Path.append(i)

    #calculate F (Total Cost)
    def GetF (self,city):
        if(len(self.Path)>1):
            self.g=GetDuration(self.Path[0].day,self.Path[0].deprature,self.Path[-1].day,self.Path[-1].arrival)
        else:
            self.g=GetDuration(self.Path[0].day,self.Path[0].deprature,self.Path[0].day,self.Path[0].arrival)
        return self.g+self.controler.CalcH(city,self.goal)

    # Compare nodes
    def __eq__(self, other):
        if self is not None and other is not None:
            return self.Name == other.Name
        else: 
            return False

    # Sort nodes
    def __lt__(self, other):
        return self.GetF(self.Name) < other.GetF(other.Name)


# A* search
def astar_search(controler,start,end,RangeOfDays):
    DaysofFlight=GetDaysList(RangeOfDays[0],RangeOfDays[1])
    # Create lists for open nodes and closed nodes
    open = []
    closed = []

    start_node = Node(start, None,controler)
    start_node.goal=end
    goal_node = Node(end, None,controler)

    # Add the start Node
    open.append(start_node)
    
    # Loop until the open list is empty
    while len(open) > 0:

        # Sort the open list to get the node with the lowest cost first
        open.sort()

        # Get the node with the lowest cost
        current_node = open.pop(0)

        # Add the current node to the closed list
        closed.append(current_node)
        
        # Check if we have reached the goal, return the path
        if current_node == goal_node:
            return current_node

        # Get neighbours
        city=start # last city
        Time="00:00" #time to search the first flight
        Day = DaysofFlight[0] #Day to search the first flight
        if current_node.Name!=start:
            lastFlight=current_node.Path[-1]
            city=lastFlight.Cto
            Time=lastFlight.arrival
            if (Greater(lastFlight.arrival,lastFlight.deprature)): #Arrival Time < Deprature (Deprature in the day after)      
                indexofDay=DaysOfWeek.index(lastFlight.day)
                if indexofDay!=6: #Day != Friday
                    Day= DaysOfWeek[indexofDay+1] #Day=the Day after flight day
                else:
                    Day= DaysOfWeek[0] #Day = saturday
            else:
                Day=lastFlight.day

        #print("@@"+Day)
        neighbors=controler.GetFlights(city,DaysofFlight,Day,Time)
        for f in neighbors:    
            # Create a neighbor node
            neighbor = Node(f.Cto, current_node,controler)
            neighbor.Path.append(f)
            # Check if the neighbor is in the closed list
            if(neighbor in closed):
                continue

            # Calculate full path cost
            neighbor.h =controler.CalcH(f.Cto,end)

            # Check if neighbor is in open list and if it has a lower f value
            if(add_to_open(open, neighbor,controler) == True):
                # Everything is green, add neighbor to open list
                open.append(neighbor)

    # Return None, no path is found
    return None

# Check if a neighbor should be added to open list
def add_to_open(open, neighbor,controler):
    for node in open:
        if (neighbor == node and neighbor.GetF(neighbor.Name) > node.GetF(node.Name)):
            return False
    return True

# The main entry point 
def main():

    controler = Controler()
    AddDayAfter=True
    # Run the search algorithm untill find a solution
    while (1>0):
        Query= str(input("Please, Enter a Query \n"))
        Query=Query.replace(" ", "")
        m = re.match(r'Print_solution\(travel\(“(.*)”,”(.*)”,\[“(.*)”,”(.*)”\]\)\)', Query)
        if not m:
            print("Wrong Querey \n")
            continue
        From=m.group(1)
        To=m.group(2)
        range=[m.group(3),m.group(4)]
        if (m.group(3) not in DaysOfWeek or m.group(4) not in DaysOfWeek):
            print("Days should be in this form ..[sat,sun,mon,tue,wed,thu,fri] ")
            continue
        if (From not in controler.CLat.keys() or To not in controler.CLat.keys()):
            print("Wrong Cities ")
            continue
        break
    while(1>0):
        Result = astar_search(controler,From,To,range)
        if Result is not None:
            break
        elif Result is None :
            print("No Path available in this range")
            if (AddToRange(range,AddDayAfter)):
                continue
            print ("No Path Between this two cities.. ")
            return
    count=1
    for i in Result.Path:
        print ("Step "+str(count)+": Use the Flight "+i.Print()) 
        count+=1
# run main method
if __name__ == "__main__": main()
