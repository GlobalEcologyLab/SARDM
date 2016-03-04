# Tool library module
from SampleGenerator import SampleGenerator

# Python extension module NumPy (requires extension installation)
import numpy as np

# Test sample number
sample_number = 10

sample_generator = SampleGenerator()

# Test 1: Latin Hypercube

print 'Test 1: Latin Hypercube multipliers\n'

# a) Uniform distribution

print 'a) Uniform distribution\n'
specification_map = { 'key1' : { 'distribution' : 'uniform', 'settings' : { 'lower' : 0.8, 'upper' : 1.2 } },
                      'key2' : { 'distribution' : 'uniform', 'settings' : { 'lower' : 0.7, 'upper' : 1.3 } },
                      'key3' : { 'distribution' : 'uniform', 'settings' : { 'lower' : 0.6, 'upper' : 1.2 } } }

# Print bounds
headers = ''
lower_values = ''
upper_values = ''
for key in sorted(specification_map.keys()) :
    headers += key + '\t'
    lower_values += ('%.2f\t') % specification_map[key]['settings']['lower']
    upper_values += ('%.2f\t') % specification_map[key]['settings']['upper']
print 'Specifications:\n', headers, '\n', lower_values, '(lower values)\n', upper_values, '(upper values)\n'

values = ''
sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(specification_map, sample_number)
for multiplier_set in sampled_multipliers :
    for key in sorted(multiplier_set.keys()) :
        values += '%.2f\t' % multiplier_set[key]
    values += '\n'
print 'Multipliers:\n', headers, '\n', values

# b) Normal distribution

print 'b) Normal distribution\n'
specification_map = { 'key1' : { 'distribution' : 'normal', 'settings' : { 'mean' : 1.0, 'std_dev' : 0.1 } },
                      'key2' : { 'distribution' : 'normal', 'settings' : { 'mean' : 1.1, 'std_dev' : 0.2 } },
                      'key3' : { 'distribution' : 'normal', 'settings' : { 'mean' : 0.9, 'std_dev' : 0.3 } } }

# Print specifications
headers = ''
mean_values = ''
stdev_values = ''
for key in sorted(specification_map.keys()) :
    headers += key + '\t'
    mean_values += ('%.2f\t') % specification_map[key]['settings']['mean']
    stdev_values += ('%.2f\t') % specification_map[key]['settings']['std_dev']
print 'Specifications:\n', headers, '\n', mean_values, '(means)\n', stdev_values, '(std devs)\n'

values = ''
sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(specification_map, sample_number)
for multiplier_set in sampled_multipliers :
    for key in sorted(multiplier_set.keys()) :
        values += '%.2f\t' % multiplier_set[key]
    values += '\n'
print 'Multipliers:\n', headers, '\n', values, '\n'

# c) Triangular distribution

print 'c) Triangular distribution\n'
specification_map = { 'key1' : { 'distribution' : 'triangular', 'settings' : { 'a' : 0.8, 'b' : 1.2, 'c' : 1.0 } },
                      'key2' : { 'distribution' : 'triangular', 'settings' : { 'a' : 0.8, 'b' : 1.2, 'c' : 0.8 } },
                      'key3' : { 'distribution' : 'triangular', 'settings' : { 'a' : 0.8, 'b' : 1.2, 'c' : 1.2 } } }

# Print specifications
headers = ''
a_values = ''
b_values = ''
c_values = ''
for key in sorted(specification_map.keys()) :
    headers += key + '\t'
    a_values += ('%.2f\t') % specification_map[key]['settings']['a']
    b_values += ('%.2f\t') % specification_map[key]['settings']['b']
    c_values += ('%.2f\t') % specification_map[key]['settings']['c']
print 'Specifications:\n', headers, '\n', a_values, '(a values)\n', b_values, '(b values)\n', c_values, '(c values)\n'

values = ''
sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(specification_map, sample_number)
for multiplier_set in sampled_multipliers :
    for key in sorted(multiplier_set.keys()) :
        values += '%.2f\t' % multiplier_set[key]
    values += '\n'
print 'Multipliers:\n', headers, '\n', values, '\n'

# d) Lognormal distribution

