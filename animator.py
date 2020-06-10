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
        self.interval = 1/20 #frequency of calls in seconds
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

    def spin_instance(self, instance, angularVelocity=[0,0,0.1]):
        def ret(dt):
            dAngle = [angularVelocity[0]*dt, angularVelocity[1]*dt, angularVelocity[2]*dt]
            r1, r2, r3 = instance.rotation
            instance.rotation = (r1+dAngle[0], r2+dAngle[1], r3+dAngle[2])
        self.dispatchList[id(instance)] = ret

    def dispatch_animations(self, dt):
        """calls all functions queued for dispatch"""
        for instanceid in self.dispatchList.keys():
            self.dispatchList[instanceid](dt)

    def stop(self):
        pyglet.clock.unschedule(self.dispatch_animations)
        self.running = False

    def start(self):
        pyglet.clock.schedule_interval(self.dispatch_animations, self.interval)
        self.running = True

def animatorDemo(animator, instance):
    print("Running animation demo...\n")
    animator.spin_instance(instance)
