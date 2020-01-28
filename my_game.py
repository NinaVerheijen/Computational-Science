# from .dir import Dir
import pygame
import sys
import os
import math as Math
import numpy as np
import random
import bisect
import time as tijd
import matplotlib.pyplot as plt
from scipy import stats
from pygame import *
from pygame.locals import *
from pygame.sprite import *
from Vehicle import Vehicle
from road import Road

# Open the simulation in the upper left corner
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

WIDTH = 1920
HEIGHT = 100
road_length = 12
pygame.display.set_caption('Traffic Simulator')


# Convert meters to pixels
def meter_to_pixel(distance):
    one_m = WIDTH/(road_length * 1000)
    dist = distance* one_m
    return dist

# Convert pixels to meters
def pixel_to_meter(pixels):
    one_p = (road_length * 1000)/WIDTH
    dist = one_p*pixels
    return dist

# Create vehicles
def vehicle_spawn(road, all_cars, max_speed, car_density):
    # Chance for spawning a vehicle
    chance = random.uniform(0, 1)
    if chance < car_density:
        # Chance that the spawned vehicle is a truck
        truck_chance = random.uniform(0,1)
        if truck_chance < 0.80:
            vehicle = Vehicle('car', max_speed, (255, 0, 0), [24/2, 12/2], 10, random.choice(road.pos_lanes), 100 + random.randrange(-10,10,2))
        else:
            # Trucks spawning more on the right lane
            choice = random.choices(population = road.pos_lanes, weights = [0, 0.01, 0.1, 0.85])
            vehicle = Vehicle('truck', max_speed, (0, 0, 255), [98/2, 14/2], 10, choice[0], 80 + random.randrange(-5,5,1))

        # Don't spawn vehicles on top of eachother
        if not spritecollideany(vehicle, all_cars):
            all_cars.add(vehicle)

            # Put car in the right lane and keep track of which lane the car is
            for number in range(len(road.pos_lanes)):
                if vehicle.y == road.pos_lanes[number]:
                    road.lanes[number].insert(0, vehicle)

    return all_cars

# Check if a vehicle should and can switch lanes
def lane_switching(car, road, all_cars):
    left = True
    right = True
    index = None
    left_follower = None
    left_leader = None
    right_follower = None
    right_leader = None
    car.can_switch = False

    # Failsave so no random switches happen
    left_acc = -200
    right_acc = -200
    follower_left_acc = -200
    follower_right_acc = -200

    # Get the x positions of cars in the adjecent lanes
    if car.lane != 1 and car.lane != 4:
        cars_x_pos_left = ([x_pos.x for x_pos in
                            road.lanes[int(car.lane - 1)-1]])
        cars_x_pos_right = ([x_pos.x for x_pos in
                                road.lanes[int(car.lane + 1)-1]])
        index_left = bisect.bisect(cars_x_pos_left, car.x)
        index_right = bisect.bisect(cars_x_pos_right, car.x)

        left_follower, left_leader = left_right_neighbours(
            index_left, cars_x_pos_left, all_cars)
        right_follower, right_leader = left_right_neighbours(
            index_right, cars_x_pos_right, all_cars)

    # If car is in left most lane
    if car.lane == 1:
        left = False
        cars_x_pos_right = ([x_pos.x for x_pos in
                            road.lanes[int(car.lane + 1)-1]])
        index_right = bisect.bisect(cars_x_pos_right, car.x)
        right_follower, right_leader = left_right_neighbours(
            index_right, cars_x_pos_right, all_cars)

    # If car is in right most lane
    if car.lane == 4:
        right = False
        cars_x_pos_left = ([x_pos.x for x_pos in
                            road.lanes[int(car.lane - 1)-1]])
        index_left = bisect.bisect(cars_x_pos_left, car.x)
        left_follower, left_leader = left_right_neighbours(
            index_left, cars_x_pos_left, all_cars)

    # Leading and following vehicle in current lane.
    leader, _ = neighbour_cars(road, car)

    # Compute current gap and acceleration
    if leader == None:
        current_acc = car.comp_acc(10000, car.max_speed)
    else:
        current_gap = compute_gap(car, leader)
        current_acc = car.comp_acc(current_gap, leader.speed)

    # If car is not in left most lane and has a follower and leader, compute acc
    if left == True and left_follower is not None and left_leader is not None:
        if compute_gap(car, left_leader) > car.gap_want and compute_gap(left_follower, car) > car.gap_want:
            # Check if new follower does not have to break to much
            follower_gap_left = compute_gap(left_follower, car)
            follower_left_acc = left_follower.comp_acc(follower_gap_left, car.speed)

            # Check if there is an increase in acc
            left_gap = compute_gap(car, left_leader)
            left_acc = car.comp_acc(left_gap, left_leader.speed)
    else:
        left_acc = -200
        follower_left_acc = -200

    # If car is not in right most lane and has a follower and leader, compute acc
    if right == True and right_follower is not None and right_leader is not None:
        if compute_gap(car, right_leader) > car.gap_want and compute_gap(right_follower, car) > car.gap_want:
            # Check if new follower does not have to break to much
            follower_gap_right = compute_gap(right_follower, car)
            follower_right_acc = right_follower.comp_acc(
                follower_gap_right, car.speed)

            # Check if there is an increase in acc
            right_gap = compute_gap(car, right_leader)
            right_acc = car.comp_acc(right_gap, right_leader.speed)
    else:
        right_acc = -200
        follower_right_acc = -200

    # Slower vehicles have a tendency to go to the right lane
    if car.max_speed < 80:
        bias_right = car.bias_right - 1
    else:
        bias_right = car.bias_right

    # Check which acceleration is the biggest.
    if left_acc > (current_acc + car.a_thres + car.bias_left) and follower_left_acc > -4:
        car.can_switch = True
        car.left_right = -1
        index = index_left

        # Is right acc more than left acc, thus more than current acc
        if right_acc >= (left_acc + car.a_thres) and follower_right_acc > -4:
            car.left_right = 1
            index = index_right

    # Right acc more than left acc
    if right_acc > (current_acc + car.a_thres + bias_right) and follower_right_acc > -4:
        car.can_switch = True
        car.left_right = 1
        index = index_right

    # It is possible to switch
    if car.can_switch == True:
        car.is_switching = True

        # Update attributes of switching car to new lane
        if car in road.lanes[int(car.lane-1)]:
            # Visualisation for switching lanes
            car.image.fill((0, 255, 0))
            road.lanes[int(car.lane - 1)].remove(car)

            car.lane = car.lane + car.left_right
            road.lanes[int(car.lane-1)].insert(index, car)

