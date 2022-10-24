from __future__ import division
import math
import random
import pandas as pd
from collections import namedtuple
import numpy as np
import re

# Fact = namedtuple("Fact", "fact_id, question, answer")
Fact = namedtuple("Fact", "fact_id, question, context_1, context_2, answer, chosen_context, encounter_2")
Response = namedtuple("Response", "fact, start_time, rt, correct")
Encounter = namedtuple("Encounter", "activation, time, reaction_time, decay")

class SpacingModel(object):

    # Model constants
    LOOKAHEAD_TIME = 15000
    FORGET_THRESHOLD = -0.8
    WORD_THRESHOLD = 0.29
    CONTEXT2_THRESHOLD = 0.35
    DEFAULT_ALPHA = 0.3
    C = 0.25
    F = 1.0
    SHUFFLE_DATA_BEFORE_LOADING = False

    def __init__(self):
        self.facts = []
        self.responses = []
    
    def decide_context(self, fact, current_time):
        """
        Changes the cosen context to word if the activation is above the switch threshold, 
        and back to context if it is below the threshold 
        """
        alpha = self.get_rate_of_forgetting(current_time, fact)

        if alpha <= self.WORD_THRESHOLD:
            fact = fact._replace(chosen_context = fact.question)
        
        elif alpha < self.CONTEXT2_THRESHOLD and fact.encounter_2 == False:
            fact = fact._replace(chosen_context = fact.context_1)
            
        
        else:
            fact = fact._replace(chosen_context = fact.context_2)
            self.facts[fact.fact_id-1] = fact._replace(encounter_2 = True)

        return fact
    
    
    def add_fact(self, fact):
        # type: (Fact) -> None
        """
        Add a fact to the list of study items.
        """
        # Ensure that a fact with this ID does not exist already
        if next((f for f in self.facts if f.fact_id == fact.fact_id), None):
            raise RuntimeError(
                "Error while adding fact: There is already a fact with the same ID: {}. Each fact must have a unique ID".format(fact.fact_id))

        self.facts.append(fact)


    def register_response(self, response):
        # type: (Response) -> None
        """
        Register a response.
        """
        # Prevent duplicate responses
        if next((r for r in self.responses if r.start_time == response.start_time), None):
            raise RuntimeError(
                "Error while registering response: A response has already been logged at this start_time: {}. Each response must occur at a unique start_time.".format(response.start_time))

        self.responses.append(response)


    def get_next_fact(self, current_time):
        # type: (int) -> (Fact, bool)
        """
        Returns a tuple containing the fact that needs to be repeated most urgently and a boolean indicating whether this fact is new (True) or has been presented before (False).
        If none of the previously studied facts needs to be repeated right now, return a new fact instead.
        """ 
        # Calculate all fact activations in the near future
        fact_activations = [(f, self.calculate_activation(current_time + self.LOOKAHEAD_TIME, f)) for f in self.facts]

        seen_facts = [(f, a) for (f, a) in fact_activations if a > -float("inf")]
        not_seen_facts = [(f, a) for (f, a) in fact_activations if a == -float("inf")]

        # Prevent an immediate repetition of the same fact
        if len(seen_facts) > 2:
            last_response = self.responses[-1]
            print("less than 2 facts ")
            seen_facts = [(f, a) for (f, a) in seen_facts if f.fact_id != last_response.fact.fact_id]

        # Reinforce the weakest fact with an activation below the threshold
        seen_facts_below_threshold = [(f, a) for (f, a)in seen_facts if a < self.FORGET_THRESHOLD]
        if len(not_seen_facts) == 0 or len(seen_facts_below_threshold) > 0:
            weakest_fact = min(seen_facts, key = lambda t: t[1])
            weakest_fact_info = self.decide_context(weakest_fact[0], current_time)
            #return((weakest_fact[0], False))
            return((weakest_fact_info, False))

        # If none of the previously seen facts has an activation below the threshold, return a new fact
        return((not_seen_facts[0][0], True))


    def get_rate_of_forgetting(self, time, fact):
        # type: (int, Fact) -> float
        """
        Return the estimated rate of forgetting of the fact at the specified time
        """
        encounters = []

        responses_for_fact = [r for r in self.responses if r.fact.fact_id == fact.fact_id and r.start_time < time]
        alpha = self.DEFAULT_ALPHA

        # Calculate the activation by running through the sequence of previous responses
        for response in responses_for_fact:
            activation = self.calculate_activation_from_encounters(encounters, response.start_time)
            encounters.append(Encounter(activation, response.start_time, self.normalise_reaction_time(response), self.DEFAULT_ALPHA))
            alpha = self.estimate_alpha(encounters, activation, response, alpha)

            # Update decay estimates of previous encounters
            encounters = [encounter._replace(decay = self.calculate_decay(encounter.activation, alpha)) for encounter in encounters]

        return(alpha)


    def calculate_activation(self, time, fact):
        # type: (int, Fact) -> float
        """
        Calculate the activation of a fact at the given time.
        """

        encounters = []

        responses_for_fact = [r for r in self.responses if r.fact.fact_id == fact.fact_id and r.start_time < time]
        alpha = self.DEFAULT_ALPHA

        # Calculate the activation by running through the sequence of previous responses
        for response in responses_for_fact:
            activation = self.calculate_activation_from_encounters(encounters, response.start_time)
            encounters.append(Encounter(activation, response.start_time, self.normalise_reaction_time(response), self.DEFAULT_ALPHA))
            alpha = self.estimate_alpha(encounters, activation, response, alpha)

            # Update decay estimates of previous encounters
            encounters = [encounter._replace(decay = self.calculate_decay(encounter.activation, alpha)) for encounter in encounters]

        return(self.calculate_activation_from_encounters(encounters, time))


    def calculate_decay(self, activation, alpha):
        # type: (float, float) -> float
        """
        Calculate activation-dependent decay
        """
        return self.C * math.exp(activation) + alpha


    def estimate_alpha(self, encounters, activation, response, previous_alpha):
        # type: ([Encounter], float, Response, float) -> float
        """
        Estimate the rate of forgetting parameter (alpha) for an item.
        """
        if len(encounters) < 2:
            return(self.DEFAULT_ALPHA)

        a_fit = previous_alpha
        #chosen_context_id, chosen_context_found = self.decide_context(response.fact.context_1, response.fact.context_2)
        # response.fact.chosen_context = chosen_context_id
        # reading_time = self.get_reading_time(response.fact.question)
        reading_time = self.get_reading_time(response.fact.chosen_context)
        estimated_rt = self.estimate_reaction_time_from_activation(activation, reading_time)
        est_diff = estimated_rt - self.normalise_reaction_time(response)

        if est_diff < 0:
            # Estimated RT was too short (estimated activation too high), so actual decay was larger
            a0 = a_fit
            a1 = a_fit + 0.05
        
        else:
            # Estimated RT was too long (estimated activation too low), so actual decay was smaller
            a0 = a_fit - 0.05
            a1 = a_fit

        # Binary search between previous fit and proposed alpha
        for _ in range(6):
            # Adjust all decays to use the new alpha
            a0_diff = a0 - a_fit
            a1_diff = a1 - a_fit
            d_a0 = [e._replace(decay = e.decay + a0_diff) for e in encounters]
            d_a1 = [e._replace(decay = e.decay + a1_diff) for e in encounters]

            # Calculate the reaction times from activation and compare against observed RTs
            encounter_window = encounters[max(1, len(encounters) - 5):]
            total_a0_error = self.calculate_predicted_reaction_time_error(encounter_window, d_a0, reading_time)
            total_a1_error = self.calculate_predicted_reaction_time_error(encounter_window, d_a1, reading_time)

            # Adjust the search area based on the lowest total error
            ac = (a0 + a1) / 2
            if total_a0_error < total_a1_error:
                a1 = ac
            else:
                a0 = ac
        
        # The new alpha estimate is the average value in the remaining bracket
        return((a0 + a1) / 2)


    def calculate_activation_from_encounters(self, encounters, current_time):
        # type: ([Encounter], int) -> float
        included_encounters = [e for e in encounters if e.time < current_time]

        if len(included_encounters) == 0:
            return(-float("inf"))

        return(math.log(sum([math.pow((current_time - e.time) / 1000, -e.decay) for e in included_encounters])))


    def calculate_predicted_reaction_time_error(self, test_set, decay_adjusted_encounters, reading_time):
        # type: ([Encounter], [Encounter], Fact) -> float
        """
        Calculate the summed absolute difference between observed response times and those predicted based on a decay adjustment.
        """
        activations = [self.calculate_activation_from_encounters(decay_adjusted_encounters, e.time - 100) for e in test_set]
        rt = [self.estimate_reaction_time_from_activation(a, reading_time) for a in activations]
        rt_errors = [abs(e.reaction_time - rt) for (e, rt) in zip(test_set, rt)]
        return(sum(rt_errors))


    def estimate_reaction_time_from_activation(self, activation, reading_time):
        # type: (float, int) -> float
        """
        Calculate an estimated reaction time given a fact's activation and the expected reading time 
        """
        return((self.F * math.exp(-activation) + (reading_time / 1000)) * 1000)


    def get_max_reaction_time_for_fact(self, fact):
        # type: (Fact) -> float
        """
        Return the highest response time we can reasonably expect for a given fact
        """

        #chosen_context_id, chosen_context_found = self.decide_context(fact.context_1, fact.context_2)
        reading_time = self.get_reading_time(fact.chosen_context)
        # reading_time = self.get_reading_time(fact.question)
        max_rt = 1.5 * self.estimate_reaction_time_from_activation(self.FORGET_THRESHOLD, reading_time)
        return(max_rt)


    def get_reading_time(self, text):
        # type: (str) -> float
        """
        Return expected reading time in milliseconds for a given string
        """
        word_count = len(text.split())

        if word_count > 1:
            character_count = len(text)
            return(max((-157.9 + character_count * 19.5), 300))
        
        return(300)

    
    def normalise_reaction_time(self, response):
        # type: (Response) -> float
        """
        Cut off extremely long responses to keep the reaction time within reasonable bounds
        """
        rt = response.rt if response.correct else 60000
        max_rt = self.get_max_reaction_time_for_fact(response.fact)
        return(min(rt, max_rt))


    