print 'd) Lognormal distribution\n'
specification_map = { 'key1' : { 'distribution' : 'lognormal', 'settings' : { 'lower' : 1.0, 'scale' : 0.01, 'sigma' : 1.0 } },
                      'key2' : { 'distribution' : 'lognormal', 'settings' : { 'lower' : 1.0, 'scale' : 0.01, 'sigma' : 0.5 } },
                      'key3' : { 'distribution' : 'lognormal', 'settings' : { 'lower' : 1.0, 'scale' : 0.1, 'sigma' : 0.25 } } }

# Print specifications
headers = ''
lower_values = ''
scale_values = ''
sigma_values = ''
for key in sorted(specification_map.keys()) :
    headers += key + '\t'
    lower_values += ('%.2f\t') % specification_map[key]['settings']['lower']
    scale_values += ('%.2f\t') % specification_map[key]['settings']['scale']
    sigma_values += ('%.2f\t') % specification_map[key]['settings']['sigma']
print 'Specifications:\n', headers, '\n', lower_values, '(lower values)\n', scale_values, '(scale values)\n', sigma_values, '(sigma values)\n'

values = ''
sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(specification_map, sample_number)
for multiplier_set in sampled_multipliers :
    for key in sorted(multiplier_set.keys()) :
        values += '%.2f\t' % multiplier_set[key]
    values += '\n'
print 'Multipliers:\n', headers, '\n', values, '\n'

# e) Beta distribution

print 'e) Beta distribution\n'
specification_map = { 'key1' : { 'distribution' : 'beta', 'settings' : { 'lower' : 0.8, 'upper' : 1.2, 'alpha' : 2.0, 'beta' : 2.0 } },
                      'key2' : { 'distribution' : 'beta', 'settings' : { 'lower' : 0.8, 'upper' : 1.2, 'alpha' : 2.0, 'beta' : 0.5 } },
                      'key3' : { 'distribution' : 'beta', 'settings' : { 'lower' : 0.8, 'upper' : 1.2, 'alpha' : 0.5, 'beta' : 2.0 } } }

# Print specifications
headers = ''
lower_values = ''
upper_values = ''
alpha_values = ''
beta_values = ''
for key in sorted(specification_map.keys()) :
    headers += key + '\t'
    lower_values += ('%.2f\t') % specification_map[key]['settings']['lower']
    upper_values += ('%.2f\t') % specification_map[key]['settings']['upper']
    alpha_values += ('%.2f\t') % specification_map[key]['settings']['alpha']
    beta_values += ('%.2f\t') % specification_map[key]['settings']['beta']
print 'Specifications:\n', headers, '\n', lower_values, '(lower values)\n', upper_values, '(upper values)\n', alpha_values, '(alpha values)\n', beta_values, '(beta values)\n'

values = ''
sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(specification_map, sample_number)
for multiplier_set in sampled_multipliers :
    for key in sorted(multiplier_set.keys()) :
        values += '%.2f\t' % multiplier_set[key]
    values += '\n'
print 'Multipliers:\n', headers, '\n', values, '\n'

# Test 2: Random

print 'Test 2: Random multipliers\n'
sample_bounds = { 'key1' : { 'bound' : 0.1 }, 'key2' : { 'bound' : 0.2 }, 'key3' : { 'bound' : 0.3 } }

# Print bounds
headers = ''
values = ''
for key in sorted(sample_bounds.keys()) :
    headers += key + '\t'
    values += (u'\u00B1' + '%.2f\t') % sample_bounds[key]['bound']
print 'Bounds:\n', headers, '\n', values, '\n'

values = ''
sampled_multipliers = sample_generator.generateRandomSampledMultipliers(sample_bounds, sample_number)
for multiplier_set in sampled_multipliers :
    for key in sorted(multiplier_set.keys()) :
        values += '%.2f\t' % multiplier_set[key]
    values += '\n'
print 'Multipliers:\n', headers, '\n', values, '\n'


# Test 3: Full Factorial

print 'Test 3: Full Factorial multipliers\n'
sample_bounds = { 'key1' : { 'bound' : 0.1 }, 'key2' : { 'bound' : 0.2 }, 'key3' : { 'bound' : 0.3 } }

# Print bounds
headers = ''
values = ''
for key in sorted(sample_bounds.keys()) :
    headers += key + '\t'
    values += (u'\u00B1' + '%.2f\t') % sample_bounds[key]['bound']
print 'Bounds:\n', headers, '\n', values, '\n'

