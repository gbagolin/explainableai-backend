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
    0: "low",
    1: "medium",
    2: "high",
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
    "Velocity regulation ARMS": "vr_ARMS.xes",
    "Tiger correct": "tiger_correct.xes",
    "Tiger 40": "dataset_tiger_40.xes",
    "Tiger 60": "dataset_tiger_60.xes",
    "Tiger 80": "dataset_tiger_80.xes",
    "Velocity regulation 10": "obstacle_avoidance_10.xes",
    "Velocity regulation 100": "obstacle_avoidance_100.xes",
}