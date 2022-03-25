from mesa import Model
from mesa.time import RandomActivation
from zmq import Message
import numpy as np
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.CriterionName import CriterionName
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value

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
        values = {0: Value.VERY_BAD, 1: Value.BAD, 2: Value.AVERAGE, 3: Value.GOOD, 4: Value.VERY_GOOD}
        for item in list_of_items:
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.PRODUCTION_COST,
                                                          values[np.random.randint(0, 5)]))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.CONSUMPTION,
                                                          values[np.random.randint(0, 5)]))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.DURABILITY,
                                                          values[np.random.randint(0, 5)]))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.ENVIRONMENT_IMPACT,
                                                          values[np.random.randint(0, 5)]))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.NOISE,
                                                          values[np.random.randint(0, 5)]))
    
class ArgumentModel(Model):
    """ArgumentModel which inherit from Model"""
    def __init__(self):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
        electric_engine = Item("Electric Engine", "A very quiet engine")
        self.list_of_items = [diesel_engine, electric_engine]
        for i in range(2):
            agent = ArgumentAgent(i, self, "agent_" + str(i))
            agent.generate_preference(self.list_of_items)
            print(agent.get_preference().get_criterion_name_list())
            print(agent.get_preference().most_preferred(self.list_of_items))
            self.schedule.add(agent)
        self.running = True
        
if __name__ == '__main__':
    model = ArgumentModel()