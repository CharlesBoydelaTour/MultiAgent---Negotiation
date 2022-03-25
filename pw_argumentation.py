from mesa import Model
from mesa.time import RandomActivation
from zmq import Message
import numpy as np
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.CriterionName import CriterionName
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionValue import CriterionValue

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
        self.preference = Preferences()
        self.preference.set_criterion_name_list([CriterionName.PRODUCTION_COST, CriterionName.ENVIRONMENT_IMPACT,
                                        CriterionName.CONSUMPTION, CriterionName.DURABILITY,
                                        CriterionName.NOISE])
        for item in list_of_items:
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.PRODUCTION_COST,
                                                          np.random.randint(0, 5)))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.CONSUMPTION,
                                                          np.random.randint(0, 5)))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.DURABILITY,
                                                          np.random.randint(0, 5)))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.ENVIRONMENT_IMPACT,
                                                          np.random.randint(0, 5)))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.NOISE,
                                                          np.random.randint(0, 5)))
    
if __name__ == '__main__':
    """Testing the ArgumentAgent class.
    """
    agent_pref = ArgumentAgent(1, None, "agent")
    agent_pref.generate_preference(["item1", "item2"])
    print(agent_pref.get_preference().get_criterion_name_list())