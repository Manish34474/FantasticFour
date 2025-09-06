import time

from model.earth import Earth, FightStatus

from model.agents.agent import Agent, AgentRole
from model.agents.bridge import Bridge
from model.agents.galactus import Galactus
from model.agents.silver_surfer import SilverSurfer
from model.agents.reed_richards import ReedRichards
from model.agents.sue_storm import SueStorm
from model.agents.the_thing import TheThing
from model.agents.human_torch import HumanTorch
from model.agents.headquarter import Headquarter
from model.agents.franklin import Franklin

from model.location import Location

from controller.config.bridge_config import BridgeConfig
from controller.config.galactus_config import GalactusConfig
from controller.config.config import Config

from view.gui import Gui


class Simulator:
    """Class representing a simulator."""

    def __init__(self) -> None:
        """
        Initialise the Simulator object.

        Initialises the simulation step, the Mars environment, and generates the initial population of agents.
        """
        self.__simulation_step = 0
        self.__earth = Earth()
        self.__agents = []
        self.__generate_initial_population()
        self.__is_running = False

        agent_colours = {Galactus: "red", ReedRichards: "blue", SueStorm: "green", TheThing: "black", None: "white", 
                         SilverSurfer: "cyan", HumanTorch: "yellow", Bridge: "magenta", Headquarter: "orange", Franklin: "pink"}
        
        self.__gui = Gui(self.__earth, agent_colours)
        # self.__gui.render()

        self.__ss_intro_step = 100
        self.__gal_intro_step = 500

    def __generate_initial_population(self) -> None:
        """Generate the initial population of agents in the simulation.
        This method creates a set of agents and places them randomly on the Earth Grid.
        The agents include Galactus, Reed Richards, Sue Storm, The Thing, Silver Surfer, Human Torch, and Bridges.
        """

        bridge_locations = [
            Location(5,5), Location(15,5), Location(5,15), Location(15,15)
        ]

        for loc in bridge_locations:
            bridge = Bridge(loc,health = BridgeConfig.initial_bridge_health)
            self.__agents.append(bridge)
            self.__earth.set_agent(bridge, loc)
        

        self.__agents.append(ReedRichards(Location(0, 0)))
        self.__earth.set_agent(ReedRichards(Location(0,0)), Location(0,0))

        self.__agents.append(SueStorm(Location(1,1)))
        self.__earth.set_agent(SueStorm(Location(1,1)),Location(1,1))
        
        self.__agents.append(TheThing(Location(4,4)))
        self.__earth.set_agent(TheThing(Location(4,4)),Location(4,4))
        
        self.__agents.append(HumanTorch(Location(13,13)))
        self.__earth.set_agent(HumanTorch(Location(13,13)),Location(13,13))

        self.__agents.append(Franklin(Location(6,6)))
        self.__earth.set_agent(Franklin(Location(6,6)), Location(6,6))

        self.__agents.append(Headquarter(Location(0,19)))
        self.__earth.set_agent(Headquarter(Location(0,19)),Location(0,19))


    def __find_empty_locations(self, r: int = 0) -> Location:
    
        grid = self.__earth.get_grid()
        n = len(grid) 

        region_size = 2 * r + 1

        for y in range(n):
            for x in range(n):
                ok = True
                for dy in range(region_size):
                    for dx in range(region_size):
                        ny = (y + dy) % n
                        nx = (x + dx) % n
                        if grid[ny][nx] is not None:
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    cx = (x + r) % n
                    cy = (y + r) % n
                    return Location(cx, cy, r)

        return None


    def __add_silver_surfer(self):
        empty_loc = self.__find_empty_locations(r = 1)
        self.__agents.append(SilverSurfer(empty_loc))
        self.__earth.set_agent(SilverSurfer(empty_loc),empty_loc)
    

    def __add_galactus(self):
        import random

        empty_loc = self.__find_empty_locations(r = GalactusConfig.gal_dest_zone)
        if empty_loc is None:
            rand_x = random.randint(0, Config.world_size - 1)
            rand_y = random.randint(0, Config.world_size - 1)
            empty_loc = Location(rand_x, rand_y, GalactusConfig.gal_dest_zone)

        self.__agents.append(Galactus(empty_loc))
        self.__earth.set_agent(Galactus(empty_loc),empty_loc)

    def run(self) -> None:
        """Run the simulation."""
        self.__is_running = True

        state_dict = {agent.name(): agent.get_state(self.__earth) for agent in self.__agents}
        print(state_dict)
        action_dict = {agent.name(): None for agent in self.__agents}

        num_episode = 1
        cum_h_reward = 0
        cum_v_reward = 0
        step = 0

        while self.__is_running:
            h_rw, v_rw = self.__update(state_dict, action_dict)
            cum_h_reward += h_rw
            cum_v_reward += v_rw
            # self.__render()
            step += 1
            if(num_episode % 10 == 0):
                print(f"\r[Ep {num_episode} | step {step}]", end="", flush=True)
            # time.sleep(0.5)

            if step == self.__ss_intro_step:
                self.__add_silver_surfer()
            
            if step == self.__gal_intro_step:
                self.__add_galactus()

            if self.__earth.get_status() == FightStatus.WON or self.__earth.get_status() == FightStatus.LOST:
                for agent in self.__agents:
                    agent.save_q()

                self.__earth.clear()
                self.__agents.clear()
                self.__generate_initial_population()
                state_dict = {agent.name(): agent.get_state(self.__earth) for agent in self.__agents}
                if(num_episode % 10 == 0 or num_episode == 0):
                    print(f"[Ep {num_episode}]: Cumulative Hero R/w = {cum_h_reward}")
                num_episode += 1
                cum_h_reward = 0
                cum_v_reward = 0
                step = 0

                

            if self.__gui.is_closed():
                self.__is_running = False                
            

    def __render(self) -> None:
        """Render the current state of the simulation."""
        self.__gui.render()

    def __update(self, state_dict, action_dict) -> int:
        """Update the simulation state."""
        for agent in self.__agents:

            if agent.get_location() is None:
                continue

            action = agent.pick_action(self.__earth)
            action_dict[agent.name()] = action
            self.__earth.register_action(action)

        h_reward, v_reward = self.__earth.execute_actions()

        for agent in self.__agents:
            if agent.get_location() is None:
                continue

            a_reward = h_reward if agent.get_agent_role() is AgentRole.HERO else v_reward
            new_state = agent.get_state(self.__earth)

            # When silver surfer and galactus are first introduced
            if agent.name() not in state_dict:
                state_dict[agent.name()] = new_state
                continue

            agent.update_q(state_dict[agent.name()], action_dict[agent.name()], a_reward,new_state , self.__earth)
            state_dict[agent.name()] = new_state
            

        self.__simulation_step += 1

        return h_reward, v_reward