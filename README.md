# Computational-Science

This is a traffic model to simulate the traffic flow on Dutch highways.

One simulation will take a little over 30 minutes. For both graphs it will take a little over an hour. During this time we ask you to leave your computer alone, as the mouse and other internal proccesses affect the results. Which will make it non-reproducable.


## How to use
0. Run "pip install -r requirements.txt" to install all following requirements.
1. Set the rush_hour variable in the main function to True or False depending on what simulation you want to run. True simulates rush hours, False simulates off-peak hours. 
2. Run traffic_sim.py to execute the program. As said before, this will take _30 minutes_ and we ask you to not use your computer for anything else during that time. 
3. After 30 minutes a graph with the results shows. You can save this one if you like, but it is automatically saved in the same folder as well.
4. Close the graph window by the red crossed button in the corner to prevent not fully finishing the running of the code.
5. The statistical analysis is now run and saved in (No)RushHourT-Test.txt 
6. Done!

### This is what the graphs should look like
![Traffic Flow During Rush Hour](/Images/RushHour.png)

![Traffic FLow Outside Rush Hour](/Images/NoRushHour.png)

You should run both situations to create both graphs.

If you want to run more simulations (different from the already generated graphs), you can change the arguments when traffic(speed, spawn_rate) is called. Speed is self explanatory and a higher spawnrate means more cars get on the road. 
Furthermore, you can alter the duration of the simulation by changing length_of_simulation. When you do so, also change length to ensure the data is saved properly. 

If you just want to look at cars, comment the graphing and statistical analysis code and put "traffic(130, 0.3)" in the mainfunction.

### End the simulation

There are 3 ways to end the simulation:
1. Let the full simulation run
2. Close the pygame window 
3. Press the escape key

Only by finishing the full simulation (option 1) graphs will be generated.
