
"""
This Python module provides a required classes to simulate the spread of Confection disease using an agent-based 
simulation approach. The simulation considers the emission of virus quanta by infected 
agents and calculates the quanta inhaled by healthy agents. Based on stochastic calculations, 
the simulation then predicts probable new infections, make agents infected by chance and continue 
the simulation based on its new status.

The CoDiss module consists of two main classes:Model and Agent. 
Both classes inherit from the ABS (Agent-Based Simulation) module, which is a lightweight and fast 
general-purpose module for agent-based modeling. The ABS module has the capability to 
consider and visualize building layouts and agents' movements according to the defined building obstructions. 

 1) The Model class is responsible for setting up the simulation environment, 
    including defining the parameters and initial conditions of the simulation. 

 2) The Agent class represents individual agents in the simulation, 
    each of which has its own set of properties and behaviors. 


The simulation can be run for a desired period of time, which is specified using the datetime Python module. 
During this time period, the spread of COVID-19 is tracked and visualized using the ABS module. 
The time-step for the simulation is adjustable, allowing for a balance between the speed and accuracy 
of the model. For COVID-19 spread, a time-step equal to 1 minute (60 seconds) is recommended to accurately
capture the spread dynamics. This module provides a powerful tool for understanding the dynamics of 
COVID-19 spread and for designing effective intervention strategies to control the spread of 
the infection disease in buildings. 
"""
__author__ = "Nima Gerami Seresht; Naimeh Sadeghi"
__license__ = "MIT"
__version__ = "1.0.3"
__maintainer__ = "Nima Gerami Seresht; Naimeh Sadeghi"
__email__ = "nima.geramiseresht@gmail.com, naima.sadeghi@gmail.com"
__status__ = "Prototype"


from ABS import agent, model
import random 
import scipy.stats as st
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import datetime
import math
from matplotlib import animation
import matplotlib.dates as mdates

def time_cal(start:datetime.datetime, hours, minutes=0, seconds=0):
        start = datetime.datetime(2022, 1, 1, start.hour, start.minute, start.second)
        end = start + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        return end.time()

def Random_Decider(rand):
        random_decider = random.uniform(0, 1)
        return True if random_decider <= rand else False


def random_location_selector(loc_array):
     loc=loc_array
     j=random.randint(0,len(loc[0])-1)
     return (loc[0][j],loc[1][j])

