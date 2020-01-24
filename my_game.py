# from .dir import Dir
import pygame
import sys
import os
import math as Math
import random
import bisect
import time as tijd
import matplotlib.pyplot as plt
from pygame import *
from pygame.locals import *
from pygame.sprite import *
from Vehicle import Vehicle
from road import Road

# from Vehicle import Vehicle
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

# pygame.init()

# clock = pygame.time.Clock()
# clock.tick(60)

# background 2 or 3 lanes

# background_image = pygame.image.load("2baans.png")
background_image = pygame.image.load("3baans.png")

# lanes = [lane1, lane2, lane3]
random.seed(2)

WIDTH = 1920 # 12 km? #1920
HEIGHT = 100
road_length = 12
# CAPTION = 'Traffic Simulator'
pygame.display.set_caption('Traffic Simulator')

# a_thres is used during lane switching to check if the new follow doesn't have to brake to much. a_thresh must be lower than the lowest acceleration of all vehicles.
a_thres = 0.2



def meter_to_pixel(distance):
    # hoeveel pixels in meter
    one_m = WIDTH/(road_length * 1000)
    dist = distance* one_m
    return dist

def pixel_to_meter(pixels):
    # meters in een pixel zitten
    one_p = (road_length * 1000)/WIDTH
    dist = one_p*pixels
    return dist


def vehicle_spawn(road, all_cars, max_speed):
    chance = random.uniform(0, 1)

    if chance < 0.1:
        truck_chance = random.uniform(0,1)
        if truck_chance < 0.80:
            vehicle = Vehicle(chance, 'car', max_speed, (255, 0, 0), [24/2, 12/2], 10, random.choice(road.pos_lanes), 100 + random.randrange(-10,10,2), [0.2,0])


        else:
            choice = random.choices(population = road.pos_lanes, weights = [0, 0.01, 0.1, 0.85])
            vehicle = Vehicle(chance, 'truck', max_speed, (0, 0, 255), [98/2, 14/2], 10, choice[0], 80 + random.randrange(-5,5,1), [0.2,0])

        if not spritecollideany(vehicle, all_cars):

            all_cars.add(vehicle)

            # put car in the right lane and keep track of which lane the car is
            for number in range(len(road.pos_lanes)):
                if vehicle.y == road.pos_lanes[number]:
                    road.lanes[number].insert(0, vehicle)

    return all_cars

def lane_switching(car, road, all_cars):
    left = True
    right = True
    index = None
    left_follower = None
    left_leader = None
    right_follower = None
    right_leader = None
    car.can_switch = False

    # Make sure they are not accidentaly choosen
    left_acc = -200
    right_acc = -200
    follower_left_acc = -200
    follower_right_acc = -200

    # get the x positions of cars in the adjecent lanes
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

    # leader and follower in current lane.
    leader, _ = neighbour_cars(road, car)

    # Compute current gap and acc
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

    # Check which acceleration is the biggest.
    if left_acc > (current_acc + a_thres + car.bias_left) and follower_left_acc > -4:
        car.can_switch = True
        car.left_right = -1
        index = index_left

        # If left acc > current acc, check if right > left, thus also > current.
        if right_acc >= (left_acc + a_thres) and follower_right_acc > -4:
            car.left_right = 1
            index = index_right

    if right_acc > (current_acc + a_thres + car.bias_right) and follower_right_acc > -4:
        car.can_switch = True
        car.left_right = 1
        index = index_right

    if car.can_switch == True:
        car.is_switching = True

        if car in road.lanes[int(car.lane-1)]:
            car.image.fill((0, 255, 0))
            road.lanes[int(car.lane - 1)].remove(car)

            car.lane = car.lane + car.left_right
            road.lanes[int(car.lane-1)].insert(index, car)


    return index


    # if car.y in road.pos_lanes:
    #     car.left_or_right = random.uniform(0, 1)
    #     # exception if most left lane or most right lane
    #     if car.lane * 10 + 29 == road.pos_lanes[0]:
    #         car.left_or_right = 1

    #     if car.lane * 10 + 29 == road.pos_lanes[-1]:
    #         car.left_or_right = 0

    # # Which lane switch,  -1 is naar boven
    # if car.left_or_right < 0.3:
    #     car.left_right = -1
    # else:
    #     car.left_right = 1


    # get the x positions of cars in the lane where the car is going to
    # if car.left_right == 1 or car.left_right == -1:
    #     cars_x_positions = ([x_pos.x for x_pos in road.lanes[int(car.lane + car.left_right)-1]])
    #     index = bisect.bisect(cars_x_positions, car.x)
    #     next_car = None
    #     prev_car = None

    #     # Find the previous and the next car in the switching lane
    #     for check_car in all_cars:

    #         # If the cars has a leader.
    #         if index is not len(cars_x_positions):
    #             if check_car.x == cars_x_positions[index]:
    #                 next_car = check_car

    #         # If the car has a follower.
    #         if index is not 0:
    #             if check_car.x == cars_x_positions[index - 1]:
    #                 prev_car = check_car


        # # The gap is big enough
        # if (prev_car is not None and next_car is not None):

        #     if compute_gap(car, next_car) > car.gap_want and compute_gap(prev_car, car) > car.gap_want:

        #         # leader and follower in current lane.
        #         leader, follower = neighbour_cars(road, car)

        #         if leader == None:
        #             current_gap = 10000
        #             current_acc = car.comp_acc(current_gap, car.max_speed)
        #         else:
        #             current_gap = compute_gap(car, leader)
        #             current_acc = car.comp_acc(current_gap, leader.speed)

        #         # Check if new follower does not have to break to much
        #         prev_gap = compute_gap(prev_car, car)
        #         prev_acc = prev_car.comp_acc(prev_gap, car.speed)

        #         # Check if there is an increase in acc
        #         switch_gap = compute_gap(car, next_car)
        #         switch_acc = car.comp_acc(switch_gap, next_car.speed)

        #         if car.left_right == 1:
        #             a_thres = car.bias_right
        #         else:
        #             a_thres = car.bias_left


        #         if switch_acc > (current_acc + a_thres) and prev_acc > -4 :
        #             car.can_switch = True
        #             car.image.fill((0, 255, 0))

        #             if car in road.lanes[int(car.lane-1)]:
        #                 road.lanes[int(car.lane - 1)].remove(car)
        # return(index)


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

