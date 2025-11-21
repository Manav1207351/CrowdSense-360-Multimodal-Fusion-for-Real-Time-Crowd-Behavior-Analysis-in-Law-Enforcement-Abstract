# src/detector/group_detector.py

import time
from datetime import datetime

class CrowdGroupDetector:
    def __init__(self, min_people=10, duration_sec=300):
        """
        Detects when a group of people stays longer than 'duration_sec'.

        Args:
            min_people: minimum number of people to start counting as a group
            duration_sec: how long the group must stay to trigger alert
        """
        self.min_people = min_people
        self.duration_sec = duration_sec
        self.group_start_time = None
        self.last_people_count = 0

    def update(self, people_count):
        """
        Update group tracking every frame.

        Returns:
            (bool) True if alert should be triggered
        """
        now = time.time()

        # Case 1: Not enough people → reset
        if people_count < self.min_people:
            self.group_start_time = None
            self.last_people_count = people_count
            return False

        # Case 2: Count enough people
        if self.group_start_time is None:
            # Start timer
            self.group_start_time = now
            self.last_people_count = people_count
            return False

        # Case 3: Timer running → check 5 minutes
        elapsed = now - self.group_start_time

        if elapsed >= self.duration_sec:
            return True

        return False

    def get_elapsed(self):
        """Return how long group has been present"""
        if self.group_start_time is None:
            return 0
        return time.time() - self.group_start_time
