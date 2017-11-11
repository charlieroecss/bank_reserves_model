#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 15:35:58 2017

@author: charlie roe
"""

"""
Citation:
The following code was adapted from server.py at
https://github.com/projectmesa/mesa/blob/master/examples/wolf_sheep/wolf_sheep/server.py
Accessed on: November 2, 2017
Author of original code: Taylor Mutch
"""

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from bank_reserves.agents import Person
from bank_reserves.model import BankReservesModel


RICH_COLOR = "46FF33" #Green
POOR_COLOR = "FF3C33" #Red
MID_COLOR = "3349FF" #Blue

def person_portrayal(agent):
    if agent is None:
        return

    portrayal = {}
    
    #update portrayal characteristics for each Person object
    if isinstance(agent, Person):
        portrayal["Shape"] = "circle"
        portrayal["r"] = .5 #radius
        portrayal["Layer"] = 0 #only need one layer
        portrayal["Filled"] = "true" #instead of empty shape
        
        color = MID_COLOR #start agents off as blue
        
        #check agent savings
        if agent.savings > agent.model.rich_threshold:
            color = RICH_COLOR #color rich agents green
        if  agent.savings < 10 and agent.loans < 10:
            color = MID_COLOR #color middle class agents blue
        if agent.loans > 10:
            color = POOR_COLOR #color poor agents red
        
        portrayal["Color"] = color #set the portrayal color for each agent
        

    return portrayal

#dictionary of user settable parameters - these map to the model __init__ parameters
model_params = {"init_people":UserSettableParameter("slider", "People", 25, 1, 200,
                                                    description="Initial Number of People"),
                "rich_threshold":UserSettableParameter("slider", "Rich Threshold", 10, 1, 20,
                                                   description="Upper End of Random Initial Wallet Amount"),
                "reserve_percent":UserSettableParameter("slider", "Reserves", 50, 1, 100,
                                                    description="Percent of deposits the bank has to hold in reserve")
                }

#set the portrayal function and size of the canvas for visualization
canvas_element = CanvasGrid(person_portrayal, 20, 20, 500, 500)

#map data to chart in the ChartModule
chart_element = ChartModule([{"Label":"Rich", "Color":RICH_COLOR},
                             {"Label":"Poor", "Color":POOR_COLOR},
                             {"Label":"Middle Class", "Color":MID_COLOR}])

#create instance of Mesa ModularServer
server = ModularServer(BankReservesModel, [canvas_element, chart_element],
                       "Bank Reserves Model",
                       model_params=model_params
                       )