# Returns gap from bumper to bumper in meters.
def compute_gap(follower, leader):
    follower_bumper = follower.x + (follower.size[0] / 2)
    leader_bumper = leader.x - (leader.size[0] / 2)
    if leader.model == 'truck' or follower.model == 'truck':
        gap = leader_bumper - follower_bumper - 20
    else:
        gap = leader_bumper - follower_bumper
    if gap < 0:
        gap = 0.00000001
    return pixel_to_meter(gap)

# Find neighbours of adjacent lane
def left_right_neighbours(index, cars_x_positions, all_cars):
    follower = None
    leader = None

    for check_car in all_cars:
        # If the cars has a leader.
        if index is not len(cars_x_positions):
            if check_car.x == cars_x_positions[index]:
                leader = check_car

        # If the car has a follower.
        if index is not 0:
            if check_car.x == cars_x_positions[index - 1]:
                follower = check_car
    return follower, leader

# Find neighbours of current lane
def neighbour_cars(road, car):
    next_car = None
    prev_car = None

    if car.can_switch == False:
        find_index = road.lanes[int(car.lane - 1)].index(car)

        if find_index + 1 is not len(road.lanes[int(car.lane - 1)]):
            next_car = road.lanes[int(car.lane - 1)][find_index+1]
        if find_index is not 0:
            prev_car = road.lanes[int(car.lane - 1)][find_index-1]

    return next_car, prev_car


# This function performs the two-tail Student T-Test on three arrays of data.
# The t and p values are written to a textfile
def stat_an(title, samples1, samples2, samples3):
    t1, p1 = stats.ttest_ind(samples1, samples2, axis=0, equal_var=False)
    t2, p2 = stats.ttest_ind(samples2, samples3, axis=0, equal_var=False)
    t3, p3 = stats.ttest_ind(samples3, samples1, axis=0, equal_var=False)

    file = open(str(title) + "T-Test.txt","w")
    file.write("Below you find the p and t values of the student t-test executed on the three different speeds.\n")
    file.write("80 vs 100 \t | \t t = " + str(t1) + "\t | \t p = " + str(p1))
    file.write("100 vs 130 \t | \t t = " + str(t2) + "\t | \t p = " + str(p2))
    file.write("130 vs 80 \t | \t t = " + str(t3) +" \t | \t p = " + str(p3))
    file.close()

