# Python modules
from os import getcwd, listdir

## Test Configuration
class TestMetapopConfiguration :

    # Initialise with the test config
    def __init__(self, config_file) :

        # Configuration file (in same directory as the tool)
        self.tool_config_file = config_file

        # Configuration relating to tool options:

        self.tool_option_parameters = ['metapop_exe_location',
                                       'default_generated_file_location',
                                       'number_of_metapop_iterations',
                                       'metapop_simulation_duration',
                                       'use_mp_baseline_values',
                                       'default_number_of_lhs_samples',
                                       'default_number_of_random_samples',
                                       'default_sample_bounds_for_random',
                                       'default_sample_bounds_for_full_factorial',
                                       'auto_run_results_summary_tool']

        self.tool_option_parameter_types = {'metapop_exe_location' : str,
                                            'default_generated_file_location' : str,
                                            'number_of_metapop_iterations' : int,
                                            'metapop_simulation_duration' : int,
                                            'use_mp_baseline_values' : bool,
                                            'default_number_of_lhs_samples' : int,
                                            'default_number_of_random_samples' : int,
                                            'default_sample_bounds_for_random' : float,
                                            'default_sample_bounds_for_full_factorial' : float,
                                            'auto_run_results_summary_tool' : bool}

        # The local disk location of the RAMAS Metapop program
        self.metapop_exe_location = r'C:\Program Files\RAMASGIS\Metapop.exe'

        # The default local disk location for generated files
        self.default_generated_file_location = r'C:\afat32\Dropbox\GlobalEcologyGroup\ProjectCode\SensitivityAnalysisToolset\v0.4\Test'

        # The number of RAMAS Metapop iterations/replications per scenario and simulation duration
        self.number_of_metapop_iterations = 100
        self.metapop_simulation_duration = 20
        self.use_mp_baseline_values = False

        # The default number of samples for LHS/Random
        self.default_number_of_lhs_samples = None #3
        self.default_number_of_random_samples = 5

        # The default sample bounds for Random/Full Factorial
        self.default_sample_bounds_for_random = 10.
        self.default_sample_bounds_for_full_factorial = 20.
        
        # Results summary tool is auto run when sample file generated
        self.auto_run_results_summary_tool = False

        # End config for tool options

        # Load config from file and warn if file not found
        self.config_warning = self.loadConfig()

    # Load configuration from a file and return warning if any
    def loadConfig(self) :
        warning = ''
        if listdir(getcwd()).count(self.tool_config_file) :
            f = open(getcwd() + '\\' + self.tool_config_file)
            lines = f.readlines()
            f.close()
            for line in lines :
                if line.find('=') != -1 :
                    name = 'self.' + line.split('=')[0].strip()
                    value = line.split('=')[1].strip()
                    try :
                        exec(name + ' = eval(value)')
                    except Exception, e :
                        exec(name + ' = value')
        else :
            warning = 'Could not find configuration file. Using default configuration.'
        return warning

    # Get tool options
    def getToolOptions(self, option_parameters=None) :
        if not option_parameters :
            option_parameters = self.tool_option_parameters
        tool_options = {}
        for option in option_parameters :
            tool_options[option] = eval('self.'+option)
        return tool_options

    # Set tool options, including updating config file
    def setToolOptions(self, tool_options) :

        # Read config file
        if listdir(getcwd()).count(self.tool_config_file) :

            # Read file lines
            f = open(getcwd() + '\\' + self.tool_config_file)
            file_lines = f.readlines()
            f.close()

            # Ensure last line has newline char
            if len(file_lines) > 0 :
                if file_lines[len(file_lines)-1].find('\n') == -1 :
                    file_lines[len(file_lines)-1] += '\n'

        else :
            file_lines = []

        # Set options within tool and config file lines
        for option, value in tool_options.items() :

            # Set within tool
            name = 'self.' + option
            exec(name + ' = value')

            # Set within config file lines
            found_within_file = False
            for i, line in enumerate(file_lines) :
                if line.find(option) != -1 :
                    if line.find('=') != -1 :
                        file_lines[i] = line.split('=')[0] + '= ' + str(value) + '\n'
                        found_within_file = True
            if not found_within_file :
                file_lines.append(option + ' = ' + str(value) + '\n')

        # Write config file
        f = open(getcwd() + '\\' + self.tool_config_file, 'w')
        f.writelines(file_lines)
        f.close()

# END TestMetapopConfiguration

## Main program

# Create and configure the file helpers
config = TestMetapopConfiguration('test_config.txt')

# TEST 1: Get tool options
print config.getToolOptions()
print config.getToolOptions(['number_of_metapop_iterations',
                             'default_sample_bounds_for_random'])

# TEST 2: Set tool options
config.setToolOptions({ 'number_of_metapop_iterations' : 200,
                        'default_sample_bounds_for_random' : 15.,
                        'default_sample_bounds_for_full_factorial' : None,
                        'auto_run_results_summary_tool' : True,
                        'default_generated_file_location' : r'C:\afat32\Dropbox\GlobalEcologyGroup\ProjectCode\SensitivityAnalysisToolset\v0.5\Test'})
print config.getToolOptions()

# TEST 3: Reload modified config
config.loadConfig()
print config.getToolOptions()

# END Main program


