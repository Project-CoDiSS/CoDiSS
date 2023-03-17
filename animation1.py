

"""
This Python file provides an animation of a case study layout, 
depicting a day in the life of the building with a few minutes of simulation time. 
The animation showcases how the agents arrive at and leave the building, 
allowing the user to visualize the movement patterns of the agents throughout the simulation. 
The ABS module generated this animation using the matplotlib library, 
which provides an easy and effective way to visualize the data. 

his Python file demonstrates how CoDiSS (Confection Disease Spread Simulator) 
can be used to visualize the dynamics of building occupancy and movement patterns, 
particularly in the context of infectious disease spread. The animation created by CoDiSS 
provides a clear and intuitive way to understand how agents move throughout the building. 
"""

import CoDiSS as con
import numpy as np
import random
import datetime
import matplotlib.pyplot as plt
import layout 



layout_1=layout.create_layout()
locations=layout.define_locations()
[washroom_lower,washroom_upper]=locations["washroom"]
[elevator]=locations["elevator"]
[desk_lower,desk_upper]=locations["desk"]
[coffee_lower,coffee_upper]=locations["coffee"]
[conference]=locations["conference"]

def random_location_selector(loc_array):
     loc=loc_array
     j=random.randint(0,len(loc[0])-1)
     return (loc[0][j],loc[1][j])

def define_agents():
     """
     returns the list of agents and their behaviour in the model
     agent speed should be based on the number of blocks moved per time step
     time-step is defined for the model and is in seconds
     """
     agent_list=[]
    

     for i in range(len(desk_lower[0])):
          a={}
          agent_desk=(desk_lower[0][i],desk_lower[1][i])
          agent_elevator=random_location_selector(elevator)
          agent_coffee=random_location_selector(coffee_lower)
          agent_washroom=random_location_selector(washroom_lower)
          agent_conf=random_location_selector(conference)
          agent_freind=random_location_selector(desk_lower)
          a['crew size']= 1
          a['tasks']=[[agent_elevator,10,0],\
                    [agent_desk,100,.9],\
                    [agent_coffee,10,.025],\
                    [agent_freind,10,.025],\
                    [agent_washroom,10,.025],\
                    [agent_conf,10,0.025]
                    ]
          shifts=[[datetime.timedelta(hours=8,minutes=3),datetime.timedelta(minutes=2)]]
          shifts.append([datetime.timedelta(hours=8,minutes=0),datetime.timedelta(minutes=2)])
          a['shift']=shifts[i%2]
          a['vaccination']=[80, 85]
          a['marker']= 'o'
          a['speed']=1
          a['infected']=False
          agent_list.append(a)

     for i in range(len(desk_upper[0])):
          a={}
          agent_desk=(desk_upper[0][i],desk_upper[1][i])
          agent_elevator=random_location_selector(elevator)
          agent_coffee=random_location_selector(coffee_upper)
          agent_washroom=random_location_selector(washroom_upper)
          agent_conf=random_location_selector(conference)
          agent_freind=random_location_selector(desk_upper)
          a['crew size']= 1
          a['tasks']=[[agent_elevator,10,0],\
                    [agent_desk,100,.9],\
                    [agent_coffee,10,.025],\
                    [agent_freind,10,.025],\
                    [agent_washroom,10,.025],\
                    [agent_conf,10,0.025]
                    ]
          a['shift']=[datetime.timedelta(hours=8,minutes=0),datetime.timedelta(seconds=200)]
          a['vaccination']=[80, 85]
          a['marker']= 'o'
          a['speed']=1
          a['infected']=False
          if agent_desk==(20,22):
               a['infected']=True
          agent_list.append(a)
     return agent_list



ventilation_efficiency=np.full((23,26), .3)

s=datetime.datetime(2020, 2, 22, 8, 0)
e=datetime.datetime(2020, 3, 9, 9, 0)

m = con.CovidModel(layout=layout_1,start_date=s,\
ventilation_efficiency=ventilation_efficiency, infection_rate=[0.05, 0],\
     workhours_per_day=.18, interventions={},\
           time_step=1,grid_size=1.5)
agent_list=define_agents()

for a in agent_list:
     # add agents
     myagent=m.add_crew(a)
     if a['infected']:
          myagent[0].get_infected()

m.animate(until=100)
#m.animate_quanta_matrix()
#layout.plot_layout(m)