# Main function that simulates the traffic
def traffic(max_speed, car_density):
    # Set the duration of one simulation in seconds
    length_of_simulation = 60
    # Time interval in seconds for datapoint saving
    t = 2

    # Initiate the simulation
    pygame.init()
    clock = pygame.time.Clock()
    clock.tick(60)
    frame = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    background_image = pygame.image.load("4baans.png")


    start_ticks=pygame.time.get_ticks()
    traf_count = 0
    traf_counts = []
    timestamps = []


    all_cars = Group()

    # Make the road
    road = Road(4)

    while True:
        tijd.sleep(0.00000000000000000000000000000000000000000000000000000005)
        seconds = (pygame.time.get_ticks()-start_ticks)/1000

        # Increment counters when an interval has been completed
        if int(seconds) % t == 0 and int(seconds) not in timestamps:
            timestamps.append(int(seconds))
            traf_counts.append(traf_count)
            traf_count = 0

        # Spawn a vehicle
        all_cars = vehicle_spawn(road, all_cars, max_speed, car_density)

        for car in all_cars:
            next_car, _ = neighbour_cars(road, car)

            # Check if car is already switching
            if car.is_switching is False:
                lane_switching(car, road, all_cars)

            # Y changing from the car to new lane
            if car.can_switch == True:
                car.y += car.left_right

            # Lane switch complete
            if car.can_switch == True:
                if car.y in road.pos_lanes:

                    # Reset attributes
                    car.can_switch = False
                    car.is_switching = False

                    # Visualisation for car back in lane
                    if car.model == 'car':
                        car.image.fill((255,0,0))
                    else:
                        car.image.fill((0, 0, 255))

            # Change speed of the car depending on the leading car
            if next_car is not None:
                gap = compute_gap(car, next_car)
                acc = car.comp_acc(gap, next_car.speed)
                car.speed += acc

                # prevent cars from going backwards.
                if car.speed < 0:
                    car.speed = 0
            else:
                # No leading car (free flow)
                gap = 10000
                car.speed += car.comp_acc(gap, car.max_speed)

                if car.speed < 0:
                    car.speed = 0

            # Move the car
            car.move()

            # Remove cars that exit the screen
            if car.x > WIDTH:
                traf_count += 1
                road.lanes[int(car.lane - 1)].pop()
                all_cars.remove(car)



        # End the simulation when the set time has been reached
        if seconds > length_of_simulation:
            pygame.quit()
            # total average number of vehicles per time interval
            trafficflow = (np.sum(traf_counts) / seconds) *t
            return trafficflow, traf_counts , timestamps



        # End the simulation when esc is pressed or the window is closed
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                if event.key == K_SPACE:
                    tijd.sleep(4)

            if event.type == pygame.QUIT:
                pygame.quit()

        # Make pygame
        frame.blit(background_image, [0, 0])
        all_cars.draw(frame)
        display.update()
        pygame.display.flip()




if __name__ == '__main__':

    # Set to True or False depending on what simulation you want to run.
    # When set to True, more cars will be spawned on the road. When set to False, less cars will be created
    rush_hour = True

    # Set variables depending on Rush Hour for user friendliness
    if rush_hour == True:
        spawn_rate = 0.3
        plt.title("Traffic Flow at Different Speeds During Rush Hour")
        title = "RushHour"
    elif rush_hour == False:
        spawn_rate = 0.1
        plt.title("Traffic Flow at Different Speeds Outside Rush Hour")
        title = "NoRushHour"

    # Initialize arrays to save datapoints
    intervals1 = np.array([0] * 31)
    intervals2 = np.array([0] * 31)
    intervals3 = np.array([0] * 31)
    tf80 = []
    tf100 = []
    tf130 = []

    # Run each different speed ten times. Save the total traffic flow and the traffic flow during each interval
    for i in range(10):
        print("You are now running round ", i, " of 10")

        tf_l, interval_l, time_l = traffic(80, spawn_rate)
        tf80.append(tf_l)
        intervals1 = np.add(intervals1, np.array(interval_l))

        tf_l, interval_l, time_l = traffic(100, spawn_rate)
        tf100.append(tf_l)
        intervals2 = np.add(intervals2, np.array(interval_l))

        tf_l, interval_l, time_l = traffic(130, spawn_rate)
        tf130.append(tf_l)
        intervals3 = np.add(intervals3, np.array(interval_l))

    # Create plot figure
    plt.figure(figsize=(20,10))
    plt.rcParams.update({'font.size': 22})

    # Plot the intervals and the average traffic flow of each speed
    plt.plot(time_l, intervals1 / 10, label="Trafficflow per time unit at %i km/h" % (80), c="green")
    plt.plot(time_l, [np.mean(tf80)] * len(time_l), label="Average trafficflow at %i km/h" % (80), c="lightgreen")

    plt.plot(time_l, intervals2 / 10, label="Trafficflow per time unit at %i km/h" % (100), c="blue")
    plt.plot(time_l, [np.mean(tf100)] * len(time_l), label="Average trafficflow at %i km/h" % (100), c="lightblue")

    plt.plot(time_l, intervals3 / 10, label="Trafficflow per time unit at %i km/h" % (130), c="red")
    plt.plot(time_l, [np.mean(tf130)]  * len(time_l), label="Average trafficflow at %i km/h" % (130), c="pink")

    # Set graph attributes
    plt.xlabel("Time in seconds")
    plt.ylabel("Number of vehicles")
    plt.legend(loc=4)
    plt.savefig('TrafficFlow'+str(title)+'.png')
    plt.show()

    # Perform statistical analysis
    stat_an(title, intervals1, intervals2, intervals3)
