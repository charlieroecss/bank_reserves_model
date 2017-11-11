"""
This version of the model has a BatchRunner at the bottom. This
is for collecting data on parameter sweeps. It is not meant to
be run with run.py, since run.py starts up a server for visualization, which
isn't necessary for the BatchRunner. To run a parameter sweep, call
batch_run.py in the command line.

The BatchRunner is set up to collect step by step data of the model. It does
this by collecting the DataCollector object in a model_reporter (i.e. the
DataCollector is collecting itself every step).

The end result of the batch run will be a csv file created in the same
directory from which Python was run. The csv file will contain the data from 
every step of every run.
"""

from bank_reserves.agents import Bank, Person
from mesa import Model
from mesa.batchrunner import BatchRunner
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
import numpy as np
import pandas as pd
import random

#for a Mesa DataCollector
def get_num_rich_agents(model):
    #list of rich agents
    rich_agents = [a for a in model.schedule.agents if a.savings > model.rich_threshold]
    #return number of rich agents
    return len(rich_agents)

#for a Mesa DataCollector
def get_num_poor_agents(model):
    #list of poor agents
    poor_agents = [a for a in model.schedule.agents if a.loans > 10]
    #return number of poor agents
    return len(poor_agents)

#for a Mesa DataCollector
def get_num_mid_agents(model):
    #list of middle class agents
    mid_agents = [a for a in model.schedule.agents if 
                  a.loans < 10 and a.savings < model.rich_threshold]
    #return number of middle class agents
    return len(mid_agents)

#for a Mesa DataCollector
def get_total_savings(model):
    #list of amounts of all agents' savings
    agent_savings = [a.savings for a in model.schedule.agents]
    #return the sum of agents' savings
    return np.sum(agent_savings)

#for a Mesa DataCollector
def get_total_wallets(model):
    #list of amounts of all agents' wallets 
    agent_wallets = [a.wallet for a in model.schedule.agents]
    #return the sum of all agents' wallets
    return np.sum(agent_wallets)

#for a Mesa DataCollector
def get_total_money(model):
    #sum of all agents' wallets
    wallet_money = get_total_wallets(model)
    #sum of all agents' savings
    savings_money = get_total_savings(model)
    #return sum of agents' wallets and savings for total money
    return wallet_money + savings_money

#for a Mesa DataCollector
def get_total_loans(model):
    #list of amounts of all agents' loans
    agent_loans = [a.loans for a in model.schedule.agents]
    #return sum of all agents' loans
    return np.sum(agent_loans)

"""
This is used in the DataCollector model_reporters to collect the
DataCollector itself for parameter sweeps. The result will be a DataCollector
object.
"""
def batch_run_data(model):
    return model.datacollector

class BankReservesModel(Model):
    
    grid_h = 20 #grid height
    grid_w = 20 #grid width
    
    """init parameters "init_people", "rich_threshold", and "reserve_percent"
       are all UserSettableParameters"""
    def __init__(self, height=grid_h, width=grid_w, init_people=2, rich_threshold=10,
                 reserve_percent=50,):
        self.height = height
        self.width = width
        self.init_people = init_people
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus=True)
        #rich_threshold is the amount of savings a person needs to be considered "rich"
        self.rich_threshold = rich_threshold
        self.reserve_percent = reserve_percent
        #see datacollector functions above
        self.datacollector = DataCollector(
                model_reporters={"Rich":get_num_rich_agents,
                                 "Poor":get_num_poor_agents,
                                 "Middle Class":get_num_mid_agents,
                                 "Savings":get_total_savings,
                                 "Wallets":get_total_wallets,
                                 "Money":get_total_money,
                                 "Loans":get_total_loans,
                                 "Batch":batch_run_data},
                agent_reporters={"Wealth":lambda x: x.wealth})
        
        #create a single bank for the model
        self.bank = Bank(1, self, self.reserve_percent)
        
        
        #create people for the model according to number of people set by user
        for i in range(self.init_people):
            #set x coordinate as a random number within the width of the grid
            x = random.randrange(self.width)
            #set y coordinate as a random number within the height of the grid
            y = random.randrange(self.height)
            p = Person(i, (x, y) , self, True, self.bank, self.rich_threshold)
            #place the Person object on the grid at coordinates (x, y)
            self.grid.place_agent(p, (x, y))
            #add the Person object to the model schedule
            self.schedule.add(p)
            
        self.running = True
    
    def step(self):
        #collect data
        self.datacollector.collect(self)
        #tell all the agents in the model to run their step function
        self.schedule.step()
        
    def run_model(self):
        for i in range(self.run_time):
            self.step()


br_params = {"init_people":[25, 100, 150, 200],
             "rich_threshold":[5, 10, 15, 20],
             "reserve_percent":[0, 50, 100]}

bank_reserves_batch_runner = BatchRunner(BankReservesModel, br_params,
                                         iterations=1, max_steps=1000,
                                         model_reporters={"Batch":batch_run_data})

if __name__ == '__main__':
    bank_reserves_batch_runner.run_all()
    run_data = bank_reserves_batch_runner.get_model_vars_dataframe()
    batch_data_collector_objects = run_data["Batch"]
    step_data = pd.DataFrame()
    for i in range(len(batch_data_collector_objects)):
        if isinstance(batch_data_collector_objects.iloc[i], DataCollector):
            dco = batch_data_collector_objects.iloc[i]
            dco_df = dco.get_model_vars_dataframe()
            step_data = step_data.append(dco_df, ignore_index=True)
    step_data.to_csv("BankReservesModel_Step_Data.csv")
    
