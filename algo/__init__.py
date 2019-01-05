from __future__ import absolute_import

from .dqn import DQN
from .qlearn import QLearn
from .sarsa import Sarsa


class _LinearDecay():
    """ Linearly Decays epsilon for exploration between a range of episodes"""

    def __init__(self, min_eps, max_eps, total_episodes):
        self.min_eps = min_eps
        self.max_eps = max_eps
        self.total_episodes = total_episodes
        self._curr_episodes = 0
        self._threshold_episodes = 0.8 * total_episodes
        self.eps = max_eps

    def update(self):
        self._curr_episodes += 1
        eps = self.max_eps * (self._threshold_episodes - self._curr_episodes) / self._threshold_episodes
        self.eps = max(self.min_eps, eps)
