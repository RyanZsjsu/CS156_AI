
"""Implement Agents and Environments (Chapters 1-2).

The class hierarchies are as follows:

Object ## A physical object that can exist in an environment
    Agent
        Wumpus
        RandomAgent
        ReflexVacuumAgent
        ...
    Dirt
    Wall
    ...
    
Environment ## An environment holds objects, runs simulations
    XYEnvironment
        VacuumEnvironment
      

"""

from utils import *
import random, copy

#______________________________________________________________________________



class Object:
    """This represents any physical object that can appear in an Environment.
    You subclass Object to get the objects you want.  Each object can have a
    .__name__  slot (used for output only)."""
    def __repr__(self):
        return '<%s>' % getattr(self, '__name__', self.__class__.__name__)

    def is_alive(self):
        """Objects that are 'alive' should return true."""
        return hasattr(self, 'alive') and self.alive

    def display(self, canvas, x, y, width, height):
        """Display an image of this Object on the canvas."""
        pass

class Agent(Object):
    """An Agent is a subclass of Object with one required slot,
    .program, which should hold a function that takes one argument, the
    percept, and returns an action. (What counts as a percept or action
    will depend on the specific environment in which the agent exists.) 
    Note that 'program' is a slot, not a method.  If it were a method,
    then the program could 'cheat' and look at aspects of the agent.
    It's not supposed to do that: the program can only look at the
    percepts.  An agent program that needs a model of the world (and of
    the agent itself) will have to build and maintain its own model.
    There is an optional slots, .performance, which is a number giving
    the performance measure of the agent in its environment."""

    def __init__(self):
        def program(percept):
            return raw_input('Percept=%s; action? ' % percept)
        self.program = program
        self.alive = True

def TraceAgent(agent):
    """Wrap the agent's program to print its input and output. This will let
    you see what the agent is doing in the environment."""
    old_program = agent.program
    def new_program(percept):
        action = old_program(percept)
        print '%s perceives %s and does %s' % (agent, percept, action)
        #print(agent.performance)
        return action
    agent.program = new_program

    return agent


#______________________________________________________________________________

class TableDrivenAgent(Agent):
    """This agent selects an action based on the percept sequence.
    It is practical only for tiny domains.
    To customize it you provide a table to the constructor. [Fig. 2.7]"""
    
    def __init__(self, table):
        "Supply as table a dictionary of all {percept_sequence:action} pairs."
        ## The agent program could in principle be a function, but because
        ## it needs to store state, we make it a callable instance of a class.
        Agent.__init__(self)
        percepts = []
        def program(percept):
            percepts.append(percept)
            action = table.get(tuple(percepts))
            return action
        self.program = program


# class RandomAgent(Agent):
#     "An agent that chooses an action at random, ignoring all percepts."
#     def __init__(self, actions):
#         Agent.__init__(self)
#         self.program = lambda percept: random.choice(actions)

# def RandomVacuumAgent():
#     "Randomly choose one of the actions from the vaccum environment."
#     return RandomAgent(['Right', 'Left', 'Suck', 'NoOp'])


#______________________________________________________________________________






class ModelBasedVacuumAgent(Agent):
    "An agent that keeps track of what locations are clean or dirty."
    def __init__(self):
        Agent.__init__(self)
        model = {loc_A: None, loc_B: None}
        def program((location, status)):
            "Same as ReflexVacuumAgent, except if everything is clean, do NoOp"
            model[location] = status ## Update the model here
            if model[loc_A] == model[loc_B] == 'Clean': return 'NoOp'
            elif status == 'Dirty': return 'Suck'
            elif location == loc_A: return 'Right'
            elif location == loc_B: return 'Left'
        self.program = program
        
#______________________________________________________________________________

