# Python module
import itertools

# Python extension modules (require extension installations)
import numpy as np
from scipy.stats import futil
from scipy.sparse.csgraph import _validation
from scipy.stats import uniform, norm, triang, lognorm, beta

## Sample generator
## * Generates sample multipliers from the specified distribution or bounds for the:
##   * Latin Hypercube sampling method for the following distributions:
##     1. Uniform distribution
##     2. Normal (Gaussian) distribution
##     3. Triangular distribution 
##     4. Lognormal distribution 
##     5. Beta distribution 
##   * Random (uniform distribution) sampling method
##   * Full factorial of low, mid and high values
## * Applies the multipliers to modify a mapped parameter set
class SampleGenerator :

    # Method generates Latin Hypercube sampled multipliers for the selected distribution specified for each parameter (via dictionary)
    def generateLatinHypercubeSampledMultipliers(self, specification_map, number_samples) :
            
        # Construct sets of random sampled multipliers from the selected distribution for each parameter
        multiplier_sets = {}
        for key, specification in specification_map.items() :

            # Generate stratified random probability values for distribution generation via inverse CDF
            stratified_random_probabilities = ((np.array(range(number_samples)) + np.random.random(number_samples))/number_samples)

            # Use stratified random probability values to generate stratified samples from selected distribution via inverse CDF
            distribution = specification['distribution']
            if distribution == 'uniform' :
                lower = specification['settings']['lower']
                base = specification['settings']['upper'] - lower
                multiplier_sets[key] = uniform.ppf(stratified_random_probabilities, loc=lower, scale=base).tolist()
            elif distribution == 'normal' :
                mean = specification['settings']['mean']
                std_dev = specification['settings']['std_dev']
                multiplier_sets[key] = norm.ppf(stratified_random_probabilities, loc=mean, scale=std_dev).tolist()
            elif distribution == 'triangular' :
                a = specification['settings']['a']
                base = specification['settings']['b'] - a
                c_std = (specification['settings']['c'] - a)/base
                multiplier_sets[key] = triang.ppf(stratified_random_probabilities, c_std, loc=a, scale=base).tolist()
            elif distribution == 'lognormal' :
                lower = specification['settings']['lower']
                scale = specification['settings']['scale']
                sigma = specification['settings']['sigma']
                multiplier_sets[key] = lognorm.ppf(stratified_random_probabilities, sigma, loc=lower, scale=scale).tolist()
            elif distribution == 'beta' :
                lower = specification['settings']['lower']
                base = specification['settings']['upper'] - lower
                a = specification['settings']['alpha']
                b = specification['settings']['beta']
                multiplier_sets[key] = beta.ppf(stratified_random_probabilities, a, b, loc=lower, scale=base).tolist()

        # Randomly select from sampled multiplier sets without replacement to form multipliers (dictionaries)
        sampled_multipliers = []
        for i in range(number_samples) :
            sampled_multiplier = {}
            for key, multiplier_set in multiplier_sets.items() :
                random_index = np.random.randint(len(multiplier_set))
                sampled_multiplier[key] = multiplier_set.pop(random_index)
            sampled_multipliers.append(sampled_multiplier)

        return sampled_multipliers

    # Method generates Random sampled multipliers for specified bounds (dictionary)
    def generateRandomSampledMultipliers(self, specification_map, number_samples) :

        # Generate samples of random multipliers
        sampled_multipliers = []
        for i in range(number_samples) :
            sampled_multiplier = {}
            for key, specification in specification_map.items() :
                lower_bound = 1 - specification['bound']
                upper_bound = 1 + specification['bound']
                sampled_multiplier[key] = np.random.uniform(lower_bound, upper_bound)
            sampled_multipliers.append(sampled_multiplier)

        return sampled_multipliers

    # Method generates Full Factorial multipliers (from lower, mid, upper) for specified bounds (dictionary)
    def generateFullFactorialMultipliers(self, specification_map) :

        # Construct sets of lower, mid, and upper multipliers 
        lower_mid_upper_sets = []
        key_set = [] # maintains key order
        for key, specification in specification_map.items() :
            lower_bound = 1 - specification['bound']
            upper_bound = 1 + specification['bound']
            lower_mid_upper_sets.append([lower_bound, 1, upper_bound])
            key_set.append(key)

        # Generate the cartesian product of the multiplier sets
        cartesian_product = list(itertools.product(*lower_mid_upper_sets))

        # Map the multiplier sets back to their parameter keys
        factorial_multipliers = []
        for multiplier_set in cartesian_product :
            key_mapped_multiplier = {}
            for index, key in enumerate(key_set) :
                key_mapped_multiplier[key] = multiplier_set[index]
            factorial_multipliers.append(key_mapped_multiplier)

        return factorial_multipliers

    # Method calculates the lower threshold value given a tail probability for a specified distribution
    def lowerThreshold(self, distribution, specification, tail_probability) :
        if distribution == 'normal' :
            mean = specification['mean']
            std_dev = specification['std_dev']
            return norm.ppf(tail_probability, loc=mean, scale=std_dev)
        elif distribution == 'lognormal' :
            lower = specification['lower']
            scale = specification['scale']
            sigma = specification['sigma']
            return lognorm.ppf(tail_probability, sigma, loc=lower, scale=scale)

    # Method calculates the upper threshold value given a tail probability for a specified distribution
    def upperThreshold(self, distribution, specification, tail_probability) :
        return self.lowerThreshold(distribution, specification, 1-tail_probability)

    # Method utilises a multiplier to modify parameter values
    def multipy(self, parameter_values, multipliers, parameter_data_types={}) :

        modified_parameter_values = {}

        # Multiply each keyed parameter value by the corresponding multiplier where supplied
        for key, multiplier in multipliers.items() :
            if type(parameter_values[key]) is dict : # nested
                modified_parameter_values[key] = {}
                for nested_key, nested_value in parameter_values[key].items() :
                    modified_parameter_values[key][nested_key] = nested_value*multiplier
                    if parameter_data_types.has_key(key) :
                        if parameter_data_types[key] == 'integer' :
                            modified_parameter_values[key][nested_key] = modified_parameter_values[key][nested_key].round().astype(int)
            else : 
                modified_parameter_values[key] = parameter_values[key]*multiplier
                if parameter_data_types.has_key(key) :
                    if parameter_data_types[key] == 'integer' :
                        modified_parameter_values[key] = modified_parameter_values[key].round().astype(int)

        return modified_parameter_values

    # Method generates plot values for the selected distribution specified for each parameter (via dictionary)
    def generateDistributionPlotValues(self, specification) :
            
        sample_number = 1000
        x_values = []
        y_values = []

        # Generate plot values from selected distribution via PDF
        distribution = specification['distribution']
        if distribution == 'uniform' :
            lower = specification['settings']['lower']
            upper = specification['settings']['upper']
            base = upper - lower
            incr = base/sample_number
            for i in range(sample_number) :
                x_values.append(lower+i*incr)
            y_values = uniform.pdf(x_values, loc=lower, scale=base).tolist()
        elif distribution == 'normal' :
            mean = specification['settings']['mean']
            std_dev = specification['settings']['std_dev']
            x_min = mean - 3*std_dev
            x_max = mean + 3*std_dev
            incr = (x_max - x_min)/sample_number
            for i in range(sample_number) :
                x_values.append(x_min+i*incr)
            y_values = norm.pdf(x_values, loc=mean, scale=std_dev).tolist()
        elif distribution == 'triangular' :
            a = specification['settings']['a']
            base = specification['settings']['b'] - a
            c_std = (specification['settings']['c'] - a)/base
            incr = base/sample_number
            for i in range(sample_number) :
                x_values.append(a+i*incr)
            y_values = triang.pdf(x_values, c_std, loc=a, scale=base).tolist()
        elif distribution == 'lognormal' :
            lower = specification['settings']['lower']
            scale = specification['settings']['scale']
            sigma = specification['settings']['sigma']
            x_max = lognorm.isf(0.01, sigma, loc=lower, scale=scale)
            incr = (x_max - lower)/sample_number
            for i in range(sample_number) :
                x_values.append(lower+i*incr)
            y_values = lognorm.pdf(x_values, sigma, loc=lower, scale=scale).tolist()
        elif distribution == 'beta' :
            lower = specification['settings']['lower']
            base = specification['settings']['upper'] - lower
            incr = base/sample_number
            for i in range(sample_number) :
                x_values.append(lower+i*incr)
            a = specification['settings']['alpha']
            b = specification['settings']['beta']
            y_values = beta.pdf(x_values, a, b, loc=lower, scale=base).tolist()

        # Remove any nan/inf values
        remove_indexes = []
        for i in range(sample_number) :
            if not np.isfinite(y_values[i]) :
                remove_indexes.append(i)
        for i in range(len(remove_indexes)) :
            x_values = np.delete(x_values, i)
            y_values = np.delete(y_values, i)

        return { 'x_values' : x_values, 'y_values' : y_values }

# END SampleGenerator        
