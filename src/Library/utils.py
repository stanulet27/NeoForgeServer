import jax.numpy as np

def get_location_function(points,checks):
    def location_function(point):
        # print("LOCATION FUNCTION")
        # print(checks.shape)
        # print(checks[np.asarray(points==point).all(axis=1).nonzero(size=1)][0])
        return checks[np.asarray(points==point).all(axis=1).nonzero(size=1)][0]
    return location_function

def get_value_function(points,displacements,dim):
    def value_function(point):
        # print("VALUE FUNCTION")
        # print(displacements.shape)
        # print(displacements[np.asarray(points==point).all(axis=1).nonzero(size=1)][0][dim])
        return displacements[np.asarray(points==point).all(axis=1).nonzero(size=1)][0][dim]
    return value_function


