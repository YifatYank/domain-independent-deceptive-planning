import os
from pyperplanmaster.src.pyperplan.planner import _parse, _ground, SEARCHES, HEURISTICS, search_plan
from pyperplanmaster.src.pyperplan.task import Operator
#from pyperplanmaster.src.pyperplan.planner import SEARCHES, search_plan
from generatePlans import createTaskFor, getRealTask, generatePlan


#DIR = os.path.dirname(__file__)
DIR = os.path.abspath("C:\\Users\\Yifat\\Desktop\\THESIS\\data")
PROBLEM_NAME = 'base-exp'
MYDIR = os.path.join(DIR, PROBLEM_NAME)
TEMP_DIR = os.path.join(MYDIR, 'temp')
PROBLEM_DIR = os.path.join(MYDIR, 'problem_files')
PLANS_DIR = os.path.join(MYDIR, 'plan_files')
REPRESENTAION_TO_FILENAME = os.path.join(PLANS_DIR, 'filesdictionary')

BLOCKS_DOMAIN_DIR = os.path.join(PROBLEM_DIR, 'domain.pddl')
GOALS_FILE = os.path.join(PROBLEM_DIR, 'goals.pddl')
REAL_GOAL_FILE = os.path.join(PROBLEM_DIR, 'real_goal.pddl')
PATH_STATES_FILE = os.path.join(PROBLEM_DIR, 'init_states.pddl')
PLAN_FILE = os.path.join(PROBLEM_DIR, 'plan.pddl')
INIT_STATE_FILE = os.path.join(PROBLEM_DIR, 'real_init_state.pddl')
TEMPLATE_FILE = os.path.join(PROBLEM_DIR, 'template_task.pddl')


lines_of_definition = ['task-name', 'domain', 'objects', 'init', 'goal']

# Returns a dictionary, contains all the nessesary parts of a task in a domain promlem. 
def load_domain_template():
    task_definition = {}

    with open(TEMPLATE_FILE) as f:
        task_definition['task-name'] = f.readline()
        task_definition['domain'] = f.readline()
        task_definition['objects'] = f.readline()
        task_definition['objects'] = task_definition['objects'].replace(";", "\n")
        task_definition['init'] = f.readline()
        task_definition['goal'] = f.readline()

    return task_definition

# Gets a template for a pddl problem, an initial strate and a goal,
# and create a file with a pddl task, for the initial satate and the goal. 
def create_task_description_file(name ,init_state, goal, template):
    task = {}
    task['task-name'] = template['task-name'].replace('template', name)
    task['domain'] = template['domain']
    task['objects'] = template['objects']
    task['init'] = init_state + "\n"
    task['goal'] = template['goal'].replace('template', goal)

    name = name + '.pddl'
    file_name = os.path.join(TEMP_DIR, name)
    with open(file_name, "w") as f:
        for line in task.values():
            f.writelines(line)
        f.writelines(')')

# My purpose in life.
def create_problems(general_name, template, init_states, goals):
    for init_index in range(len(init_states)):
        for goal_index in range(len(goals)):
            name = general_name + "from" + str(init_index) + "to" + str(goal_index)
            create_task_description_file(name ,init_states[init_index], goals[goal_index], template)

def get_states_of_plan(name, domaindir):
    # Create a plan for the chosen goal.
    #problem_file = os.path.join(TEMP_DIR, name.format(str(init_state_num), str(goal_num)))
    problem_file = os.path.join(TEMP_DIR, name + ".pddl")
    plan_ops = search_plan(domaindir, problem_file, SEARCHES["bfs"], None)

    # Executes the plan step by step and saves the wolrd state after each step.
    world_states = []

    problem = _parse(domaindir, problem_file)
    task = _ground(problem)
    
    curr_state = task.initial_state
    world_states.append(curr_state)

    for action in plan_ops:
        for operator, successor_state in task.get_successor_states(curr_state):
            # Check about that:
            if operator == action:
                world_states.append(successor_state)
                curr_state = successor_state

    return plan_ops, world_states

def write_states_to_file(file_name, states):
    with open (file_name, "w") as f:
        for state in states:
            f.write("(:INIT")
            for fact in state:
                f.write(" " + str(fact).upper())
            f.write(")\n")

def write_obs_to_file(file_name, obs):
    name = file_name + '.pddl'
    file_name = os.path.join(PLANS_DIR, name)
    with open (file_name, "w") as f:
        if len(obs) != 0:
            f.write(str(obs[0].name).upper())
            for i in range(1, len(obs)):
                f.write("\n" + str(obs[i].name).upper())

def blocks_representaion(str):
    format_state = str
    format_state = format_state.replace("CLEAR", "C")
    format_state = format_state.replace("ONTABLE", "OT")
    format_state = format_state.replace("ON", "O")
    format_state = format_state.replace("HOLDING", "H")
    format_state = format_state.replace("HANDEMPTY", "HE")

    return format_state

def depots_representation(str):
    format_state = str
    format_state = format_state.replace("CLEAR", "C")
    format_state = format_state.replace("AVAILABLE", "A")
    format_state = format_state.replace("LIFTING", "L")
    format_state = format_state.replace("CRATE", "CR")
    format_state = format_state.replace("AT", "A")
    format_state = format_state.replace("ON", "O")
    format_state = format_state.replace("IN ", "I ")
    format_state = format_state.replace("PALLET", "P")
    format_state = format_state.replace("DEPOT", "D")
    
    format_state = format_state.replace("DISTRIBUTOR", "DI")
    format_state = format_state.replace("HOIST", "H")
    format_state = format_state.replace("TRUCK", "T")

    return format_state

