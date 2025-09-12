import time
import json
import csv
import os
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

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
    """Class representing a simulator with enhanced metrics tracking."""

    def __init__(self, num_episodes=100, log_dir="logs", plot_dir="plots", gui_flag: bool = False) -> None:
        """
        Initialise the Simulator object.

        Initialises the simulation step, the Mars environment, and generates the initial population of agents.
        """
        self.__simulation_step = 0
        self.__earth = Earth()
        self.__agents = []
        self.__generate_initial_population()
        self.__is_running = False

        agent_colours = {Galactus: "red", ReedRichards: "blue", SueStorm: "green", 
                         TheThing: "black", None: "white", SilverSurfer: "cyan", 
                         HumanTorch: "yellow", Bridge: "magenta", Headquarter: "orange", 
                         Franklin: "pink"}
        
        self.__gui_flag = gui_flag

        self.__gui = Gui(self.__earth, agent_colours) if self.__gui_flag else None

        self.__ss_intro_step = 5
        self.__gal_intro_step = 10
        
        # Metrics tracking
        self.num_episodes = num_episodes
        self.current_episode = 0
        self.metrics = {
            'episode_rewards': [],
            'episode_lengths': [],
            'win_status': [],  # 1 for win, 0 for loss
            'hero_rewards': [],
            'villain_rewards': [],
            'timestep_rewards': []  # For detailed per-timestep tracking
        }
        
        # Setup directories
        self.log_dir = Path(log_dir)
        self.plot_dir = Path(plot_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.plot_dir.mkdir(exist_ok=True)
        
        # Create unique run identifier
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize logging
        self._init_logging()

    def _init_logging(self):
        """Initialize logging files."""
        # CSV log file
        self.csv_log_path = self.log_dir / f"metrics_{self.run_id}.csv"
        with open(self.csv_log_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['episode', 'reward', 'length', 'win_status', 
                            'avg_hero_reward', 'avg_villain_reward'])
        
        # JSON log file for detailed metrics
        self.json_log_path = self.log_dir / f"detailed_metrics_{self.run_id}.json"
        
        # Episode-level log
        self.episode_log_path = self.log_dir / f"episode_log_{self.run_id}.txt"
        with open(self.episode_log_path, 'w') as f:
            f.write(f"Simulation Run: {self.run_id}\n")
            f.write(f"Start Time: {datetime.now()}\n")
            f.write("=" * 50 + "\n\n")

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

    def _log_episode_summary(self, episode, episode_reward, episode_length, win_status, 
                            hero_reward, villain_reward):
        """Log summary of an episode."""
        # CSV logging
        with open(self.csv_log_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([episode, episode_reward, episode_length, win_status, 
                            hero_reward, villain_reward])
        
        # Text logging
        with open(self.episode_log_path, 'a') as f:
            status = "WON" if win_status == 1 else "LOST"
            f.write(f"Episode {episode}: {status} | Length: {episode_length} | "
                   f"Reward: {episode_reward:.2f} | "
                   f"Hero R: {hero_reward:.2f} | Villain R: {villain_reward:.2f}\n")
        
        # JSON logging (update after each episode)
        self._update_json_log()

    def _update_json_log(self):
        """Update the JSON log with current metrics."""
        metrics_data = {
            'run_id': self.run_id,
            'total_episodes': self.current_episode,
            'avg_reward': np.mean(self.metrics['episode_rewards']) if self.metrics['episode_rewards'] else 0,
            'avg_episode_length': np.mean(self.metrics['episode_lengths']) if self.metrics['episode_lengths'] else 0,
            'win_rate': np.mean(self.metrics['win_status']) if self.metrics['win_status'] else 0,
            'avg_hero_reward': np.mean(self.metrics['hero_rewards']) if self.metrics['hero_rewards'] else 0,
            'avg_villain_reward': np.mean(self.metrics['villain_rewards']) if self.metrics['villain_rewards'] else 0,
            'episode_details': [
                {
                    'episode': i+1,
                    'reward': self.metrics['episode_rewards'][i],
                    'length': self.metrics['episode_lengths'][i],
                    'win_status': self.metrics['win_status'][i],
                    'hero_reward': self.metrics['hero_rewards'][i],
                    'villain_reward': self.metrics['villain_rewards'][i]
                }
                for i in range(len(self.metrics['episode_rewards']))
            ]
        }
        
        with open(self.json_log_path, 'w') as f:
            json.dump(metrics_data, f, indent=2)

    def _plot_metrics(self):
        """Create and save plots of the collected metrics."""
        episodes = list(range(1, len(self.metrics['episode_rewards']) + 1))
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Simulation Metrics - Run {self.run_id}', fontsize=16)
        
        # Plot 1: Reward over episodes
        ax1.plot(episodes, self.metrics['episode_rewards'], 'b-', label='Total Reward')
        ax1.plot(episodes, self.metrics['hero_rewards'], 'g-', label='Hero Reward')
        ax1.plot(episodes, self.metrics['villain_rewards'], 'r-', label='Villain Reward')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Reward')
        ax1.set_title('Reward per Episode')
        ax1.legend()
        ax1.grid(True)
        
        # Plot 2: Episode length
        ax2.plot(episodes, self.metrics['episode_lengths'], 'purple')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Length (steps)')
        ax2.set_title('Episode Length')
        ax2.grid(True)
        
        # Plot 3: Win rate (moving average)
        window_size = max(1, len(episodes) // 10)
        win_rates = [np.mean(self.metrics['win_status'][max(0, i-window_size):i+1]) 
                    for i in range(len(episodes))]
        ax3.plot(episodes, win_rates, 'orange')
        ax3.set_xlabel('Episode')
        ax3.set_ylabel('Win Rate')
        ax3.set_title(f'Win Rate (Moving Avg, window={window_size})')
        ax3.set_ylim(0, 1)
        ax3.grid(True)
        
        # Plot 4: Cumulative reward
        cumulative_rewards = np.cumsum(self.metrics['episode_rewards'])
        ax4.plot(episodes, cumulative_rewards, 'b-')
        ax4.set_xlabel('Episode')
        ax4.set_ylabel('Cumulative Reward')
        ax4.set_title('Cumulative Total Reward')
        ax4.grid(True)
        
        plt.tight_layout()
        plt.savefig(self.plot_dir / f'metrics_{self.run_id}.png')
        plt.close()
        
        # Additional plot: Reward distribution
        plt.figure(figsize=(10, 6))
        plt.hist(self.metrics['episode_rewards'], bins=20, alpha=0.7, edgecolor='black')
        plt.xlabel('Reward')
        plt.ylabel('Frequency')
        plt.title('Distribution of Episode Rewards')
        plt.grid(True, alpha=0.3)
        plt.savefig(self.plot_dir / f'reward_distribution_{self.run_id}.png')
        plt.close()

    def run(self) -> None:
        """Run the simulation for multiple episodes with metrics tracking."""
        self.__is_running = True

        # Initial setup
        state_dict = {agent.name(): agent.get_state(self.__earth) for agent in self.__agents}
        action_dict = {agent.name(): None for agent in self.__agents}

        # Episode loop
        for episode in range(self.num_episodes):
            self.current_episode = episode + 1
            print(f"\nStarting Episode {self.current_episode}/{self.num_episodes}")
            
            # Reset episode metrics
            episode_reward = 0
            episode_hero_reward = 0
            episode_villain_reward = 0
            step = 0
            
            # Episode simulation loop
            while self.__is_running:
                h_rw, v_rw = self.__update(state_dict, action_dict)
                episode_hero_reward += h_rw
                episode_villain_reward += v_rw
                episode_reward = episode_hero_reward - episode_villain_reward
                
                step += 1

                if self.__gui_flag:
                    self.__render()
                    # time.sleep(0.5)
                
                # Add Silver Surfer and Galactus at specified steps
                if step == self.__ss_intro_step:
                    self.__add_silver_surfer()
                
                if step == self.__gal_intro_step:
                    self.__add_galactus()

                # Check for episode termination
                status = self.__earth.get_status()
                if status in [FightStatus.WON, FightStatus.LOST]:
                    # Save Q-tables and record metrics
                    for agent in self.__agents:
                        agent.save_q()
                    
                    # Record episode metrics
                    win_status = 1 if status == FightStatus.WON else 0
                    self.metrics['episode_rewards'].append(episode_reward)
                    self.metrics['episode_lengths'].append(step)
                    self.metrics['win_status'].append(win_status)
                    self.metrics['hero_rewards'].append(episode_hero_reward)
                    self.metrics['villain_rewards'].append(episode_villain_reward)
                    
                    # Log episode summary
                    self._log_episode_summary(
                        self.current_episode, episode_reward, step, win_status,
                        episode_hero_reward, episode_villain_reward
                    )
                    
                    # Plot metrics periodically
                    if self.current_episode % 10 == 0:
                        self._plot_metrics()
                    
                    # Reset for next episode
                    self.__earth.clear()
                    self.__agents.clear()
                    self.__generate_initial_population()
                    state_dict = {agent.name(): agent.get_state(self.__earth) for agent in self.__agents}
                    
                    print(f"Episode {self.current_episode}: {'WON' if win_status else 'LOST'} "
                          f"in {step} steps, Reward: {episode_reward:.2f}")
                    break
                
                # Check for GUI close
                if self.__gui_flag and self.__gui.is_closed():
                    self.__is_running = False
                    break
            
            if not self.__is_running:
                break
        
        # Final plots and summary
        self._plot_metrics()
        self._print_final_summary()

    def _print_final_summary(self):
        """Print a final summary of the simulation run."""
        if not self.metrics['episode_rewards']:
            print("No episodes completed.")
            return
            
        avg_reward = np.mean(self.metrics['episode_rewards'])
        avg_length = np.mean(self.metrics['episode_lengths'])
        win_rate = np.mean(self.metrics['win_status'])
        avg_hero_reward = np.mean(self.metrics['hero_rewards'])
        avg_villain_reward = np.mean(self.metrics['villain_rewards'])
        
        print("\n" + "="*60)
        print("SIMULATION SUMMARY")
        print("="*60)
        print(f"Total Episodes: {len(self.metrics['episode_rewards'])}")
        print(f"Average Reward: {avg_reward:.2f}")
        print(f"Average Episode Length: {avg_length:.2f} steps")
        print(f"Win Rate: {win_rate:.2%}")
        print(f"Average Hero Reward: {avg_hero_reward:.2f}")
        print(f"Average Villain Reward: {avg_villain_reward:.2f}")
        print(f"Metrics saved to: {self.log_dir}")
        print(f"Plots saved to: {self.plot_dir}")
        print("="*60)

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

            if agent.name() not in state_dict:
                state_dict[agent.name()] = new_state
                continue

            agent.update_q(state_dict[agent.name()], action_dict[agent.name()],
                        a_reward, new_state, self.__earth)
            state_dict[agent.name()] = new_state

        self.__simulation_step += 1

        return h_reward, v_reward
