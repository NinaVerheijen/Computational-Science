# from .dir import Dir
import pygame
import sys
import os
import math as Math
import random
import bisect
import time as tijd
from pygame import *
from pygame.locals import *
from pygame.sprite import *
from Vehicle import Vehicle
from road import Road

# from Vehicle import Vehicle
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

pygame.init()

clock = pygame.time.Clock()
clock.tick(60)

# background 2 or 3 lanes

# background_image = pygame.image.load("2baans.png")
background_image = pygame.image.load("3baans.png")

# lanes = [lane1, lane2, lane3]
random.seed(2)

WIDTH = 1920 # 8 km?
HEIGHT = 100
road_length = 12
# CAPTION = 'Traffic Simulator'
pygame.display.set_caption('Traffic Simulator')



def meter_to_pixel(distance):
    # hoeveel pixels in meter
    one_m = WIDTH/(road_length * 1000)
    dist = distance*one_m
    return dist

def pixel_to_meter(pixels):
    # meters in een pixel zitten
    one_p = (road_length * 1000)/WIDTH
    dist = pixels*one_p
    return dist

# Returns gap from bumper to bumper in meters.
def compute_gap(follower, leader):
    follower_bumper = follower.x + (follower.size[0] / 2)
    leader_bumper = leader.x - (leader.size[0] / 2)
    gap = leader_bumper - follower_bumper
    return pixel_to_meter(gap)

def traffic():
    frame = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    all_cars = Group()
    # Make the road
    road = Road(4,50)
    # print(road.lanes, road.pos_lanes)
    road.add_lane()
    # print(road.lanes, road.pos_lanes)
    road.delete_lane(all_cars)
    # print(road.lanes)

    while True:
        tijd.sleep(0.05)
        # tijd.sleep(0.000000000000000000000000000000000000000000000000000000001)
        chance = random.uniform(0, 1)

        if chance < 0.3:
            truck_chance = random.uniform(0,1)

            if truck_chance < 0.80:
                car = Vehicle(chance, 'car', (255, 0, 0), [24/2, 12/2], -50, random.choice(road.pos_lanes), 50 + random.randrange(-10,10,2), [0.2,0])
                all_cars.add(car)
            else:
                choice = random.choices(population = road.pos_lanes, weights = [0.02, 0.04, 0.1, 0.84])
                truck = Vehicle(chance + 0.0000001, 'truck', (0, 0, 255), [98/2, 14/2], -50, choice[0], 10 + random.randrange(-5,5,1), [0.2,0])
                all_cars.add(truck)

            # put car in the right lane and keep track of which lane the car is
            for number in range(len(road.pos_lanes)):
                if car.y == road.pos_lanes[number]:
                    road.lanes[number].append(car)

        for car in all_cars:
            change_lanes = random.uniform(0, 1)

            if change_lanes < 0.005:
                car.switch = True

            if car.switch is True:
                car.image.fill((0,255,0))
                if car.y in road.pos_lanes:
                    car.left_or_right = random.uniform(0, 1)
                    # exception if most left lane or most right lane
                    if car.lane * 50 == road.pos_lanes[0]:
                        car.left_or_right = 1

                    if car.lane * 50 == road.pos_lanes[-1]:
                        car.left_or_right = 0

                # Which lane switch,  -1 is naar boven
                if car.left_or_right < 0.5:
                    car.left_right = -1
                elif car.left_or_right >= 0.5:
                    car.left_right = 1

                if car.left_right == 1 or car.left_right == -1:
                    going_lane = road.pos_lanes[int(car.lane + car.left_right) - 1]
                    # print(car.lane, going_lane)
                    cars_x_positions = ([x_pos.x for x_pos in road.lanes[int(car.lane + car.left_right)-1]])
                    cars_x_positions.reverse()
                    index = bisect.bisect(cars_x_positions, car.x)
                    # print("index: ", index, "xposition: ", car.x, cars_x_positions)
                    # print("___________________________________________________________________")
                    # if index == 0 or index == len(cars_x_positions):
                    for check_car in all_cars:
                        if index is not len(cars_x_positions):
                            if check_car.x == cars_x_positions[index]:
                                next_car = check_car
                        else:
                            next_car = None
                        if index is not 0:
                            if check_car.x == cars_x_positions[index - 1]:
                                prev_car = check_car
                        else:
                            prev_car = None
                    # front_gap = pixel_to_meter(next_car.x - car.x)
                    # back_gap = pixel_to_meter(prev_car.x - car.x)
                        # no back car or front car
                    # print(next_car)

                    # print(prev_car)

                    # if next_car is not None:
                    #     print('front', compute_gap(car, next_car))
                    # print('back', compute_gap(prev_car, car))
                    # print('prev', prev_car.x)
                    # print('car', car.x)
                    # if next_car is not None:
                    #     print('next', next_car.x)
                    # print('----------------------------------------------------')

                    if (prev_car is not None and next_car is not None) and compute_gap(car, next_car) > car.gap_want and compute_gap(prev_car, car) > car.gap_want:
                        car.can_switch = True


                # Y changing from the car to new lane
                if car.can_switch == True:
                    car.y += car.left_right
                elif car.can_switch == False and car.y in road.pos_lanes:
                    car.switch = False





                # lane switch complete
                if car.y in road.pos_lanes:
                    car.lane = car.y / 50
                    car.switch = False
                    car.image.fill((255,0,0))

            for c in all_cars:

                # Only check cars that are in same lane and in front of car
                if car.y == c.y and car.x < c.x:
                    # gap in lane tussen volgende auto in x

                    gap = compute_gap(car, c)
                    car.speed += car.comp_acc(gap, c.speed)

                    # prevent cars from going backwards.
                    if car.speed < 0:
                        car.speed = 0

                # If there is no car in front of current car.
                else:
                    gap = 1000000
                    car.speed += car.comp_acc(gap, car.speed)

                    if car.speed < 0:
                        car.speed = 0


            car.move()
            if car.x > WIDTH:
                all_cars.remove(car)


        # if len(road.lanes[-1]) >= 2:
        #     road.delete_lane(all_cars)
        #     road.add_lane()
        #     road.add_lane()

        # quit pygame

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # frame.fill((255, 255, 255))
        frame.blit(background_image, [0, 0])

        # Draw the lanes
        # pygame.draw.line(frame, (0, 0, 0), (0, road.pos_lanes[0] - 10), (WIDTH, road.pos_lanes[0] - 10))
        # for lane in road.pos_lanes:
        #     pygame.draw.line(frame, (0, 0, 0), (0, lane + 10), (WIDTH, lane + 10))

        all_cars.draw(frame)
        display.update()



        pygame.display.flip()


if __name__ == '__main__':
    traffic()
