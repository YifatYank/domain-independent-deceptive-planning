import random
import os
import re
import subprocess
import shutil
from pyperplanmaster.src.pyperplan.planner import _parse, _ground, SEARCHES, search_plan

def get_plan_to_goal(problem, temp_path):
    real_hype = str(problem['real-hype'])
    real_hype = real_hype[1:-1]
    real_hype = real_hype.replace("'","")
    real_hype = real_hype.replace(", ","")

    with open (problem['init_state']) as f :
        problem_file_content = f.readlines()
    
    for i in range(len(problem_file_content)):
        if "HYPOTHESIS" in  problem_file_content[i]:
            problem_file_content[i] = problem_file_content[i].replace("<HYPOTHESIS>",real_hype)
    problem_file = os.path.join(temp_path, "temp_file.pddl")
    
    with open(problem_file , 'w') as f:
        f.writelines(problem_file_content)

    plan_ops = search_plan(domain_files[domain], problem_file, SEARCHES["bfs"], None)

    return plan_ops

def choose_combined_goal(atom_goals):
    combined_goals = []
    
    prob = 0.75
    new_goal = []
   
    # Put every atom-goal in the combined-goal in a prob of 1\num of goals.       
    for atom_goal in atom_goals:
        num = random.random()
        if (num < prob):
            new_goal.append(atom_goal)
    
    if len(new_goal) == 0:
        atom_goals_array = list(atom_goals)
        new_goal.append(atom_goals_array[random.randint(0,len(atom_goals) -1)])

    return new_goal

def turn_goals_to_atoms(goals):
    atom_goals_set = set()

    for goal in goals:
        seperated_goals = goal.split(",")
        for sep_goal in seperated_goals:
            if "\\n" in sep_goal:
                print("here")
            atom_goals_set.add(sep_goal)

    return atom_goals_set

def choose_goals(goals_list, num_of_goals):
    index_set = set()
    chosen_goals = []

    while(len(index_set) < num_of_goals):
        index_set.add(random.randint(0, len(goals_list) -1))

    goals_array = list(goals_list)

    for index in index_set:
        chosen_goals.append(goals_array[index])

    return chosen_goals

def create_problems_java_format(domain_new_problem_path):
    index = 0
    for problem in problems[domain]:
        # First check if there is a plan from the initial state to the goal.
        # (Mabey the goal that was randomly built is unreachable).
        pln = get_plan_to_goal(problem, "C:\\Users\\Yifat\\Desktop\\THESIS")        
        if pln is None:
            # Dont create a zip file for this problem.
            continue


        problem_path = os.path.join(domain_new_problem_path, "problem-" + str(index))
        os.makedirs(problem_path)

        # Copy the domain file
        shutil.copy(domain_files[domain], os.path.join(problem_path, DOMAIN_FILE))
        
        # Copy the init file.
        shutil.copy(problem['init_state'], os.path.join(problem_path, INIT_STATE_FILE_NAME))
        
        with open(os.path.join(problem_path, HYPES_FILE_NAME), "w") as f:
            for hype in problem['hypes']:
                f.writelines(hype + "\n")

        real_hype = str(problem['real-hype'])
        real_hype = real_hype[1:-1]
        real_hype = real_hype.replace("'","")
        real_hype = real_hype.replace(", ",",")

        with open(os.path.join(problem_path, REAL_HYP_FILE), "w") as f:
            f.writelines(real_hype)

        with open(os.path.join(problem_path, OBS_FILE), "w") as f:
            for action in pln:
                f.writelines(str(action.name) + "\n")

        # If all the files were created:
        if (os.path.exists(os.path.join(problem_path, DOMAIN_FILE)) and
            os.path.exists(os.path.join(problem_path, INIT_STATE_FILE_NAME)) and
            os.path.exists(os.path.join(problem_path, HYPES_FILE_NAME)) and
            os.path.exists(os.path.join(problem_path, REAL_HYP_FILE)) and
            os.path.exists(os.path.join(problem_path, OBS_FILE))):

            command = 'C:\\Program Files\\WinRAR\\WinRAR.exe'
            
            file_name_without_path = re.match("[^//]*$","problem_path")
            full_command = ["cmd", "/c", command, "a", "-ep1" ,problem_path + ".tar.bz2" ,problem_path + "\\*" ]
            result = subprocess.run(full_command)
            print(str(full_command))

        if result.returncode == 0:
            print("Success:")
        else:
            print("Fail:")
            print(result.stderr)             
        index += 1

def create_problems_for_initial_state(domain, initial_state, num_of_problems):
    for i in range(num_of_problems):
        problem_dict = {}
        problem_dict['init_state'] = init_files[domain][str(initial_state)]
        problem_dict['hypes'] = choose_goals(goals[domain][str(initial_state)], 5)
        problem_dict['real-hype'] = choose_combined_goal(problem_dict['hypes'])
        problems[domain].append(problem_dict)

