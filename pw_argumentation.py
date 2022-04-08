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
from communication.mailbox.Mailbox import Mailbox




class ArgumentAgent(CommunicatingAgent):
    """ ArgumentAgent which inherit from CommunicatingAgent."""
    def __init__(self, unique_id, model, name):
        super().__init__(unique_id, model, name)
        self.id = unique_id
        self.name = name
        self.model = model
        #self.list_of_items_object = self.model.list_of_items
        #self.list_of_items = [i.get_name() for i in self.model.list_of_items]
        self.list_of_items = self.model.list_of_items
        print(self.list_of_items)
        self.profile = model.profiles[unique_id]
        self.preference = self.generate_manual_preferences(self.list_of_items, self.profile)
        self.commit_item =[]
        self.not_proposed_items = [i.get_name() for i in self.list_of_items]
        self.str_to_obj = {}
        for i in self.not_proposed_items:
            for object in self.list_of_items:
                if object.get_name() == i:
                    self.str_to_obj[i] = object
        
    def step(self):
        super().step()
        # read mailbox
        list_messages = self.get_new_messages()
        if len(list_messages) == 0:
            item = self.preference.most_preferred([self.str_to_obj[item] for item in self.not_proposed_items])
            self.not_proposed_items.remove(item.get_name())
            #select a random agent to porpose item (not self)
            dest = np.random.choice(self.model.schedule.agents)
            while dest.id == self.id:
                dest = np.random.choice(self.model.schedule.agents)
            print(self.model.schedule.agents)
            item = True, item, ''
            self.send_message(Message(self.get_name(), dest.get_name(), MessagePerformative.PROPOSE, item))
        else:
            for message in list_messages:
                print(message)
                #treat message
                self.treat_message(message)
            
    def treat_message(self, message):
        #extract information from message
        sender = message.get_exp()
        performative = message.get_performative()
        decision, item, argument = message.get_content()
        
        #Respond to propose
        if performative == MessagePerformative.PROPOSE:
            self.not_proposed_items.remove(item.get_name())
            #check if item in 10% top
            if self.preference.is_item_among_top_10_percent(item, self.list_of_items):
                #ACCEPT
                self.send_message(Message(self.get_name(), sender, MessagePerformative.ACCEPT, item))
            else:
                #ASK_WHY
                content = True, item, ''
                self.send_message(Message(self.get_name(), sender, MessagePerformative.ASK_WHY, content))
    
        #Respond to accept
        elif performative == MessagePerformative.ACCEPT:
            #COMMIT
            self.send_message(Message(self.get_name(), sender, MessagePerformative.COMMIT, item))
            self.commit_item.append(item)
            #########Sup item here or in model ??????
        
        #Respond to commit
        elif performative == MessagePerformative.COMMIT:
            if item not in self.commit_item:
                #COMMIT
                self.send_message(Message(self.get_name(), sender, MessagePerformative.COMMIT, item))
                self.commit_item.append(item)
        
        #Respond to ask_why
        elif performative == MessagePerformative.ASK_WHY:
            new_argument = Argument(True, item)
            if len(new_argument.List_supporting_proposal(item, self.preference)) == 0:
                #take out item from list of not proposed items
                new_item = self.preference.most_preferred([self.str_to_obj[item] for item in self.not_proposed_items])
                new_item = True, new_item, ''
                self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))
                self.not_proposed_items.remove(new_item.get_name())
            else:
                arg_why = new_argument.argument_why(item, self.preference) #arg_why = decision, item, argument
                self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, arg_why))
        
        #Respond to argue
        elif performative == MessagePerformative.ARGUE:
            if decision == True:
                #ACCEPT
                new_argument = Argument(False, item)
                if len(new_argument.List_attacking_proposal(item, self.preference)) == 0:
                    #take out item from list of not proposed items
                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ACCEPT, item))
                else:
                    adv_criterion = argument[0].get_criterion()
                    arg_to_arg = new_argument.argument_to_argument(item, self.preference, adv_criterion)
                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, arg_to_arg))
            else: 
                new_argument = Argument(True, item)
                if len(new_argument.List_supporting_proposal(item, self.preference)) == 0:
                    if len(self.not_proposed_items) == 0 :
                        self.send_message(Message(self.get_name(), sender, MessagePerformative.ACCEPT, item))
                    else: 
                        new_item = self.preference.most_preferred([self.str_to_obj[item] for item in self.not_proposed_items])
                        new_item = True, new_item, ''
                        self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))
                        self.not_proposed_items.remove(new_item.get_name())
                else :    
                    adv_criterion = argument[0].get_criterion()
                    arg_to_arg = new_argument.argument_to_argument(item, self.preference, adv_criterion)
                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, arg_to_arg))
                    
    def get_preference(self):
        return self.preference
    
    
    #def generate_random_preference(self, list_of_items):
    #    """give a score for each item for each agent""" 
    #    self.preference = Preferences()
    #    self.preference.set_criterion_name_list([CriterionName.PRODUCTION_COST, CriterionName.ENVIRONMENT_IMPACT,
    #                                    CriterionName.CONSUMPTION, CriterionName.DURABILITY,
    #                                    CriterionName.NOISE])
    #    values = {0: Value.VERY_BAD, 1: Value.BAD, 2: Value.AVERAGE, 3: Value.GOOD, 4: Value.VERY_GOOD}
    #    for item in list_of_items:
    #        self.preference.add_criterion_value(CriterionValue(item, CriterionName.PRODUCTION_COST,
    #                                                      values[np.random.randint(0, 5)]))
    #        print(values[np.random.randint(0, 5)])                                              
    #        self.preference.add_criterion_value(CriterionValue(item, CriterionName.CONSUMPTION,
    #                                                      values[np.random.randint(0, 5)]))
    #        self.preference.add_criterion_value(CriterionValue(item, CriterionName.DURABILITY,
    #                                                      values[np.random.randint(0, 5)]))
    #        self.preference.add_criterion_value(CriterionValue(item, CriterionName.ENVIRONMENT_IMPACT,
    #                                                      values[np.random.randint(0, 5)]))
    #        self.preference.add_criterion_value(CriterionValue(item, CriterionName.NOISE,
    #                                                      values[np.random.randint(0, 5)]))

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
        self.running = True
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
            
    def step(self):
        """step of the model"""
        self.__messages_service.dispatch_messages()
        self.schedule.step()
            
    def __str__(self, arg):
        
        decision, item, argument = arg
        if decision:
            str = f"{item.get_name()}\t<=\t"
        else:
            str = f"not {item.get_name()} \t<=\t"
        for element in argument:
            str += element.__str__() + ',  '
        return str
            


if __name__ == "__main__":
    model = ArgumentModel()
    for i in range(5):
        model.step()