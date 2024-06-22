import random


class Timeout:
    def __init__(self, driver):
        self.driver = driver

    def usual_timeout(self):
        self.driver.reconnect(random.randint(300, 900))

    def arena_timeout(self):
        self.driver.reconnect(random.randint(300, 900))
