# CoDiSS
Contagious Disease Spread Simulator

This Python module provides a tool to simulate the spread of confection disease in buildings using an agent-based simulation approach. The simulation considers the emission of virus quanta by infected 
agents and calculates the quanta inhaled by healthy agents. Based on stochastic calculations, the simulation predicts probable new infections, makes agents infected by chance and continues the simulation based on the agents' new status.

The CoDiss module consists of two main classes: Model and Agent. 
Both classes inherit from the ABS.py (Agent-Based Simulation); this file is taken from the github repository: 
	https://github.com/Project-AgentBuilt/AgentBuilt

 1) The Model class is responsible for setting up the simulation environment,  including defining the parameters and initial conditions of the simulation. 

 2) The Agent class represents individual agents in the simulation, each with its properties and behaviors. 

The simulation can be run for a desired period, which is specified using the datetime Python module. During this time, the spread of COVID-19 is tracked and visualized using the ABS module. 
The time step for the simulation is adjustable, allowing for a balance between the speed and accuracy of the model. For COVID-19 spread, a time-step equal to 1 minute (60 seconds) is recommended to capture the spread dynamics accurately. This module provides a powerful tool for understanding the dynamics of COVID-19 spread and designing effective intervention strategies to control the spread of contagious diseases in buildings. 
