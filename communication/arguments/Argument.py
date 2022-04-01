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
        list_supporting_proposal = []
        for criterion in preferences.get_criteria_list():
            if preferences.get_criterion_value(criterion, item) == "GOOD" or preferences.get_criterion_value(criterion, item) == "VERY_GOOD":
                list_supporting_proposal.append(criterion)
        return list_supporting_proposal
    
    def List_attacking_proposal ( self , item , preferences ) :
        """ Generate a list of premisses which can be used to attack an item
            param item : Item - name of the item
            return : list of all premisses CON an item ( sorted by order of importance based on preferences )
        """
        list_rejecting_proposal = []
        for criterion in preferences.get_criteria_list():
            if preferences.get_criterion_value(criterion, item) == "BAD" or preferences.get_criterion_value(criterion, item) == "VERY_BAD":
                list_rejecting_proposal.append(criterion)
        return list_rejecting_proposal
    
    def support_proposal ( self , item , preferences ) :
        """Used when the agent receives " ASK_WHY " after having proposed an item
            param item : str - name of the item which was proposed
            return : string - the strongest supportive argument
        """
        if self.__decision:
            list_supporting_proposal = self.List_supporting_proposal(item, preferences)
            #sort by best criterion
            list_supporting_proposal.sort(key=lambda x: preferences.get_criterion_value(x, item), reverse=True)
            #generate argument
            self.add_premiss_couple_values(list_supporting_proposal[0], preferences.get_criterion_value(list_supporting_proposal[0], item))
            return list_supporting_proposal[0]
        else:
            list_rejecting_proposal = self.List_attacking_proposal(item, preferences)
            #sort by best criterion
            list_rejecting_proposal.sort(key=lambda x: preferences.get_criterion_value(x, item), reverse=False)
            #generate argument
            self.add_premiss_couple_values(list_rejecting_proposal[0], preferences.get_criterion_value(list_rejecting_proposal[0], item))
            return list_rejecting_proposal[0]
    