class UIFeatures(SpacingModel):
    """
    Separating UI Specific Functions in a different class for readability and efficiency
    """
    def __init__(self) -> None:
        super().__init__()
        # self.vocab_df = pd.read_csv(pool[u"vocabulary_marked.csv"]) #annotated data
        self.vocab_df = pd.read_csv("vocabulary_marked.csv") #annotated data
        self.vocab_dict = dict(zip(self.vocab_df["question"].values, self.vocab_df["answer"].values)) # word: translation pairs
        self.reverse_vocab_dict = dict(zip(self.vocab_df["answer"].values, self.vocab_df["question"].values)) # translation:word pairs

    def word_from_context(self, context):
        """
        Extract the required word from the context. 
        Eg:
        "Deze opleiding heeft 'gemiddeld' 60 studenten per jaar." -> 'gemiddeld'
        """
        return re.findall("'.*'", context)[-1].replace("'","")
    
    def ret_translated_word(self, word):
        """
        Return the translation of the word from the dataframe. eg: English <-> Dutch 
        """
        try:
            return self.vocab_dict[word]
        except KeyError:
            return self.reverse_vocab_dict[word]
        else:
            print("Wrong word. Not in dict")
    
    def ret_translated_context(self, context):
        """
        Finds the word from the annotated context and return the translation of the word from the dataframe
        """

        return self.ret_translated_word(self.word_from_context(context=context))
    
    def calc_rof(self,row):
            return(self.get_rate_of_forgetting(row["start_time"] + 1, row["fact"]))
        
    def calc_reading_time(self,row):
        return(self.get_reading_time(row["fact"].context_1))
    
    def export_data(self, path = None):
        # type: (str) -> DataFrame
        """
        Save the response data to the specified csv file, and return a copy of the pandas DataFrame.
        If no path is specified, return a CSV-formatted copy of the data instead.
        """

        dat = self.create_statistics()
        # Save to CSV file if a path was specified, otherwise return the CSV-formatted output
        if path is not None:
            dat.to_csv(path, encoding="UTF-8")
            return(dat)
        
        return(dat.to_csv())
    
    def achievement(self):
        """
        All stats for user achievements
        """
        dat = self.create_statistics()
        correct, wrong = dat["correct"].value_counts().values
        mean_correct = correct/(correct+wrong)
        mean_wrong = wrong/(correct+wrong)

        return f"""
        \n
        Trial Index : {dat.index}\r
        Total Correct : {correct}\r
        Total Wrong : {wrong}\r
        Mean Correct : {mean_correct}\r
        Mean Wrong : {mean_wrong}\r
        """


    def create_statistics(self):
        dat_resp = pd.DataFrame(self.responses)
        dat_facts = pd.DataFrame([r.fact for r in self.responses])
        dat = pd.concat([dat_resp, dat_facts], axis = 1)

        # Add column for rate of forgetting estimate after each observation
        # dat["alpha"] = dat.apply(self.calc_rof, axis = 1)
        dat["reading_time"] = dat.apply(self.calc_reading_time, axis =1)
        dat["fogetting_rate"] = dat.apply(self.calc_rof, axis = 1)
        # dat["chosen_context"] = dat.apply(chosen_context_finder, axis =1)
        dat.drop(columns = "fact", inplace = True)

        # Add trial number column
        dat.index.name = "trial"
        dat.index = dat.index + 1

        return dat


