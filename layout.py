"""
This file creates the wall layout for the case study 
"""
import numpy as np
import matplotlib.pyplot as plt



def create_layout():
    """
    This function creates the wall layout of the 11th floor of the call center for the case study.
    Returns:
        numpy array: The array representing the wall layout of the case study
    """
    # building wall layout
    layout=np.zeros((23,26))
    layout[1:,0]=1; layout[1:,25]=1; layout[0,1:]=2; layout[22,1:]=2
    layout[22,25]=3; layout[1:,9]=1; layout[22,9]=3;layout[1:,17]=1;layout[22,17]=3; layout[14:,13]=1
    layout[4,10:18]=2; layout[4,10:18]=2; layout[4,10:18]=2; layout[8,10:18]=2; layout[10,10:18]=2
    layout[14,10:18]=2; layout[14,17]=3; layout[8,17]=3; layout[17,10:18]=2

    layout[4,9]=0; layout[10,9]=0; layout[17,9]=0; layout[18,9]=0; layout[18,17]=0
    layout[17,13]=3; layout[22,13]=3
    #right rooms
    layout[4,1:8]=2; layout[1:5,8]=1
    layout[4,8]=3; layout[2,7:9]=2; layout[3,8]=0; layout[2,6:7]=2; layout[1:5,6]=1; layout[1:5,3]=1
    layout[18:,6]=1; layout[22,6]=3; layout[18:,3]=1; layout[22,3]=3; layout[18,1:10]=2

    layout[18,1]=0; layout[18,4]=0; layout[18,9]=0
    #elevators
    layout[8,13]=1; layout[8,12]=3; layout[7,13]=2; layout[8,11]=1; layout[8,10]=3; layout[7,11]=2

    layout[10,13]=0; layout[11,13]=3; layout[11,12]=1; layout[10,11]=0; layout[11,11]=3; layout[11,10]=1
    return layout

def add_1_zone(layout):
    layout[11,19:]=2
    layout[11,25]=3
    return layout

def add_3_zones(layout):
    # adding two zones in upper area
    layout[8,19:]=2;layout[15,19:]=2
    layout[8,25]=3;layout[15,25]=3

    # adding one zone in the lower area
    layout[11,2:7]=2
    return layout

def add_6_zones(layout):
    # adding  zones in upper area
    layout[5,19:25]=2;layout[9,19:25]=2;layout[13,19:]=2;layout[17,19:25]=2
    layout[13,25]=3

    # adding  zones in the lower area
    layout[9,2:7]=2;layout[13,2:7]=2
    return layout

def add_15_zones(layout):
     # adding zones in upper area
    layout[2,19:25]=2;layout[4,19:25]=2;layout[6,19:25]=2;layout[8,19:25]=2;layout[10,19:25]=2;layout[12,19:25]=2
    layout[14,19:25]=2;layout[16,19:25]=2;layout[18,19:25]=2;layout[20,19:25]=2
    layout[12,25]=3

    # adding zones in the lower area
    layout[7,2:7]=2;layout[9,2:7]=2;layout[11,2:7]=2;layout[13,2:7]=2;layout[15,2:7]=2
    return layout

def add_33_zones(layout):
     # adding two zones in upper area
    layout[1:22,19:25]=2
    layout[11:15,24]=3
    # adding one zone in the lower area
    layout[6:17,2:7]=2
    return layout

