# Tool library module
from PopulationMatrixGenerator import PopulationMatrixGenerator

# Python extension module NumPy (requires extension installation)
import numpy as np

population_coordinates = np.array([
[0, 0],
[3, 4],
[4, 5]])

population_matrix_generator = PopulationMatrixGenerator(population_coordinates)

print 'Loaded', population_matrix_generator.populations, 'populations with coordinates:'
print population_matrix_generator.population_coordinates

# TEST 1: Calculate inter-population distances
print '\nTEST 1: Calculated inter-population distances:'
population_matrix_generator.calculateInterPopulationDistances()
print population_matrix_generator.inter_population_distances

# Using realistic values from SandLizard_baseline.mp
population_coordinates = np.array([
[18000, 95000],
[18000, 95750],
[18750, 95000],
[18750, 95750],
[18000, 96500],
[18750, 96500],
[19500, 95000],
[19500, 95750]])

population_matrix_generator = PopulationMatrixGenerator(population_coordinates)

print '\nLoaded', population_matrix_generator.populations, 'populations with coordinates:'
print population_matrix_generator.population_coordinates

# TEST 2: Calculate dispersal/migration matrix Mij
print '\nTEST 2: Calculate dispersal/migration matrix Mij'
a = 0.400
b = 550.0
c = 1.000
Dmax = 1200.0
print 'Using a = ', a, ', b = ', b, ', c = ', c, ', Dmax = ', Dmax
print 'Expected Mij ='
print np.array([[0, 0.10228, 0.10229, 0.05815, 0, 0, 0, 0],
 [0.10229, 0, 0.05815, 0.10229, 0.10229, 0.05815, 0, 0],
 [0.10229, 0.05815, 0, 0.10229, 0, 0, 0.10229, 0.05815],
 [0.05815, 0.10229, 0.10229, 0, 0.05815, 0.10229, 0.05815, 0.10229],
 [0, 0.10229, 0, 0.05815, 0, 0.10229, 0, 0],
 [0, 0.05815, 0, 0.10229, 0.10229, 0, 0, 0.05815],
 [0, 0, 0.10229, 0.05815, 0, 0, 0, 0.10229],
 [0, 0, 0.05815, 0.10229, 0, 0.05815, 0.10229, 0]])
print 'Calculated Mij =\n', population_matrix_generator.calculateDispersalMatrix(a, b, c, Dmax).round(5)

 # TEST 3: Calculate correlation matrix Cij
print '\nTEST 3: Calculate correlation matrix Cij'
a = 1.000
b = 8000.00
c = 1.00
print 'Using a = ', a, ', b = ', b, ', c = ', c
print 'Expected Cij ='
print np.array([[0, 0, 0, 0, 0, 0, 0, 0],
 [0.91051, 0, 0, 0, 0, 0, 0, 0],
 [0.91051, 0.87583, 0, 0, 0, 0, 0, 0],
 [0.87583, 0.91051, 0.91051, 0, 0, 0, 0, 0],
 [0.82903, 0.91051, 0.81088, 0.87583, 0, 0, 0, 0],
 [0.81088, 0.87583, 0.82903, 0.91051, 0.91051, 0, 0, 0],
 [0.82903, 0.81088, 0.91051, 0.87583, 0.76708, 0.81088, 0, 0],
 [0.81088, 0.82903, 0.87583, 0.91051, 0.81088, 0.87583, 0.91051, 0]])
print 'Calculated Cij =\n', population_matrix_generator.calculateCorrelationMatrix(a, b, c).round(5)
