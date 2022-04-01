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
        self.__decision = boolean_decision
        self.__item = item.get_name()
        self.__comparison_list = []
        self.__couple_values_list = []

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
        for couple_value in self.__couple_values_list :
            if couple_value.get_criterion_name() == item :
                list_supporting_proposals.append(couple_value)
        list_supporting_proposals.sort(key=lambda x: preferences.get_preference(x.get_criterion_name()))
        return list_supporting_proposals
    
    def List_attacking_proposal ( self , item , preferences ) :
        """ Generate a list of premisses which can be used to attack an item
            param item : Item - name of the item
            return : list of all premisses CON an item ( sorted by order of importance based on preferences )
        """
        list_attacking_proposals = []
        for comparison in self.__comparison_list :
            if comparison.get_worst_criterion_name() == item :
                list_attacking_proposals.append(comparison)
        list_attacking_proposals.sort(key=lambda x: preferences.get_preference(x.get_worst_criterion_name()))
        return list_attacking_proposals
    
    def support_proposal ( self , item ) :
        """Used when the agent receives " ASK_WHY " after having proposed an item
            param item : str - name of the item which was proposed
            return : string - the strongest supportive argument
        """
        for couple_value in self.__couple_values_list :
            if couple_value.get_criterion_name() == item :
                return couple_value.get_value()
        return None
    