def define_locations():
    """
    Define different locations in the building
    Returns:
        dictionay: list of designated locations in a the layout such as desk, washroom, elevator, and coffee
    """
    washroom_lower_x,washroom_lower_y=np.meshgrid(range(15,18),range(10,14))
    washroom_lower_x=washroom_lower_x.flatten();washroom_lower_y=washroom_lower_y.flatten()
    washroom_lower=[washroom_lower_x,washroom_lower_y]
    
    washroom_upper_x,washroom_upper_y=np.meshgrid(range(15,18),range(14,18))
    washroom_upper_x=washroom_upper_x.flatten();washroom_upper_y=washroom_upper_y.flatten()
    washroom_upper=[washroom_upper_x,washroom_upper_y]

    washroom= list(washroom_lower[0])+list(washroom_upper[0]),list(washroom_lower[1])+list(washroom_upper[1])

    #x,y=np.meshgrid([8,11],[11,13])
    x,y=np.meshgrid(range(9,11),range(10,16))
    elevator=[x.flatten(),y.flatten()]

    x1,y1=np.meshgrid(range(1,5),range(4,7))
    #x2,y2=np.meshgrid(range(18,23),range(10,18))
    x2,y2=np.meshgrid(range(1,5),range(1,4))
    meet1=[x1.flatten(),y1.flatten()]
    meet2=[x2.flatten(),y2.flatten()]
    meet=[list(meet1[0])+list(meet2[0]),list(meet1[1])+list(meet2[1])]

    x,y=np.meshgrid(range(1,5),range(10,18))
    conference=[x.flatten(),y.flatten()]

    x,y=np.meshgrid(range(1,23),range(19,25))
    desk_upper=[x.flatten(),y.flatten()]


    x,y=np.meshgrid(range(11,15),range(25,26))
    desk_upper2=[x.flatten(),y.flatten()]
    desk_upper=[list(desk_upper2[0])+list(desk_upper[0]),list(desk_upper2[1])+list(desk_upper[1])]

    x,y=np.meshgrid(range(19,23),range(1,9,3))
    desk_lower=[x.flatten(),y.flatten()]

    x,y=np.meshgrid(range(19,23),range(3,8,3))
    desk_lower2=[x.flatten(),y.flatten()]
    desk_lower=[list(desk_lower[0])+list(desk_lower2[0]),list(desk_lower[1])+list(desk_lower2[1])]


    x,y=np.meshgrid(range(6,18),range(2,7))
    desk_lower2=[x.flatten(),y.flatten()]
    desk_lower=[list(desk_lower[0])+list(desk_lower2[0]),list(desk_lower[1])+list(desk_lower2[1])]

    desk=[list(desk_upper[0])+list(desk_lower[0]),list(desk_upper[1])+list(desk_lower[1])]

    #coffee
    coffee_lower=[[13,12,11],[8,8,8]]
    coffee_upper=[[13,12,11],[18,18,18]]
    coffee=[list(coffee_lower[0])+list(coffee_upper[0]),list(coffee_lower[1])+list(coffee_upper[1])]

    locations={}
    locations["washroom"]= [washroom_lower,washroom_upper]
    locations["elevator"]=[elevator]
    locations["desk"]=[desk_lower,desk_upper]
    locations["coffee"]=[coffee_lower,coffee_upper]
    locations["conference"]=[conference]
    locations["meet"]=[meet1,meet2]
    locations["gwashroom"]= washroom
    locations["gelevator"]=elevator
    locations["gdesk"]=desk
    locations["gcoffee"]=coffee
    locations["gconference"]=conference
    locations["gmeet"]=meet
    return locations

def add_1_coffee_area(locations):
    #1.5 times the inital coffee areas
    global coffee, coffee_lower, coffee_upper
    #coffee
    coffee_upper=[[13,12,11,6,7,8],[18,18,18,18,18,18]]
    coffee_lower=[[13,12,11],[8,8,8]]
    coffee=[list(coffee_lower[0])+list(coffee_upper[0]),list(coffee_lower[1])+list(coffee_upper[1])]

    locations["coffee"]=[coffee_lower,coffee_upper]
    locations["gcoffee"]=coffee
    return locations

def add_3_coffee_areas(locations):
    # 2.5 times the inital coffee areas
    global coffee, coffee_lower, coffee_upper
    #coffee
    coffee_upper=[[13,12,11,1,2,3,20,21,22],[18,18,18,18,18,18,18,18,18]]
    coffee_lower=[[14,13,12,6,7,8],[8,8,8,8,8,8]]
    coffee=[list(coffee_lower[0])+list(coffee_upper[0]),list(coffee_lower[1])+list(coffee_upper[1])]

    locations["coffee"]=[coffee_lower,coffee_upper]
    locations["gcoffee"]=coffee
    return locations

def add_6_coffee_areas(locations):
    # 4 times the inital coffee areas
    global coffee, coffee_lower, coffee_upper
    #coffee
    coffee_upper=[[16,15,14,13,12,11,1,2,3,5,6,7,19,20,21],[18,18,18,18,18,18,18,18,18,18,18,18,18,18,18]]
    coffee_lower=[[14,13,12,6,7,8,18,18,18],[8,8,8,8,8,8,8,7,6]]
    coffee=[list(coffee_lower[0])+list(coffee_upper[0]),list(coffee_lower[1])+list(coffee_upper[1])]

    locations["coffee"]=[coffee_lower,coffee_upper]
    locations["gcoffee"]=coffee
    return locations

