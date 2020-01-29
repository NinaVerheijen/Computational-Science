import pygame
import sys
import math as Math
import random
import numpy as np
import time as tijd
from pygame import *
from pygame.locals import *
from pygame.sprite import *

WIDTH = 1920
HEIGHT = 100
road_length = 12


# Convert meters to pixels
def meter_to_pixel(distance):
    one_m = WIDTH / (road_length * 1000)
    dist = distance * one_m

    return dist

# Convert pixels to meters 
def pixel_to_meter(pixels):
    one_p = (road_length * 1000) / WIDTH
    dist = pixels*one_p

    return dist

class Vehicle(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the Vehicle,
    # and its x and y position

    def __init__(self, model, maximumspeed, color, size, x, lane, speed):

        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        """
        image = the vehicle
        lane = current lane
        speed = current speed
        max_speed = maximum speed
        model = car or truck
        can_switch = possible to change lanes
        is_switching = in process of changing lanes
        left_right = direction of changing lanes 
        a_thres = minimum threshold for changing lanes in respect to acceleration 
        bias_left and bias_right = how likely to go left or right when lane switching
        aggression = how aggressive a driver is (smaller gap, more speed)
        gap_want = the gap that the vehicle wants between it and the leading vehicle
        """

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.size = size
        self.image = pygame.Surface(self.size)
        self.image.fill(color)
        self.lane = (lane - 29) / 10
        self.speed  = speed * (1 - self.lane/100*10)
        self.model = model
        self.x = int(x) 
        self.y = int(lane)
        self.can_switch = False
        self.is_switching = False
        self.left_right = None
        self.a_thres = 0.2

        # random aggression of the vehciles
        std = np.random.normal(1, 0.4, 2)
        self.aggression  = abs(np.mean(std))

        # Trucks more likely to be in right lane
        if self.model == 'truck':
            self.max_speed = 90
            self.bias_left = 2
            self.bias_right = -1
        else:
            self.max_speed = maximumspeed * self.aggression
            self.bias_left = 0.5
            self.bias_right = -0.2 + (self.lane * 0.1)

        # 50% chance to go faster, more likely to go little bit faster than alot
        chance = random.uniform(0,1)
        if chance > 0.5:
            bias = Math.pow(random.random(), 4)
            speed = int(round(10 + (50 - 10) * bias))
            too_fast = random.uniform(0,1)
            if too_fast <= 0.1:
                self.max_speed = self.max_speed + speed
            else:
                self.max_speed = self.max_speed + random.randint(3, 10)

        self.gap_want = 50 * (2 - self.aggression)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect(center=(x,lane))
        self.rect.size = (size[0] + 10, size[1])

    # Compute desired gap
    def desired_gap(self, v, d_v):
        """
        s_0 is minimum bumper to bumper gap -> 2m
        a is acceleration in every day traffic -> 0.3m/s^2
        b is comfortable (breaking) deceleration in everyday traffic -> 3.0m/s^2
        delta is acceleration exponent -> 4
        T is desired safety time -> 1.5 s
        s is current gap
        """
        b = 3

        if self.model == 'truck':
            s_0 = self.gap_want + 20
            a = 0.25 * (self.aggression) 
            T = 2 * (2 - self.aggression)
        else:
            # minimum gap between cars
            s_0 = self.gap_want  
            a = 0.3 * (self.aggression) 
            T = 1.5 * (2 - self.aggression)
        des_gap = s_0 + max(0, v * T + ((v * d_v) / (2 * Math.sqrt(a * b))))
        return des_gap

    # Compute acceleration
    def comp_acc(self, s, lead_speed):
        a = 0.3 * (self.aggression) 
        v_0 = (self.max_speed) 
        v = self.speed
        d = 4
        d_v = abs(v - lead_speed) 
        
        a_free = a * (1-(v / v_0)**d)
        a_int = a * ((self.desired_gap(v, d_v) / s)**2)
        acc =  a_free - a_int
        return acc

    # Move the car and update
    def move(self):
        new_x = self.x + meter_to_pixel(self.speed)
        new_y = self.y

        self.rect.right = new_x 
        self.x = new_x  
        self.rect.bottom = new_y  
        self.y = new_y
