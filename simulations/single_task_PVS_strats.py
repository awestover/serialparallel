import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# number of processors
p = 100
# serial implementation work 
k = 5
# parallel implementation work-competitiveness factor (i.e. how many times more work does the parallel implementation cost)
r = 6

# strategy parameters
epsilon = 1
T = p//r # threshold
print(T)
# T = int(0.1 * p/r)
# T = int(p / r**1.5)

# this is not a full strategy, it is a partial strategy
# epsilon is a parameter of this partial strategy
# m is the number of tasks to be scheduled
def pack(epsilon, work_vec, m):
    cur_backlog = max(work_vec)
    num_tasks_packed = 0
    for i in range(p):
        if num_tasks_packed == m:
            return num_tasks_packed
        while (work_vec[i] + k <= epsilon + cur_backlog) and num_tasks_packed < m:
            print(f"packing stuff to {i} which has fill {work_vec[i]} compared to backlog of {cur_backlog}")
            work_vec[i] += k
            num_tasks_packed += 1
    return num_tasks_packed

# T is a parameter of this strategy
# m is the number of tasks to be scheduled
def pure_threshold_schedule_strategy(T, epsilon, work_vec, m):
    num_tasks_packed = pack(epsilon, work_vec, m) # note: this modifies work_vec
    work_vec_idxs = np.argsort(work_vec)

    ct = 0
    cur_rho = 0 
    while num_tasks_packed + ct < m:
        if m - num_tasks_packed >= T:
            print("schedule in serial")
            # schedule all in serial
            work_vec[work_vec_idxs[cur_rho]] += k
            cur_rho = (cur_rho + 1) % p
        else:
            print("schedule in parallel")
            # schedule all in parallel
            left_to_be_consumed = r*k
            while left_to_be_consumed > 0:
                if cur_rho < p-1:
                    # 0, 1, ..., cur_rho is the set of processors that have the smallest amount of work in them
                    delta = work_vec[work_vec_idxs[cur_rho + 1]] - work_vec[work_vec_idxs[cur_rho]]
                    if delta*(cur_rho + 1) < left_to_be_consumed:
                        for i in range(cur_rho):
                            work_vec[work_vec_idxs[i]] += delta
                        left_to_be_consumed -= delta*(cur_rho + 1)
                        cur_rho += 1
                    else: 
                        for i in range(cur_rho):
                            work_vec[work_vec_idxs[i]] += left_to_be_consumed/(cur_rho+1)
                        left_to_be_consumed = 0
                else:
                    for i in range(p):
                        work_vec[work_vec_idxs[i]] += left_to_be_consumed/p
                    left_to_be_consumed = 0
        ct += 1

    return work_vec


n = np.random.randint(2000) + 2000
work_vec = [0 for i in range(p)]
task_start_times = [0 for i in range(n)]

num_generated = 0
prev_generate_time = 0
while num_generated < n:
    will_generate = min(np.random.randint(p), n-num_generated)
    delta_time = np.random.randint(10)
    for i in range(will_generate):
        task_start_times[num_generated + i] = prev_generate_time + delta_time
    num_generated += will_generate
    prev_generate_time += delta_time

T_max = task_start_times[-1] + (n*k)//p + 1 # upper bound (ish) on completion time (if all tasks come at the end it is achieved) 
new_tasks = [0 for i in range(T_max)]
for i in range(n):
    new_tasks[task_start_times[i]] += 1

plt.stem(new_tasks)
plt.show()

next_task = 0
awake_time = 0

fig, ax = plt.subplots()
bars = plt.bar([i for i in range(p)], work_vec, color='r')

def init():
    ax.set_xlim(0, p)
    ax.set_ylim(0, 50)
    return bars

def update(t):
    global next_task, awake_time, work_vec, ani
    if max(work_vec) > 0:
        awake_time += 1
    else:
        if t > task_start_times[-1]:
            plt.close("all")

    cur_m = 0
    while next_task < n and task_start_times[next_task] == t:
        cur_m += 1
        next_task += 1

    work_vec = pure_threshold_schedule_strategy(T, epsilon, work_vec, cur_m)
    for i in range(p):
        work_vec[i] = max(0, work_vec[i] - 1)

    # update bars
    for bar, h in zip(bars, work_vec):
        bar.set_height(h)
    return bars

ani = FuncAnimation(fig, update, frames=[i for i in range(T_max)],
                    init_func=init, blit=True)
plt.show()

