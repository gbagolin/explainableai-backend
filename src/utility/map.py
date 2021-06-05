from src.xpomcp.State import State

'''States for Tiger problem '''
TIGER_LEFT = State("tiger left")
TIGER_RIGHT = State("tiger right")
'''States for Velocity regulation problem '''
EASY = State(0)
INTERMEDIATE = State(1)
DIFFICULT = State(2)
'''
MAP BETWEEN ACTION AND STRING. 
'''

MAP_STATES_TO_FRONTEND = {
    0: "easy",
    1: "intermediate",
    2: "difficult",
    "tiger left": "tiger left",
    "tiger right": "tiger right"
}

MAP_ACTIONS_TO_FRONTEND = {
    0: "slow",
    1: "medium",
    2: "fast",
    "open left": "open left",
    "open right": "open right",
    "listen": "listen"
}

MAP_ACTIONS_TO_BACKEND = {
    "slow": 0,
    "medium": 1,
    "fast": 2,
    "open left": "open left",
    "open right": "open right",
    "listen": "listen",
}

MAP_TRACES = {
    "velocity regulation arms": "vr_ARMS.xes",
    "tiger correct": "tiger_correct.xes",
    "tiger 40": "dataset_tiger_40.xes",
    "tiger 60": "dataset_tiger_60.xes",
    "tiger 80": "dataset_tiger_80.xes",
    "velocity regulation 10": "obstacle_avoidance_10.xes",
    "velocity regulation 10 with graph": "obstacle_avoidance_10_graph.xes",
    "velocity regulation 100": "obstacle_avoidance_100.xes",
    "vr 50 no shields" : "vr_50_no_shield.xes", 
    "vr 70 no shields" : "vr_70_no_shield.xes",
    "vr 90 no shields" : "vr_90_no_shield.xes",
    "vr 103 no shields" : "vr_103_no_shield.xes",
}
