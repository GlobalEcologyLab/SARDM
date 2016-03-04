# Python modules

# Python extension module NumPy (requires extension installation)
import numpy as np

# Tool library module
from MpParameterBoundConstraintHelper import MpParameterBoundConstraintHelper

## Test Configuration
class TestMpFileParameterConfiguration :

    # Initialise with the test config
    def __init__(self) :

        # Configure parameter list in desired order
        self.parameters = ['single 1', 'single 2', 'single 3', 'single row', 'single column 1', 'single column 2', 'single column 3',
                           'matrix 1', 'matrix 2', 'matrix 3', 'matrix 4', 'layered matrix 1', 'layered matrix 2', 'layered matrix 3', 'layered matrix 4']

        self.parameter_constraints = {}
        self.parameter_constraints['single 1'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0 }]
        self.parameter_constraints['single 2'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 }]
        self.parameter_constraints['single 3'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'upper' : 1 }]
        self.parameter_constraints['single row 1'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 }]
        self.parameter_constraints['single column 1'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 }]
        self.parameter_constraints['single column 2'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1 }]
        self.parameter_constraints['single column 3'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 },
                                                         { 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1, 'from_row' : 2 }]
        self.parameter_constraints['matrix 1'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 },
                                                  { 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1, 'from_row' : 2 }]
        self.parameter_constraints['matrix 2'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 },
                                                  { 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1, 'from_row' : 2 }]
        self.parameter_constraints['matrix 3'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 },
                                                  { 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1, 'from_row' : 2 }]
        self.parameter_constraints['matrix 4'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'upper' : 1 },
                                                  { 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1, 'from_row' : 2 }]
        self.parameter_constraints['layered matrix 1'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0 }]
        self.parameter_constraints['layered matrix 2'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'upper' : 1 }]
        self.parameter_constraints['layered matrix 3'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1, 'from_row' : 2 }]
        self.parameter_constraints['layered matrix 4'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 },
                                                          { 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1, 'from_row' : 2 }]
        self.parameter_constraints['layered masked matrix 1'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0 }]
        self.parameter_constraints['layered masked matrix 2'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'upper' : 1 }]
        self.parameter_constraints['layered masked matrix 3'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1, 'from_row' : 2 }]
        self.parameter_constraints['layered masked matrix 4'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 },
                                                                 { 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1, 'from_row' : 2 }]

        self.likely_normal_stdevs_for_constraint_violation = 2

        # Configure parameter mapping section so that indicates if parameter is multi-layered
        self.parameter_mapping = { 'single 1' : {}, 'single 2' : {}, 'single 3' : {}, 'single row 1' : {},
                                   'single column 1' : {}, 'single column 2' : {}, 'single column 3' : {},
                                   'matrix 1' : {}, 'matrix 2' : {}, 'matrix 3' : {}, 'matrix 4' : {} }
        self.parameter_mapping['single 1'] = {}
        self.parameter_mapping['layered matrix 1'] = { 'layers' : 2 }
        self.parameter_mapping['layered matrix 2'] = { 'layers' : 2 }
        self.parameter_mapping['layered matrix 3'] = { 'layers' : 2 }
        self.parameter_mapping['layered matrix 4'] = { 'layers' : 2 }
        self.parameter_mapping['layered masked matrix 1'] = { 'layers' : 2 }
        self.parameter_mapping['layered masked matrix 2'] = { 'layers' : 2 }
        self.parameter_mapping['layered masked matrix 3'] = { 'layers' : 2 }
        self.parameter_mapping['layered masked matrix 4'] = { 'layers' : 2 }

# END TestMpFileParameterConfiguration
        
## Main program

# Create and configure the constraint helper
config = TestMpFileParameterConfiguration()
mp_constraint_helper = MpParameterBoundConstraintHelper(config)

# TEST 1: Single value matrices
# a) No constraints defined
# b) Lower value constraint only
# c) Lower and upper value constraints
# d) Upper value constraint applied to a value that already exceeds it

test_baseline_parameter_values = {}
test_baseline_parameter_values['single 0'] = np.array([[0.8]])
test_baseline_parameter_values['single 1'] = np.array([[0.8]])
test_baseline_parameter_values['single 2'] = np.array([[0.8]])
test_baseline_parameter_values['single 3'] = np.array([[1.1]])

# Calculate the maximum parameter bounds
mp_constraint_helper.calculateMinimumAndMaximumMulitpliersAndBounds(test_baseline_parameter_values)

