import threading
from IntelligenceHandler.IntelligenceHandler import IntelligenceHandler

def DroneController(drone):
  class DroneController(drone):
      def __init__(self, workerAddress, interfaceAddress, 
                  manualControlOnly):
          #The web address that handles the worker objects,
          #machines handling object-detection, depth-perception,
          #and LLM inference. 
          self.workerAddress = workerAddress

          #The web address which the drone and human teammates connect to. 
          self.interfaceAddress = interfaceAddress
          self.manualControlOnly = manualControlOnly

          self.movementThread = threading.Thread(target=self.createMovementHandler)
          self.intelThread = threading.Thread(target=self.createIntelligenceHandler)
          
          #instantiate parent object, the specific drone be utilized
          super().__init__(self.interfaceAddress)

          self.intelligence = IntelligenceHandler(self, 
            self.workerAddress)
          
          self.startDrone()

      # Controls system/drone action/movement 
      def createMovementHandler(self) :
        self.movementController.run()

      def completedAction(self):
         self.movementController.completedAction()
      
      #This handles the worker pool connections:
      #the drone imagery, llm response, etc. 
      #Additionally, houses all of the data asscoiated
      #with the mentioned items. It is integral to 
      #to the system. 
      def createIntelligenceHandler(self) :
          self.intelligence.run()
      
      def startDrone(self):
        self.movementThread.start()
        self.intelThread.start()
        self.movementThread.join()

  return DroneController