class Environment:
    """Abstract class representing an Environment.  'Real' Environment classes
    inherit from this. Your Environment will typically need to implement:
        percept:           Define the percept that an agent sees.
        execute_action:    Define the effects of executing an action.
                           Also update the agent.performance slot.
    The environment keeps a list of .objects and .agents (which is a subset
    of .objects). Each agent has a .performance slot, initialized to 0.
    Each object has a .location slot, even though some environments may not
    need this."""

    def __init__(self,):
        self.objects = []; self.agents = []

    object_classes = [] ## List of classes that can go into environment

    def percept(self, agent):
	"Return the percept that the agent sees at this point. Override this."
        abstract

    def execute_action(self, agent, action):
        "Change the world to reflect this action. Override this."
        abstract

    def default_location(self, object):
	"Default location to place a new object with unspecified location."
        return None

    def exogenous_change(self):
	"If there is spontaneous change in the world, override this."
	pass

    def is_done(self):
        "By default, we're done when we can't find a live agent."
        for agent in self.agents:
            if agent.is_alive(): return False
        return True
    

    def step(self):
	"""Run the environment for one time step. If the
	actions and exogenous changes are independent, this method will
	do.  If there are interactions between them, you'll need to
	override this method."""
	if not self.is_done():
            actions = [agent.program(self.percept(agent))
                       for agent in self.agents]
            for (agent, action) in zip(self.agents, actions):
		self.execute_action(agent, action)
            self.exogenous_change()

    def run(self, steps=1000):
	"""Run the Environment for given number of time steps."""
	for step in range(steps):
            if self.is_done(): 
            	return
            self.step()
    

    def add_object(self, object, location=None):
	"""Add an object to the environment, setting its location. Also keep
	track of objects that are agents.  Shouldn't need to override this."""
	object.location = location or self.default_location(object)
	self.objects.append(object)
	if isinstance(object, Agent):
            object.performance = 0
            self.agents.append(object)
	return self
    


#______________________________________________________________________________
## Vacuum environment 

class TrivialVacuumEnvironment(Environment): #PROFESSOR SAID TO USE THIS ENVIRONMENT FOR ASSIGNMENT
    """This environment has two locations, A and B. Each can be Dirty or Clean.
    The agent perceives its location and the location's status. This serves as
    an example of how to implement a simple Environment."""

    countOfMoves = 0

    def __init__(self):
        Environment.__init__(self)
        self.status = {loc_A:random.choice(['Clean', 'Dirty']),
                       loc_B:random.choice(['Clean', 'Dirty'])}
        
    def percept(self, agent):
        "Returns the agent's location, and the location status (Dirty/Clean)."
        return (agent.location, self.status[agent.location]) #here we are returning a tuple)
        #this returns something like ((1,0), Dirty)
    def execute_action(self, agent, action):
        """Change agent's location and/or location's status; track performance.
        Score 10 for each dirt cleaned; -1 for each move."""

        if action == 'Right':
            agent.location = loc_B
            agent.performance -= 1
            
            print("Agent's current performance:%s" % agent.performance)
        elif action == 'Left':
            agent.location = loc_A
            agent.performance -= 1
            
            print(agent.performance)
        elif action == 'Suck':
            if self.status[agent.location] == 'Dirty':
                agent.performance += 10
                print(agent.performance)
            self.status[agent.location] = 'Clean'

    def default_location(self, object):
        "Agents start in either location at random."
        return random.choice([loc_A, loc_B])


    #def displayMetrics():


class Dirt(Object): pass
class Wall(Object): pass

def interpret_input(percept):
        location, spotStatus = percept
        if location == loc_A and spotStatus =='Clean':
            return '1' #1 means 'RIGHT'
        elif location == loc_A and spotStatus =='Dirty':
            return '2' #2 means 'SUCK'
        elif location == loc_B and spotStatus == 'Clean':
            return '3' #means 'LEFT'
        else:
            return '4' #means 'SUCK'

