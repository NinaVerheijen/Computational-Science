import pygame


class Road:

    def __init__(self, lanes):

        self.lanes = []
        self.pos_lanes = []
        
        # Initialize the starting lanes
        for number_lanes in range(lanes):
            self.lanes.append([])
            self.pos_lanes.append(10 * (number_lanes+1) + 29)

    # Add new lane to the road
    def add_lane(self):
        self.lanes.append([])
        self.pos_lanes.append(10 * (len(self.lanes)))

    # Delete the last lane and delete all cars on that lane
    def delete_lane(self, all_cars):
        for delete_cars in all_cars:
            if delete_cars.y == self.pos_lanes[-1]:
                all_cars.remove(delete_cars)
        self.lanes.pop()
        self.pos_lanes.pop()