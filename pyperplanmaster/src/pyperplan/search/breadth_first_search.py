#
# This file is part of pyperplan.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

"""
Implements the breadth first search algorithm.
"""

from collections import deque
import logging

from . import searchspace
import os

def breadth_first_search(planning_task):
    """
    Searches for a plan on the given task using breadth first search and
    duplicate detection.

    @param planning_task: The planning task to solve.
    @return: The solution as a list of operators or None if the task is
    unsolvable.
    """
    #FILE_NAME = os.path.abspath("C:\\Users\\Yifat\\Desktop\\THESIS\\bli.txt")
    #with open (FILE_NAME,"w")as file:
    #    file.write("from" + str(planning_task.initial_state))
    
    # counts the number of loops (only for printing)
    iteration = 0
    # fifo-queue storing the nodes which are next to explore
    queue = deque()
    queue.append(searchspace.make_root_node(planning_task.initial_state))
    # set storing the explored nodes, used for duplicate detection
    closed = {frozenset(planning_task.initial_state)}
    while queue:
        iteration += 1
        if iteration % 10000 == 0:
            print("iteration: ", iteration)   
        logging.debug(
            "breadth_first_search: Iteration %d, #unexplored=%d"
            % (iteration, len(queue))
        )
        # get the next node to explore
        node = queue.popleft()
        # exploring the node or if it is a goal node extracting the plan
        if planning_task.goal_reached(node.state):
            logging.info("Goal reached. Start extraction of solution.")
            logging.info("%d Nodes expanded" % iteration)
            return node.extract_solution()
        for operator, successor_state in planning_task.get_successor_states(node.state):
            # duplicate detection
            if frozenset(successor_state) not in closed:
                #with open (FILE_NAME,"a")as file:
                #    file.write("****" + str(successor_state) + "\n")
                queue.append(
                    searchspace.make_child_node(node, operator, successor_state)
                )
                # remember the successor state
                closed.add(frozenset(successor_state))
    #with open (FILE_NAME,"a")as file:
    #    file.write("---------------------------")
    logging.info("No operators left. Task unsolvable.")
    logging.info("%d Nodes expanded" % iteration)
    print("iteration num:", iteration)
    return None
