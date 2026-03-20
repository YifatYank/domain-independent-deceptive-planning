import random
import os
import re
import subprocess
import shutil
import sys
from pyperplanmaster.src.pyperplan.planner import _parse, _ground, SEARCHES, search_plan


TEMPLATE_FILE_NAME = "template.pddl"
HYPES_FILE_NAME = "hyps.dat"
REAL_HYP_FILE = "real_hyp.dat"
DOMAIN_FILE_NAME = "domain.pddl"
OBS_FILE = "obs.dat"


class recognition_problem:
    def __init__(self):
        # The name of the pddl file the problem will be written to.
        self.name = None
        # Path for the domain file of the problem.
        self.domain_file_path = None
        # Usesd for creating the problem's pddl file. 
        self.template = None 
        # The recognition problem properties.
        self.init_state = None
        self.hypes = None
        self.real_hype = None

class planning_domain:
    def __init__(self):
        self.name = None
        self.domain_file_path = None
        self.domain_path = None
        self.planning_problems = []
        self.recognition_problems = []


def get_plan_to_goal(problem, temp_path):
    real_hype = str(problem.real_hype)
    real_hype = real_hype[1:-1]
    real_hype = real_hype.replace("'","")
    real_hype = real_hype.replace(", "," ")

    template = problem.template
    
    for i in range(len(template)):
        if "HYPOTHESIS" in  template[i]:
            template[i] = template[i].replace("<HYPOTHESIS>",real_hype)
    problem_file = os.path.join(temp_path, "temp_file.pddl")
    
    with open(problem_file , 'w') as f:
        f.writelines(template)

    plan_ops = search_plan(problem.domain_file_path, problem_file, SEARCHES["ids"], None)

    return plan_ops


def make_recognition_problem_template(file):
    with open (file) as f :
        file_content = f.readlines()

    template_lines = []

    line_num = 0
    for line_num in range(len(file_content)):
        if file_content[line_num].find("goal") == -1:
            template_lines.append(file_content[line_num])
        else:
            break
    
    for line_num2 in range(line_num, len(file_content)):
        modified_line = file_content[line_num2].upper()        
        modified_line  = re.sub("\([^()]*\)", "", modified_line)        
        modified_line = re.sub("  +", " ", modified_line)
        modified_line = modified_line.replace("AND", "AND <HYPOTHESIS>")

        template_lines.append(modified_line)
    return template_lines


def choose_combined_goal(atom_goals):
    lst = list(atom_goals)
    #goals_num = random.randint(2, len(lst))
    goals_num = 2
    combined_goal = []
    
    for i in range(goals_num):
        choise = random.randint(0, len(lst) -1)
        combined_goal.extend(lst[choise])
        lst.pop(choise)

    return combined_goal


def make_hypes(task, hypes_num, min_facts_num, max_fact_num):
    hype_set = []
    lst = list(task.goals)

    for i in range(hypes_num):
        curr_hype = []
        facts_num = random.randint(min_facts_num, max_fact_num)
        for j in range(facts_num):
            if len(lst) == 0:
                break
            choise = random.randint(0, len(lst) -1)
            curr_hype.append(lst[choise])
            lst.pop(choise)
        hype_set.append(curr_hype)
        if len(lst) == 0:
            break
    return hype_set


def make_muiltple_goals_recognition_problem(planning_problem, domain, number_of_problems):
    task = _ground(planning_problem[0])
    template = make_recognition_problem_template(planning_problem[1])
    problems = []

    for i in range(number_of_problems):
        rec_problem = recognition_problem()
        rec_problem.domain_file_path = domain.domain_file_path
        rec_problem.name = task.name + "-" + str(i+1)
        rec_problem.init_state = task.initial_state
        rec_problem.hypes = make_hypes(task, 5, 2,2)
        rec_problem.real_hype = choose_combined_goal(rec_problem.hypes)
        rec_problem.template = template
        problems.append(rec_problem)

    return problems

def hype_print_format(hype):
    print_hype = str(hype)
    print_hype = print_hype[1:-1]
    print_hype = print_hype.replace("'","")
    print_hype = print_hype.replace(", ",",")

    return print_hype

