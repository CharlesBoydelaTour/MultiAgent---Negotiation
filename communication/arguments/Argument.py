#!/usr/bin/env python3

from communication.arguments.Comparison import Comparison
from communication.arguments.CoupleValue import CoupleValue


class Argument:
    """Argument class.
    This class implements an argument used in the negotiation.

    attr:
        decision:
        item:
        comparison_list:
        couple_values_list:
    """


    def __init__(self, boolean_decision, item):
        """Creates a new Argument.
        """
        self.__decision = boolean_decision #for positive or negative argument
        self.__item = item.get_name() #item name
        self.__comparison_list = [] 
        self.__couple_values_list = [] # either (criterion,value) or (criterion,criterion)

    def add_premiss_comparison(self, criterion_name_1, criterion_name_2):
        """Adds a premiss comparison in the comparison list.
        """
        self.__comparison_list.append(Comparison(criterion_name_1, criterion_name_2))

    def add_premiss_couple_values(self, criterion_name, value):
        """Add a premiss couple values in the couple values list.
        """
        self.__couple_values_list.append(CoupleValue(criterion_name, value))

    def List_supporting_proposal ( self , item , preferences ) :
        """ Generate a list of premisses which can be used to support an item
        param item : Item - name of the item
        return : list of all premisses PRO an item ( sorted by order of importance based on agent 's preferences)  
        """
        list_supporting_proposals = []
        
        pref_ordered = preferences.get_criterion_name_list()

        for i, criterion_name in enumerate(pref_ordered):
            value = preferences.get_value(item, criterion_name)
            #print(value.value)
            if value.value >=3:
                list_supporting_proposals.append(criterion_name)
                self.add_premiss_couple_values(criterion_name, value)
                for criterion_name_2 in pref_ordered[i+1:]:
                    self.add_premiss_comparison(criterion_name, criterion_name_2)

        return list_supporting_proposals


                    #print(self.__comparison_list[-1].get_best_criterion_name())
                #print(20*'-'+'\n',self.__couple_values_list[-1].get_criterion(), '\n'+20*'-')
                #criterion_name = self.__couple_values_list[-1].get_criterion()
                #value = self.__couple_values_list[-1].get_value()
                #print(self.__couple_values_list[-1].__str__())
                
                #premisse = (criterion_name, value)
                #print(self.__couple_values_list)
                #print(criterion_name)
                
                #print(list_supporting_proposals)
        """        
        print(30*'#')
        print(list_supporting_proposals)
        print__comparison_list = []
        print__couple_values_list = []
        for comparison in self.__comparison_list:
            #print(comparison.get_best_criterion_name())
            print__comparison_list.append((comparison.get_best_criterion_name(),comparison.get_worst_criterion_name()))
        print(30*'#')
        print(print__comparison_list)

        for couple_val in self.__couple_values_list:
            print__couple_values_list.append((couple_val.get_criterion(),couple_val.get_value()))            
        
        print(30*'#')
        print(print__couple_values_list)
        """
        #return list_supporting_proposals


    def List_attacking_proposal ( self , item , preferences ) :
        """ Generate a list of premisses which can be used to attack an item
            param item : Item - name of the item
            return : list of all premisses CON an item ( sorted by order of importance based on preferences )
        """
        list_attacking_proposals = []

        pref_ordered = preferences.get_criterion_name_list()

        for i, criterion_name in enumerate(pref_ordered):
            value = preferences.get_value(item, criterion_name)
            #print(value.value)
            if value.value <=2:
                list_attacking_proposals.append(criterion_name)
                self.add_premiss_couple_values(criterion_name, value)
                for criterion_name_2 in pref_ordered[i+1:]:
                    self.add_premiss_comparison(criterion_name, criterion_name_2)

        return list_attacking_proposals


        
    
    def argument_why ( self , item, preferences) :
        """Used when the agent receives " ASK_WHY " after having proposed an item
            param item : str - name of the item which was proposed
            return : string - the strongest supportive argument
        """
        argument =[]
       
        #print(item.get_name())
        #crit_name = self.List_supporting_proposal(item , preferences)[0]
        #value = self.List_supporting_proposal(item , preferences)[1]
        self.List_supporting_proposal(item , preferences)
        argument.append(self.__couple_values_list[0])



        #print(argument)
        #argument.__str__()
        #print(argument.__str__())
        #message = f"{item.get_name()} <= {argument.__str__()}"

        return self.__decision, item, argument


    def argument_to_argument ( self , item, preferences, criterion_recu  ) :
        """
        ...

        """
        argument =[]
        if not self.__decision:        

            list_attacking_proposals = self.List_attacking_proposal(item , preferences)
            if len(list_attacking_proposals) >= 1:
                for i, criterion in enumerate(list_attacking_proposals):
                    if preferences.is_preferred_criterion(criterion_name_1 = criterion, criterion_name_2 = criterion_recu):
                        
                        argument.append(Comparison(criterion, criterion_recu))
                        argument.append(self.__couple_values_list[i])
                        break
            else:
                print('accept pour le moment')

            return self.__decision, item, argument

        else:
            
