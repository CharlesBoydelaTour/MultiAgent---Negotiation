from mesa import Model
from mesa.time import RandomActivation
import numpy as np
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.CriterionName import CriterionName
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
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
        self.list_of_agents = []
        for i in range(2):
            agent = ArgumentAgent(i, self, "agent_" + str(i))
            agent.generate_preference(self.list_of_items)
            #print(agent.get_preference().get_criterion_name_list())
            print("The prefered item for agent_" + str(i) + " is " + agent.get_preference().most_preferred(self.list_of_items).get_name())
            self.schedule.add(agent)
            self.list_of_agents.append(agent)
        self.running = True

        #implement situation where A1 propose item and A2 accept item if in top 10% otherwaise ask why
        self.__messages_service.send_message(Message("agent_0", "agent_1", MessagePerformative.PROPOSE ,self.list_of_items[0]))
        if self.list_of_agents[1].get_preference().is_item_among_top_10_percent(self.list_of_items[0], self.list_of_items):
            self.__messages_service.send_message(Message("agent_1", "agent_0", MessagePerformative.ACCEPT ,self.list_of_items[0]))
            self.__messages_service.send_message(Message("agent_0", "agent_1", MessagePerformative.COMMIT ,self.list_of_items[0]))
            self.__messages_service.send_message(Message("agent_1", "agent_0", MessagePerformative.COMMIT ,self.list_of_items[0]))
        else:   
            self.__messages_service.send_message(Message("agent_1", "agent_0", MessagePerformative.ASK_WHY ,self.list_of_items[0]))
            self.__messages_service.send_message(Message("agent_0", "agent_1", MessagePerformative.ARGUE ,self.list_of_items[0]))

if __name__  == "__main__":
    model = ArgumentModel()