def save_recognition_problems_java_format(problems, domain_new_problem_path):
    index = 0

    for rec_problem in problems:
        # First check if there is a plan from the initial state to the goal.
        # (Mabey the goal that was randomly built is unreachable).
        pln = get_plan_to_goal(rec_problem, "C:\\Users\\Yifat\\Desktop\\THESIS")        
        if pln is None:
            # Dont create a zip file for this problem.
            continue


        problem_path = os.path.join(domain_new_problem_path, rec_problem.name)
        os.makedirs(problem_path)

        # Copy the domain file
        shutil.copy(rec_problem.domain_file_path, os.path.join(problem_path, DOMAIN_FILE_NAME))
        
        # Create the template file.
        with open(os.path.join(problem_path, TEMPLATE_FILE_NAME), "w") as f:
            f.writelines(rec_problem.template)
        
        with open(os.path.join(problem_path, HYPES_FILE_NAME), "w") as f:
            for hype in rec_problem.hypes: 
                f.writelines(hype_print_format(hype) + "\n")

        with open(os.path.join(problem_path, REAL_HYP_FILE), "w") as f:
            f.writelines(hype_print_format(rec_problem.real_hype))

        with open(os.path.join(problem_path, OBS_FILE), "w") as f:
            for action in pln:
                f.writelines(str(action.name) + "\n")

        # If all the files were created:
        if (os.path.exists(os.path.join(problem_path, DOMAIN_FILE_NAME)) and
            os.path.exists(os.path.join(problem_path, TEMPLATE_FILE_NAME)) and
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
        

def make_recognition_problems_for_domain(domain):
    for problem in domain.planning_problems:
        domain.recognition_problems.extend(make_muiltple_goals_recognition_problem(problem, domain,2))
    

def get_planning_problems(domain):
    files_in_directory = [f for f in os.listdir(domain.domain_path)]

    # Get all the planning problems in this domian.
    for file in files_in_directory:
        if file != DOMAIN_FILE_NAME:
            # Get the problem file's name, paese the problem, and save it.
            file_path = os.path.join(domain.domain_path, file)
            problem = _parse(domain.domain_file_path, file_path)
            domain.planning_problems.append((problem, file_path))


def handle_domain(domain_name, domain_path, new_problems_path):
    domain = planning_domain()
    domain.name = domain_name
    domain.domain_file_path = os.path.join(domain_path, DOMAIN_FILE_NAME)
    domain.domain_path = domain_path
    
    get_planning_problems(domain)
    make_recognition_problems_for_domain(domain)
    save_recognition_problems_java_format(domain.recognition_problems, new_problems_path)

    return domain


def hadle_single_file(file_name, prob_num, target_path):
    if file_name == DOMAIN_FILE_NAME:
        return
    
    # Load the planning problem from the file. 
    planning_problem = _parse(DOMAIN_FILE_NAME, file_name)

    # Make a recognition problem from the file.
    task = _ground(planning_problem)
    template = make_recognition_problem_template(file_name)
    problems = []

    for i in range(prob_num):
        rec_problem = recognition_problem()
        rec_problem.domain_file_path = DOMAIN_FILE_NAME
        rec_problem.name = task.name + "-" + str(i+1)
        rec_problem.init_state = task.initial_state
        rec_problem.hypes = make_hypes(task, 5, 2,2)
        rec_problem.real_hype = choose_combined_goal(rec_problem.hypes)
        rec_problem.template = template
        problems.append(rec_problem)

    # Save the recognition problens that were created.
    save_recognition_problems_java_format(problems, target_path)
    print("done!")


def main1():
    args = sys.argv[1:]
    if len(args) < 2:
        print("Script usage:")
        print("make_problem_from_pddl.py <planning_problem_file.pddl> <path_to_create_new_problems> <number_of_problems_to_create>")
        return

    file_name = args[0]
    target_path = args[1]
    num_prob = 1
    
    if len(args) > 2:
        num_prob = args[2]
    
    hadle_single_file(file_name, num_prob, target_path)


def main():
    random.seed(10)
    path = os.path.abspath("C:\\Users\\Yifat\\Documents\\GitHub\\classical-domains\\yifat-experiments")
    new_problems_path = os.path.abspath("C:\\Users\\Yifat\\Documents\\GitHub\\goal-recognition-muiltiple-goals-experiments\\new_experiments")
    domains = ["blocks"]

    for domain_name in domains:
        domain_path  = os.path.join(path, domain_name)
        domain = handle_domain(domain_name, domain_path, new_problems_path)
        print("done: ", domain_name)
    
    print("fun!")

if __name__ == "__main__":
    main1()