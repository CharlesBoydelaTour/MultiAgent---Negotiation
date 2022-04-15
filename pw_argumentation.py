from mesa import Model
from mesa.time import RandomActivation, BaseScheduler
import numpy as np
#from sqlalchemy import true
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
import random



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
        self.profile = model.profiles[unique_id]
        self.preference = self.generate_manual_preferences(self.list_of_items, self.profile)
        #self.preference = self.generate_random_preference(self.list_of_items)
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
        self.end_status = False
        
    def step(self):
        super().step()
        # read mailbox
        list_messages = self.get_new_messages()
        
        if self.start == True:

            item = self.preference.most_preferred([self.str_to_obj[item] for item in self.not_proposed_items])
            self.not_proposed_items.remove(item.get_name())
            #select a random agent to porpose item (not self)
            dest_id = self.id+1
            dest = self.model.schedule.agents[dest_id]

            item = True, item, ''
            self.send_message(Message(self.get_name(), dest.get_name(), MessagePerformative.PROPOSE, item))
            self.start = False
        else:
            if len(list_messages)==0:
                 self.end_status=True
            elif len(list_messages)==1:
                print(list_messages[0])
                self.treat_message(list_messages[0])
            elif len(list_messages)==2:
             ####################################quelques ameliorations###################   
                for message in list_messages:
                    performative = message.get_performative()
                    if performative == MessagePerformative.PROPOSE:
                        print(message)
                        decision, item, argument = message.get_content()
                        self.not_proposed_items.remove(item.get_name())
                        self.proposed_items.append(item.get_name())
                        
                    elif performative == MessagePerformative.ARGUE:
                        print(message)
                        #treat message
                        self.treat_message(message)
              ###############################################################################

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
                
                ############################################################################################################
                ### Je pense ici, arg sera toujours différent de None. En fait, il vient de proposer cet item,
                ### donc la liste des used argument pour cet item est toujours vide
                ### Donc on peut éliminer le else en bas
                ############################################################################################################

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
                    ##################################################################
                    content = True, item, ''  # j'ai ajoute ca
                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ACCEPT, content)) # j'ai corrige content ai lieu item
                    ###################################################################
                
                else:
                    adv_criterion = argument[0].get_criterion()
                    
                    
                    if len(argument) == 1: # This is the case when we receive a response to Ask_why
                        adv_value = argument[0].get_value()
                        
                        #Calculate my evaluation for the item in this criterion
                        my_value = self.preference.get_value(item, adv_criterion)
                        
                        passer = False
                        
                        #Check if I have a better item in this criterion
                        not_proposed_object = [self.str_to_obj[item] for item in self.not_proposed_items]
                        for my_item in not_proposed_object:
                            if my_item != item:
                                value_my_item = self.preference.get_value(my_item, adv_criterion)
                                if value_my_item.value > adv_value.value:

                                    self.not_proposed_items.remove(my_item.get_name()) ########################################
                                    new_item = True, my_item, ''
                                    self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))
                                    my_argument = [CoupleValue(adv_criterion, value_my_item)]
                                    my_message = True, my_item, my_argument
                                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, my_message))

                                    

                ############################################################################################################
                ### La, j'ai un item qui est meilleur pour ce critère. en algo sur pdf, il faut répondre par argue avec 
                ### ce new item.
                ### Ce que je propose, c'est d'envoyer deux messages: Propose(new_item) et puis un argument justificatif
                ### l'argument justificatif sera sous la forme d'une réponse à ask_why : argue item criterion = value
                ### dans ce cas on assure que les deux agents peuvent proposer
                ### pk envoyer 2 messages et non pas un seul: si on envoie juste propose, l'autre demande why, et on risque de
                ### lui répondre par un autre critère (dans ce cas on perd l'acheminement logique
                                    """
                                    my_argument = [CoupleValue(adv_criterion, value_my_item), str(value_my_item.name) + ' is better than ' + str(adv_value.name)]
                                    my_message = True, my_item, my_argument
                                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, my_message))
                                    """
                ### ATTENTION: je pense que dans ce cas pour que l'autre ne fait pas un ask_why, on modifie dans la condition
                ### de lecture de messages.  Si len(new_messages) == 2: on check le type  puis on print le propose, puis print 
                ### le 2eme message qui est arg et  le traiter
               
                ############################################################################################################                                    
                                    

                                    passer = True

                                    break
                        
                        if not passer and my_value.value <= 2:
                                #my_argument = [CoupleValue(adv_criterion, my_value), str(my_value.name) + ' is worst than ' + str(adv_value.name)]
                                my_argument = [CoupleValue(adv_criterion, my_value)]
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

                        not_proposed_object = [self.str_to_obj[item] for item in self.not_proposed_items]
                        for my_item in not_proposed_object:
                            if my_item != item:
                                value_my_item = self.preference.get_value(my_item, adv_criterion)
                                if value_my_item.value > adv_value.value:
                                    self.not_proposed_items.remove(my_item.get_name()) #####################################
                                    new_item = True, my_item, ''
                                    self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))
                                    my_argument = [CoupleValue(adv_criterion, value_my_item)]
                                    my_message = True, my_item, my_argument
                                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, my_message))
                                    
                                    
                                    
                ############################################################################################################
                ### La, j'ai un item qui est meilleur pour ce critère. en algo sur pdf, il faut répondre par argue avec 
                ### ce new item.
                ### Ce que je propose, c'est d'envoyer deux messages: Propose(new_item) et puis un argument justificatif
                ### l'argument justificatif sera sous la forme d'une réponse à ask_why : argue item criterion = value
                ### dans ce cas on assure que les deux agents peuvent proposer
                ### pk envoyer 2 messages et non pas un seul: si on envoie juste propose, l'autre demande why, et on risque de
                ### lui répondre par un autre critère (dans ce cas on perd l'acheminement logique
                                    """
                                    
                                    
                                    my_argument = [CoupleValue(adv_criterion, value_my_item), str(value_my_item.name) + ' is better than ' + str(adv_value.name)]
                                    my_message = True, my_item, my_argument
                                    self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, my_message))
                                    """
                ### ATTENTION: je pense que dans ce cas pour que l'autre ne fait pas un ask_why, on modifie dans la condition
                ### de lecture de messages.  Si len(new_messages) == 2: on check le type  puis on print le propose, puis print 
                ### le 2eme message qui est arg et  le traiter
               
                ############################################################################################################    
                
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
                        ####################################################################################################
                        ### Je pense là, on doit plutôt accepter le new_item parce qu'il a été déjà proposé par l'adversaire.
                        ### Plutôt que de le reproposer
                        """
                        self.not_proposed_items.remove(new_item.get_name())
                        new_item = True, new_item, ''
                        self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))

                        """
                        #####################################################################################################
                        
                        content = True, new_item, ''
                        self.send_message(Message(self.get_name(), sender, MessagePerformative.ACCEPT, content))
                        
                    else: 
                        #take an item not already proposed
                        new_item = self.preference.most_preferred([self.str_to_obj[item] for item in self.not_proposed_items])
                        self.not_proposed_items.remove(new_item.get_name())
                        new_item = True, new_item, ''
                        self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))
                else :    
                    adv_criterion = argument[0].get_criterion()

                    decision, item, args = new_argument.argument_to_argument(item, self.preference, adv_criterion)
                    arg = self.select_argument(item, args, self.used_arguments)
                    if arg != None:
                        self.used_arguments.append((item, self.get_argument(arg)) )
                    
                        arg_to_arg = decision, item, arg

                        self.send_message(Message(self.get_name(), sender, MessagePerformative.ARGUE, arg_to_arg))

                    else:
                        if len(self.not_proposed_items) == 0 :
                            #take an item proposed by the other agent
                            new_item = self.preference.most_preferred([self.str_to_obj[item] for item in self.proposed_items])
                            
                            ####################################################################################################
                            ### Je pense là, on doit plutôt accepter le new_item parce qu'il a été déjà proposé par l'adversaire.
                            ### Plutôt que de le reproposer
                            """
                            
                            
                            self.not_proposed_items.remove(new_item.get_name())
                            new_item = True, new_item, ''
                            self.send_message(Message(self.get_name(), sender, MessagePerformative.PROPOSE, new_item))
                            """
                            #####################################################################################################
                            content = True, new_item, ''
                            self.send_message(Message(self.get_name(), sender, MessagePerformative.ACCEPT, content))

                            
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
        #
        item_values = self.model.item_values
        list_criterion = [CriterionName.PRODUCTION_COST, CriterionName.ENVIRONMENT_IMPACT,
                                       CriterionName.CONSUMPTION, CriterionName.DURABILITY,
                                       CriterionName.NOISE]
        #randomised list_criterion order
        list_criterion = random.sample(list_criterion, len(list_criterion))

        preference.set_criterion_name_list(list_criterion)
        
        values = {0: Value.VERY_BAD, 1: Value.BAD, 2: Value.AVERAGE, 3: Value.GOOD, 4: Value.VERY_GOOD}
        i=0
        for item in list_of_items:
           preference.add_criterion_value(CriterionValue(item, CriterionName.PRODUCTION_COST,
                                                         values[item_values[i][0]]))                                             
           preference.add_criterion_value(CriterionValue(item, CriterionName.CONSUMPTION,
                                                         values[item_values[i][1]]))
           preference.add_criterion_value(CriterionValue(item, CriterionName.DURABILITY,
                                                         values[item_values[i][2]]))
           preference.add_criterion_value(CriterionValue(item, CriterionName.ENVIRONMENT_IMPACT,
                                                         values[item_values[i][3]]))
           preference.add_criterion_value(CriterionValue(item, CriterionName.NOISE,
                                                      values[item_values[i][4]]))
           i=i+1

        return preference

    def generate_manual_preferences(self, list_of_items, profiles ):
        # To be completed
        """give a score for each item for each agent""" 
        preference = Preferences()

        values = {0: Value.VERY_BAD, 1: Value.BAD, 2: Value.AVERAGE, 3: Value.GOOD, 4: Value.VERY_GOOD}
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
            elif str(item) == "Steam Engine (A steam-punk engine)":
                profile = profiles[3]
            elif str(item) == "Natural Gas (A compressed natural gas engine)":
                profile = profiles[4]
            
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
    def __init__(self, profiles):
        super().__init__()
        self.schedule = BaseScheduler(self)
        self.__messages_service = MessageService(self.schedule)
        self.running = True
        diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
        electric_engine = Item("Electric Engine", "A very quiet engine")
        steam_engine = Item("Steam Engine", "A steam-punk engine")
        natural_gas = Item("Natural Gas", "A compressed natural gas engine")
        self.profiles = profiles

        self.list_of_items = [diesel_engine, electric_engine, steam_engine, natural_gas]
        self.item_values = self.generate_item_values()
        self.list_of_agents = []
        
        #### multi agent generation ####
        for i in range(2):
            print(80*'=')
            agent_name = "agent_" + str(i)
            if i % 2 == 0 :
                agent = ArgumentAgent(i, self, agent_name, True) 
            else:
                agent = ArgumentAgent(i, self, agent_name, False)

            self.schedule.add(agent)
            self.list_of_agents.append(agent)
        
    def generate_item_values(self):
        #generate a list of 5 item values for each item
        item_values = []
        for item in self.list_of_items:
            item_values.append([random.randint(1,4) for i in range(5)])
        return item_values
    
    def step(self):
        """step of the model"""
        self.__messages_service.dispatch_messages()
        self.schedule.step()
        return [agent.end_status for agent in self.list_of_agents]

            

            