values = ''
sampled_multipliers = sample_generator.generateFullFactorialMultipliers(sample_bounds)
for multiplier_set in sampled_multipliers :
    for key in sorted(multiplier_set.keys()) :
        values += '%.2f\t' % multiplier_set[key]
    values += '\n'
print 'Multipliers:\n', headers, '\n', values, '\n'

# Test 4: Test lower and upper threshold functions for unbounded distributions
print 'Test 4: Test lower and upper threshold functions for unbounded distributions\n'
print 'Normal distribution: mean = 1.0, stdev = 0.1'
print 'Lower threshold p = 0.01 : ', sample_generator.lowerThreshold('normal', { 'mean' : 1.0, 'std_dev' : 0.1 }, 0.01)
print 'Upper threshold p = 0.01 : ', sample_generator.upperThreshold('normal', { 'mean' : 1.0, 'std_dev' : 0.1 }, 0.01)
print '\nLognormal distribution: lower = 1.0, scale = 0.01, sigma = 1.0'
print 'Upper threshold p = 0.01 : ', sample_generator.upperThreshold('lognormal', { 'lower' : 1.0, 'scale' : 0.01, 'sigma' : 1.0 }, 0.01)

# Test 5: Utilises a multiplier to modify parameter values
parameter_values = { 'key1' : np.array(10.0), 'key2' : np.array(20.0), 'key3' : np.array(29) }
parameter_data_types = { 'key3' : 'integer' }
parameter_output_formats = { 'key1' : '%.1f', 'key2' : '%.1f', 'key3' : '%d' }
multipliers = { 'key1' : 1.1, 'key2' : 0.9, 'key3' : 1.2 }
modified_parameter_values = sample_generator.multipy(parameter_values, multipliers, parameter_data_types)
param_values = ''
mult_values = ''
modified_values = ''
for key in sorted(parameter_values.keys()) :
        param_values += (parameter_output_formats[key]+'\t') % parameter_values[key]
        mult_values += '%.1f\t' % multipliers[key]
        modified_values += (parameter_output_formats[key]+'\t') % modified_parameter_values[key]
print 'Test 5: Applying Multipliers to Parameters\n'
print 'Initial parameter values:\n', headers, '\n', param_values, '\n'
print 'Multipliers:\n', mult_values, '\n'
print 'Modified parameter values:\n', modified_values, '\n'

# Test 6: Graphical plotting tests for Latin Hypercube Sampling distributions

print 'Test 6: Graphical plotting tests for Latin Hypercube Sampling distributions\n'