class SimpleReflexAgent(Agent): #USE THIS AGENt FOR SIMPLE RELFEX
    """This agent takes action based solely on the percept. [Fig. 2.13]"""
    #This Simple Reflex Agent will never stop because it only goes off of percept 
    #and has no memory of previous room being clean or not.
    
    def __init__(self, rules, interpret_input):
        Agent.__init__(self)
        def program(percept): #percept function from vacuumenvironemtn "Returns the agent's location, and the location status (Dirty/Clean)."
            state = interpret_input(percept) #(loc_A, Dirty) tuple or (loc_B, CLean)
            action = rule_match(state, rules)
            #action = rule.action
            return action
        self.program = program
        
        
    # def interpret_input(percept):
    #     location, spotStatus = percept
    #     if location == loc_A and spotStatus =='Clean':
    #     	return '1' #1 means 'RIGHT'
    #     elif location == loc_A and spotStatus =='Dirty':
    #    		return '2' #2 means 'SUCK'
    #    	elif location == loc_B and spotStatus == 'Clean':
    #    		return '3' #means 'LEFT'
    #    	else:
    #    		return '4' #means 'SUCK'



    def rule_match(state, rules):
		for rule in rules:
			if state == 1:
				return 'Right'
			elif state == 2:
				return 'Suck'
			elif state == 3:
				return 'Left'
			else:
				return 'Suck'

		

#
	


	#def interpret_input(percept, rules):
		#location, spotStatus = percept
		#for rule in rules:
		#	if location == (0,0) and 


loc_A, loc_B = (0, 0), (1, 0) # The two locations for the Vacuum world

class ReflexVacuumAgent(Agent): 
    "A reflex agent for the two-state vacuum environment. [Fig. 2.8]"

    def __init__(self):
        Agent.__init__(self)
        def program((location, status)):
            if status == 'Dirty': return 'Suck'
            elif location == loc_A: return 'Right'
            elif location == loc_B: return 'Left'
        self.program = program

    
#______________________________________________________________________________

def compare_agents(EnvFactory, AgentFactories, n=10, steps=1000):
    """See how well each of several agents do in n instances of an environment.
    Pass in a factory (constructor) for environments, and several for agents.
    Create n instances of the environment, and run each agent in copies of 
    each one for steps. Return a list of (agent, average-score) tuples."""
    envs = [EnvFactory() for i in range(n)]
    return [(A, test_agent(A, steps, copy.deepcopy(envs))) 
            for A in AgentFactories]

def test_agent(AgentFactory, steps, envs):
    "Return the mean score of running an agent in each of the envs, for steps"
    total = 0
    for env in envs:
        agent = AgentFactory()
        env.add_object(agent)
        env.run(steps)
        total += agent.performance
    return float(total)/len(envs)

#______________________________________________________________________________

_docex = """
a = ReflexVacuumAgent()
a.program
a.program((loc_A, 'Clean')) ==> 'Right'
a.program((loc_B, 'Clean')) ==> 'Left'
a.program((loc_A, 'Dirty')) ==> 'Suck'
a.program((loc_A, 'Dirty')) ==> 'Suck'

e = TrivialVacuumEnvironment()
e.add_object(TraceAgent(ModelBasedVacuumAgent()))
e.run(5)

## Environments, and some agents, are randomized, so the best we can
## give is a range of expected scores.  If this test fails, it does
## not necessarily mean something is wrong.
envs = [TrivialVacuumEnvironment() for i in range(100)]
def testv(A): return test_agent(A, 4, copy.deepcopy(envs)) 
testv(ModelBasedVacuumAgent)
(7 < _ < 11) ==> True
testv(ReflexVacuumAgent)
(5 < _ < 9) ==> True
testv(TableDrivenVacuumAgent)
(2 < _ < 6) ==> True
testv(RandomVacuumAgent)
(0.5 < _ < 3) ==> True
"""

#The rules are supposed to be a set of condition-action rules, said in book


print("**************************START OF PROGRAM*****************************")
print("AGENTS PERFORMANCE IS MEASURED BY POINTS: +10 Points for each dirty spot cleaned, -1 for each movement")
print("\n")

e = TrivialVacuumEnvironment()
e.add_object(TraceAgent(ModelBasedVacuumAgent()))
#we want SimpleReflexAgent, not ModelBasedVacuumAgent
e.run(5)

rules = ['Left', 'Right', 'Suck']
e2 = TrivialVacuumEnvironment()

#e2.add_object(TraceAgent(SimpleReflexAgent(rules, interpret_input())))
#e2.run(7)


e3 = TrivialVacuumEnvironment()
e3.add_object(TraceAgent(ReflexVacuumAgent()))
e3.run(20)

print("\n***********************END OF PROGRAM*******************************")

