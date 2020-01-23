import pygame
import sys
import math as Math
import random
import time as tijd
from pygame import *
from pygame.locals import *
from pygame.sprite import *

WIDTH = 1100 # 8 km?
HEIGHT = 400
road_length = 18

def meter_to_pixel(distance):
    one_m = WIDTH/(road_length * 1000)
    dist = distance*one_m
    return dist

def pixel_to_meter(pixels):
    one_p = (road_length * 1000)/WIDTH
    dist = pixels*one_p
    return dist

class Vehicle(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the Vehicle,
    # and its x and y position

    def __init__(self, ID, model, maximumspeed, color, size, x, lane, speed, direction):

        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.ID = ID
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.lane = (lane-29) / 10 
        self.speed  = speed * (1 - self.lane/100*10)
        self.model = model
        # if model == 'truck':
        #     self.max_speed = 90
        # else:
        #     self.max_speed = 130

        if model == 'truck':
            self.max_speed = 90
        else:
            self.max_speed = maximumspeed

        self.x = int(x)  # variable denoting x position of car
        self.y = int(lane)
        self.direction = direction
        self.size = size
        self.switch = False
        self.can_switch = False
        self.left_right = 0
        self.left_or_right = None
        self.gap_want = 30

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect(center=(x,lane))
        self.rect.size = (size[0] + 10, size[1])


    def desired_gap(self, v, d_v):
        """
        s_0 is minimum bumper to bumper gap -> 2m
        a is acceleration in every day traffic -> 0.3m/s^2
        b is comfortable (breaking) deceleration in everyday traffic -> 3.0m/s^2
        delta is acceleration exponent -> 4
        T is desired safety time -> 1.5 s
        s is current gap
        """
        s_0 = 300  # minimum gap between cars
        a = 0.3
        b = 3
        T = 1.5                   
        des_gap = s_0 + max(0, v*T + ((v*d_v)/ (2*Math.sqrt(a*b))))
        return des_gap

    def comp_acc(self, s, lead_speed):
        a = 0.3
        
        v_0 = self.max_speed
        v = self.speed
        d = 4
        d_v = abs(v - lead_speed) #lead_speed = leading car speed
        a_free = a*(1-(v/v_0)**d)
        a_int = a*((self.desired_gap(v, d_v) / s)**2) # hoeveel de auto de gap wil van de auto voor hem

        acc =  a_free - a_int
        return acc

    def move(self):
        new_x = self.x + meter_to_pixel(self.speed)  # new place for the car
        new_y = self.y

        self.rect.right = new_x  # move the car
        self.x = new_x  # update the car position
        self.rect.bottom = new_y  # move the car
        self.y = new_y

