# Python modules

# Python extension module NumPy (requires extension installation)
import numpy as np

## MP parameter constraint helper
## * Defines the types of constraints that are possible
## * Calculates minimum and maximum multipliers and maximum bound values for MP parameters given configured constraints
class MpParameterBoundConstraintHelper :

    # Define the types of constraints that are possible (static variables)

    # Limited cell values (lower and upper constraint applied to all matrix cells)
    LIMITED_CELL_VALUES = 1

    # Limited column sums (upper constraint for sum of column values from_row) 
    LIMITED_COLUMN_SUMS = 2

    # Define constraint application strategies
    LIMIT_BOUNDS = 1
    WARNING_ONLY = 2
    
    # Initialise with the MP file parameter config
    def __init__(self, mp_file_parameter_config) :

        self.config = mp_file_parameter_config

        # Minimum and maximum parameter multipliers (%)
        self.minimum_parameter_multipliers = {}
        self.maximum_parameter_multipliers = {}

        # Maximum parameter bounds (%)
        self.maximum_parameter_bounds = {}

    # Method determines whether or not a minimum multiplier constraint exists for a parameter
    def hasMinimumMultiplierConstraintForParameter(self, parameter_key) :
        if self.minimum_parameter_multipliers.has_key(parameter_key) :
            return True
        else :
            return False

    # Method determines whether or not a minimum multiplier constraint exists for a parameter
    def hasMaximumMultiplierConstraintForParameter(self, parameter_key) :
        if self.maximum_parameter_multipliers.has_key(parameter_key) :
            return True
        else :
            return False

    # Method determines whether or not a bound constraint exists for a parameter
    def hasBoundConstraintForParameter(self, parameter_key) :
        if self.maximum_parameter_bounds.has_key(parameter_key) :
            return True
        else :
            return False

    # Method retrieves minimum parameter multiplier value for a specified parameter
    def getMinimumParameterMultiplier(self, parameter_key) :
        if self.hasMinimumMultiplierConstraintForParameter(parameter_key) :
            return self.minimum_parameter_multipliers[parameter_key]['value']
        else :
            return None

    # Method retrieves maximum parameter multiplier value for a specified parameter
    def getMaximumParameterMultiplier(self, parameter_key) :
        if self.hasMaximumMultiplierConstraintForParameter(parameter_key) :
            return self.maximum_parameter_multipliers[parameter_key]['value']
        else :
            return None

    # Method retrieves maximum parameter bound value for a specified parameter
    def getMaximumParameterBound(self, parameter_key) :
        if self.hasBoundConstraintForParameter(parameter_key) :
            return self.maximum_parameter_bounds[parameter_key]['value']
        else :
            return None

    # Method generates a warning message when a bound constraint on a parameter is exceeded
    def generateBoundConstraintWarningForParameter(self, parameter_key) :
        warning_message = 'A bound greater than ' + ('%.1f' % self.getMaximumParameterBound(parameter_key))
        warning_message += ('% may result in ' + parameter_key)
        if self.maximum_parameter_bounds[parameter_key]['caused_by_type'] == MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES :
            warning_message += ' values '
        elif self.maximum_parameter_bounds[parameter_key]['caused_by_type'] == MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS :
            warning_message += ' column sums '
        corresponding_constraint = self.findCorrespondingConfiguredConstraintForParameter(self.maximum_parameter_bounds[parameter_key]['caused_by_type'], parameter_key)
        if self.maximum_parameter_bounds[parameter_key]['bound'] == 'lower' :
            warning_message += ('lower than ' + str(corresponding_constraint['lower']) + '.')
        elif self.maximum_parameter_bounds[parameter_key]['bound'] == 'upper' :
            warning_message += ('greater than ' + str(corresponding_constraint['upper']) + '.')
        return warning_message

    # Method generates a warning message when the specified distribution settings are likely to result in a constraint violation for parameter is encountered
    def generateLikelyDistributionConstraintWarningForParameter(self, distribution, parameter_key, likely_lower_constraint_violation, likely_upper_constraint_violation) :
        warning_message = 'The ' + distribution + ' distribution settings entered may result in ' + parameter_key
        if likely_lower_constraint_violation :
            corresponding_constraint = self.findCorrespondingConfiguredConstraintForParameter(self.minimum_parameter_multipliers[parameter_key]['caused_by_type'], parameter_key)
            warning_message += (' values less than ' + str(corresponding_constraint['lower']))
            if distribution in ['uniform', 'triangular', 'lognormal', 'beta'] :
                warning_message += (' (when lower < ' + ('%.1f' % self.getMinimumParameterMultiplier(parameter_key)) + '%)')
        if likely_lower_constraint_violation and likely_upper_constraint_violation :
            warning_message += ' and'
        if likely_upper_constraint_violation :
            caused_by_type = self.maximum_parameter_multipliers[parameter_key]['caused_by_type']
            if caused_by_type == MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES :
                warning_message += ' values '
            elif caused_by_type == MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS :
                warning_message += ' column sums '
            corresponding_constraint = self.findCorrespondingConfiguredConstraintForParameter(caused_by_type, parameter_key)
            warning_message += ('greater than ' + str(corresponding_constraint['upper']))
            if distribution in ['uniform', 'triangular', 'beta'] :
                warning_message += (' (when upper > ' + ('%.1f' % self.getMaximumParameterMultiplier(parameter_key)) + '%)')
        warning_message += '.'
        return warning_message

    # Method finds the configured constraint corresponding to the given constraint type for the parameter key
    def findCorrespondingConfiguredConstraintForParameter(self, constraint_type, parameter_key) :
        corresponding_constraint = {}
        for constraint in self.config.parameter_constraints[parameter_key] :
            if constraint['constraint_type'] == constraint_type :
                corresponding_constraint = constraint
        return corresponding_constraint

    # Method calculates the minimum and maximum multipliers and maximum bounds (%) for the baseline parameter values using configured constraints
    def calculateMinimumAndMaximumMulitpliersAndBounds(self, baseline_parameter_values) :

        for key, parameter_value in baseline_parameter_values.items() :

            # If there are constraints configured for the parameter
            if self.config.parameter_constraints.has_key(key) :

                # Initialise parameter bound at 100%
                self.maximum_parameter_bounds[key] = { 'value' : 100, 'caused_by_type' : '', 'bound' : '' }

                # Assess each constraint for the parameter
                for constraint in self.config.parameter_constraints[key] :

                    # Limited cell value constraint
                    if constraint['constraint_type'] == MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES :

                        # Find the minimum and maximum parameter values
                        maximum_cell_value = parameter_value.flatten().max()

                        # Lower value constraint
                        if constraint.has_key('lower') :
                            self.minimum_parameter_multipliers[key] = { 'value' : 0, 'caused_by_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES }
                            minimum_cell_value = parameter_value.flatten().min()
                            if minimum_cell_value :
                                minimum_multiplier = (constraint['lower']/minimum_cell_value)*100
                                if minimum_multiplier >= self.minimum_parameter_multipliers[key]['value'] :
                                    self.minimum_parameter_multipliers[key]['value'] = minimum_multiplier
                                maximum_bound = (1 - constraint['lower']/minimum_cell_value)*100
                                if maximum_bound <= self.maximum_parameter_bounds[key]['value'] :
                                    self.maximum_parameter_bounds[key]['value'] = maximum_bound
                                    self.maximum_parameter_bounds[key]['caused_by_type'] = MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES
                                    self.maximum_parameter_bounds[key]['bound'] = 'lower'
                            if not(self.maximum_parameter_bounds[key]['caused_by_type']) :
                                self.maximum_parameter_bounds[key]['caused_by_type'] = MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES
                            if not(self.maximum_parameter_bounds[key]['bound']) :
                                self.maximum_parameter_bounds[key]['bound'] = 'lower'
     
                        # Upper value constraint
                        if constraint.has_key('upper') :
                            if not(self.maximum_parameter_multipliers.has_key(key)) :
                                self.maximum_parameter_multipliers[key] = { 'value' : float('+inf'), 'caused_by_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES }
                            maximum_cell_value = parameter_value.flatten().max()
                            if maximum_cell_value :
                                maximum_multiplier = (constraint['upper']/maximum_cell_value)*100
                                if maximum_multiplier <= self.maximum_parameter_multipliers[key]['value'] :
                                    self.maximum_parameter_multipliers[key]['value'] = maximum_multiplier
                                    self.maximum_parameter_multipliers[key]['caused_by_type'] = MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES
                                maximum_bound = (constraint['upper']/maximum_cell_value - 1)*100
                                if maximum_bound < 0 :
                                    maximum_bound = 0
                                if maximum_bound <= self.maximum_parameter_bounds[key]['value'] :
                                    self.maximum_parameter_bounds[key]['value'] = maximum_bound
                                    self.maximum_parameter_bounds[key]['caused_by_type'] = MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES
                                    self.maximum_parameter_bounds[key]['bound'] = 'upper'
                            if not(self.maximum_parameter_bounds[key]['caused_by_type']) :
                                self.maximum_parameter_bounds[key]['caused_by_type'] = MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES
                            if not(self.maximum_parameter_bounds[key]['bound']) :
                                self.maximum_parameter_bounds[key]['bound'] = 'upper'
                            
                    # Limited column sum constraint
                    elif constraint['constraint_type'] == MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS :
                        if constraint.has_key('upper') : # must be defined
                            if not(self.maximum_parameter_multipliers.has_key(key)) :
                                self.maximum_parameter_multipliers[key] = { 'value' : float('+inf'), 'caused_by_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES }
                            from_row = 1
                            if constraint.has_key('from_row') :
                                from_row = constraint['from_row']
                            if self.config.parameter_mapping[key].has_key('layers') : # Handle layers differently
                                maximum_column_sum = parameter_value[:,(from_row-1):].sum(1).max()
                            else :
                                maximum_column_sum = parameter_value[(from_row-1):].sum(0).max()
                            if maximum_column_sum :
                                maximum_multiplier = (constraint['upper']/maximum_column_sum)*100
                                if maximum_multiplier <= self.maximum_parameter_multipliers[key]['value'] :
                                    self.maximum_parameter_multipliers[key]['value'] = maximum_multiplier
                                    self.maximum_parameter_multipliers[key]['caused_by_type'] = MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS
                                maximum_bound = (constraint['upper']/maximum_column_sum - 1)*100
                                if maximum_bound < 0 :
                                    maximum_bound = 0
                                if maximum_bound <= self.maximum_parameter_bounds[key]['value'] :
                                    self.maximum_parameter_bounds[key]['value'] = maximum_bound
                                    self.maximum_parameter_bounds[key]['caused_by_type'] = MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS
                                    self.maximum_parameter_bounds[key]['bound'] = 'upper'
                            if not(self.maximum_parameter_bounds[key]['caused_by_type']) :
                                self.maximum_parameter_bounds[key]['caused_by_type'] = MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS
                            if not(self.maximum_parameter_bounds[key]['bound']) :
                                self.maximum_parameter_bounds[key]['bound'] = 'upper'

    # Method checks the modified parameter value(s) against the constraints for a specified parameter
    def checkParameterValuesAgainstConstraints(self, parameter_key, parameter_value) :

        # Returns a list of constraint violations
        constraint_violations = []

        if self.config.parameter_constraints.has_key(parameter_key) :

            for constraint in self.config.parameter_constraints[parameter_key] :

                # Limited cell value constraint
                if constraint['constraint_type'] == MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES :

                    # Lower value constraint
                    if constraint.has_key('lower') :
                        minimum_cell_value = parameter_value.flatten().min()
                        if minimum_cell_value < constraint['lower'] :
                            constraint_violations.append({ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'violation' : 'lower' })

                    # Upper value constraint
                    if constraint.has_key('upper') :
                        maximum_cell_value = parameter_value.flatten().max()
                        if maximum_cell_value > constraint['upper'] :
                            constraint_violations.append({ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'violation' : 'upper' })

                # Limited column sum constraint
                elif constraint['constraint_type'] == MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS :
                    if constraint.has_key('upper') : # must be defined
                        from_row = 1
                        if constraint.has_key('from_row') :
                            from_row = constraint['from_row']
                        if self.config.parameter_mapping[parameter_key].has_key('layers') : # Handle layers differently
                            maximum_column_sum = parameter_value[:,(from_row-1):].sum(1).max()
                        else :
                            maximum_column_sum = parameter_value[(from_row-1):].sum(0).max()
                        if maximum_column_sum > constraint['upper'] :
                            constraint_violations.append({ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'violation' : 'upper' })

        return constraint_violations

    # Method constructs printable string for parameter constraint violations for specified parameter (for notes in data frame)
    def parameterConstraintViolationsToString(self, parameter_key, violations) :

        printable_string = parameter_key + ': '
        count = 0

        for violation in violations :

            if count :
                printable_string += '; '
            count += 1
            
            # Process constraint type
            if violation['constraint_type'] == MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES :
                printable_string += 'values '
            elif violation['constraint_type'] == MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS :
                printable_string += 'column sums '

            # Find corresponding configured constraint
            corresponding_constraint = self.findCorrespondingConfiguredConstraintForParameter(violation['constraint_type'], parameter_key)

            # Process constraint
            if corresponding_constraint :
                if violation['violation'] == 'lower' :
                    printable_string += ('less than ' + str(corresponding_constraint['lower']))
                elif violation['violation'] == 'upper' :
                    printable_string += ('greater than ' + str(corresponding_constraint['upper']))    

        return printable_string
