import os
import sys
import gym
import math
import time
import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple
from itertools import count

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
torch.set_default_tensor_type(torch.DoubleTensor)

sys.path.append('../model')
from dqn_model import DQN

# Load gym environment
sys.path.append('../env')
from gym.envs.registration import register
register(
    id='dqnenv-v0',
    entry_point='env.environment:dqnEnvironment'
)

env = gym.make('dqnenv-v0')

end_num = int(np.load('../processdata/path_num.npy'))

# Parameters
BATCH_SIZE = 16
GAMMA = 0.8
EPS_START = 0.99
EPS_END = 0.05
EPS_DECAY = 300000
TARGET_UPDATE = 10
N_ACTIONS = end_num
N_STATES = 10   

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))

policy_net = DQN(1, N_ACTIONS).to(device)
target_net = DQN(1, N_ACTIONS).to(device)
print(target_net)
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

class ReplayMemory(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        """Saves a transition."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

optimizer = optim.Adam(policy_net.parameters())
memory = ReplayMemory(10000)

steps_done = 0
episode_durations = []

def convertDim(x):
    result = x.unsqueeze(0)
    return result

######################################################################
def select_action(state):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    if sample > eps_threshold:
        with torch.no_grad():
            return policy_net(state).max(1)[1].view(1, 1)
    else:
        return torch.tensor([[random.randrange(N_ACTIONS)]], device=device, dtype=torch.long)

# Training loop

def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)
    batch = Transition(*zip(*transitions))

    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                          batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                                if s is not None])

    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    state_action_values = policy_net(state_batch).gather(1, action_batch)

    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()
    
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch
    loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))
    
    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()

def start_train():
    num_episodes = 400
    # The max step of MAP
    max_steps = 10000000

    print("Conduct training for up to {} episodes...".format(num_episodes))
    for i_episode in range(num_episodes):
        if os.path.exists('../saved_model/dqn_model.pt'):
            target_net.load_state_dict(torch.load('../saved_model/dqn_model.pt'))

        env.reset()
        x = env.reset()
        state = torch.tensor([[x]]).double()
        total_reward = 0
        total_step = 0

        for t in count():
            action = select_action(state)
            new_state, reward, done, steps = env.step(action.item())
            reward = torch.tensor([reward], device=device)

            if not done:
                next_state = torch.tensor([[new_state]]).double()
            else:
                next_state = None
            memory.push(state, action, next_state, reward)

            state = next_state
            optimize_model()

            total_reward = total_reward + reward
            total_step = total_step + steps

            if done:
                episode_durations.append(t + 1)
                if i_episode % 10 == 0: print(">", end ="", flush=True)
                break
            elif total_step > max_steps:
                print('Maximum number of steps {} reached for episode {0} => exit loop'.format(max_steps, i_episode))
                break

        if i_episode % TARGET_UPDATE == 0:
            torch.save(policy_net.state_dict(), '../saved_model/dqn_model.pt')

if __name__ == '__main__':
    try:
        start_train()

        start_state = torch.tensor([[0]]).double()
        current_state = start_state
        step = 0
        target_state = torch.tensor([[end_num - 1]]).double()

        policy_net.load_state_dict(torch.load('../saved_model/dqn_model.pt'))
        next_state = policy_net(current_state).max(1)[1].view(1,1).double()
        print(("\nTraining result for next state: 0 -> {:.0f} -> " + str(end_num)).format(next_state.item()))
    except KeyboardInterrupt:
        print ("\n\nKeyboard interrupt detected => end execution")
        sys.exit(1)

env._close()
