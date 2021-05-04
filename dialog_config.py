import pickle
import copy
import numpy as np
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sys_inform_slots = ['disease']

start_dia_acts = {
    'request': ['disease']
}

sys_inform_slots_values = [
    'adhd',
    'depression',
    'osteoporosis',
    'influenza',
    'copd',
    'type ii diabetes',
    'other'
]

# top 80% most frequent symptoms
sys_request_slots_highfreq = [
    'fever',
    'restlessness',
    'headache',
    'difficulty breathing',
    'sore throat',
    'cough',
    'eye pain',
    'tiredness or fatigue',
    'muscle or body aches',
    'sleep disturbances, including insomnia or sleeping too much',
    'shortness of breath',
    'easily distracted',
    'dry, persistent cough',
    'back pain',
    'wheezing',
    'chest pain or tightness',
    'chills and sweats',
    'weight loss',
    'nausea',
    'trouble focusing on a task',
    'vomiting and diarrhea',
    'feelings of sadness'
]

sys_request_slots = symptoms = [
    'always on the go',
    'angry outbursts, irritability or frustration, even over small matters',
    'anxiety or agitation',
    'areas of darkened skin, usually in the armpits and neck',
    'back pain',
    'be disorganized',
    'bone pain',
    'brittle bones',
    "can not read people's feelings and moods",
    'chest pain or tightness',
    'chills and sweats',
    'clear, white, yellow, or greenish mucus',
    'cough',
    'crying or tearfulness',
    'daydream a lot',
    'dehydration (dry mouth, no tears when crying)',
    'difficulty breathing',
    'dizziness',
    'dry, persistent cough',
    'easily distracted',
    'even small tasks take extra effort',
    'excess phlegm or sputum',
    'eye pain',
    'feeling misunderstood and extremely sensitive',
    'feelings of emptiness or hopelessness',
    'feelings of sadness',
    'feelings of worthlessness or guilt',
    'fever',
    'fidget and squirm when seated',
    'fracture from a fall',
    'frequent infections',
    'frequent or recurrent thoughts of death, suicidal thoughts, suicide attempts or suicide',
    'frequent respiratory infections',
    'frequent urination',
    'frequently interrupt or intrude on others',
    'get up frequently to walk or run around',
    'have a hard time getting along with others',
    'have a hard time paying attention to details',
    'have a hard time waiting for their turn',
    'have a hard time waiting to talk or react',
    'have trouble staying on topic while talking',
    'having trouble playing quietly or doing quiet hobbies',
    'headache',
    'impatience',
    'impulsiveness',
    'increased appetite or hunger',
    'increased thirst',
    'joint pain',
    'loss of consciousness or fainting',
    'loss of interest or pleasure in most or all normal activities, such as sex, hobbies or sports',
    'low sugar reading',
    'memory difficulties or forgetfulness',
    'mood swings',
    'muscle or body aches',
    'nausea',
    'neck pain',
    'not following social rules',
    'not listening to others',
    'numbness or tingling in the hands or feet',
    'often wanting to stay at home, rather than going out to socialize or doing new things',
    'personality changes',
    'problems at social events or work',
    'receding gums',
    'reduced appetite',
    'restlessness',
    'runny or stuffy nose',
    'seizures',
    'severe muscle pain',
    'shortness of breath',
    'sleep disturbances, including insomnia or sleeping too much',
    'slight curving of the upper back',
    'slow-healing sores',
    'slowed thinking, speaking or body movements',
    'sore throat',
    'swelling in ankles, feet, or legs',
    'talk excessively',
    'tiredness or fatigue',
    'too wrapped up in own thoughts',
    'trouble focusing on a task',
    'trouble thinking, concentrating, making decisions and remembering things',
    'vomiting and diarrhea',
    'weak and brittle fingernails',
    'weakness',
    'weight gain',
    'weight loss',
    'wheezing',
    'winded'
]

################################################################################
# Dialog status
################################################################################
FAILED_DIALOG = -1
SUCCESS_DIALOG = 1
NO_OUTCOME_YET = 0

# Rewards
SUCCESS_REWARD = 50
FAILURE_REWARD = 0
PER_TURN_REWARD = 0


################################################################################
#  Diagnosis
################################################################################
NO_DECIDE = 0
NO_MATCH = "no match"
NO_MATCH_BY_RATE = "no match by rate"

################################################################################
#  Special Slot Values
################################################################################
I_AM_NOT_SURE = -1
I_DO_NOT_CARE = "I do not care"
NO_VALUE_MATCH = "NO VALUE MATCHES!!!"

################################################################################
#  Slot Values
################################################################################
TRUE = 1
FALSE = -1
NOT_SURE = -2
NOT_MENTION = 0

################################################################################
#  Constraint Check
################################################################################
CONSTRAINT_CHECK_FAILURE = 0
CONSTRAINT_CHECK_SUCCESS = 1

################################################################################
#  NLG Beam Search
################################################################################
nlg_beam_size = 10

################################################################################
#  run_mode: 0 for dia-act; 1 for NL; 2 for no output
################################################################################
run_mode = 0
auto_suggest = 0

################################################################################
#   A Basic Set of Feasible actions to be Consdered By an RL agent
################################################################################
feasible_actions = [

    ############################################################################
    #   thanks actions
    ############################################################################
    {'diaact': "thanks", 'inform_slots': {}, 'request_slots': {}},
    {'diaact': "inform", 'inform_slots': {'disease': 'UNK', 'taskcomplete': "PLACEHOLDER"}, 'request_slots': {}}

]
############################################################################
#   Adding the inform actions
############################################################################
for slot_val in sys_inform_slots_values:
    slot = 'disease'
    feasible_actions.append({'diaact': 'inform', 'inform_slots': {slot:slot_val, 'taskcomplete': "PLACEHOLDER"}, 'request_slots':{}})
############################################################################
#   Adding the request actions
############################################################################
for slot in sys_request_slots:
    feasible_actions.append({'diaact': 'request', 'inform_slots': {}, 'request_slots': {slot: 'UNK'}})

