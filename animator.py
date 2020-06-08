"""
module containing logic associated with automated placement, scaling and rotation
of UDS files over time
"""
import pyglet
class UDSAnimator:
    """
    Class defining automated movement of renderInstances
    handles scheduling of frame updates and
    """
    def __init__(self):
        #mapping of instances to the animating function(s)
        self.dispatchList = {}
        self.running = False
        self.interval = 1/20 #frequency of calls in s
        self.start()

    @property
    def interval(self):
        return self.__interval

    @interval.setter
    def interval(self, interval):
        self.__interval = interval
        if self.running:
            #we want to restart the animations at the correct interval if we are already runnint
            self.stop()
            self.start()

    def spin_instance(self, instance):
        def ret():
            rate =0.1
            r1, r2, r3 = instance.rotation
            instance.rotation = (r1, r2, r3+rate)
        self.dispatchList[id(instance)] = ret

    def dispatch_animations(self, dt):
        """calls all functions queued for dispatch"""
        for instanceid in self.dispatchList.keys():
            self.dispatchList[instanceid]()

    def stop(self):
        pyglet.clock.unschedule(self.dispatch_animations)
        self.running = False

    def start(self):
        pyglet.clock.schedule_interval(self.dispatch_animations, self.interval)
        self.running = True

def animatorDemo(animator, instance):
    print("Running animation demo...\n")
    animator.spin_instance(instance)