# Print parameter values and maximum bounds
print 'Test 1:'
for key in sorted(test_baseline_parameter_values.keys()) :
    print 'parameter', key, 'value = '
    print test_baseline_parameter_values[key]
    print 'minimum multiplier = ', mp_constraint_helper.getMinimumParameterMultiplier(key)
    print 'maximum multiplier = ', mp_constraint_helper.getMaximumParameterMultiplier(key)
    print 'maximum bound = ', mp_constraint_helper.getMaximumParameterBound(key)
    if mp_constraint_helper.hasBoundConstraintForParameter(key) :
        print 'bound warning: ', mp_constraint_helper.generateBoundConstraintWarningForParameter(key)
    has_min_mult = mp_constraint_helper.hasMinimumMultiplierConstraintForParameter(key)
    has_max_mult = mp_constraint_helper.hasMaximumMultiplierConstraintForParameter(key)
    if has_min_mult or has_max_mult :
        print 'normal warning: ', mp_constraint_helper.generateLikelyDistributionConstraintWarningForParameter('normal', key, has_min_mult, has_max_mult)

# TEST 2: Single row matrix
# a) Lower and upper value constraints

test_baseline_parameter_values = {}
test_baseline_parameter_values['single row 1'] = np.array([[0.2, 0.4, 0.6, 0.8]])

# Calculate the maximum parameter bounds
mp_constraint_helper.calculateMinimumAndMaximumMulitpliersAndBounds(test_baseline_parameter_values)

# Print parameter values and maximum bounds
print '\nTest 2:'
for key in sorted(test_baseline_parameter_values.keys()) :
    print 'parameter', key, 'value = '
    print test_baseline_parameter_values[key]
    print 'minimum multiplier = ', mp_constraint_helper.getMinimumParameterMultiplier(key)
    print 'maximum multiplier = ', mp_constraint_helper.getMaximumParameterMultiplier(key)
    print 'maximum bound = ', mp_constraint_helper.getMaximumParameterBound(key)
    if mp_constraint_helper.hasBoundConstraintForParameter(key) :
        print 'bound warning: ', mp_constraint_helper.generateBoundConstraintWarningForParameter(key)
    has_min_mult = mp_constraint_helper.hasMinimumMultiplierConstraintForParameter(key)
    has_max_mult = mp_constraint_helper.hasMaximumMultiplierConstraintForParameter(key)
    if has_min_mult or has_max_mult :
        print 'normal warning: ', mp_constraint_helper.generateLikelyDistributionConstraintWarningForParameter('normal', key, has_min_mult, has_max_mult)

# TEST 3: Single column matrices
# a) Lower and upper value constraints
# b) Upper sum constraint (implicitly all rows)
# c) Lower and upper value constraints plus upper sum constraint from specified row

test_baseline_parameter_values = {}
test_baseline_parameter_values['single column 1'] = np.array([[0.2], [0.4], [0.6], [0.8]])
test_baseline_parameter_values['single column 2'] = np.array([[0.1], [0.2], [0.3], [0.2]])
test_baseline_parameter_values['single column 3'] = np.array([[0.8], [0.1], [0.2], [0.3]])

# Calculate the maximum parameter bounds
mp_constraint_helper.calculateMinimumAndMaximumMulitpliersAndBounds(test_baseline_parameter_values)

# Print parameter values and maximum bounds
print '\nTest 3:'
for key in sorted(test_baseline_parameter_values.keys()) :
    print 'parameter', key, 'value = '
    print test_baseline_parameter_values[key]
    print 'minimum multiplier = ', mp_constraint_helper.getMinimumParameterMultiplier(key)
    print 'maximum multiplier = ', mp_constraint_helper.getMaximumParameterMultiplier(key)
    print 'maximum bound = ', mp_constraint_helper.getMaximumParameterBound(key)
    if mp_constraint_helper.hasBoundConstraintForParameter(key) :
        print 'bound warning: ', mp_constraint_helper.generateBoundConstraintWarningForParameter(key)
    has_min_mult = mp_constraint_helper.hasMinimumMultiplierConstraintForParameter(key)
    has_max_mult = mp_constraint_helper.hasMaximumMultiplierConstraintForParameter(key)
    if has_min_mult or has_max_mult :
        print 'normal warning: ', mp_constraint_helper.generateLikelyDistributionConstraintWarningForParameter('normal', key, has_min_mult, has_max_mult)

