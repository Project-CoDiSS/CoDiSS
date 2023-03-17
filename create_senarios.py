"""
This Python module provides a flexible way to define and test various 
interventions in an office layout. The module defines different scenarios, 
such as adding decompression areas, reducing agent cluster sizes in working areas,
 and shifting agent schedules. Each scenario is assigned a unique ID, and by calling 
 the scenario(ID) function, the module returns the relevant layout, agent locations, 
 and agent behavioral characteristics for the given scenario. The module defines 25 
 scenarios, allowing various interventions to be tested and evaluated.

In this file, there are lines in each intervention as "os.makedir",
These lines should be "commented" if the directory exists (or uncommented if it does not exist). 
The directory will then be used to store the simulation results.
"""

import layout
import datetime
import scipy.stats as st
import os

def senario(id):
    """
        return layout, locations, shifts, meetings, based on senario id
    """
    layout_1=layout.create_layout()
    locations=layout.define_locations()
    [washroom_lower,washroom_upper]=locations["washroom"]
    [elevator]=locations["elevator"]
    [desk_lower,desk_upper]=locations["desk"]
    [coffee_lower,coffee_upper]=locations["coffee"]
    [conference]=locations["conference"]
    [meet1,meet2]=locations["meet"]
    g1={"location":meet1,"start":datetime.time(10,0,0),"duration":60,"size":15} #average of 6 to 10 people
    g2={"location":meet2,"start":datetime.time(10,0,0),"duration":60,"size":15} #average of 6 to 10 people
    g3={"location":meet1,"start":datetime.time(11,0,0),"duration":60,"size":15} #average of 6 to 10 people
    g4={"location":meet2,"start":datetime.time(11,0,0),"duration":60,"size":15} #average of 6 to 10 people
    interval=st.uniform(0,1)
    gatherings=[g1,g2,g3,g4]
    workers_percent=100 #percentage of workers working in the office: decreasing the work density
    shifts=[[datetime.timedelta(hours=9,minutes=30),datetime.timedelta(hours=7)]]
    interventions={"isolation":st.uniform(0,3)}
    
    folder=r".\\"
    if id==0:
        os.mkdir("Base")
        #baseline
        file_loc=folder+r"\Base"
    elif id==1:
        #os.mkdir("Add_coffee_1")
        # add_1_coffee_area
        locations=layout.add_1_coffee_area(locations)
        file_loc=folder+r"\Add_coffee_1"
    elif id==2:
        #os.mkdir("Add_coffee_3")
        # add_3_coffee_area
        locations=layout.add_3_coffee_areas(locations)
        file_loc=folder+r"\Add_coffee_3"
    elif id==3:
        #os.mkdir("Add_coffee_6")
        # add_6_coffee_area
        locations=layout.add_6_coffee_areas(locations)
        file_loc=folder+r"\Add_coffee_6"
    elif id==4:
        #os.mkdir("Add_zone_1")
        #add 1 working zone
        file_loc=folder+r"\Add_zone_1"
        layout_1=layout.add_1_zone(layout_1)
    elif id==5:
        #os.mkdir("Add_zone_3")
        #add 3 working zone
        file_loc=folder+r"\Add_zone_3"
        layout_1=layout.add_3_zones(layout_1)
    elif id==6:
        #os.mkdir("Add_zone_6")
        #add 6 working zone
        file_loc=folder+r"\Add_zone_6"
        layout_1=layout.add_6_zones(layout_1)
    elif id==7:
        #os.mkdir("Add_zone_15")
        #add 15 working zone
        file_loc=folder+r"\Add_zone_15"
        layout_1=layout.add_15_zones(layout_1)
    elif id==8:
        #os.mkdir("Add_zone_33")
        #add 33 working zone
        file_loc=folder+r"\Add_zone_33"
        layout_1=layout.add_33_zones(layout_1)
    elif id==9:
        #os.mkdir("Arrival_float_30")
        #define interval in minutes, allowing a 30 min floating arrival time
        interval=st.uniform(0,30)
        file_loc=folder+r"\Arrival_float_30"
    elif id==10:
        #os.mkdir("Arrival_float_60")
        #define interval in minutes, allowing a 30 min floating arrival time
        interval=st.uniform(0,60)
        file_loc=folder+r"\Arrival_float_60"
    elif id==11:
        #os.mkdir("Arrival_float_120")
        #define interval in minutes, allowing a 30 min floating arrival time
        interval=st.uniform(0,120)
        file_loc=folder+r"\Arrival_float_120"
    elif id==12:
        #os.mkdir("Arrival_float_180")
        #define interval in minutes, allowing a 30 min floating arrival time
        interval=st.uniform(0,180)
        file_loc=folder+r"\Arrival_float_180"
    elif id==13:
        #os.mkdir("meet_room_size")
        # using the conference room
        g1={"location":conference,"start":datetime.time(9,30,0),"duration":60,"size":15} #average of 6 to 10 people
        g2={"location":conference,"start":datetime.time(10,30,0),"duration":60,"size":15} #average of 6 to 10 people
        g3={"location":conference,"start":datetime.time(11,30,0),"duration":60,"size":15} #average of 6 to 10 people
        g4={"location":conference,"start":datetime.time(12,30,0),"duration":60,"size":15} #average of 6 to 10 people
        gatherings=[g1,g2,g3,g4]
        file_loc=folder+r"\meet_room_size"
    elif id==14:
        #os.mkdir("meet_agents_size")
        # decrease number of people in meetings
        g1={"location":meet1,"start":datetime.time(10,0,0),"duration":60,"size":7} #average of 6 to 10 people
        g2={"location":meet2,"start":datetime.time(10,0,0),"duration":60,"size":8} #average of 6 to 10 people
        g3={"location":meet1,"start":datetime.time(11,0,0),"duration":60,"size":8} #average of 6 to 10 people
        g4={"location":meet2,"start":datetime.time(11,0,0),"duration":60,"size":7} #average of 6 to 10 people
        gatherings=[g1,g2,g3,g4]
        file_loc=folder+r"\meet_agents_size"
    elif id==15:
        #os.mkdir("meet_duration_30")
        # decrease meeting duration to 30 minutes
        g1={"location":meet1,"start":datetime.time(10,0,0),"duration":30,"size":15} #average of 6 to 10 people
        g2={"location":meet2,"start":datetime.time(10,0,0),"duration":30,"size":15} #average of 6 to 10 people
        g3={"location":meet1,"start":datetime.time(11,0,0),"duration":30,"size":15} #average of 6 to 10 people
        g4={"location":meet2,"start":datetime.time(11,0,0),"duration":30,"size":15} #average of 6 to 10 people
        gatherings=[g1,g2,g3,g4]
        file_loc=folder+r"\meet_duration_30"
    elif id==16:
        #os.mkdir("meet_duration_45")
        # decrease meeting duration to 45 minutes
        g1={"location":meet1,"start":datetime.time(10,0,0),"duration":45,"size":15} #average of 6 to 10 people
        g2={"location":meet2,"start":datetime.time(10,0,0),"duration":45,"size":15} #average of 6 to 10 people
        g3={"location":meet1,"start":datetime.time(11,0,0),"duration":45,"size":15} #average of 6 to 10 people
        g4={"location":meet2,"start":datetime.time(11,0,0),"duration":45,"size":15} #average of 6 to 10 people
        gatherings=[g1,g2,g3,g4]
        file_loc=folder+r"\meet_duration_45"
    elif id==17:
        #os.mkdir("Add_shift_1")
        #increase number of shifts: 2
        shifts=[[datetime.timedelta(hours=9,minutes=30),datetime.timedelta(hours=7)],[datetime.timedelta(hours=17),datetime.timedelta(hours=7)]]
        file_loc=folder+r"\Add_shift_1"
    elif id==18:
        #os.mkdir("Workers_4_5th")
        #Reduce number of workers to 2/3
        workers_percent=80
        file_loc=folder+r"\Workers_4_5th"
    elif id==19:
        #os.mkdir("Workers_2_3rd")
        #Reduce number of workers to 2/3
        workers_percent=66.6667
        file_loc=folder+r"\Workers_2_3rd"
    elif id==20:
        #os.mkdir("Workers_half")
        #Reduce number of workers to half
        workers_percent=50
        file_loc=folder+r"\Workers_half"
    elif id==21:
        #os.mkdir("Mask")
        # applying normal surgical masks for 66 perentage of times
        #this isolation only models sick days after symptoms
        interventions={"isolation":st.uniform(0,3),"mask":[st.uniform(42,88-42),17.8]}
        file_loc=folder+r"\Mask"
    elif id==22:
        os.mkdir("Vaccine")
        # using a 85 percent effective vaccine for 75 percent of workers
        interventions={"isolation":st.uniform(0,3),"vaccine":[st.uniform(50,60-50),70.2]}
        file_loc=folder+r"\Vaccine"
    elif id==23:
        #all in one
        #os.mkdir("zone_coffee")
        layout_1=layout.add_33_zones(layout_1)
        locations=layout.add_6_coffee_areas(locations)
        file_loc=folder+r"\zone_coffee"
    elif id==24:
        #os.mkdir("zone_coffee_meet")
    
        layout_1=layout.add_33_zones(layout_1)
        locations=layout.add_6_coffee_areas(locations)

        # using the conference room
        g1={"location":meet1,"start":datetime.time(10,0,0),"duration":30,"size":15} #average of 6 to 10 people
        g2={"location":meet2,"start":datetime.time(10,0,0),"duration":30,"size":15} #average of 6 to 10 people
        g3={"location":meet1,"start":datetime.time(11,0,0),"duration":30,"size":15} #average of 6 to 10 people
        g4={"location":meet2,"start":datetime.time(11,0,0),"duration":30,"size":15} #average of 6 to 10 people
       
        gatherings=[g1,g2,g3,g4]
        
        file_loc=folder+r"\zone_coffee_meet"

    elif id==25:
        #all in one
        #os.mkdir("all")
    
        layout_1=layout.add_33_zones(layout_1)
        locations=layout.add_6_coffee_areas(locations)

        # using the conference room
        g1={"location":meet1,"start":datetime.time(10,0,0),"duration":30,"size":15} #average of 6 to 10 people
        g2={"location":meet2,"start":datetime.time(10,0,0),"duration":30,"size":15} #average of 6 to 10 people
        g3={"location":meet1,"start":datetime.time(11,0,0),"duration":30,"size":15} #average of 6 to 10 people
        g4={"location":meet2,"start":datetime.time(11,0,0),"duration":30,"size":15} #average of 6 to 10 people
       
        gatherings=[g1,g2,g3,g4]
        
        interval=st.uniform(0,180)
        
        file_loc=folder+r"\all"


    #plot layout
    plt=layout.plot_layout(layout_1,locations)
    plt.savefig(file_loc+r"\layout.jpg",bbox_inches='tight',dpi=600)
    plt.savefig(file_loc+r"\layout.pdf",bbox_inches='tight',dpi=600)
    plt.clf()
    return layout_1,locations,interval, gatherings,workers_percent,shifts,interventions,file_loc