def one_game(random_criterion_preferences=True):
    
    #scores : [cost of production, consumption, durability, environment impact, noise]  total = 12
    diesel_engine_scores = [3, 3, 4, 1, 1]
    electric_engine_scores = [0, 4, 2, 2, 4]
    steam_engine_scores = [1, 3, 3, 3, 2]
    natural_gas_scores = [1, 2, 4, 3, 2]
    if random_criterion_preferences:
        agent0_preferences = generate_preferences() #[0,3,1,2,4]
        agent1_preferences = generate_preferences() #[3,4,0,1,2]
    else :
        agent0_preferences = (0,3,1,2,4)
        agent1_preferences = (3,4,0,1,2)
        preferences_to_agent = {agent0_preferences:0, agent1_preferences:1}
        
    status = [False]
    agent0_profile = [agent0_preferences,diesel_engine_scores, electric_engine_scores, steam_engine_scores, natural_gas_scores]
    agent1_profile = [agent1_preferences,diesel_engine_scores, electric_engine_scores, steam_engine_scores, natural_gas_scores]
    player_list = [agent0_profile,agent1_profile]
    #shuffle player list to randomize the order of players
    starting_agent, next_agent = random.sample(player_list, 2) 
    print("Agent0 criterion preferences: ", starting_agent[0])
    print("Agent1 criterion preferences: ", next_agent[0])
    model = ArgumentModel(profiles=[starting_agent, next_agent])
    while True not in status:
        status = model.step()
    chosen_object = model.list_of_agents[0].commit_item[0]
    winning_agent = find_winning_agent(model)
    
    if not random_criterion_preferences:
        winning_agent = preferences_to_agent[winning_agent.profile[0]]
        
    return chosen_object, winning_agent
    
    
