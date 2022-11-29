"""
k8s-env基础类
"""
import math
from typing import Optional, Union

import numpy as np

import gym
from gym import logger, spaces
from k8sOperater import k8s_client


class K8sEnv(gym.Env):

    def __init__(self, render_mode: Optional[str] = None):
        nodeList = k8s_client.getK8sClient().CoreV1Api().list_node()
        # 清空 Namespace
        k8s_client.deleteTestPods()
        nodeNum = 0
        for node in nodeList.items:
            nodeNum = nodeNum + 1
        self.nodeNum = nodeNum
        self.action_space = spaces.Discrete(nodeNum)  # 1维离散空间
        self.qValues = np.float32(np.array([0] * nodeNum))
        print(self.qValues)
        self.low = np.array([0, 0, 0, 0, 0, 0] * nodeNum).reshape(nodeNum, 6)
        self.high = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        # self.high = np.array([0, 0, 0, 0, 0, 0])
        # index = 0
        self.action = 0
        self.reward = 0.0
        self.terminated = False
        self.state = np.array([0, 0, 0, 0, 0, 0] * nodeNum)
        # np.array(self.state, dtype=np.float32), reward, terminated

        for node in nodeList.items:
            # print("high[0]="+self.high[0])
            self.high[0] = max(self.high[0], float(node.status.allocatable['cpu']))
            self.high[3] = max(self.high[3], float(node.status.allocatable['cpu']))
            self.high[1] = max(self.high[1], float(node.status.allocatable['memory'][:-2]))
            self.high[4] = max(self.high[4], float(node.status.allocatable['memory'][:-2]))
            self.high[2] = max(self.high[2], float(node.status.allocatable['ephemeral-storage']))
            self.high[5] = max(self.high[5], float(node.status.allocatable['ephemeral-storage']))
        for i in len(self.high):
            while self.high[i] > 9999:
                self.high[i] = self.high[i] / 1024
        self.observation_space = spaces.Box(np.float32(self.low), np.array(self.high * nodeNum).reshape(nodeNum, 6),
                                            shape=(nodeNum, 6))  # 多维连续空间
        k8s_client.createTestNamespace()

        # self.render_mode = render_mode
        # self.renderer = Renderer(self.render_mode, self._render)
        #
        # self.screen_width = 600
        # self.screen_height = 400

    '''
    更新策略网络的Q值,保存的目的是为了直接返回给调度器
    '''

    def updateQvalues(self, qvalues):
        for i in range(len(qvalues)):
            self.qValues[i] = qvalues[i]

    def updateQvaluesByAction(self, action):
        maxValue = 0
        maxIndex = -1
        for i in range(len(self.qValues)):
            if maxValue < self.qValues[i]:
                maxValue = self.qValues[i]
                maxIndex = i
        if 0 < action < self.nodeNum:
            self.qValues[maxIndex] = maxValue + 5

    def getQvalues(self):
        return self.qValues

    def updateDQNArgs(self, request):
        self.reward = request.reward
        print('++++++reward is ' + str(request.reward))
        self.action = request.action
        index = 0
        for nodeMertic in request.nextState:
            self.state[index] = nodeMertic.metric
            index += 1
        if len(request.filterNodes) == 0:
            self.terminated = True

    def step(self, action):
        err_msg = f"{action!r} ({type(action)}) invalid"
        assert self.action_space.contains(action), err_msg
        assert self.state is not None, "Call reset before using step method."
        return np.array(self.state, dtype=np.float32), self.reward, self.terminated, False, {}

    def reset(
            self,
            *,
            seed: Optional[int] = None,
            return_info: bool = False,
            options: Optional[dict] = None,
    ):
        super().reset(seed=seed)
        k8s_client.deleteTestNamespace()
        k8s_client.createTestNamespace()
        return np.array(self.state, dtype=np.float32)
        # Note that if you use custom reset bounds, it may lead to out-of-bound
        # state/observations.
        # low, high = utils.maybe_parse_reset_bounds(
        #     options, -0.05, 0.05  # default low
        # )  # default high
        # self.state = self.np_random.uniform(low=low, high=high, size=(4,))
        # self.steps_beyond_terminated = None
        # self.renderer.reset()
        # self.renderer.render_step()
        # if not return_info:
        #     return np.array(self.state, dtype=np.float32)
        # else:
        #     return np.array(self.state, dtype=np.float32), {}

    # def render(self, mode="human"):
    #     if self.render_mode is not None:
    #         return self.renderer.get_renders()
    #     else:
    #         return self._render(mode)
    #
    # def _render(self, mode="human"):
    #     assert mode in self.metadata["render_modes"]
    #     try:
    #         import pygame
    #         from pygame import gfxdraw
    #     except ImportError:
    #         raise DependencyNotInstalled(
    #             "pygame is not installed, run `pip install gym[classic_control]`"
    #         )
    #
    #     if self.screen is None:
    #         pygame.init()
    #         if mode == "human":
    #             pygame.display.init()
    #             self.screen = pygame.display.set_mode(
    #                 (self.screen_width, self.screen_height)
    #             )
    #         else:  # mode in {"rgb_array", "single_rgb_array"}
    #             self.screen = pygame.Surface((self.screen_width, self.screen_height))
    #     if self.clock is None:
    #         self.clock = pygame.time.Clock()
    #
    #     world_width = self.x_threshold * 2
    #     scale = self.screen_width / world_width
    #     polewidth = 10.0
    #     polelen = scale * (2 * self.length)
    #     cartwidth = 50.0
    #     cartheight = 30.0
    #
    #     if self.state is None:
    #         return None
    #
    #     x = self.state
    #
    #     self.surf = pygame.Surface((self.screen_width, self.screen_height))
    #     self.surf.fill((255, 255, 255))
    #
    #     l, r, t, b = -cartwidth / 2, cartwidth / 2, cartheight / 2, -cartheight / 2
    #     axleoffset = cartheight / 4.0
    #     cartx = x[0] * scale + self.screen_width / 2.0  # MIDDLE OF CART
    #     carty = 100  # TOP OF CART
    #     cart_coords = [(l, b), (l, t), (r, t), (r, b)]
    #     cart_coords = [(c[0] + cartx, c[1] + carty) for c in cart_coords]
    #     gfxdraw.aapolygon(self.surf, cart_coords, (0, 0, 0))
    #     gfxdraw.filled_polygon(self.surf, cart_coords, (0, 0, 0))
    #
    #     l, r, t, b = (
    #         -polewidth / 2,
    #         polewidth / 2,
    #         polelen - polewidth / 2,
    #         -polewidth / 2,
    #     )
    #
    #     pole_coords = []
    #     for coord in [(l, b), (l, t), (r, t), (r, b)]:
    #         coord = pygame.math.Vector2(coord).rotate_rad(-x[2])
    #         coord = (coord[0] + cartx, coord[1] + carty + axleoffset)
    #         pole_coords.append(coord)
    #     gfxdraw.aapolygon(self.surf, pole_coords, (202, 152, 101))
    #     gfxdraw.filled_polygon(self.surf, pole_coords, (202, 152, 101))
    #
    #     gfxdraw.aacircle(
    #         self.surf,
    #         int(cartx),
    #         int(carty + axleoffset),
    #         int(polewidth / 2),
    #         (129, 132, 203),
    #     )
    #     gfxdraw.filled_circle(
    #         self.surf,
    #         int(cartx),
    #         int(carty + axleoffset),
    #         int(polewidth / 2),
    #         (129, 132, 203),
    #     )
    #
    #     gfxdraw.hline(self.surf, 0, self.screen_width, carty, (0, 0, 0))
    #
    #     self.surf = pygame.transform.flip(self.surf, False, True)
    #     self.screen.blit(self.surf, (0, 0))
    #     if mode == "human":
    #         pygame.event.pump()
    #         self.clock.tick(self.metadata["render_fps"])
    #         pygame.display.flip()
    #
    #     elif mode in {"rgb_array", "single_rgb_array"}:
    #         return np.transpose(
    #             np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
    #         )

    # def close(self):
    #     if self.screen is not None:
    #         import pygame
    #
    #         pygame.display.quit()
    #         pygame.quit()
    #         self.isopen = False


# if __name__ == '__main__':

    # list = []
    # list.append(0)
    # print(list)
    # nextState = np.array([0, 0, 0, 0, 0, 0] * 3).reshape(3, 6)
    # test = [0, 0, 0, 0, 0]
    # print(nextState)
# nodeList = k8s_client.getK8sClient().CoreV1Api().list_node()
# 清空 Namespace

# k8s_client.deleteTestPods()
# nodeNum = 0
# for node in nodeList.items:
#   print(float(node.status.allocatable['cpu']))
# nodeNum = nodeNum + 1
# print(nodeNum)
