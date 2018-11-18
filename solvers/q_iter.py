import numpy as np
import itertools

from prettytable import PrettyTable, ALL
from numpy.linalg import norm


class QIter(object):
    def __init__(self, world, beta=0.9):
        self.beta = beta
        self.prev_total = {}
        self.world = world
        self.values = {}
        self.total = {}
        self.typ_max_q = {}
        for action in world.actions:
            self.prev_total[action] = np.full(world.shape, -np.inf)
            self.total[action] = world.total_reward.copy()

        for (k, v) in world.rewards.items():
            self.typ_max_q[k] = v.copy()
            for action in world.actions:
                if action not in self.values:
                    self.values[action] = {}
                self.values[action][k] = v.copy()

        self.max_q = world.total_reward.copy()
        self.policy = np.full(world.shape, None)
        self.iters = 0
        self.find_policy()

    def find_policy(self):
        rows = self.world.shape[0]
        cols = self.world.shape[1]
        for (r, c) in itertools.product(range(rows), range(cols)):
            if self.world.terminal[r, c]:
                self.policy[r, c] = None
                continue

            policy = None
            max_action_val = -np.inf

            for action in self.world.actions:
                if self.total[action][r, c] > max_action_val:
                    max_action_val = self.total[action][r, c]
                    policy = action

            self.policy[r, c] = policy
            self.max_q[r, c] = max_action_val
            for k in self.world.rewards.keys():
                self.typ_max_q[k][r, c] = self.values[policy][k][r, c]

    def update(self):
        self.iters += 1
        rows = self.world.shape[0]
        cols = self.world.shape[1]

        for action in self.world.actions:
            new_vals = {}
            for (typ, _) in self.values[action].items():
                typ_vals = np.zeros(self.world.shape)
                for (r, c) in itertools.product(range(rows), range(cols)):
                    for (r_sp, c_sp) in itertools.product(range(rows), range(cols)):
                        typ_vals[r, c] += self.world.transition_prob(
                            (r, c), action, (r_sp, c_sp)) * self.typ_max_q[typ][r_sp, c_sp]

                    typ_vals[r, c] *= self.beta
                    typ_vals[r, c] += self.world.rewards[typ][r, c]

                new_vals[typ] = typ_vals

            self.values[action] = new_vals

            (self.prev_total[action], self.total[action]) = (
                self.total[action],  np.zeros(self.world.shape))
            for (_, v) in self.values[action].items():
                self.total[action] += v

        # Update policy
        self.find_policy()

    def update_until(self, stop_condition):
        """
        condition is a function
        """
        while not stop_condition(self):
            self.update()

        return self.values

    def solve(self, max_iters=None, threshold=1e-8):
        # We want to use a local iters variable
        # or you get counterintuitive behavior
        iters = 0

        def tolerance(slf):
            nonlocal iters
            if max_iters != None and iters > max_iters:
                return True
            iters += 1
            eval_max = -np.inf
            for action in slf.world.actions:
                eval_max = max(
                    np.max(np.abs(slf.prev_total[action] - slf.total[action])), eval_max)
            return eval_max < threshold
        return self.update_until(tolerance)

    def format_solution(self):
        fmt_str = "Solved problem in %d iterations w/ beta=%f" % (
            self.iters, self.beta)

        table = PrettyTable([])
        table.hrules = ALL
        table.add_column("Reward Type", [*self.world.rewards, "total"])
        for action in self.world.actions:
            table.add_column(
                action, [*self.values[action].values(), self.total[action]])

        fmt_str = "%s\n\nValues:\n%s\n\nMaxQ:\n%s\n\nPolicy:\n%s" % (
            fmt_str, table, self.max_q, self.policy)

        return fmt_str