# matplotlib must be installed to run these tests
try :
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt

    plt.figure()
    
    sample_number = 1000
    
    # a) Uniform distributions
    specification_map = { 'key1' : { 'distribution' : 'uniform', 'settings' : { 'lower' : 0.8, 'upper' : 1.2 } },
                          'key2' : { 'distribution' : 'uniform', 'settings' : { 'lower' : 0.7, 'upper' : 1.3 } },
                          'key3' : { 'distribution' : 'uniform', 'settings' : { 'lower' : 0.6, 'upper' : 1.2 } } }
    sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(specification_map, sample_number)
    d1 = []
    d2 = []
    d3 = []
    for mults in sampled_multipliers :
        d1.append(mults['key1'])
        d2.append(mults['key2'])
        d3.append(mults['key3'])
    plt.subplot(5,3,1)
    plt.title('a) Uniform distributions')
    plt.hist(d1)
    plt.subplot(5,3,2)
    plt.hist(d2)
    plt.subplot(5,3,3)
    plt.hist(d3)

    # b) Normal distributions
    specification_map = { 'key1' : { 'distribution' : 'normal', 'settings' : { 'mean' : 1.0, 'std_dev' : 0.1 } },
                          'key2' : { 'distribution' : 'normal', 'settings' : { 'mean' : 1.1, 'std_dev' : 0.2 } },
                          'key3' : { 'distribution' : 'normal', 'settings' : { 'mean' : 0.9, 'std_dev' : 0.3 } } }
    sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(specification_map, sample_number)
    d1 = []
    d2 = []
    d3 = []
    for mults in sampled_multipliers :
        d1.append(mults['key1'])
        d2.append(mults['key2'])
        d3.append(mults['key3'])
    plt.subplot(5,3,4)
    plt.title('b) Normal distributions')
    plt.hist(d1)
    plt.subplot(5,3,5)
    plt.hist(d2)
    plt.subplot(5,3,6)
    plt.hist(d3)
    
    # c) Triangular distributions
    specification_map = { 'key1' : { 'distribution' : 'triangular', 'settings' : { 'a' : 0.8, 'b' : 1.2, 'c' : 1.0 } },
                          'key2' : { 'distribution' : 'triangular', 'settings' : { 'a' : 0.8, 'b' : 1.2, 'c' : 0.8 } },
                          'key3' : { 'distribution' : 'triangular', 'settings' : { 'a' : 0.8, 'b' : 1.2, 'c' : 1.2 } } }
    sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(specification_map, sample_number)
    d1 = []
    d2 = []
    d3 = []
    for mults in sampled_multipliers :
        d1.append(mults['key1'])
        d2.append(mults['key2'])
        d3.append(mults['key3'])
    plt.subplot(5,3,7)
    plt.title('c) Triangular distributions')
    plt.hist(d1)
    plt.subplot(5,3,8)
    plt.hist(d2)
    plt.subplot(5,3,9)
    plt.hist(d3)

    # d) Lognormal distributions
    specification_map = { 'key1' : { 'distribution' : 'lognormal', 'settings' : { 'lower' : 1.0, 'scale' : 0.01, 'sigma' : 1.0 } },
                          'key2' : { 'distribution' : 'lognormal', 'settings' : { 'lower' : 1.0, 'scale' : 0.01, 'sigma' : 0.5 } },
                          'key3' : { 'distribution' : 'lognormal', 'settings' : { 'lower' : 1.0, 'scale' : 0.1, 'sigma' : 0.25 } } }
    sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(specification_map, sample_number)
    d1 = []
    d2 = []
    d3 = []
    for mults in sampled_multipliers :
        d1.append(mults['key1'])
        d2.append(mults['key2'])
        d3.append(mults['key3'])
    plt.subplot(5,3,10)
    plt.title('d) Lognormal distributions')
    plt.hist(d1)
    plt.subplot(5,3,11)
    plt.hist(d2)
    plt.subplot(5,3,12)
    plt.hist(d3)

    # e) Beta distributions
    specification_map = { 'key1' : { 'distribution' : 'beta', 'settings' : { 'lower' : 0.8, 'upper' : 1.2, 'alpha' : 2.0, 'beta' : 2.0 } },
                          'key2' : { 'distribution' : 'beta', 'settings' : { 'lower' : 0.8, 'upper' : 1.2, 'alpha' : 2.0, 'beta' : 0.5 } },
                          'key3' : { 'distribution' : 'beta', 'settings' : { 'lower' : 0.8, 'upper' : 1.2, 'alpha' : 0.5, 'beta' : 2.0 } } }
    sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(specification_map, sample_number)
    d1 = []
    d2 = []
    d3 = []
    for mults in sampled_multipliers :
        d1.append(mults['key1'])
        d2.append(mults['key2'])
        d3.append(mults['key3'])
    plt.subplot(5,3,13)
    plt.title('e) Beta distributions')
    plt.hist(d1)
    plt.subplot(5,3,14)
    plt.hist(d2)
    plt.subplot(5,3,15)
    plt.hist(d3)

    plt.subplots_adjust(left=0.15)
    plt.show()

    # f) Mixed distributions
    plt.figure()
    bins = 20
    specification_map = { 'key1' : { 'distribution' : 'uniform', 'settings' : { 'lower' : 0.8, 'upper' : 1.2 } },
                          'key2' : { 'distribution' : 'normal', 'settings' : { 'mean' : 1.0, 'std_dev' : 0.05 } },
                          'key3' : { 'distribution' : 'triangular', 'settings' : { 'a' : 0.8, 'b' : 1.2, 'c' : 1.0 } },
                          'key4' : { 'distribution' : 'lognormal', 'settings' : { 'lower' : 1.0, 'scale' : 0.1, 'sigma' : 0.5 } },
                          'key5' : { 'distribution' : 'beta', 'settings' : { 'lower' : 0.8, 'upper' : 1.2, 'alpha' : 2.0, 'beta' : 2.0 } } }
    sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(specification_map, sample_number)
    d1 = []
    d2 = []
    d3 = []
    d4 = []
    d5 = []
    for mults in sampled_multipliers :
        d1.append(mults['key1'])
        d2.append(mults['key2'])
        d3.append(mults['key3'])
        d4.append(mults['key4'])
        d5.append(mults['key5'])
    plt.subplot(5,1,1)
    plt.title('f) Mixed distributions')
    plt.hist(d1,bins)
    plt.subplot(5,1,2)
    plt.hist(d2,bins)
    plt.subplot(5,1,3)
    plt.hist(d3,bins)
    plt.subplot(5,1,4)
    plt.hist(d4,bins)
    plt.subplot(5,1,5)
    plt.hist(d5,bins)

    plt.subplots_adjust(left=0.15)
    plt.show()

