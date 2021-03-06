from gridworld.test_gridworld import MiniGridworld
from gridworld.q_world import QWorld

TEST_POINTS = 1000


def test_reset():
    underlying = MiniGridworld()
    world = QWorld(underlying)
    terminals = underlying.terminals
    impassable = underlying.impassable

    for _ in range(TEST_POINTS):
        state = world.reset()
        assert(not terminals[state] and not impassable[state])


def test_act():
    world = QWorld(MiniGridworld())

    state = (2, 0)
    nxt = (2, 1)

    (s_sp, rewards, total_reward, terminal) = world.act(state, 'r')

    assert(s_sp == nxt)
    assert(rewards['success'] == 1)
    assert(rewards['fail'] == 0)
    assert(total_reward == 1)
    assert(terminal)

    nxt = (3, 0)
    (s_sp, rewards, total_reward, terminal) = world.act(state, 'd')
    assert(s_sp == nxt)
    assert(rewards['success'] == 0)
    assert(rewards['fail'] == 0)
    assert(total_reward == 0)
    assert(not terminal)
