from functools import wraps
import errno
import os
import signal
 
################################################################################
#                                                                              #
# Source: https://stackoverflow.com/questions/31822190/how-does-the-timeouttimelimit-decorator-work
#                                                                              #
################################################################################

class TimeoutError(Exception):
    pass
 
def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)
 
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
 
        return wraps(func)(wrapper)
 
    return decorator

################################################################################

class Node:
    """Game tree node object"""
    def __init__(self, player_to_move, move=None, parent=None):
        self.move = move
        self.parent = parent
        self.player_to_move = player_to_move

        self.visited = 0
        self.score = 0

        self.children = []
    
    def add_child(self, child):
        """Add a child node to the node

        Args:
            child (obj): Node object
        """
        self.children.append(child)
    
    def is_fully_expanded(self):
        """Check if node is fully expanded.
        """
        if self.children and all(c.visited>0 for c in self.children):
            return True
        else:
            return False