class CovidModel(model):
    
    def __init__(self, layout,start_date,ventilation_efficiency, infection_rate=[0,0], workhours_per_day=8, \
                  interventions={"mask":[95,95],"test":[1, 60, 14],"isolation":5},\
                workdays= 5, ghatherings = [],time_step=1,grid_size=1.5):
        '''
        inputs:
        num_teams: number of all the workers on the site, the same as the number of agents
        num_crew: the same as the number of working locations infection_rate: number of agents who are 
        ill at the start of the simulation.
        crew characteristics:
            if site layout plan is given, crew characteristics is a list including dictionaries for each crew presenting the following informaiton respectively
                [{crew size, work position, warehouse position, task randomizer, shift}, {...}]
            if site layout is not given, the library makes the dictionaries automatically, but the crew characteristics will be a list of following values:
                [project team size, number of crews, (warehouse location), task randomizer, number of shifts]
        layout:
            A matrix showing the layout of the construction site, a 1 means two grids have a connection and 0 means the grids have no connection 
        ventilation:
            Specifies the ventilation rate in each cell in the network. lower ventilation indicates indoor space.
        interventions: 
            "mask":[mask efficiency, mask compliance], 
            "vaccination":[vaccination efficiency, vaccination compliance]
            "test":[interval between tests in days,test accuracy in percentage,isolation duration]
        '''
        self.site_width,self.site_height=layout.shape
        self.grid_size=grid_size
        self.time_step=time_step
        self.gravitational_settleing=np.array([0.9999658,0.99984729,0.99944496,0.99866597])**self.time_step
        self.inactivation=0.999824978151303**self.time_step
        self.ci=st.uniform(.01,.1) # a factor? .01 to .1
        self.viral_load={(0,1):st.uniform(1e2,5e4-1e2),(1,2):st.uniform(5e4,1e7-5e4),(2,4):st.uniform(2e7,2.5e8-2e7),(4,6):st.uniform(5e4,2e7-5e4),(6,10):st.uniform(1e2,1e6),(10,14):st.uniform(1e1,1e4)}#viral load based on days
        

        self.vaccine_viral_load_factor=1/4.78 
        self.asymptotic_probability=0.05
        self.sympotom_development=st.uniform(2,8-2) #days after infection
        
        #raspitory infection deseases factors
        self.IR={1:st.uniform(1.38*self.time_step/3600,(3.3-1.38)*self.time_step/3600),2:st.uniform(1.38*self.time_step/3600,(3.3-1.38)*self.time_step/3600)}
        self.N=np.array([0.084,0.009,0.003,0.002]) #arosel emmission for different channels when breathing
        self.V=np.array([2.14,24.42,179.59,696.91])*1e-8
        self.N_factor={1:st.uniform(1,1),2:st.uniform(1.5,3.4-1.5),3:st.uniform(20,30-20)} #number of particles based on task
        
        super().__init__(layout, start_date=start_date, time_step=time_step)
        self.ventilation_efficiency = ventilation_efficiency # determines how much volume of fresh air (or sanitized air) is blown into the space in each hour (measured as the proportion of the space volume)
        
        self.infection_rate = infection_rate[0]
        self.camp_infection_rate = infection_rate[1]
        self.site_workhours = [self.start_time.time(), time_cal(self.start_time, workhours_per_day)]
        self.site_workhours[1]=datetime.timedelta(hours=self.site_workhours[1].hour,minutes=self.site_workhours[1].minute)
        self.workdays = workdays
        self.workhours_per_day = workhours_per_day 
        self.gatherings=ghatherings
        for gathering in self.gatherings:
            gathering["happened"]=False
        #isolation 
        self.isolation_loc = (self.site_width  - 1, self.site_height - 1)
        self.isolation_node=str(self.isolation_loc).strip("()")
        
       
        
        ### Virus content and infected people
        self.quanta_matrix=np.zeros([self.site_width, self.site_height,4],dtype=np.float64) #considering four channels
        self.total_quanta=self.quanta_matrix[:,:,0]+self.quanta_matrix[:,:,1]+self.quanta_matrix[:,:,2]+self.quanta_matrix[:,:,3]
        self.total_inhaled_matrix=self.total_quanta.copy()
        self.infection_matrix=np.zeros([self.site_width, self.site_height],dtype=np.float64)
        self.mortality = []
        self.simulated_days=[]
        
        

        right_spread=np.int0(np.logical_and([self.layout!=3],[self.layout!=2]))
        left_spread=np.roll(right_spread,1,axis=1)
        left_spread[0][0,:]=1
        up_spread=np.int0(np.logical_and([self.layout!=3],[self.layout!=1]))
        down_spread=np.roll(up_spread,1)
        down_spread[0][:,0]=1

        #ventilation
        self.left_spread=8e-4/self.grid_size*self.ventilation_efficiency/4 *left_spread[0]*self.time_step
        self.right_spread=8e-4/self.grid_size*self.ventilation_efficiency/4*right_spread[0]*self.time_step
        self.up_spread=8e-4/self.grid_size*self.ventilation_efficiency/4*up_spread[0]*self.time_step
        self.down_spread=8e-4/self.grid_size*self.ventilation_efficiency/4*down_spread[0]*self.time_step
       
        #*****Interventions*****
        self.interventions = interventions
        self.mask_compliance = 0
        self.mask_efficiency = 0.0 #determines the efficiency of the mask worn by each agent; 0 for no maks.
        if "mask" in self.interventions:
            self.mask_efficiency = self.interventions["mask"][0].rvs() / 100
            self.mask_compliance = self.interventions["mask"][1] / 100
        self.daily_infection_report={self.now.date():0}

  
    def add_crew(self,crew):
        agents=[]
        for i in range(crew["crew size"]):
            if "vaccine" in self.interventions:
                a=CovidAgent(self, id,crew['tasks'],crew["shift"],\
                    vaccination=self.interventions["vaccine"]) #create a new convidAgent
            else:
                a=CovidAgent(self, id,crew['tasks'],crew["shift"]) #create a new convidAgent

            if "marker" in crew:
                a.marker=crew["marker"]
            if "color" in crew:
                a.color=crew["color"]
            if "speed" in crew:
                a.speed=crew['speed']
            if Random_Decider(self.infection_rate):
                a.get_infected(self.now)
            a.active=False
            agents.append(a)
        return agents


    def step(self):
                  
        #running covid tests on a pre-specified time intervals
        if "test" in self.interventions:
            interval=self.interventions["test"][0]
            accuracy=self.interventions["test"][1] / 100
            duration=self.interventions["test"][2]
            if self.now.time() == self.start_time.time() and (self.now.date() - self.start_time.date()).days % interval == 0:
                self.__Test_Intervention(accuracy, duration)

        
        #work calendar arrangement
        now_timedelta=datetime.timedelta(hours=self.now.time().hour,minutes=self.now.time().minute).seconds
        if self.site_workhours[1].seconds+self.time_step>now_timedelta >= self.site_workhours[1].seconds:
            self.now += datetime.timedelta (days=1, hours=-1* self.workhours_per_day, seconds=-1*self.time_step)

        #at the start of each day
        if self.now.time() == self.start_time.time() and self.now.date()!=self.start_time.date(): #sets the total volume of viruses back to zero at the start of each day
            self.daily_infection_report[self.now.date()]=0
            for a in self.agents:
                if a.healthy:
                    a.check_infection() # check if a has been infected when outside work
                elif not a.healthy and a.task_type==4: # check if agent can come out from isolation
                    a.check_finish_isolation()
                elif not a.healthy and not a.symptotic:
                    a.check_symptom_start()
            while self.now.weekday() >= self.workdays: # note: I changed if to while here
                self.now += datetime.timedelta(days=1)
                self.daily_infection_report[self.now.date()]=0
            self.quanta_matrix = np.zeros([int(self.site_width), int(self.site_height),4],dtype=np.float64)
            
            
            
            for gathering in self.gatherings:#at the start of each day, set the start of each gathering to False
                gathering["happened"]=False
                
            if ' ' in self.interventions:
                for a in self.agents:
                    if not a.healthy and a.symptotic and a.task_type!=4 and a.isolation_finished==False:
                        duration=int(self.interventions['isolation'].rvs())
                        print("Agent took", duration, "days off due to symptom development at time: ",self.now)
                        a.isolate(duration)
                        a.check_finish_isolation()
  
        else:
            self.Decay()
            self.quanta_spread()
            self.total_quanta+=(self.quanta_matrix[:,:,0]+self.quanta_matrix[:,:,1]+self.quanta_matrix[:,:,2]+self.quanta_matrix[:,:,3])

        for gathering in self.gatherings:
            if not gathering["happened"] and gathering["start"]<=self.now.time():
                gathering["happened"]=True
                active_agents=self.get_active_agents()
                gathering_agents=random.sample(active_agents,min(gathering["size"],len(active_agents)))
                gathering_duration=gathering["duration"]
                for a in gathering_agents:
                    a.go_to_gathering(gathering["location"],gathering_duration)
        for a in self.agents:
            # modeling half day working in south Korea, 4 hours is only for the case sutdy
            # this should change for different locations and situations
            # Future: add this option to the agent based model
            now_timedelta=datetime.timedelta(hours=self.now.time().hour,minutes=self.now.time().minute,seconds=self.now.time().second)
            if (self.now.weekday()<self.workdays and a.shift[0]<=now_timedelta<a.shift[0]+a.shift[1]) or (self.now.weekday()==self.workdays and a.shift[0]<=now_timedelta<a.shift[0]+datetime.timedelta(hours=5)) and a.task_type!=4:
                if not a.active:
                    a.arrive()
            else:
                if a.active and not a.is_leaving:
                    a.leave()
        super().step() 
            #runs step for all active agents 
            #and increases the simulation time
            #according to the time step


    def Decay(self):   
        d=self.inactivation*self.gravitational_settleing
        #the infecation content decreases in each step
        self.quanta_matrix[:,:,0]*=d[0] 
        self.quanta_matrix[:,:,1]*=d[1] 
        self.quanta_matrix[:,:,2]*= d[2] 
        self.quanta_matrix[:,:,3]*= d[3] 
      
    
    def __Test_Intervention (self, accuracy, duration):
        for agent in self.agents:
            if agent.task_type!=4:
                temp = agent.task
                agent.task_type = 5
                if not agent.healthy and Random_Decider(accuracy):
                    print("Agent is taking",duration,"days off due to testing intervention at time: ",self.now)
                    agent.isolate(duration)
                else:
                    agent.task_type = temp
        self.now += datetime.timedelta(minutes=duration)


    def get_active_agents(self):
        r=[]
        for a in self.agents:
            if a.active:
                r.append(a)
        return r

    def myrun(self, end_date,interventions=None):
        import time
        start_run=time.time()
        if interventions!=None:
            self.interventions=interventions
            if "mask" in self.interventions:
                self.mask_efficiency = self.interventions["mask"][0].rvs() / 100
                self.mask_compliance = self.interventions["mask"][1] / 100
        self.step()
         
        while self.now<end_date:
            self.step()

        print("end run:",time.time()-start_run)

    def Run(self, duration, outputs, live = False):
        """
        This function is not working or tested yet
        run the simulation model for the specified duration
        Parameters
        ----------
        duration : int
            DESCRIPTION.
        output : list of strings
            A list indicating the outputs of the model
            "daily infections" indicates a report of infected people at the end of each day
        Returns
        -------
        None.

        """
        results = {'Simulation Time': []}

        #calcuates the time of the simulation for the end of date
        end_date = self.start_time +datetime.timedelta(days=int(duration * 7 / self.workdays))
        
        for key in outputs:
            results.update({key : []})
        
        if self.now <= self.end_date:
            simulation_time = results['Simulation Time']
            simulation_time.append(self.now)
            results.update({'Simulation Time' : simulation_time})

            if "mortality" in outputs:
                mortality = results['mortality']
                mortality.append(self.mortality)
                results.update({'mortality' : mortality})
      
            self.step()
        else:
            print("Simulation run is completed")
            return results

    def quanta_spread(self):

        for ch in range(4):#for each channel
            left_quanta_spread=self.left_spread*self.quanta_matrix[:,:,ch]
            right_quanta_spread=self.right_spread*self.quanta_matrix[:,:,ch]
            up_quanta_spread=self.up_spread*self.quanta_matrix[:,:,ch]
            down_quanta_spread=self.down_spread*self.quanta_matrix[:,:,ch]
            
            left_spread_roll=np.roll(left_quanta_spread,-1,axis=0)#arent we doing the roll 4 times for each cell?
            left_spread_roll[-1,:]=0

            right_spread_roll=np.roll(right_quanta_spread,1,axis=0)
            right_spread_roll[0,:]=0

            up_spread_roll=np.roll(up_quanta_spread,1,axis=1)
            up_spread_roll[:,0]=0

            down_spread_roll=np.roll(down_quanta_spread,-1,axis=1)
            down_spread_roll[:,-1]=0

            total_spread=left_spread_roll+right_spread_roll+up_spread_roll+down_spread_roll-right_quanta_spread-left_quanta_spread-up_quanta_spread-down_quanta_spread
            self.quanta_matrix[:,:,ch]+=total_spread
    
    def attack_rate(self):
        results={}
        total_ill=0
        dates=[]
        numbers=[]
        for d in self.daily_infection_report:
            dates.append(d)
            numbers.append(self.daily_infection_report[d])
        attack_rate=sum(numbers)/len(self.agents)*100
        return attack_rate,dates,numbers

    def plot_daily_infections(self,file_name=None):
        t=self.attack_rate()
        rate=t[0]
        dates=t[1]
        numbers=t[2]
        fig,ax=plt.subplots(1)
        ax.bar(dates,numbers)
        ax.set_ylabel("Number of new infections")
        ax.set_xlabel("Date")
        fig.autofmt_xdate()
        if file_name!=None:
            plt.savefig(file_name+'.png')
            plt.savefig(file_name+'.pdf')
        plt.show()

    
        

    def animate_quanta_matrix(self,p_duration=3600,max_prob=.00001,until=1000,frames=200, interval=20):
        self.fig,self.ax=plt.subplots()
        self.plot_layout(self.ax)
        a=np.random.rand(self.site_width,self.site_height)*max_prob
        im0 = self.ax.imshow(a.T,   cmap='Reds', interpolation='none',origin='lower') #interpolation="nearest"
        title=plt.title(str(self.now))
        cbar=plt.colorbar(im0)
        cbar.set_label("Probability")

        def animate(i):
            self.step()
            a= self.quanta_matrix[:,:,0]+self.quanta_matrix[:,:,1]+self.quanta_matrix[:,:,2]+self.quanta_matrix[:,:,3]
            a=1-np.exp(-p_duration*1.3*a/3600) #IR/3600*a*3600(for one minute) a will be the probability of getting infected after p_duration (one minute default value)
            a[self.isolation_loc[0],self.isolation_loc[1]]=0
            im0.set_array(a.T)
            title.set_text(str(self.now))
            return [im0]
        animate(1)
        self.anim = animation.FuncAnimation(self.fig, animate, 
                               frames=frames, interval=interval, blit=False)
        plt.show(block=True)

    def plot_dangar_zones(self,max_prob=None,file_name=None):
        """
        This function plots the heatmpat of the building
        based on the probability of getting infected if a person is in that zone
        for the duration of the simulation
        """
        self.fig,self.ax=plt.subplots()
        self.plot_layout(self.ax)
        if max_prob!=None:
            a=np.random.rand(self.site_width,self.site_height)*max_prob
            im0 = self.ax.imshow(a.T,   cmap='Reds', interpolation='none',origin='lower') #interpolation="nearest"
            plt.title(str(self.now))
            cbar=plt.colorbar(im0)
            cbar.set_label("Probability")
            a=1-np.exp(-2/3600*self.total_quanta*self.time_step) 
            a[self.isolation_loc[0],self.isolation_loc[1]]=0
            im0.set_array(a.T)
        else:
            a=1-np.exp(-2/3600*self.total_quanta) 
            a[self.isolation_loc[0],self.isolation_loc[1]]=0
            im0 = self.ax.imshow(a.T,   cmap='Reds', interpolation='none',origin='lower') #interpolation="nearest"
            plt.title(str(self.now))
            cbar=plt.colorbar(im0)
            cbar.set_label("Probability")
        if file_name!=None:
            plt.savefig(file_name+".pdf")
            plt.savefig(file_name+".jpg")
        plt.show(block=True)
        
    def infection_probability_matrix(self):
        """
        return the probability of getting infected if a healthy person is in one zone during the simulation
        """
        return 1-np.exp(-2/3600*self.total_quanta) 
    def effective_infection_probability_matrix(self):
        """
        return the probability of getting infected in each zone
        """
        return  1-np.exp(-self.total_inhaled_matrix) 

    def plot_effective_danger_zones(self,file_name=None):
        """
        This function plots the 
        """
        self.fig,self.ax=plt.subplots()
        self.plot_layout(self.ax)
        a=1-np.exp(-self.total_inhaled_matrix) 
        im0 = self.ax.imshow(a.T,   cmap='Reds', interpolation='none',origin='lower') #interpolation="nearest"
        plt.title(str(self.now))
        cbar=plt.colorbar(im0)
        cbar.set_label("Probability")
        if file_name!=None:
            plt.savefig(file_name+".pdf")
            plt.savefig(file_name+".jpg")
        plt.show(block=True)
       
        


    def _plot_sperad_direction(self):
        """
        This is only to test that the directions of spread is correctly defined for model, 
        it is not for reporting purposes
        """
        fig,ax=plt.subplots(2,2)
        ax[0,0].imshow(self.left_spread.T,   cmap='Reds', interpolation='none',origin='lower')
        ax[0,0].set_title("left spread")
        self.plot_layout(ax[0,0])

        ax[0,1].imshow(self.right_spread.T,   cmap='Reds', interpolation='none',origin='lower')
        ax[0,1].set_title("right spread")
        self.plot_layout(ax[0,1])

        ax[1,0].imshow(self.down_spread.T,   cmap='Reds', interpolation='none',origin='lower')
        ax[1,0].set_title("down spread")
        self.plot_layout(ax[1,0])

        ax[1,1].imshow(self.up_spread.T,   cmap='Reds', interpolation='none',origin='lower')
        ax[1,1].set_title("up spread")
        self.plot_layout(ax[1,1])

        plt.show()
        fig,ax=plt.subplots(2,2)
        left_spread_roll=np.roll(self.left_spread,-1,axis=0)#arent we doing the roll 4 times for each cell?
        left_spread_roll[-1,:]=0

        right_spread_roll=np.roll(self.right_spread,1,axis=0)
        right_spread_roll[0,:]=0

        up_spread_roll=np.roll(self.up_spread,1,axis=1)
        up_spread_roll[:,0]=0

        down_spread_roll=np.roll(self.down_spread,-1,axis=1)
        down_spread_roll[:,-1]=0

        ax[0,0].imshow( left_spread_roll.T,   cmap='Reds', interpolation='none',origin='lower')
        ax[0,0].set_title("left spread")
        self.plot_layout(ax[0,0])

        ax[0,1].imshow(right_spread_roll.T,   cmap='Reds', interpolation='none',origin='lower')
        ax[0,1].set_title("right spread")
        self.plot_layout(ax[0,1])

        ax[1,0].imshow(down_spread_roll.T,   cmap='Reds', interpolation='none',origin='lower')
        ax[1,0].set_title("down spread")
        self.plot_layout(ax[1,0])

        ax[1,1].imshow(up_spread_roll.T,   cmap='Reds', interpolation='none',origin='lower')
        ax[1,1].set_title("up spread")
        self.plot_layout(ax[1,1])
        plt.show()

