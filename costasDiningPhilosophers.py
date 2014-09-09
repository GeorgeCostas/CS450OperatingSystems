# George Costas CS450 IIT
#hw number 4 The dining philosophers
from threading import Thread, Semaphore, Lock, Condition
from collections import deque
from time import sleep
from timeit import Timer
import random, time
import sys
# number of philosophers; index of P_i's left and right forks
#

NUM_PHIL = 0
NUM_MEAL = 0
ANNOUNCE_ACTIONS = False
footman = Semaphore(1);
state = ['thinking'] * NUM_PHIL
mutex = Semaphore(1)

def set_num_phil(input):
    global NUM_PHIL
    NUM_PHIL = input

def set_num_meal(input):
    global NUM_MEAL
    NUM_MEAL = input

def set_state():
    global state
    state = ['thinking'] * NUM_PHIL

def right(i): return i
def left(i): return (i+1) % NUM_PHIL

def test(id, forks):
    if state[id] == 'hungry' and state [left (id)] != 'eating' and state [right (id)] != 'eating':
        state[id] = 'eating'
        forks[id].release()

# Sleep for uniformly random value between 0 and limit.
def pause(id, max_pause):
	sleeptime = random.uniform(0, max_pause) #* (id+1)
	time.sleep(sleeptime)

# Philosopher thinks for <= think_time seconds then becomes hungry.
def think(id, think_time):
	pause(id, think_time)

# Philosopher eats for <= eat_time seconds
def eat(id, times_eaten, eat_time):
	pause(id, eat_time)

# Get fork to left of identified philosopher
def get_left(id, forks):
	forks[left(id)].acquire()

# Get fork to right of identified philosopher
def get_right(id, forks):
	forks[right(id)].acquire()

def get_forks_nohold(id, forks, fork_pause = 1):
    success = None
    while (success == None or False):
        forks[right(id)].acquire()
        pause(id, fork_pause)
        if forks[left(id)].acquire(False):
            forks[right(id)].release()
        else:
            success = True

def get_forks_footman(id, forks, fork_pause = 1):
    footman.acquire() # before philos to prevent the footman from failing
    get_right(id, forks)
    pause(id, fork_pause)
    get_left(id, forks)

def get_forks_asymmetric(id, forks, fork_pause = 1):
    if(id % 2 == 0): #a righty
        get_right(id, forks)
        pause(id, fork_pause)
        get_left(id, forks)
    else: # a lefty
        get_left(id, forks)
        pause(id, fork_pause)
        get_right(id, forks)

def get_forks_tenanbaum(id, forks, action_time):
    mutex.acquire()
    state[id] = 'hungry'
    test(id, forks)
    mutex.release()
    forks[id].acquire

#releases both of the philosophers forks
def drop_forks(id, forks):
	forks[right(id)].release()
	forks[left(id)].release()

def drop_forks_footman(id, forks):
    forks[right(id)].release()
    forks[left(id)].release()
    footman.release()

def drop_forks_tenanbaum(id, forks):
    mutex.acquire()
    state[id] = 'thinking'
    test(right(id), forks)
    test(left(id), forks)
    mutex.release()

def philosopher_nohold(get_forks_nohold, id, forks, action_time = 1, fork_pause = 1):
	times_eaten = 0
	while NUM_MEAL < 0 or times_eaten < NUM_MEAL:
		think(id, action_time)  # think and become hungry
		get_forks_nohold(id, forks, fork_pause)

		times_eaten += 1
		eat(id, times_eaten, action_time)
		drop_forks(id, forks)
	return

def philosopher_footman(get_forks_footman, id, forks, action_time = 1, fork_pause = 1):
    times_eaten = 0
    while NUM_MEAL < 0 or times_eaten < NUM_MEAL:
        think(id, action_time)
        get_forks_footman(id, forks, fork_pause)

        times_eaten += 1
        eat(id, times_eaten, action_time)
        drop_forks_footman(id, forks)
    return

def philosopher_asymmetric(get_forks_asymmetric, id, forks, action_time = 1, fork_pause = 1):
    times_eaten = 0
    while NUM_MEAL < 0 or times_eaten < NUM_MEAL:
        think(id, action_time)
        get_forks_asymmetric(id, forks, fork_pause)

        times_eaten += 1
        eat(id, times_eaten, action_time)
        drop_forks(id, forks)
    return

def philosopher_tenanbaum(get_forks_tenanbaum, id, forks, action_time = 1, fork_pause = 1):
    times_eaten = 0
    while NUM_MEAL < 0 or times_eaten < NUM_MEAL:
        think(id, action_time)
        get_forks_tenanbaum(id, forks, fork_pause)

        times_eaten += 1
        eat(id, times_eaten, action_time)
        drop_forks_tenanbaum(id, forks)
    return

# Params: get_forks: Either get_forks1 or get_forks2; a function
#       that takes arguments (id, forks, fork_pause = 1) and
#       implements a strategy for getting the right and left forks.
#   action_time: max seconds to eat or think
#   fork_pause: max seconds to pause between getting forks
def nohold_run(action_time = 1, fork_pause = 1):
	forks = [Semaphore(1) for i in range(NUM_PHIL)]
	phils = [Thread(target = philosopher_nohold, \
				args = [get_forks_nohold, id, forks, action_time, fork_pause] )
				for id in range(NUM_PHIL) ]
	for phil in phils:
		phil.start()
	for phil in phils:
		phil.join()

def footman_run(action_time = 1, fork_pause = 1):
    forks = [Semaphore(1) for i in range(NUM_PHIL)]
    phils = [Thread(target = philosopher_footman, \
        args = [get_forks_footman, id, forks, action_time, fork_pause] )
        for id in range(NUM_PHIL) ]
    for phil in phils:
        phil.start()
    for phil in phils:
        phil.join()

def asymmetric_run(action_time = 1, fork_pause = 1):
    forks = [Semaphore(1) for i in range(NUM_PHIL)]
    phils = [Thread(target = philosopher_asymmetric, \
        args = [get_forks_asymmetric, id, forks, action_time, fork_pause] )
        for id in range(NUM_PHIL)]
    for phil in phils:
        phil.start()
    for phil in phils:
        phil.join()

def tenanbaum_run(action_time = 1, fork_pause = 1):
    forks = [Semaphore(1) for i in range(NUM_PHIL)]
    phils = [Thread(target= philosopher_tenanbaum, \
        args = [get_forks_tenanbaum, id, forks, action_time, fork_pause] )
        for id in range(NUM_PHIL)]
    for phil in phils:
        phil.start()
    for phil in phils:
        phil.join()

def main(philos, meals):
    set_num_phil(philos)
    set_num_meal(meals)
    set_state()

    print('Setting the table for: {} philosophers, {} meals'.format(NUM_PHIL, NUM_MEAL))

    timer0 = Timer(nohold_run)
    print('no holds solution, time elapsed: {:0.4f}s'.format(timer0.timeit(1)))

    timer1 = Timer(footman_run)
    print('footman solution, time elapsed: {:0.4f}s'.format(timer1.timeit(1)))

    timer2 = Timer(asymmetric_run)
    print('asymmetric solution, time elapsed: {:0.4f}s'.format(timer2.timeit(1)))

    timer3 = Timer(tenanbaum_run)
    print('tenanbaums solution, time elapsed: {:0.4f}s'.format(timer3.timeit(1)))