except Exception, e :
    print 'matplotlib must be installed to run these tests'

# Test 7: Graphical plotting verification tests for Latin Hypercube Sampling Stratified Generation

print 'Test 7: Graphical plotting verification tests for Latin Hypercube Sampling Stratified Generation\n'

# matplotlib must be installed to run these tests
try :
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
    import numpy as np
    import scipy.stats as ss

    plt.figure()

    number_samples = 5
    repeat_generations = 1000

    uniform_multipliers = []
    normal_multipliers = []
    triangular_multipliers = []
    lognormal_multipliers = []
    beta_multipliers = []
    for i in range(number_samples) :
        uniform_multipliers.append([])
        normal_multipliers.append([])
        triangular_multipliers.append([])
        lognormal_multipliers.append([])
        beta_multipliers.append([])
    for j in range(repeat_generations) :

        # Generate stratified random probability values for distribution generation via inverse CDF
        stratified_random_probabilities = ((np.array(range(number_samples)) + np.random.random(number_samples))/number_samples)

        # Uniform multipliers
        lower = 0.8
        base = 1.2 - lower
        uniform_multiplier = ss.uniform.ppf(stratified_random_probabilities, loc=lower, scale=base).tolist()

        # Normal multipliers
        mean = 1.1
        std_dev = 0.1
        normal_multiplier = ss.norm.ppf(stratified_random_probabilities, loc=(mean), scale=std_dev).tolist()

        # Triangular multipliers
        a = 0.6
        base = 1.4 - a
        c_std = (1.2 - a)/base
        triangular_multiplier = ss.triang.ppf(stratified_random_probabilities, c_std, loc=(a), scale=base).tolist()

        # Lognormal multipliers
        lower = 1.0
        scale = 0.1
        sigma = 1.0
        lognormal_multiplier = ss.lognorm.ppf(stratified_random_probabilities, sigma, loc=lower, scale=scale).tolist()

        # Beta multipliers
        lower = 0.8
        base = 1.2 - lower
        a = 2.0
        b = 2.0
        beta_multiplier = ss.beta.ppf(stratified_random_probabilities, a, b, loc=lower, scale=base).tolist()

        for i in range(number_samples) :
            uniform_multipliers[i].append(uniform_multiplier[i])
            normal_multipliers[i].append(normal_multiplier[i])
            triangular_multipliers[i].append(triangular_multiplier[i])
            lognormal_multipliers[i].append(lognormal_multiplier[i])
            beta_multipliers[i].append(beta_multiplier[i])

    bins = 20

    for i in range(number_samples) :
        plt.subplot(5,5,i+1)
        plt.hist(uniform_multipliers[i],bins)
        if i == 0 :
            plt.title('a) Stratified uniform distribution')

    for i in range(number_samples) :
        plt.subplot(5,5,i+number_samples+1)
        plt.hist(normal_multipliers[i],bins)
        if i == 0 :
            plt.title('b) Stratified normal distribution')

    for i in range(number_samples) :
        plt.subplot(5,5,i+2*number_samples+1)
        plt.hist(triangular_multipliers[i],bins)
        if i == 0 :
            plt.title('c) Stratified triangular distribution')

    for i in range(number_samples) :
        plt.subplot(5,5,i+3*number_samples+1)
        plt.hist(lognormal_multipliers[i],bins)
        if i == 0 :
            plt.title('d) Stratified lognormal distribution')

    for i in range(number_samples) :
        plt.subplot(5,5,i+4*number_samples+1)
        plt.hist(beta_multipliers[i],bins)
        if i == 0 :
            plt.title('c) Stratified beta distribution')

    plt.subplots_adjust(left=0.15)
    plt.show()

