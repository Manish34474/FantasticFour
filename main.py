from controller.simulator import Simulator

# Run simulation with metrics tracking
simulator = Simulator(
    num_episodes=100,      # Run 100 episodes
    log_dir="simulation_logs",  # Directory for log files
    plot_dir="simulation_plots" # Directory for plot images
)
simulator.run()