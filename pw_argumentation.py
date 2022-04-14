from mesa import Model
from mesa.time import RandomActivation, BaseScheduler
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
from communication.arguments.CoupleValue import CoupleValue




class ArgumentAgent(CommunicatingAgent):
    """ ArgumentAgent which inherit from CommunicatingAgent."""
    def __init__(self, unique_id, model, name, start):
        super().__init__(unique_id, model, name)
        self.id = unique_id
        self.name = name
        self.model = model
        #self.list_of_items_object = self.model.list_of_items
        #self.list_of_items = [i.get_name() for i in self.model.list_of_items]
        self.list_of_items = self.model.list_of_items
        print(self.list_of_items)
        self.profile = model.profiles[unique_id]
        #self.preference = self.generate_manual_preferences(self.list_of_items, self.profile)
        self.preference = self.generate_random_preference(self.list_of_items)
        self.commit_item =[]
        self.not_proposed_items = [i.get_name() for i in self.list_of_items]
        self.proposed_items = []
        self.used_arguments = []
        self.str_to_obj = {}
        for i in self.not_proposed_items:
            for object in self.list_of_items:
                if object.get_name() == i:
                    self.str_to_obj[i] = object
        self.start = start
        
    def step(self):
        super().step()
        # read mailbox
        list_messages = self.get_new_messages()
        
        if self.start == True:
            item = self.preference.most_preferred([self.str_to_obj[item] for item in self.not_proposed_items])
            self.not_proposed_items.remove(item.get_name())
            #select a random agent to porpose item (not self)
            dest = np.random.choice(self.model.schedule.agents)
            while dest.id == self.id:
                dest = np.random.choice(self.model.schedule.agents)
            #print(self.model.schedule.agents)
            item = True, item, ''
            self.send_message(Message(self.get_name(), dest.get_name(), MessagePerformative.PROPOSE, item))
            self.start = False
        else:
            #print(len(list_messages))
            for message in list_messages:
                print(message)
                #treat message
                self.treat_message(message)
        

    """
    def select_argument(self, arguments, used_arguments):

        result_to_use = None
        for argument in arguments:
            cr1, val1, cr2 = self.get_argument(argument)            
            if not( (cr1, val1, cr2) in used_arguments):
                result_to_use = argument
                break
        return result_to_use
    """

    
    def select_argument(self,item, arguments, used_arguments):
        argument_to_use = None
        for argument in arguments:
            cr1 = self.get_argument(argument)            
            if not( (item,cr1) in used_arguments):
                argument_to_use = argument
                break
        return argument_to_use


    def get_argument(self, arg):
        cr1 = arg[0].get_criterion().name
        val1 = arg[0].get_value()
        return cr1, 
                 
            
    def treat_message(self, message):
        #extract information from message
        sender = message.get_exp()
        performative = message.get_performative()
        decision, item, argument = message.get_content()
        
    
        #Respond to propose
        if performative == MessagePerformative.PROPOSE:
            self.not_proposed_items.remove(item.get_name())
            self.proposed_items.append(item.get_name())
            #check if item in 10% top
            if self.preference.is_item_among_top_10_percent(item, self.list_of_items):
                #ACCEPT
                content = True, item, ''
                self.send_message(Message(self.get_name(), sender, MessagePerformative.ACCEPT, content))
            else:
                #ASK_WHY
                content = True, item, ''
                self.send_message(Message(self.get_name(), sender, MessagePerformative.ASK_WHY, content))
    
        #Respond to accept
        elif performative == MessagePerformative.ACCEPT:
            #COMMIT
            content = True, item, ''
            self.send_message(Message(self.get_name(), sender, MessagePerformative.COMMIT, content))
            self.commit_item.append(item)
        
        #Respond to commit
        elif performative == MessagePerformative.COMMIT:
            if item not in self.commit_item:
                #COMMIT
                content = True, item, ''
                self.send_message(Message(self.get_name(), sender, MessagePerformative.COMMIT, content))
                self.commit_item.append(item)
            
        
        #Respond to ask_why
        elif performative == MessagePerformative.ASK_WHY:
            new_argument = Argument(True, item)
            if len(new_argument.List_supporting_proposal(item, self.preference)) == 0:
                #take out item from list of not proposed items
                new_item = self.preference.most_preferred([self.str_to_obj[item] for item in self.not_proposed_items])
                self.not_proposed_items.remove(new_item.get_name())
                new_item = True, new_item, ''
                self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))
            else:
                decision, item, args = new_argument.argument_why(item, self.preference) #arg_why = decision, item, argument
                
                arg = self.select_argument(item, args, self.used_arguments)

                if arg != None:
                    self.used_arguments.append((item, self.get_argument(arg)) )
                    arg_why = decision, item, arg
                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, arg_why))
                else:
                        content = True, item, ''
                        self.send_message(Message(self.get_name(), sender, MessagePerformative.ACCEPT, content))
        
        #Respond to argue
        elif performative == MessagePerformative.ARGUE:
            if decision == True:

                
                new_argument = Argument(False, item)
                if len(new_argument.List_attacking_proposal(item, self.preference)) == 0:
                    #take out item from list of not proposed items
                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ACCEPT, item))
                else:
                    

                    adv_criterion = argument[0].get_criterion()
                    
                    
                    if len(argument) == 1:
                        adv_value = argument[0].get_value()
                        
                        

                        
                        my_value = self.preference.get_value(item, adv_criterion)
                        
                        passer = False

                        for my_item in self.list_of_items:
                            if my_item != item:
                                value_my_item = self.preference.get_value(item, adv_criterion)
                                if value_my_item.value > adv_value.value:
                                    
                                    my_argument = [CoupleValue(adv_criterion, value_my_item), str(value_my_item.name) + ' is better than ' + str(adv_value.name)]
                                    my_message = True, my_item, my_argument
                                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, my_message))
                                    

                                    passer = True

                                    break
                        
                        if not passer and my_value.value <= 2:
                                my_argument = [CoupleValue(adv_criterion, my_value), str(my_value.name) + ' is worst than ' + str(adv_value.name)]
                                my_message = False, item, my_argument
                                self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, my_message))
                                

                                passer = True

                        if not passer:

                            decision, item, args = new_argument.argument_to_argument(item, self.preference, adv_criterion)
                            
                            arg = self.select_argument(item, args, self.used_arguments)

                            if arg != None:
                                self.used_arguments.append((item, self.get_argument(arg)) )

                                arg_to_arg = decision, item, arg
                                self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, arg_to_arg))
                            else:
                                content = True, item, ''
                                self.send_message(Message(self.get_name(), sender, MessagePerformative.ACCEPT, content))


                    elif len(argument) == 2:
                        
                        adv_value = argument[0].get_value()   

                        passer = False

                        for my_item in self.list_of_items:
                            if my_item != item:
                                value_my_item = self.preference.get_value(item, adv_criterion)
                                if value_my_item.value > adv_value.value:
                                    
                                    my_argument = [CoupleValue(adv_criterion, value_my_item), str(value_my_item.name) + ' is better than ' + str(adv_value.name)]
                                    my_message = True, my_item, my_argument
                                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, my_message))

                                    passer = True

                                    break

                        if not passer:

                            



                            decision, item, args = new_argument.argument_to_argument(item, self.preference, adv_criterion)
                            arg = self.select_argument(item, args, self.used_arguments)

                            if arg != None:
                                self.used_arguments.append((item, self.get_argument(arg)) )
                                
                                arg_to_arg = decision, item, arg
                                self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, arg_to_arg))
                            
                            else:
                                content = True, item, ''
                                self.send_message(Message(self.get_name(), sender, MessagePerformative.ACCEPT, content))


                                     


            else: 
                new_argument = Argument(True, item)
                
                if len(new_argument.List_supporting_proposal(item, self.preference)) == 0:
                    if len(self.not_proposed_items) == 0 :
                        #take an item proposed by the other agent
                        new_item = self.preference.most_preferred([self.str_to_obj[item] for item in self.proposed_items])
                        self.not_proposed_items.remove(new_item.get_name())
                        new_item = True, new_item, ''
                        self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))
                    else: 
                        #take an item not already proposed
                        new_item = self.preference.most_preferred([self.str_to_obj[item] for item in self.not_proposed_items])
                        self.not_proposed_items.remove(new_item.get_name())
                        new_item = True, new_item, ''
                        self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))
                else :    
                    adv_criterion = argument[0].get_criterion()

                    decision, item, args = new_argument.argument_to_argument(item, self.preference, adv_criterion)
                    print(args)
                    arg = self.select_argument(item, args, self.used_arguments)
                    print(arg)
                    if arg != None:
                        self.used_arguments.append((item, self.get_argument(arg)) )
                    
                        arg_to_arg = decision, item, arg

                        self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, arg_to_arg))

                    else:
                        if len(self.not_proposed_items) == 0 :
                            #take an item proposed by the other agent
                            new_item = self.preference.most_preferred([self.str_to_obj[item] for item in self.proposed_items])
                            self.not_proposed_items.remove(new_item.get_name())
                            new_item = True, new_item, ''
                            self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))
                        else: 
                            #take an item not already proposed
                            new_item = self.preference.most_preferred([self.str_to_obj[item] for item in self.not_proposed_items])
                            self.not_proposed_items.remove(new_item.get_name())
                            new_item = True, new_item, ''
                            self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))
                    



    def get_preference(self):
        return self.preference
    
    
    def generate_random_preference(self, list_of_items):
        """give a score for each item for each agent""" 
        preference = Preferences()
        preference.set_criterion_name_list([CriterionName.PRODUCTION_COST, CriterionName.ENVIRONMENT_IMPACT,
                                       CriterionName.CONSUMPTION, CriterionName.DURABILITY,
                                       CriterionName.NOISE])
        values = {0: Value.VERY_BAD, 1: Value.BAD, 2: Value.AVERAGE, 3: Value.GOOD, 4: Value.VERY_GOOD}
        for item in list_of_items:
           preference.add_criterion_value(CriterionValue(item, CriterionName.PRODUCTION_COST,
                                                         values[np.random.randint(0, 5)]))                                             
           preference.add_criterion_value(CriterionValue(item, CriterionName.CONSUMPTION,
                                                         values[np.random.randint(0, 5)]))
           preference.add_criterion_value(CriterionValue(item, CriterionName.DURABILITY,
                                                         values[np.random.randint(0, 5)]))
           preference.add_criterion_value(CriterionValue(item, CriterionName.ENVIRONMENT_IMPACT,
                                                         values[np.random.randint(0, 5)]))
           preference.add_criterion_value(CriterionValue(item, CriterionName.NOISE,
                                                         values[np.random.randint(0, 5)]))
        return preference

    def generate_manual_preferences(self, list_of_items, profiles ):
        # To be completed
        """give a score for each item for each agent""" 
        preference = Preferences()

        values = {1: Value.VERY_BAD, 2: Value.BAD, 3: Value.GOOD, 4: Value.VERY_GOOD}
        criterions = {0: CriterionName.PRODUCTION_COST, 1: CriterionName.CONSUMPTION, 
                      2: CriterionName.DURABILITY, 3: CriterionName.ENVIRONMENT_IMPACT,
                      4: CriterionName.NOISE}

        criterion_name_list = []
        for i in profiles[0]:
            criterion_name_list.append(criterions[i])
        
        preference.set_criterion_name_list(criterion_name_list)
        
        for item in list_of_items:

            if str(item) == "Diesel Engine (A super cool diesel engine)":
                profile = profiles[1]
            elif str(item) == "Electric Engine (A very quiet engine)":
                profile = profiles[2]
            
            preference.add_criterion_value(CriterionValue(item, CriterionName.PRODUCTION_COST,
                                                      values[profile[0]]))
            preference.add_criterion_value(CriterionValue(item, CriterionName.CONSUMPTION,
                                                      values[profile[1]]))
            preference.add_criterion_value(CriterionValue(item, CriterionName.DURABILITY,
                                                      values[profile[2]]))
            preference.add_criterion_value(CriterionValue(item, CriterionName.ENVIRONMENT_IMPACT,
                                                      values[profile[3]]))
            preference.add_criterion_value(CriterionValue(item, CriterionName.NOISE,
                                                          values[profile[4]]))
            return preference
        


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model"""
    def __init__(self):
        super().__init__()
        self.schedule = BaseScheduler(self)
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
            if i % 2 == 0 :
                agent = ArgumentAgent(i, self, agent_name, True)
            else:
                agent = ArgumentAgent(i, self, agent_name, False)
            # print(agent_name)
            
            # print(80*'=')
            # agent.generate_random_preference(self.list_of_items)
            # #agent.generate_manual_preferences(self.list_of_items, self.profiles[i])
            
            # print(f'order of preferences for {agent_name} : \n', agent.get_preference().get_criterion_name_list())

            # print(20*'-')

            # print(f"The prefered item for {agent_name} is: " , agent.get_preference().most_preferred(self.list_of_items).get_name())
            # print(20*'=')
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
    for i in range(10):
        model.step()