# TEST 4: Matrix
# a) Lower and upper value constraints plus upper sum constraint from specified row
# b) Lower and upper value constraints plus upper sum constraint applied to a sum that already exceeds it
# c) Lower and upper value constraints plus upper sum constraint applied to matrix with zero and small entries
# d) Upper value constraint plus upper sum constraint applied to matrix with zero and small entries

test_baseline_parameter_values = {}
test_baseline_parameter_values['matrix 1'] = np.array([[0.6, 0.5], [0.4, 0.3], [0.3, 0.5]])
test_baseline_parameter_values['matrix 2'] = np.array([[0.6, 0.5], [0.4, 0.3], [0.7, 0.5]])
test_baseline_parameter_values['matrix 3'] = np.array([[0.3, 0.4], [0.1, 0.0], [0.0, 0.2]])
test_baseline_parameter_values['matrix 4'] = np.array([[0.3, 0.4], [0.1, 0.0], [0.0, 0.2]])

# Calculate the maximum parameter bounds
mp_constraint_helper.calculateMinimumAndMaximumMulitpliersAndBounds(test_baseline_parameter_values)

# Print parameter values and maximum bounds
print '\nTest 4:'
for key in sorted(test_baseline_parameter_values.keys()) :
    print 'parameter', key, 'value = '
    print test_baseline_parameter_values[key]
    print 'minimum multiplier = ', mp_constraint_helper.getMinimumParameterMultiplier(key)
    print 'maximum multiplier = ', mp_constraint_helper.getMaximumParameterMultiplier(key)
    print 'maximum bound = ', mp_constraint_helper.getMaximumParameterBound(key)
    if mp_constraint_helper.hasBoundConstraintForParameter(key) :
        print 'bound warning: ', mp_constraint_helper.generateBoundConstraintWarningForParameter(key)
    has_min_mult = mp_constraint_helper.hasMinimumMultiplierConstraintForParameter(key)
    has_max_mult = mp_constraint_helper.hasMaximumMultiplierConstraintForParameter(key)
    if has_min_mult or has_max_mult :
        print 'normal warning: ', mp_constraint_helper.generateLikelyDistributionConstraintWarningForParameter('normal', key, has_min_mult, has_max_mult)

# TEST 5: Check Modified Matrix Constraint Violations
# a) No constraints registered for parameter
# b) No violations for registered parameter
# c) Lower & upper value plus column sum violations

values_0 = np.array([[1.1, -2], [0.8, 0.3], [0.3, 0.5]])
values_1 = np.array([[0.6, 0.5], [0.4, 0.3], [0.3, 0.5]])
values_2 = np.array([[1.1, -2], [0.8, 0.3], [0.3, 0.5]])

constraint_violations_0 = mp_constraint_helper.checkParameterValuesAgainstConstraints('matrix 0', values_0)
constraint_violations_1 = mp_constraint_helper.checkParameterValuesAgainstConstraints('matrix 1', values_1)
constraint_violations_2 = mp_constraint_helper.checkParameterValuesAgainstConstraints('matrix 2', values_2)

print '\nTest 5:'
print 'violations 0: ', constraint_violations_0
print 'violations 1: ', constraint_violations_1
print 'violations 2: ', constraint_violations_2

print mp_constraint_helper.parameterConstraintViolationsToString('matrix 0', constraint_violations_0)
print mp_constraint_helper.parameterConstraintViolationsToString('matrix 1', constraint_violations_1)
print mp_constraint_helper.parameterConstraintViolationsToString('matrix 2', constraint_violations_2)

# TEST 6: Check constraints and violations with multiple layered matrices
# a) Lower cell constraint
# b) Upper cell constraint
# c) Column sum constraint
# d) Lower & upper value plus column sum violations

test_baseline_parameter_values = {}
test_baseline_parameter_values['layered matrix 1'] = np.array([[[0.9, 0.4], [0.3, 0.3], [0.5, 0.2]], [[0.6, 0.5], [0.4, 0.3], [0.3, 0.2]]])
test_baseline_parameter_values['layered matrix 2'] = np.array([[[0.9, 0.4], [0.3, 0.3], [0.5, 0.2]], [[0.6, 0.5], [0.4, 0.3], [0.3, 0.2]]])
test_baseline_parameter_values['layered matrix 3'] = np.array([[[0.9, 0.4], [0.3, 0.3], [0.5, 0.2]], [[0.6, 0.5], [0.4, 0.3], [0.3, 0.2]]])

