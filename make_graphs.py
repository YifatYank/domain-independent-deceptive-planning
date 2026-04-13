import sys
import matplotlib.pyplot as plt
import numpy as np

def parse_observation(observations):
    obs = [x.strip().replace('[', '').replace(']','') for x in observations.split(',')]
    if obs[-1] == "":
        obs = obs[:-1]
    return obs

def parse_data(data):
    dat = [[float(r) for r in x.strip().split(' ')] for x in data]
    return dat 

if __name__ == "__main__":
    stats_file_name = sys.argv[1]
    data = []

    with open(stats_file_name) as stats_file:
        data = stats_file.readlines()
    
    real_goal = data[0].strip()

    observations = data[1]
    observations = parse_observation(observations)
    
    goals = data[2]
    goals = parse_observation(goals)
    
    stats = data[3:]
    stats = parse_data(stats)
    #stats = np.array(stats)

    x = [i for i in range (1, len(observations) + 1)]
    # plt.plot(stats)
    for stat_index in reversed(range(len(stats))):
        plt.ylim = (0,1)
        plt.plot(x, stats[stat_index], label = goals[stat_index])
        
    plt.legend()
    plt.rc('font', size=12)
    plt.title("Real Goal:" + real_goal, fontdict = {'size':20})
    plt.xticks(x,labels=observations, fontdict = {'size':12})
    plt.tight_layout()
    plt.show()