class CovidAgent(agent):
    """
        self.task indicates the state of agent at work, 1 traveling and 2 is staying;
        4 is isolating; and 5 is testing time freeze
    """
    def __init__(self, model:model,id, tasks, shift, vaccination=[st.uniform(0,0),0],speed=1):
        
        '''
        tasks:
        a list of tasks that the agnet can perform:
        {task_location,task_duration in time-steps,task_probability}
        speed is the number of cells per time step. 

        -----notes---
            Whether a person is talking, singing or just breathing impacts the number and distribution 
            of droplets and arosol that may cuase infection. An attribute is assinged to each agent to 
            indicate which of the following activities are perfomed by the agent: breathing, talking, ...
            According to 
            https://www.nature.com/articles/s41598-020-79985-6
            aerosols and droplets emmited due to coughing of a SARS-CoV patients contain very limited amont
            of the Covid virus. 

            "In order to quantify the deposition distribution of cough-generated droplets and 
            aerosol particles containing SARS-CoV-2, we applied the Stochastic Lung Deposition Model. 
            It was found here that the probability of direct infection of the acinar airways due to 
            inhalation of particles emitted by a bystander cough is very low. As the number of viruses 
            deposited in the extrathoracic airways is about 7 times higher than in the acinar airways, 
            we concluded that COVID-19 pneumonia must be preceded by SARS-CoV-2 infection of the upper 
            airways in most cases."
            Therefore, couphing is not  considered as an important status to quantify infectios aerosols emmited 
            from a person in this simuation.
        '''
    
        #health status
        self.healthy=True
        self.symptotic=False
        self.color='g'
        self.inhaled=0
        self.shift = shift
        
        # decide by chance if the person is vaccinated and provides an immunity percentage
        self.immunity = (Random_Decider(vaccination[1] / 100) * vaccination[0].rvs() / 100) 
        if self.immunity>0:
            self.vaccinated=True
        else:
            self.vaccinated=False
        self.infection_time = []
        self.infection_dates = []
        self.symptom_start_date = None

        self.tasks = tasks
        self.arrive()
        super().__init__(model,id,self.node,color=self.color,speed=speed)
      
        #isolation
        self.isolation_time = [] #storing the starting time of self isolation
        self.isolation_dur=0
        self.isolation_finished=False
        self.agent_paths={} #find paths from to
        self.is_leaving=False
        self.gathering_remaining_duration=0


    def arrive(self):
        tasks=self.tasks
        self.is_leaving=False
        self.active=True
        self.pos=self.tasks[0][0]
        self.stay_dur=tasks[0][1]
        self.node=str(self.pos).strip("()")  #str:i,j
        self.task_type = 2
        self.face=1# 1:breathing, 2:normal talking, 3.loud talking or singing,4.sneezing 
        

    def leave(self):
        """
        set the destination of the agent to leave the building
        the task type wll be also travelig 
        """
        self.is_leaving=True
        self.task_type=1
        t=self.tasks[0]
        destination=str(t[0]).strip('()')
        if (str((self.node,destination)) in self.agent_paths):
            p=self.agent_paths[str((self.node,destination))]
        else:
            p=list(nx.dijkstra_path(self.model.graph,self.node,destination))
            self.agent_paths[str((self.node,destination))]=p
        self.set_path(p)
        
    def go_to_gathering(self,location,duration):
        self.task_type=1
        destination=str(random_location_selector(location)).strip('()')
        self.gathering_remaining_duration=duration
        if (str((self.node,destination)) in self.agent_paths):
            p=self.agent_paths[str((self.node,destination))]
        else:
            p=list(nx.dijkstra_path(self.model.graph,self.node,destination))
            self.agent_paths[str((self.node,destination))]=p
        self.set_path(p)

    def step(self):
            if self.task_type!=4: #it is not in isolation
                if self.task_type == 2:

                    if self.stay_dur>0:
                        self.stay_dur-=1
                    else:
                        if not self.is_leaving:
                            self.start_new_task()
                        else:
                            self.active=False
                            self.is_leaving=False
                elif self.task_type == 1: #traveling between different positions
                    if self.is_arrived():
                        self.task_type=2 #stay in that position
                        self.stay_dur=self.get_stay_dur()
                    else:
                        self.walk()
    
                if not self.healthy:
                    self.emit_quanta()
                else:
                    if not self.healthy:
                        print("I should not be here1")
                    self.inhaling()
            
            #getting infected when outside work
            now_timedelta=datetime.timedelta(hours=self.model.now.time().hour,minutes=self.model.now.time().minute,seconds=self.model.now.time().second)
            if self.healthy and now_timedelta == self.shift[0]+self.shift[1]:
                if Random_Decider(self.model.camp_infection_rate * self.immunity) and self.healthy:
                    self.get_infected(self.now-datetime.timedelta(days=1)) #at start of each day agents get infected by the camp infection chance; if no camp the infection rate is equal to the general rate
                    
    def start_new_task(self):
        r=random.random()
        prob=0
        p=[]

        for t in self.tasks:
            prob+=t[2]
            if r<prob:
                #travel to this position
                destination=str(t[0]).strip('()')
                if (str((self.node,destination)) in self.agent_paths):
                    p=self.agent_paths[str((self.node,destination))]
                    break
                elif t[0] != self.pos:
                    try:
                        
                        p=list(nx.dijkstra_path(self.model.graph,self.node,destination))
                        self.agent_paths[str((self.node,destination))]=p
                        break
                    except:
                        p=[]
                        break
                else:
                    p=[]
                    break
        if p == []:
           self.task_type=2
           self.stay_dur=self.get_stay_dur()
        else:
            self.task_type=1
            self.set_path(p)

    def is_arrived(self):
        """
        returns true if agent arrived to the end of its assigned path
        """
        return self._path[-1]==self.node
    
    def get_stay_dur(self):
        """
        returns the duration that the agent will remain in the specified position
        """
        if self.gathering_remaining_duration>0:
            value=self.gathering_remaining_duration
            self.gathering_remaining_duration=0
            return value
        for t in self.tasks:
            if self.pos==t[0]:
                return t[1]
    def inhaling(self):
        """
        Adds quanta to the inhaled amount of virus 
        """
        #Wells–Riley equation (Riley et al., 1978)
        n=sum(self.model.quanta_matrix[self.pos[0],self.pos[1]])
        IR=self.model.IR[self.task_type].rvs()
        mask_facor=(1 - self.model.mask_efficiency * Random_Decider(self.model.mask_compliance))
        inhaled_now=IR*n*mask_facor
        self.inhaled+=inhaled_now
        if inhaled_now>0:
            self.model.total_inhaled_matrix[self.pos[0],self.pos[1]]+=inhaled_now.copy()
            self.model.infection_matrix[self.pos[0],self.pos[1]]+=1-np.exp(-inhaled_now)

    def check_infection(self):
        """
        Give a chance to an agnet to get infected or not depending on the inhaled amount of q
        """
        R=1-math.exp(-self.inhaled)
        if self.healthy and Random_Decider(R * (1-self.immunity)):
            self.get_infected(self.model.now-datetime.timedelta(days=1)) #since check infection is at the start of next day, the day of infection is actually the previous day
            
        self.inhaled=0



    def get_infected(self,infection_time="now"):
        if infection_time=="now":
            self.infection_time.append(self.model.now) 
            self.model.daily_infection_report[self.infection_time[-1].date()]+=1
        else:
            self.infection_time.append(infection_time)
            self.model.daily_infection_report[self.infection_time[-1].date()]=1
        print("A new agent is infected at time", self.infection_time[-1])
        self.infection_dates.append(str(self.infection_time[-1].date()))
        self.symptom_start_date=self.infection_time[-1]+datetime.timedelta(days=self.model.sympotom_development.rvs())
        self.healthy=False
        self.color='r'
        self.isolation_finished=False

    def check_symptom_start(self):
        if self.symptotic:
            return
        if self.model.now>self.symptom_start_date:
            self.symptotic=True

    def isolate(self,duration):
        '''
        Isolates an agent to simulate isolation
        '''
        
        self.pos=self.model.isolation_loc
        self.node=self.model.isolation_node
        self.task_type=4 #it is in isolation
        self.isolation_time.append(self.model.now)
        self.isolation_dur=duration
        self.active=False
        
    
    def check_finish_isolation(self):
        diff=self.model.now-self.isolation_time[-1]
        if diff.days>=self.isolation_dur:
            self.isolation_finished=True
            self.task_type=1
            print("Agent come back to work at time: ", self.model.now)
            
    def get_viral_load(self):
        '''
        returns the viral load in an agents mucus

       
        The base value for ct is defined as a random variable. 
        normal distribution is assumed for log10 value of ct becuase the underlying 
        distribution type is not known and most natural phenomas
        can be modeled with normal distribution.
        the 50th percentile equal to ... reported in paper:
         "Infectious viral load in unvaccinated and vaccinated patients infected with SARS-CoV-2 WT, Delta and Omicron"
         is used as the mean value for the nomral distribution.
        The standard deviation is calcuated
        based on 25th(q25) an 75th(q75) percentiles reported in the above paper.
        Thus the baseline ct (ct_ref) is defined as 
         equation:       ct_ref=10^normal(mean=,std=)
        This ct value is then updated based on the vaccination status of a patient.

         Accoding to the paper:
        "Infectious viral load in unvaccinated and vaccinated patients infected with SARS-CoV-2 WT, Delta and Omicron"
        vaccinated people, when infected, have decreased levels of viral load compared to unvaccinated people.
        Also, no elevated viral load is seen in 
        Omicron varient compared to Delta, 
        "suggesting that other mechanisms than increase VL contribute to the high infectiousness of Omicron." 
        "Overall, RNA genome  copies were significantly lower in vaccinated vs. unvaccinated patients 
        (2·5 fold, 0·40 log10, p=0·0005). 
         The decrease in infectious VL was even more pronounced in vaccinated patients 
         (4·78 fold, 0·68 log10, 231 ****p<0·0001)"

        Therefore, if a patient is vaccinated the ct value is updated accordingly (decreased 4.78 folds).
        
        The viral load is furhter updated based on the number of days a patient have been 
        infected.

        in the following paper: 
        "Viral dynamics in mild and severe cases of COVID-19"
        "We previously reported that the viral load of severe acute respiratory syndrome 
        coronavirus (SARS-CoV-2) peaks within the first week of disease onset.1,2
        Findings from Feb, 2020, indicated that the clinical spectrum of this 
        disease can be very heterogeneous. Here, we report the viral RNA shedding 
        patterns observed in patients with mild and severe COVID-19."
        '''
        
        load=self.model.viral_load
        vaccine_f=self.model.vaccine_viral_load_factor
        if len(self.infection_time)==0:
            return 0     
        days=self.model.now-self.infection_time[-1] #calculate number of days patient infected
        days=days.days
        for k in load:
            if k[0]<=days<k[1]:
                if self.vaccinated:
                    return load[k].rvs()*vaccine_f
                else:
                    return load[k].rvs()
        self.healthy=True
        self.color='g'
        self.symptom_start_date=None
        self.symptotic=False
        return 0    

    def update_face_status(self):
        '''
        updates the status of a persons face
        1:breathing
        2:talking
        3:singing
        4:sneezing
        
        Accoding to 
        https://onlinelibrary.wiley.com/doi/full/10.1111/joim.13326
        "In contrast to several other types of respiratory tract infection, 
         sneezing is not among the common symptoms of infection with SARS-CoV-2 [55, 60]."
        Therefore, probability of sneezing is considerd the same for a noraml or infected agent. 
         Nevertheless, it is important to model sneezing as if tirggered, " a sneeze by a carrier will generate 
         a large cloud of virus-laden respiratory fluid droplets [61]."
        
        Accoding to a study in 
        paper:https://europepmc.org/article/med/12012947
        the average number of sneezes per person is equal to 3 sneezes per day. therefore
        the probability of sneezing per second per person is assumed equal 3/24*8*3600
        note:would you please check that in the paper, I coudn't find the text.

        probability of other possible tasks like breathing, talking or singing is considered equal
        '''
        psneez=4.3e-6*self.model.step
        if Random_Decider(psneez):
            self.face=4
        elif Random_Decider(.25):
            self.face=3
        elif Random_Decider(.5):
            self.face=2
        else:
            self.face=1
        return True

    def emit_quanta(self):
        
        N=self.model.N*self.model.N_factor[self.face].rvs()
        V=self.model.V
        IR=self.model.IR[self.task_type].rvs()
        ci=self.model.ci.rvs()
        mask_factor=(1 - self.model.mask_efficiency) * Random_Decider(self.model.mask_compliance)
        a=self.get_viral_load()
        quanta=a*ci*IR*N*V*(1-mask_factor)
        self.model.quanta_matrix[self.pos[0],self.pos[1]]+=quanta

        #1:breathing
        #2:talking
        #3:singing
        #4:sneezing

        #*****************
        #Inhalation rate
        #2:direct work, stay in the cell
        #1:walk to material wharehouse
        #3:personal time
        '''
        Emits quanta of the agent for four different channels
        and updates the quanta matrix

        
        **************supporting litreature******************
        In the study :
        paper:Comparing aerosol concentrations and particle size distributions generated by singing, speaking and breathing

        Different size distributions are reported for aerosol mass concentration"
        "This comparison is most important when considering the potential of the different 
        activities to transmit infection.
        "
        The concentration of particles with diamter greater than 10 micro meter was detected very low
        in all cases in this sutyd. 
        Therfore, no channel is condiered for particles above 10 micro meter.


        this function employs
            self.face
            self.viral_load

        Accodring to ...
        https://www.tandfonline.com/doi/abs/10.1080/02786826.2021.1883544


        table in:
        https://first10em.com/aerosols-droplets-and-airborne-spread/
        provided the number of droplets for a single sneeze vs. a single couph.
        We calculated the ratio between a couph and a sneeze for different channels using these numbers. 
        excel file: table sneeze to couph


        In the study :
        paper:Comparing aerosol concentrations and particle size distributions generated by singing, speaking and breathing
        the size and the number of droplets generated due to singing, speaking and couphing are compared. 
        According to their study,
        "
        at the quieter volume (50 to 60 dBA), neither singing (p = 0.19) nor speaking (p = 0.20) were 
        significantly different to breathing. At the loudest volume (90 to 100 dBA), 
        a statistically significant difference (p < 0.001) was observed between singing and speaking,
         but with singing only generating a factor of between 1.5 and 3.4 more aerosol mass. 
        "

        "
        Measured size distributions for speaking and singing were fitted to bimodal lognormal distributions,
        consistent with previous studies for speaking, breathing and coughing (Asadi et al. 2019; Johnson et al.
        2011; Morawska et al. 2009). The fits for the different
        "

        "
        Speaking and singing generated statistically significant differences in mass concentrations 
        of aerosol at similar level of loudness; however, these were modest 
        (median singing values only a factor of 1.5–3.4
        times larger than speaking) relative to the effects of
        the loudness of vocalization (a factor of 20–30
        increase). Converting from a number concentration to
        a mass concentration for breathing, resulted in the
        mass concentration range shifting to lower values relative to speaking and singing,
         a consequence of the different size distributions associated with voicing and
        breathing (median values 24 and 36 times higher for
        speaking and singing at the highest loudness, respectively, compared with breathing).
        "
        Also, according to their results, concentration of droplets due to couphing is higher 
        with a factor between 3 to 14. The ration of concentration in each channel is 
        caclculated according to excel file 
        '''
        
        '''
        according to paper:"Estimation of airborne viral emission: Quanta emission rate of SARS-CoV-2 for infection risk assessment"
        (resting, standing, light exercise, moderate exercise, and heavy exercise)
        averaged between males and females, are equal to 
        0.49, 0.54, 1.38, 2.35, and 3.30 m3 h−1, respectively
        '''
        '''
         according to paper:"Estimation of airborne viral emission: Quanta emission rate of SARS-CoV-2 for infection risk assessment"
        The conversion factor, ci , i.e. the ratio between one infectious quantum and the infectious dose
        expressed in viral RNA copies, barely represents the probability of a pathogen surviving inside the
        host to initiate the infection; thus ci=1 implicitly assumes that infection will occur for each
        pathogen (RNA copy in the case of SARS-CoV-2) received by the exposed people. There are
        currently no values available in the scientific literature for ci for SARS-CoV-2. Watanabe et al. 27 124
        estimated the infectious doses of several coronaviruses on the basis of data sets challenging
        humans with virus HCoV-229E (known as an agent of human common cold) and animals with
        other viruses (e.g. mice with MHV-1, considered as a surrogate of SARS-CoV-1). On the basis of the
        orders of magnitude of 
        the infectivity conversion factors for the overall data sets, we assumed a cirange between 0.01 and 0.1.
        '''
        
             