def double_washroom_size(layout,locations):
    #double the size of washrooms area in teh model
    washroom_lower_x,washroom_lower_y=np.meshgrid(range(15,21),range(10,14))
    washroom_lower_x=washroom_lower_x.flatten();washroom_lower_y=washroom_lower_y.flatten()
    washroom_lower=[washroom_lower_x,washroom_lower_y]
    
    washroom_upper_x,washroom_upper_y=np.meshgrid(range(15,21),range(14,18))
    washroom_upper_x=washroom_upper_x.flatten();washroom_upper_y=washroom_upper_y.flatten()
    washroom_upper=[washroom_upper_x,washroom_upper_y]

    washroom= list(washroom_lower[0])+list(washroom_upper[0]),list(washroom_lower[1])+list(washroom_upper[1])
    locations["gwashroom"]= washroom
    locations["washroom"]= [washroom_lower,washroom_upper]
    layout[14,10:18]=2; layout[20,10:18]=2;layout[20,17]=3; layout[20,13]=3; layout[22,17]=2; layout[22,9]=2; 
    return layout,locations

def triple_washroom_size(layout,locations):
    #2.7  the size of washrooms area in teh model
    washroom_lower_x,washroom_lower_y=np.meshgrid(range(15,23),range(10,14))
    washroom_lower_x=washroom_lower_x.flatten();washroom_lower_y=washroom_lower_y.flatten()
    washroom_lower=[washroom_lower_x,washroom_lower_y]
    
    washroom_upper_x,washroom_upper_y=np.meshgrid(range(15,23),range(14,18))
    washroom_upper_x=washroom_upper_x.flatten();washroom_upper_y=washroom_upper_y.flatten()
    washroom_upper=[washroom_upper_x,washroom_upper_y]

    washroom= list(washroom_lower[0])+list(washroom_upper[0]),list(washroom_lower[1])+list(washroom_upper[1])
    locations["gwashroom"]= washroom
    locations["washroom"]= [washroom_lower,washroom_upper]
    layout[17,10:18]=0
    return layout,locations

def plot_layout(layout,locations,filename=None):
     """
     gets model m and plot the layout based on the layout.py
     """
     washroom=locations["gwashroom"]
     elevator=locations["gelevator"]
     desk=locations["gdesk"]
     coffee=locations["gcoffee"]
     conference=locations["gconference"]
     meet=locations["gmeet"]
     fig,ax=plt.subplots(1,1,figsize=(7,8))
     color='green'
     blocksize=12
     a=layout
     w,h=a.shape
     for i in range(w): #rows are y
            for j in range(h): #columns are x
                if a[i,j]==1:
                    ax.plot([i-.5,i+.5],[j+.5,j+.5],color=color)
                if a[i,j]==2:
                    ax.plot([i+.5,i+.5],[j-.5,j+.5],color=color)
                if a[i,j]==3:
                    ax.plot([i-.5,i+.5],[j+.5,j+.5],color=color)
                    ax.plot([i+.5,i+.5],[j-.5,j+.5],color=color)
                if a[i,j]==4:
                    ax.plot(i,j,marker='s',markersize=blocksize,color=color)
        
     #ax.scatter(washroom_upper[0]+washroom_lower[0],washroom_upper[1]+washroom_lower[1],alpha=.3,s=120,marker='s',label="washroom")
     ax.scatter(washroom[0],washroom[1],alpha=.3,s=120,marker='s',label="Washroom")
     ax.scatter(coffee[0],coffee[1],alpha=.3,s=120,marker='s',label="Decompression area")
     ax.scatter(conference[0],conference[1],alpha=.3,s=120,marker='s',label="Conference room")
     ax.scatter(elevator[0],elevator[1],alpha=.3,s=120,marker='s',label="Elevator hall")
     ax.scatter(meet[0],meet[1],alpha=.3,s=120,marker='s',label="Meeting room")
     ax.scatter(desk[0],desk[1],alpha=.3,s=90,marker='o',label="Desk")
     ax.legend(loc='lower center', bbox_to_anchor=(0.5, -.15),
          ncol=3, fancybox=True, shadow=True)
     return plt

# layout=create_layout()
# locations=define_locations()
# layout=add_33_zones(layout)
# locations=add_6_coffee_areas(locations)
# layout,locations=double_washroom_size(layout,locations)
# plot_layout(layout,locations)
