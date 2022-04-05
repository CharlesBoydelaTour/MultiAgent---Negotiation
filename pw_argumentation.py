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
from communication.arguments.Argument import Argument




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
            print(values[np.random.randint(0, 5)])                                              
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.CONSUMPTION,
                                                          values[np.random.randint(0, 5)]))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.DURABILITY,
                                                          values[np.random.randint(0, 5)]))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.ENVIRONMENT_IMPACT,
                                                          values[np.random.randint(0, 5)]))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.NOISE,
                                                          values[np.random.randint(0, 5)]))

    def generate_manual_preferences(self, list_of_items, profiles ):
        # To be completed
        """give a score for each item for each agent""" 
        self.preference = Preferences()

        values = {1: Value.VERY_BAD, 2: Value.BAD, 3: Value.GOOD, 4: Value.VERY_GOOD}
        criterions = {0: CriterionName.PRODUCTION_COST, 1: CriterionName.CONSUMPTION, 
                      2: CriterionName.DURABILITY, 3: CriterionName.ENVIRONMENT_IMPACT,
                      4: CriterionName.NOISE}

        criterion_name_list = []
        for i in profiles[0]:
            criterion_name_list.append(criterions[i])
        
        self.preference.set_criterion_name_list(criterion_name_list)
        
        for item in list_of_items:

            if str(item) == "Diesel Engine (A super cool diesel engine)":
                profile = profiles[1]
            elif str(item) == "Electric Engine (A very quiet engine)":
                profile = profiles[2]
            
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.PRODUCTION_COST,
                                                      values[profile[0]]))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.CONSUMPTION,
                                                      values[profile[1]]))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.DURABILITY,
                                                      values[profile[2]]))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.ENVIRONMENT_IMPACT,
                                                      values[profile[3]]))
            self.preference.add_criterion_value(CriterionValue(item, CriterionName.NOISE,
                                                          values[profile[4]]))
        


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model"""
    def __init__(self):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
        electric_engine = Item("Electric Engine", "A very quiet engine")

        self.profiles = [[[0,3,1,2,4],[4, 3, 4, 1, 2],[2, 1, 3, 4, 4]],
                            [[3,4,0,1,2],[3, 2, 3, 1, 1],[3, 2, 2, 4, 4]]]

        self.list_of_items = [diesel_engine, electric_engine]
        self.list_of_agents = []
        for i in range(2):
            print(80*'=')
            agent_name = "agent_" + str(i)
            agent = ArgumentAgent(i, self, agent_name )
            print(agent_name)
            
            print(80*'=')
            agent.generate_manual_preferences(self.list_of_items, self.profiles[i])
            
            print(f'order of preferences for {agent_name} : \n', agent.get_preference().get_criterion_name_list())

            print(20*'-')
            #print(agent.get_preference().most_preferred(self.list_of_items))
            #print(20*'-')
            print(f"The prefered item for {agent_name} is: " , agent.get_preference().most_preferred(self.list_of_items).get_name())
            print(20*'=')
            self.schedule.add(agent)
            self.list_of_agents.append(agent)
        self.running = True

        #implement situation where A1 propose item and A2 accept item if in top 10% otherwaise ask why
        def generate_message(i, message):
                    self.__messages_service.send_message(message)
                    print(f'Message {i}', message)
                    print(15*' ' + 15*'-' )


        proposed_item = self.list_of_items[0]

        
        #for i in range(2):
        #    agent_name = "agent_" + str(i)
        #    agent = ArgumentAgent(i, self, agent_name )


        msg_1 = Message("agent_0", "agent_1", MessagePerformative.PROPOSE ,proposed_item)
        generate_message(1, msg_1)

        if self.list_of_agents[1].get_preference().is_item_among_top_10_percent(proposed_item, self.list_of_items):

            msg_2 = Message("agent_1", "agent_0", MessagePerformative.ACCEPT ,proposed_item.get_name())
            generate_message(2, msg_2)

            msg_3 = Message("agent_0", "agent_1", MessagePerformative.COMMIT ,proposed_item.get_name())
            generate_message(3, msg_3)

            msg_4 = Message("agent_1", "agent_0", MessagePerformative.COMMIT ,proposed_item.get_name())
            generate_message(4, msg_4)


        else:   
            msg_2 = Message("agent_1", "agent_0", MessagePerformative.ASK_WHY ,proposed_item.get_name())
            generate_message(2, msg_2)

            ARG = Argument(True, proposed_item)
            arg = ARG.argument(proposed_item, self.list_of_agents[0].get_preference())

            msg_3 = Message("agent_0", "agent_1", MessagePerformative.ARGUE ,arg)
            generate_message(3, msg_3)



if __name__ == "__main__":
    model = ArgumentModel()



