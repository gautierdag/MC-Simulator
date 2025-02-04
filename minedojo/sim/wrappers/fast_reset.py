"""
Do fast reset: reset using MC native command `/kill`, instead of waiting for generating new worlds

Side effects:
    1. Changes to the world will not be reset. E.g., if the agent chops lots of trees then calling fast reset
        will not restore those trees.
    2. If you specify agent starting health and food, these specs will only be respected at the first reset
        (i.e., generating a new world) but will not be respected in the following resets (i.e., reset using MC cmds).
        So be careful to use this wrapper if your usages require specific initial health/food.
    3. Statistics/achievements will not be reset. This wrapper will maintain a property `info_prev_reset`. If your
        tasks use stat/achievements to evaluation, please retrieve this property and calculate differences
"""
from __future__ import annotations

import gym
import math
import logging

from ..sim import MineDojoSim
from ...sim.mc_meta.mc import MAX_FOOD, MAX_LIFE
from ..inventory import parse_inventory_item, map_slot_number_to_cmd_slot

logger = logging.getLogger(__name__)


class FastResetWrapper(gym.Wrapper):
    def __init__(
        self,
        env: MineDojoSim,
        random_teleport_range: int | None = 1000,
        clear_ground: bool = True,
        kill_mobs: bool = True,
        random_teleport_agent=True,
        no_daylight_cycle=True,
        custom_commands=None,
        force_slow_reset_interval: int = 0,
    ):
        super().__init__(env=env)
        start_time, start_weather = env.start_time, env.initial_weather
        initial_inventory, start_position = env.initial_inventory, env.start_position
        start_health, start_food = env.start_health, env.start_food
        if start_health != MAX_LIFE or start_food != MAX_FOOD:
            print(
                "Warning! You use non-default values for `start_health` and `start_food`. "
                "However, they will not take effects because `fast_reset = True`. "
                "Consider using `fast_reset = False` instead."
            )
        if random_teleport_range is None:
            random_teleport_range = 200

        self.reset_count = 0
        self.force_slow_reset_interval = force_slow_reset_interval

        self._reset_cmds = ["/kill"]
        self._reset_cmds.extend(
            [f"/time set {start_time or 0}", f'/weather {start_weather or "normal"}']
        )
        if initial_inventory is not None:
            for inventory_item in initial_inventory:
                slot, item_dict = parse_inventory_item(inventory_item)
                self._reset_cmds.append(
                    f'/replaceitem entity @p {map_slot_number_to_cmd_slot(slot)} minecraft:{item_dict["type"]} {item_dict["quantity"]} {item_dict["metadata"]}'
                )
        if start_position is not None:
            self._reset_cmds.append(
                f'/tp {start_position["x"]} {start_position["y"]} {start_position["z"]} {start_position["yaw"]} {start_position["pitch"]}'
            )
        if kill_mobs:
            self._reset_cmds.extend(
                [
                    "/kill @e[type=!player]",
                    f"/time set {start_time or 0}",
                    f"/time set {start_time or 0}",
                ]
            )
        if clear_ground:
            self._reset_cmds.append("/kill @e[type=item]")

        self.random_teleport_range = random_teleport_range
        self.random_teleport_agent = random_teleport_agent

        if no_daylight_cycle:
            self._reset_cmds.append("/gamerule doDaylightCycle false")

        self._custom_commands = custom_commands
        if custom_commands is not None:
            self._reset_cmds.extend(custom_commands)

        self._server_start = False
        self._info_prev_reset = None
        self._previous_start_location = None

    def _calculate_random_offset(self, distance: int = 100):
        """
        Calculates a random position within the given range using the environment's seeded RNG.
        """

        # Sample an angle uniformly from 0 to 2*pi
        angle = self.env._rng.uniform(0, 2 * math.pi)
        # Convert polar coordinates to Cartesian coordinates
        x_offset = int(distance * math.cos(angle))
        y_offset = int(distance * math.sin(angle))
        return x_offset, y_offset

    def reset(self, **kwargs):      
        if not self._server_start or self.reset_count > self.force_slow_reset_interval:
            logger.info(f"server start: {self._server_start} | Force slow reset interval: {self.force_slow_reset_interval}")
            self.reset_count = 1
            self._server_start = True
            obs = self.env.reset(**kwargs)
            if self._custom_commands is not None:
                for cmd in self._custom_commands:
                    obs, _, _, info = self.env.execute_cmd(cmd)
                self._info_prev_reset = self.env.prev_info
            self._previous_x = obs["location_stats"]["pos"][0]
            self._previous_z = obs["location_stats"]["pos"][2]
            logger.info(f"Start Position @ {self._previous_x}, {self._previous_z}")
            return obs
        
        for cmd in self._reset_cmds:
            obs, _, _, info = self.env.execute_cmd(cmd)
        if self.random_teleport_agent and self.random_teleport_range > 0:
            x_offset, z_offset = self._calculate_random_offset(
                self.random_teleport_range
            )
            x = self._previous_x + x_offset
            z = self._previous_z + z_offset

            logger.info(f"Random teleport to {x}, {z} due to offset {x_offset}, {z_offset}")
            cmd = f"/spreadplayers {x} {z} 0 1 false @p"

            # Save the new target position
            self._previous_x = x
            self._previous_z = z

            # Execute the command
            obs, _, _, info = self.env.execute_cmd(cmd)
        self._info_prev_reset = self.env.prev_info
        self.reset_count += 1  
        return obs

    def step(self, action):
        obs, r, d, info = self.env.step(action)

        return obs, r, d, info

    def execute_cmd(self, *args, **kwargs):
        return self.env.execute_cmd(*args, **kwargs)

    def spawn_mobs(self, *args, **kwargs):
        return self.env.spawn_mobs(*args, **kwargs)

    def set_block(self, *args, **kwargs):
        return self.env.set_block(*args, **kwargs)

    def clear_inventory(self, *args, **kwargs):
        return self.env.clear_inventory(*args, **kwargs)

    def set_inventory(self, *args, **kwargs):
        return self.env.set_inventory(*args, **kwargs)

    def teleport_agent(self, *args, **kwargs):
        return self.env.teleport_agent(*args, **kwargs)

    def kill_agent(self, *args, **kwargs):
        return self.env.kill_agent(*args, **kwargs)

    def set_time(self, *args, **kwargs):
        return self.env.set_time(*args, **kwargs)

    def set_weather(self, *args, **kwargs):
        return self.env.set_weather(*args, **kwargs)

    def random_teleport(self, *args, **kwargs):
        return self.env.random_teleport(*args, **kwargs)

    @property
    def prev_obs(self):
        return self.env.prev_obs

    @property
    def prev_info(self):
        return self.env.prev_info

    @property
    def info_prev_reset(self):
        return self._info_prev_reset

    @property
    def prev_action(self):
        return self.env.prev_action

    @property
    def is_terminated(self):
        return self.env.is_terminated
