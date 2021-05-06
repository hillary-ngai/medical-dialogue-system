"""
Created on May 17, 2016

@author: xiul, t-zalipt
"""

import json
import dialog_config
from dialog_system.state_tracker import StateTracker


class DialogManager:
    """ A dialog manager to mediate the interaction between an agent and a customer """

    def __init__(self, agent, user, act_set, slot_set, params):
        self.agent = agent
        self.user = user
        self.act_set = act_set
        self.slot_set = slot_set  # slot for agent
        self.state_tracker = StateTracker()
        self.user_action = None
        self.reward = 0
        self.episode_over = False
        self.dialog_status = dialog_config.NO_OUTCOME_YET
        self.hit_rate = 0
         
    def initialize_episode(self):
        """ Refresh state for new dialog """

        self.reward = 0
        self.episode_over = False
        self.state_tracker.initialize_episode()
        self.user_action, self.goal = self.user.initialize_episode()
        self.state_tracker.update(user_action=self.user_action)
        self.hit_rate = 0

        if dialog_config.run_mode < 3:
            print("New episode, user goal:")
            print(self.user.goal)
            self.print_function(user_action=self.user_action)

        self.agent.initialize_episode()

    def next_turn(self, record_training_data=True):
        """ This function initiates each subsequent exchange between agent and user (agent first) """

        #   CALL AGENT TO TAKE HER TURN
        self.state = self.state_tracker.get_state_for_agent()
        print('state', self.state)
        self.agent_action, repeat = self.agent.state_to_action(self.state)
        
        #   Register AGENT action with the state_tracker
        self.state_tracker.update(agent_action=self.agent_action)

        # self.agent.add_nl_to_action(self.agent_action) # add NL to Agent Dia_Act
        self.print_function(agent_action=self.agent_action['act_slot_response'])

        #   CALL USER TO TAKE HER TURN
        self.sys_action = self.state_tracker.dialog_history_dictionaries()[-1]
        self.user_action, self.episode_over, self.dialog_status, hit = self.user.next(self.sys_action)

        self.reward = self.reward_function(self.dialog_status, hit)

        #   Update state tracker with latest user action
        if self.episode_over != True:
            self.state_tracker.update(user_action=self.user_action)
            self.print_function(user_action=self.user_action)

        #  Inform agent of the outcome for this timestep (s_t, a_t, r, s_{t+1}, episode_over)
        if record_training_data:
            self.agent.register_experience_replay_tuple(self.state, self.reward,
                                                        self.state_tracker.get_state_for_agent(), self.episode_over)
        self.hit_rate += hit
        return self.episode_over, self.reward, self.dialog_status, self.hit_rate


    def reward_function(self, dialog_status, hit_rate):
        """ Reward Function 1: a reward function based on the dialog_status """
        if dialog_status == dialog_config.FAILED_DIALOG:
            reward = -1*self.user.max_turn  # -22
        elif dialog_status == dialog_config.SUCCESS_DIALOG:
            reward =  2 * self.user.max_turn  # 44
        else:
            reward = -1 + hit_rate
        return reward


    def print_function(self, agent_action=None, user_action=None):
        """ Print Function """

        if agent_action:
            # print(agent_action)
            if dialog_config.run_mode == 0:
                if self.agent.__class__.__name__ != 'AgentCmd':
                    #print("Turn %d sys: %s" % (agent_action['turn'], agent_action['nl']))
                    if user_action:
                        print("diaact", user_action['diaact'])
                        print("request_slots", user_action['request_slots'])
                        print("inform_slots", user_action['inform_slots'])
                        print("Turn %d" % (agent_action['turn']))
                        print()
            elif dialog_config.run_mode == 1:
                if self.agent.__class__.__name__ != 'AgentCmd':

                    print("Turn %d sys: %s, inform_slots: %s, request slots: %s" %(agent_action['turn'], agent_action['diaact'], agent_action['inform_slots'], agent_action['request_slots']))
            elif dialog_config.run_mode == 2:  # debug mode
                print("Turn %d sys: %s, inform_slots: %s, request slots: %s" % (agent_action['turn'], agent_action['diaact'], agent_action['inform_slots'],agent_action['request_slots']))
                #print("Turn %d sys: %s" % (agent_action['turn'], agent_action['nl']))

                # if dialog_config.auto_suggest == 1:
                #     print('(Suggested Values: %s)' % (self.state_tracker.get_suggest_slots_values(agent_action['request_slots'])))
        elif user_action:
            if dialog_config.run_mode == 0:
                print("diaact", user_action['diaact'])
                print("inform_slots", user_action['inform_slots'])
                print("request_slots", user_action['request_slots'])
                print("Turn %d" % (user_action['turn']))
                print()
            elif dialog_config.run_mode == 1:
                print("Turn %s usr: %s, inform_slots: %s, request_slots: %s" % (user_action['turn'], user_action['diaact'], user_action['inform_slots'], user_action['request_slots']))
            elif dialog_config.run_mode == 2:  # debug mode, show both
                print("Turn %d usr: %s, inform_slots: %s, request_slots: %s" % (user_action['turn'], user_action['diaact'], user_action['inform_slots'], user_action['request_slots']))
                print("Turn %d usr: %s" % (user_action['turn'], user_action['nl']))
            #
            # if self.agent.__class__.__name__ == 'AgentCmd':  # command line agent
            #     user_request_slots = user_action['request_slots']
            #     if 'ticket' in user_request_slots.keys(): del user_request_slots['ticket']
            #     if len(user_request_slots) > 0:
            #         possible_values = self.state_tracker.get_suggest_slots_values(user_action['request_slots'])
            #         for slot in possible_values.keys():
            #             if len(possible_values[slot]) > 0:
            #                 print('(Suggested Values: %s: %s)' % (slot, possible_values[slot]))
            #             elif len(possible_values[slot]) == 0:
            #                 print('(Suggested Values: there is no available %s)' % (slot))
            #     else:
            #         kb_results = self.state_tracker.get_current_kb_results()
            #         print('(Number of movies in KB satisfying current constraints: %s)' % len(kb_results))