def unzip_file(problem_tar_file):
    match = re.match(r"^[^.]+", problem_tar_file)
    if not match:
        return
    file_without_extention = match.group(0)
    file_without_extention += "\\"

    command = 'C:\\Program Files\\WinRAR\\WinRAR.exe'
    full_command = ["cmd", "/c", command, "x", "-o+", "-y", problem_tar_file, file_without_extention]
    result = subprocess.run(full_command)
    #result = subprocess.run(["cmd", "/c", command, arg, problem_tar_file, file_without_extention])
    #print(str(full_command))

    if result.returncode == 0:
    #    print("Success:")
    #    print(result.stdout)
        return file_without_extention
    else:
        print(str(full_command))
        print("Fail:")
        print(result.stderr)

    return None

def handle_file(domain ,problem_tar_file):   
    folder_name =  unzip_file(problem_tar_file)

    if folder_name is not None:
        # Get the initial state
        with open(os.path.join(folder_name, INIT_STATE_FILE_NAME)) as stats_file:
            init_state = stats_file.readlines()

        init_states[domain].add(str(init_state))
        
        # If this init state was not seen before.
        if not str(init_state) in goals[domain]: 
            # Add it to the list of init states.    
            goals[domain][str(init_state)] = set()
            init_files[domain][str(init_state)] = os.path.join(folder_name, INIT_STATE_FILE_NAME)

        # Get the diffrent possible goals.
        with open(os.path.join(folder_name, HYPES_FILE_NAME)) as stats_file:
            hyps = stats_file.readlines()

        for hype in hyps:
            split_to_atoms = hype.replace("\n", "")
            split_to_atoms = split_to_atoms.replace(", ",",")
            split_to_atoms = split_to_atoms.split(",")
            for atom in split_to_atoms:
                goals[domain][str(init_state)].add(atom)

        # If the domain file was not located.
        if not domain in domain_files:
            domain_file_name = os.path.join(folder_name, DOMAIN_FILE)
            if os.path.exists(domain_file_name) != "":
                domain_files[domain] = domain_file_name                

def handle_domin(domain, domain_path, new_problems_path):
    init_states[domain] = set()
    goals[domain] = {}
    init_files[domain] = {}
    problems[domain] = []


    files_in_directory = [f for f in os.listdir(domain_path)]
    tar_file_reg = ".*tar.bz2"

    # Go through all the files in this domain, 
    # get all the diffrent initial states, 
    # and for each inititial state get all the diffrent hyposis.
    for file in files_in_directory:
        if re.match(tar_file_reg, file):
            handle_file(domain, os.path.join(domain_path, file))
 
    # Generate diffrent muiltple-goal problems, with each intial state.
    for init_state in init_states[domain]:
        create_problems_for_initial_state(domain, init_state, 6)

    # Create the problems' files.
    # Make the domians directory' of it does not exsit.
    domain_new_problem_path = os.path.join(new_problems_path, domain)
    os.makedirs(domain_new_problem_path,exist_ok=True)
    create_problems_java_format(domain_new_problem_path)
    


domains = ["blocks-world"]# "campus" , "campus-noisy", "depots", "driverlog", "dwr", "easy-ipc-grid", 
 #          "easy-ipc-grid-noisy", "ferry"]#, "intrusion-detection", "intrusion-detection-noisy", "kitchen", 
#           "kitchen-noisy", "logistics", "miconic", "rovers", "satellite", "sokoban", "zeno-travel"]
#domains = ["blocks"]

INIT_STATE_FILE_NAME = "template.pddl"
HYPES_FILE_NAME = "hyps.dat"
REAL_HYP_FILE = "real_hyp.dat"
DOMAIN_FILE = "domain.pddl"
OBS_FILE = "obs.dat"


init_states = {}
goals = {}
problems = {}
domain_files = {"blocks-world":  "C:\\Users\\Yifat\\Desktop\\THESIS\\data\\3-atom-goals-2-towers\\problem_files\\domain.pddl",
                "blocks":  "C:\\Users\\Yifat\\Desktop\\THESIS\\data\\3-atom-goals-2-towers\\problem_files\\domain.pddl"}
init_files = {}

if __name__ == "__main__":
    random.seed(14)
    path = os.path.abspath("C:\\Users\\Yifat\\Documents\\GitHub\\OnlineGoalRecognition-DiscreteDomains\\dataset")
    #path = os.path.abspath("C:\\Users\\Yifat\\Documents\\GitHub\\OnlineGoalRecognition-DiscreteDomains\\yifat-experiments\\try")
    new_problems_path = os.path.abspath("C:\\Users\\Yifat\\Documents\\GitHub\\OnlineGoalRecognition-DiscreteDomains\\yifat-experiments\\script-creared")

    for domain in domains:
        domain_path  = os.path.join(path, domain)
        domain_path = os.path.join(domain_path, "100")
        handle_domin(domain, domain_path, new_problems_path)
        print("done: ", domain)
    
    print("fun!")