except Exception, e :
    print 'matplotlib must be installed to run these tests', e

# Test 8: Graphical plotting verification tests for distribution plot values generation

print 'Test 8: Graphical plotting verification tests for distribution plot values generation\n'

# matplotlib must be installed to run these tests
try :
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt

    plt.figure()

    # a) Uniform distributions
    specification_map = { 'key1' : { 'distribution' : 'uniform', 'settings' : { 'lower' : 0.8, 'upper' : 1.2 } },
                          'key2' : { 'distribution' : 'uniform', 'settings' : { 'lower' : 0.7, 'upper' : 1.3 } },
                          'key3' : { 'distribution' : 'uniform', 'settings' : { 'lower' : 0.6, 'upper' : 1.2 } } }
    plt.subplot(5,3,1)
    plt.title('a) Uniform distributions')
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key1'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')
    plt.subplot(5,3,2)
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key2'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')
    plt.subplot(5,3,3)
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key3'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')

    # b) Normal distributions
    specification_map = { 'key1' : { 'distribution' : 'normal', 'settings' : { 'mean' : 1.0, 'std_dev' : 0.1 } },
                          'key2' : { 'distribution' : 'normal', 'settings' : { 'mean' : 1.1, 'std_dev' : 0.2 } },
                          'key3' : { 'distribution' : 'normal', 'settings' : { 'mean' : 0.9, 'std_dev' : 0.3 } } }
    plt.subplot(5,3,4)
    plt.title('b) Normal distributions')
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key1'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')
    plt.subplot(5,3,5)
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key2'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')
    plt.subplot(5,3,6)
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key3'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')
    
    # c) Triangular distributions
    specification_map = { 'key1' : { 'distribution' : 'triangular', 'settings' : { 'a' : 0.8, 'b' : 1.2, 'c' : 1.0 } },
                          'key2' : { 'distribution' : 'triangular', 'settings' : { 'a' : 0.8, 'b' : 1.2, 'c' : 0.8 } },
                          'key3' : { 'distribution' : 'triangular', 'settings' : { 'a' : 0.8, 'b' : 1.2, 'c' : 1.2 } } }
    plt.subplot(5,3,7)
    plt.title('c) Triangular distributions')
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key1'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')
    plt.subplot(5,3,8)
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key2'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')
    plt.subplot(5,3,9)
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key3'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')

    # d) Lognormal distributions
    specification_map = { 'key1' : { 'distribution' : 'lognormal', 'settings' : { 'lower' : 1.0, 'scale' : 0.01, 'sigma' : 1.0 } },
                          'key2' : { 'distribution' : 'lognormal', 'settings' : { 'lower' : 1.0, 'scale' : 0.01, 'sigma' : 0.5 } },
                          'key3' : { 'distribution' : 'lognormal', 'settings' : { 'lower' : 1.0, 'scale' : 0.1, 'sigma' : 0.25 } } }
    plt.subplot(5,3,10)
    plt.title('d) Lognormal distributions')
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key1'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')
    plt.subplot(5,3,11)
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key2'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')
    plt.subplot(5,3,12)
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key3'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')

    # e) Beta distributions
    specification_map = { 'key1' : { 'distribution' : 'beta', 'settings' : { 'lower' : 0.8, 'upper' : 1.2, 'alpha' : 2.0, 'beta' : 2.0 } },
                          'key2' : { 'distribution' : 'beta', 'settings' : { 'lower' : 0.8, 'upper' : 1.2, 'alpha' : 2.0, 'beta' : 0.5 } },
                          'key3' : { 'distribution' : 'beta', 'settings' : { 'lower' : 0.8, 'upper' : 1.2, 'alpha' : 0.5, 'beta' : 2.0 } } }
    plt.subplot(5,3,13)
    plt.title('e) Beta distributions')
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key1'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')
    plt.subplot(5,3,14)
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key2'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')
    plt.subplot(5,3,15)
    plot_values = sample_generator.generateDistributionPlotValues(specification_map['key3'])
    plt.plot(plot_values['x_values'], plot_values['y_values'], 'k')

    plt.subplots_adjust(left=0.15)
    plt.show()

except Exception, e :
    print 'matplotlib must be installed to run these tests', e
