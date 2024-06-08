class WrongDrone(Exception):
    def __init__(self, serverDroneName, currentDroneName):
        super().__init__(f"The drone active on the server, {serverDroneName}," + \
                          f"does not match \nthe drone class currently being used, {currentDroneName}")
        self.nameOfDroneOnServer = serverDroneName