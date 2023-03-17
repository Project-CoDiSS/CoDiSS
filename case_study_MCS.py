
"""
This Python file utilizes the CoDiSS.py and Create_Scenarios modules to simulate and test 
the effectiveness of different interventions in controlling the spread of infectious diseases. 
By providing the scenario ID, simulation start and finish dates, and the number of 
Monte Carlo simulation runs, the file runs the specified scenario for the desired number of 
times and generates results related to disease spread for the simulation duration, including the 
attack rate and high-risk zones in the provided office layout. 
"""

import CoDiSS as con
import numpy as np
import datetime
import matplotlib.pyplot as plt
import random
import matplotlib.dates as mdates
import scipy.stats as st
import pandas as pd
from create_senarios import senario
import winsound
import pickle
        

for senario_ID in [0]:
     layout_1,locations,interval, gatherings,workers_percentage,shifts,interventions,file_loc=senario(senario_ID)
     simu_results_pic = open(file_loc+"\\sim_results.pickle", "wb")
     np.random.seed(40)
     random.seed(40)
     MCS_number=100 #number of runs for Monte_Carlo simulation
     [washroom_lower,washroom_upper]=locations["washroom"]
     [elevator]=locations["elevator"]
     [desk_lower,desk_upper]=locations["desk"]
     [coffee_lower,coffee_upper]=locations["coffee"]
     [conference]=locations["conference"]
     [meet1,meet2]=locations["meet"]
     
     work_duration= shifts[-1][0]-shifts[0][0]
     work_duration+=shifts[-1][-1]
     workhours_per_day=(work_duration.total_seconds())/3600
     workhours_per_day=workhours_per_day+1+interval.args[-1]/60
     ## Define a random selector for the location of the entitiy
     def random_location_selector(loc_array):
          loc=loc_array
          j=random.randint(0,len(loc[0])-1)
          return (loc[0][j],loc[1][j])

     # creater a list of agent behaviours that include, location,probability and duration
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
               #reduce the number of workers according to the provided percentage
               if workers_percentage/100<=random.random():
                   continue

               agent_elevator=random_location_selector(elevator)
               agent_coffee=random_location_selector(coffee_lower)
               agent_washroom=random_location_selector(washroom_lower)
               agent_conf=random_location_selector(conference)
               agent_freind=random_location_selector(desk_lower)
               a['crew size']= 1
               task_ps=[random.uniform(86,93),random.uniform(3,6),random.uniform(3,6),random.uniform(1,2)]
               task_ps=np.array(task_ps)/sum(task_ps)
               a['tasks']=[[agent_elevator,3,0],\
                         [agent_desk,5,task_ps[0]],\
                         [agent_coffee,5,task_ps[1]],\
                         [agent_freind,5,task_ps[2]],\
                         [agent_washroom,5,task_ps[3]]\
                         ]
               delta=datetime.timedelta(minutes=int(interval.rvs()))#allow float
               shift=random.choice(shifts)
               arrive_early=datetime.timedelta(minutes=random.randint(0, 15))
               leave_late=datetime.timedelta(minutes=random.randint(0, 15))
               act_start=shift[0]+delta-arrive_early
               act_finish=shift[1]+arrive_early+leave_late+delta
               a['shift']=[act_start, act_finish]
               a['marker']= 'o'
               a['speed']=60
               a['infected']=False
               agent_list.append(a)

          for i in range(len(desk_upper[0])):
                
               a={}
               agent_desk=(desk_upper[0][i],desk_upper[1][i])
               # reduce the number of workers according to the provided percentage of workers
               if agent_desk!=(20,22) and workers_percentage/100<=random.random():
                    continue
               
               agent_elevator=random_location_selector(elevator)
               agent_coffee=random_location_selector(coffee_upper)
               agent_washroom=random_location_selector(washroom_upper)
               agent_conf=random_location_selector(conference)
               agent_freind=random_location_selector(desk_upper)
               
               # Probabilities working, coffee, freind, washroom
               task_ps=[random.uniform(86,93),random.uniform(3,6),random.uniform(3,6),random.uniform(1,2)]
               task_ps=np.array(task_ps)/sum(task_ps)
               a['crew size']= 1
               a['tasks']=[[agent_elevator,3,0],\
                         [agent_desk,5,task_ps[0]],\
                         [agent_coffee,5,task_ps[1]],\
                         [agent_freind,5,task_ps[2]],\
                         [agent_washroom,5,task_ps[3]]\
                         ]
               delta=datetime.timedelta(minutes=int(interval.rvs()))#allow float
               shift=random.choice(shifts)
               arrive_early=datetime.timedelta(minutes=random.randint(0, 15))
               leave_late=datetime.timedelta(minutes=random.randint(0, 15))
               act_start=shift[0]+delta-arrive_early
               act_finish=shift[1]+arrive_early+leave_late+delta
               a['shift']=[act_start, act_finish]
              
               a['marker']= 'o'
               a['speed']=60
               a['infected']=False
               if agent_desk==(20,22):
                    a['infected']=True
               agent_list.append(a)
          return agent_list

     case_study_number=[1     ,3     ,2     ,1    , 3   ,3    ,7    ,16    ,14    ,12    ,16     ,10   ,8]
     case_study_day=   [(2,25),(2,28),(2,29),(3,1),(3,2),(3,4),(3,5),(3,6) ,(3,7) ,(3,8) ,(3,9) ,(3,10),(3,11)]
     case_study_date=[]

     for d in case_study_day:
          case_study_date.append((datetime.datetime(2020,d[0],d[1],8,0)-datetime.timedelta(days=4)).date())


     # ************************************
     # Defining model and adding its agents
     ventilation_efficiency=np.full((23,26), .3)
     s=datetime.datetime(2020, 2, 21, 9, 0)
     e=datetime.datetime(2020, 3, 9, 9, 45)
     #e=datetime.datetime(2020, 2, 21, 9, 4)

     site_width,site_height=layout_1.shape
     effective_p_matrix=np.zeros([site_width, site_height],dtype=np.float64)
     p_matrix=np.zeros([site_width, site_height])
     expected_number_matrix=np.zeros([site_width, site_height])
     daily_infection_report={}
     expected_infections=[]
     infected_number=[]
     infected_dates=[]
     attack_rates=[]


     for i in range(MCS_number):
          print("Scenario number is",senario_ID)
          print("Run number is:",i)
          m1 = con.CovidModel(layout=layout_1,start_date=s,ghatherings=gatherings,\
               ventilation_efficiency=ventilation_efficiency, infection_rate=[0.0, 0],\
               workhours_per_day=workhours_per_day, interventions=interventions,\
                    time_step=60,grid_size=1.5,workdays= 6)


          agent_list=define_agents()
          for a in agent_list:
               # add agents
               myagent=m1.add_crew(a)
               if a['infected']:
                    myagent[0].get_infected(s)
          
          m1.myrun(e, interventions=interventions)
          effective_p_matrix+=m1.effective_infection_probability_matrix()
          p_matrix+=m1.infection_probability_matrix()
          expected_number_matrix+=m1.infection_matrix
          for day in m1.daily_infection_report:
               if day not in daily_infection_report:
                    daily_infection_report[day]=[]
               daily_infection_report[day].append(m1.daily_infection_report[day])
          t=m1.attack_rate()
          rate=t[0]
          dates=t[1]
          numbers=t[2]
          infected_dates.append(dates)
          infected_number.append(np.cumsum(np.array(numbers)))
          attack_rates.append(rate)

     effective_p_matrix/=MCS_number
     p_matrix/=MCS_number
     expected_number_matrix/=MCS_number
     
     #Pickling the simulation results in the following order: [effective_p_matrix, p_matrix, expected_number_matrix, attack_rates, infected_dates, infected_number, daily_infection_report]
     pickle.dump([effective_p_matrix, p_matrix, expected_number_matrix, attack_rates, infected_dates, infected_number, daily_infection_report], simu_results_pic)

     # Plotting effective_p_matrix : effective infection probabilit matrix
     fig,ax=plt.subplots()
     m1.plot_layout(ax)
     im0 = ax.imshow(effective_p_matrix.T,  vmin=0,vmax=1, cmap='Reds', interpolation='none',origin='lower') #interpolation="nearest"
     plt.title("Infection probability")
     cbar=plt.colorbar(im0)
     cbar.set_label("Probability")
     plt.savefig(file_loc+r"\effective_probability_matrix_case_study.pdf",bbox_inches='tight',dpi=600)
     plt.savefig(file_loc+r"\effective_probability_matrix_case_study.jpg",bbox_inches='tight',dpi=600)
     #plt.show(block=True)
     plt.clf()

     # Plotting infection probability matrix
     fig,ax=plt.subplots()
     m1.plot_layout(ax)
     im0 = ax.imshow(p_matrix.T,   cmap='Reds', vmin=0,vmax=1,interpolation='none',origin='lower') #interpolation="nearest"
     plt.title("Infection probability")
     cbar=plt.colorbar(im0)
     cbar.set_label("Probability")
     plt.savefig(file_loc+r"\probability_matrix_case_study.pdf",bbox_inches='tight',dpi=600)
     plt.savefig(file_loc+r"\probability_matrix_case_study.jpg",bbox_inches='tight',dpi=600)
     #plt.show(block=True)
     plt.clf()

     #plotting expected number of infections
     fig,ax=plt.subplots()
     m1.plot_layout(ax)
     im0 = ax.imshow(expected_number_matrix.T,  vmin=0,vmax=1, cmap='Reds', interpolation='none',origin='lower') #interpolation="nearest"
     cbar=plt.colorbar(im0)
     cbar.set_label("Expected number of infections")
     plt.savefig(file_loc+r"\expected_number_of_infections.pdf",bbox_inches='tight',dpi=600)
     plt.savefig(file_loc+r"\expected_number_of_infections.jpg",bbox_inches='tight',dpi=600)
     plt.clf()

     # save csv file for the daily infections
     df=pd.DataFrame.from_dict(daily_infection_report)
     df.to_csv(file_loc+r"\daily_infection_results.csv")


     #Box_plot of number of infections per day on average 
     df.boxplot()
     plt.xticks(rotation=45)
     plt.ylabel("New infections")
     plt.xlabel("Date")
     plt.savefig(file_loc+r"\daily_infection_boxplot.pdf",bbox_inches='tight',dpi=600)
     plt.savefig(file_loc+r"\daily_infection_boxplot.jpg",bbox_inches='tight',dpi=600)
     plt.clf()

     # Boxplot of cummulative number of infections per day
     df.cumsum(axis=1).boxplot()
     plt.xticks(rotation=45)
     plt.ylabel("Infected agents")
     plt.xlabel("Date")
     plt.savefig(file_loc+r"\cum_daily_infection_boxplot.pdf",bbox_inches='tight',dpi=600)
     plt.savefig(file_loc+r"\cum_daily_infection_boxplot.jpg",bbox_inches='tight',dpi=600)
     plt.clf()



     # Plotting number of cummulative infections per day
     fig,ax=plt.subplots(1)
     fig.autofmt_xdate()
     for i in range(len(infected_dates)):
          e_list=infected_number[i]
          days=infected_dates[i]
          if i==0:
               ax.plot(days, e_list,alpha=.25,color='orange',label="Simulation results")
          else:
               ax.plot(days, e_list,alpha=.25,color='orange')
     days = mdates.DayLocator()
     ax.xaxis.set_major_locator(days)
     ax.set_ylabel("Infected agents")
     ax.set_xlabel("Date")
     ax.set_ylim(0,130)
     ax.bar(case_study_date,np.cumsum(np.array(case_study_number)),alpha=.5,color='k',label="Empirical data")
     df=df.transpose()
     ax.plot(df.cumsum().mean(axis=1).index,df.cumsum().mean(axis=1).values,color='red',alpha=1,label="simulation results' Mean")
     plt.legend()
     plt.savefig(file_loc+r"\cum_daily_infection.pdf",bbox_inches='tight',dpi=600)
     plt.savefig(file_loc+r"\cum_daily_infection.jpg",bbox_inches='tight',dpi=600)
     #plt.show(block=True)
     plt.clf()


     # Plot histogram of infection rate in different simulation runs
     plt.hist(attack_rates, density=True, bins=10) 
     plt.xlabel("Infection rate")
     plt.ylabel("Frequency")
     plt.savefig(file_loc+r"\attack_rate_histogram.pdf",bbox_inches='tight',dpi=600)
     plt.savefig(file_loc+r"\attack_rate_histogram.jpg",bbox_inches='tight',dpi=600)
     #plt.show()
     plt.clf()
     simu_results_pic.close()

winsound.Beep(440, 500)

