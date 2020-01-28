# Computational-Science

This is a traffic model to simulate the traffic flow on Dutch highways.

When you start the simulation, please let your computer run the trials.
One simulation will take a little over 30 minutes. For both graphs it will take a little over an hour. During this time we ask you to leave your computer alone, as the mouse and other internal proccesses affect the results. Which will make it not reproducable.


## How to use
Run "pip install -r requirements.txt" to install all following requirements.

Run traffic_sim.py to execute the program.
If you want to run a rush hour simulation, set the rush_hour variable (line 371) to True. If you want to run a non rush hour simulation, set the variable to False.

You should run both situations to create both graphs.

If you want to run more simulations (different from our already generated graphs), you can change the arguments when traffic(speed, spawn_rate) is called. A higher spawnrate means more cars. 
Furthermore, you can alter the duration of the simulation by changing length_of_simulation (line 249) and length ()


There are 3 ways to end the simulation:
1. Let the full simulation run
2. Close the pygame window 
3. Press the escape key

Only by finishing the full simulation graphs will be generated
