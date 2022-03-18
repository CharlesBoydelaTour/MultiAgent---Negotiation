from mesa import Model
from mesa.time import RandomActivation
from zmq import Message
import numpy as np
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService

class ArgumentAgent(CommunicatingAgent):
    """ ArgumentAgent which inherit from CommunicatingAgent."""
    def __init__(self, unique_id, model, name):
        super().__init__(unique_id, model, name)
        self.preference = None
    
    def step(self):
        super.step()
    
    def get_preference(self):
        return self.preference
    
    def generate_preference(self, list_of_items):
        """give a score for each item for each agent""" 
        
        for item in list_of_items:
            for criter in range(5):
                value = np.random.choice()