# Calculate the maximum parameter bounds
mp_constraint_helper.calculateMinimumAndMaximumMulitpliersAndBounds(test_baseline_parameter_values)

# Print parameter values and maximum bounds
print '\nTest 6'
for key in sorted(test_baseline_parameter_values.keys()) :
    print 'parameter', key, 'value = '
    print test_baseline_parameter_values[key]
    print 'minimum multiplier = ', mp_constraint_helper.getMinimumParameterMultiplier(key)
    print 'maximum multiplier = ', mp_constraint_helper.getMaximumParameterMultiplier(key)
    print 'maximum bound = ', mp_constraint_helper.getMaximumParameterBound(key)
    if mp_constraint_helper.hasBoundConstraintForParameter(key) :
        print 'bound warning: ', mp_constraint_helper.generateBoundConstraintWarningForParameter(key)
    has_min_mult = mp_constraint_helper.hasMinimumMultiplierConstraintForParameter(key)
    has_max_mult = mp_constraint_helper.hasMaximumMultiplierConstraintForParameter(key)
    if has_min_mult or has_max_mult :
        print 'normal warning: ', mp_constraint_helper.generateLikelyDistributionConstraintWarningForParameter('normal', key, has_min_mult, has_max_mult)

# Test violations
values = np.array([[[1.1, 0.5], [0.4, 0.3], [0.3, 0.5]], [[0.6, -2], [0.8, 0.3], [0.3, 0.5]]])
constraint_violations = mp_constraint_helper.checkParameterValuesAgainstConstraints('layered matrix 4', values)
print 'Testing violations for\n', values
print 'violations: ', constraint_violations

# TEST 7: Check constraints and violations with multiple layered masked matrices (same as Test 6 with mask)
# a) Lower cell constraint
# b) Upper cell constraint
# c) Column sum constraint
# d) Lower & upper value plus column sum violations

mask = ([[[0, 0], [0, 1], [0, 1]], [[0, 0], [0, 1], [0, 1]]])
old_test_baseline_parameter_values = test_baseline_parameter_values.copy()
test_baseline_parameter_values = {}
test_baseline_parameter_values['layered masked matrix 1'] = np.ma.masked_array(old_test_baseline_parameter_values['layered matrix 1'], mask=mask)
test_baseline_parameter_values['layered masked matrix 2'] = np.ma.masked_array(old_test_baseline_parameter_values['layered matrix 2'], mask=mask)
test_baseline_parameter_values['layered masked matrix 3'] = np.ma.masked_array(old_test_baseline_parameter_values['layered matrix 3'], mask=mask)

# Calculate the maximum parameter bounds
mp_constraint_helper.calculateMinimumAndMaximumMulitpliersAndBounds(test_baseline_parameter_values)

# Print parameter values and maximum bounds
print '\nTest 7'
for key in sorted(test_baseline_parameter_values.keys()) :
    print 'parameter', key, 'value = '
    print test_baseline_parameter_values[key]
    print 'minimum multiplier = ', mp_constraint_helper.getMinimumParameterMultiplier(key)
    print 'maximum multiplier = ', mp_constraint_helper.getMaximumParameterMultiplier(key)
    print 'maximum bound = ', mp_constraint_helper.getMaximumParameterBound(key)
    if mp_constraint_helper.hasBoundConstraintForParameter(key) :
        print 'bound warning: ', mp_constraint_helper.generateBoundConstraintWarningForParameter(key)
    has_min_mult = mp_constraint_helper.hasMinimumMultiplierConstraintForParameter(key)
    has_max_mult = mp_constraint_helper.hasMaximumMultiplierConstraintForParameter(key)
    if has_min_mult or has_max_mult :
        print 'normal warning: ', mp_constraint_helper.generateLikelyDistributionConstraintWarningForParameter('normal', key, has_min_mult, has_max_mult)

# Test violations
values = np.ma.masked_array(np.array([[[1.1, 0.5], [0.4, 0.3], [0.3, 0.5]], [[0.6, -2], [0.8, 0.3], [0.3, 0.5]]]), mask=mask)
constraint_violations = mp_constraint_helper.checkParameterValuesAgainstConstraints('layered masked matrix 4', values)
print 'Testing violations for\n', values
print 'violations: ', constraint_violations
