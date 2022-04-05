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

        for criterion_name in preferences.get_criterion_name_list():
            value = preferences.get_value(item, criterion_name)

            if value in ["GOOD" , "VERY_GOOD"]:
                premisse = self.add_premiss_couple_values(criterion_name, value)
                list_supporting_proposals.append(premisse)
        return list_supporting_proposals


    def List_attacking_proposal ( self , item , preferences ) :
        """ Generate a list of premisses which can be used to attack an item
            param item : Item - name of the item
            return : list of all premisses CON an item ( sorted by order of importance based on preferences )
        """
        list_attacking_proposals = []
        for criterion_name in preferences.get_criterion_name_list():
            value = preferences.get_value(item, criterion_name)

            if value in ["BAD" , "VERY_BAD"]:
                premisse = self.add_premiss_couple_values(criterion_name, value)
                list_attacking_proposals.append(premisse)

        return list_attacking_proposals

    
    def argument ( self , item, preferences  ) :
        """Used when the agent receives " ASK_WHY " after having proposed an item
            param item : str - name of the item which was proposed
            return : string - the strongest supportive argument
        """
        if self.__decision:        
            #print(item.get_name())
            #print(self.List_supporting_proposal(item , preferences))
            return (item.get_name(), self.List_supporting_proposal(item , preferences))

        else:
            return (item.get_name(), self.List_attacking_proposal(item , preferences))
    
