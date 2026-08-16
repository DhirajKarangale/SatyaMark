import time
import threading
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.states = {}
        self.lock = threading.RLock()
        
    def _init_state(self, service_name):
        with self.lock:
            if service_name not in self.states:
                self.states[service_name] = 'disconnected'
                
    def set_status(self, service_name, status):
        with self.lock:
            self._init_state(service_name)
            if self.states[service_name] != status:
                self.states[service_name] = status
                logger.info(f"[ConnectionManager] {service_name} is now {status}")
                    
    def get_status(self, service_name):
        with self.lock:
            self._init_state(service_name)
            return self.states[service_name]
            
    def ensure_connection(self, service_name, ping_fn=None):
        self._init_state(service_name)
        
        if self.get_status(service_name) == 'connected':
            return
            
        logger.info(f"[ConnectionManager] Operation paused for {service_name}. Current status: {self.get_status(service_name)}")
        
        with self.lock:
            if self.states[service_name] == 'disconnected':
                self.states[service_name] = 'connecting'
                
        while True:
            status = self.get_status(service_name)
            if status == 'connected':
                break
                
            if status == 'connecting':
                if ping_fn:
                    try:
                        ping_fn()
                        self.set_status(service_name, 'connected')
                        logger.info(f"[ConnectionManager] Operation resumed for {service_name}.")
                        break
                    except Exception as e:
                        time.sleep(2)
                else:
                    time.sleep(1)

connection_manager = ConnectionManager()
