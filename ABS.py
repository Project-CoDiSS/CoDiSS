

"""
This file is transferred from the AgentBuilt project:
 
 https://github.com/Project-AgentBuilt/AgentBuilt

The ABS (Agent-Based Simulation) module enables agent-based modeling in the built environment. 
With its lightweight design and fast processing speed, it efficiently simulates complex systems. 
The ABS module considers building layouts and agents' movements, factoring in defined obstructions.

The module employs a grid-based approach for swift and effective simulation. 
It also utilizes the networkX library to generate a graph of the building and 
efficiently track agents' locations, assigning them optimal paths between locations.

The ABS module includes two primary classes: Model, which creates the simulation environment, 
and Agent, which models individual agents. The module uses the matplotlib library to animate 
agents' movements and the datetime module to track simulation time.
"""
__author__ = " Naimeh Sadeghi;Nima Gerami Seresht;"
__license__ = "MIT"
__version__ = "1.0.2"
__maintainer__ = "Naimeh Sadeghi;Nima Gerami Seresht"
__email__ = "naima.sadeghi@gmail.com;nima.geramiseresht@gmail.com,"
__status__ = "Prototype"

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
import datetime


class model():
    def __init__(self,layout,start_date: datetime.datetime, time_step):
        '''
        Create the model with the specified start date and the time step expressed in seconds; then,
        Create the model grid from layout, the layout is a numpy array representing cells
        in the model. each cell value can be either 0, 1, 2, or 3.
        1: a block under the cell
        2: a block right of the cell
        3: a block under and right of a cell 
        0: no block under or right of the cell
        '''
        self.layout=layout
        self.graph=self.make_graph()
        self.agents=[] # a dictionary with  node name and list of agents in that position
        self.now = start_date
        self.start_time = start_date
        self.time_step = time_step

    def make_graph(self):
        '''
        creates a graph for the layout in which the node names are 
        represented as "i,j", where i is the row number and j is the column number
        '''
        a=self.layout
        w,h=a.shape
        g=nx.Graph()
        
        #adding nodes to the network
        for i in range(w+1):
            for j in range(h+1):
                    g.add_node(str(i)+', '+str(j),pos=(i,j))
        #adding edges to the network
        for i in range(w):
            for j in range(h):
                if  a[i,j]==0:
                    if j+1<h:
                        g.add_edge(str(i)+', '+str(j),str(i)+', '+str(j+1),weight=1)
                    if i+1<w:
                        g.add_edge(str(i)+', '+str(j),str(i+1)+', '+str(j),weight=1)
                if  a[i,j]==2: #there is a wall on the right of the cell
                    g.add_edge(str(i)+', '+str(j),str(i)+', '+str(j+1),weight=1)
                if  a[i,j]==1:#there is a wall under the cell
                    g.add_edge(str(i)+', '+str(j),str(i+1)+', '+str(j),weight=1)
                
                if i+1<w and j+1<h:
                    if a[i,j]==0  and (a[i,j+1]==0 or a[i,j+1]==1) and (a[i+1,j]==2 or a[i+1,j]==0) and a[i+1,j]!=4:
                        g.add_edge(str(i)+', '+str(j),str(i+1)+', '+str(j+1),weight=1.414)
                if i+1<w and j>0:
                    if a[i,j-1]==0  and (a[i,j]==1 or a[i,j]==0) and (a[i+1,j-1]==0 or a[i+1,j-1]==2) and a[i+1,j]!=4:
                        g.add_edge(str(i)+', '+str(j),str(i+1)+', '+str(j-1),weight=1.414)

        for i in range(w):
            for j in range(h):
                if a[i,j]==4:
                    g.remove_node(str(i)+', '+str(j))
        return g


    def plot_layout(self,ax,color='green',blocksize=12):
        a=self.layout
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
        
        return ax
    
    def plot_graph(self,node_size=100):
        pos=nx.get_node_attributes(self.graph,'pos')
        nx.draw(self.graph,pos,node_size=node_size)
        return plt
    
    def plot_agents(self,size=10):
        for agent in self.agents:
                x,y=agent.pos
                plt.plot(x,y,marker=agent.marker,markersize=size,color=agent.color,alpha=agent.alpha)
        return plt
    
    
    def agent_array(self,cond='True'):
        r=np.zeros(self.layout.shape)
        for agent in self.agents:
            if  eval(cond):
                r[eval(agent.node)]+=1
        return r

    def step(self):
        for agent in self.agents:
                if agent.active:
                    agent.step()
        self.now += datetime.timedelta(seconds=self.time_step)

    def run(self,num_steps=1000):
        for i in range(num_steps):
            self.step()
    
    def animate(self,until=1000,frames=200, interval=20):
        self.fig,self.ax=plt.subplots()
        self.plot_layout(self.ax)
        title=plt.title(str(self.now))
        #self.plot_graph()
        self.lines=[]
        for agent in self.agents:
                
                x,y=agent.pos
                line,=self.ax.plot(x,y,color=agent.color,marker=agent.marker,markersize=agent.size)
                self.lines.append(line)
        def animate(i):
            self.step()
            k=0
            for agent in self.agents:
                #only active agents with the same shift should be shown
                x,y=agent.pos
                self.lines[k].set_data(x, y)
                self.lines[k].set_marker(agent.marker)
                if agent.active:
                    self.lines[k].set(alpha=1)
                else:
                    self.lines[k].set(alpha=0)
                title.set_text(str(self.now))
                k+=1
            return self.lines
        animate(1)
        self.anim = animation.FuncAnimation(self.fig, animate, 
                               frames=frames, interval=interval, blit=False)
        plt.show(block=True)


class agent:
    def __init__(self,model,id,node:str,speed=1,marker='o',color='r',size=10,alpha=1):
        '''
        node:str
            postion of the agent as a node name lie "i,j"
        id:
            id of the agent
        '''
        self.model=model
        self.id=id
        self.marker=marker
        self.color=color
        self.size=size
        self.speed=speed
        self.pos=eval(node)
        self.node=node
        model.agents.append(self)
        self._id_in_path=0
        self._path=[]
        self.alpha=alpha
        self.active=True

    def set_path(self,path):
        self._path=path
        self._id_in_path=0

    def walk(self):
        '''
        path is the list of nodes that the entity should move on it
        the speed is assumed one node per step
        it is assumed that two consecutive nodes
        in a path are directly connected
        '''
        
        self._id_in_path+=self.speed
        if self._path==[]:
            self.set_path([self.node])
        if self._id_in_path>len(self._path)-1:
            self._id_in_path=len(self._path)-1
        self.node=self._path[int(self._id_in_path)]
        self.pos=eval(self.node)

    def step(self):
        pass

    def neighbor_nodes(self):
        nnodes=self.model.graph.neighbors(self.node)
        l=[]
        for n in nnodes:
            l.append(str(n))
        return l