# Make a unick state reparesentation, for init states, and goal states.
def unique_state_representation(state, domain_spesific_representation):
    format_state = str(state).strip()
    format_state = domain_spesific_representation(format_state)

    format_state = format_state.replace(":INIT ", "")  # Deals with init state representstion.
    format_state = format_state.replace(") (",")-(")
    format_state = format_state.replace(" ","_")
    format_state = format_state.replace("))",")")      # Deals with init state representstion.
    format_state = format_state.replace("((","(")      # Deals with init state representstion.
    

    format_state = format_state.split("-")
    
    format_state.sort()
    format_state = str(format_state)
    format_state = format_state.replace("'","")
    format_state = format_state.replace(", ","")

    format_state = format_state[1:-1]

    return format_state

def write_resresentations_to_file_names(representation_dist, file_name):
    with open (file_name, "w") as f:
        f.writelines(representation_dist)

if __name__ == "__main__":
    # Load the domain's template.
    task_definition = load_domain_template()
    
    # Load the goal state.
    goal = []
    with open (REAL_GOAL_FILE) as f:
        goal = f.read() 
    goal = goal.splitlines()
    goal = goal[0]

    # Load the init state
    init_state = []
    with open (INIT_STATE_FILE) as f:
        init_state = f.read()
    init_state = init_state.splitlines()
    init_state = init_state[0]

    # Create a file problem from init to goal
    create_task_description_file("init-to-goal" ,init_state, goal, task_definition)

    # Creates a file with all the world's states, during the plan execution from the init state to the goal.
    #plan_actions, states_during_plan_execution = get_states_of_plan("init-to-goal", BLOCKS_DOMAIN_DIR)
    #write_states_to_file(PATH_STATES_FILE, states_during_plan_execution)
    #write_obs_to_file("plan", plan_actions)

    # Get the states of the world, during the plan's exexution.
    states_during_execution = []
    with open (PATH_STATES_FILE) as f:
        states_during_execution = f.read()
    states_during_execution = states_during_execution.splitlines()

    # Gets all the possible goals.
    possible_goals = []
    with open (GOALS_FILE) as f:
        possible_goals = f.read()
    possible_goals = possible_goals.splitlines()


    file_index = 0
    representaion_to_file_name = {}
    # Go throuth each state of the world, during the plan's exexution.
    for state in states_during_execution:
        print("state = ", state)
        # Go throuth all the possible goals.
        format_state = unique_state_representation(state, blocks_representaion)
        for goal in possible_goals:
            #file_name = "obs-" + PROBLEM_NAME + "-"+ str(file_index)
            print("goal = ", goal)
            format_goal = unique_state_representation(goal, blocks_representaion)            
            uniq_froblem_name = "from-" + format_state + "-to-" + format_goal
            file_name = "obs-" + uniq_froblem_name
            
            
            create_task_description_file(file_name, state, goal, task_definition)
            plan_obs, _ = get_states_of_plan(file_name, BLOCKS_DOMAIN_DIR)
            
            write_obs_to_file(file_name, plan_obs)
            representaion_to_file_name[uniq_froblem_name] = file_name
    
    write_resresentations_to_file_names(representaion_to_file_name, REPRESENTAION_TO_FILENAME)

    print("fun!")




'''
def calc_prob_for_goals(name, domaindir, task_definition, goals, init_state, goal_num, init_state_num):
    name = name + "from{}to{}.pddl"
    
    # Get the states the agent reached during the plan to the goal.
    states_of_plan = get_states_of_plan(name, domaindir, goal_num, init_state_num)

    num_of_goals = len(goals)
    # Save the problem files, from the init state to all the possible goals.
    problems_files = []
    for curr_goal_num in range(num_of_goals):
        problems_files.append(os.path.join(TEMP_DIR, name.format(str(init_state_num),str(curr_goal_num))))

    # Calculates the length of the shortest plan from the initial state to each goal.
    shortest_plan_length = {}
    for curr_goal_num in range(num_of_goals):
        curr_problem_file = problems_files[curr_goal_num]
        curr_plan_ops = search_plan(domaindir, curr_problem_file, SEARCHES["bfs"], None)
        shortest_plan_length[curr_goal_num] = []
        shortest_plan_length[curr_goal_num].append(len(curr_plan_ops))

    
    templatedir = f"{TEMP_DIR}/template_form.pddl"
    template = ""
    # Read template
    with open(templatedir) as templatefile:
        template = templatefile.read()
        templatefile.close()

    goals_other_formate = []
    for goal in goals:
        goals_other_formate.append(change_goal_format(goal))

    landmarks_list = []
    initial_state = states_of_plan[0] 
    for state in states_of_plan:
        landmarks_list.append(state)

        for curr_goal_num in range(num_of_goals):
            temp_landmark_list = landmarks_list
            temp_landmark_list.append(goals_other_formate[curr_goal_num])
            plan = generatePlan(initial_state, temp_landmark_list, template, domaindir)
            shortest_plan_length[curr_goal_num].append(len(plan))


def change_goal_format(goal):
    goal = goal.replace(") ",")-")
    return goal.split('-')

'''