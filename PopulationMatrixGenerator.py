# Python module
#import itertools

# Python extension module NumPy (requires extension installation)
import numpy as np

## Population matrix generator
## * Generates population matrices from distance function definitions for:
##   * Dispersal/migration
##   * Correlation
class PopulationMatrixGenerator :

    # Initialise with the population coordinates (numpy array with X,Y pair for each poplation)
    def __init__(self, population_coordinates) :

        # Number of populations
        self.populations = population_coordinates.shape[0]

        # Population coordinates
        self.population_coordinates = population_coordinates

        # Inter-population distance matrix (stored once calculated)
        self.inter_population_distances = None

    # Calculate matrix from details
    def calculateMatrix(self, details) :
        matrix = None
        if details.has_key('matrix') and details.has_key('parameters') :
            if details['matrix'] == 'dispersal' :
                a = details['parameters']['a']
                b = details['parameters']['b']
                c = details['parameters']['c']
                Dmax = details['parameters']['Dmax']
                matrix = self.calculateDispersalMatrix(a, b, c, Dmax)
            elif details['matrix'] == 'correlation' :
                a = details['parameters']['a']
                b = details['parameters']['b']
                c = details['parameters']['c']
                matrix = self.calculateCorrelationMatrix(a, b, c)
        return matrix

    # Calculate dispersal/migration matrix
    def calculateDispersalMatrix(self, a, b, c, Dmax) :

        # Calculate inter-population distances if needed
        if self.inter_population_distances == None : # type(self.inter_population_distances) != np.ndarray :
            self.calculateInterPopulationDistances()

        # Construct the dispersal matrix
        dispersal_matrix = np.zeros((self.populations, self.populations))
        for i in range(self.populations) :
            for j in range(self.populations) :
                Dij = self.inter_population_distances[i,j]
                if i != j and Dij <= Dmax :
                    dispersal_matrix[i,j] = a*np.exp(-1*Dij**c/b)

        return dispersal_matrix
    
    # Calculate correlation matrix
    def calculateCorrelationMatrix(self, a, b, c) :

        # Calculate inter-population distances if needed
        if self.inter_population_distances == None : # type(self.inter_population_distances) != np.ndarray :
            self.calculateInterPopulationDistances()

        # Construct the correlation matrix
        correlation_matrix = np.zeros((self.populations, self.populations))
        for i in range(self.populations) :
            for j in range(self.populations) :
                Dij = self.inter_population_distances[i,j]
                if i > j :
                    correlation_matrix[i,j] = a*np.exp(-1*Dij**c/b)

        return correlation_matrix

    # Calculate inter-population distances
    def calculateInterPopulationDistances(self) :
        x_distances = np.zeros((self.populations, self.populations))
        y_distances = np.zeros((self.populations, self.populations))
        for i in range(self.populations) :
            for j in range(self.populations) :
               x_distances[i,j] = self.population_coordinates[i,0] - self.population_coordinates[j,0]
               y_distances[i,j] = self.population_coordinates[i,1] - self.population_coordinates[j,1]
        self.inter_population_distances = np.hypot(x_distances, y_distances)
