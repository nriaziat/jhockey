from datetime import datetime


class PausableTimer:
    def __init__(self):
        self.timestarted: datetime = None
        self.timepaused: datetime = None
        self.paused = False

    def start(self):
        """Starts an internal timer by recording the current time"""
        self.timestarted = datetime.now()

    def pause(self):
        """Pauses the timer"""
        if self.timestarted is None:
            raise ValueError("Timer not started")
        if self.paused:
            raise ValueError("Timer is already paused")
        self.timepaused = datetime.now()
        self.paused = True

    def resume(self):
        """Resumes the timer by adding the pause time to the start time"""
        if self.timestarted is None:
            raise ValueError("Timer not started")
        if not self.paused:
            raise ValueError("Timer is not paused")
        pausetime = datetime.now() - self.timepaused
        self.timestarted = self.timestarted + pausetime
        self.paused = False

    def get(self) -> datetime:
        """Returns a timedelta object showing the amount of time
        elapsed since the start time, less any pauses"""
        if self.timestarted is None:
            raise ValueError("Timer not started")
        if self.paused:
            return self.timepaused - self.timestarted
        else:
            return datetime.now() - self.timestarted

    def reset(self):
        """Resets the timer"""
        self.timestarted = None
        self.timepaused = None
        self.paused = False