def traffic(max_speed):
    pygame.init()

    clock = pygame.time.Clock()
    clock.tick(60)
    frame = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    all_cars = Group()
    # Make the road
    road = Road(4)
 
    start_ticks=pygame.time.get_ticks()
    trafficcount = 0
    trafficcountie = 0
    graphie = []
    graphieint = []
    timie = []
    # graphtime interval
    t = 2


    while True:
        tijd.sleep(0.00000005)
        seconds=(pygame.time.get_ticks()-start_ticks)/1000


        if int(seconds) % t == 0 and int(seconds) not in timie:
            # print(int(seconds))
            graphie.append(trafficcount)
            graphieint.append(trafficcountie)
            trafficcountie = 0
            timie.append(int(seconds))
        # else:
        all_cars = vehicle_spawn(road, all_cars, max_speed)

        for car in all_cars:

            change_lanes = random.uniform(0, 1)

            if change_lanes < 0.9:
                car.switch = True

            next_car, prev_car = neighbour_cars(road, car)

            if car.switch is True:
                if car.is_switching is False:
                    index = lane_switching(car, road, all_cars)

                # Y changing from the car to new lane
                if car.can_switch == True:
                    car.y += car.left_right
                    # car.lane = (car.y-29) / 10
                    # road.lanes[int(car.lane-1)].insert(index, car)


                # lane switch complete
                if car.can_switch == True:
                    if car.y in road.pos_lanes:

                        car.switch = False
                        car.can_switch = False
                        car.is_switching = False


                        if car.model == 'car':
                            car.image.fill((255,0,0))
                        else:
                            car.image.fill((0, 0, 255))

            if next_car is not None:
                gap = compute_gap(car, next_car)
                
                acc = car.comp_acc(gap, next_car.speed)
                # if car.speed < 10:
                    # print(gap, 'ACC', acc, '\n', car.x, car.lane)
                    # print('-------------------------')
                car.speed += acc

                # prevent cars from going backwards.
                if car.speed < 0:
                    car.speed = 0
            else:
                gap = 10000

                car.speed += car.comp_acc(gap, car.max_speed)

                if car.speed < 0:
                    car.speed = 0

            car.move()
            if car.x > WIDTH:

                trafficcount += 1
                trafficcountie += 1

                print('car has exited', car.speed, car.max_speed)

                print(car.speed, car.max_speed)
                road.lanes[int(car.lane - 1)].pop()
                all_cars.remove(car)


        # quit pygame
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                if event.key == K_SPACE:
                    tijd.sleep(4)

            if event.type == pygame.QUIT:
                # total average number of vehicles per time interval
                trafficflow = (trafficcount / seconds) *t
                pygame.quit()
                return trafficflow, graphie, graphieint, timie

        # make pygame
        frame.blit(background_image, [0, 0])
        all_cars.draw(frame)
        display.update()
        pygame.display.flip()




if __name__ == '__main__':
    # # run traffic lower speed
    # average_tf_l, cummulative_tf_l, interval_tf_l, timeline_l = traffic(100)
    # # run traffic higher speed
    # average_tf_h, cummulative_tf_h, interval_tf_h, timeline_h = traffic(130)
    # # plt.plot(timeline, cummulative_tf, label="Cummulative trafficflow", c="#7F98FF")
    # # plt.plot(timeline, interval_tf, label="Trafficflow per time unit", c="#3152D4")
    # # plt.plot(timeline, [average_tf] * len(timeline), label="Average trafficflow", c="#001F9A")
    # plt.plot(timeline_l, cummulative_tf_l, label="Cummulative trafficflow", c="lightblue")
    # plt.plot(timeline_l, interval_tf_l, label="Trafficflow per time unit", c="blue")
    # plt.plot(timeline_l, [average_tf_l] * len(timeline_l), label="Average trafficflow", c="darkblue")
    # plt.legend()
    # plt.show()

    traffic(130)