def find_winning_agent(model):
    chosen_object = model.list_of_agents[0].commit_item[0]
    winning_value = 0
    for agent in model.list_of_agents:
        object_value = chosen_object.get_score(agent.get_preference())
        if object_value > winning_value:
            winning_value = object_value
            winning_agent = agent
    return winning_agent

def generate_preferences():
    # generate a list [?,?,?,?,?] with integer from 0 to 4
    list = [0,1,2,3,4]
    randomised_list = random.sample(list, 5)
    return randomised_list
        
def find_list_of_arguments(model):
    list_of_arguments = []
    for agent in model.list_of_agents:
        list_of_arguments.append(agent.used_arguments)

def counter_item_type(items):
    """count the number of items of each type"""
    counter = {}
    for item in items:
        if item.get_name() in counter:
            counter[item.get_name()] += 1
        else:
            counter[item.get_name()] = 1
    return counter

def counter_criterion_type(arguments):
    """count the number of criterion"""
    counter = {}
    for argument in arguments:
        if argument != []:
            if argument[0][1][0] in counter:
                counter[argument[0][1][0]] += 1
            else:
                counter[argument[0][1][0]] = 1
    return counter

if __name__ == "__main__":
    chosen_objects = []
    winners = []
    winner_arguments = []
    random_criterion_preferences=True
    for i in range(1000): 
        chosen_object, winning_agent = one_game(random_criterion_preferences=random_criterion_preferences)
        chosen_objects.append(chosen_object)
        winners.append(winning_agent)
        print(winning_agent)
        if random_criterion_preferences:
            winner_arguments.append(winning_agent.used_arguments)

    if not random_criterion_preferences:
        counter_one_win = sum(winners)
        counter_zero_win = len(winners) - counter_one_win
        print(f"Number of times agent 0 won: {counter_one_win}")
        print(f"Number of times agent 1 won: {counter_zero_win}")
    #print how many times each item was chosen
    counter = counter_item_type(chosen_objects)
    print(counter)
    #plot counter as a bar chart
    import matplotlib.pyplot as plt
    plt.bar(counter.keys(), counter.values())
    plt.show()
    #print how many time each argument was used
    counter = counter_criterion_type(winner_arguments)
    plt.bar(counter.keys(), counter.values())
    plt.show()
