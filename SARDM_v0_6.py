# Python modules
import string
import sys
import time
import Tkinter as tk
from os import chdir, environ, getcwd, listdir, mkdir, path
from subprocess import call
from shutil import copyfile
from tkFileDialog import *
from tkFont import Font
from tkMessageBox import *
import warnings
warnings.simplefilter('ignore')

# Python extension module NumPy (requires extension installation)
import numpy as np

# Python extension module Matplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import rcParams

# Tool library modules
from MpFileExtractorAndGeneratorHelper import MpFileExtractorAndGeneratorHelper
from MpParameterBoundConstraintHelper import MpParameterBoundConstraintHelper
from SampleGenerator import SampleGenerator

# TEST FLAG:
# * Saves the generated template
# * Puts a pause in the generated batch file
DEBUG = False

## Configuration (future versions could load from a file)
## * Configures what Latin Hypercube Sampling distributions are available for each parameter
## * Maps the file row and column locations of the parameters
## * Configures the desired output formats for the parameters
## * Configures constraints for the parameters
## * Configures parameter data types
## * Configures the location of the RAMAS Metapop executable
## * Configures the names of the RAMAS Metapop output files
class MetapopConfiguration :

    # Initialise with the default config
    def __init__(self, user_app_data_dir, config_file) :

        # Configuration file (initially in the same directory as the tool, but copied to user application data directory)
        self.tool_config_file = config_file

        # User application data directory
        self.user_application_data_directory = user_app_data_dir

        # Configure parameter list in desired order
        self.parameters = ['Initial Abundance', 'Rmax', 'Carrying Capacity', 'Allee Effect', 'Probability of a Catastrophe 1', 'Local Multiplier 1', 'Stage Multiplier 1',
                           'Probability of a Catastrophe 2', 'Local Multiplier 2', 'Stage Multiplier 2', 'Dispersal Matrix', 'Correlation Matrix', 'Fecundity Rates',
                           'Survival Rates', 'Environmental Variation']

        # Configure what Latin Hypercube Sampling distributions are available for each parameter
        self.lhs_distributions = ['Uniform', 'Gaussian', 'Triangular', 'Lognormal', 'Beta']
        self.lhs_distribution_settings = {}
        self.lhs_distribution_settings['Uniform'] = [{ 'name' : 'Lower', 'postfix' : '%'}, { 'name' : 'Upper', 'postfix' : '%'}]
        self.lhs_distribution_settings['Gaussian'] = [{ 'name' : 'Mean', 'postfix' : '%'}, { 'name' : 'Std. Dev.', 'postfix' : '%'}]
        self.lhs_distribution_settings['Triangular'] = [{ 'name' : 'Lower (a)', 'postfix' : '%'}, { 'name' : 'Upper (b)', 'postfix' : '%'}, { 'name' : 'Mode (c)', 'postfix' : '%'}]
        self.lhs_distribution_settings['Lognormal'] = [{ 'name' : 'Lower', 'postfix' : '%'}, { 'name' : 'Scale', 'postfix' : '%'}, { 'name' : 'Sigma', 'postfix' : ''}]
        self.lhs_distribution_settings['Beta'] = [{ 'name' : 'Lower', 'postfix' : '%'}, { 'name' : 'Upper', 'postfix' : '%'}, { 'name' : 'Alpha', 'postfix' : ''}, { 'name' : 'Beta', 'postfix' : ''}]
        self.parameter_includes_lhs_distributions = {}
        self.parameter_includes_lhs_distributions['Rmax'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Carrying Capacity'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Allee Effect'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Probability of a Catastrophe 1'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Local Multiplier 1'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Stage Multiplier 1'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Probability of a Catastrophe 2'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Local Multiplier 2'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Stage Multiplier 2'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Dispersal Matrix'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Correlation Matrix'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Fecundity Rates'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Survival Rates'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Environmental Variation'] = self.lhs_distributions
        self.parameter_includes_lhs_distributions['Initial Abundance'] = self.lhs_distributions      

        # Configure parameter mapping to MP file.
        # * Dynamic variables define mappings to variables within the MP file needed to define parameter mappings.
        # * Options define extracted values that alter the way parameters are processed.
        # * Alternatives define different extraction specifications dependent on options.
        # * Conditions for parameter inclusion defines a pattern match for a specified line or list of options.
        # * Also alternative conditions may be defined dependent on options.
        # * Additional parameters may relate to other model variables including links to temporal trends and other files.
        self.parameter_mapping = {}
        self.parameter_mapping['dynamic_variables'] = {}
        self.parameter_mapping['dynamic_variables']['lifestages'] = { 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 10, 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['dynamic_variables']['female_stages'] = { 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 39, 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['dynamic_variables']['populations'] = { 'pattern' : '^Migration', 'value' : 'line-45' }
        self.parameter_mapping['dynamic_variables']['migration_label_line'] = { 'pattern' : '^Migration', 'value' : 'line' }
        self.parameter_mapping['dynamic_variables']['correlation_label_line'] = { 'pattern' : '^Correlation', 'value' : 'line' }
        self.parameter_mapping['dynamic_variables']['stage_matrix_label_line'] = { 'pattern' : '^\d+ type\(s\) of stage matrix', 'value' : 'line' }
        self.parameter_mapping['dynamic_variables']['stage_matrix_types'] = { 'pattern' : '^\d+ type\(s\) of stage matrix', 'value' : 'int(match.split()[0])' }
        self.parameter_mapping['dynamic_variables']['std_dev_matrix_label_line'] = { 'pattern' : '^\d+ type\(s\) of st\.dev\. matrix', 'value' : 'line' }
        self.parameter_mapping['dynamic_variables']['std_dev_matrix_types'] = { 'pattern' : '^\d+ type\(s\) of st\.dev\. matrix', 'value' : 'int(match.split()[0])' }
        self.parameter_mapping['dynamic_variables']['constraints_matrix_label_line'] = { 'pattern' : '^Constraints Matrix', 'value' : 'line' }
        self.parameter_mapping['dynamic_variables']['simulation_results_line'] = { 'pattern' : '^Simulation results', 'value' : 'line' }
        self.parameter_mapping['dynamic_variables']['end_of_file_line'] = { 'pattern' : '^-End of file-', 'value' : 'line' }
        self.parameter_mapping['search_for_dynamic_variables_from_row'] = 7 # ignore comment rows
        self.parameter_mapping['omit_results_from_mp_template'] = { 'omit' : True, 'from_line' : 'simulation_results_line', 'to_line' : 'end_of_file_line-1' }
        self.parameter_mapping['options'] = {}
        self.parameter_mapping['options']['Dispersal Matrix'] = {}
        self.parameter_mapping['options']['Dispersal Matrix']['uses_function'] = { 'line' : 'migration_label_line+1', 'value' : 'line.split()[0]' }
        self.parameter_mapping['options']['Dispersal Matrix']['a'] = { 'line' : 'migration_label_line+2', 'value' : 'float(line.split(\',\')[0])' }
        self.parameter_mapping['options']['Dispersal Matrix']['b'] = { 'line' : 'migration_label_line+2', 'value' : 'float(line.split(\',\')[1])' }
        self.parameter_mapping['options']['Dispersal Matrix']['c'] = { 'line' : 'migration_label_line+2', 'value' : 'float(line.split(\',\')[2])' }
        self.parameter_mapping['options']['Dispersal Matrix']['Dmax'] = { 'line' : 'migration_label_line+2', 'value' : 'float(line.split(\',\')[3])' }
        self.parameter_mapping['options']['Correlation Matrix'] = {}
        self.parameter_mapping['options']['Correlation Matrix']['uses_function'] = { 'line' : 'correlation_label_line+1', 'value' : 'line.split()[0]' }
        self.parameter_mapping['options']['Correlation Matrix']['a'] = { 'line' : 'correlation_label_line+2', 'value' : 'float(line.split(\',\')[0])' }
        self.parameter_mapping['options']['Correlation Matrix']['b'] = { 'line' : 'correlation_label_line+2', 'value' : 'float(line.split(\',\')[1])' }
        self.parameter_mapping['options']['Correlation Matrix']['c'] = { 'line' : 'correlation_label_line+2', 'value' : 'float(line.split(\',\')[2])' }
        self.parameter_mapping['options']['Rmax'] = {}
        self.parameter_mapping['options']['Rmax']['density_dependence_type_population_specific'] = { 'line' : 33, 'value' : 'line.split()[0]' }
        self.parameter_mapping['options']['Rmax']['density_dependence_type_for_all'] = { 'from_line' : 34, 'lines' : 1, 'values' : 'line.split()[0]' }
        self.parameter_mapping['options']['Rmax']['density_dependence_type_per_population'] = { 'from_line' : 45, 'lines' : 'populations', 'values' : 'line.split(\',\')[4]' }
        self.parameter_mapping['options']['Carrying Capacity'] = {}
        self.parameter_mapping['options']['Carrying Capacity']['density_dependence_type_population_specific'] = { 'line' : 33, 'value' : 'line.split()[0]' }
        self.parameter_mapping['options']['Carrying Capacity']['density_dependence_type_for_all'] = { 'from_line' : 34, 'lines' : 1, 'values' : 'line.split()[0]' }
        self.parameter_mapping['options']['Carrying Capacity']['density_dependence_type_per_population'] = { 'from_line' : 45, 'lines' : 'populations', 'values' : 'line.split(\',\')[4]' }
        self.parameter_mapping['options']['Allee Effect'] = {}
        self.parameter_mapping['options']['Allee Effect']['density_dependence_type_population_specific'] = { 'line' : 33, 'value' : 'line.split()[0]' }
        self.parameter_mapping['options']['Allee Effect']['density_dependence_type_for_all'] = { 'from_line' : 34, 'lines' : 1, 'values' : 'line.split()[0]' }
        self.parameter_mapping['options']['Allee Effect']['density_dependence_type_per_population'] = { 'from_line' : 45, 'lines' : 'populations', 'values' : 'line.split(\',\')[4]' }
        self.parameter_mapping['options']['Probability of a Catastrophe 1'] = {}
        self.parameter_mapping['options']['Probability of a Catastrophe 1']['density_dependence_type_population_specific'] = { 'line' : 33, 'value' : 'line.split()[0]' }
        self.parameter_mapping['options']['Probability of a Catastrophe 1']['density_dependence_type_for_all'] = { 'from_line' : 34, 'lines' : 1, 'values' : 'line.split()[0]' }
        self.parameter_mapping['options']['Probability of a Catastrophe 1']['density_dependence_type_per_population'] = { 'from_line' : 45, 'lines' : 'populations', 'values' : 'line.split(\',\')[4]' }
        self.parameter_mapping['options']['Probability of a Catastrophe 1']['catastrophe_extent'] = { 'line' : 13, 'value' : 'line.strip()' }
        self.parameter_mapping['options']['Probability of a Catastrophe 1']['catastrophe_affects'] = { 'line' : 14, 'value_list' : 'line.strip().split(\',\')' }
        self.parameter_mapping['options']['Local Multiplier 1'] = {}
        self.parameter_mapping['options']['Local Multiplier 1']['density_dependence_type_population_specific'] = { 'line' : 33, 'value' : 'line.split()[0]' }
        self.parameter_mapping['options']['Local Multiplier 1']['density_dependence_type_for_all'] = { 'from_line' : 34, 'lines' : 1, 'values' : 'line.split()[0]' }
        self.parameter_mapping['options']['Local Multiplier 1']['density_dependence_type_per_population'] = { 'from_line' : 45, 'lines' : 'populations', 'values' : 'line.split(\',\')[4]' }
        self.parameter_mapping['options']['Local Multiplier 1']['catastrophe_extent'] = { 'line' : 13, 'value' : 'line.strip()' }
        self.parameter_mapping['options']['Local Multiplier 1']['catastrophe_affects'] = { 'line' : 14, 'value_list' : 'line.strip().split(\',\')' }
        self.parameter_mapping['options']['Stage Multiplier 1'] = {}
        self.parameter_mapping['options']['Stage Multiplier 1']['catastrophe_extent'] = { 'line' : 13, 'value' : 'line.strip()' }
        self.parameter_mapping['options']['Stage Multiplier 1']['catastrophe_affects'] = { 'line' : 14, 'value_list' : 'line.strip().split(\',\')' }
        self.parameter_mapping['options']['Probability of a Catastrophe 2'] = {}
        self.parameter_mapping['options']['Probability of a Catastrophe 2']['density_dependence_type_population_specific'] = { 'line' : 33, 'value' : 'line.split()[0]' }
        self.parameter_mapping['options']['Probability of a Catastrophe 2']['density_dependence_type_for_all'] = { 'from_line' : 34, 'lines' : 1, 'values' : 'line.split()[0]' }
        self.parameter_mapping['options']['Probability of a Catastrophe 2']['density_dependence_type_per_population'] = { 'from_line' : 45, 'lines' : 'populations', 'values' : 'line.split(\',\')[4]' }
        self.parameter_mapping['options']['Probability of a Catastrophe 2']['catastrophe_extent'] = { 'line' : 20, 'value' : 'line.strip()' }
        self.parameter_mapping['options']['Probability of a Catastrophe 2']['catastrophe_affects'] = { 'line' : 21, 'value_list' : 'line.strip().split(\',\')' }
        self.parameter_mapping['options']['Local Multiplier 2'] = {}
        self.parameter_mapping['options']['Local Multiplier 2']['density_dependence_type_population_specific'] = { 'line' : 33, 'value' : 'line.split()[0]' }
        self.parameter_mapping['options']['Local Multiplier 2']['density_dependence_type_for_all'] = { 'from_line' : 34, 'lines' : 1, 'values' : 'line.split()[0]' }
        self.parameter_mapping['options']['Local Multiplier 2']['density_dependence_type_per_population'] = { 'from_line' : 45, 'lines' : 'populations', 'values' : 'line.split(\',\')[4]' }
        self.parameter_mapping['options']['Local Multiplier 2']['catastrophe_extent'] = { 'line' : 20, 'value' : 'line.strip()' }
        self.parameter_mapping['options']['Local Multiplier 2']['catastrophe_affects'] = { 'line' : 21, 'value_list' : 'line.strip().split(\',\')' }
        self.parameter_mapping['options']['Stage Multiplier 2'] = {}
        self.parameter_mapping['options']['Stage Multiplier 2']['catastrophe_extent'] = { 'line' : 20, 'value' : 'line.strip()' }
        self.parameter_mapping['options']['Stage Multiplier 2']['catastrophe_affects'] = { 'line' : 21, 'value_list' : 'line.strip().split(\',\')' }
        self.parameter_mapping['options']['Probability of a Catastrophe 1 other extent'] = {}
        self.parameter_mapping['options']['Probability of a Catastrophe 1 other extent']['catastrophe_extent'] = { 'line' : 13, 'value' : 'line.strip()' }
        self.parameter_mapping['options']['Probability of a Catastrophe 2 other extent'] = {}
        self.parameter_mapping['options']['Probability of a Catastrophe 2 other extent']['catastrophe_extent'] = { 'line' : 20, 'value' : 'line.strip()' }
        self.parameter_mapping['options']['Fecundity Rates'] = {}
        self.parameter_mapping['options']['Fecundity Rates']['sex_structure'] = { 'line' : 38, 'value' : 'line.strip()' }
        self.parameter_mapping['options']['Fecundity Rates']['mating_system'] = { 'line' : 40, 'value' : 'line.strip()' }
        self.parameter_mapping['options']['Survival Rates'] = {}
        self.parameter_mapping['options']['Survival Rates']['sex_structure'] = { 'line' : 38, 'value' : 'line.strip()' }
        self.parameter_mapping['options']['Survival Rates']['mating_system'] = { 'line' : 40, 'value' : 'line.strip()' }
        self.parameter_mapping['alternatives'] = {}
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 1'] = {}
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 1']['option'] = 'catastrophe_extent'
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 1']['Local'] = { 'may_link_to_temporal_trend_files' : True, 'use_file_value' : 'max', 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 13, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 1']['Correlated'] = { 'may_link_to_temporal_trend_files' : True, 'use_file_value' : 'max', 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 13, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 1']['Regional'] = { 'may_link_to_temporal_trend_files' : True, 'use_file_value' : 'max', 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 12, 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Stage Multiplier 1'] = {}
        self.parameter_mapping['alternatives']['Stage Multiplier 1']['option'] = 'catastrophe_affects'
        self.parameter_mapping['alternatives']['Stage Multiplier 1']['Abundances'] = { 'mask_values' : [1], 'number_rows' : 1, 'number_columns' : 'lifestages', 'start_row' : 'constraints_matrix_label_line+2*lifestages+2', 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['alternatives']['Stage Multiplier 1']['Vital Rates'] = { 'mask_values' : [1], 'number_rows' : 'lifestages', 'number_columns' : 'lifestages', 'start_row' : 'constraints_matrix_label_line+lifestages+2', 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 2'] = {}
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 2']['option'] = 'catastrophe_extent'
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 2']['Local'] = { 'may_link_to_temporal_trend_files' : True, 'use_file_value' : 'max', 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 20, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 2']['Correlated'] = { 'may_link_to_temporal_trend_files' : True, 'use_file_value' : 'max', 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 20, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 2']['Regional'] = { 'may_link_to_temporal_trend_files' : True, 'use_file_value' : 'max', 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 19, 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Stage Multiplier 2'] = {}
        self.parameter_mapping['alternatives']['Stage Multiplier 2']['option'] = 'catastrophe_affects'
        self.parameter_mapping['alternatives']['Stage Multiplier 2']['Abundances'] = { 'mask_values' : [1], 'number_rows' : 1, 'number_columns' : 'lifestages', 'start_row' : 'constraints_matrix_label_line+3*lifestages+3', 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['alternatives']['Stage Multiplier 2']['Vital Rates'] = { 'mask_values' : [1], 'number_rows' : 'lifestages', 'number_columns' : 'lifestages', 'start_row' : 'constraints_matrix_label_line+2*lifestages+3', 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['alternatives']['Dispersal Matrix'] = {}
        self.parameter_mapping['alternatives']['Dispersal Matrix']['option'] = 'uses_function'
        self.parameter_mapping['alternatives']['Dispersal Matrix']['FALSE'] = { 'number_rows' : 'populations', 'number_columns' : 'populations', 'start_row' : 'migration_label_line+3', 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Dispersal Matrix']['TRUE'] = { 'calculate_matrix' : { 'type' : 'population', 'matrix' : 'dispersal', 'parameters' : {} }, 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 'migration_label_line+2', 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Correlation Matrix'] = {}
        self.parameter_mapping['alternatives']['Correlation Matrix']['option'] = 'uses_function'
        self.parameter_mapping['alternatives']['Correlation Matrix']['FALSE'] = { 'under_diagonal_only' : '', 'number_rows' : 'populations', 'number_columns' : 'populations', 'start_row' : 'correlation_label_line+3', 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Correlation Matrix']['TRUE'] = { 'calculate_matrix' : { 'type' : 'population', 'matrix' : 'correlation', 'parameters' : {} }, 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 'correlation_label_line+2', 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 1 other extent'] = {}
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 1 other extent']['option'] = 'catastrophe_extent'
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 1 other extent']['Local'] = { 'may_link_to_temporal_trend_files' : True, 'copy_files' : True, 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 12, 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 1 other extent']['Correlated'] = { 'may_link_to_temporal_trend_files' : True, 'copy_files' : True, 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 12, 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 1 other extent']['Regional'] = { 'may_link_to_temporal_trend_files' : True, 'copy_files' : True, 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 13, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 2 other extent'] = {}
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 2 other extent']['option'] = 'catastrophe_extent'
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 2 other extent']['Local'] = { 'may_link_to_temporal_trend_files' : True, 'copy_files' : True, 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 19, 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 2 other extent']['Correlated'] = { 'may_link_to_temporal_trend_files' : True, 'copy_files' : True, 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 19, 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Probability of a Catastrophe 2 other extent']['Regional'] = { 'may_link_to_temporal_trend_files' : True, 'copy_files' : True, 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 20, 'delimiter' : ',' }
        self.parameter_mapping['alternatives']['Fecundity Rates'] = {}
        self.parameter_mapping['alternatives']['Fecundity Rates']['option'] = 'sex_structure'
        fecundity_rates_submatrix_mask = { 'partition' : 'diagonal_upper_right', 'rows' : 'first', 'include_diagonal' : False }
        self.parameter_mapping['alternatives']['Fecundity Rates']['OnlyFemale'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'whole_matrix' : fecundity_rates_submatrix_mask } }
        self.parameter_mapping['alternatives']['Fecundity Rates']['OnlyMale'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'whole_matrix' : fecundity_rates_submatrix_mask } }
        self.parameter_mapping['alternatives']['Fecundity Rates']['AllIndividuals'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'whole_matrix' : fecundity_rates_submatrix_mask } }
        self.parameter_mapping['alternatives']['Fecundity Rates']['TwoSexes'] = { 'option' : 'mating_system' }
        self.parameter_mapping['alternatives']['Fecundity Rates']['TwoSexes']['Monogamous'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'quadrants' : { 'divide_at' : 'female_stages', 'upper_left' : fecundity_rates_submatrix_mask, 'lower_left' : fecundity_rates_submatrix_mask } } }
        self.parameter_mapping['alternatives']['Fecundity Rates']['TwoSexes']['Polygynous'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'quadrants' : { 'divide_at' : 'female_stages', 'upper_left' : fecundity_rates_submatrix_mask, 'lower_left' : fecundity_rates_submatrix_mask } } }
        self.parameter_mapping['alternatives']['Fecundity Rates']['TwoSexes']['Polyandrous'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'quadrants' : { 'divide_at' : 'female_stages', 'upper_right' : fecundity_rates_submatrix_mask, 'lower_right' : fecundity_rates_submatrix_mask } } }
        self.parameter_mapping['alternatives']['Survival Rates'] = {}
        self.parameter_mapping['alternatives']['Survival Rates']['option'] = 'sex_structure'
        survival_rates_submatrix_mask = { 'partition' : 'diagonal_lower_left', 'rows' : 'all', 'include_diagonal' : True }
        self.parameter_mapping['alternatives']['Survival Rates']['OnlyFemale'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'whole_matrix' : survival_rates_submatrix_mask } }
        self.parameter_mapping['alternatives']['Survival Rates']['OnlyMale'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'whole_matrix' : survival_rates_submatrix_mask } }
        self.parameter_mapping['alternatives']['Survival Rates']['AllIndividuals'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'whole_matrix' : survival_rates_submatrix_mask } }
        self.parameter_mapping['alternatives']['Survival Rates']['TwoSexes'] = { 'option' : 'mating_system' }
        self.parameter_mapping['alternatives']['Survival Rates']['TwoSexes']['Monogamous'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'quadrants' : { 'divide_at' : 'female_stages', 'upper_left' : survival_rates_submatrix_mask, 'lower_right' : survival_rates_submatrix_mask } } }
        self.parameter_mapping['alternatives']['Survival Rates']['TwoSexes']['Polygynous'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'quadrants' : { 'divide_at' : 'female_stages', 'upper_left' : survival_rates_submatrix_mask, 'lower_right' : survival_rates_submatrix_mask } } }
        self.parameter_mapping['alternatives']['Survival Rates']['TwoSexes']['Polyandrous'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'quadrants' : { 'divide_at' : 'female_stages', 'upper_left' : survival_rates_submatrix_mask, 'lower_right' : survival_rates_submatrix_mask } } }
        self.parameter_mapping['alternatives']['conditions'] = {}
        self.parameter_mapping['alternatives']['conditions']['Rmax'] = {}
        self.parameter_mapping['alternatives']['conditions']['Rmax']['option'] = 'density_dependence_type_population_specific'
        self.parameter_mapping['alternatives']['conditions']['Rmax']['No'] = { 'option' : 'density_dependence_type_for_all', 'values' : [], 'match_any' : ['LO', 'BH', 'LA', 'BA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Rmax']['Yes'] = { 'option' : 'density_dependence_type_per_population', 'values' : [], 'match_any' : ['LO', 'BH', 'LA', 'BA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Carrying Capacity'] = {}
        self.parameter_mapping['alternatives']['conditions']['Carrying Capacity']['option'] = 'density_dependence_type_population_specific'
        self.parameter_mapping['alternatives']['conditions']['Carrying Capacity']['No'] = { 'option' : 'density_dependence_type_for_all', 'values' : [], 'match_any' : ['LO', 'BH', 'CE', 'LA', 'BA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Carrying Capacity']['Yes'] = { 'option' : 'density_dependence_type_per_population', 'values' : [], 'match_any' : ['LO', 'BH', 'CE', 'LA', 'BA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Allee Effect'] = {}
        self.parameter_mapping['alternatives']['conditions']['Allee Effect']['option'] = 'density_dependence_type_population_specific'
        self.parameter_mapping['alternatives']['conditions']['Allee Effect']['No'] = { 'option' : 'density_dependence_type_for_all', 'values' : [], 'match_any' : ['EA', 'LA', 'BA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Allee Effect']['Yes'] = { 'option' : 'density_dependence_type_per_population', 'values' : [], 'match_any' : ['EA', 'LA', 'BA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1'] = {}
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['precondition'] = {}
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['precondition']['option'] = 'density_dependence_type_population_specific'
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['precondition']['No'] = { 'option' : 'density_dependence_type_for_all', 'values' : [], 'match_any' : ['EX', 'CE', 'EA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['precondition']['Yes'] = { 'option' : 'density_dependence_type_per_population', 'values' : [], 'match_any' : ['EX', 'CE', 'EA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['postcondition'] = {}
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['postcondition']['option'] = 'catastrophe_extent'
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['postcondition'][False] = {}
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['postcondition'][False]['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['postcondition'][False]['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['postcondition'][False]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['postcondition'][True] = {}
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['postcondition'][True]['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['postcondition'][True]['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 1']['postcondition'][True]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1'] = {}
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['precondition'] = {}
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['precondition']['option'] = 'density_dependence_type_population_specific'
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['precondition']['No'] = { 'option' : 'density_dependence_type_for_all', 'values' : [], 'match_any' : ['EX', 'CE', 'EA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['precondition']['Yes'] = { 'option' : 'density_dependence_type_per_population', 'values' : [], 'match_any' : ['EX', 'CE', 'EA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'] = {}
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition']['option'] = 'catastrophe_extent'
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][False] = {}
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][False]['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][False]['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][False]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : [], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][True] = {}
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][True]['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][True]['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][True]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : [], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Stage Multiplier 1'] = {}
        self.parameter_mapping['alternatives']['conditions']['Stage Multiplier 1']['option'] = 'catastrophe_extent'
        self.parameter_mapping['alternatives']['conditions']['Stage Multiplier 1']['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Stage Multiplier 1']['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Stage Multiplier 1']['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2'] = {}
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['precondition'] = {}
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['precondition']['option'] = 'density_dependence_type_population_specific'
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['precondition']['No'] = { 'option' : 'density_dependence_type_for_all', 'values' : [], 'match_any' : ['EX', 'CE', 'EA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['precondition']['Yes'] = { 'option' : 'density_dependence_type_per_population', 'values' : [], 'match_any' : ['EX', 'CE', 'EA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'] = {}
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition']['option'] = 'catastrophe_extent'
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][False] = {}
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][False]['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][False]['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][False]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : [], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][True] = {}
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][True]['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][True]['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][True]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : [], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2'] = {}
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['precondition'] = {}
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['precondition']['option'] = 'density_dependence_type_population_specific'
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['precondition']['No'] = { 'option' : 'density_dependence_type_for_all', 'values' : [], 'match_any' : ['EX', 'CE', 'EA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['precondition']['Yes'] = { 'option' : 'density_dependence_type_per_population', 'values' : [], 'match_any' : ['EX', 'CE', 'EA', 'CA', 'UD'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['postcondition'] = {}
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['postcondition']['option'] = 'catastrophe_extent'
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['postcondition'][False] = {}
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['postcondition'][False]['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['postcondition'][False]['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['postcondition'][False]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['postcondition'][True] = {}
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['postcondition'][True]['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['postcondition'][True]['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 2']['postcondition'][True]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Stage Multiplier 2'] = {}
        self.parameter_mapping['alternatives']['conditions']['Stage Multiplier 2']['option'] = 'catastrophe_extent'
        self.parameter_mapping['alternatives']['conditions']['Stage Multiplier 2']['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Stage Multiplier 2']['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Stage Multiplier 2']['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['conditions'] = {}
        self.parameter_mapping['conditions']['Rmax'] = { 'choose_alternative' : True }
        self.parameter_mapping['conditions']['Carrying Capacity'] = { 'choose_alternative' : True }
        self.parameter_mapping['conditions']['Allee Effect'] = { 'choose_alternative' : True }
        self.parameter_mapping['conditions']['Probability of a Catastrophe 1'] = { 'choose_alternative' : True }
        self.parameter_mapping['conditions']['Local Multiplier 1'] = { 'choose_alternative' : True }
        self.parameter_mapping['conditions']['Stage Multiplier 1'] = { 'choose_alternative' : True }
        self.parameter_mapping['conditions']['Probability of a Catastrophe 2'] = { 'choose_alternative' : True }
        self.parameter_mapping['conditions']['Local Multiplier 2'] = { 'choose_alternative' : True }
        self.parameter_mapping['conditions']['Stage Multiplier 2'] = { 'choose_alternative' : True }
        self.parameter_mapping['conditions']['Dispersal Matrix'] = { 'condition' : 'populations > 1', 'satisfied' : False }
        self.parameter_mapping['conditions']['Correlation Matrix'] = { 'condition' : 'populations > 1', 'satisfied' : False }
        self.parameter_mapping['additional'] = {}
        self.parameter_mapping['additional']['Replications'] = { 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 7, 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['additional']['Duration'] = { 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 8, 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['additional']['Populations'] = { 'value' : 'populations' }
        self.parameter_mapping['additional']['Density dependence'] = { 'line' : 26, 'value' : 'line.strip()' }
        self.parameter_mapping['additional']['Stages'] = { 'value' : 'lifestages' }
        self.parameter_mapping['additional']['population_coordinates'] = { 'number_rows' : 'populations', 'number_columns' : 2, 'start_row' : 45, 'start_column' : 2, 'delimiter' : ',' }
        self.parameter_mapping['additional']['temporal_trend_in_k'] = { 'may_link_to_temporal_trend_files' : True, 'link_to_parameter' : 'Carrying Capacity', 'use_file_value' : 'first', 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 10, 'delimiter' : ',' }
        self.parameter_mapping['additional']['relative_fecundity'] = { 'may_link_to_temporal_trend_files' : True, 'copy_files' : True, 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 16, 'delimiter' : ',' }
        self.parameter_mapping['additional']['relative_survival'] = { 'may_link_to_temporal_trend_files' : True, 'copy_files' : True, 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 17, 'delimiter' : ',' }
        self.parameter_mapping['additional']['relative_dispersal'] = { 'may_link_to_temporal_trend_files' : True, 'copy_files' : True, 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 25, 'delimiter' : ',' }
        self.parameter_mapping['additional']['relative_variability_fecundity'] = { 'may_link_to_temporal_trend_files' : True, 'copy_files' : True, 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 26, 'delimiter' : ',' }
        self.parameter_mapping['additional']['relative_variability_survival'] = { 'may_link_to_temporal_trend_files' : True, 'copy_files' : True, 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 27, 'delimiter' : ',' }
        self.parameter_mapping['additional']['user_defined_density_dependence_function'] = { 'file_with_full_path' : True, 'line' : 35, 'value' : 'line.strip()' }
        self.parameter_mapping['additional']['map_features'] = { 'file_with_full_path' : True, 'line' : 1, 'value' : 'line.split(\'map=\').pop().strip()' }
        self.parameter_mapping['additional']['Probability of a Catastrophe 1 other extent'] = { 'choose_alternative' : True }
        self.parameter_mapping['additional']['Probability of a Catastrophe 2 other extent'] = { 'choose_alternative' : True }
        self.parameter_mapping['Rmax'] = { 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 6, 'delimiter' : ',' }
        self.parameter_mapping['Carrying Capacity'] = { 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 7, 'delimiter' : ',' }
        self.parameter_mapping['Allee Effect'] = { 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 9, 'delimiter' : ',' }
        self.parameter_mapping['Probability of a Catastrophe 1'] = { 'choose_alternative' : True }
        self.parameter_mapping['Local Multiplier 1'] = { 'may_link_to_temporal_trend_files' : True, 'use_file_value' : 'first', 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 12, 'delimiter' : ',' }
        self.parameter_mapping['Stage Multiplier 1'] = { 'choose_alternative' : True }
        self.parameter_mapping['Probability of a Catastrophe 2'] = { 'choose_alternative' : True }
        self.parameter_mapping['Local Multiplier 2'] = { 'may_link_to_temporal_trend_files' : True, 'use_file_value' : 'first', 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 19, 'delimiter' : ',' }
        self.parameter_mapping['Stage Multiplier 2'] = { 'choose_alternative' : True }
        self.parameter_mapping['Dispersal Matrix'] = { 'choose_alternative' : True }
        self.parameter_mapping['Correlation Matrix'] = { 'choose_alternative' : True }
        self.parameter_mapping['Stage Matrix'] = { 'sectioned' : True, 'layers' : 'stage_matrix_types', 'number_rows' : 'lifestages', 'number_columns' : 'lifestages', 'start_row' : 'stage_matrix_label_line+5', 'next_layer' : '4+lifestages', 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['Fecundity Rates'] = { 'choose_alternative' : True }
        self.parameter_mapping['Survival Rates'] = { 'choose_alternative' : True }
        self.parameter_mapping['Environmental Variation'] = { 'layers' : 'std_dev_matrix_types', 'number_rows' : 'lifestages', 'number_columns' : 'lifestages', 'start_row' : 'std_dev_matrix_label_line+2', 'next_layer' : '1+lifestages', 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['Initial Abundance'] = { 'number_rows' : 'populations', 'number_columns' : 1, 'start_row' : 45, 'start_column' : 4, 'delimiter' : ',' }

        # Configure parameter data type. The default is 'float', and thus no entry is required for floats.
        self.parameter_data_types = {}
        self.parameter_data_types['Carrying Capacity'] = 'integer'
        self.parameter_data_types['Allee Effect'] = 'integer'
        self.parameter_data_types['Initial Abundance'] = 'integer'

        # Configure parameter output formats
        self.data_frame_mp_file_heading = 'Modified MP file'
        self.data_frame_heading_lines = 3
        self.data_frame_field_width = 15
        self.data_frame_percent_width = self.data_frame_field_width - 1
        self.data_frame_field_width_substitution = 'FW'
        self.data_frame_notes_marker = ' *'
        self.parameter_output_format = {}
        self.parameter_output_format['Rmax'] = { 'short_heading' : 'Rmax', 'mp_format' : '%.3G', 'display_format' : '%.3G', 'output_file_heading' : 'Rmax', 'output_file_format' : '%FW.3G', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Carrying Capacity'] = { 'short_heading' : 'Capac', 'mp_format' : '%d', 'display_format' : '%d', 'output_file_heading' : ['Carrying', 'Capacity', ''], 'output_file_format' : '%FWd', 'output_file_percent_format' : '%FWd%%' }
        self.parameter_output_format['Allee Effect'] = { 'short_heading' : 'Allee', 'mp_format' : '%d', 'display_format' : '%d', 'output_file_heading' : ['Allee', 'Effect', ''], 'output_file_format' : '%FWd', 'output_file_percent_format' : '%FWd%%' }
        self.parameter_output_format['Probability of a Catastrophe 1'] = { 'short_heading' : 'ProbCat1', 'mp_format' : '%.5G', 'display_format' : '%.3G', 'output_file_heading' : ['Probability', 'Catastrophe', '1'], 'output_file_format' : '%FW.5G', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Local Multiplier 1'] = { 'short_heading' : 'LocMult1', 'mp_format' : '%.3G', 'display_format' : '%.3G', 'output_file_heading' : ['Local', 'Multiplier', '1'], 'output_file_format' : '%FW.3G', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Stage Multiplier 1'] = { 'short_heading' : 'StgMult1', 'mp_format' : '%.6G', 'display_format' : '%.3G', 'output_file_heading' : ['Stage', 'Multipliers', '1'], 'output_file_format' : '%FW.3G', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Probability of a Catastrophe 2'] = { 'short_heading' : 'ProbCat2', 'mp_format' : '%.5G', 'display_format' : '%.3G', 'output_file_heading' : ['Probability', 'Catastrophe', '2'], 'output_file_format' : '%FW.5G', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Local Multiplier 2'] = { 'short_heading' : 'LocMult2', 'mp_format' : '%.3G', 'display_format' : '%.3G', 'output_file_heading' : ['Local', 'Multiplier', '2'], 'output_file_format' : '%FW.3G', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Stage Multiplier 2'] = { 'short_heading' : 'StgMult2', 'mp_format' : '%.6G', 'display_format' : '%.3G', 'output_file_heading' : ['Stage', 'Multipliers', '2'], 'output_file_format' : '%FW.3G', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Dispersal Matrix'] = { 'short_heading' : 'Disp', 'mp_format' : '%.5G', 'display_format' : '%.3G', 'output_file_heading' : ['Dispersal', 'Matrix', ''], 'output_file_format' : '%FW.3G', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Stage Matrix'] = { 'mp_format' : '%.9G' }
        self.parameter_output_format['Fecundity Rates'] = { 'short_heading' : 'Fecund', 'mp_format' : '%.9G', 'display_format' : '%.3G', 'output_file_heading' : ['Fecundity', 'Rates', ''], 'output_file_format' : '%FW.5G', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Survival Rates'] = { 'short_heading' : { 'single' : 'Surv', 'multiple' : ['LowSurv', 'HiSurv'] }, 'mp_format' : '%.9G', 'display_format' : '%.3G', 'output_file_heading' : ['Survival', 'Rates', ''], 'output_file_format' : '%FW.5G', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Environmental Variation'] = { 'short_heading' : 'EnvVar', 'mp_format' : '%.9G', 'display_format' : '%.3G', 'output_file_heading' : ['Environmental', 'Variation', ''], 'output_file_format' : '%FW.5G', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Initial Abundance'] = { 'short_heading' : 'InitN', 'mp_format' : '%d', 'display_format' : '%d', 'output_file_heading' : ['Initial', 'Abundance', ''], 'output_file_format' : '%FWd', 'output_file_percent_format' : '%FWd%%' }
        self.parameter_output_format['Correlation Matrix'] = { 'short_heading' : 'Corr', 'mp_format' : '%.5G', 'display_format' : '%.3G', 'output_file_heading' : ['Correlation', 'Matrix', ''], 'output_file_format' : '%FW.3G', 'output_file_percent_format' : '%FW.1f%%' }

        # Configure how to select the initial parameter value displayed
        self.parameter_initial_display = {}
        self.parameter_initial_display['Initial Abundance'] = 'first_non_zero'
        self.parameter_initial_display['Rmax'] = 'first_non_zero'
        self.parameter_initial_display['Carrying Capacity'] = 'first_non_zero'
        self.parameter_initial_display['Allee Effect'] = 'first_non_zero'
        self.parameter_initial_display['Probability of a Catastrophe 1'] = 'first_non_zero'
        self.parameter_initial_display['Local Multiplier 1'] = 'first_non_zero'
        self.parameter_initial_display['Stage Multiplier 1'] = 'first_non_zero'
        self.parameter_initial_display['Probability of a Catastrophe 2'] = 'first_non_zero'
        self.parameter_initial_display['Local Multiplier 2'] = 'first_non_zero'
        self.parameter_initial_display['Stage Multiplier 2'] = 'first_non_zero'
        self.parameter_initial_display['Dispersal Matrix'] = 'first_non_zero'
        self.parameter_initial_display['Correlation Matrix'] = 'first_non_zero'
        self.parameter_initial_display['Fecundity Rates'] = 'last_non_zero'
        self.parameter_initial_display['Survival Rates'] = 'last_non_zero'
        self.parameter_initial_display['Environmental Variation'] = 'first_non_zero'

        # Configure how to express the data frame values for the parameters (default uses unique or percentage)
        self.parameter_data_frame = {}
        self.parameter_data_frame['Initial Abundance'] = 'sum_values'
        self.parameter_data_frame['Carrying Capacity'] = 'sum_values'

        # Configure how to express the result input values for the parameters (default uses unique or percentage)
        self.parameter_result_input = {}
        self.parameter_result_input['Initial Abundance'] = 'sum_values'
        self.parameter_result_input['Rmax'] = 'first_value'
        self.parameter_result_input['Carrying Capacity'] = 'sum_values'
        self.parameter_result_input['Allee Effect'] = 'first_value'
        self.parameter_result_input['Probability of a Catastrophe 1'] = 'unique_or_percent'
        self.parameter_result_input['Local Multiplier 1'] = 'unique_or_percent'
        self.parameter_result_input['Stage Multiplier 1'] = 'unique_or_percent'
        self.parameter_result_input['Probability of a Catastrophe 2'] = 'unique_or_percent'
        self.parameter_result_input['Local Multiplier 2'] = 'unique_or_percent'
        self.parameter_result_input['Stage Multiplier 2'] = 'unique_or_percent'
        self.parameter_result_input['Dispersal Matrix'] = 'percent_change'
        self.parameter_result_input['Correlation Matrix'] = 'percent_change'
        self.parameter_result_input['Fecundity Rates'] = 'last_non_zero'
        self.parameter_result_input['Survival Rates'] = ['min_non_zero', 'max']
        self.parameter_result_input['Environmental Variation'] = 'percent_change'

        # Configure file generation numbering format
        self.file_generation_numbering_format = '_%04d' # generates numbering from _0001
        
        # Configure parameter constraints
        self.parameter_constraints = {}
        self.parameter_constraints['Rmax'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 1 }]
        self.parameter_constraints['Probability of a Catastrophe 1'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 }]
        self.parameter_constraints['Probability of a Catastrophe 2'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 }]
        self.parameter_constraints['Dispersal Matrix'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 },
                                                          { 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1 }]
        self.parameter_constraints['Correlation Matrix'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 }]
        self.parameter_constraints['Survival Rates'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 },
                                                        { 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1 }]

        # Configure the constraint probability threshold for unbounded distributions (tail)
        self.constraint_probability_threshold_for_unbounded_distributions = 0.01

        # Configure constraint application strategies (only warnings implemented to date)
        self.constraint_application_strategy = {}
        self.constraint_application_strategy['Rmax'] = MpParameterBoundConstraintHelper.WARNING_ONLY
        self.constraint_application_strategy['Probability of a Catastrophe 1'] = MpParameterBoundConstraintHelper.WARNING_ONLY
        self.constraint_application_strategy['Probability of a Catastrophe 2'] = MpParameterBoundConstraintHelper.WARNING_ONLY
        self.constraint_application_strategy['Dispersal Matrix'] = MpParameterBoundConstraintHelper.WARNING_ONLY
        self.constraint_application_strategy['Correlation Matrix'] = MpParameterBoundConstraintHelper.WARNING_ONLY
        self.constraint_application_strategy['Survival Rates'] = MpParameterBoundConstraintHelper.WARNING_ONLY

        # Configure selection of results collected in the desired presentation order
        self.metapop_results = ['Expected Minimum Abundance', 'Final number of occupied patches', 'Final N for persistent runs', 'Total extinction risk', 'Quasi extinction risk']
        
        # Configure the names of the RAMAS Metapop result files that may be used by the tool
        self.metapop_result_files = ['Abund.txt', 'FinalStageN.txt', 'Harvest.txt', 'HarvestRisk.txt', 'IntExpRisk.txt', 'IntExtRisk.txt', 'IntPerDec.txt', 'LocalOcc.txt', 'LocExtDur.txt', 'MetapopOcc.txt', 'QuasiExp.txt', 'QuasiExt.txt', 'TerExpRisk.txt', 'TerExtRisk.txt', 'TerPerDec.txt']

        # Configure the result file details (not all used)
        self.metapop_result_file_details = {}
        self.metapop_result_file_details['Abund.txt'] = { 'title' : 'Trajectory summary' }
        self.metapop_result_file_details['FinalStageN.txt'] = { 'title' : 'Final stage abundances' }
        self.metapop_result_file_details['Harvest.txt'] = { 'title' : 'Harvest summary' }
        self.metapop_result_file_details['HarvestRisk.txt'] = { 'title' : 'Risk of low harvest' }
        self.metapop_result_file_details['IntExpRisk.txt'] = { 'title' : 'Interval explosion risk' }
        self.metapop_result_file_details['IntExtRisk.txt'] = { 'title' : 'Interval extinction risk' }
        self.metapop_result_file_details['IntPerDec.txt'] = { 'title' : 'Interval percent decline' }
        self.metapop_result_file_details['LocalOcc.txt'] = { 'title' : 'Local occupancy' }
        self.metapop_result_file_details['LocExtDur.txt'] = { 'title' : 'Local extinction duration' }
        self.metapop_result_file_details['MetapopOcc.txt'] = { 'title' : 'Metapopulation occupancy' }
        self.metapop_result_file_details['QuasiExp.txt'] = { 'title' : 'Time to quasi-explosion' }
        self.metapop_result_file_details['QuasiExt.txt'] = { 'title' : 'Time to quasi-extinction' }
        self.metapop_result_file_details['TerExpRisk.txt'] = { 'title' : 'Terminal explosion risk' }
        self.metapop_result_file_details['TerExtRisk.txt'] = { 'title' : 'Terminal extinction risk' }
        self.metapop_result_file_details['TerPerDec.txt'] = { 'title' : 'Terminal percent decline' }

        # Configure any extraction dependencies that exist between result files
        self.metapop_result_file_dependencies = {}
        self.metapop_result_file_dependencies['IntExtRisk.txt'] = { 'dependent_on' : ['QuasiExt.txt'] }

        # Configure result component mapping to RAMAS Metapop result files
        common_result_component_mapping = {}
        common_result_component_mapping['populations'] = { 'pattern' : '^\s+\d+\s+populations', 'value' : 'match' } # not used as yet
        common_result_component_mapping['replications'] = { 'pattern' : '^\s+\d+\s+replications', 'value' : 'match' } # not used as yet
        common_result_component_mapping['duration'] = { 'pattern' : 'Duration = \d+', 'value' : 'int(match.split()[2])' }
        self.metapop_result_component_mapping = {}
        self.metapop_result_component_mapping['Abund.txt'] = { 'process_order' : ['duration', 'title_line', 'mean_final_n', 'mean_n', 'time'] }
        self.metapop_result_component_mapping['Abund.txt']['duration'] = common_result_component_mapping['duration']
        self.metapop_result_component_mapping['Abund.txt']['title_line'] = { 'pattern' : self.metapop_result_file_details['Abund.txt']['title'], 'value' : 'line' }
        self.metapop_result_component_mapping['Abund.txt']['mean_final_n'] = { 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 'title_line+duration+4', 'start_column' : 4, 'delimiter' : '' }
        self.metapop_result_component_mapping['Abund.txt']['mean_n'] = { 'number_rows' : 'duration+1', 'number_columns' : 1, 'start_row' : 'title_line+4', 'start_column' : 4, 'delimiter' : '' }
        self.metapop_result_component_mapping['Abund.txt']['time'] = { 'number_rows' : 'duration+1', 'number_columns' : 1, 'start_row' : 'title_line+4', 'start_column' : 1, 'delimiter' : '' }
        self.metapop_result_component_mapping['QuasiExt.txt'] = { 'process_order' : ['quasi_ext_threshold'] }
        self.metapop_result_component_mapping['QuasiExt.txt']['quasi_ext_threshold'] = { 'pattern' : 'Threshold level = \d+', 'value' : 'int(match.split()[3])' }
        self.metapop_result_component_mapping['IntExtRisk.txt'] = { 'process_order' : ['title_line', 'expected_min_n', 'initial_threshold', 'initial_ext_risk', 'quasi_ext_threshold', 'thresholds_to_quasi', 'ext_risk_to_quasi'] }
        self.metapop_result_component_mapping['IntExtRisk.txt']['title_line'] = { 'pattern' : self.metapop_result_file_details['IntExtRisk.txt']['title'], 'value' : 'line' }
        self.metapop_result_component_mapping['IntExtRisk.txt']['expected_min_n'] = { 'pattern' : 'Expected minimum abundance = \d+.\d+', 'value' : 'float(match.split()[4])' }
        self.metapop_result_component_mapping['IntExtRisk.txt']['initial_threshold'] = { 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 'title_line+5', 'start_column' : 1, 'delimiter' : '' }
        self.metapop_result_component_mapping['IntExtRisk.txt']['initial_ext_risk'] = { 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 'title_line+5', 'start_column' : 2, 'delimiter' : '' }
        self.metapop_result_component_mapping['IntExtRisk.txt']['quasi_ext_threshold'] = { 'dependent_on' : { 'result_file' : 'QuasiExt.txt', 'component' : 'quasi_ext_threshold' } }
        self.metapop_result_component_mapping['IntExtRisk.txt']['thresholds_to_quasi'] = { 'until_value_condition' : '>= quasi_ext_threshold', 'start_row' : 'title_line+5', 'column' : 1, 'delimiter' : '' }
        self.metapop_result_component_mapping['IntExtRisk.txt']['ext_risk_to_quasi'] = { 'number_rows' : 'len(thresholds_to_quasi)', 'number_columns' : 1, 'start_row' : 'title_line+5', 'start_column' : 2, 'delimiter' : '' }
        self.metapop_result_component_mapping['MetapopOcc.txt'] = { 'process_order' : ['duration', 'title_line', 'final_n_occ_patches', 'n_occ_patches', 'time'] }
        self.metapop_result_component_mapping['MetapopOcc.txt']['duration'] = common_result_component_mapping['duration']
        self.metapop_result_component_mapping['MetapopOcc.txt']['title_line'] = { 'pattern' : self.metapop_result_file_details['MetapopOcc.txt']['title'], 'value' : 'line' }
        self.metapop_result_component_mapping['MetapopOcc.txt']['final_n_occ_patches'] = { 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 'title_line+duration+4', 'start_column' : 4, 'delimiter' : '' }
        self.metapop_result_component_mapping['MetapopOcc.txt']['n_occ_patches'] = { 'number_rows' : 'duration+1', 'number_columns' : 1, 'start_row' : 'title_line+4', 'start_column' : 4, 'delimiter' : '' }
        self.metapop_result_component_mapping['MetapopOcc.txt']['time'] = { 'number_rows' : 'duration+1', 'number_columns' : 1, 'start_row' : 'title_line+4', 'start_column' : 1, 'delimiter' : '' }

        # Configure result mapping to RAMAS Metapop result file components
        self.metapop_result_mapping = {}
        self.metapop_result_mapping['Expected Minimum Abundance'] = { 'collect' : [{ 'result_file' : 'IntExtRisk.txt', 'component' : 'expected_min_n' }], 'value' : 'expected_min_n' }
        self.metapop_result_mapping['Final number of occupied patches'] = { 'collect' : [{ 'result_file' : 'MetapopOcc.txt', 'component' : 'final_n_occ_patches' }], 'value' : 'final_n_occ_patches' }
        self.metapop_result_mapping['Final N for persistent runs'] = { 'collect' : [{ 'result_file' : 'Abund.txt', 'component' : 'mean_final_n' }, { 'result_file' : 'IntExtRisk.txt', 'component' : 'initial_threshold' }, { 'result_file' : 'IntExtRisk.txt', 'component' : 'initial_ext_risk' }], 'condition' : 'initial_threshold == 0 and initial_ext_risk < 1', 'value' : 'mean_final_n/(1-initial_ext_risk)', 'alt_value' : 'mean_final_n' }
        self.metapop_result_mapping['Total extinction risk'] = { 'collect' : [{ 'result_file' : 'IntExtRisk.txt', 'component' : 'initial_threshold' }, { 'result_file' : 'IntExtRisk.txt', 'component' : 'initial_ext_risk' }], 'condition' : 'initial_threshold == 0', 'value' : 'initial_ext_risk', 'alt_value' : '0.0' }
        self.metapop_result_mapping['Quasi extinction risk'] = { 'collect' : [{ 'result_file' : 'IntExtRisk.txt', 'component' : 'initial_threshold' }, { 'result_file' : 'IntExtRisk.txt', 'component' : 'quasi_ext_threshold' }, { 'result_file' : 'IntExtRisk.txt', 'component' : 'thresholds_to_quasi' }, { 'result_file' : 'IntExtRisk.txt', 'component' : 'ext_risk_to_quasi' }], 'condition' : 'initial_threshold <= quasi_ext_threshold', 'value' : 'linear_interpolate(quasi_ext_threshold, thresholds_to_quasi, ext_risk_to_quasi)', 'alt_value' : '0.0' }
        
        # Configure result output and result summary formats
        self.result_summary_run_heading = 'Run'
        self.result_summary_heading_lines = self.data_frame_heading_lines
        self.result_summary_field_width = self.data_frame_field_width # = 15
        self.result_summary_percent_width = self.result_summary_field_width-1
        self.result_summary_field_width_substitution = self.data_frame_field_width_substitution
        self.result_output_format = {}
        self.result_output_format['Expected Minimum Abundance'] = { 'short_heading' : 'EMA', 'output_file_heading' : ['Expected', 'Minimum', 'Abundance'], 'output_file_format' : '%FW.4G' }
        self.result_output_format['Final number of occupied patches'] = { 'short_heading' : 'FinalOcc', 'output_file_heading' : ['Final number', 'of occupied', 'patches'], 'output_file_format' : '%FW.4G' }
        self.result_output_format['Final N for persistent runs'] = { 'short_heading' : 'FinalN', 'output_file_heading' : ['Final N for', 'persistent', 'runs'], 'output_file_format' : '%FW.4G' }
        self.result_output_format['Total extinction risk'] = { 'short_heading' : 'Ext', 'output_file_heading' : ['Total', 'extinction', 'risk'], 'output_file_format' : '%FW.4G' }
        self.result_output_format['Quasi extinction risk'] = { 'short_heading' : 'QuasiExt', 'output_file_heading' : ['Quasi', 'extinction', 'risk'], 'output_file_format' : '%FW.4G' }

        # Configure selection of result plots collected in the desired presentation order
        self.metapop_result_plots = ['Predicted Abundance', 'Predicted Metapopulation Occupancy']

        # Configure result plot mapping to RAMAS Metapop result file components
        self.metapop_result_plot_mapping = {}
        self.metapop_result_plot_mapping['Predicted Abundance'] = { 'fields': ['Time', 'Average'], 'collect' : [{ 'result_file' : 'Abund.txt', 'component' : 'time' }, { 'result_file' : 'Abund.txt', 'component' : 'mean_n' }], 'value' : 'join_arrays(time,mean_n)' }
        self.metapop_result_plot_mapping['Predicted Metapopulation Occupancy'] = { 'fields': ['Time', 'Average'], 'collect' : [{ 'result_file' : 'MetapopOcc.txt', 'component' : 'time' }, { 'result_file' : 'MetapopOcc.txt', 'component' : 'n_occ_patches' }], 'value' : 'join_arrays(time,n_occ_patches)' }

        # Configure result plot calculated data (calculated across samples)
        common_fields = ['Time', 'Minimum', 'Mean-2SD', 'Mean-1SD', 'Mean', 'Mean+1SD', 'Mean+2SD', 'Maximum']
        common_calculations = { 'fields' : common_fields, 'calculations' : { 'Minimum' : { 'field' : 'Average', 'calculate' : 'minimum' },
                                                                             'Mean-2SD' : { 'field' : 'Average', 'calculate' : 'mean-2*stdev' },
                                                                             'Mean-1SD' : { 'field' : 'Average', 'calculate' : 'mean-1*stdev' },
                                                                             'Mean' : { 'field' : 'Average', 'calculate' : 'mean' },
                                                                             'Mean+1SD' : { 'field' : 'Average', 'calculate' : 'mean+1*stdev' },
                                                                             'Mean+2SD' : { 'field' : 'Average', 'calculate' : 'mean+2*stdev' },
                                                                             'Maximum' : { 'field' : 'Average', 'calculate' : 'maximum' } } }
        self.result_plot_calculated_data = {}
        self.result_plot_calculated_data['Predicted Abundance'] = common_calculations
        self.result_plot_calculated_data['Predicted Metapopulation Occupancy'] = common_calculations

        # Configure result plot file and visualisation details
        self.result_plot_intervals = ['mean', 'mean-1sd', 'mean-2sd', 'min-mean-max']
        self.result_plot_default_interval = 'mean-2sd'
        self.result_plot_interval_data = {}
        self.result_plot_interval_data['mean'] = 'Mean'
        self.result_plot_interval_data['mean-1sd'] = { 'lower' : 'Mean-1SD', 'mid' : 'Mean', 'upper' : 'Mean+1SD' }
        self.result_plot_interval_data['mean-2sd'] = { 'lower' : 'Mean-2SD', 'mid' : 'Mean', 'upper' : 'Mean+2SD' }
        self.result_plot_interval_data['min-mean-max'] = { 'lower' : 'Minimum', 'mid' : 'Mean', 'upper' : 'Maximum' }
        self.result_plot_interval_label = {}
        self.result_plot_interval_label['mean'] = 'Mean'
        self.result_plot_interval_label['mean-1sd'] = 'Mean '+u'\u00B1'+' 1 Standard Deviation'
        self.result_plot_interval_label['mean-2sd'] = 'Mean '+u'\u00B1'+' 2 Standard Deviation'
        self.result_plot_interval_label['min-mean-max'] = 'Minimum-Mean-Maximum'
        self.result_plot_file_details = {}
        self.result_plot_file_details['Predicted Abundance'] = { 'filename' : 'Predicted_Abundance', 'fields' : common_fields }
        self.result_plot_file_details['Predicted Metapopulation Occupancy'] = { 'filename' : 'Predicted_Metapopulation_Occupancy', 'fields' : common_fields }
        self.result_plot_view_details = {}
        self.result_plot_view_details['Predicted Abundance'] = {}
        self.result_plot_view_details['Predicted Abundance']['mean'] = { 'plot_type' : 'time_series', 'plot_title' : 'Predicted Abundance', 'x_data' : 'Time', 'x_label' : 'Time',
                                                                         'y_data' : self.result_plot_interval_data['mean'], 'y_label' : self.result_plot_interval_label['mean'] }
        self.result_plot_view_details['Predicted Abundance']['mean-1sd'] = { 'plot_type' : 'time_series_interval', 'plot_title' : 'Predicted Abundance', 'x_data' : 'Time', 'x_label' : 'Time',
                                                                             'y_data' : self.result_plot_interval_data['mean-1sd'], 'y_label' : self.result_plot_interval_label['mean-1sd'] }
        self.result_plot_view_details['Predicted Abundance']['mean-2sd'] = { 'plot_type' : 'time_series_interval', 'plot_title' : 'Predicted Abundance', 'x_data' : 'Time', 'x_label' : 'Time',
                                                                             'y_data' : self.result_plot_interval_data['mean-2sd'], 'y_label' : self.result_plot_interval_label['mean-2sd'] }
        self.result_plot_view_details['Predicted Abundance']['min-mean-max'] = { 'plot_type' : 'time_series_interval', 'plot_title' : 'Predicted Abundance', 'x_data' : 'Time', 'x_label' : 'Time',
                                                                                 'y_data' : self.result_plot_interval_data['min-mean-max'], 'y_label' : self.result_plot_interval_label['min-mean-max'] }
        self.result_plot_view_details['Predicted Metapopulation Occupancy'] = {}
        self.result_plot_view_details['Predicted Metapopulation Occupancy']['mean'] = { 'plot_type' : 'time_series', 'plot_title' : 'Predicted Metapopulation Occupancy', 'x_data' : 'Time', 'x_label' : 'Time',
                                                                                        'y_data' : self.result_plot_interval_data['mean'], 'y_label' : self.result_plot_interval_label['mean'] }
        self.result_plot_view_details['Predicted Metapopulation Occupancy']['mean-1sd'] = { 'plot_type' : 'time_series_interval', 'plot_title' : 'Predicted Metapopulation Occupancy', 'x_data' : 'Time', 'x_label' : 'Time',
                                                                                            'y_data' : self.result_plot_interval_data['mean-1sd'], 'y_label' : self.result_plot_interval_label['mean-1sd'] }
        self.result_plot_view_details['Predicted Metapopulation Occupancy']['mean-2sd'] = { 'plot_type' : 'time_series_interval', 'plot_title' : 'Predicted Metapopulation Occupancy', 'x_data' : 'Time', 'x_label' : 'Time',
                                                                                            'y_data' : self.result_plot_interval_data['mean-2sd'], 'y_label' : self.result_plot_interval_label['mean-2sd'] }
        self.result_plot_view_details['Predicted Metapopulation Occupancy']['min-mean-max'] = { 'plot_type' : 'time_series_interval', 'plot_title' : 'Predicted Metapopulation Occupancy', 'x_data' : 'Time', 'x_label' : 'Time',
                                                                                                'y_data' : self.result_plot_interval_data['min-mean-max'], 'y_label' : self.result_plot_interval_label['min-mean-max'] }
                                
        # Configuration not in tool options (yet)
        self.minimum_number_of_samples = 50
        self.maximum_parameter_matrix_size = 2500
        self.oversized_parameter_matrix_frame_size = 6

        # Configuration relating to tool options:

        self.tool_option_parameters = ['metapop_exe_location',
                                       'run_metapop_batch_locally',
                                       'default_generated_file_location',
                                       'number_of_metapop_iterations',
                                       'metapop_simulation_duration',
                                       'use_mp_baseline_values',
                                       'reset_sampling_when_loading_file',
                                       'default_number_of_lhs_samples',
                                       'default_number_of_random_samples',
                                       'enforce_minimum_number_of_samples',
                                       'default_lhs_uniform_distr_lower_setting',
                                       'default_lhs_uniform_distr_upper_setting',
                                       'default_lhs_gaussian_distr_mean_setting',
                                       'default_lhs_gaussian_distr_stdev_setting',
                                       'default_lhs_triangular_distr_lower_setting',
                                       'default_lhs_triangular_distr_upper_setting',
                                       'default_lhs_triangular_distr_mode_setting',
                                       'default_lhs_lognormal_distr_lower_setting',
                                       'default_lhs_lognormal_distr_scale_setting',
                                       'default_lhs_lognormal_distr_scale_increment',
                                       'default_lhs_lognormal_distr_sigma_setting',
                                       'default_lhs_lognormal_distr_sigma_increment',
                                       'default_lhs_beta_distr_lower_setting',
                                       'default_lhs_beta_distr_upper_setting',
                                       'default_lhs_beta_distr_alpha_setting',
                                       'default_lhs_beta_distr_alpha_increment',
                                       'default_lhs_beta_distr_beta_setting',
                                       'default_lhs_beta_distr_beta_increment',
                                       'default_sample_bounds_for_random',
                                       'default_sample_bounds_for_full_factorial',
                                       'auto_run_results_summary_tool']

        self.tool_option_parameter_types = {'metapop_exe_location' : str,
                                            'run_metapop_batch_locally' : bool,
                                            'default_generated_file_location' : str,
                                            'number_of_metapop_iterations' : int,
                                            'metapop_simulation_duration' : int,
                                            'use_mp_baseline_values' : bool,
                                            'reset_sampling_when_loading_file' : bool,
                                            'default_number_of_lhs_samples' : int,
                                            'default_number_of_random_samples' : int,
                                            'enforce_minimum_number_of_samples' : bool,
                                            'default_lhs_uniform_distr_lower_setting' : float,
                                            'default_lhs_uniform_distr_upper_setting' : float,
                                            'default_lhs_gaussian_distr_mean_setting' : float,
                                            'default_lhs_gaussian_distr_stdev_setting' : float,
                                            'default_lhs_triangular_distr_lower_setting' : float,
                                            'default_lhs_triangular_distr_upper_setting' : float,
                                            'default_lhs_triangular_distr_mode_setting' : float,
                                            'default_lhs_lognormal_distr_lower_setting' : float,
                                            'default_lhs_lognormal_distr_scale_setting' : float,
                                            'default_lhs_lognormal_distr_scale_increment' : float,
                                            'default_lhs_lognormal_distr_sigma_setting' : float,
                                            'default_lhs_lognormal_distr_sigma_increment' : float,
                                            'default_lhs_beta_distr_lower_setting' : float,
                                            'default_lhs_beta_distr_upper_setting' : float,
                                            'default_lhs_beta_distr_alpha_setting' : float,
                                            'default_lhs_beta_distr_alpha_increment' : float,
                                            'default_lhs_beta_distr_beta_setting' : float,
                                            'default_lhs_beta_distr_beta_increment' : float,
                                            'default_sample_bounds_for_random' : float,
                                            'default_sample_bounds_for_full_factorial' : float,
                                            'auto_run_results_summary_tool' : bool}

        # Mapping for LHS option default settings
        self.lhs_option_default_settings = {}
        self.lhs_option_default_settings['Uniform'] = { 'Lower' : 'default_lhs_uniform_distr_lower_setting', 'Upper' : 'default_lhs_uniform_distr_upper_setting' }
        self.lhs_option_default_settings['Gaussian'] = { 'Mean' : 'default_lhs_gaussian_distr_mean_setting', 'Std. Dev.' : 'default_lhs_gaussian_distr_stdev_setting' }
        self.lhs_option_default_settings['Triangular'] = { 'Lower (a)' : 'default_lhs_triangular_distr_lower_setting', 'Upper (b)' : 'default_lhs_triangular_distr_upper_setting', 'Mode (c)' : 'default_lhs_triangular_distr_mode_setting' }
        self.lhs_option_default_settings['Lognormal'] = { 'Lower' : 'default_lhs_lognormal_distr_lower_setting', 'Scale' : 'default_lhs_lognormal_distr_scale_setting', 'Scale Increment' : 'default_lhs_lognormal_distr_scale_increment', 'Sigma' : 'default_lhs_lognormal_distr_sigma_setting', 'Sigma Increment' : 'default_lhs_lognormal_distr_sigma_increment' }
        self.lhs_option_default_settings['Beta'] = { 'Lower' : 'default_lhs_beta_distr_lower_setting', 'Upper' : 'default_lhs_beta_distr_upper_setting', 'Alpha' : 'default_lhs_beta_distr_alpha_setting', 'Alpha Increment' : 'default_lhs_beta_distr_alpha_increment', 'Beta' : 'default_lhs_beta_distr_beta_setting', 'Beta Increment' : 'default_lhs_beta_distr_beta_increment' }

        # The local/ext disk location of the RAMAS Metapop program
        self.metapop_exe_location = r'C:\Program Files\RAMASGIS\Metapop.exe'

        # Metapop batch file run on local machine
        self.run_metapop_batch_locally = True

        # The default local disk location for generated files
        self.default_generated_file_location = r'C:\afat32\Dropbox\GlobalEcologyGroup\ProjectCode\SensitivityAnalysisToolset\v0.4\Test'

        # The number of RAMAS Metapop iterations/replications per scenario and simulation duration
        self.number_of_metapop_iterations = 100
        self.metapop_simulation_duration = 20
        self.use_mp_baseline_values = False

        # Reset the sampling parameters when loading a new baseline file
        self.reset_sampling_when_loading_file = True

        # The default number of samples for LHS/Random
        self.default_number_of_lhs_samples = None
        self.default_number_of_random_samples = None
        self.enforce_minimum_number_of_samples = True

        # The default LHS settings
        self.default_lhs_uniform_distr_lower_setting = 90.
        self.default_lhs_uniform_distr_upper_setting = 110.
        self.default_lhs_gaussian_distr_mean_setting = 100.
        self.default_lhs_gaussian_distr_stdev_setting = 5.
        self.default_lhs_triangular_distr_lower_setting = 90.
        self.default_lhs_triangular_distr_upper_setting = 110.
        self.default_lhs_triangular_distr_mode_setting = 100.
        self.default_lhs_lognormal_distr_lower_setting = 100.
        self.default_lhs_lognormal_distr_scale_setting = 10.
        self.default_lhs_lognormal_distr_scale_increment = 1.
        self.default_lhs_lognormal_distr_sigma_setting = 1.
        self.default_lhs_lognormal_distr_sigma_increment = 0.1
        self.default_lhs_beta_distr_lower_setting = 90.
        self.default_lhs_beta_distr_upper_setting = 110.
        self.default_lhs_beta_distr_alpha_setting = 1.
        self.default_lhs_beta_distr_alpha_increment = 0.1
        self.default_lhs_beta_distr_beta_setting = 1.
        self.default_lhs_beta_distr_beta_increment = 0.1

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
        orig_config_file_path = path.join(getcwd(), self.tool_config_file)
        user_config_file_path = path.join(self.user_application_data_directory, self.tool_config_file)
        if not path.exists(user_config_file_path) and path.exists(orig_config_file_path) :
            copyfile(orig_config_file_path, user_config_file_path)
        if path.exists(user_config_file_path) :
            f = open(user_config_file_path)
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

        config_file_path = path.join(self.user_application_data_directory, self.tool_config_file)

        # Read config file
        if path.exists(config_file_path) :

            # Read file lines
            f = open(config_file_path)
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
        f = open(config_file_path, 'w')
        f.writelines(file_lines)
        f.close()

# END MetapopConfiguration
        
## Application GUI
## * Constructs tool GUI components using parameter configuration
## * Defines and follows a workflow of step completion
## * Performs tool operations utilising mp file helper and sample generator modules
class ApplicationGUI(tk.Frame) :

    # Initialise GUI and workflow
    def __init__(self, application_name, user_application_data_directory, master=None) :

        tk.Frame.__init__(self, master)
        self.grid()

        # Set user application data directory
        self.user_application_data_directory = user_application_data_directory

        # Load MP File Parameter Configuration
        self.config = MetapopConfiguration(self.user_application_data_directory, application_name+'_config.txt')

        # Warn if config file not loaded properly
        if self.config.config_warning :
            showwarning('Error Loading Configuration', self.config.config_warning)

        # Create a MP file extractor and generator helper
        self.mp_file_helper = MpFileExtractorAndGeneratorHelper(self.config)

        # Create a MP parameter constraint helper
        self.mp_constraint_helper = MpParameterBoundConstraintHelper(self.config)

        # Get current config tool options
        tool_option_values = self.config.getToolOptions()

        # If batch is run locally and current Metapop exe location doesn't exist try to find it
        if tool_option_values['run_metapop_batch_locally'] and not path.exists(tool_option_values['metapop_exe_location']) :
            metapop_exe_path = environ['PROGRAMFILES']
            metapop_exe_path = path.join(metapop_exe_path, self.findMatchingInDirectory(metapop_exe_path, 'RAMASGIS'))
            metapop_exe_path = path.join(metapop_exe_path, self.findMatchingInDirectory(metapop_exe_path, 'Metapop.exe'))
            if self.mp_file_helper.splitPath(metapop_exe_path)['name'].lower().find('metapop.exe') != -1 :
                self.config.setToolOptions({ 'metapop_exe_location' : metapop_exe_path })

        # Maintain flag to indicate that the parameters were successfully extracted from the baseline file
        self.extraction_ok = False

        # Extracted parameter values from the baseline MP file when loaded
        self.baseline_parameter_values = { 'extracted' : {}, 'calculated' : {}, 'file_links' : {} }

        # Record generated MP file count and output directory and flag generate completed or error
        self.generated_file_count = 0
        self.generate_directory_ok = False
        self.generate_directory = {} # name, (parent) directory, path, and timestamped (optional directory name)
        self.file_generate_complete = False
        self.file_generate_error = False

        # Record the results directory and flag generate completed or error
        self.results_directory = {} # name, (parent) directory, and path
        self.results_summary_generation_complete = False
        self.results_summary_generated = False
        self.results_summary_generation_error = False

        # Current directory locations
        self.current_figure_save_directory = ''

        # Flag when validation warnings are pending
        self.validation_warning_pending = False

        # Flag when warning produced by update call to validation method
        self.warning_shown_for_update_validation = False

        # Flag for forcing shifting focus when validation is triggered by option menus
        self.force_shift_focus = False

        # Flag warning messages so as to avoid calling additional validation checks triggered by focusout events
        self.currently_showing_warning_message = False

        # Set the current parameter LHS distribution viewed
        self.current_parameter_lhs_distribution_viewed = None

        # Entry field map for recovering field details from its pathname
        self.entry_field_map = {}

        # MP Generation Process steps
        self.process_step = {}
        self.process_step['mp_file_load'] = { 'number' : '1', 'dependents' : [], 'completed': False }
        self.process_step['sampling_settings'] = { 'number' : '2', 'dependents' : ['mp_file_load'], 'completed': False }
        self.process_step['parameter_settings'] = { 'number' : '3', 'dependents' : ['mp_file_load', 'sampling_settings'], 'completed': False }
        self.process_step['file_generation'] = { 'number' : '4', 'dependents' : ['mp_file_load', 'sampling_settings', 'parameter_settings'], 'completed': False }

        # MP Results Process steps
        self.results_process_step = {}
        self.results_process_step['results_directory'] = { 'number' : '1', 'dependents' : [], 'completed': False }
        self.results_process_step['results_selection'] = { 'number' : '2', 'dependents' : ['results_directory'], 'completed': False }
        self.results_process_step['results_summary_generation'] = { 'number' : '3', 'dependents' : ['results_directory', 'results_selection'], 'completed': False }

        # Process frames
        self.createMenu()

        # Configure the font for tool headings
        default_font = Font(font='TkDefaultFont')
        self.tool_label_font = Font(family=default_font.cget('family'), size=default_font.cget('size'), weight='bold')

        # MP Generation frames
        generation_tool_label = tk.Label(self, text='MP Sampling Generation', font=self.tool_label_font)
        self.mp_generation_frame = tk.LabelFrame(self, labelwidget=generation_tool_label, relief=tk.RAISED, padx=5, pady=5)
        self.createFileLoadFrame()
        self.createSamplingFrame()
        self.createParameterFrame()
        self.createGenerateFrame()
        self.mp_generation_frame.grid(row=0, column=0, padx=5, pady=5)

    # Menu GUI (will grow over time)
    def createMenu(self) :

        # Menu bar
        top = self.winfo_toplevel()
        self.menu_bar = tk.Menu(top, postcommand=self.shiftFocus)
        top['menu'] = self.menu_bar

        # File menu
        self.file_menu = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        # self.file_menu.add_command(label='Load MP File', command=self.loadMPFile)
        self.file_menu.add_command(label='Quit', command=self.quit)

        # Run menu
        self.run_menu = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(label='Run', menu=self.run_menu)        
        self.run_menu.add_command(label='RAMAS Metapop Batch', command=self.runBatch)
        self.run_menu.add_command(label='Results Summary', command=self.runResults)

        # Options menu
        self.options_menu = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(label='Options', menu=self.options_menu)
        self.options_menu.add_command(label='Edit', command=self.editOptions)

    # Ensures menu selection triggers entry field validation focusout events
    def shiftFocus(self, force_after=False) :
        self.focus_set()
        if force_after and self.validation_warning_pending :
            self.force_shift_focus = True
        
    # MP Generation: GUI for Step 1: Baseline MP File
    def createFileLoadFrame(self) :

        step_number = self.process_step['mp_file_load']['number']
        self.file_load_frame = tk.LabelFrame(self.mp_generation_frame, text='Step '+step_number+': Baseline MP File', padx=10, pady=10)

        # Create load button and labels and place them on a grid
        self.load_button = tk.Button(self.file_load_frame, text='Load MP File', command=self.loadMPFile)
        self.load_label_text = tk.StringVar(value=' : Select a baseline MP file to load')
        self.load_label = tk.Label(self.file_load_frame, textvariable=self.load_label_text)
        self.load_button.grid(row=0, column=0, sticky=tk.NW+tk.SW, padx=1)        
        self.load_label.grid(row=0, column=1, sticky=tk.NW+tk.SW)

        # Create a frame for displaying the MP file settings
        self.mp_file_settings_frame = tk.Frame(self.file_load_frame)
        self.mp_file_settings_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NW+tk.SW, padx=0, pady=5)

        self.file_load_frame.grid(row=0, column=0, sticky=tk.NW+tk.SE, padx=5, pady=5)

    # MP Generation: GUI for Step 2: Sampling
    def createSamplingFrame(self) :

        # Configure sample type selection
        self.sampling_types = ['Latin Hypercube', 'Random', 'Full Factorial']
        self.sampling_details = {}
        self.sampling_details['Latin Hypercube'] = { 'sample_number_required' : True, 'sample_number' : tk.StringVar() }
        self.sampling_details['Random'] = { 'sample_number_required' : True, 'sample_number' : tk.StringVar() }
        self.sampling_details['Full Factorial'] = { 'sample_number_required' : False }
        self.selected_sampling_type = tk.StringVar()
        self.sampling_type_radiobutton = {}
        self.sample_number_entry = {}

        step_number = self.process_step['sampling_settings']['number']
        sampling_frame = tk.LabelFrame(self.mp_generation_frame, text='Step '+step_number+': Sampling', padx=10, pady=10)

        # Register validation and selection behaviour methods
        validate_samples = sampling_frame.register(self.validateNumberOfSamples)

        sampling_row = 0

        for index, sample_type in enumerate(self.sampling_types) :

            # Create GUI elements and place them on a grid

            # Sampling type selection
            self.sampling_type_radiobutton[sample_type] = tk.Radiobutton(sampling_frame, text=None, variable=self.selected_sampling_type, value=sample_type, state=tk.DISABLED, command=self.updateSamplingType)
            self.sampling_type_radiobutton[sample_type].grid(row=sampling_row, column=0, sticky=tk.NW)
            tk.Label(sampling_frame, text=sample_type).grid(row=sampling_row, column=1, columnspan=2, sticky=tk.NW)

            # Select the first radio button and deselect others and any corresponding number of samples entries
            if index == 0 : 
                self.sampling_type_radiobutton[sample_type].select()
                self.current_sampling_type = sample_type
            else :
                self.sampling_type_radiobutton[sample_type].deselect()
            
            # Include number of samples when required
            if self.sampling_details[sample_type]['sample_number_required'] :

                tk.Label(sampling_frame, text=': Number of samples:').grid(row=sampling_row, column=3, sticky=tk.NW)
                self.sample_number_entry[sample_type] = tk.Entry(sampling_frame, textvariable=self.sampling_details[sample_type]['sample_number'], width=6, justify=tk.CENTER, state=tk.DISABLED, validate='all', validatecommand=(validate_samples, '%P', '%V', 'sampling', sample_type))
                self.entry_field_map[str(self.sample_number_entry[sample_type])] = { 'section' : 'sampling', 'field' : 'sample_number', 'sample_type' : sample_type }
                self.sample_number_entry[sample_type].grid(row=sampling_row, column=4, sticky=tk.NW)

                # Bind entry field to key release event
                self.sample_number_entry[sample_type].bind('<Any-KeyRelease>', self.__keyReleaseOnEntryField)

            sampling_row += 1

        sampling_frame.grid(row=1, column=0, sticky=tk.NW+tk.SE, padx=5, pady=0)

    # MP Generation: GUI for Step 3: Parameter Settings
    def createParameterFrame(self) :

        # Parameter selection variables
        self.modify_parameter = {}
        self.parameter_checkbox_bound = {}
        self.parameter_checkbox_lhs_settings = {}

        # Parameter baseline values
        self.parameter_baseline_values = {}
        self.parameter_baseline_values['value'] = {} # Selected single value as string
        self.parameter_baseline_values['matrix_value'] = {} # Selected single value as np float
        self.parameter_baseline_values['row'] = {} # Row index for selected
        self.parameter_baseline_values['column'] = {} # Column index for selected
        self.parameter_baseline_values['cell_width'] = {} # Cell widths
        self.parameter_baseline_values['highlight'] = {} # Flag highlighting

        # Parameter set via (% of baseline or selected value)
        self.parameter_set_via_text = {}
        self.parameter_set_via_selection_values = ['% of baseline', 'Selected value']
        self.parameter_bounds_set_via_selection_menu = {}
        self.parameter_lhs_settings_set_via_selection_menu = {}

        # Parameter bounds variables for random, and full factorial
        self.sample_bound_text = {}
        self.sample_bound_postfix_text = {}
        self.sample_bound_entry = {}
        self.sample_bound_selected_value_text = {}
        self.sample_bound_selected_value_entry = {}

        # Parameter settings variables for LHS
        self.lhs_distribution_selection_text = {}
        self.lhs_distribution_selection_menu = {}
        self.lhs_distribution_settings = {}
        self.lhs_current_displayed_distribution = {}
        self.lhs_setting_text = {}
        self.lhs_setting_previous_text = {}
        self.lhs_setting_postfix_text = {}
        self.lhs_setting_entry = {}
        self.lhs_setting_selected_value_text = {}
        self.lhs_setting_selected_value_previous_text = {}
        self.lhs_setting_selected_value_entry = {}
        self.lhs_view_distribution_button = {}

        # Parent parameter frame
        step_number = self.process_step['parameter_settings']['number']
        self.parameter_frame = tk.LabelFrame(self.mp_generation_frame, text='Step '+step_number+': Parameter Settings', padx=10, pady=10)

        # Child frames for dynamic parameter settings based on selected sampling method
        self.parameter_bounds_frame = tk.Frame(self.parameter_frame)
        self.parameter_lhs_settings_frame = tk.Frame(self.parameter_frame)

        # Child frames and their v (expand) and x (contract) buttons for baseline values
        self.parameter_bounds_baseline_v_frame = {} # single value
        self.parameter_bounds_baseline_v_button = {}
        self.parameter_bounds_baseline_x_frame = {} # expanded
        self.parameter_bounds_baseline_x_button = {}
        self.parameter_bounds_baseline_x_label = {}
        self.parameter_lhs_settings_baseline_v_frame = {}
        self.parameter_lhs_settings_baseline_v_button = {}
        self.parameter_lhs_settings_baseline_x_frame = {}
        self.parameter_lhs_settings_baseline_x_button = {}
        self.parameter_lhs_settings_baseline_x_label  = {}
        # x frame contents frames
        self.bounds_baseline_values_outer_frame = {}
        self.bounds_baseline_values_inner_frame = {}
        self.lhs_settings_baseline_values_outer_frame = {}
        self.lhs_settings_baseline_values_inner_frame = {}

        # Register parameter selection commands
        parameter_bounds_selection = self.parameter_bounds_frame.register(self.parameterBoundsSelection)
        parameter_lhs_settings_selection = self.parameter_lhs_settings_frame.register(self.parameterLHSSettingsSelection)
        parameter_lhs_distribution_selection = self.parameter_lhs_settings_frame.register(self.parameterLHSDistributionSelection)
        parameter_set_via_selection = self.parameter_frame.register(self.parameterSetViaSelection)
        forced_shift_focus = self.parameter_frame.register(self.shiftFocus)

        # Register baseline parameter update view command
        update_baseline_parameter_view = self.parameter_frame.register(self.updateBaselineParameterView)

        # Register LHS distribution view command
        view_lhs_distribution = self.parameter_frame.register(self.viewLhsDistribution)

        # Register validation commands
        validate_bounds = self.parameter_bounds_frame.register(self.validateParameterBounds)
        validate_lhs_settings = self.parameter_lhs_settings_frame.register(self.validateParameterLHSSettings)
        validate_bounds_selected_value = self.parameter_bounds_frame.register(self.validateParameterBoundsSelectedValue)
        validate_lhs_settings_selected_value = self.parameter_lhs_settings_frame.register(self.validateParameterLHSSettingsSelectedValue)
        validate_lhs_settings_via_spinbox = self.parameter_lhs_settings_frame.register(self.validateParameterLHSSettingsViaSpinbox)

        # Parameter setting headings
        tk.Label(self.parameter_bounds_frame, text='Select parameters to modify').grid(row=0, column=0, columnspan=2, sticky=tk.W)
        tk.Label(self.parameter_bounds_frame, text='Loaded values').grid(row=0, column=2, sticky=tk.W, padx=2)
        tk.Label(self.parameter_bounds_frame, text='Set via').grid(row=0, column=3, sticky=tk.W, padx=5)
        tk.Label(self.parameter_bounds_frame, text='Sample bounds').grid(row=0, column=4, sticky=tk.W, padx=5)
        tk.Label(self.parameter_lhs_settings_frame, text='Select parameters to modify').grid(row=0, column=0, columnspan=2, sticky=tk.W)
        tk.Label(self.parameter_lhs_settings_frame, text='Loaded values').grid(row=0, column=2, sticky=tk.W, padx=2)
        tk.Label(self.parameter_lhs_settings_frame, text='Select distribution').grid(row=0, column=3, sticky=tk.W, padx=5)
        tk.Label(self.parameter_lhs_settings_frame, text='Set via').grid(row=0, column=4, sticky=tk.W, padx=5)
        tk.Label(self.parameter_lhs_settings_frame, text='  Distribution settings').grid(row=0, column=5, columnspan=12, sticky=tk.W)
        
        for index, key in enumerate(self.config.parameters) :

            # Value storage
            self.parameter_baseline_values['value'][key] = tk.StringVar(value='   ')
            self.parameter_baseline_values['row'][key] = 0
            self.parameter_baseline_values['column'][key] = 0
            self.parameter_baseline_values['highlight'][key] = True
            self.modify_parameter[key] = tk.IntVar(value=0)
            self.parameter_set_via_text[key] = tk.StringVar(value=self.parameter_set_via_selection_values[0])
            self.sample_bound_text[key] = tk.StringVar()
            self.sample_bound_postfix_text[key] = tk.StringVar(value='%')
            self.sample_bound_selected_value_text[key] = tk.StringVar()
            self.lhs_distribution_selection_text[key] = tk.StringVar()
            self.lhs_setting_text[key] = {}
            self.lhs_setting_previous_text[key] = {}
            self.lhs_setting_postfix_text[key] = {}
            self.lhs_setting_selected_value_text[key] = {}
            self.lhs_setting_selected_value_previous_text[key] = {}
            for distr in self.config.lhs_distributions :
                self.lhs_setting_text[key][distr] = {}
                self.lhs_setting_previous_text[key][distr] = {}
                self.lhs_setting_postfix_text[key][distr] = {}
                self.lhs_setting_selected_value_text[key][distr] = {}
                self.lhs_setting_selected_value_previous_text[key][distr] = {}
                for distr_setting in self.config.lhs_distribution_settings[distr] :
                    self.lhs_setting_text[key][distr][distr_setting['name']] = tk.StringVar()
                    self.lhs_setting_previous_text[key][distr][distr_setting['name']] = ''
                    self.lhs_setting_postfix_text[key][distr][distr_setting['name']] = tk.StringVar(value=distr_setting['postfix'])
                    self.lhs_setting_selected_value_text[key][distr][distr_setting['name']] = tk.StringVar()
                    self.lhs_setting_selected_value_previous_text[key][distr][distr_setting['name']] = ''

            # Create GUI elements and place them on the grid for the appropriate frame

            # Parameter bounds frame (dynamic)

            # Parameter selection
            self.parameter_checkbox_bound[key] = tk.Checkbutton(self.parameter_bounds_frame, variable=self.modify_parameter[key], state=tk.DISABLED, command=(parameter_bounds_selection, key))
            self.parameter_checkbox_bound[key].grid(row=index+1, column=0, sticky=tk.NW)
            tk.Label(self.parameter_bounds_frame, text=key).grid(row=index+1, column=1, sticky=tk.NW)

            # Baseline values
            self.parameter_bounds_baseline_v_frame[key] = tk.Frame(self.parameter_bounds_frame, relief=tk.SUNKEN, bd=2)
            self.parameter_bounds_baseline_x_frame[key] = tk.Frame(self.parameter_bounds_frame, relief=tk.SUNKEN, bd=2)
            self.parameter_bounds_baseline_v_button[key] = tk.Button(self.parameter_bounds_baseline_v_frame[key], state=tk.DISABLED, text='v', command=(update_baseline_parameter_view, 'bounds', 'v', key))
            self.parameter_bounds_baseline_x_button[key] = tk.Button(self.parameter_bounds_baseline_x_frame[key], state=tk.NORMAL, text='x', command=(update_baseline_parameter_view, 'bounds', 'x', key))
            self.parameter_bounds_baseline_x_button[key].grid(row=0, column=1, sticky=tk.NE)
            self.parameter_bounds_baseline_x_frame[key].grid(row=index+1, column=2, sticky=tk.W, padx=5)
            self.parameter_bounds_baseline_x_frame[key].grid_remove()
            self.parameter_bounds_baseline_x_label[key] = tk.Label(self.parameter_bounds_baseline_v_frame[key], textvariable=self.parameter_baseline_values['value'][key], relief=tk.GROOVE, bd=2, width=3)
            self.parameter_bounds_baseline_x_label[key].grid(row=0, column=0)
            self.parameter_bounds_baseline_v_button[key].grid(row=0, column=1, sticky=tk.NE)
            self.parameter_bounds_baseline_v_frame[key].grid(row=index+1, column=2, sticky=tk.W, padx=5)

            # Parameter set via selection
            self.parameter_bounds_set_via_selection_menu[key] = tk.OptionMenu(self.parameter_bounds_frame, self.parameter_set_via_text[key], *self.parameter_set_via_selection_values)
            self.parameter_bounds_set_via_selection_menu[key].config(state=tk.DISABLED, highlightthickness=0)
            self.parameter_bounds_set_via_selection_menu[key]['menu'].config(postcommand=(forced_shift_focus, True))
            for set_via_index, set_via_value in enumerate(self.parameter_set_via_selection_values) :
                self.parameter_bounds_set_via_selection_menu[key]['menu'].entryconfigure(set_via_index, command=(parameter_set_via_selection, key, set_via_value))
            self.parameter_bounds_set_via_selection_menu[key].grid(row=index+1, column=3, sticky=tk.NW, padx=8)

            # Sample bound entry
            sample_bound_frame = tk.Frame(self.parameter_bounds_frame) # child frame for widget spacing
            self.sample_bound_entry[key] = tk.Entry(sample_bound_frame, textvariable=self.sample_bound_text[key], width=6, justify=tk.CENTER, state=tk.DISABLED, validate='all', validatecommand=(validate_bounds, '%P', '%V', key))
            self.sample_bound_selected_value_entry[key] = tk.Entry(sample_bound_frame, textvariable=self.sample_bound_selected_value_text[key], width=6, justify=tk.CENTER, state=tk.DISABLED, validate='all', validatecommand=(validate_bounds_selected_value, '%P', '%V', key))
            self.entry_field_map[str(self.sample_bound_entry[key])] = { 'section' : 'parameter_settings', 'context' : 'bounds', 'field' : 'sample_bound', 'parameter_key' : key }
            self.entry_field_map[str(self.sample_bound_selected_value_entry[key])] = { 'section' : 'parameter_settings', 'context' : 'bounds', 'field' : 'sample_bound_selected_value', 'parameter_key' : key }
            tk.Label(sample_bound_frame, text=u'\u00B1').grid(row=0, column=0, sticky=tk.NW, pady=2)
            self.sample_bound_selected_value_entry[key].grid(row=0, column=1, sticky=tk.NW, pady=2)
            self.sample_bound_selected_value_entry[key].grid_remove()
            self.sample_bound_entry[key].grid(row=0, column=1, sticky=tk.NW, pady=2)
            tk.Label(sample_bound_frame, textvariable=self.sample_bound_postfix_text[key]).grid(row=0, column=2, sticky=tk.NW)
            sample_bound_frame.grid(row=index+1, column=4, sticky=tk.NW, padx=5, pady=2)

            # Parameter LHS Settings frame (dynamic)

            # Parameter selection
            self.parameter_checkbox_lhs_settings[key] = tk.Checkbutton(self.parameter_lhs_settings_frame, variable=self.modify_parameter[key], state=tk.DISABLED, command=(parameter_lhs_settings_selection, key))
            self.parameter_checkbox_lhs_settings[key].grid(row=index+1, column=0, sticky=tk.NW)
            tk.Label(self.parameter_lhs_settings_frame, text=key).grid(row=index+1, column=1, sticky=tk.NW)

            # Child frames for baseline values
            self.parameter_lhs_settings_baseline_v_frame[key] = tk.Frame(self.parameter_lhs_settings_frame, relief=tk.SUNKEN, bd=2)
            self.parameter_lhs_settings_baseline_x_frame[key] = tk.Frame(self.parameter_lhs_settings_frame, relief=tk.SUNKEN, bd=2)
            self.parameter_lhs_settings_baseline_v_button[key] = tk.Button(self.parameter_lhs_settings_baseline_v_frame[key], state=tk.DISABLED, text='v', command=(update_baseline_parameter_view, 'lhs_settings', 'v', key))
            self.parameter_lhs_settings_baseline_x_button[key] = tk.Button(self.parameter_lhs_settings_baseline_x_frame[key], state=tk.NORMAL, text='x', command=(update_baseline_parameter_view, 'lhs_settings', 'x', key))
            self.parameter_lhs_settings_baseline_x_button[key].grid(row=0, column=1, sticky=tk.NE)
            self.parameter_lhs_settings_baseline_x_frame[key].grid(row=index+1, column=2, sticky=tk.W, padx=5)
            self.parameter_lhs_settings_baseline_x_frame[key].grid_remove()
            self.parameter_lhs_settings_baseline_x_label[key] = tk.Label(self.parameter_lhs_settings_baseline_v_frame[key], textvariable=self.parameter_baseline_values['value'][key], relief=tk.GROOVE, bd=2, width=3)
            self.parameter_lhs_settings_baseline_x_label[key].grid(row=0, column=0)
            self.parameter_lhs_settings_baseline_v_button[key].grid(row=0, column=1, sticky=tk.NE)
            self.parameter_lhs_settings_baseline_v_frame[key].grid(row=index+1, column=2, sticky=tk.W, padx=5)

            # Distribution selection
            self.lhs_distribution_selection_text[key].set(self.config.lhs_distributions[0])
            self.lhs_current_displayed_distribution[key] = self.config.lhs_distributions[0]
            self.lhs_distribution_selection_menu[key] = tk.OptionMenu(self.parameter_lhs_settings_frame, self.lhs_distribution_selection_text[key], *self.config.lhs_distributions)
            self.lhs_distribution_selection_menu[key].config(state=tk.DISABLED, highlightthickness=0)
            self.lhs_distribution_selection_menu[key]['menu'].config(postcommand=(forced_shift_focus, True))
            for distr_index, distr in enumerate(self.config.lhs_distributions) :
                self.lhs_distribution_selection_menu[key]['menu'].entryconfigure(distr_index, command=(parameter_lhs_distribution_selection, key, distr))
                if not (distr in self.config.parameter_includes_lhs_distributions[key]) :
                    self.lhs_distribution_selection_menu[key]['menu'].entryconfigure(distr_index, state=tk.DISABLED)
            self.lhs_distribution_selection_menu[key].grid(row=index+1, column=3, sticky=tk.NW, padx=8)

            # Parameter set via selection
            self.parameter_lhs_settings_set_via_selection_menu[key] = tk.OptionMenu(self.parameter_lhs_settings_frame, self.parameter_set_via_text[key], *self.parameter_set_via_selection_values)
            self.parameter_lhs_settings_set_via_selection_menu[key].config(state=tk.DISABLED, highlightthickness=0)
            self.parameter_lhs_settings_set_via_selection_menu[key]['menu'].config(postcommand=(forced_shift_focus, True))
            for set_via_index, set_via_value in enumerate(self.parameter_set_via_selection_values) :
                self.parameter_lhs_settings_set_via_selection_menu[key]['menu'].entryconfigure(set_via_index, command=(parameter_set_via_selection, key, set_via_value))
            self.parameter_lhs_settings_set_via_selection_menu[key].grid(row=index+1, column=4, sticky=tk.NW, padx=8)

            # Distribution settings
            self.lhs_distribution_settings[key] = {}
            self.lhs_setting_entry[key] = {}
            self.lhs_setting_selected_value_entry[key] = {}
            self.lhs_view_distribution_button[key] = {}
            for distr_index, distr in enumerate(self.config.lhs_distributions) :
                column_index = 5
                self.lhs_distribution_settings[key][distr] = []
                self.lhs_setting_entry[key][distr] = {}
                self.lhs_setting_selected_value_entry[key][distr] = {}
                for distr_setting in self.config.lhs_distribution_settings[distr] :

                    # Create setting elements
                    setting_label = tk.Label(self.parameter_lhs_settings_frame, text=('  ' + distr_setting['name']))
                    if self.config.lhs_option_default_settings[distr].has_key(distr_setting['name']+' Increment') :
                        self.lhs_setting_entry[key][distr][distr_setting['name']] = tk.Spinbox(self.parameter_lhs_settings_frame, textvariable=self.lhs_setting_text[key][distr][distr_setting['name']], width=5, justify=tk.CENTER, state=tk.DISABLED, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', key, distr, distr_setting['name']), command=(validate_lhs_settings_via_spinbox, key, distr, distr_setting['name'], 'lhs_setting_entry'))
                        self.lhs_setting_selected_value_entry[key][distr][distr_setting['name']] = tk.Spinbox(self.parameter_lhs_settings_frame, textvariable=self.lhs_setting_selected_value_text[key][distr][distr_setting['name']], width=5, justify=tk.CENTER, state=tk.DISABLED, validate='all', validatecommand=(validate_lhs_settings_selected_value, '%P', '%V', key, distr, distr_setting['name']), command=(validate_lhs_settings_via_spinbox, key, distr, distr_setting['name'], 'lhs_setting_selected_value_entry'))
                    else :
                        self.lhs_setting_entry[key][distr][distr_setting['name']] = tk.Entry(self.parameter_lhs_settings_frame, textvariable=self.lhs_setting_text[key][distr][distr_setting['name']], width=6, justify=tk.CENTER, state=tk.DISABLED, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', key, distr, distr_setting['name']))
                        self.lhs_setting_selected_value_entry[key][distr][distr_setting['name']] = tk.Entry(self.parameter_lhs_settings_frame, textvariable=self.lhs_setting_selected_value_text[key][distr][distr_setting['name']], width=6, justify=tk.CENTER, state=tk.DISABLED, validate='all', validatecommand=(validate_lhs_settings_selected_value, '%P', '%V', key, distr, distr_setting['name']))
                    self.entry_field_map[str(self.lhs_setting_entry[key][distr][distr_setting['name']])] = { 'section' : 'parameter_settings', 'context' : 'lhs_settings', 'field' : 'lhs_setting', 'parameter_key' : key, 'distribution' : distr, 'distr_setting' : distr_setting['name'] }
                    self.entry_field_map[str(self.lhs_setting_selected_value_entry[key][distr][distr_setting['name']])] = { 'section' : 'parameter_settings', 'context' : 'lhs_settings', 'field' : 'lhs_setting_selected_value', 'parameter_key' : key, 'distribution' : distr, 'distr_setting' : distr_setting['name'] }
                    setting_postfix = tk.Label(self.parameter_lhs_settings_frame, textvariable=self.lhs_setting_postfix_text[key][distr][distr_setting['name']])
                    self.lhs_distribution_settings[key][distr].append({ 'element' : setting_label })
                    self.lhs_distribution_settings[key][distr].append({ 'element' : self.lhs_setting_entry[key][distr][distr_setting['name']],
                                                                        'selected_value_element' : self.lhs_setting_selected_value_entry[key][distr][distr_setting['name']] })
                    self.lhs_distribution_settings[key][distr].append({ 'element' : setting_postfix })

                    # Add them to the grid
                    setting_label.grid(row=index+1, column=column_index, sticky=tk.NW, pady=2)
                    self.lhs_setting_entry[key][distr][distr_setting['name']].grid(row=index+1, column=column_index+1, sticky=tk.NW, pady=2)
                    self.lhs_setting_selected_value_entry[key][distr][distr_setting['name']].grid(row=index+1, column=column_index+1, sticky=tk.NW, pady=2)
                    setting_postfix.grid(row=index+1, column=column_index+2, sticky=tk.NW, padx=0, pady=2)

                    # Remove all but first (remembers grid settings for when they are swapped via method: parameterLHSDistributionSelection)
                    if distr_index != 0 :
                        setting_label.grid_remove()
                        self.lhs_setting_entry[key][distr][distr_setting['name']].grid_remove()
                        setting_postfix.grid_remove()
                    self.lhs_setting_selected_value_entry[key][distr][distr_setting['name']].grid_remove()
                        
                    column_index += 3

                # Add view distribution button
                self.lhs_view_distribution_button[key][distr] = tk.Button(self.parameter_lhs_settings_frame, state=tk.DISABLED, text='View', command=(view_lhs_distribution, key, distr))
                self.lhs_view_distribution_button[key][distr].grid(row=index+1, column=column_index, sticky=tk.NW, padx=8, pady=2)
                if distr_index != 0 :
                    self.lhs_view_distribution_button[key][distr].grid_remove()

            # Bind entry fields to key release events (for workflow updates)
            self.sample_bound_entry[key].bind('<Any-KeyRelease>', self.__keyReleaseOnEntryField)
            self.sample_bound_selected_value_entry[key].bind('<Any-KeyRelease>', self.__keyReleaseOnEntryField)
            for distr in self.config.lhs_distributions :
                for distr_setting in self.config.lhs_distribution_settings[distr] :
                    self.lhs_setting_entry[key][distr][distr_setting['name']].bind('<Any-KeyRelease>', self.__keyReleaseOnEntryField)
                    self.lhs_setting_selected_value_entry[key][distr][distr_setting['name']].bind('<Any-KeyRelease>', self.__keyReleaseOnEntryField)

        # Place frames on the grid of their parent
        self.parameter_lhs_settings_frame.grid(row=0, column=0)
        self.parameter_frame.grid(row=0, rowspan=3, column=1, sticky=tk.NW+tk.SE, padx=5, pady=5)

    # MP Generation: GUI for Step 4: Sampling File Generation
    def createGenerateFrame(self) :

        step_number = self.process_step['file_generation']['number']
        generate_frame = tk.LabelFrame(self.mp_generation_frame, text='Step '+step_number+': Sampling File Generation', padx=5, pady=10)

        # Register generic focus method
        focus_on_field = generate_frame.register(self.focusOnField)

        # Get current config tool options
        tool_option_values = self.config.getToolOptions()

        # Set MP settings
        self.generate_metapop_iterations = tk.StringVar(value='_')
        self.generate_metapop_duration = tk.StringVar(value='_')
        settings_uses = 'baseline settings:'
        if not tool_option_values['use_mp_baseline_values'] :
            settings_uses = 'option settings:'
            if tool_option_values['number_of_metapop_iterations'] :
                self.generate_metapop_iterations.set(tool_option_values['number_of_metapop_iterations'])
            if tool_option_values['metapop_simulation_duration'] :
                self.generate_metapop_duration.set(tool_option_values['metapop_simulation_duration'])

        # Display MP settings
        mp_settings_frame = tk.Frame(generate_frame)
        self.generate_settings_uses_text = tk.StringVar(value='MP generation uses '+settings_uses)
        self.generate_metapop_iterations_label = tk.Label(mp_settings_frame, textvariable=self.generate_metapop_iterations)
        self.generate_metapop_duration_label = tk.Label(mp_settings_frame, textvariable=self.generate_metapop_duration)
        self.generate_use_mp_baseline_values = tk.IntVar(value=int(tool_option_values['use_mp_baseline_values']))
        self.generate_use_mp_baseline_values_checkbox = tk.Checkbutton(mp_settings_frame, variable=self.generate_use_mp_baseline_values, text='Use values from baseline MP file', state=tk.DISABLED, command=self.updateGenerationSettings)
        tk.Label(mp_settings_frame, textvariable=self.generate_settings_uses_text).grid(row=0, column=0, columnspan=3, sticky=tk.NW+tk.SW, padx=0, pady=0)
        tk.Label(mp_settings_frame, text='').grid(row=1, column=0, padx=3, pady=0)
        tk.Label(mp_settings_frame, text='Iterations per scenario (replications):').grid(row=1, column=1, sticky=tk.NW+tk.SW, padx=4, pady=0)
        self.generate_metapop_iterations_label.grid(row=1, column=2, sticky=tk.NW+tk.SW, padx=0, pady=0)
        tk.Label(mp_settings_frame, text='').grid(row=2, column=0, padx=3, pady=0)
        tk.Label(mp_settings_frame, text='Simulation duration:').grid(row=2, column=1, sticky=tk.NW+tk.SW, padx=4, pady=0)
        self.generate_metapop_duration_label.grid(row=2, column=2, sticky=tk.NW+tk.SW, padx=0, pady=0)
        tk.Label(mp_settings_frame, text='').grid(row=3, column=0, padx=3, pady=0)
        self.generate_use_mp_baseline_values_checkbox.grid(row=3, column=1, columnspan=2, sticky=tk.NW+tk.SW, padx=1, pady=1)
        mp_settings_frame.grid(row=0, column=0, sticky=tk.NW+tk.SW, padx=3)

        # Auto run results summary
        if path.exists(tool_option_values['metapop_exe_location']) :
            auto_run_results_summary_value = tool_option_values['auto_run_results_summary_tool']
        else :
            auto_run_results_summary_value = False
        self.auto_run_results_summary = tk.IntVar(value=int(auto_run_results_summary_value))
        self.auto_run_results_summary_checkbox = tk.Checkbutton(generate_frame, variable=self.auto_run_results_summary, text='Automatically run batch and results summary', state=tk.DISABLED, command=self.autorunResultsSummarySelected)
        self.auto_run_results_summary_checkbox.grid(row=1, column=0, columnspan=3, sticky=tk.NW+tk.SW, padx=2, pady=0)

        # Register directory selection method
        select_file_generation_directory = generate_frame.register(self.selectFileGenerationDirectory)

        # Create generate buttons and workflow label and place them on a grid
        generate_buttons_frame = tk.Frame(generate_frame)
        location_descr = ' : Select location for generated files'
        if tool_option_values['default_generated_file_location'] and path.exists(tool_option_values['default_generated_file_location']) :
            self.generate_directory = self.mp_file_helper.splitPath(tool_option_values['default_generated_file_location'])
            self.generate_directory_ok = True
            location_descr = ' : File generation in \"' + self.generate_directory['name'] + '\"'
        self.generate_directory_descr = tk.StringVar(value=location_descr)
        self.generate_directory_button = tk.Button(generate_buttons_frame, text='Select Directory', state=tk.DISABLED, command=(select_file_generation_directory, 'generate'))
        self.generate_directory_label = tk.Label(generate_buttons_frame, textvariable=self.generate_directory_descr, justify=tk.LEFT)
        self.generate_button = tk.Button(generate_buttons_frame, text='Generate Files', state=tk.DISABLED, command=self.generateFiles)
        steps_to_be_completed = self.dependentStepsToBeCompleted('file_generation')
        self.generate_label_text = tk.StringVar(value=' : Complete steps '+string.join(steps_to_be_completed, ', '))
        self.generate_label = tk.Label(generate_buttons_frame, textvariable=self.generate_label_text)
        self.generate_directory_button.grid(row=0, column=0, sticky=tk.NW+tk.SE, pady=5)
        self.generate_directory_label.grid(row=0, column=1, sticky=tk.NW+tk.SW)
        self.generate_button.grid(row=1, column=0, sticky=tk.NW+tk.SE, pady=5)
        self.generate_label.grid(row=1, column=1, sticky=tk.NW+tk.SW)
        generate_buttons_frame.grid(row=2, column=0, sticky=tk.NW+tk.SW, padx=6)

        # Warn if metapop exe not found locally
        metapop_exe_warning_message = ( 'Warning: RAMAS Metapop program file (exe) not found.\n' +
                                        'The generated batch file will not run on this machine.\n' +
                                        'Adjust via the options menu if required.' )
        self.metapop_exe_warning_label = tk.Label(generate_frame, text=metapop_exe_warning_message, justify=tk.LEFT)
        if not path.exists(tool_option_values['metapop_exe_location']) :
            self.metapop_exe_warning_label.grid(row=3, column=0, sticky=tk.NW+tk.SW, padx=3, pady=0)

        # Notify if duration altered and temporal trends utilised
        duration_when_temporal_trends_message = ('Note: The number of entries in the temporal trend files\n' +
                                                 'may differ from the altered simulation duration.')
        self.duration_when_temporal_trends_label = tk.Label(generate_frame, text=duration_when_temporal_trends_message, justify=tk.LEFT)
        if self.durationAlteredWithTemporalTrends() :
            self.duration_when_temporal_trends_label.grid(row=4, column=0, sticky=tk.NW+tk.SW, padx=3, pady=0)

        generate_frame.grid(row=2, column=0, sticky=tk.NW+tk.SE, padx=5, pady=5)

    # MP Results: Create options window
    def createResultsWindow(self) :

        # Create the results window
        self.results_window = tk.Toplevel(self)
        self.results_window.title(application_name + ' Results Summary')
        self.results_window.transient(self)
        self.results_window.focus_set()

        # MP Results frames
        results_tool_label = tk.Label(self.results_window, text='MP Results Summary Generation', font=self.tool_label_font)
        self.mp_results_frame = tk.LabelFrame(self.results_window, labelwidget=results_tool_label, text='', relief=tk.RAISED, padx=5, pady=5)
        self.createResultsDirectoryFrame()
        self.createResultsSelectionFrame()
        self.createResultsSummaryFrame()
        self.mp_results_frame.grid(row=0, column=0, padx=5, pady=5)

        # Close button
        results_actions_frame = tk.Frame(self.results_window)
        close_results_button = tk.Button(results_actions_frame, text='Close', command=self.results_window.destroy)
        close_results_button.grid(row=0, column=0, sticky=tk.NW+tk.SE, padx=0, pady=0)
        results_actions_frame.grid(row=1, column=0, sticky=tk.NW+tk.SE, padx=5, pady=0)
        tk.Frame(self.results_window).grid(row=2, column=0, sticky=tk.NW+tk.SE, padx=0, pady=1)

    # MP Results: GUI for Step 1: Load Results
    def createResultsDirectoryFrame(self) :

        step_number = self.results_process_step['results_directory']['number']
        results_directory_frame = tk.LabelFrame(self.mp_results_frame, text='Step '+step_number+': Load Results', padx=10, pady=10)

        # Create load button and status frame and place them on a grid

        # Load button
        self.results_directory_button = tk.Button(results_directory_frame, text='Load Directory', command=self.loadResultsDirectory)
        self.results_directory_button.grid(row=0, column=0)

        # Status frame (future: may include run batch button for when results are absent)
        self.results_directory_label_text = tk.StringVar(value=' : Select the directory containing the MP results')
        self.results_directory_status_frame = tk.Frame(results_directory_frame)
        tk.Label(self.results_directory_status_frame, textvariable=self.results_directory_label_text).grid(row=0, column=0, sticky=tk.NW)
        self.results_directory_status_frame.grid(row=0, column=1, sticky=tk.NW)        

        results_directory_frame.grid(row=0, column=0, sticky=tk.NW+tk.SE, padx=5, pady=5)

    # MP Results: GUI for Step 2: Results Selection
    def createResultsSelectionFrame(self) :

        step_number = self.results_process_step['results_selection']['number']
        results_selection_frame = tk.LabelFrame(self.mp_results_frame, text='Step '+step_number+': Select Results', padx=10, pady=10)

        # Results selection variables
        self.result_selected = {}
        self.results_selection_checkbox = {}

        # Register results selection command
        results_selection_command = results_selection_frame.register(self.resultsSelection)

        # Result selection via checkboxes
        for index, result in enumerate(self.config.metapop_results) :

            # Value storage
            self.result_selected[result] = tk.IntVar(value=0)

            # Checkbox and label for result
            self.results_selection_checkbox[result] = tk.Checkbutton(results_selection_frame, variable=self.result_selected[result], state=tk.DISABLED, command=(results_selection_command, result))
            self.results_selection_checkbox[result].grid(row=index+1, column=0)
            tk.Label(results_selection_frame, text=result).grid(row=index+1, column=1, sticky=tk.W)

        results_selection_frame.grid(row=1, column=0, sticky=tk.NW+tk.SE, padx=5, pady=0)

    # MP Results: GUI for Step 3: Results Summary
    def createResultsSummaryFrame(self) :

        step_number = self.results_process_step['results_summary_generation']['number']
        results_summary_frame = tk.LabelFrame(self.mp_results_frame, text='Step '+step_number+': Generate Results Summary', padx=10, pady=10)

        # Create generate summary button and workflow label and place them on a grid
        self.results_summary_button = tk.Button(results_summary_frame, text='Generate Summary', command=self.generateResultsSummary, state=tk.DISABLED)
        steps_to_be_completed = self.dependentStepsToBeCompleted('results_summary_generation', self.results_process_step)
        self.results_summary_label_text = tk.StringVar(value='Complete steps '+string.join(steps_to_be_completed, ', '))
        self.results_summary_label = tk.Label(results_summary_frame, textvariable=self.results_summary_label_text)
        self.results_summary_button.grid(row=0, column=0, sticky=tk.W)
        tk.Label(results_summary_frame, text=' :').grid(row=0, column=1)
        self.results_summary_label.grid(row=0, column=2, columnspan=2, sticky=tk.W)

        # Register selection behaviour methods
        select_result_plot = results_summary_frame.register(self.resultsPlotSelection)

        # Create the view plot button and selection
        self.results_plot_label = tk.Label(results_summary_frame, text='Plots Generated:')
        self.results_plot_text = tk.StringVar()
        self.results_plot_text.set(self.config.metapop_result_plots[0])
        self.results_plot_view_button = tk.Button(results_summary_frame, text='View', command=self.generateResultsPlot)
        self.results_plot_menu = tk.OptionMenu(results_summary_frame, self.results_plot_text, *self.config.metapop_result_plots)
        self.results_plot_menu.config(highlightthickness=0, anchor=tk.W)
        for i, selection in enumerate(self.config.metapop_result_plots) :
            self.results_plot_menu['menu'].entryconfigure(i, command=(select_result_plot, selection))
        self.results_plot_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        self.results_plot_menu.grid(row=1, column=2, sticky=tk.W)
        self.results_plot_view_button.grid(row=1, column=3, sticky=tk.W, padx=5)
        results_summary_frame.columnconfigure(2, weight=1)
        results_summary_frame.columnconfigure(3, weight=1000)
        self.showResultsAvailablePlots(False)

        results_summary_frame.grid(row=2, column=0, sticky=tk.NW+tk.SE, padx=5, pady=5)

    # Menu Method: Changing Sensitivity Analysis Tool
    def changeTool(self, tool) :
        
        # Hide the root frame child if it exists
        if self.grid_slaves() :
            self.grid_slaves().pop().grid_forget()

        # Populate the root frame with appropriate contents
        if tool == 'mp_generation' :
            self.mp_generation_frame.grid(row=0, column=0, padx=5, pady=5)
        elif tool == 'mp_results' :
            self.mp_results_frame.grid(row=0, column=0, padx=5, pady=5)

    # Menu Method: Run RAMAS Metapop batch
    def runBatch(self, batch_file_path=None) :

        # Find batch file if not given (correctly)
        if not (batch_file_path and path.exists(batch_file_path)) :

            # Use default generation directory if it exists
            initial_directory = getcwd()
            tool_option_values = self.config.getToolOptions()
            if self.generate_directory.has_key('path') :
                initial_directory = self.generate_directory['path']
            elif tool_option_values['default_generated_file_location'] and path.exists(tool_option_values['default_generated_file_location']) :
                initial_directory = tool_option_values['default_generated_file_location']
            elif path.exists(environ['USERPROFILE']) :
                initial_directory = environ['USERPROFILE']
            
            # Open file selection dialog
            batch_file_path = askopenfilename(title='Select the RAMAS Metapop batch file to run', filetypes=[('Batch Files', '*.bat'), ('All Files', '*.*')], initialdir=initial_directory)

        # Run batch file
        if batch_file_path and path.exists(batch_file_path) :
            try :
                self.after_idle(lambda: chdir(self.mp_file_helper.splitPath(batch_file_path)['directory']))
                self.after_idle(lambda: call(batch_file_path))
            except Exception, e :
                showerror('Batch Run Error', 'Could not run batch file: '+batch_file_path+'.\n'+str(e))
                print >> sys.stderr, 'Error running batch file', batch_file_path, ':', e

    # Menu Method: Run results summary
    def runResults(self) :
        if hasattr(self, 'results_window') :
            if self.results_window.children :
                self.results_window.focus_set()
            else :
                self.results_window.destroy()
                self.createResultsWindow()
        else :
            self.createResultsWindow()

    # Menu Method: Edit options
    def editOptions(self) :

        if hasattr(self, 'options_window') :
            if self.options_window.children :
                self.options_window.focus_set()
            else :
                self.options_window.destroy()
                self.createOptionsWindow()
        else :
            self.createOptionsWindow()

    # Menu Method: Create options window
    def createOptionsWindow(self) :

        # Create the options window
        self.options_window = tk.Toplevel(self)
        self.options_window.title(application_name + ' Options')
        self.options_window.transient(self)
        self.options_window.focus_set()

        # Get current config tool options
        tool_option_values = self.config.getToolOptions()

        # If batch is run locally and current Metapop exe location doesn't exist try to find it
        if tool_option_values['run_metapop_batch_locally'] and not path.exists(tool_option_values['metapop_exe_location']) :
            metapop_exe_path = environ['PROGRAMFILES']
            metapop_exe_path = path.join(metapop_exe_path, self.findMatchingInDirectory(metapop_exe_path, 'RAMASGIS'))
            metapop_exe_path = path.join(metapop_exe_path, self.findMatchingInDirectory(metapop_exe_path, 'Metapop.exe'))
            if self.mp_file_helper.splitPath(metapop_exe_path)['name'].lower().find('metapop.exe') != -1 :
                tool_option_values['metapop_exe_location'] = metapop_exe_path

        # If current default generated file location doesn't exist then clear it
        if not path.exists(tool_option_values['default_generated_file_location']) :
            tool_option_values['default_generated_file_location'] = ''

        # Create the General File Options frame

        file_options_frame = tk.LabelFrame(self.options_window, text='General File Options', padx=5, pady=5)

        # Metapop program file (exe) location
        self.metapop_exe_location = tk.StringVar(value=tool_option_values['metapop_exe_location'])
        self.metapop_exe_location_button = tk.Button(file_options_frame, text='Select Exe File', command=self.selectExeFile)
        self.metapop_exe_location_label = tk.Label(file_options_frame, textvariable=self.metapop_exe_location, justify=tk.LEFT)
        self.metapop_exe_location_entry = tk.Entry(file_options_frame, textvariable=self.metapop_exe_location, width=60, justify=tk.LEFT)
        tk.Label(file_options_frame, text='RAMAS Metapop program file (exe) location:').grid(row=0, column=0, columnspan=3, sticky=tk.NW+tk.SW, padx=5, pady=0)
        tk.Label(file_options_frame, text='').grid(row=1, column=0, padx=5, pady=0)
        if tool_option_values['run_metapop_batch_locally'] :
            self.metapop_exe_location_button.grid(row=1, column=1, padx=4, pady=5, sticky=tk.NW+tk.SE)
            self.metapop_exe_location_label.grid(row=1, column=2, padx=5, pady=5, sticky=tk.NW+tk.SW)
        else :
            self.metapop_exe_location_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.NW+tk.SW)
        
        # Metapop batch file run on local machine
        self.run_metapop_batch_locally = tk.IntVar(value=int(tool_option_values['run_metapop_batch_locally']))
        self.run_metapop_batch_locally_checkbox = tk.Checkbutton(file_options_frame, variable=self.run_metapop_batch_locally, text='Metapop batch file run on local machine', command=self.setBatchLocalOptions)
        tk.Label(file_options_frame, text='').grid(row=2, column=0, padx=5, pady=0)
        self.run_metapop_batch_locally_checkbox.grid(row=2, column=1, columnspan=2, sticky=tk.NW+tk.SW, padx=0, pady=2)

        # Register directory selection method
        select_file_generation_directory = file_options_frame.register(self.selectFileGenerationDirectory)

        # Default location for generated files
        self.default_generated_file_location = tk.StringVar(value=tool_option_values['default_generated_file_location'])
        self.default_generated_file_location_button = tk.Button(file_options_frame, text='Select Directory', command=(select_file_generation_directory, 'options'))
        default_generated_file_location_label = tk.Label(file_options_frame, textvariable=self.default_generated_file_location, justify=tk.LEFT)
        tk.Label(file_options_frame, text='Default toolkit working directory:').grid(row=3, column=0, columnspan=3, sticky=tk.NW+tk.SW, padx=5, pady=0)
        tk.Label(file_options_frame, text='').grid(row=4, column=0, padx=5, pady=0)
        self.default_generated_file_location_button.grid(row=4, column=1, padx=4, pady=5, sticky=tk.NW+tk.SE)
        default_generated_file_location_label.grid(row=4, column=2, padx=5, pady=5, sticky=tk.NW+tk.SW)
        
        file_options_frame.grid(row=0, column=0, sticky=tk.NW+tk.SE, padx=10, pady=10)

        # Create the MP Sampling Generation Tool Options frame

        mp_sampling_options_frame = tk.LabelFrame(self.options_window, text='MP Sampling Generation Options', padx=5, pady=5)

        # Register validation and selection behaviour methods
        validate_samples = mp_sampling_options_frame.register(self.validateNumberOfSamples)
        validate_bounds = mp_sampling_options_frame.register(self.validateParameterBoundOptions)
        validate_lhs_settings = self.parameter_lhs_settings_frame.register(self.validateParameterLHSSettingsOptions)
        validate_counts = mp_sampling_options_frame.register(self.validateIntegerCounts)

        # Baseline File Options
        self.reset_sampling_when_loading_file = tk.IntVar(value=int(tool_option_values['reset_sampling_when_loading_file']))
        self.reset_sampling_when_loading_file_checkbox = tk.Checkbutton(mp_sampling_options_frame, variable=self.reset_sampling_when_loading_file, text='Reset the sampling parameters when loading a new baseline file')
        row = 0
        tk.Label(mp_sampling_options_frame, text='Baseline File Options:').grid(row=row, column=0, columnspan=16, sticky=tk.NW+tk.SW, padx=5, pady=0)
        row += 1 # 1
        self.reset_sampling_when_loading_file_checkbox.grid(row=row, column=1, columnspan=15, sticky=tk.NW+tk.SW, padx=1, pady=0)

        # Sampling Options
        self.enforce_minimum_number_of_samples = tk.IntVar(value=int(tool_option_values['enforce_minimum_number_of_samples']))
        self.default_number_of_lhs_samples = tk.StringVar(value=tool_option_values['default_number_of_lhs_samples'])
        self.default_number_of_random_samples = tk.StringVar(value=tool_option_values['default_number_of_random_samples'])
        if tool_option_values['enforce_minimum_number_of_samples'] :
            if tool_option_values['default_number_of_lhs_samples'] < self.config.minimum_number_of_samples :
                self.default_number_of_lhs_samples.set(str(self.config.minimum_number_of_samples))
            if tool_option_values['default_number_of_random_samples'] < self.config.minimum_number_of_samples :
                self.default_number_of_random_samples.set(str(self.config.minimum_number_of_samples))
        self.default_number_of_lhs_samples_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_number_of_lhs_samples, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_samples, '%P', '%V', 'options', 'Latin Hypercube'))
        self.default_number_of_random_samples_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_number_of_random_samples, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_samples, '%P', '%V', 'options', 'Random'))
        self.enforce_minimum_number_of_samples_checkbox = tk.Checkbutton(mp_sampling_options_frame, variable=self.enforce_minimum_number_of_samples, text='Restrict the number of samples to a minimum of '+str(self.config.minimum_number_of_samples)+' (from tool configuration)', command=self.setNumberOfSamplesRestriction)
        row += 1 # 2
        tk.Label(mp_sampling_options_frame, text='Sampling Options:').grid(row=row, column=0, columnspan=16, sticky=tk.NW+tk.SW, padx=5, pady=0)
        row += 1 # 3
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='Default number of Latin Hypercube samples:').grid(row=row, column=1, columnspan=4, sticky=tk.NW+tk.SW, padx=4, pady=0)
        self.default_number_of_lhs_samples_entry.grid(row=row, column=5, sticky=tk.NW+tk.SW, padx=0, pady=2)
        row += 1 # 4
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='Default number of random samples:').grid(row=row, column=1, columnspan=4, sticky=tk.NW+tk.SW, padx=4, pady=0)
        self.default_number_of_random_samples_entry.grid(row=row, column=5, sticky=tk.NW+tk.SW, padx=0, pady=2)
        row += 1 # 5
        self.enforce_minimum_number_of_samples_checkbox.grid(row=row, column=1, columnspan=15, sticky=tk.NW+tk.SW, padx=1, pady=0)

        # Parameter Settings Options
        self.default_lhs_uniform_distr_lower_setting = tk.StringVar(value=tool_option_values['default_lhs_uniform_distr_lower_setting'])
        self.default_lhs_uniform_distr_upper_setting = tk.StringVar(value=tool_option_values['default_lhs_uniform_distr_upper_setting'])
        self.default_lhs_gaussian_distr_mean_setting = tk.StringVar(value=tool_option_values['default_lhs_gaussian_distr_mean_setting'])
        self.default_lhs_gaussian_distr_stdev_setting = tk.StringVar(value=tool_option_values['default_lhs_gaussian_distr_stdev_setting'])
        self.default_lhs_triangular_distr_lower_setting = tk.StringVar(value=tool_option_values['default_lhs_triangular_distr_lower_setting'])
        self.default_lhs_triangular_distr_upper_setting = tk.StringVar(value=tool_option_values['default_lhs_triangular_distr_upper_setting'])
        self.default_lhs_triangular_distr_mode_setting = tk.StringVar(value=tool_option_values['default_lhs_triangular_distr_mode_setting'])
        self.default_lhs_lognormal_distr_lower_setting = tk.StringVar(value=tool_option_values['default_lhs_lognormal_distr_lower_setting'])
        self.default_lhs_lognormal_distr_scale_setting = tk.StringVar(value=tool_option_values['default_lhs_lognormal_distr_scale_setting'])
        self.default_lhs_lognormal_distr_scale_increment = tk.StringVar(value=tool_option_values['default_lhs_lognormal_distr_scale_increment'])
        self.default_lhs_lognormal_distr_sigma_setting = tk.StringVar(value=tool_option_values['default_lhs_lognormal_distr_sigma_setting'])
        self.default_lhs_lognormal_distr_sigma_increment = tk.StringVar(value=tool_option_values['default_lhs_lognormal_distr_sigma_increment'])
        self.default_lhs_beta_distr_lower_setting = tk.StringVar(value=tool_option_values['default_lhs_beta_distr_lower_setting'])
        self.default_lhs_beta_distr_upper_setting = tk.StringVar(value=tool_option_values['default_lhs_beta_distr_upper_setting'])
        self.default_lhs_beta_distr_alpha_setting = tk.StringVar(value=tool_option_values['default_lhs_beta_distr_alpha_setting'])
        self.default_lhs_beta_distr_alpha_increment = tk.StringVar(value=tool_option_values['default_lhs_beta_distr_alpha_increment'])
        self.default_lhs_beta_distr_beta_setting = tk.StringVar(value=tool_option_values['default_lhs_beta_distr_beta_setting'])
        self.default_lhs_beta_distr_beta_increment = tk.StringVar(value=tool_option_values['default_lhs_beta_distr_beta_increment'])
        default_lhs_uniform_distr_lower_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_uniform_distr_lower_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Uniform', 'Lower'))
        default_lhs_uniform_distr_upper_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_uniform_distr_upper_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Uniform', 'Upper'))
        default_lhs_gaussian_distr_mean_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_gaussian_distr_mean_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Gaussian', 'Mean'))
        default_lhs_gaussian_distr_stdev_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_gaussian_distr_stdev_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Gaussian', 'Std. Dev.'))
        default_lhs_triangular_distr_lower_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_triangular_distr_lower_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Triangular', 'Lower (a)'))
        default_lhs_triangular_distr_upper_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_triangular_distr_upper_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Triangular', 'Upper (b)'))
        default_lhs_triangular_distr_mode_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_triangular_distr_mode_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Triangular', 'Mode (c)'))
        default_lhs_lognormal_distr_lower_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_lognormal_distr_lower_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Lognormal', 'Lower'))
        default_lhs_lognormal_distr_scale_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_lognormal_distr_scale_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Lognormal', 'Scale'))
        default_lhs_lognormal_distr_scale_increment_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_lognormal_distr_scale_increment, width=4, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Lognormal', 'Scale Increment'))
        default_lhs_lognormal_distr_sigma_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_lognormal_distr_sigma_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Lognormal', 'Sigma'))
        default_lhs_lognormal_distr_sigma_increment_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_lognormal_distr_sigma_increment, width=4, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Lognormal', 'Sigma Increment'))
        default_lhs_beta_distr_lower_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_beta_distr_lower_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Beta', 'Lower'))
        default_lhs_beta_distr_upper_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_beta_distr_upper_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Beta', 'Upper'))
        default_lhs_beta_distr_alpha_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_beta_distr_alpha_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Beta', 'Alpha'))
        default_lhs_beta_distr_alpha_increment_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_beta_distr_alpha_increment, width=4, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Beta', 'Alpha Increment'))
        default_lhs_beta_distr_beta_setting_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_beta_distr_beta_setting, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Beta', 'Beta'))
        default_lhs_beta_distr_beta_increment_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_lhs_beta_distr_beta_increment, width=4, justify=tk.CENTER, validate='all', validatecommand=(validate_lhs_settings, '%P', '%V', 'Beta', 'Beta Increment'))

        self.default_sample_bounds_for_random = tk.StringVar(value=tool_option_values['default_sample_bounds_for_random'])
        default_sample_bounds_for_random_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_sample_bounds_for_random, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_bounds, '%P', '%V'))
        self.default_sample_bounds_for_full_factorial = tk.StringVar(value=tool_option_values['default_sample_bounds_for_full_factorial'])
        default_sample_bounds_for_full_factorial_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.default_sample_bounds_for_full_factorial, width=6, justify=tk.CENTER, validate='all', validatecommand=(validate_bounds, '%P', '%V'))

        row += 1 # 6
        tk.Label(mp_sampling_options_frame, text='Parameter Settings Options:').grid(row=row, column=0, columnspan=16, sticky=tk.NW+tk.SW, padx=5, pady=0)

        row += 1 # 7
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='Default sample settings for Latin Hypercube:').grid(row=row, column=1, columnspan=15, sticky=tk.NW+tk.SW, padx=4, pady=0)

        row += 1 # 8
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=1, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='Uniform distribution:                            ').grid(row=row, column=2, sticky=tk.NW+tk.SW, padx=4, pady=2) # TODO: spacing
        tk.Label(mp_sampling_options_frame, text='Lower').grid(row=row, column=3, columnspan=2, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_uniform_distr_lower_setting_entry.grid(row=row, column=5, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=6, padx=0, pady=2, sticky=tk.NW+tk.SW)
        tk.Label(mp_sampling_options_frame, text='  Upper').grid(row=row, column=7, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_uniform_distr_upper_setting_entry.grid(row=row, column=8, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=9, columnspan=2, padx=0, pady=2, sticky=tk.NW+tk.SW)

        row += 1 # 9
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=1, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='Gaussian distribution:').grid(row=row, column=2, sticky=tk.NW+tk.SW, padx=4, pady=2)
        tk.Label(mp_sampling_options_frame, text='Mean').grid(row=row, column=3, columnspan=2, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_gaussian_distr_mean_setting_entry.grid(row=row, column=5, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=6, padx=0, pady=2, sticky=tk.NW+tk.SW)
        tk.Label(mp_sampling_options_frame, text='  Std. Dev.').grid(row=row, column=7, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_gaussian_distr_stdev_setting_entry.grid(row=row, column=8, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=9, columnspan=2, padx=0, pady=2, sticky=tk.NW+tk.SW)

        row += 1 # 10
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=1, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='Triangular distribution:').grid(row=row, column=2, sticky=tk.NW+tk.SW, padx=4, pady=2)
        tk.Label(mp_sampling_options_frame, text='Lower (a)').grid(row=row, column=3, columnspan=2, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_triangular_distr_lower_setting_entry.grid(row=row, column=5, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=6, padx=0, pady=2, sticky=tk.NW+tk.SW)
        tk.Label(mp_sampling_options_frame, text='  Upper (b)').grid(row=row, column=7, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_triangular_distr_upper_setting_entry.grid(row=row, column=8, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=9, columnspan=3, padx=0, pady=2, sticky=tk.NW+tk.SW)
        tk.Label(mp_sampling_options_frame, text='  Mode (c)').grid(row=row, column=12, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_triangular_distr_mode_setting_entry.grid(row=row, column=13, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=14, columnspan=2, padx=0, pady=2, sticky=tk.NW+tk.SW)

        row += 1 # 11
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=1, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='Lognormal distribution:').grid(row=row, column=2, sticky=tk.NW+tk.SW, padx=4, pady=2)
        tk.Label(mp_sampling_options_frame, text='Lower').grid(row=row, column=3, columnspan=2, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_lognormal_distr_lower_setting_entry.grid(row=row, column=5, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=6, padx=0, pady=2, sticky=tk.NW+tk.SW)
        tk.Label(mp_sampling_options_frame, text='  Scale').grid(row=row, column=7, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_lognormal_distr_scale_setting_entry.grid(row=row, column=8, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text=u'\u00B1').grid(row=row, column=9, sticky=tk.NW, pady=2)
        default_lhs_lognormal_distr_scale_increment_entry.grid(row=row, column=10, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=11, padx=0, pady=2, sticky=tk.NW+tk.SW)
        tk.Label(mp_sampling_options_frame, text='  Sigma').grid(row=row, column=12, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_lognormal_distr_sigma_setting_entry.grid(row=row, column=13, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text=u'\u00B1').grid(row=row, column=14, sticky=tk.NW, pady=2)
        default_lhs_lognormal_distr_sigma_increment_entry.grid(row=row, column=15, sticky=tk.NW+tk.SW, padx=0, pady=2)

        row += 1 # 12
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=1, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='Beta distribution:').grid(row=row, column=2, sticky=tk.NW+tk.SW, padx=4, pady=2)
        tk.Label(mp_sampling_options_frame, text='Lower').grid(row=row, column=3, columnspan=2, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_beta_distr_lower_setting_entry.grid(row=row, column=5, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=6, padx=0, pady=2, sticky=tk.NW+tk.SW)
        tk.Label(mp_sampling_options_frame, text='  Upper').grid(row=row, column=7, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_beta_distr_upper_setting_entry.grid(row=row, column=8, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=9, columnspan=3, padx=0, pady=2, sticky=tk.NW+tk.SW)
        tk.Label(mp_sampling_options_frame, text='  Alpha').grid(row=row, column=12, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_beta_distr_alpha_setting_entry.grid(row=row, column=13, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text=u'\u00B1').grid(row=row, column=14, sticky=tk.NW, pady=2)
        default_lhs_beta_distr_alpha_increment_entry.grid(row=row, column=15, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='  Beta').grid(row=row, column=16, padx=0, pady=2, sticky=tk.NW+tk.SW)
        default_lhs_beta_distr_beta_setting_entry.grid(row=row, column=17, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text=u'\u00B1').grid(row=row, column=18, sticky=tk.NW, pady=2)
        default_lhs_beta_distr_beta_increment_entry.grid(row=row, column=19, sticky=tk.NW+tk.SW, padx=0, pady=2)

        row += 1 # 13
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='Default sample bounds for Random:').grid(row=row, column=1, columnspan=3, sticky=tk.NW+tk.SW, padx=4, pady=0)
        tk.Label(mp_sampling_options_frame, text=u'\u00B1').grid(row=row, column=4, sticky=tk.NE, pady=2)
        default_sample_bounds_for_random_entry.grid(row=row, column=5, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=6, padx=0, pady=0, sticky=tk.NW+tk.SW)

        row += 1 # 14
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='Default sample bounds for Full Factorial:').grid(row=row, column=1, columnspan=3, sticky=tk.NW+tk.SW, padx=4, pady=0)
        tk.Label(mp_sampling_options_frame, text=u'\u00B1').grid(row=row, column=4, sticky=tk.NE, pady=2)
        default_sample_bounds_for_full_factorial_entry.grid(row=row, column=5, sticky=tk.NW+tk.SW, padx=0, pady=2)
        tk.Label(mp_sampling_options_frame, text='%').grid(row=row, column=6, padx=0, pady=0, sticky=tk.NW+tk.SW)

        # Sampling File Generation Options
        if tool_option_values['use_mp_baseline_values'] :
            mp_setting_state = tk.DISABLED
        else :
            mp_setting_state = tk.NORMAL
        self.number_of_metapop_iterations = tk.StringVar(value=tool_option_values['number_of_metapop_iterations'])
        self.number_of_metapop_iterations_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.number_of_metapop_iterations, width=6, justify=tk.CENTER, state=mp_setting_state, validate='all', validatecommand=(validate_counts, '%P', '%V', 'number_of_metapop_iterations'))
        self.metapop_simulation_duration = tk.StringVar(value=tool_option_values['metapop_simulation_duration'])
        self.metapop_simulation_duration_entry = tk.Entry(mp_sampling_options_frame, textvariable=self.metapop_simulation_duration, width=6, justify=tk.CENTER, state=mp_setting_state, validate='all', validatecommand=(validate_counts, '%P', '%V', 'metapop_simulation_duration'))
        self.use_mp_baseline_values = tk.IntVar(value=int(tool_option_values['use_mp_baseline_values']))
        self.use_mp_baseline_values_checkbox = tk.Checkbutton(mp_sampling_options_frame, variable=self.use_mp_baseline_values, text='Use values from baseline MP file', command=self.setGenerationOptions)
        row += 1 # 15
        tk.Label(mp_sampling_options_frame, text='MP Generation Options:').grid(row=row, column=0, columnspan=16, sticky=tk.NW+tk.SW, padx=5, pady=0)
        row += 1 # 16
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='Number of RAMAS Metapop iterations per scenario:').grid(row=row, column=1, columnspan=4, sticky=tk.NW+tk.SW, padx=4, pady=0)
        self.number_of_metapop_iterations_entry.grid(row=row, column=5, sticky=tk.NW+tk.SW, padx=0, pady=2)
        row += 1 # 17
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        tk.Label(mp_sampling_options_frame, text='RAMAS Metapop simulation duration:').grid(row=row, column=1, columnspan=4, sticky=tk.NW+tk.SW, padx=4, pady=0)
        self.metapop_simulation_duration_entry.grid(row=row, column=5, sticky=tk.NW+tk.SW, padx=0, pady=2)
        row += 1 # 18
        tk.Label(mp_sampling_options_frame, text='').grid(row=row, column=0, padx=3, pady=0)
        self.use_mp_baseline_values_checkbox.grid(row=row, column=1, columnspan=15, sticky=tk.NW+tk.SW, padx=1, pady=0)

        row += 1 # 19
        tk.Frame(mp_sampling_options_frame).grid(row=row, column=0, padx=0, pady=1)
        mp_sampling_options_frame.grid(row=1, column=0, sticky=tk.NW+tk.SE, padx=10, pady=0)

        # Create the Results Options frame

        mp_results_options_frame = tk.LabelFrame(self.options_window, text='MP Results Summary Options', padx=5, pady=5)

        # Register generic focus method (NOT USED)
        focus_on_field = mp_results_options_frame.register(self.focusOnField)

        # Auto run results summary
        self.auto_run_results_summary_tool = tk.IntVar(value=int(tool_option_values['auto_run_results_summary_tool']))
        self.auto_run_results_summary_tool_checkbox = tk.Checkbutton(mp_results_options_frame, variable=self.auto_run_results_summary_tool, text='Automatically run batch and results summary when MP generation is complete', command=self.autorunResultsSummaryToolSelected)
        self.auto_run_results_summary_tool_checkbox.grid(row=0, column=0, sticky=tk.NW+tk.SW, padx=2, pady=0)
        #tk.Label(mp_results_options_frame, text='Automatically run results summary when MP generation is complete').grid(row=0, column=1)

        mp_results_options_frame.grid(row=2, column=0, sticky=tk.NW+tk.SE, padx=10, pady=10)

        # Save options and cancel buttons
        option_actions_frame = tk.Frame(self.options_window)
        self.save_options_button = tk.Button(option_actions_frame, text='Save Options', command=self.saveOptions)
        cancel_options_button = tk.Button(option_actions_frame, text='Cancel', command=self.cancelOptions)
        self.save_options_button.grid(row=0, column=0, sticky=tk.NW+tk.SE, padx=0, pady=0)
        cancel_options_button.grid(row=0, column=1, sticky=tk.NW+tk.SE, padx=10, pady=0)
        option_actions_frame.grid(row=3, column=0, sticky=tk.NW+tk.SE, padx=10, pady=0)
        tk.Frame(self.options_window).grid(row=4, column=0, padx=0, pady=5)

    # Options Method: Looks for subdirectory matching substring  
    def findMatchingInDirectory(self, directory, matching_substring) :
        found_dir = ''
        for item in listdir(directory) :
            if item.lower().find(matching_substring.lower()) != -1 and not found_dir :
                found_dir = item
        return found_dir
                              
    # Options Method: Select Exe File
    def selectExeFile(self) :

        # Place focus on load button
        self.metapop_exe_location_button.focus_set()

        # Exit if validation warning is pending
        if self.validation_warning_pending :
            self.validation_warning_pending = False
            return True

        # Check if current location exists or attempt to find it
        initial_directory = '\\'
        current_exe = self.metapop_exe_location.get()
        if path.exists(current_exe) :
           initial_directory = self.mp_file_helper.splitPath(current_exe)['directory']
           initial_file = self.mp_file_helper.splitPath(current_exe)['name']
        else :
            # Attempt to find Metapop Exe
            initial_directory = path.join(initial_directory, self.findMatchingInDirectory(initial_directory, 'Program Files'))
            initial_directory = path.join(initial_directory, self.findMatchingInDirectory(initial_directory, 'RAMASGIS'))
            initial_file = self.findMatchingInDirectory(initial_directory, 'Metapop.exe')

        # Open file selection dialog
        exe_file_path = askopenfilename(title='Select the location of the RAMAS Metapop program (exe) file',
                                        initialdir=initial_directory,
                                        initialfile=initial_file,
                                        filetypes=[('Exe Files', '*.exe'), ('All Files', '*.*')])
        
        # Set exe path label
        if exe_file_path : # File selected
            exe_file_path = exe_file_path.replace('/', '\\')
            self.metapop_exe_location.set(exe_file_path)

        # Reset focus to options window
        self.options_window.focus_set()

    # Options Method: Set batch local options
    def setBatchLocalOptions(self) :

        # Place focus on ckeckbox
        self.run_metapop_batch_locally_checkbox.focus_set()

        # Exit if validation warning is pending
        if self.validation_warning_pending :
            self.run_metapop_batch_locally.set(int(not bool(self.run_metapop_batch_locally.get())))
            self.validation_warning_pending = False
            return True

        # If batch is run locally and current Metapop exe location doesn't exist try to find it
        if self.run_metapop_batch_locally.get() and not path.exists(self.metapop_exe_location.get()) :
            metapop_exe_path = environ['PROGRAMFILES']
            metapop_exe_path = path.join(metapop_exe_path, self.findMatchingInDirectory(metapop_exe_path, 'RAMASGIS'))
            metapop_exe_path = path.join(metapop_exe_path, self.findMatchingInDirectory(metapop_exe_path, 'Metapop.exe'))
            if self.mp_file_helper.splitPath(metapop_exe_path)['name'].lower().find('metapop.exe') != -1 :
                self.metapop_exe_location.set(metapop_exe_path)

        # Swap entry method
        if self.run_metapop_batch_locally.get() :
            self.metapop_exe_location_entry.grid_forget()
            self.metapop_exe_location_button.grid(row=1, column=1, padx=4, pady=5, sticky=tk.NW+tk.SE)
            self.metapop_exe_location_label.grid(row=1, column=2, padx=5, pady=5, sticky=tk.NW+tk.SW)
        else :
            self.metapop_exe_location_button.grid_forget()
            self.metapop_exe_location_label.grid_forget()
            self.metapop_exe_location_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.NW+tk.SW)

    # Generation and Options Method: Select file generation directory
    def selectFileGenerationDirectory(self, context) :
        
        # Use existing generation directory if it exists
        current_dir = ''
        if context == 'options' :
            self.default_generated_file_location_button.focus_set()
            if self.validation_warning_pending :
                self.validation_warning_pending = False
                return True
            current_dir = self.default_generated_file_location.get()
        else : # 'generate'
            self.generate_directory_button.focus_set()
            if self.validation_warning_pending :
                self.validation_warning_pending = False
                return True
            if self.generate_directory.has_key('path') :
                if self.generate_directory.has_key('timestamped') and self.generate_directory['timestamped'] :
                    current_dir = self.generate_directory['directory']
                else :
                    current_dir = self.generate_directory['path']
        if path.exists(current_dir) :
            initial_directory = current_dir
        elif path.exists(environ['USERPROFILE']) :
            initial_directory = environ['USERPROFILE']
        else :
            initial_directory = getcwd()

        # Open file selection dialog
        generation_directory_path = askdirectory(title='Select the directory to generate files',
                                                 initialdir=initial_directory)

        if generation_directory_path : # Directory selected

            # Create directory if it doesn't already exist
            if not path.exists(generation_directory_path) :
                try :
                    generation_directory_path = self.mp_file_helper.createDirectoryPath(generation_directory_path)
                except Exception, e :
                    directory_name = self.mp_file_helper.splitPath(generation_directory_path)['name']
                    showerror('Directory Error', 'Error loading or creating directory \"'+directory_name+'\". Check file permissions.')
                    print >> sys.stderr, 'Error loading or creating directory:', e

            # Set path label
            generation_directory_path = path.normpath(str(generation_directory_path))
            if context == 'options' :
                self.default_generated_file_location.set(generation_directory_path)
            else : # 'generate'
                self.generate_directory = self.mp_file_helper.splitPath(generation_directory_path)
                self.generate_directory_ok = True
                location_descr = ' : File generation in \"' + self.generate_directory['name'] + '\"'
                self.generate_directory_descr.set(location_descr)

        if context == 'options' :

            # Reset focus to options window
            self.options_window.focus_set()

        else : # 'generate'

            # Place focus on the select directory button
            self.generate_directory_button.focus_set()

            # Update workflow status
            self.updateStepsCompleted()

    # Options Method: Set number of samples restriction
    def setNumberOfSamplesRestriction(self) :
        
        # Place focus on checkbox
        self.enforce_minimum_number_of_samples_checkbox.focus_set()

        # Reset pending validation warning if any
        self.validation_warning_pending = False

        # Restrict values to minimum if required
        if self.enforce_minimum_number_of_samples.get() :
            if int(self.default_number_of_lhs_samples.get()) < self.config.minimum_number_of_samples :
                self.default_number_of_lhs_samples.set(str(self.config.minimum_number_of_samples))
            if int(self.default_number_of_random_samples.get()) < self.config.minimum_number_of_samples :
                self.default_number_of_random_samples.set(str(self.config.minimum_number_of_samples))

    # Options Method: Set generation options
    def setGenerationOptions(self) :

        # Place focus on checkbox
        self.use_mp_baseline_values_checkbox.focus_set()

        # Exit if validation warning is pending
        if self.validation_warning_pending :
            self.use_mp_baseline_values.set(int(not bool(self.use_mp_baseline_values.get())))
            self.validation_warning_pending = False
            return True

        if self.use_mp_baseline_values.get() :
            self.number_of_metapop_iterations_entry.configure(state=tk.DISABLED)
            self.metapop_simulation_duration_entry.configure(state=tk.DISABLED)
        else :
            self.number_of_metapop_iterations_entry.configure(state=tk.NORMAL)
            self.metapop_simulation_duration_entry.configure(state=tk.NORMAL)

    #  Options Method: Autorun results summary tool selected
    def autorunResultsSummaryToolSelected(self) :
        
        # Place focus on load button
        self.auto_run_results_summary_tool_checkbox.focus_set()

        # Revert selection if validation warning is pending
        if self.validation_warning_pending :
            self.auto_run_results_summary_tool.set(int(not bool(self.auto_run_results_summary_tool.get())))
            self.validation_warning_pending = False

    # Options Method: Save options
    def saveOptions(self) :

        # Place focus on load button
        self.save_options_button.focus_set()

        # Exit if validation warning is pending
        if self.validation_warning_pending :
            self.validation_warning_pending = False
            return True

        # Set options
        tool_options = self.config.getToolOptions()
        for option in tool_options.keys() :
            data_type = self.config.tool_option_parameter_types[option]
            option_value = eval('self.'+option+'.get()')
            if option_value == '' and not data_type == str :
                tool_options[option] = None 
            else :
                tool_options[option] = data_type(option_value)
        self.config.setToolOptions(tool_options)

        # Close options window
        self.options_window.destroy()

        # Propagate options
        self.propagateOptions()

        # Update workflow status
        self.updateStepsCompleted()

    # Options Method: Cancel Options
    def cancelOptions(self) :
        self.options_window.destroy()

    # Options Method: Propagate Options
    def propagateOptions(self) :

        # Get revised options
        tool_option_values = self.config.getToolOptions()

        # Propagate sampling options
        default_options_mapping = { 'Latin Hypercube' : 'default_number_of_lhs_samples',
                                    'Random' : 'default_number_of_random_samples' }
        for key, details in self.sampling_details.items() :
            if key == self.selected_sampling_type.get() :
                if details['sample_number_required'] :
                    default_sample_number = tool_option_values[default_options_mapping[key]]
                    if default_sample_number :
                        default_str = str(default_sample_number)
                    else :
                        default_str = ''
                    self.sampling_details[key]['sample_number'].set(default_str)

        # Propagate parameter settings options
        for key, parameter_selected in self.modify_parameter.items() :
            if parameter_selected.get() :
                if self.selected_sampling_type.get() == 'Random' or self.selected_sampling_type.get() == 'Full Factorial' :
                    if self.selected_sampling_type.get() == 'Random' :
                        default_sample_bounds = tool_option_values['default_sample_bounds_for_random']
                    else :
                        default_sample_bounds = tool_option_values['default_sample_bounds_for_full_factorial']
                    if default_sample_bounds :
                        default_str = str(default_sample_bounds)
                    else :
                        default_str = ''
                    previous_value = self.sample_bound_text[key].get()
                    self.sample_bound_text[key].set(default_str)
                    if default_str != previous_value :
                        self.validateParameterBounds(default_str, 'focusout', key, update_call=True)
                elif self.selected_sampling_type.get() == 'Latin Hypercube' :
                    for distr in self.config.lhs_distributions :
                        for setting in self.config.lhs_distribution_settings[distr] :
                            default_lhs_setting = tool_option_values[self.config.lhs_option_default_settings[distr][setting['name']]]
                            if default_lhs_setting :
                                default_str = str(default_lhs_setting)
                            else :
                                default_str = ''
                            previous_value = self.lhs_setting_text[key][distr][setting['name']].get()
                            self.lhs_setting_previous_text[key][distr][setting['name']] = previous_value
                            self.lhs_setting_text[key][distr][setting['name']].set(default_str)
                            if self.config.lhs_option_default_settings[distr].has_key(setting['name']+' Increment') :
                                entry_increment = tool_option_values[self.config.lhs_option_default_settings[distr][setting['name']+' Increment']]
                                if entry_increment :
                                    self.lhs_setting_entry[key][distr][setting['name']].configure(from_=entry_increment, to=1000, increment=entry_increment)
                            if self.lhs_distribution_selection_text[key].get() == distr and default_str != previous_value and not self.warning_shown_for_update_validation :
                                self.validateParameterLHSSettings(default_str, 'focusout', key, distr, setting['name'], update_call=True)
                        self.warning_shown_for_update_validation = False
                    # Update set via selected value fields
                    if self.parameter_set_via_text[key].get() != self.parameter_set_via_selection_values[0] :
                        self.parameterSetViaSelection(key, self.parameter_set_via_text[key].get(), selection_made=False)
                    # Update current viewed LHS distribution
                    if self.current_parameter_lhs_distribution_viewed == key  and self.parameterHasValidSettings(key, to_view=True) :
                        self.updateLhsDistributionWindow(key, self.lhs_current_displayed_distribution[key], button_pressed=False)
                
        # Propagate sampling file generation options
        self.generate_metapop_iterations.set('_')
        self.generate_metapop_duration.set('_')
        if tool_option_values['use_mp_baseline_values'] :
            self.generate_settings_uses_text.set('MP generation uses baseline settings:')
            if self.extraction_ok :
                self.generate_metapop_iterations.set(int(self.mp_file_helper.getAdditionalParameterValue('Replications')))
                self.generate_metapop_duration.set(int(self.mp_file_helper.getAdditionalParameterValue('Duration')))
        else :
            self.generate_settings_uses_text.set('MP generation uses option settings:')
            if tool_option_values['number_of_metapop_iterations'] :
                self.generate_metapop_iterations.set(tool_option_values['number_of_metapop_iterations'])
            if tool_option_values['metapop_simulation_duration'] :
                self.generate_metapop_duration.set(tool_option_values['metapop_simulation_duration'])
        self.generate_use_mp_baseline_values.set(int(tool_option_values['use_mp_baseline_values']))
        location_descr = ' : Select location for generated files'
        if tool_option_values['default_generated_file_location'] and path.exists(tool_option_values['default_generated_file_location']) :
            self.generate_directory = self.mp_file_helper.splitPath(tool_option_values['default_generated_file_location'])
            self.generate_directory_ok = True
            location_descr = ' : File generation in \"' + self.generate_directory['name'] + '\"'
        self.generate_directory_descr.set(location_descr)

        # Propagate auto run result summary and warning if metapop exe not found locally
        if path.exists(tool_option_values['metapop_exe_location']) :
            self.auto_run_results_summary.set(int(tool_option_values['auto_run_results_summary_tool']))
            self.metapop_exe_warning_label.grid_forget()
        else :
            self.auto_run_results_summary.set(0)
            self.metapop_exe_warning_label.grid(row=3, column=0, sticky=tk.NW+tk.SW, padx=3, pady=0)

    # Generic: Method for setting focus on a field
    def focusOnField(self, field_name) :
        eval('self.'+field_name).focus_set()
        self.validation_warning_pending = False

    # MP Generation: Step 1 Method: MP file load
    def loadMPFile(self) :

        # Place focus on load button
        self.load_button.focus_set()

        # Exit if validation warning is pending
        if self.validation_warning_pending :
            self.validation_warning_pending = False
            return True
        
        # Use default generation directory if it exists
        initial_directory = getcwd()
        tool_option_values = self.config.getToolOptions()
        if self.mp_file_helper.getBaselineMpFileDirectory() and path.exists(self.mp_file_helper.getBaselineMpFileDirectory()) :
            initial_directory = self.mp_file_helper.getBaselineMpFileDirectory()
        elif tool_option_values['default_generated_file_location'] and path.exists(tool_option_values['default_generated_file_location']) :
            initial_directory = tool_option_values['default_generated_file_location']
        elif path.exists(environ['USERPROFILE']) :
            initial_directory = environ['USERPROFILE']
        
        # Open file selection dialog
        mp_file_path = askopenfilename(title='Select a baseline MP file to load', filetypes=[('MP Files', '*.mp'), ('All Files', '*.*')], initialdir=initial_directory)

        previous_successful_extraction = self.extraction_ok
        if mp_file_path : # File selected

            # Load the file using the helper
            file_loaded_ok = False
            try :
                self.mp_file_helper.loadBaselineMpFile(mp_file_path)
                file_loaded_ok = True
            except Exception, e :
                showerror('File Load Error', 'Error loading the baseline MP file. Check file permissions.')
                print >> sys.stderr, 'Error loading the baseline MP file:', e
                file_loaded_ok = False
                self.load_label_text.set(' : Cannot load baseline MP file.')

            # Extract the baseline parameter values from the MP file contents, any that need to be calculated, and files linked to parameters
            if file_loaded_ok :
                try :
                    self.baseline_parameter_values['extracted'] = self.mp_file_helper.extractParametersFromMpFileContents()
                    self.baseline_parameter_values['calculated'] = self.mp_file_helper.constructFunctionDefinedMatrices()
                    self.baseline_parameter_values['file_links'] = self.mp_file_helper.loadFilesLinkedToParameters()
                    self.extraction_ok = True
                    self.load_label_text.set(' : \"' + self.mp_file_helper.getBaselineMpFileName() + '\" loaded')
                except Exception, e :
                    showerror('Extraction Error', 'Error extracting parameters from the baseline MP file contents.\nCheck that the loaded MP file is compatible with the tool configuration.')
                    print >> sys.stderr, 'Error extracting parameters from the baseline MP file contents:', e
                    self.extraction_ok = False
                    self.load_label_text.set(' : Cannot extract configured parameters from \"' + self.mp_file_helper.getBaselineMpFileName() + '\"')
                    self.mp_file_settings_frame.destroy()
                    self.mp_file_settings_frame = tk.Frame(self.file_load_frame)
                    self.mp_file_settings_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NW+tk.SE, padx=0, pady=5)
            else :
                self.extraction_ok = False

        # Calculate maximum parameter bounds for extracted parameters
        if self.extraction_ok :
            baseline_parameter_value_matrices = self.getBaselineParameterMatrices(adjust_diagonal_only_matrices=False)
            self.mp_constraint_helper.calculateMinimumAndMaximumMulitpliersAndBounds(baseline_parameter_value_matrices)

        # Set parameter baseline value views
        if self.extraction_ok :
            self.clearParameterBaselineValueViews()
            self.initialiseParameterBaselineValueViews()
        else :
            self.clearParameterBaselineValueViews()

        # Display the Metapop settings from the loaded file
        if self.extraction_ok :
            self.displayMpFileSettings()

        # Reset sampling selection and thus parameter settings when required
        if tool_option_values['reset_sampling_when_loading_file'] or not previous_successful_extraction or not self.extraction_ok :
            self.selected_sampling_type.set(self.sampling_types[0])
            self.updateSamplingType(selection_made=False)
        else :
            self.updateSamplingFrame(reset=False)

    # MP General Method: Get baseline parameter matrices
    def getBaselineParameterMatrices(self, use_calculated=True, adjust_diagonal_only_matrices=True) :

        baseline_parameter_value_matrices = {}
        for parameter_key, extracted_value in self.baseline_parameter_values['extracted'].items() :
            baseline_parameter_value_matrices[parameter_key] = extracted_value.copy()

        # Copy values from linked files if any
        for parameter_key, parameter_file_links in self.baseline_parameter_values['file_links'].items() :
            for row in range(np.shape(baseline_parameter_value_matrices[parameter_key])[0]) :
                for col in range(np.shape(baseline_parameter_value_matrices[parameter_key])[1]) :
                    link_file_name = parameter_file_links['link_frame'].iget_value(row, col)
                    if parameter_file_links['file_contents'].has_key(link_file_name) :
                        if parameter_file_links['use_file_value'] == 'max' :
                            baseline_parameter_value_matrices[parameter_key][row, col] = np.max(parameter_file_links['file_contents'][link_file_name].get_values())
                        else : # first value
                            baseline_parameter_value_matrices[parameter_key][row, col] = parameter_file_links['file_contents'][link_file_name].iget_value(0, 0)
                    
        # Combine extracted and calculated matrices
        if use_calculated :
            for parameter_key, calculated_value in self.baseline_parameter_values['calculated'].items() :
                baseline_parameter_value_matrices[parameter_key] = calculated_value

        # Adjust 'under diagonal only' matrices (Correlation Matrix only so far)
        if adjust_diagonal_only_matrices :
            if baseline_parameter_value_matrices.has_key('Correlation Matrix') :
                baseline_parameter_value_matrices['Correlation Matrix'] = baseline_parameter_value_matrices['Correlation Matrix'] + baseline_parameter_value_matrices['Correlation Matrix'].transpose()

        return baseline_parameter_value_matrices

    # MP Generation: Step 1 Method: Initialise parameter baseline selected values
    def initialiseParameterBaselineValueViews(self) :

        # Combine extracted and calculated matrices
        baseline_parameter_value_matrices = self.getBaselineParameterMatrices()

        # Baseline values to be placed in label grids within scrollable frames
        self.baseline_value_label_map = {}

        # Labels arranged in a scrollable canvas for each parameter
        self.bounds_baseline_value_labels = {}
        self.lhs_settings_baseline_value_labels = {}
        self.bounds_baseline_scrollable_canvas = {}
        self.lhs_settings_baseline_scrollable_canvas = {}
        self.bounds_baseline_scrollY = {}
        self.bounds_baseline_scrollX = {}
        self.lhs_settings_baseline_scrollY = {}
        self.lhs_settings_baseline_scrollX = {}

        # Handle oversized matrices via a row and column strip
        self.baseline_matrix_is_oversized = {}
        self.baseline_matrix_dimensions = {}
        self.baseline_matrix_grid_dimensions = {}
        self.baseline_oversized_strip_row_from = {}
        self.baseline_oversized_strip_column_from = {}

        # For each parameter present in the loaded baseline MP file
        for key, value_matrix in baseline_parameter_value_matrices.items() :

            # Determine indexes dependent on multi-layers
            number_of_layers = 1
            r_index = 0
            c_index = 1
            if len(value_matrix.shape) == 3 :
                number_of_layers = value_matrix.shape[0]
                r_index = 1
                c_index = 2

            # Prepare to look for first non zero value
            non_zero_value = { 'found' : False, 'r' : 0, 'c' : 0 }

            # Initialise expanded view cell width
            self.parameter_baseline_values['cell_width'][key] = 3

            for r in range(value_matrix.shape[r_index]) :
                for c in range(value_matrix.shape[c_index]) :

                    # Extracted value dependent on multi-layers and masking
                    masked = False
                    if len(np.shape(value_matrix)) == 3 :
                        if type(value_matrix) is np.ma.MaskedArray :
                            value = value_matrix.data[0,r,c]
                            masked = value_matrix.mask[0,r,c]
                        else :
                            value = value_matrix[0,r,c]
                    else :
                        if type(value_matrix) is np.ma.MaskedArray :
                            value = value_matrix.data[r,c]
                            masked = value_matrix.mask[r,c]
                        else :
                            value = value_matrix[r,c]

                    # Save first non-zero non-masked value found (for first sex if two sex model)
                    search_until_row = value_matrix.shape[r_index]
                    parameter_mapping = self.mp_file_helper.parameter_mapping[key]
                    if parameter_mapping.has_key('subset_mask') and parameter_mapping['subset_mask'].has_key('quadrants') and parameter_mapping['subset_mask']['quadrants'].has_key('divide_at') :
                        search_until_row = parameter_mapping['subset_mask']['quadrants']['divide_at']
                    if not non_zero_value['found'] or (self.config.parameter_initial_display[key] == 'last_non_zero' and r < search_until_row) :
                        if value != 0.0 and not masked:
                            non_zero_value['found'] = True
                            non_zero_value['r'] = r
                            non_zero_value['c'] = c

                    # Convert parameters to other types (default is float)
                    if self.config.parameter_data_types.has_key(key) :
                        if self.config.parameter_data_types[key] == 'integer' :
                            value = value.round().astype(int)
                    # Convert value to a formatted string
                    value_string = self.config.parameter_output_format[key]['display_format'] % value
                    
                    # Clear diagonal of 'under diagonal only' matrices (Correlation Matrix only so far)
                    if key == 'Correlation Matrix' and r == c :
                        value_string = ''

                    # Ignore masked entries for subset parameters
                    if parameter_mapping.has_key('subset_mask') and masked :
                        value_string = ''

                    # Set expanded view cell width to widest value string encountered
                    if len(value_string) > self.parameter_baseline_values['cell_width'][key] :
                        self.parameter_baseline_values['cell_width'][key] = len(value_string)

                    # Select first non-zero value and locate and highlight it in the grid
                    if non_zero_value['found'] and r == non_zero_value['r'] and c == non_zero_value['c'] :
                        self.parameter_baseline_values['row'][key] = r
                        self.parameter_baseline_values['column'][key] = c
                        self.parameter_baseline_values['value'][key].set(value_string)
                        self.parameter_baseline_values['matrix_value'][key] = value
                        self.parameter_baseline_values['highlight'][key] = True
                        self.parameter_bounds_baseline_x_label[key].configure(state=tk.NORMAL, width=self.parameter_baseline_values['cell_width'][key])
                        self.parameter_lhs_settings_baseline_x_label[key].configure(state=tk.NORMAL, width=self.parameter_baseline_values['cell_width'][key])
                    elif r == 0 and c == 1 and key == 'Correlation Matrix' : # initialise in case no non-zero found
                        self.parameter_baseline_values['value'][key].set(value_string)
                        self.parameter_baseline_values['matrix_value'][key] = value
                        self.parameter_baseline_values['highlight'][key] = False # not(masked)
                    elif r == 0 and c == 0 : # initialise in case no non-zero found
                        self.parameter_baseline_values['value'][key].set(value_string)
                        self.parameter_baseline_values['matrix_value'][key] = value
                        self.parameter_baseline_values['highlight'][key] = False # not(masked)

            if not non_zero_value['found'] :
                if key == 'Correlation Matrix' :
                    self.parameter_baseline_values['row'][key] = 0
                    self.parameter_baseline_values['column'][key] = 1
                else :
                    self.parameter_baseline_values['row'][key] = 0
                    self.parameter_baseline_values['column'][key] = 0
                if self.parameter_baseline_values['highlight'][key] :
                    self.parameter_bounds_baseline_x_label[key].configure(state=tk.NORMAL, width=self.parameter_baseline_values['cell_width'][key])
                    self.parameter_lhs_settings_baseline_x_label[key].configure(state=tk.NORMAL, width=self.parameter_baseline_values['cell_width'][key])
                else :
                    self.parameter_bounds_baseline_x_label[key].configure(state=tk.DISABLED, width=self.parameter_baseline_values['cell_width'][key])
                    self.parameter_lhs_settings_baseline_x_label[key].configure(state=tk.DISABLED, width=self.parameter_baseline_values['cell_width'][key])

    # MP Generation: Step 3 Method: Set parameter baseline value expanded view for parameter
    def setParameterBaselineValueExpandedView(self, key, context) :

        # Combine extracted and calculated matrices
        value_matrix = self.getBaselineParameterMatrices()[key]

        # Resolve context
        if context == 'bounds' :
            parameter_baseline_x_frame = self.parameter_bounds_baseline_x_frame
            baseline_values_outer_frame = self.bounds_baseline_values_outer_frame
            baseline_values_inner_frame = self.bounds_baseline_values_inner_frame
            baseline_value_labels = self.bounds_baseline_value_labels
            baseline_scrollable_canvas = self.bounds_baseline_scrollable_canvas
            baseline_scrollY = self.bounds_baseline_scrollY
            baseline_scrollX = self.bounds_baseline_scrollX
        elif context == 'lhs_settings' :
            parameter_baseline_x_frame = self.parameter_lhs_settings_baseline_x_frame
            baseline_values_outer_frame = self.lhs_settings_baseline_values_outer_frame
            baseline_values_inner_frame = self.lhs_settings_baseline_values_inner_frame
            baseline_value_labels = self.lhs_settings_baseline_value_labels
            baseline_scrollable_canvas = self.lhs_settings_baseline_scrollable_canvas
            baseline_scrollY = self.lhs_settings_baseline_scrollY
            baseline_scrollX = self.lhs_settings_baseline_scrollX

        # Outer frame for label grids
        baseline_values_outer_frame[key] = tk.Frame(parameter_baseline_x_frame[key])

        # Scrollable canvas
        baseline_scrollable_canvas[key] = tk.Canvas(baseline_values_outer_frame[key])

        # Label grid inner frame to be placed inside scrollable canvas
        baseline_values_inner_frame[key] = tk.Frame(baseline_values_outer_frame[key])

        # Place inner frame inside scrollable canvas
        baseline_scrollable_canvas[key].create_window(0, 0, anchor=tk.NW, window=baseline_values_inner_frame[key])
        
        # Label grids
        baseline_value_labels[key] = []

        # Determine indexes dependent on multi-layers
        number_of_layers = 1
        r_index = 0
        c_index = 1
        if len(np.shape(value_matrix)) == 3 :
            number_of_layers = np.shape(value_matrix)[0]
            r_index = 1
            c_index = 2

        # Collect matrix indexes for labels
        rows = np.shape(value_matrix)[r_index]
        columns = np.shape(value_matrix)[c_index]
        r_c_indexes = {}
        if rows*columns > self.config.maximum_parameter_matrix_size : # strip cross
            self.baseline_matrix_is_oversized[key] = True
            self.baseline_matrix_dimensions[key] = { 'rows' : rows, 'columns' : columns }
            self.baseline_oversized_strip_row_from[key] = 0
            self.baseline_oversized_strip_column_from[key] = 0
            for r in range(rows) :
                r_c_indexes[r] = []
                for c in range(self.config.oversized_parameter_matrix_frame_size) :
                    r_c_indexes[r].append(c)
            for r in range(self.config.oversized_parameter_matrix_frame_size) :
                for c in range(self.config.oversized_parameter_matrix_frame_size, columns) :
                    r_c_indexes[r].append(c)
        else : # full matrix
            self.baseline_matrix_is_oversized[key] = False
            for r in range(rows) :
                r_c_indexes[r] = []
                for c in range(columns) :
                    r_c_indexes[r].append(c)

        # Initialise baseline value label array
        for r in range(rows) :
            baseline_value_labels[key].append([])
            for c in range(columns) :
                baseline_value_labels[key][r].append(None)

        # Build grids of labels for the matrix
        for r in range(rows) :
            for c in r_c_indexes[r] :

                # Extracted value dependent on multi-layers and masking
                masked = False
                if len(np.shape(value_matrix)) == 3 :
                    if type(value_matrix) is np.ma.MaskedArray :
                        value = value_matrix.data[0,r,c]
                        masked = value_matrix.mask[0,r,c]
                    else :
                        value = value_matrix[0,r,c]
                else :
                    if type(value_matrix) is np.ma.MaskedArray :
                        value = value_matrix.data[r,c]
                        masked = value_matrix.mask[r,c]
                    else :
                        value = value_matrix[r,c]

                # Convert parameters to other types (default is float)
                if self.config.parameter_data_types.has_key(key) :
                    if self.config.parameter_data_types[key] == 'integer' :
                        value = value.round().astype(int)
                # Convert value to a formatted string
                value_string = self.config.parameter_output_format[key]['display_format'] % value

                # Flag cell enabled for selecting value
                cell_enabled = True
                
                # Clear diagonal of 'under diagonal only' matrices (Correlation Matrix only so far)
                if key == 'Correlation Matrix' and r == c :
                    value_string = ''
                    cell_enabled = False

                # Ignore masked entries for subset parameters
                if self.mp_file_helper.parameter_mapping[key].has_key('subset_mask') and masked :
                    value_string = ''

                # Disable masked entries
                if masked :
                    cell_enabled = False

                # Add value labels to grid
                baseline_value_labels[key][r][c] = tk.Label(baseline_values_inner_frame[key], relief=tk.GROOVE, bd=2, text=value_string, width=self.parameter_baseline_values['cell_width'][key])
                if masked :
                    baseline_value_labels[key][r][c].configure(state=tk.DISABLED)
                baseline_value_labels[key][r][c].grid(row=r, column=c, sticky=tk.NW+tk.SE, padx=0, pady=0)

                # Bind button press event to the label (uses map to identify the label in event function)
                self.baseline_value_label_map[str(baseline_value_labels[key][r][c])] = { 'context' : context, 'key' : key, 'r' : r, 'c' : c }
                selectedParameterBaselineValue = parameter_baseline_x_frame[key].register(self.__selectedParameterBaselineValue)
                if cell_enabled :
                    baseline_value_labels[key][r][c].bind('<Button-1>', self.__selectedParameterBaselineValue)

        # Highlight the currently selected cell
        if baseline_value_labels[key][self.parameter_baseline_values['row'][key]][self.parameter_baseline_values['column'][key]] and self.parameter_baseline_values['highlight'][key] :
            baseline_value_labels[key][self.parameter_baseline_values['row'][key]][self.parameter_baseline_values['column'][key]].configure(bg='white')

        # Get value grid frame dimensions
        baseline_values_inner_frame[key].update_idletasks()
        grid_height = baseline_values_inner_frame[key].winfo_reqheight()
        grid_width = baseline_values_inner_frame[key].winfo_reqwidth()
        if self.baseline_matrix_is_oversized[key] :
            self.baseline_matrix_grid_dimensions[key] = { 'height' : grid_height, 'width' : grid_width }

        # Add scrollable canvases to outer frames
        baseline_scrollable_canvas[key].grid(row=0, column=0)

        # Add scrollbars if the dimensions are too big
        max_height = 80
        max_width = 120

        # Register scrollbar commands
        scroll_y_command = baseline_values_outer_frame[key].register(self.baselineScrollYCommand)
        scroll_x_command = baseline_values_outer_frame[key].register(self.baselineScrollXCommand)

        # Bounds value grids
        if grid_height > max_height or grid_width > max_width :
            baseline_scrollable_canvas[key]['scrollregion'] = (0, 0, grid_width, grid_height)
        if grid_height > max_height :
            baseline_scrollable_canvas[key]['height'] = max_height
            baseline_scrollY[key] = tk.Scrollbar(baseline_values_outer_frame[key], orient=tk.VERTICAL, command=(scroll_y_command, key, context))
            baseline_scrollY[key].grid(row=0, column=1, sticky=tk.N+tk.S)
            baseline_scrollable_canvas[key]['yscrollcommand'] = baseline_scrollY[key].set
        else :
            baseline_scrollable_canvas[key]['height'] = grid_height
        if grid_width > max_width :
            baseline_scrollable_canvas[key]['width'] = max_width
            baseline_scrollX[key] = tk.Scrollbar(baseline_values_outer_frame[key], orient=tk.HORIZONTAL, command=(scroll_x_command, key, context))
            baseline_scrollX[key].grid(row=1, column=0, sticky=tk.E+tk.W)
            baseline_scrollable_canvas[key]['xscrollcommand'] = baseline_scrollX[key].set
        else :
            baseline_scrollable_canvas[key]['width'] = grid_width

        # Add outer frames
        baseline_values_outer_frame[key].grid(row=0, column=0, sticky=tk.NW)

    # MP Generation: Step 3 Method: Baseline ScrollY Command
    def baselineScrollYCommand(self, key, context, *args) :

        # Resolve context
        if context == 'bounds' :
            parameter_baseline_x_frame = self.parameter_bounds_baseline_x_frame
            baseline_values_inner_frame = self.bounds_baseline_values_inner_frame
            baseline_value_labels = self.bounds_baseline_value_labels
            baseline_scrollable_canvas = self.bounds_baseline_scrollable_canvas
            baseline_scrollY = self.bounds_baseline_scrollY
            baseline_scrollX = self.bounds_baseline_scrollX
        elif context == 'lhs_settings' :
            parameter_baseline_x_frame = self.parameter_lhs_settings_baseline_x_frame
            baseline_values_inner_frame = self.lhs_settings_baseline_values_inner_frame
            baseline_value_labels = self.lhs_settings_baseline_value_labels
            baseline_scrollable_canvas = self.lhs_settings_baseline_scrollable_canvas
            baseline_scrollY = self.lhs_settings_baseline_scrollY
            baseline_scrollX = self.lhs_settings_baseline_scrollX

        if self.baseline_matrix_is_oversized[key] :
            
            # Resolve current scroll positions
            view_height = 80
            view_width = 120
            matrix_rows = self.baseline_matrix_dimensions[key]['rows']
            matrix_columns = self.baseline_matrix_dimensions[key]['columns']
            canvas_height = self.baseline_matrix_grid_dimensions[key]['height']
            canvas_width = self.baseline_matrix_grid_dimensions[key]['width']
            x_position = baseline_scrollX[key].get()[0]
            x_bar_width = baseline_scrollX[key].get()[1]-baseline_scrollX[key].get()[0]
            view_columns = float(view_width)/canvas_width*matrix_columns
            view_column_from = int(x_position/(1-x_bar_width)*(matrix_columns-view_columns))
            y_position = baseline_scrollY[key].get()[0]
            y_bar_height = baseline_scrollY[key].get()[1]-baseline_scrollY[key].get()[0]
            view_rows = float(view_height)/canvas_height*matrix_rows
            view_row_from = int(y_position/(1-y_bar_height)*(matrix_rows-view_rows))

            # Need to shift column strip if scrollX has moved
            if view_column_from != self.baseline_oversized_strip_column_from[key] :

                existing_from_row = self.baseline_oversized_strip_row_from[key]
                existing_from_column = self.baseline_oversized_strip_column_from[key]
                frame_size = self.config.oversized_parameter_matrix_frame_size

                # Remove existing column strip
                for r in range(matrix_rows) :
                    for c in range(existing_from_column, (existing_from_column + frame_size)) :
                        if r not in range(existing_from_row, (existing_from_row + frame_size)) :
                            if r < matrix_rows and c < matrix_columns :
                                self.baseline_value_label_map.pop(str(baseline_value_labels[key][r][c]))
                                baseline_value_labels[key][r][c].destroy()
                                baseline_value_labels[key][r][c] = None

                # Add shifted column strip
                value_matrix = self.getBaselineParameterMatrices()[key]
                for r in range(matrix_rows) :
                    for c in range(view_column_from, (view_column_from + frame_size)) :
                        if r not in range(existing_from_row, (existing_from_row + frame_size)) :
                            if r < matrix_rows and c < matrix_columns :

                                # Extracted value dependent on multi-layers and masking
                                masked = False
                                if len(np.shape(value_matrix)) == 3 :
                                    if type(value_matrix) is np.ma.MaskedArray :
                                        value = value_matrix.data[0,r,c]
                                        masked = value_matrix.mask[0,r,c]
                                    else :
                                        value = value_matrix[0,r,c]
                                else :
                                    if type(value_matrix) is np.ma.MaskedArray :
                                        value = value_matrix.data[r,c]
                                        masked = value_matrix.mask[r,c]
                                    else :
                                        value = value_matrix[r,c]

                                # Convert parameters to other types (default is float)
                                if self.config.parameter_data_types.has_key(key) :
                                    if self.config.parameter_data_types[key] == 'integer' :
                                        value = value.round().astype(int)
                                # Convert value to a formatted string
                                value_string = self.config.parameter_output_format[key]['display_format'] % value
                                
                                # Flag cell enabled for selecting value
                                cell_enabled = True
                                
                                # Clear diagonal of 'under diagonal only' matrices (Correlation Matrix only so far)
                                if key == 'Correlation Matrix' and r == c :
                                    value_string = ''
                                    cell_enabled = False

                                # Ignore masked entries for subset parameters
                                if self.mp_file_helper.parameter_mapping[key].has_key('subset_mask') and masked :
                                    value_string = ''

                                # Disable masked entries
                                if masked :
                                    cell_enabled = False

                                # Add value labels to grid
                                baseline_value_labels[key][r][c] = tk.Label(baseline_values_inner_frame[key], relief=tk.GROOVE, bd=2, text=value_string, width=self.parameter_baseline_values['cell_width'][key])
                                if masked :
                                    baseline_value_labels[key][r][c].configure(state=tk.DISABLED)
                                baseline_value_labels[key][r][c].grid(row=r, column=c, sticky=tk.NW+tk.SE, padx=0, pady=0)

                                # Bind button press event to the label (uses map to identify the label in event function)
                                self.baseline_value_label_map[str(baseline_value_labels[key][r][c])] = { 'context' : context, 'key' : key, 'r' : r, 'c' : c }
                                selectedParameterBaselineValue = parameter_baseline_x_frame[key].register(self.__selectedParameterBaselineValue)
                                if cell_enabled :
                                    baseline_value_labels[key][r][c].bind('<Button-1>', self.__selectedParameterBaselineValue)

                # Highlight the currently selected cell
                if baseline_value_labels[key][self.parameter_baseline_values['row'][key]][self.parameter_baseline_values['column'][key]] and self.parameter_baseline_values['highlight'][key] :
                    baseline_value_labels[key][self.parameter_baseline_values['row'][key]][self.parameter_baseline_values['column'][key]].configure(bg='white')

                # Get value grid frame dimensions
                baseline_values_inner_frame[key].update_idletasks()
                grid_height = baseline_values_inner_frame[key].winfo_reqheight()
                grid_width = baseline_values_inner_frame[key].winfo_reqwidth()
                self.baseline_matrix_grid_dimensions[key] = { 'height' : grid_height, 'width' : grid_width }

                # Update the strip from row
                self.baseline_oversized_strip_column_from[key] = view_column_from

        # Scroll canvas
        baseline_scrollable_canvas[key].yview(*args)

    # MP Generation: Step 3 Method: Baseline ScrollX Command
    def baselineScrollXCommand(self, key, context, *args) :

        # Resolve context
        if context == 'bounds' :
            parameter_baseline_x_frame = self.parameter_bounds_baseline_x_frame
            baseline_values_inner_frame = self.bounds_baseline_values_inner_frame
            baseline_value_labels = self.bounds_baseline_value_labels
            baseline_scrollable_canvas = self.bounds_baseline_scrollable_canvas
            baseline_scrollY = self.bounds_baseline_scrollY
            baseline_scrollX = self.bounds_baseline_scrollX
        elif context == 'lhs_settings' :
            parameter_baseline_x_frame = self.parameter_lhs_settings_baseline_x_frame
            baseline_values_inner_frame = self.lhs_settings_baseline_values_inner_frame
            baseline_value_labels = self.lhs_settings_baseline_value_labels
            baseline_scrollable_canvas = self.lhs_settings_baseline_scrollable_canvas
            baseline_scrollY = self.lhs_settings_baseline_scrollY
            baseline_scrollX = self.lhs_settings_baseline_scrollX

        if self.baseline_matrix_is_oversized[key] :
            
            # Resolve current scroll positions
            view_height = 80
            view_width = 120
            matrix_rows = self.baseline_matrix_dimensions[key]['rows']
            matrix_columns = self.baseline_matrix_dimensions[key]['columns']
            canvas_height = self.baseline_matrix_grid_dimensions[key]['height']
            canvas_width = self.baseline_matrix_grid_dimensions[key]['width']
            x_position = baseline_scrollX[key].get()[0]
            x_bar_width = baseline_scrollX[key].get()[1]-baseline_scrollX[key].get()[0]
            view_columns = float(view_width)/canvas_width*matrix_columns
            view_column_from = int(x_position/(1-x_bar_width)*(matrix_columns-view_columns))
            y_position = baseline_scrollY[key].get()[0]
            y_bar_height = baseline_scrollY[key].get()[1]-baseline_scrollY[key].get()[0]
            view_rows = float(view_height)/canvas_height*matrix_rows
            view_row_from = int(y_position/(1-y_bar_height)*(matrix_rows-view_rows))

            #print 'row:', view_row_from, ', col:', view_column_from

            # Need to shift row strip if scrollY has moved
            if view_row_from != self.baseline_oversized_strip_row_from[key] :
                #print 'need to shift row strip'

                existing_from_row = self.baseline_oversized_strip_row_from[key]
                existing_from_column = self.baseline_oversized_strip_column_from[key]
                frame_size = self.config.oversized_parameter_matrix_frame_size

                # Remove existing row strip
                for r in range(existing_from_row, (existing_from_row + frame_size)) :
                    for c in range(matrix_columns) :
                        if c not in range(existing_from_column, (existing_from_column + frame_size)) :
                            if r < matrix_rows and c < matrix_columns :
                                self.baseline_value_label_map.pop(str(baseline_value_labels[key][r][c]))
                                baseline_value_labels[key][r][c].destroy()
                                baseline_value_labels[key][r][c] = None

                # Add shifted row strip
                value_matrix = self.getBaselineParameterMatrices()[key]
                for r in range(view_row_from, (view_row_from + frame_size)) :
                    for c in range(matrix_columns) :
                        if c not in range(existing_from_column, (existing_from_column + frame_size)) :
                            if r < matrix_rows and c < matrix_columns :

                                # Extracted value dependent on multi-layers and masking
                                masked = False
                                if len(np.shape(value_matrix)) == 3 :
                                    if type(value_matrix) is np.ma.MaskedArray :
                                        value = value_matrix.data[0,r,c]
                                        masked = value_matrix.mask[0,r,c]
                                    else :
                                        value = value_matrix[0,r,c]
                                else :
                                    if type(value_matrix) is np.ma.MaskedArray :
                                        value = value_matrix.data[r,c]
                                        masked = value_matrix.mask[r,c]
                                    else :
                                        value = value_matrix[r,c]

                                # Convert parameters to other types (default is float)
                                if self.config.parameter_data_types.has_key(key) :
                                    if self.config.parameter_data_types[key] == 'integer' :
                                        value = value.round().astype(int)
                                # Convert value to a formatted string
                                value_string = self.config.parameter_output_format[key]['display_format'] % value
                                
                                # Flag cell enabled for selecting value
                                cell_enabled = True
                                
                                # Clear diagonal of 'under diagonal only' matrices (Correlation Matrix only so far)
                                if key == 'Correlation Matrix' and r == c :
                                    value_string = ''
                                    cell_enabled = False

                                # Ignore masked entries for subset parameters
                                if self.mp_file_helper.parameter_mapping[key].has_key('subset_mask') and masked :
                                    value_string = ''

                                # Disable masked entries
                                if masked :
                                    cell_enabled = False

                                # Add value labels to grid
                                baseline_value_labels[key][r][c] = tk.Label(baseline_values_inner_frame[key], relief=tk.GROOVE, bd=2, text=value_string, width=self.parameter_baseline_values['cell_width'][key])
                                if masked :
                                    baseline_value_labels[key][r][c].configure(state=tk.DISABLED)
                                baseline_value_labels[key][r][c].grid(row=r, column=c, sticky=tk.NW+tk.SE, padx=0, pady=0)

                                # Bind button press event to the label (uses map to identify the label in event function)
                                self.baseline_value_label_map[str(baseline_value_labels[key][r][c])] = { 'context' : context, 'key' : key, 'r' : r, 'c' : c }
                                selectedParameterBaselineValue = parameter_baseline_x_frame[key].register(self.__selectedParameterBaselineValue)
                                if cell_enabled :
                                    baseline_value_labels[key][r][c].bind('<Button-1>', self.__selectedParameterBaselineValue)

                # Highlight the currently selected cell
                if baseline_value_labels[key][self.parameter_baseline_values['row'][key]][self.parameter_baseline_values['column'][key]] and self.parameter_baseline_values['highlight'][key] :
                    baseline_value_labels[key][self.parameter_baseline_values['row'][key]][self.parameter_baseline_values['column'][key]].configure(bg='white')

                # Get value grid frame dimensions
                baseline_values_inner_frame[key].update_idletasks()
                grid_height = baseline_values_inner_frame[key].winfo_reqheight()
                grid_width = baseline_values_inner_frame[key].winfo_reqwidth()
                self.baseline_matrix_grid_dimensions[key] = { 'height' : grid_height, 'width' : grid_width }

                # Update the strip from row
                self.baseline_oversized_strip_row_from[key] = view_row_from

        # Scroll canvas
        baseline_scrollable_canvas[key].xview(*args)

    # MP Generation: Step 3 Event Method: Select parameter baseline value
    def __selectedParameterBaselineValue(self, event) :

        # Get details from map
        selected_label_details = self.baseline_value_label_map[str(event.widget)]
        key = selected_label_details['key']
        r = selected_label_details['r']
        c = selected_label_details['c']
        if selected_label_details['context'] == 'bounds' :
            value_string = self.bounds_baseline_value_labels[key][r][c]['text']
        else : # lhs_settings
            value_string = self.lhs_settings_baseline_value_labels[key][r][c]['text']
        
        # Remove highlight from previous
        previous_r = self.parameter_baseline_values['row'][key]
        previous_c = self.parameter_baseline_values['column'][key]

        if selected_label_details['context'] == 'bounds' :
            self.bounds_baseline_value_labels[key][previous_r][previous_c].configure(bg='SystemButtonFace')
        else : # lhs_settings
            self.lhs_settings_baseline_value_labels[key][previous_r][previous_c].configure(bg='SystemButtonFace')

        # Highlight selection
        if selected_label_details['context'] == 'bounds' :
            self.bounds_baseline_value_labels[key][r][c].configure(bg='white')
        else : # lhs_settings
            self.lhs_settings_baseline_value_labels[key][r][c].configure(bg='white')

        # Combine extracted and calculated matrices
        baseline_parameter_value_matrices = self.getBaselineParameterMatrices()

        # Extracted value dependent on multi-layers and masking
        if len(np.shape(baseline_parameter_value_matrices[key])) == 3 :
            if type(baseline_parameter_value_matrices[key]) is np.ma.MaskedArray :
                value = baseline_parameter_value_matrices[key].data[0][r][c]
            else :
                value = baseline_parameter_value_matrices[key][0][r][c]
        else :
            if type(baseline_parameter_value_matrices[key]) is np.ma.MaskedArray :
                value = baseline_parameter_value_matrices[key].data[r][c]
            else :
                value = baseline_parameter_value_matrices[key][r][c]

        # Update selection
        self.parameter_baseline_values['row'][key] = r
        self.parameter_baseline_values['column'][key] = c
        self.parameter_baseline_values['value'][key].set(value_string)
        self.parameter_baseline_values['matrix_value'][key] = value

        # Resolve parameter fields given set via method
        self.parameterSetViaSelection(key, self.parameter_set_via_text[key].get(), selection_made=False)

        # Update current viewed LHS distribution
        if self.current_parameter_lhs_distribution_viewed == key and self.parameterHasValidSettings(key, to_view=True) :
            distr = self.lhs_distribution_selection_text[key].get()
            self.updateLhsDistributionWindow(key, distr, button_pressed=False)

        # Update steps completed
        self.updateStepsCompleted()

    # MP Generation: Step 1 Method: Clear parameter baseline value views
    def clearParameterBaselineValueViews(self) :
        for key in self.config.parameters :
            self.parameter_baseline_values['value'][key].set('   ')
            self.parameter_bounds_baseline_x_label[key].configure(state=tk.NORMAL, width=3)
            self.parameter_lhs_settings_baseline_x_label[key].configure(state=tk.NORMAL, width=3)
            self.clearParameterBaselineValueExpandedView(key)
        self.bounds_baseline_values_outer_frame = {}
        self.lhs_settings_baseline_values_outer_frame = {}

    # MP Generation: Step 1 Method: Clear parameter baseline value views
    def clearParameterBaselineValueExpandedView(self, key) :
        if self.bounds_baseline_values_outer_frame.has_key(key) :
            if self.bounds_baseline_values_outer_frame[key].winfo_children() :
                self.bounds_baseline_values_outer_frame[key].destroy()
            self.bounds_baseline_values_outer_frame.pop(key)
        if self.lhs_settings_baseline_values_outer_frame.has_key(key) :
            if self.lhs_settings_baseline_values_outer_frame[key].winfo_children() :
                self.lhs_settings_baseline_values_outer_frame[key].destroy()
            self.lhs_settings_baseline_values_outer_frame.pop(key)

    # MP Generation: Step 3 Method: Update baseline parameter view
    def updateBaselineParameterView(self, context, button, parameter_key, button_pressed=True) :

        if button_pressed :
            # Shift focus so as to trigger any pending validation warnings
            self.focus_set()
            
            # Exit if validation warning is pending
            if self.validation_warning_pending :
                self.validation_warning_pending = False
                return True
        
        # Swap premade frames
        if button == 'v' : # expand
            self.setParameterBaselineValueExpandedView(parameter_key, context)
            if context == 'bounds' :
                self.parameter_bounds_baseline_v_frame[parameter_key].grid_remove()
                self.parameter_bounds_baseline_x_frame[parameter_key].grid()
            elif context == 'lhs_settings' :
                self.parameter_lhs_settings_baseline_v_frame[parameter_key].grid_remove()
                self.parameter_lhs_settings_baseline_x_frame[parameter_key].grid()
        elif button == 'x' : # contract
            if context == 'bounds' :
                self.parameter_bounds_baseline_x_frame[parameter_key].grid_remove()
                self.parameter_bounds_baseline_v_frame[parameter_key].grid()
            elif context == 'lhs_settings' :
                self.parameter_lhs_settings_baseline_x_frame[parameter_key].grid_remove()
                self.parameter_lhs_settings_baseline_v_frame[parameter_key].grid()
            self.clearParameterBaselineValueExpandedView(parameter_key)

    # MP Generation: Step 3 Method: View LHS distribution
    def viewLhsDistribution(self, parameter_key, distribution, button_pressed=True) :

        if button_pressed :
            # Shift focus so as to trigger any pending validation warnings
            self.focus_set()
            
            # Exit if validation warning is pending
            if self.validation_warning_pending :
                self.validation_warning_pending = False
                return True

            # Set the current parameter LHS distribution viewed
            self.current_parameter_lhs_distribution_viewed = parameter_key

        # Create or update plot window
        if hasattr(self, 'lhs_distribution_window') :
            if self.lhs_distribution_window.children :
                self.lhs_distribution_window.focus_set()
                self.updateLhsDistributionWindow(parameter_key, distribution, button_pressed)
            else :
                self.lhs_distribution_window.destroy()
                self.createLhsDistributionWindow(parameter_key, distribution)
        else :
            self.createLhsDistributionWindow(parameter_key, distribution)        
        
    # MP Generation: Step 3 Method: Create LHS distribution window
    def createLhsDistributionWindow(self, parameter_key, distribution) :

        plot_values = self.getLhsDistributionPlotValues(parameter_key, distribution)

        if plot_values :

            # Create the view LHS distribution window
            self.lhs_distribution_window = tk.Toplevel(self)
            self.lhs_distribution_window.title(distribution + ' distribution for ' + parameter_key)
            self.lhs_distribution_window.transient(self)
            self.lhs_distribution_window.focus_set()

            # Setup plot
            self.lhs_distribution_plot_frame = tk.Frame(self.lhs_distribution_window, padx=0, pady=0)
            self.lhs_distribution_plot_figure = Figure(figsize=(5,2.5), frameon=False, linewidth=10, dpi=100, tight_layout=True)
            self.lhs_distribution_plot_axes = self.lhs_distribution_plot_figure.add_subplot(111)
            self.lhs_distribution_plot_axes.tick_params(labelsize=8)
            self.lhs_distribution_plot_axes.set_yticks([])
            self.lhs_distribution_plot_axes.autoscale(False, 'x')
            self.lhs_distribution_plot_axes.autoscale(False, 'y')
            self.lhs_distribution_plot_canvas = FigureCanvasTkAgg(self.lhs_distribution_plot_figure, master=self.lhs_distribution_plot_frame)
            self.lhs_distribution_plot_canvas.show()
            self.lhs_distribution_plot_canvas.get_tk_widget().grid(row=0, column=0) #.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            self.lhs_distribution_plot_frame.grid(row=0, column=0, padx=0, pady=0)

            # Plot the distribution
            self.lhs_distribution_plot_figure.get_axes().pop().set_xbound(min(plot_values['x_values']), max(plot_values['x_values']))
            self.lhs_distribution_plot_figure.get_axes().pop().set_ybound(0, np.nanmax(plot_values['y_values'])*1.2)
            self.lhs_distribution_plot_figure.get_axes().pop().set_xlabel(self.parameter_set_via_text[parameter_key].get(), fontsize=8)
            self.lhs_distribution_plot_axes.plot(plot_values['x_values'], plot_values['y_values'], 'k')

    # MP Generation: Step 3 Method: Update LHS distribution window
    def updateLhsDistributionWindow(self, parameter_key, distribution, button_pressed) :

        # Handle updates when button not pressed
        update = False
        if not button_pressed : # only update if present
            if hasattr(self, 'lhs_distribution_window') :
                if self.lhs_distribution_window.children :
                    update = True
        else :
            update = True

        # Exit if update not required
        if not update :
            return True

        # Re-plot the distribution
        plot_values = self.getLhsDistributionPlotValues(parameter_key, distribution)
        if plot_values :
            self.lhs_distribution_window.title(distribution + ' distribution for ' + parameter_key)
            self.lhs_distribution_plot_axes.clear()
            self.lhs_distribution_plot_axes.set_yticks([])
            self.lhs_distribution_plot_axes.autoscale(False, 'x')
            self.lhs_distribution_plot_axes.autoscale(False, 'y')
            self.lhs_distribution_plot_axes.set_xbound(min(plot_values['x_values']), max(plot_values['x_values']))
            self.lhs_distribution_plot_axes.set_ybound(0, np.nanmax(plot_values['y_values'])*1.2)
            self.lhs_distribution_plot_axes.set_xlabel(self.parameter_set_via_text[parameter_key].get(), fontsize=8)
            self.lhs_distribution_plot_axes.plot(plot_values['x_values'], plot_values['y_values'], 'k')
            self.lhs_distribution_plot_canvas.draw()

    # MP Generation: Step 3 Method: Get LHS distribution plot values
    def getLhsDistributionPlotValues(self, parameter_key, distribution) :
        
        # Parameter set via ('% of baseline' or 'Selected value')
        if self.parameter_set_via_text[parameter_key].get() == self.parameter_set_via_selection_values[0] :
            lhs_setting_text = self.lhs_setting_text[parameter_key][distribution]
        else :
            lhs_setting_text = self.lhs_setting_selected_value_text[parameter_key][distribution]

        # Gather distribution settings
        distribution_specifications = { 'settings' : {} }
        if distribution == 'Uniform' :
            distribution_specifications['distribution'] = 'uniform'
            distribution_specifications['settings']['lower'] = float(lhs_setting_text['Lower'].get())
            distribution_specifications['settings']['upper'] = float(lhs_setting_text['Upper'].get())
        elif distribution == 'Gaussian' :
            distribution_specifications['distribution'] = 'normal'
            distribution_specifications['settings']['mean'] = float(lhs_setting_text['Mean'].get())
            distribution_specifications['settings']['std_dev'] = float(lhs_setting_text['Std. Dev.'].get())
        elif distribution == 'Triangular' :
            distribution_specifications['distribution'] = 'triangular'
            distribution_specifications['settings']['a'] = float(lhs_setting_text['Lower (a)'].get())
            distribution_specifications['settings']['b'] = float(lhs_setting_text['Upper (b)'].get())
            distribution_specifications['settings']['c'] = float(lhs_setting_text['Mode (c)'].get())
        elif distribution == 'Lognormal' :
            distribution_specifications['distribution'] = 'lognormal'
            distribution_specifications['settings']['lower'] = float(lhs_setting_text['Lower'].get())
            distribution_specifications['settings']['scale'] = float(lhs_setting_text['Scale'].get())
            distribution_specifications['settings']['sigma'] = float(lhs_setting_text['Sigma'].get())
        elif distribution == 'Beta' :
            distribution_specifications['distribution'] = 'beta'
            distribution_specifications['settings']['lower'] = float(lhs_setting_text['Lower'].get())
            distribution_specifications['settings']['upper'] = float(lhs_setting_text['Upper'].get())
            distribution_specifications['settings']['alpha'] = float(lhs_setting_text['Alpha'].get())
            distribution_specifications['settings']['beta'] = float(lhs_setting_text['Beta'].get())

        # Get the plot values
        plot_values = {} # 'x_values', 'y_values'
        sample_generator = SampleGenerator()
        try :
            plot_values = sample_generator.generateDistributionPlotValues(distribution_specifications)
        except Exception, e :
            showerror('Plot Generation Error', 'Could not generate distribution plot values.')
            print >> sys.stderr, 'Error generating distribution plot values:', e

        return plot_values

    # MP Generation: Step 1 Method: Display the Metapop settings from the loaded file
    def displayMpFileSettings(self) :
        if self.mp_file_settings_frame.winfo_children() :
            self.mp_file_settings_frame.destroy()
            self.mp_file_settings_frame = tk.Frame(self.file_load_frame)
            self.mp_file_settings_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NW+tk.SE, padx=0, pady=5)
        tk.Label(self.mp_file_settings_frame, text='Loaded baseline settings:').grid(row=0, column=0, columnspan=3, sticky=tk.NW+tk.SW, padx=0, pady=0)
        tk.Label(self.mp_file_settings_frame, text='').grid(row=1, column=0, padx=3, pady=0)
        tk.Label(self.mp_file_settings_frame, text='Iterations per scenario (replications):').grid(row=1, column=1, sticky=tk.NW+tk.SW, padx=4, pady=0)
        tk.Label(self.mp_file_settings_frame, text=str(int(self.mp_file_helper.getAdditionalParameterValue('Replications')))).grid(row=1, column=2, sticky=tk.NW+tk.SW, padx=0, pady=0)
        tk.Label(self.mp_file_settings_frame, text='').grid(row=2, column=0, padx=3, pady=0)
        tk.Label(self.mp_file_settings_frame, text='Simulation duration:').grid(row=2, column=1, sticky=tk.NW+tk.SW, padx=4, pady=0)
        tk.Label(self.mp_file_settings_frame, text=str(int(self.mp_file_helper.getAdditionalParameterValue('Duration')))).grid(row=2, column=2, sticky=tk.NW+tk.SW, padx=0, pady=0)
        tk.Label(self.mp_file_settings_frame, text='').grid(row=3, column=0, padx=3, pady=0)
        tk.Label(self.mp_file_settings_frame, text='Number of subpopulations:').grid(row=3, column=1, sticky=tk.NW+tk.SW, padx=4, pady=0)
        tk.Label(self.mp_file_settings_frame, text=str(int(self.mp_file_helper.getAdditionalParameterValue('Populations')))).grid(row=3, column=2, sticky=tk.NW+tk.SW, padx=0, pady=0)
        tk.Label(self.mp_file_settings_frame, text='').grid(row=4, column=0, padx=3, pady=0)
        tk.Label(self.mp_file_settings_frame, text='Density dependence:').grid(row=4, column=1, sticky=tk.NW+tk.SW, padx=4, pady=0)
        tk.Label(self.mp_file_settings_frame, text=self.mp_file_helper.getAdditionalParameterValue('Density dependence')).grid(row=4, column=2, sticky=tk.NW+tk.SW, padx=0, pady=0)
        tk.Label(self.mp_file_settings_frame, text='').grid(row=5, column=0, padx=3, pady=0)
        tk.Label(self.mp_file_settings_frame, text='Number of stages:').grid(row=5, column=1, sticky=tk.NW+tk.SW, padx=4, pady=0)
        tk.Label(self.mp_file_settings_frame, text=str(int(self.mp_file_helper.getAdditionalParameterValue('Stages')))).grid(row=5, column=2, sticky=tk.NW+tk.SW, padx=0, pady=0)

    # MP Generation: Step 2 Method: Enable/disable number of samples and any corresponding subtype selections when sampling types are selected/unselected
    def updateSamplingType(self, selection_made=True) :
        default_options_mapping = { 'Latin Hypercube' : 'default_number_of_lhs_samples',
                                    'Random' : 'default_number_of_random_samples' }
        # Place focus on checkbox
        self.sampling_type_radiobutton[self.selected_sampling_type.get()].focus_set()
        
        # Exit if validation warning is pending
        if self.validation_warning_pending :
            self.selected_sampling_type.set(self.current_sampling_type)
            self.validation_warning_pending = False
            return True

        # Update sampling settings
        if (self.selected_sampling_type.get() != self.current_sampling_type) or (not selection_made) :
            self.current_sampling_type = self.selected_sampling_type.get()
            for key, details in self.sampling_details.items() :
                if key == self.selected_sampling_type.get() :
                    if details['sample_number_required'] :
                        default_sample_number = self.config.getToolOptions([default_options_mapping[key]])[default_options_mapping[key]]
                        if default_sample_number :
                            enforce_minimum_number_of_samples = self.config.getToolOptions(['enforce_minimum_number_of_samples'])['enforce_minimum_number_of_samples']
                            if enforce_minimum_number_of_samples and (default_sample_number < self.config.minimum_number_of_samples) :
                                default_str = str(self.config.minimum_number_of_samples)
                            else :
                                default_str = str(default_sample_number)
                        else :
                            default_str = ''
                        self.sampling_details[key]['sample_number'].set(default_str)
                        self.sample_number_entry[key].configure(state=tk.NORMAL)
                else :
                    if details['sample_number_required'] :
                        self.sampling_details[key]['sample_number'].set('')
                        self.sample_number_entry[key].configure(state=tk.DISABLED)
            self.updateSamplingFrame(selection_made=selection_made, reset=True)

    # MP Generation: Step 2 Method: Alter parameter settings display based upon sampling type selection
    def updateSamplingFrame(self, selection_made=False, reset=True) :

        # Get the sampling type and subtype (if it exists)
        sampling_type = self.selected_sampling_type.get()
        
        if reset : # option set or first load or previous load failed

            # Hide the current parameter frame child if it exists
            if self.parameter_frame.grid_slaves() :
                self.parameter_frame.grid_slaves().pop().grid_forget()

            # Populate the parameter frame with appropriate contents
            if sampling_type == 'Latin Hypercube' :
                self.parameter_lhs_settings_frame.grid(row=0, column=0)
            else :
                self.parameter_bounds_frame.grid(row=0, column=0)

            # Deselect any selected parameters
            for key, parameter_selected in self.modify_parameter.items() :
                if parameter_selected.get() :

                    parameter_selected.set(0)

                    # Return parameter view to single field and disable 'v' button
                    self.updateBaselineParameterView('bounds', 'x', key, button_pressed=False)
                    self.parameter_bounds_baseline_x_label[key].configure(bg='SystemButtonFace')
                    self.parameter_bounds_baseline_v_button[key].configure(state=tk.DISABLED)
                    self.updateBaselineParameterView('lhs_settings', 'x', key, button_pressed=False)
                    self.parameter_lhs_settings_baseline_x_label[key].configure(bg='SystemButtonFace')
                    self.parameter_lhs_settings_baseline_v_button[key].configure(state=tk.DISABLED)

                    # Return distribution selection to first in list and disable selection
                    self.parameterLHSDistributionSelection(key, self.config.lhs_distributions[0], selection_made=False)
                    self.lhs_distribution_selection_menu[key].config(state=tk.DISABLED)

                    # Return set via to '% of baseline' 
                    self.parameter_set_via_text[key].set(self.parameter_set_via_selection_values[0])
                    self.parameterSetViaSelection(key, self.parameter_set_via_selection_values[0], selection_made=False)
                    self.parameter_bounds_set_via_selection_menu[key].configure(state=tk.DISABLED)
                    self.parameter_lhs_settings_set_via_selection_menu[key].configure(state=tk.DISABLED)

                    # Clear and disable entry fields
                    self.sample_bound_text[key].set('')
                    self.sample_bound_entry[key].configure(state=tk.DISABLED)
                    self.sample_bound_selected_value_text[key].set('')
                    self.sample_bound_selected_value_entry[key].configure(state=tk.DISABLED)
                    for distr in self.config.lhs_distributions :
                        self.lhs_view_distribution_button[key][distr].configure(state=tk.DISABLED)
                        for setting in self.config.lhs_distribution_settings[distr] :
                            self.lhs_setting_text[key][distr][setting['name']].set('')
                            self.lhs_setting_previous_text[key][distr][setting['name']] = ''
                            self.lhs_setting_entry[key][distr][setting['name']].configure(state=tk.DISABLED)
                            self.lhs_setting_selected_value_text[key][distr][setting['name']].set('')
                            self.lhs_setting_selected_value_previous_text[key][distr][setting['name']] = ''
                            self.lhs_setting_selected_value_entry[key][distr][setting['name']].configure(state=tk.DISABLED)

        else : # keep the selected parameters when they are extracted from another baseline file

            for key, parameter_selected in self.modify_parameter.items() :
                if parameter_selected.get() :

                    # Return parameter view to single field
                    self.updateBaselineParameterView('bounds', 'x', key, button_pressed=False)
                    self.updateBaselineParameterView('lhs_settings', 'x', key, button_pressed=False)

                    # Resolve selected value parameters when appropriate
                    self.parameterSetViaSelection(key, self.parameter_set_via_text[key].get(), selection_made=False)

                    # Run constraint checks when extracted
                    key_present = (key in self.baseline_parameter_values['extracted'].keys())
                    if key_present :
                        if sampling_type == 'Random' or sampling_type == 'Full Factorial' :
                            self.validateParameterBounds(self.sample_bound_text[key].get(), 'focusout', key)
                        elif sampling_type == 'Latin Hypercube' :
                            distr = self.lhs_distribution_selection_text[key].get()
                            for setting in self.config.lhs_distribution_settings[distr] :
                                self.validateParameterLHSSettings(self.lhs_setting_text[key][distr][setting['name']].get(), 'focusout', key, distr, setting['name'], update_call=True)
            
        self.updateStepsCompleted()

    # MP Generation: Step 3 Method: Add focus to selection and update settings for parameter bounds selection
    def parameterBoundsSelection(self, key) :

        # Place focus on checkbox
        self.parameter_checkbox_bound[key].focus_set()

        # Exit if validation warning is pending
        if self.validation_warning_pending :
            self.modify_parameter[key].set(int(not bool(self.modify_parameter[key].get())))
            self.validation_warning_pending = False
            return True

        self.updateParameterSettings(key)

    # MP Generation: Step 3 Method: Update settings for parameter lhs settings selection
    def parameterLHSSettingsSelection(self, key) :

        # Place focus on checkbox
        self.parameter_checkbox_lhs_settings[key].focus_set()

        # Exit if validation warning is pending
        if self.validation_warning_pending :
            self.modify_parameter[key].set(int(not bool(self.modify_parameter[key].get())))
            self.validation_warning_pending = False
            return True

        self.updateParameterSettings(key)

    # MP Generation: Step 3 Method: Enable/disable and set default parameter settings when parameters are selected/unselected
    def updateParameterSettings(self, key) :
        parameter_selected = self.modify_parameter[key]
        if parameter_selected.get() :
            tool_options = self.config.getToolOptions()
            if self.selected_sampling_type.get() == 'Random' or self.selected_sampling_type.get() == 'Full Factorial' :
                self.parameter_bounds_set_via_selection_menu[key].configure(state=tk.NORMAL)
                if self.parameter_baseline_values['highlight'][key] :
                    self.parameter_bounds_baseline_x_label[key].configure(bg='white', state=tk.NORMAL)
                else :
                    self.parameter_bounds_baseline_x_label[key].configure(bg='SystemButtonFace', state=tk.DISABLED)
                self.parameter_bounds_baseline_v_button[key].configure(state=tk.NORMAL)
                self.sample_bound_entry[key].configure(state=tk.NORMAL)
                self.sample_bound_selected_value_entry[key].configure(state=tk.NORMAL)
                if self.selected_sampling_type.get() == 'Random' :
                    default_sample_bounds = tool_options['default_sample_bounds_for_random']
                elif self.selected_sampling_type.get() == 'Full Factorial' :
                    default_sample_bounds = tool_options['default_sample_bounds_for_full_factorial']
                if default_sample_bounds :
                    default_str = str(default_sample_bounds)
                else :
                    default_str = ''
                self.sample_bound_text[key].set(default_str)
                self.validateParameterBounds(default_str, 'focusout', key)
            elif self.selected_sampling_type.get() == 'Latin Hypercube' :
                if self.parameter_baseline_values['highlight'][key] :
                    self.parameter_lhs_settings_baseline_x_label[key].configure(bg='white', state=tk.NORMAL)
                else :
                    self.parameter_lhs_settings_baseline_x_label[key].configure(bg='SystemButtonFace', state=tk.DISABLED)
                self.parameter_lhs_settings_baseline_v_button[key].configure(state=tk.NORMAL)
                self.lhs_distribution_selection_menu[key].config(state=tk.NORMAL)
                self.parameter_lhs_settings_set_via_selection_menu[key].configure(state=tk.NORMAL)
                for distr in self.config.lhs_distributions :
                    self.lhs_view_distribution_button[key][distr].configure(state=tk.NORMAL)
                    for setting in self.config.lhs_distribution_settings[distr] :
                        self.lhs_setting_entry[key][distr][setting['name']].configure(state=tk.NORMAL)
                        self.lhs_setting_selected_value_entry[key][distr][setting['name']].configure(state=tk.NORMAL)
                        default_lhs_setting = tool_options[self.config.lhs_option_default_settings[distr][setting['name']]]
                        if default_lhs_setting :
                            default_str = str(default_lhs_setting)
                        else :
                            default_str = ''
                        self.lhs_setting_text[key][distr][setting['name']].set(default_str)
                        self.lhs_setting_previous_text[key][distr][setting['name']] = default_str
                        if self.config.lhs_option_default_settings[distr].has_key(setting['name']+' Increment') :
                            entry_increment = tool_options[self.config.lhs_option_default_settings[distr][setting['name']+' Increment']]
                            if entry_increment :
                                self.lhs_setting_entry[key][distr][setting['name']].configure(from_=entry_increment, to=1000, increment=entry_increment)
                        if self.lhs_distribution_selection_text[key].get() == distr and not self.warning_shown_for_update_validation :
                            self.validateParameterLHSSettings(default_str, 'focusout', key, distr, setting['name'], update_call=True)
                    self.warning_shown_for_update_validation = False
                # Set default distribution
                self.parameterLHSDistributionSelection(key, self.config.parameter_includes_lhs_distributions[key][0], selection_made=False)
        else :

                # Return parameter view to single field and disable 'v' button
                self.updateBaselineParameterView('bounds', 'x', key, button_pressed=False)
                self.parameter_bounds_baseline_x_label[key].configure(bg='SystemButtonFace')
                self.parameter_bounds_baseline_v_button[key].configure(state=tk.DISABLED)
                self.updateBaselineParameterView('lhs_settings', 'x', key, button_pressed=False)
                self.parameter_lhs_settings_baseline_x_label[key].configure(bg='SystemButtonFace')
                self.parameter_lhs_settings_baseline_v_button[key].configure(state=tk.DISABLED)

                # Return distribution selection to first in list and disable selection
                self.parameterLHSDistributionSelection(key, self.config.lhs_distributions[0], selection_made=False)
                self.lhs_distribution_selection_menu[key].config(state=tk.DISABLED)

                # Return set via to '% of baseline'
                self.parameter_set_via_text[key].set(self.parameter_set_via_selection_values[0])
                self.parameterSetViaSelection(key, self.parameter_set_via_selection_values[0], selection_made=False)
                self.parameter_bounds_set_via_selection_menu[key].configure(state=tk.DISABLED)
                self.parameter_lhs_settings_set_via_selection_menu[key].configure(state=tk.DISABLED)

                # Clear and disable entry fields
                self.sample_bound_text[key].set('')
                self.sample_bound_entry[key].configure(state=tk.DISABLED)
                self.sample_bound_selected_value_text[key].set('')
                self.sample_bound_selected_value_entry[key].configure(state=tk.DISABLED)
                for distr in self.config.lhs_distributions :
                    for setting in self.config.lhs_distribution_settings[distr] :
                        self.lhs_setting_text[key][distr][setting['name']].set('')
                        self.lhs_setting_previous_text[key][distr][setting['name']] = ''
                        self.lhs_setting_entry[key][distr][setting['name']].configure(state=tk.DISABLED)
                        self.lhs_setting_selected_value_text[key][distr][setting['name']].set('')
                        self.lhs_setting_selected_value_previous_text[key][distr][setting['name']] = ''
                        self.lhs_setting_selected_value_entry[key][distr][setting['name']].configure(state=tk.DISABLED)
                    # And view distibution button
                    self.lhs_view_distribution_button[key][distr].configure(state=tk.DISABLED)
                # Remove LHS distribution view window if present
                if self.current_parameter_lhs_distribution_viewed == key :
                    if hasattr(self, 'lhs_distribution_window') :
                        self.lhs_distribution_window.destroy()

        self.updateStepsCompleted()

    # MP Generation: Step 3 Method: Alter parameter settings display based upon sampling subtype selection
    def parameterLHSDistributionSelection(self, key, distr, selection_made=True) :

        self.lhs_distribution_selection_text[key].set(distr) # needed as OptionMenu menu item commands have been overridden

        # Update settings for distribution if changed
        if distr != self.lhs_current_displayed_distribution[key] :
            
            # Remove existing settings from grid
            for setting in self.lhs_distribution_settings[key][self.lhs_current_displayed_distribution[key]] :
                setting['element'].grid_remove()
                if setting.has_key('selected_value_element') :
                    setting['selected_value_element'].grid_remove()
            self.lhs_view_distribution_button[key][self.lhs_current_displayed_distribution[key]].grid_remove()

            # Add new settings to the grid
            for setting in self.lhs_distribution_settings[key][distr] :
                distr_setting = self.config.lhs_distribution_settings[distr]
                if setting.has_key('selected_value_element') :
                    if self.parameter_set_via_text[key].get() == self.parameter_set_via_selection_values[0] :
                        setting['element'].grid()
                    else :
                        setting['selected_value_element'].grid()
                else :
                    setting['element'].grid()
            self.lhs_view_distribution_button[key][distr].grid()

            # Update current displayed distribution
            self.lhs_current_displayed_distribution[key] = distr

            # Resolve parameter settings given set via method
            self.parameterSetViaSelection(key, self.parameter_set_via_text[key].get(), selection_made=False)

        if selection_made :

            # Validate defaults if any
            for setting in self.config.lhs_distribution_settings[distr] :
                current_value = self.lhs_setting_text[key][distr][setting['name']].get()
                if current_value and not self.warning_shown_for_update_validation :
                    self.validateParameterLHSSettings(current_value, 'focusout', key, distr, setting['name'], update_call=True)
            self.warning_shown_for_update_validation = False

            # Update current viewed LHS distribution
            if self.current_parameter_lhs_distribution_viewed == key  and self.parameterHasValidSettings(key, to_view=True) :
                self.updateLhsDistributionWindow(key, distr, button_pressed=False)

            # Update steps completed
            self.updateStepsCompleted()

            # Shift focus
            self.focus_set()

    # MP Generation: Step 3 Method: Alter parameter settings display based upon set via method selection
    def parameterSetViaSelection(self, key, set_via, selection_made=True) :

        self.parameter_set_via_text[key].set(set_via) # needed as OptionMenu menu item commands have been overridden

        if set_via == self.parameter_set_via_selection_values[0] : # % of baseline

            # Swap bound entry and update postfix
            self.sample_bound_selected_value_entry[key].grid_remove()
            self.sample_bound_entry[key].grid()
            self.sample_bound_postfix_text[key].set('%')

            # Swap LHS entries and update postfixes
            distr = self.lhs_distribution_selection_text[key].get()
            for distr_setting in self.config.lhs_distribution_settings[distr] :
                self.lhs_setting_selected_value_entry[key][distr][distr_setting['name']].grid_remove()
                self.lhs_setting_entry[key][distr][distr_setting['name']].grid()
                self.lhs_setting_postfix_text[key][distr][distr_setting['name']].set(distr_setting['postfix'])
            
        else : # Selected value
            
            # Swap bound entry, update postfix, and calculate value
            self.sample_bound_entry[key].grid_remove()
            self.sample_bound_selected_value_entry[key].grid()
            self.sample_bound_postfix_text[key].set('')
            if self.parameter_baseline_values['matrix_value'].has_key(key) :
                if self.isFloat(self.sample_bound_text[key].get()) :
                    calculated_value = self.parameter_baseline_values['matrix_value'][key]*float(self.sample_bound_text[key].get())/100
                    # Convert parameters to other types (default is float)
                    if self.config.parameter_data_types.has_key(key) :
                        if self.config.parameter_data_types[key] == 'integer' :
                            calculated_value = calculated_value.round().astype(int)
                    # Convert value to a formatted string
                    value_string = str(calculated_value)
                    self.sample_bound_selected_value_text[key].set(value_string)

            # Swap LHS entries, update postfixes, and calculate values
            distr = self.lhs_distribution_selection_text[key].get()
            tool_options = self.config.getToolOptions()
            for distr_setting in self.config.lhs_distribution_settings[distr] :
                self.lhs_setting_entry[key][distr][distr_setting['name']].grid_remove()
                self.lhs_setting_selected_value_entry[key][distr][distr_setting['name']].grid()
                if distr_setting['postfix'] == '%' :
                    self.lhs_setting_postfix_text[key][distr][distr_setting['name']].set('')
                    if self.parameter_baseline_values['matrix_value'].has_key(key) :
                        if self.isFloat(self.lhs_setting_text[key][distr][distr_setting['name']].get()) :
                            calculated_value = self.parameter_baseline_values['matrix_value'][key]*float(self.lhs_setting_text[key][distr][distr_setting['name']].get())/100
                            # Convert lower and upper parameters to other types (default is float)
                            if self.config.parameter_data_types.has_key(key) :
                                if self.config.parameter_data_types[key] == 'integer' and (distr_setting['name'].find('Lower') >= 0 or distr_setting['name'].find('Upper') >= 0) :
                                    calculated_value = calculated_value.round().astype(int)
                            value_string = str(calculated_value)
                            self.lhs_setting_selected_value_text[key][distr][distr_setting['name']].set(value_string)
                            self.lhs_setting_selected_value_previous_text[key][distr][distr_setting['name']] = value_string
                            if self.config.lhs_option_default_settings[distr].has_key(distr_setting['name']+' Increment') :
                                entry_increment = tool_options[self.config.lhs_option_default_settings[distr][distr_setting['name']+' Increment']]
                                if entry_increment :
                                    calculated_increment = self.parameter_baseline_values['matrix_value'][key]*entry_increment/100
                                    from_value = calculated_increment
                                    self.lhs_setting_selected_value_entry[key][distr][distr_setting['name']].configure(from_=calculated_increment, to=1000, increment=calculated_increment)
                                    if calculated_value == 0 :
                                        self.lhs_setting_selected_value_text[key][distr][distr_setting['name']].set(value_string)
                else :
                    self.lhs_setting_selected_value_text[key][distr][distr_setting['name']].set(self.lhs_setting_text[key][distr][distr_setting['name']].get())
                    self.lhs_setting_selected_value_previous_text[key][distr][distr_setting['name']] = self.lhs_setting_text[key][distr][distr_setting['name']].get()
                    if self.config.lhs_option_default_settings[distr].has_key(distr_setting['name']+' Increment') :
                        entry_increment = tool_options[self.config.lhs_option_default_settings[distr][distr_setting['name']+' Increment']]
                        if entry_increment :
                            self.lhs_setting_selected_value_entry[key][distr][distr_setting['name']].configure(from_=entry_increment, to=1000, increment=entry_increment)

        if selection_made :

            # Update current viewed LHS distribution
            if self.current_parameter_lhs_distribution_viewed == key and self.parameterHasValidSettings(key, to_view=True) :
                self.updateLhsDistributionWindow(key, distr, button_pressed=False)

            # Update steps completed
            self.updateStepsCompleted()

            # Shift focus
            self.focus_set()

    # MP Generation: Step 4 Method: Update Generation Settings
    def updateGenerationSettings(self) :

        # Place focus on checkbox
        self.generate_use_mp_baseline_values_checkbox.focus_set()

        # Exit if validation warning is pending
        if self.validation_warning_pending :
            self.generate_use_mp_baseline_values.set(int(not bool(self.generate_use_mp_baseline_values.get())))
            self.validation_warning_pending = False
            return True

        # Update settings
        tool_option_values = self.config.getToolOptions()
        self.generate_metapop_iterations.set('_')
        self.generate_metapop_duration.set('_')
        if self.generate_use_mp_baseline_values.get() :
            self.generate_settings_uses_text.set('MP generation uses baseline settings:')
            if self.extraction_ok :
                self.generate_metapop_iterations.set(int(self.mp_file_helper.getAdditionalParameterValue('Replications')))
                self.generate_metapop_duration.set(int(self.mp_file_helper.getAdditionalParameterValue('Duration')))
        else :
            self.generate_settings_uses_text.set('MP generation uses option settings:')
            if tool_option_values['number_of_metapop_iterations'] :
                self.generate_metapop_iterations.set(tool_option_values['number_of_metapop_iterations'])
            if tool_option_values['metapop_simulation_duration'] :
                self.generate_metapop_duration.set(tool_option_values['metapop_simulation_duration'])

        # Update workflow status
        self.updateStepsCompleted()

    #  MP Generation: Step 4 Method: Duration altered with temporal trends
    def durationAlteredWithTemporalTrends(self) :
        if not self.generate_use_mp_baseline_values.get() :
            tool_option_values = self.config.getToolOptions()
            if self.isPositiveInteger(tool_option_values['metapop_simulation_duration']) :
                if self.mp_file_helper.getAdditionalParameterValue('Duration') :
                    if int(self.mp_file_helper.getAdditionalParameterValue('Duration')) != tool_option_values['metapop_simulation_duration'] :
                        for parameter_key, file_links in self.baseline_parameter_values['file_links'].items() :
                            if self.modify_parameter[parameter_key].get() :
                                if file_links.has_key('file_contents') and file_links['file_contents'] :
                                    return True
        return False

    #  MP Generation: Step 4 Method: Autorun results summary selected
    def autorunResultsSummarySelected(self) :
        
        # Place focus on load button
        self.auto_run_results_summary_checkbox.focus_set()

        # Revert selection if validation warning is pending
        if self.validation_warning_pending :
            self.auto_run_results_summary.set(int(not bool(self.auto_run_results_summary.get())))
            self.validation_warning_pending = False

    # MP Generation: Step 4 Method: Generate sampling files
    def generateFiles(self) :

        # Place focus on load button
        self.generate_button.focus_set()

        # Exit if validation warning is pending
        if self.validation_warning_pending :
            self.validation_warning_pending = False
            return True
        
        # Get the sampling details including the type, subtype (if it exists), and the number of samples if required
        sampling_type = self.selected_sampling_type.get()
        sample_number = 1
        sampling_details = self.sampling_details[sampling_type]
        if sampling_details['sample_number_required'] :
            sample_number_text = sampling_details['sample_number'].get()
            try :
                sample_number = int(sample_number_text)
            except Exception, e :
                showerror('Float Error', 'Sample number for '+sampling_type+': '+sample_number_text+' not an integer')

        # Gather the selected parameters to be modified in the desired order
        selected_parameters = []
        for parameter in self.config.parameters :
            if self.modify_parameter[parameter].get() :
                selected_parameters.append(parameter)

        # Reset file helper generation functionality
        self.mp_file_helper.reset_sampling_generation()

        # Reset the generation directory to its parent if it is timestamped
        if self.generate_directory.has_key('timestamped') and self.generate_directory['timestamped'] :
            self.generate_directory = self.mp_file_helper.splitPath(self.generate_directory['directory'])

        # Initialise generated file count
        self.generated_file_count = 0

        # Set the file output directory
        self.mp_file_helper.setOutputDirectory(self.generate_directory['path'])

        # Check if the output directory is empty, if not then generate a time-stamped directory
        if not self.mp_file_helper.outputDirectoryIsEmpty() :
            self.generate_directory = self.mp_file_helper.generateTimestampedOutputDirectory()

        # Create a generation template
        template_generation_ok = True
        template_save_file = None
        if DEBUG :
            template_save_file = 'template.txt'
            self.generated_file_count += 1
        try :
            if not self.generate_use_mp_baseline_values.get() :
                modified_settings = { 'Replications' : eval(self.generate_metapop_iterations.get()),
                                      'Duration' : eval(self.generate_metapop_duration.get()) }
                self.mp_file_helper.modifyAdditionalParameterValues(modified_settings)
            self.mp_file_helper.createGenerationTemplate(selected_parameters, template_save_file)
        except Exception, e :
            showerror('Template Creation Error', 'Error creating template: '+str(e))
            print >> sys.stderr, 'Error creating MP template:', e
            template_generation_ok = False

        # Compile parameter sampling specifications
        sampling_specifications = {}
        for parameter_key in selected_parameters :
            sampling_specifications[parameter_key] = {}
            if sampling_type == 'Latin Hypercube' :
                distribution = self.lhs_distribution_selection_text[parameter_key].get()
                sampling_specifications[parameter_key]['settings'] = {}
                if distribution == 'Uniform' :
                    lower_text = self.lhs_setting_text[parameter_key][distribution]['Lower'].get()
                    upper_text = self.lhs_setting_text[parameter_key][distribution]['Upper'].get()
                    sampling_specifications[parameter_key]['distribution'] = 'uniform'
                    sampling_specifications[parameter_key]['settings']['lower'] = float(lower_text)/100 # was %
                    sampling_specifications[parameter_key]['settings']['upper'] = float(upper_text)/100 # was %
                elif distribution == 'Gaussian' :
                    mean_text = self.lhs_setting_text[parameter_key][distribution]['Mean'].get()
                    stdev_text = self.lhs_setting_text[parameter_key][distribution]['Std. Dev.'].get()
                    sampling_specifications[parameter_key]['distribution'] = 'normal'
                    sampling_specifications[parameter_key]['settings']['mean'] = float(mean_text)/100 # was %
                    sampling_specifications[parameter_key]['settings']['std_dev'] = float(stdev_text)/100 # was %
                elif distribution == 'Triangular' :
                    lower_a_text = self.lhs_setting_text[parameter_key][distribution]['Lower (a)'].get()
                    upper_b_text = self.lhs_setting_text[parameter_key][distribution]['Upper (b)'].get()
                    mode_c_text = self.lhs_setting_text[parameter_key][distribution]['Mode (c)'].get()
                    sampling_specifications[parameter_key]['distribution'] = 'triangular'
                    sampling_specifications[parameter_key]['settings']['a'] = float(lower_a_text)/100 # was %
                    sampling_specifications[parameter_key]['settings']['b'] = float(upper_b_text)/100 # was %
                    sampling_specifications[parameter_key]['settings']['c'] = float(mode_c_text)/100 # was %
                elif distribution == 'Lognormal' :
                    lower_text = self.lhs_setting_text[parameter_key][distribution]['Lower'].get()
                    scale_text = self.lhs_setting_text[parameter_key][distribution]['Scale'].get()
                    sigma_text = self.lhs_setting_text[parameter_key][distribution]['Sigma'].get()
                    sampling_specifications[parameter_key]['distribution'] = 'lognormal'
                    sampling_specifications[parameter_key]['settings']['lower'] = float(lower_text)/100 # was %
                    sampling_specifications[parameter_key]['settings']['scale'] = float(scale_text)/100 # was %
                    sampling_specifications[parameter_key]['settings']['sigma'] = float(sigma_text)
                elif distribution == 'Beta' :
                    lower_text = self.lhs_setting_text[parameter_key][distribution]['Lower'].get()
                    upper_text = self.lhs_setting_text[parameter_key][distribution]['Upper'].get()
                    alpha_text = self.lhs_setting_text[parameter_key][distribution]['Alpha'].get()
                    beta_text = self.lhs_setting_text[parameter_key][distribution]['Beta'].get()
                    sampling_specifications[parameter_key]['distribution'] = 'beta'
                    sampling_specifications[parameter_key]['settings']['lower'] = float(lower_text)/100 # was %
                    sampling_specifications[parameter_key]['settings']['upper'] = float(upper_text)/100 # was %
                    sampling_specifications[parameter_key]['settings']['alpha'] = float(alpha_text)
                    sampling_specifications[parameter_key]['settings']['beta'] = float(beta_text)
            else :
                bound_text = self.sample_bound_text[parameter_key].get()
                sampling_specifications[parameter_key]['bound'] = float(bound_text)/100 # was %

        # Generate sampling multipliers
        sample_generator = SampleGenerator()
        sampled_multipliers = []
        multipliers_ok = True
        try :
            if sampling_type == 'Latin Hypercube' :
                sampled_multipliers = sample_generator.generateLatinHypercubeSampledMultipliers(sampling_specifications, sample_number)
            elif sampling_type == 'Random' :
                sampled_multipliers = sample_generator.generateRandomSampledMultipliers(sampling_specifications, sample_number)
            elif sampling_type == 'Full Factorial' :
                sampled_multipliers = sample_generator.generateFullFactorialMultipliers(sampling_specifications)
        except Exception, e :
            showerror('Sampling Multiplier Error', 'Unknown error generating sampling multipliers.')
            print >> sys.stderr, 'Error generating sampling multipliers:', e
            multipliers_ok = False

        # Compile generation data: used later for cross-referencing with RAMAS Metapop outputs
        generation_data = {}
        generation_data['sampling'] = { 'sampling_type' : sampling_type, 'sampled_multipliers' : sampled_multipliers }
        generation_data['parameters'] = { 'selected' : selected_parameters, 'baseline_values' : self.baseline_parameter_values }
        generation_data['generate_directory'] = self.generate_directory
        generation_data['file_generation_numbering_format'] = self.config.file_generation_numbering_format # in case format config is changed
        generation_data['samples'] = []

        # Use the sampled multipliers to generate modified parameter values and write them to an MP file and a data frame entry
        if self.extraction_ok and template_generation_ok and multipliers_ok :
            try :
                for index, multipliers in enumerate(sampled_multipliers) :

                    # Generate modified parameter extracted and calculated values using the multipliers
                    extracted_parameter_values = self.getBaselineParameterMatrices(use_calculated=False, adjust_diagonal_only_matrices=False)
                    modified_extracted_parameter_values = sample_generator.multipy(extracted_parameter_values, multipliers, self.config.parameter_data_types)
                    multipliers_for_calculated_values = {}
                    for parameter_key in self.baseline_parameter_values['calculated'].keys() :
                        if multipliers.has_key(parameter_key) :
                            multipliers_for_calculated_values[parameter_key] = multipliers[parameter_key]
                    modified_calculated_parameter_values = sample_generator.multipy(self.baseline_parameter_values['calculated'], multipliers_for_calculated_values, self.config.parameter_data_types)

                    # Generate modified linked file contents using the multipliers
                    linked_file_contents = {}
                    linked_file_multipliers = {}
                    for parameter_key, file_links in self.baseline_parameter_values['file_links'].items() :
                        if multipliers.has_key(parameter_key) :
                            linked_file_contents[parameter_key] = {}
                            linked_file_multipliers[parameter_key] = multipliers[parameter_key]
                            for filename, contents in file_links['file_contents'].items() :
                                linked_file_contents[parameter_key][filename] = contents.get_values()
                    modified_linked_file_contents = sample_generator.multipy(linked_file_contents, linked_file_multipliers, self.config.parameter_data_types)

                    # Generate modified MP file
                    generated_mp_file_name = self.mp_file_helper.generateModifiedMpFile(modified_extracted_parameter_values, index+1)
                    self.generated_file_count += 1

                    # Generate modified linked files
                    generated_linked_files = self.mp_file_helper.generateModifiedLinkedFiles(modified_linked_file_contents, index+1)
                    self.generated_file_count += len(generated_linked_files)

                    # Generate data frame entry from modified value matrices
                    modified_parameter_value_matrices = modified_extracted_parameter_values.copy()
                    for parameter_key, modified_calculated_value in modified_calculated_parameter_values.items() :
                        modified_parameter_value_matrices[parameter_key] = modified_calculated_value
                    data_frame_entry_details = self.mp_file_helper.generateDataFrameEntry(generated_mp_file_name, modified_parameter_value_matrices, multipliers)

                    # Generate MP batch entry
                    self.mp_file_helper.generateMpBatchEntry(generated_mp_file_name, index+1)

                    # Add sample entry to generation data
                    generation_data['samples'].append({ 'sample_number' : index+1, 'multipliers' : multipliers, 'generated_mp_file_name' : generated_mp_file_name, 'data_frame_entry_details' : data_frame_entry_details })

                # Copy other linked files
                copied_linked_files = self.mp_file_helper.copyUnmodifiedLinkedFiles()
                self.generated_file_count += len(copied_linked_files)

                # Generate data frame file
                self.mp_file_helper.generateDataFrameFile()
                self.generated_file_count += 1

                # Generate MP batch file
                self.mp_file_helper.generateMpBatchFile(DEBUG)
                self.generated_file_count += 1

                # Save generation data
                self.mp_file_helper.saveGenerationData(generation_data)
                self.generated_file_count += 1

                # Flag completion and update workflow status
                self.file_generate_complete = True

            except Exception, e :
                showerror('File Generation Error', 'Could not generate files: '+str(e))
                print >> sys.stderr, 'Error generating files:', e
                self.file_generate_error = True
        else :
            self.file_generate_error = True

        # Update workflow status
        self.updateStepsCompleted()

        # Auto run results summary tool
        if self.auto_run_results_summary.get() :

            # Run generated batch file
            self.runBatch(path.join(self.generate_directory['path'], 'mp_batch.bat'))

            # Run results summary tool
            self.after_idle(lambda: self.runResultsSummaryTool())

    # MP Generation: Step 4 Method: (Auto) Run results summary tool
    def runResultsSummaryTool(self) :

        # Run results summary
        self.runResults()

        # Load the results
        self.showResultsAvailablePlots(False)
        result_sets_loaded = {}
        self.results_directory = self.mp_file_helper.splitPath(self.generate_directory['path'])
        try :
            self.mp_file_helper.reset_result_load()
            result_load_details = self.mp_file_helper.loadMpResults(self.results_directory['path'])
            result_sets_loaded = result_load_details['result_sets_loaded']
            warnings = result_load_details['warnings']
            if warnings :
                showwarning('Results Warning', warnings.pop())
            if result_sets_loaded :
                self.results_directory_label_text.set(' : ' + str(result_sets_loaded) + ' result sets loaded from ' + self.results_directory['name'])
            else :
                self.results_directory_label_text.set(' : Select the directory containing the MP results')
        except Exception, e :
            showerror('Results Load Error', 'Error loading the MP results: '+str(e))
            print >> sys.stderr, 'Error loading the MP results:', e
            self.results_directory_label_text.set(' : Error loading the MP results')

        # Update workflow status
        self.updateResultsStepsCompleted()

        if result_sets_loaded :

            # Select all results
            for key in self.config.metapop_results :
                self.result_selected[key].set(1)
        
            # Generate results summary
            self.generateResultsSummary()

    # MP Results: Step 1 Method: Load results directory
    def loadResultsDirectory(self) :

        # Place focus on results directory button
        self.results_directory_button.focus_set()

        # Use existing MP generation directory if it exists
        initial_directory = getcwd()
        tool_option_values = self.config.getToolOptions()
        if self.generate_directory.has_key('path') :
            initial_directory = self.generate_directory['path']
        elif tool_option_values['default_generated_file_location'] and path.exists(tool_option_values['default_generated_file_location']) :
            initial_directory = tool_option_values['default_generated_file_location']
        elif path.exists(environ['USERPROFILE']) :
            initial_directory = environ['USERPROFILE']
        
        # Open file selection dialog
        results_directory_path = askdirectory(title='Select the directory containing the MP results', initialdir=initial_directory)

        if results_directory_path : # Directory selected

            self.showResultsAvailablePlots(False)

            # Split directory into path, parent directory, and name
            self.results_directory = self.mp_file_helper.splitPath(results_directory_path)

            # Load the results using the file helper
            try :
                self.mp_file_helper.reset_result_load()
                result_load_details = self.mp_file_helper.loadMpResults(results_directory_path)
                result_sets_loaded = result_load_details['result_sets_loaded']
                warnings = result_load_details['warnings']
                if warnings :
                    showwarning('Results Warning', warnings.pop())
                if result_sets_loaded :
                    self.results_directory_label_text.set(' : ' + str(result_sets_loaded) + ' result sets loaded from ' + self.results_directory['name'])
                else :
                    self.results_directory_label_text.set(' : Select the directory containing the MP results')
            except Exception, e :
                showerror('Results Load Error', 'Error loading the MP results: '+str(e))
                print >> sys.stderr, 'Error loading the MP results:', e
                self.results_directory_label_text.set(' : Error loading the MP results')

        # Update workflow status
        self.updateResultsStepsCompleted()

    # MP Results: Step 2 Method: Add focus to selection and update workflow status
    def resultsSelection(self, result) :
        self.results_selection_checkbox[result].focus_set()
        self.updateResultsStepsCompleted()

    # MP Results: Step 4 Method: Generate results summary
    def generateResultsSummary(self) :

        # Place focus on load button
        self.results_summary_button.focus_set()

        # Gather the selected results to be included in the result summary in the desired order
        selected_results = []
        for result in self.config.metapop_results :
            if self.result_selected[result].get() :
                selected_results.append(result)

        # Generate result input and output files
        try :
            self.mp_file_helper.generateInputAndOutputFiles(selected_results)

        except Exception, e :
            showerror('Result Input and Output File Generation Error', 'Could not fully generate result input and output files: '+str(e))
            print >> sys.stderr, 'Error generating result input and output files:', e

        # Generate result plot files
        try :
            self.mp_file_helper.generateResultPlotFiles()

        except Exception, e :
            showerror('Result Plot File Generation Error', 'Could not fully generate result plot files: '+str(e))
            print >> sys.stderr, 'Error generating result plot files:', e

        # Generate results summary
        try :
            self.mp_file_helper.generateResultSummary(selected_results)

            # Flag completion
            self.results_summary_generation_complete = True

        except Exception, e :
            showerror('Result Summary Generation Error', 'Could not fully generate result summary: '+str(e))
            print >> sys.stderr, 'Error generating result summary:', e
            self.results_summary_generation_error = True
            if str(e).count('GLM generated successfully') :
                self.results_summary_generated = True

        # Show view result plots if data is loaded
        if self.mp_file_helper.isResultPlotDataLoaded() :
            self.showResultsAvailablePlots(True)

        # Update workflow status
        self.updateResultsStepsCompleted()

    # MP Results: Step 4 Method: Show results available plots
    def showResultsAvailablePlots(self, show) :
        if show :
            self.results_plot_label.grid()
            self.results_plot_view_button.grid()
            self.results_plot_menu.grid()
        else :
            self.results_plot_label.grid_remove()
            self.results_plot_view_button.grid_remove()
            self.results_plot_menu.grid_remove()            

    # MP Results: Step 4 Method: Generate Results Plot
    def generateResultsPlot(self) :
        if hasattr(self, 'view_results_plot_window') :
            if self.view_results_plot_window.children :
                self.view_results_plot_window.focus_set()
                self.updateResultsPlotWindow()
            else :
                self.view_results_plot_window.destroy()
                self.createResultsPlotWindow()
        else :
            self.createResultsPlotWindow()        

    # MP Results: Step 4 Method: Create Results Plot Window
    def createResultsPlotWindow(self) :

        # Create the view results plot window
        self.view_results_plot_window = tk.Toplevel(self)
        self.view_results_plot_window.title('View Results Plot')
        self.view_results_plot_window.transient(self)
        self.view_results_plot_window.focus_set()

        # Create figure
        self.view_results_plot_frame = tk.Frame(self.view_results_plot_window, padx=0, pady=0)
        self.current_results_plot_interval = self.config.result_plot_default_interval
        self.createResultsPlotFigure()

        # Plot the figure
        self.view_results_plot_canvas = FigureCanvasTkAgg(self.view_results_plot_figure, master=self.view_results_plot_frame)
        self.view_results_plot_canvas.show()
        self.view_results_plot_canvas.get_tk_widget().grid(row=0, column=0)
        self.view_results_plot_frame.grid(row=0, column=0, padx=0, pady=0)

        # Add toolbar
        toolbar = NavigationToolbar2TkAgg(self.view_results_plot_canvas, self.view_results_plot_window)
        toolbar.update()
        toolbar.grid(row=1, column=0, padx=0, pady=0)
        toolbar.grid_remove()

        # Set initial save directory
        if not(self.current_figure_save_directory and path.exists(self.current_figure_save_directory)) and (self.results_directory['path'] and path.exists(self.results_directory['path'])) :
            rcParams['savefig.directory'] = self.results_directory['path']
        self.current_figure_toolbar = toolbar

        # Add interval option selection and buttons
        button_frame = tk.Frame(self.view_results_plot_frame, padx=0, pady=0)
        self.results_plot_interval_text = tk.StringVar(value=self.config.result_plot_interval_label[self.current_results_plot_interval])
        results_plot_interval_selection = []
        for option in self.config.result_plot_intervals :
            results_plot_interval_selection.append(self.config.result_plot_interval_label[option])
        results_plot_interval_menu = tk.OptionMenu(button_frame, self.results_plot_interval_text, *results_plot_interval_selection)
        select_results_plot_interval = self.view_results_plot_frame.register(self.selectResultsPlotInterval)
        results_plot_interval_menu.config(highlightthickness=0, anchor=tk.W)
        for i, option in enumerate(self.config.result_plot_intervals) :
            results_plot_interval_menu['menu'].entryconfigure(i, command=(select_results_plot_interval, option))
        tk.Label(button_frame, text='Plot Interval:').grid(row=0, column=0, padx=0, pady=0)
        results_plot_interval_menu.grid(row=0, column=1, padx=0, pady=0)        
        tk.Label(button_frame, text='Plot Interval:').grid(row=0, column=0, padx=0, pady=0)
        tk.Button(button_frame, text='Save', anchor=tk.CENTER, command=self.saveFigureViaToolbar).grid(row=0, column=2, padx=5, pady=0)
        tk.Button(button_frame, text='Close', anchor=tk.CENTER, command=self.closeFigureWindow).grid(row=0, column=3, padx=0, pady=0)
        button_frame.grid(row=1, column=0, padx=0, pady=5)

    # MP Results: Step 4 Method: Update Results Plot Window
    def updateResultsPlotWindow(self) :
        self.createResultsPlotFigure()
        self.view_results_plot_canvas.get_tk_widget().grid_remove()
        self.view_results_plot_canvas = FigureCanvasTkAgg(self.view_results_plot_figure, master=self.view_results_plot_frame)
        self.view_results_plot_canvas.show()
        self.view_results_plot_canvas.get_tk_widget().grid(row=0, column=0)

    # MP Results: Step 4 Method: Results Plot Selection: Updates Plot If Present
    def resultsPlotSelection(self, selected) :

        self.results_plot_text.set(selected) # needed as OptionMenu menu item commands have been overridden

        # Update Results Plot If Present
        if hasattr(self, 'view_results_plot_window') :
            if self.view_results_plot_window.children :
                self.view_results_plot_window.focus_set()
                self.updateResultsPlotWindow()

    # MP Results: Step 4 Method: Create Results Plot Figure
    def createResultsPlotFigure(self) :

        # Resolve data to plot
        result_plot_key = self.results_plot_text.get()
        result_plot_config = self.config.result_plot_view_details[result_plot_key]
        result_plot_data = self.mp_file_helper.getResultsPlotData()[result_plot_key]
        plot_type = result_plot_config[self.current_results_plot_interval]['plot_type']
        plot_title = result_plot_config[self.current_results_plot_interval]['plot_title']
        x_data = result_plot_data[result_plot_config[self.current_results_plot_interval]['x_data']]
        if plot_type == 'time_series_interval' :
            y_data = result_plot_data[result_plot_config[self.current_results_plot_interval]['y_data']['mid']]
            lower_data = result_plot_data[result_plot_config[self.current_results_plot_interval]['y_data']['lower']]
            upper_data = result_plot_data[result_plot_config[self.current_results_plot_interval]['y_data']['upper']]
        else : # no others so far
            y_data = result_plot_data[result_plot_config[self.current_results_plot_interval]['y_data']]
        x_label = result_plot_config[self.current_results_plot_interval]['x_label']
        y_label = result_plot_config[self.current_results_plot_interval]['y_label']

        # Create plot
        figure_size = (14, 8)
        self.view_results_plot_figure = Figure(frameon=True, linewidth=0, dpi=100, figsize=figure_size)
        self.view_results_plot_figure.suptitle(plot_title, fontsize=14)
        self.view_results_plot_axis = self.view_results_plot_figure.add_subplot(111)
        self.view_results_plot_axis.plot(x_data, y_data)
        if plot_type == 'time_series_interval' :
            self.view_results_plot_axis.fill_between(x_data, lower_data, upper_data, facecolor='yellow', alpha=0.5)
        self.view_results_plot_axis.set_xbound(lower=min(x_data), upper=max(x_data))
        self.view_results_plot_axis.set_xlabel(x_label, fontsize=12)
        self.view_results_plot_axis.set_ylabel(y_label, fontsize=12)
        self.view_results_plot_figure.subplots_adjust(top=0.93, bottom=0.09, left=0.08, right= 0.96)

    # MP Results: Step 4 Method: Select Results Plot Interval
    def selectResultsPlotInterval(self, selected) :

        self.results_plot_interval_text.set(self.config.result_plot_interval_label[selected]) # needed as OptionMenu menu item commands have been overridden
        self.current_results_plot_interval = selected

        # Update results plot
        self.updateResultsPlotWindow()

    # MP Results: Step 4 Method: Save Figure Via Toolbar
    def saveFigureViaToolbar(self) :
        figure_path = self.current_figure_toolbar.save_figure(initialfile='figure', filetypes=['png', 'pdf'])
        figure_path = path.normpath(str(figure_path))
        if figure_path and path.exists(figure_path) :
            figure_path_dict = self.mp_file_helper.splitPath(figure_path)
            self.current_figure_save_directory = figure_path_dict['directory']

    # MP Results: Step 4 Method: Close Figure Window
    def closeFigureWindow(self) :
        if hasattr(self, 'view_results_plot_window') :
            self.view_results_plot_window.destroy()

    # MP Generation: Workflow Methods : Ensures user has completed steps before enabling sampling file generation

    # MP Generation: Update workflow progress
    def updateStepsCompleted(self, key_release=False) :

        # Update completed status
        self.process_step['mp_file_load']['completed'] = self.fileLoadAndExtractionCompleted()

        # Update sampling setting enable/disable
        default_options_mapping = { 'Latin Hypercube' : 'default_number_of_lhs_samples',
                                    'Random' : 'default_number_of_random_samples' }
        if not(self.dependentStepsToBeCompleted('sampling_settings')) :
            for key, radiobutton in self.sampling_type_radiobutton.items() :
                radiobutton.configure(state=tk.NORMAL)
                if key == self.selected_sampling_type.get() :
                    if self.sampling_details[key]['sample_number_required'] :
                        if not self.sampling_details[key]['sample_number'].get() :
                            default_sample_number = self.config.getToolOptions([default_options_mapping[key]])[default_options_mapping[key]]
                            if default_sample_number :
                                enforce_minimum_number_of_samples = self.config.getToolOptions(['enforce_minimum_number_of_samples'])['enforce_minimum_number_of_samples']
                                if enforce_minimum_number_of_samples and (default_sample_number < self.config.minimum_number_of_samples) :
                                    default_str = str(self.config.minimum_number_of_samples)
                                else :
                                    default_str = str(default_sample_number)
                            else :
                                default_str = ''
                            if not key_release :
                                self.sampling_details[key]['sample_number'].set(default_str)
                        self.sample_number_entry[key].configure(state=tk.NORMAL)
        else :
            for key, radiobutton in self.sampling_type_radiobutton.items() :
                radiobutton.configure(state=tk.DISABLED)
            for key, entryfield in self.sample_number_entry.items() :
                self.sampling_details[key]['sample_number'].set('')
                entryfield.configure(state=tk.DISABLED)

        # Update completed status
        self.process_step['sampling_settings']['completed'] = self.samplingCompleted(key_release)

        # Update parameter settings checkbox enable/disable
        no_dependent_steps = not(self.dependentStepsToBeCompleted('parameter_settings'))
        for key in self.config.parameters :
            key_present = (key in self.baseline_parameter_values['extracted'].keys())
            if no_dependent_steps and key_present and self.parameter_baseline_values['highlight'][key] :
                self.parameter_checkbox_bound[key].configure(state=tk.NORMAL)
                self.parameter_checkbox_lhs_settings[key].configure(state=tk.NORMAL)
                if self.modify_parameter[key].get() :
                    self.parameter_bounds_baseline_x_label[key].configure(bg='white', state=tk.NORMAL)
                    self.parameter_lhs_settings_baseline_x_label[key].configure(bg='white', state=tk.NORMAL)
                    self.parameter_bounds_baseline_v_button[key].configure(state=tk.NORMAL)
                    self.sample_bound_entry[key].configure(state=tk.NORMAL)
                    self.parameter_lhs_settings_baseline_v_button[key].configure(state=tk.NORMAL)
                    self.lhs_distribution_selection_menu[key].config(state=tk.NORMAL)
                    for distr in self.config.lhs_distributions :
                        if self.parameterHasValidSettings(key, to_view=True) :
                            self.lhs_view_distribution_button[key][distr].configure(state=tk.NORMAL)
                        else :
                            self.lhs_view_distribution_button[key][distr].configure(state=tk.DISABLED)
                        for setting in self.config.lhs_distribution_settings[distr] :
                            self.lhs_setting_entry[key][distr][setting['name']].configure(state=tk.NORMAL)
            else :

                # Deselect and disable parameter checkboxes
                self.modify_parameter[key].set(0)
                self.parameter_checkbox_bound[key].configure(state=tk.DISABLED)
                self.parameter_checkbox_lhs_settings[key].configure(state=tk.DISABLED)

                # Return parameter view to single field and disable 'v' button
                self.updateBaselineParameterView('bounds', 'x', key, button_pressed=False)
                self.parameter_bounds_baseline_x_label[key].configure(bg='SystemButtonFace', state=tk.DISABLED)
                self.parameter_bounds_baseline_v_button[key].configure(state=tk.DISABLED)
                self.updateBaselineParameterView('lhs_settings', 'x', key, button_pressed=False)
                self.parameter_lhs_settings_baseline_x_label[key].configure(bg='SystemButtonFace', state=tk.DISABLED)
                self.parameter_lhs_settings_baseline_v_button[key].configure(state=tk.DISABLED)

                # Return distribution selection to first in list and disable selection
                self.parameterLHSDistributionSelection(key, self.config.lhs_distributions[0], selection_made=False)
                self.lhs_distribution_selection_menu[key].config(state=tk.DISABLED)
                
                # Return set via to '% of baseline'
                self.parameter_set_via_text[key].set(self.parameter_set_via_selection_values[0])
                self.parameterSetViaSelection(key, self.parameter_set_via_selection_values[0], selection_made=False)
                self.parameter_bounds_set_via_selection_menu[key].configure(state=tk.DISABLED)
                self.parameter_lhs_settings_set_via_selection_menu[key].configure(state=tk.DISABLED)

                # Clear and disable entry fields
                self.sample_bound_text[key].set('')
                self.sample_bound_entry[key].configure(state=tk.DISABLED)
                self.sample_bound_selected_value_text[key].set('')
                self.sample_bound_selected_value_entry[key].configure(state=tk.DISABLED)
                for distr in self.config.lhs_distributions :
                    self.lhs_view_distribution_button[key][distr].configure(state=tk.DISABLED)
                    for setting in self.config.lhs_distribution_settings[distr] :
                        self.lhs_setting_text[key][distr][setting['name']].set('')
                        self.lhs_setting_previous_text[key][distr][setting['name']] = ''
                        self.lhs_setting_entry[key][distr][setting['name']].configure(state=tk.DISABLED)
                        self.lhs_setting_selected_value_text[key][distr][setting['name']].set('')
                        self.lhs_setting_selected_value_previous_text[key][distr][setting['name']] = ''
                        self.lhs_setting_selected_value_entry[key][distr][setting['name']].configure(state=tk.DISABLED)

            if not key_present :
                self.updateBaselineParameterView('bounds', 'x', key, button_pressed=False)
                self.updateBaselineParameterView('lhs_settings', 'x', key, button_pressed=False)
                self.parameter_checkbox_bound[key].deselect()
                self.parameter_checkbox_lhs_settings[key].deselect()
                self.parameter_checkbox_bound[key].configure(state=tk.DISABLED)
                self.parameter_bounds_baseline_x_label[key].configure(bg='SystemButtonFace')
                self.parameter_bounds_baseline_v_button[key].configure(state=tk.DISABLED)
                self.parameter_checkbox_lhs_settings[key].configure(state=tk.DISABLED)
                self.parameter_lhs_settings_baseline_x_label[key].configure(bg='SystemButtonFace')
                self.parameter_lhs_settings_baseline_v_button[key].configure(state=tk.DISABLED)
                self.sample_bound_text[key].set('')
                for distr in self.config.lhs_distributions :
                    self.lhs_view_distribution_button[key][distr].configure(state=tk.DISABLED)
                    for setting in self.config.lhs_distribution_settings[distr] :
                        self.lhs_setting_text[key][distr][setting['name']].set('')
                        self.lhs_setting_previous_text[key][distr][setting['name']] = ''

        # Update completed status
        self.process_step['parameter_settings']['completed'] = self.parametersCompleted()
        self.process_step['file_generation']['completed'] = self.generateCompleted()

        # Update file generation
        tool_option_values = self.config.getToolOptions()
        if self.generate_use_mp_baseline_values.get() and self.extraction_ok :
            self.generate_metapop_iterations.set(int(self.mp_file_helper.getAdditionalParameterValue('Replications')))
            self.generate_metapop_duration.set(int(self.mp_file_helper.getAdditionalParameterValue('Duration')))
        steps_to_be_completed = self.dependentStepsToBeCompleted('file_generation')
        if steps_to_be_completed :
            self.generate_use_mp_baseline_values_checkbox.configure(state=tk.DISABLED)
            self.auto_run_results_summary_checkbox.configure(state=tk.DISABLED)
            self.generate_directory_button.configure(state=tk.DISABLED)
            self.generate_button.configure(state=tk.DISABLED)
            if len(steps_to_be_completed) > 1 :
                self.generate_label_text.set(' : Complete steps ' + string.join(steps_to_be_completed, ', '))
            else :
                self.generate_label_text.set(' : Complete step ' + str(steps_to_be_completed.pop()))
        elif self.process_step['file_generation']['completed'] :
            self.generate_label_text.set(' : ' + str(self.generated_file_count) + ' files output to \"' + self.generate_directory['name'] + '\"')
            self.file_generate_complete = False # Ready for next sample generation
        elif self.file_generate_error :
            self.generate_label_text.set(' : Error generating files')
            self.file_generate_error = False # Ready to try again
        else :
            self.generate_use_mp_baseline_values_checkbox.configure(state=tk.NORMAL)
            self.generate_directory_button.configure(state=tk.NORMAL)
            if path.exists(tool_option_values['metapop_exe_location']) :
                self.auto_run_results_summary_checkbox.configure(state=tk.NORMAL)
            else :
                self.auto_run_results_summary_checkbox.configure(state=tk.DISABLED)
            if self.generateReady() :
                self.generate_button.configure(state=tk.NORMAL)
                self.generate_label_text.set(' : Ready to generate files')
            else :
                self.generate_button.configure(state=tk.DISABLED)
                self.generate_label_text.set(' : Complete this step')

        # Note if duration altered with temporal trends
        if self.durationAlteredWithTemporalTrends() :
            self.duration_when_temporal_trends_label.grid(row=4, column=0, sticky=tk.NW+tk.SW, padx=3, pady=0)
        else :
            self.duration_when_temporal_trends_label.grid_forget()

    # MP Generation: File load step is complete when the baseline mp file is loaded
    def fileLoadAndExtractionCompleted(self) :
        return self.mp_file_helper.isBaselineMpFileLoaded() and self.extraction_ok

    # MP Generation: Sampling step is complete when the selected sampling type has a valid sample number if required
    def samplingCompleted(self, key_release=False) :
        sample_type = self.selected_sampling_type.get()
        tool_options = self.config.getToolOptions()
        if self.sampling_details[sample_type]['sample_number_required'] :
            if self.isPositiveInteger(self.sampling_details[sample_type]['sample_number'].get()) :
                if key_release :
                    return True
                else :
                    if tool_options['enforce_minimum_number_of_samples'] :
                        return (int(self.sampling_details[sample_type]['sample_number'].get()) >= self.config.minimum_number_of_samples)
                    else :
                        return True
            else :
                return False
        else :
            return True

    # MP Generation: Parameter step is complete when at least one parameter is selected and all selected parameters have valid settings
    def parametersCompleted(self) :

        number_of_parameters_selected = 0
        number_of_valid_parameters = 0

        # Get sampling type
        sampling_type = self.selected_sampling_type.get()

        # Check parameter settings for selected fields (if any)
        for parameter_key, parameter_selected in self.modify_parameter.items() :
            if parameter_selected.get() :
                number_of_parameters_selected += 1
                number_of_valid_parameters += int(self.parameterHasValidSettings(parameter_key))

        return ( (number_of_parameters_selected > 0) and (number_of_parameters_selected == number_of_valid_parameters) )

    # MP Generation: Parameter has valid settings
    def parameterHasValidSettings(self, parameter_key, to_view=False) :
        valid_settings = False
        if self.selected_sampling_type.get() == 'Latin Hypercube' :
            if to_view and self.parameter_set_via_text[parameter_key].get() != self.parameter_set_via_selection_values[0] :
                lhs_setting_text = self.lhs_setting_selected_value_text
            else :
                lhs_setting_text = self.lhs_setting_text
            distribution = self.lhs_distribution_selection_text[parameter_key].get()
            if distribution == 'Uniform' :
                lower_text = lhs_setting_text[parameter_key][distribution]['Lower'].get()
                upper_text = lhs_setting_text[parameter_key][distribution]['Upper'].get()
                settings_are_floats = (self.isNonNegativetiveFloat(lower_text) and self.isNonNegativetiveFloat(upper_text))
                if settings_are_floats :
                    valid_settings = (float(lower_text) < float(upper_text))
            elif distribution == 'Gaussian' :
                mean_text = lhs_setting_text[parameter_key][distribution]['Mean'].get()
                stdev_text = lhs_setting_text[parameter_key][distribution]['Std. Dev.'].get()
                valid_settings = (self.isNonNegativetiveFloat(mean_text) and self.isPositiveFloat(stdev_text))
            elif distribution == 'Triangular' :
                lower_a_text = lhs_setting_text[parameter_key][distribution]['Lower (a)'].get()
                upper_b_text = lhs_setting_text[parameter_key][distribution]['Upper (b)'].get()
                mode_c_text = lhs_setting_text[parameter_key][distribution]['Mode (c)'].get()
                settings_are_floats = (self.isNonNegativetiveFloat(lower_a_text) and self.isNonNegativetiveFloat(upper_b_text) and self.isNonNegativetiveFloat(mode_c_text))
                if settings_are_floats :
                    valid_settings = ( (float(lower_a_text) < float(upper_b_text)) and (float(lower_a_text) <= float(mode_c_text) <= float(upper_b_text)) )
            elif distribution == 'Lognormal' :
                lower_text = lhs_setting_text[parameter_key][distribution]['Lower'].get()
                scale_text = lhs_setting_text[parameter_key][distribution]['Scale'].get()
                sigma_text = lhs_setting_text[parameter_key][distribution]['Sigma'].get()
                valid_settings = (self.isNonNegativetiveFloat(lower_text) and self.isPositiveFloat(scale_text) and self.isPositiveFloat(sigma_text))
            elif distribution == 'Beta' :
                lower_text = lhs_setting_text[parameter_key][distribution]['Lower'].get()
                upper_text = lhs_setting_text[parameter_key][distribution]['Upper'].get()
                alpha_text = lhs_setting_text[parameter_key][distribution]['Alpha'].get()
                beta_text = lhs_setting_text[parameter_key][distribution]['Beta'].get()
                settings_are_floats = (self.isNonNegativetiveFloat(lower_text) and self.isNonNegativetiveFloat(upper_text) and self.isPositiveFloat(alpha_text) and self.isPositiveFloat(beta_text))
                if settings_are_floats :
                    valid_settings = (float(lower_text) < float(upper_text))
        else :
            if to_view and self.parameter_set_via_text[parameter_key].get() != self.parameter_set_via_selection_values[0] :
                valid_settings = (self.isPositiveFloat(self.sample_bound_selected_value_text[parameter_key].get()))
            else :
                valid_settings = (self.isPositiveFloat(self.sample_bound_text[parameter_key].get()))
        return valid_settings

    # MP Generation: Generate step is ready when indicated via flag
    def generateReady(self) :
        return ( self.generate_directory_ok and
                 self.isPositiveInteger(self.generate_metapop_iterations.get()) and
                 self.isPositiveInteger(self.generate_metapop_duration.get()) )

    # MP Generation: Generate step is complete when indicated via flag
    def generateCompleted(self) :
        return self.file_generate_complete

    # MP Results: Update workflow progress
    def updateResultsStepsCompleted(self) :

        # Update completed status
        self.results_process_step['results_directory']['completed'] = self.resultsLoadCompleted()

        # Update results checkbox enable/disable
        if not(self.dependentStepsToBeCompleted('results_selection', self.results_process_step)) :
            for key in self.config.metapop_results :
                if self.results_selection_checkbox[key]['state'] == tk.DISABLED :
                    self.result_selected[key].set(1)
                self.results_selection_checkbox[key].configure(state=tk.NORMAL)
        else :
            for key in self.config.metapop_results :
                self.results_selection_checkbox[key].configure(state=tk.DISABLED)
                self.result_selected[key].set(0)

        # Update completed status
        self.results_process_step['results_selection']['completed'] = self.resultsSelectionCompleted()
        self.results_process_step['results_summary_generation']['completed'] = self.resultsSummaryGenerationCompleted()

        # Update file generation status
        steps_to_be_completed = self.dependentStepsToBeCompleted('results_summary_generation', self.results_process_step)
        if steps_to_be_completed :
            self.results_summary_button.configure(state=tk.DISABLED)
            self.results_summary_label_text.set('Complete steps ' + string.join(steps_to_be_completed, ', '))
        elif self.results_process_step['results_summary_generation']['completed'] :
            self.results_summary_label_text.set('Result summary file generated in ' + self.results_directory['name'])
            self.results_summary_generation_complete = False # Ready for next result summary
        elif self.results_summary_generation_error :
            if self.results_summary_generated :
                self.results_summary_label_text.set('Result summary file generated with some errors in ' + self.results_directory['name'])
                self.results_summary_generated = False
            else :
                self.results_summary_label_text.set('Error generating results summary')
            self.results_summary_generation_error = False # Ready to try again
        else :
            self.results_summary_button.configure(state=tk.NORMAL)
            self.results_summary_label_text.set('Ready to generate results summary')

    # MP Results: Results load step is complete when the results have been loaded successfully
    def resultsLoadCompleted(self) :
        return self.mp_file_helper.mpResultsLoadedOk()

    # MP Results: Results selection is complete when at least one results checkbox is selected
    def resultsSelectionCompleted(self) :

        number_of_results_selected = 0

        # Check selected results (if any)
        for key, result_selected in self.result_selected.items() :
            if result_selected.get() :
                number_of_results_selected += 1
        
        return number_of_results_selected > 0

    # MP Results: Generate results summary step is complete when indicated via flag
    def resultsSummaryGenerationCompleted(self) :
        return self.results_summary_generation_complete

    # General workflow method: Determine what steps still need to be completed
    def dependentStepsToBeCompleted(self, step, process_step=None) :
        if not process_step :
            process_step = self.process_step
        step_numbers = []
        for dependent in process_step[step]['dependents'] :
            if not process_step[dependent]['completed'] :
                step_numbers.append(process_step[dependent]['number'])
        return step_numbers

    # MP Generation Validation Methods: Ensure correct user inputs

    # MP Generation and Options: Number of samples validation accepts positive integer entry only, and accepts configured minumum value
    def validateNumberOfSamples(self, string_value, reason, context, sample_type) :

        # Resolve window and entry field
        # * context in ('sampling', 'options')
        # * sample_type in ('Latin Hypercube', 'Random')
        if context == 'sampling' :
            context_window = self
            self.force_shift_focus = False
        elif context == 'options' :
            context_window = self.options_window

        # Anticipate warning/error if minimum number of samples is not met
        enforce_minimum_samples = False
        if context == 'sampling' :
            if self.config.enforce_minimum_number_of_samples :
                enforce_minimum_samples = True
        elif context == 'options' :
            if self.enforce_minimum_number_of_samples.get() :
                enforce_minimum_samples = True
                
        warning_pending = False
        if string_value :
            if self.isInteger(string_value) :
                if not self.isPositiveInteger(string_value) :
                    warning_pending = True
                elif int(string_value) < self.config.minimum_number_of_samples :
                    warning_pending = enforce_minimum_samples

        if reason == 'key' :
            self.validation_warning_pending = warning_pending
            if string_value :
                # Limit data entry
                return self.isInteger(string_value)
            else :
                return True

        elif reason == 'focusin' :
            self.validation_warning_pending = warning_pending
            return True

        elif reason == 'focusout' and self.focus_get() and not self.currently_showing_warning_message : # warning messages remove focus too
            # Warn user if minimum number of samples is not met
            if warning_pending :
                if enforce_minimum_samples and (int(string_value) < self.config.minimum_number_of_samples) :
                    warning_message = ( 'The configured minimum number of samples permitted is ' + str(self.config.minimum_number_of_samples) + '.\n' +
                                        'This restriction may be altered via the options menu or the tool configuration file.' )
                else :
                    if context == 'sampling' :
                        warning_message = 'The number of samples must be a positive number.'
                    elif context == 'options' :
                        warning_message = 'If entered, the number of samples must be a positive number.'
                self.currently_showing_warning_message = True
                showwarning('Minumum Number of Samples', warning_message, parent=context_window)
                self.currently_showing_warning_message = False
                if context == 'sampling' :
                    self.sample_number_entry[sample_type].focus_set()
                elif context == 'options' :
                    if sample_type == 'Latin Hypercube' :
                        self.default_number_of_lhs_samples_entry.focus_set()
                    elif sample_type == 'Random' :
                        self.default_number_of_random_samples_entry.focus_set()
                if enforce_minimum_samples and (int(string_value) < self.config.minimum_number_of_samples) :
                    self.after_idle(lambda: self.resetNumberOfSamples(context, sample_type))
            return True

        else :
            return True

    # MP Generation and Options: Reset number of samples
    def resetNumberOfSamples(self, context, sample_type) :
        if context == 'sampling' :
            self.sampling_details[sample_type]['sample_number'].set(str(self.config.minimum_number_of_samples))
        elif context == 'options' :
            if sample_type == 'Latin Hypercube' :
                self.default_number_of_lhs_samples.set(str(self.config.minimum_number_of_samples))
            elif sample_type == 'Random' :
                self.default_number_of_random_samples.set(str(self.config.minimum_number_of_samples))
        self.validation_warning_pending = False

    # Options: Validation of default bounds accepts positive floating point entry only
    def validateParameterBoundOptions(self, string_value, reason) :

        warning_pending = False
        if string_value :
            if self.isFloat(string_value) :
                if not self.isPositiveFloat(string_value) :
                    warning_pending = True

        if reason == 'key' :
            self.validation_warning_pending = warning_pending
            if string_value :
                return string_value == '.' or self.isNonNegativetiveFloat(string_value)
            else :
                return True

        elif reason == 'focusin' :
            self.validation_warning_pending = warning_pending
            return True

        elif reason == 'focusout' and self.focus_get() and not self.currently_showing_warning_message : # warning messages remove focus too
            if warning_pending :
                warning_message = 'If entered, the sample bounds must be a positive number.'
                self.currently_showing_warning_message = True
                showwarning('Positive Sample Bounds Only', warning_message, parent=self.options_window)
                self.currently_showing_warning_message = False
            return True

        else :
            return True

    # Options: Validation of integer counts validation accepts positive integer entry only
    def validateIntegerCounts(self, string_value, reason, field) :

        warning_pending = False
        if string_value :
            if self.isInteger(string_value) :
                if not self.isPositiveInteger(string_value) :
                    warning_pending = True

        if reason == 'key' :
            self.validation_warning_pending = warning_pending
            if string_value :
                return self.isInteger(string_value)
            else :
                return True

        elif reason == 'focusin' :
            self.validation_warning_pending = warning_pending
            return True

        elif reason == 'focusout' and self.focus_get() and not self.currently_showing_warning_message : # warning messages remove focus too
            if warning_pending :
                if field == 'number_of_metapop_iterations' :
                    warning_message = 'If entered, the number of RAMAS Metapop iterations per scenario must be a positive number.'
                elif field == 'metapop_simulation_duration' :
                    warning_message = 'If entered, the RAMAS Metapop simulation duration must be a positive number.'
                self.currently_showing_warning_message = True
                showwarning('Positive Number Entry', warning_message, parent=self.options_window)
                self.currently_showing_warning_message = False
                if field == 'number_of_metapop_iterations' :
                    self.number_of_metapop_iterations_entry.focus_set()
                elif field == 'metapop_simulation_duration' :
                    self.metapop_simulation_duration_entry.focus_set()
            return True

        else :
            return True

    # Options: Validation of default LHS parameter settings
    def validateParameterLHSSettingsOptions(self, string_value, reason, distribution, setting_field) :

        # Anticipate warning/error conditions not satisfied
        warning_pending = False

        # Conditions for showing the warning/error
        show_warnings_if_any = False
        if reason == 'focusout' and self.focus_get() and not self.currently_showing_warning_message : # warning messages remove focus too
            show_warnings_if_any = True
            if self.validation_warning_pending :
                self.validation_warning_pending = False

        # Anticipate warning/error if constraints not satisfied
        warning_pending = False
        if distribution == 'Uniform' :
            lower_text = self.default_lhs_uniform_distr_lower_setting.get()
            upper_text = self.default_lhs_uniform_distr_upper_setting.get()
        elif distribution == 'Gaussian' :
            mean_text = self.default_lhs_gaussian_distr_mean_setting.get()
            stdev_text = self.default_lhs_gaussian_distr_stdev_setting.get()
        elif distribution == 'Triangular' :
            lower_text = self.default_lhs_triangular_distr_lower_setting.get()
            upper_text = self.default_lhs_triangular_distr_upper_setting.get()
            mode_text = self.default_lhs_triangular_distr_mode_setting.get()
        elif distribution == 'Lognormal' :
            scale_text = self.default_lhs_lognormal_distr_scale_setting.get()
            sigma_text = self.default_lhs_lognormal_distr_sigma_setting.get()
        elif distribution == 'Beta' :
            lower_text = self.default_lhs_beta_distr_lower_setting.get()
            upper_text = self.default_lhs_beta_distr_upper_setting.get()
            alpha_text = self.default_lhs_beta_distr_alpha_setting.get()
            beta_text = self.default_lhs_beta_distr_beta_setting.get()
        if self.isNonNegativetiveFloat(string_value) :
            if setting_field == 'Lower' or setting_field == 'Lower (a)' :
                lower_text = float(string_value)
            elif setting_field == 'Upper' or setting_field == 'Upper (b)' :
                upper_text = float(string_value)
            elif setting_field == 'Mode (c)' :
                mode_text = float(string_value)
            elif setting_field == 'Mean' :
                mean_text = float(string_value)
            elif setting_field == 'Std. Dev.' :
                stdev_text = float(string_value)
            elif setting_field == 'Scale' :
                scale_text = float(string_value)
            elif setting_field == 'Sigma' :
                sigma_text = float(string_value)
            elif setting_field == 'Alpha' :
                alpha_text = float(string_value)
            elif setting_field == 'Beta' :
                beta_text = float(string_value)

        # Warn user if the lower < upper constraint is not satisfied
        if (distribution == 'Uniform' or distribution == 'Triangular' or distribution == 'Beta') and (setting_field == 'Lower' or setting_field == 'Lower (a)' or setting_field == 'Upper' or setting_field == 'Upper (b)') :
            if self.isFloat(lower_text) and self.isFloat(upper_text) :
                if not( float(lower_text) < float(upper_text) ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror(distribution+' lower < upper condition violation', distribution+' distribution lower bound must be less than upper bound.')
                        self.currently_showing_warning_message = False
                        return False

        # Warn if Gaussian standard deviation is zero
        if distribution == 'Gaussian' and setting_field == 'Std. Dev.':
            if self.isFloat(stdev_text) :
                if not( float(stdev_text) > 0 ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Zero standard deviation', 'The Gaussian standard deviation must be a positive number (non-zero).')
                        self.currently_showing_warning_message = False
                        return False

        # Warn user if the triangular distribution bound condition a <= c <= b is not satisfied
        if distribution == 'Triangular' and (setting_field == 'Lower (a)' or setting_field == 'Upper (b)' or setting_field == 'Mode (c)') :
            if self.isFloat(lower_text) and self.isFloat(upper_text) and self.isFloat(mode_text) :
                if not( float(lower_text) <= float(mode_text) <= float(upper_text) ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Triangular a <= c <= b condition violation', 'Triangular distribution mode c must be between the lower bound a and upper bound b (inclusively).')
                        self.currently_showing_warning_message = False
                        return False

        # Warn user if the scale setting is not a positive number (0)
        if distribution == 'Lognormal' and setting_field == 'Scale' :
            if self.isFloat(scale_text) :
                if not( float(scale_text) > 0 ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Zero sigma', 'The Lognormal scale setting must be a positive number (non-zero).')
                        self.currently_showing_warning_message = False
                        return False

        # Warn user if the sigma setting is not a positive number (0)
        if distribution == 'Lognormal' and setting_field == 'Sigma' :
            if self.isFloat(sigma_text) :
                if not( float(sigma_text) > 0 ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Zero sigma', 'The Lognormal sigma setting must be a positive number (non-zero).')
                        self.currently_showing_warning_message = False
                        return False

        # Warn user if the alpha setting is not a positive number (0)
        if distribution == 'Beta' and setting_field == 'Alpha' :
            if self.isFloat(alpha_text) :
                if not( float(alpha_text) > 0 ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Zero alpha', 'The Beta distribution alpha setting must be a positive number (non-zero).')
                        self.currently_showing_warning_message = False
                        return False

        # Warn user if the beta setting is not a positive number (0)
        if distribution == 'Beta' and setting_field == 'Beta' :
            if self.isFloat(beta_text) :
                if not( float(beta_text) > 0 ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Zero beta', 'The Beta distribution beta setting must be a positive number (non-zero).')
                        self.currently_showing_warning_message = False
                        return False

        if reason == 'key' :
            self.validation_warning_pending = warning_pending
            if string_value :
                return string_value == '.' or self.isNonNegativetiveFloat(string_value)
            else :
                return True

        elif reason == 'focusin' :
            self.validation_warning_pending = False
            return True

        else :
            return True

    # MP Generation: Parameter bounds validation accepts positive floating point entry only (since no '-' characters)
    # Warns user if calculated maximum parameter bounds are exceeded
    def validateParameterBounds(self, string_value, reason, parameter_key, update_call=False) :
        if reason == 'focusout' and (self.focus_get() or update_call) and not self.currently_showing_warning_message : # warning messages remove focus too
            # Handle case when focus has moved to a (option) menu
            if self.validation_warning_pending :
                self.validation_warning_pending = False
            elif self.force_shift_focus :
                self.force_shift_focus = False
                return True

        # Anticipate warning/error if maximum parameter bound is exceeded
        warning_pending = False
        if self.isFloat(string_value) :
            if self.mp_constraint_helper.hasBoundConstraintForParameter(parameter_key) :
                if float(string_value) > self.mp_constraint_helper.getMaximumParameterBound(parameter_key) :
                    warning_pending = True
            if not self.isPositiveFloat(string_value) :
                warning_pending = True

        if reason == 'key' :
            self.validation_warning_pending = warning_pending
            if string_value :
                # Limit data entry
                return string_value == '.' or self.isNonNegativetiveFloat(string_value)
            else :
                return True

        elif reason == 'focusin' :
            if self.force_shift_focus :
                self.focus_set()
                return True
            self.validation_warning_pending = warning_pending
            return True

        elif reason == 'focusout' and (self.focus_get() or update_call) and not self.currently_showing_warning_message : # warning messages remove focus too
            # Warn user if maximum parameter bound is exceeded
            if self.isFloat(string_value) :
                if self.mp_constraint_helper.hasBoundConstraintForParameter(parameter_key) :
                    if float(string_value) > self.mp_constraint_helper.getMaximumParameterBound(parameter_key) :
                        warning_message = self.mp_constraint_helper.generateBoundConstraintWarningForParameter(parameter_key)
                        self.currently_showing_warning_message = True
                        showwarning('Parameter Bound Constraint Exceeded', warning_message)
                        self.currently_showing_warning_message = False
                        self.validation_warning_pending = False
                        return True
                if not self.isPositiveFloat(string_value) :
                    self.currently_showing_warning_message = True
                    showwarning('Positive Parameter Sample Bound Only', 'Parameter sample bounds must be positive numbers.')
                    self.currently_showing_warning_message = False
                    self.validation_warning_pending = False
                    return True
            return True

        else :
            return True

    # MP Generation: Parameter bounds selected value validation calls validation on corresponding '% of baseline'
    # If altered the '% of baseline' is calculated and set within the corresponding field
    def validateParameterBoundsSelectedValue(self, string_value, reason, parameter_key) :
        if reason != 'forced' :
            if self.isNonNegativetiveFloat(string_value) :
                selected_value = self.parameter_baseline_values['matrix_value'][parameter_key]
                if selected_value > 0 :
                    calculated_value = str(float(string_value)/selected_value*100)
                else :
                    calculated_value = self.sample_bound_text[parameter_key].get()
                if string_value != self.sample_bound_selected_value_text[parameter_key].get() :
                    self.sample_bound_text[parameter_key].set(calculated_value)
            else :
                calculated_value = string_value
                if string_value == '' :
                    self.sample_bound_text[parameter_key][distribution][setting_field].set('')
            return self.validateParameterBounds(calculated_value, reason, parameter_key)
        else :
            return True

    # MP Generation: Parameter LHS settings selected value validation calls validation on corresponding '% of baseline'
    # If altered '% of baseline' is calculated and set within the corresponding field
    def validateParameterLHSSettingsSelectedValue(self, string_value, reason, parameter_key, distribution, setting_field, update_call=False) :
        if reason != 'forced' :
            if self.isNonNegativetiveFloat(string_value) :
                for distr_setting in self.config.lhs_distribution_settings[distribution] :
                    if distr_setting['name'] == setting_field :
                        if distr_setting['postfix'] == '%' :
                            selected_value = self.parameter_baseline_values['matrix_value'][parameter_key]
                            if selected_value > 0 :
                                calculated_value = str(float(string_value)/selected_value*100)
                            else :
                                calculated_value = self.lhs_setting_text[parameter_key][distribution][setting_field].get()
                        else :
                            calculated_value = string_value
                        if string_value != self.lhs_setting_selected_value_text[parameter_key][distribution][setting_field].get() or update_call :
                            self.lhs_setting_text[parameter_key][distribution][setting_field].set(calculated_value)
                            self.lhs_setting_previous_text[parameter_key][distribution][setting_field] = calculated_value
            else :
                calculated_value = string_value
                if string_value == '' :
                    self.lhs_setting_text[parameter_key][distribution][setting_field].set('')
                    self.lhs_setting_previous_text[parameter_key][distribution][setting_field] = ''
            return self.validateParameterLHSSettings(calculated_value, reason, parameter_key, distribution, setting_field)
        else :
            return True

    # MP Generation: Spinbox arrow presses trigger 'focusout' on entry validation methods
    def validateParameterLHSSettingsViaSpinbox(self, parameter_key, distribution, setting_field, entry_type) :

        # Shift focus
        self.focus_set()

        # Exit and undo spinbox increment/decrement if validation warning is pending
        if self.validation_warning_pending :
            self.validation_warning_pending = False
            if entry_type == 'lhs_setting_selected_value_entry' :
                self.lhs_setting_selected_value_text[parameter_key][distribution][setting_field].set(self.lhs_setting_selected_value_previous_text[parameter_key][distribution][setting_field])
            else : # lhs_setting_entry
                self.lhs_setting_text[parameter_key][distribution][setting_field].set(self.lhs_setting_previous_text[parameter_key][distribution][setting_field])
            return True

        # Call validation
        if entry_type == 'lhs_setting_selected_value_entry' :
            string_value = self.lhs_setting_selected_value_text[parameter_key][distribution][setting_field].get()
            self.lhs_setting_selected_value_previous_text[parameter_key][distribution][setting_field] = string_value
            valid = self.validateParameterLHSSettingsSelectedValue(string_value, 'focusout', parameter_key, distribution, setting_field, True)
        else : # lhs_setting_entry
            string_value = self.lhs_setting_text[parameter_key][distribution][setting_field].get()
            self.lhs_setting_previous_text[parameter_key][distribution][setting_field] = string_value
            valid = self.validateParameterLHSSettings(string_value, 'focusout', parameter_key, distribution, setting_field, True)

        # Update current viewed LHS distribution
        if self.current_parameter_lhs_distribution_viewed == parameter_key  and self.parameterHasValidSettings(parameter_key, to_view=True) :
            self.updateLhsDistributionWindow(parameter_key, distribution, button_pressed=False)

        # Update view button enabled/disable
        if self.parameterHasValidSettings(parameter_key, to_view=True) :
            self.lhs_view_distribution_button[parameter_key][distribution].configure(state=tk.NORMAL)
        else :
            self.lhs_view_distribution_button[parameter_key][distribution].configure(state=tk.DISABLED)

        return valid

    # MP Generation: Parameter LHS settings validation accepts positive floating point entry only (since no '-' characters)
    # Warns user if calculated parameter values are likely to be out-of-range
    def validateParameterLHSSettings(self, string_value, reason, parameter_key, distribution, setting_field, update_call=False) :

        # Anticipate warning/error conditions not satisfied
        warning_pending = False

        # Record previous values
        if reason == 'forced' or reason == 'key' :
            self.lhs_setting_previous_text[parameter_key][distribution][setting_field] = self.lhs_setting_text[parameter_key][distribution][setting_field].get()
            self.lhs_setting_selected_value_previous_text[parameter_key][distribution][setting_field] = self.lhs_setting_selected_value_text[parameter_key][distribution][setting_field].get()

        # Conditions for showing the warning/error
        show_warnings_if_any = False
        if reason == 'focusout' and (self.focus_get() or update_call) and not self.currently_showing_warning_message : # warning messages remove focus too

            show_warnings_if_any = True

            # Handle case when focus has moved to a (option) menu
            if self.validation_warning_pending :
                self.validation_warning_pending = False
            elif self.force_shift_focus :
                self.force_shift_focus = False
                return True

        if distribution == 'Uniform' :

            lower_text = self.lhs_setting_text[parameter_key][distribution]['Lower'].get()
            upper_text = self.lhs_setting_text[parameter_key][distribution]['Upper'].get()
            if self.isNonNegativetiveFloat(string_value) :
                if setting_field == 'Lower' :
                    lower_text = float(string_value)
                elif setting_field == 'Upper' :
                    upper_text = float(string_value)

            # Warn user if the uniform distribution bound condition lower < upper is not satisfied
            if (setting_field == 'Lower' or setting_field == 'Upper') and self.isFloat(lower_text) and self.isFloat(upper_text) :
                if not( float(lower_text) < float(upper_text) ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Uniform lower < upper condition violation', 'Uniform distribution lower bound must be less than upper bound.')
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return False

            # Warn user if the Uniform distribution settings are likely to result in values that exceed constraints
            if (setting_field == 'Lower' or setting_field == 'Upper') and (self.isFloat(lower_text) or self.isFloat(upper_text)) :

                # Initialise constraint violation flags
                likely_lower_constraint_violation = False
                likely_upper_constraint_violation = False

                # Check minimumum multiplier constraints
                if setting_field == 'Lower' and self.isFloat(lower_text) and self.mp_constraint_helper.hasMinimumMultiplierConstraintForParameter(parameter_key) :
                    likely_lower_constraint_violation = (float(lower_text) < self.mp_constraint_helper.getMinimumParameterMultiplier(parameter_key))

                # Check maximumum multiplier constraints
                if setting_field == 'Upper' and self.isFloat(upper_text) and self.mp_constraint_helper.hasMaximumMultiplierConstraintForParameter(parameter_key) :
                    likely_upper_constraint_violation = (float(upper_text) > self.mp_constraint_helper.getMaximumParameterMultiplier(parameter_key))

                # Either likely constraint violation generates warning
                if likely_lower_constraint_violation or likely_upper_constraint_violation :
                    warning_pending = True
                    if show_warnings_if_any :
                        warning_message = self.mp_constraint_helper.generateLikelyDistributionConstraintWarningForParameter('uniform', parameter_key, likely_lower_constraint_violation, likely_upper_constraint_violation)
                        self.currently_showing_warning_message = True
                        showwarning('Likely to be Outside Constraints', warning_message)
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return True

        elif distribution == 'Gaussian' :

            mean_text = self.lhs_setting_text[parameter_key][distribution]['Mean'].get()
            stdev_text = self.lhs_setting_text[parameter_key][distribution]['Std. Dev.'].get()
            if self.isNonNegativetiveFloat(string_value) :
                if setting_field == 'Mean' :
                    mean_text = float(string_value)
                elif setting_field == 'Std. Dev.' :
                    stdev_text = float(string_value)

            # Warn user if the standard deviation is not a positive number (0)
            if setting_field == 'Std. Dev.' and self.isFloat(stdev_text) :
                if not( float(stdev_text) > 0 ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Zero standard deviation', 'The Gaussian standard deviation must be a positive number (non-zero).')
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return False

            # Warn user if the normal distribution settings are likely to result in values that exceed constraints
            if self.isFloat(mean_text) and self.isFloat(stdev_text) :

                # Initialise constraint violation flags
                likely_lower_constraint_violation = False
                likely_upper_constraint_violation = False

                # Threshold probability for lower and upper tails
                threshold_probability = self.config.constraint_probability_threshold_for_unbounded_distributions

                # Check minimumum multiplier constraints
                if self.mp_constraint_helper.hasMinimumMultiplierConstraintForParameter(parameter_key) :
                    sample_generator = SampleGenerator()
                    lower_threshold_multiplier = 100*sample_generator.lowerThreshold('normal', { 'mean' : float(mean_text)/100, 'std_dev' : float(stdev_text)/100 }, threshold_probability)
                    likely_lower_constraint_violation = (lower_threshold_multiplier < self.mp_constraint_helper.getMinimumParameterMultiplier(parameter_key))

                # Check maximumum multiplier constraints
                if self.mp_constraint_helper.hasMaximumMultiplierConstraintForParameter(parameter_key) :
                    sample_generator = SampleGenerator()
                    upper_threshold_multiplier = 100*sample_generator.upperThreshold('normal', { 'mean' : float(mean_text)/100, 'std_dev' : float(stdev_text)/100 }, threshold_probability)
                    likely_upper_constraint_violation = (upper_threshold_multiplier > self.mp_constraint_helper.getMaximumParameterMultiplier(parameter_key))

                # Either likely constraint violation generates warning
                if likely_lower_constraint_violation or likely_upper_constraint_violation :
                    warning_pending = True
                    if show_warnings_if_any :
                        warning_message = self.mp_constraint_helper.generateLikelyDistributionConstraintWarningForParameter('normal', parameter_key, likely_lower_constraint_violation, likely_upper_constraint_violation)
                        self.currently_showing_warning_message = True
                        showwarning('Likely to be Outside Constraints', warning_message)
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return True

        elif distribution == 'Triangular' :

            lower_a_text = self.lhs_setting_text[parameter_key][distribution]['Lower (a)'].get()
            upper_b_text = self.lhs_setting_text[parameter_key][distribution]['Upper (b)'].get()
            mode_c_text = self.lhs_setting_text[parameter_key][distribution]['Mode (c)'].get()
            if self.isNonNegativetiveFloat(string_value) :
                if setting_field == 'Lower (a)' :
                    lower_a_text = float(string_value)
                elif setting_field == 'Upper (b)' :
                    upper_b_text = float(string_value)
                elif setting_field == 'Mode (c)' :
                    mode_c_text = float(string_value)

            # Warn user if the triangular distribution bound condition a < b is not satisfied
            if (setting_field == 'Lower (a)' or setting_field == 'Upper (b)') and self.isFloat(lower_a_text) and self.isFloat(upper_b_text) :
                if not( float(lower_a_text) < float(upper_b_text) ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Triangular a < b condition violation', 'Triangular distribution lower bound a must be less than upper bound b.')
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return False

            # Warn user if the triangular distribution bound condition a <= c <= b is not satisfied
            if (setting_field == 'Lower (a)' or setting_field == 'Upper (b)' or setting_field == 'Mode (c)') and self.isFloat(lower_a_text) and self.isFloat(upper_b_text) and self.isFloat(mode_c_text) :
                if not( float(lower_a_text) <= float(mode_c_text) <= float(upper_b_text) ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Triangular a <= c <= b condition violation', 'Triangular distribution mode c must be between the lower bound a and upper bound b (inclusively).')
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return False

            # Warn user if the triangular distribution settings are likely to result in values that exceed constraints
            if (setting_field == 'Lower (a)' or setting_field == 'Upper (b)') and (self.isFloat(lower_a_text) or self.isFloat(upper_b_text)) :

                # Initialise constraint violation flags
                likely_lower_constraint_violation = False
                likely_upper_constraint_violation = False

                # Check minimumum multiplier constraints
                if setting_field == 'Lower (a)' and self.isFloat(lower_a_text) and self.mp_constraint_helper.hasMinimumMultiplierConstraintForParameter(parameter_key) :
                    likely_lower_constraint_violation = (float(lower_a_text) < self.mp_constraint_helper.getMinimumParameterMultiplier(parameter_key))

                # Check maximumum multiplier constraints
                if setting_field == 'Upper (b)' and self.isFloat(upper_b_text) and self.mp_constraint_helper.hasMaximumMultiplierConstraintForParameter(parameter_key) :
                    likely_upper_constraint_violation = (float(upper_b_text) > self.mp_constraint_helper.getMaximumParameterMultiplier(parameter_key))

                # Either likely constraint violation generates warning
                if likely_lower_constraint_violation or likely_upper_constraint_violation :
                    warning_pending = True
                    if show_warnings_if_any :
                        warning_message = self.mp_constraint_helper.generateLikelyDistributionConstraintWarningForParameter('triangular', parameter_key, likely_lower_constraint_violation, likely_upper_constraint_violation)
                        self.currently_showing_warning_message = True
                        showwarning('Likely to be Outside Constraints', warning_message)
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return True

        elif distribution == 'Lognormal' :

            lower_text = self.lhs_setting_text[parameter_key][distribution]['Lower'].get()
            scale_text = self.lhs_setting_text[parameter_key][distribution]['Scale'].get()
            sigma_text = self.lhs_setting_text[parameter_key][distribution]['Sigma'].get()
            if self.isNonNegativetiveFloat(string_value) :
                if setting_field == 'Lower' :
                    lower_text = float(string_value)
                elif setting_field == 'Scale' :
                    scale_text = float(string_value)
                elif setting_field == 'Sigma' :
                    sigma_text = float(string_value)

            # Warn user if the scale setting is not a positive number (0)
            if setting_field == 'Scale' and self.isFloat(scale_text) :
                if not( float(scale_text) > 0 ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Zero sigma', 'The Lognormal scale setting must be a positive number (non-zero).')
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return False

            # Warn user if the sigma setting is not a positive number (0)
            if setting_field == 'Sigma' and self.isFloat(sigma_text) :
                if not( float(sigma_text) > 0 ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Zero sigma', 'The Lognormal sigma setting must be a positive number (non-zero).')
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return False

            # Warn user if the Uniform distribution settings are likely to result in values that exceed constraints
            if (setting_field == 'Lower' or setting_field == 'Scale' or setting_field == 'Sigma') and (self.isFloat(lower_text) or self.isFloat(scale_text) or self.isFloat(sigma_text)) :

                # Initialise constraint violation flags
                likely_lower_constraint_violation = False
                likely_upper_constraint_violation = False

                # Threshold probability for upper tail
                threshold_probability = self.config.constraint_probability_threshold_for_unbounded_distributions

                # Check minimumum multiplier constraints
                if setting_field == 'Lower' and self.isFloat(lower_text) and self.mp_constraint_helper.hasMinimumMultiplierConstraintForParameter(parameter_key) :
                    likely_lower_constraint_violation = (float(lower_text) < self.mp_constraint_helper.getMinimumParameterMultiplier(parameter_key))

                # Check maximumum multiplier constraints
                if self.isFloat(lower_text) and self.isFloat(scale_text) and self.isFloat(sigma_text) and self.mp_constraint_helper.hasMaximumMultiplierConstraintForParameter(parameter_key) :
                    sample_generator = SampleGenerator()
                    upper_threshold_multiplier = 100*sample_generator.upperThreshold('lognormal', { 'lower' : float(lower_text)/100, 'scale' : float(scale_text)/100, 'sigma' : float(sigma_text) }, threshold_probability)
                    likely_upper_constraint_violation = (upper_threshold_multiplier > self.mp_constraint_helper.getMaximumParameterMultiplier(parameter_key))

                # Either likely constraint violation generates warning
                if likely_lower_constraint_violation or likely_upper_constraint_violation :
                    warning_pending = True
                    if show_warnings_if_any :
                        warning_message = self.mp_constraint_helper.generateLikelyDistributionConstraintWarningForParameter('lognormal', parameter_key, likely_lower_constraint_violation, likely_upper_constraint_violation)
                        self.currently_showing_warning_message = True
                        showwarning('Likely to be Outside Constraints', warning_message)
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return True

        elif distribution == 'Beta' :

            lower_text = self.lhs_setting_text[parameter_key][distribution]['Lower'].get()
            upper_text = self.lhs_setting_text[parameter_key][distribution]['Upper'].get()
            alpha_text = self.lhs_setting_text[parameter_key][distribution]['Alpha'].get()
            beta_text = self.lhs_setting_text[parameter_key][distribution]['Beta'].get()
            if self.isNonNegativetiveFloat(string_value) :
                if setting_field == 'Lower' :
                    lower_text = float(string_value)
                elif setting_field == 'Upper' :
                    upper_text = float(string_value)
                elif setting_field == 'Alpha' :
                    alpha_text = float(string_value)
                elif setting_field == 'Beta' :
                    beta_text = float(string_value)

            # Warn user if the beta distribution bound condition lower < upper is not satisfied
            if (setting_field == 'Lower' or setting_field == 'Upper') and self.isFloat(lower_text) and self.isFloat(upper_text) :
                if not( float(lower_text) < float(upper_text) ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Beta lower < upper condition violation', 'Beta distribution lower bound must be less than upper bound.')
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return False

            # Warn user if the alpha setting is not a positive number (0)
            if setting_field == 'Alpha' and self.isFloat(alpha_text) :
                if not( float(alpha_text) > 0 ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Zero alpha', 'The Beta distribution alpha setting must be a positive number (non-zero).')
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return False

            # Warn user if the beta setting is not a positive number (0)
            if setting_field == 'Beta' and self.isFloat(beta_text) :
                if not( float(beta_text) > 0 ) :
                    warning_pending = True
                    if show_warnings_if_any :
                        self.currently_showing_warning_message = True
                        showerror('Zero beta', 'The Beta distribution beta setting must be a positive number (non-zero).')
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return False

            # Warn user if the distribution settings are likely to result in values that exceed constraints
            if (setting_field == 'Lower' or setting_field == 'Upper') and (self.isFloat(lower_text) or self.isFloat(upper_text)) :

                # Initialise constraint violation flags
                likely_lower_constraint_violation = False
                likely_upper_constraint_violation = False

                # Check minimumum multiplier constraints
                if setting_field == 'Lower' and self.isFloat(lower_text) and self.mp_constraint_helper.hasMinimumMultiplierConstraintForParameter(parameter_key) :
                    likely_lower_constraint_violation = (float(lower_text) < self.mp_constraint_helper.getMinimumParameterMultiplier(parameter_key))

                # Check maximumum multiplier constraints
                if setting_field == 'Upper' and self.isFloat(upper_text) and self.mp_constraint_helper.hasMaximumMultiplierConstraintForParameter(parameter_key) :
                    likely_upper_constraint_violation = (float(upper_text) > self.mp_constraint_helper.getMaximumParameterMultiplier(parameter_key))

                # Either likely constraint violation generates warning
                if likely_lower_constraint_violation or likely_upper_constraint_violation :
                    warning_pending = True
                    if show_warnings_if_any :
                        warning_message = self.mp_constraint_helper.generateLikelyDistributionConstraintWarningForParameter('beta', parameter_key, likely_lower_constraint_violation, likely_upper_constraint_violation)
                        self.currently_showing_warning_message = True
                        showwarning('Likely to be Outside Constraints', warning_message)
                        self.currently_showing_warning_message = False
                        if update_call :
                            self.warning_shown_for_update_validation = True
                        return True

        if reason == 'key' :
            self.validation_warning_pending = warning_pending
            if string_value :
                # Limit data entry
                return string_value == '.' or self.isNonNegativetiveFloat(string_value)
            else :
                return True

        elif reason == 'focusin' :
            if self.force_shift_focus :
                self.focus_set()
                return True
            self.validation_warning_pending = warning_pending
            return True

        else :
            return True

    # MP Generation : Event handlers

    # MP Generation: Key releases on entry fields update the workflow steps completed
    def __keyReleaseOnEntryField(self, event) :
        self.updateStepsCompleted(True)
        
        # Update current viewed LHS distribution
        if self.entry_field_map.has_key(str(event.widget)) :
            if self.entry_field_map[str(event.widget)]['section'] == 'parameter_settings' :
                if self.entry_field_map[str(event.widget)]['context'] == 'lhs_settings' :
                    key = self.entry_field_map[str(event.widget)]['parameter_key']
                    if self.current_parameter_lhs_distribution_viewed == key and self.parameterHasValidSettings(key, to_view=True) :
                        distr = self.lhs_distribution_selection_text[key].get()
                        self.updateLhsDistributionWindow(key, distr, button_pressed=False)

    # General Purpose Validation Methods

    # String is a float?
    def isFloat(self, string_value) :
        try :
            float(string_value)
            return True
        except Exception, e :
            return False

    # String is a positive float?
    def isPositiveFloat(self, string_value) :
        try :
            float_value = float(string_value)
            return float_value > 0
        except Exception, e :
            return False

    # String is a non-negative float?
    def isNonNegativetiveFloat(self, string_value) :
        try :
            float_value = float(string_value)
            return float_value >= 0
        except Exception, e :
            return False

    # String is an integer?
    def isInteger(self, string_value) :
        return (type(eval(string_value)) == int)

    # String is a positive integer?
    def isPositiveInteger(self, string_value) :
        try :
            integer_value = int(string_value)
            return integer_value > 0
        except Exception, e :
            return False

# END ApplicationGUI

## Main program

application_name = 'SARDM'
application_version = 'v0.6'
application_longname = 'SARDM: Sensitivity Analysis of Range Dynamics Models'

# Set user application data directory
if environ.has_key('APPDATA'):
    user_app_data_root = environ['APPDATA']
else:
    user_app_data_root = environ['USERPROFILE']
user_application_data_directory = path.join(user_app_data_root , (application_name + ' ' + application_version))
if not path.exists(user_application_data_directory) :
    try :
        mkdir(user_application_data_directory)
    except Exception, e :
        showerror('Directory Error', 'Cannot create application directory '+user_application_data_directory+'. Check file permissions.')
        print >> sys.stderr, 'Error creating user application directory', user_application_data_directory, ':', e
        user_application_data_directory = user_app_data_root

# Log files
if not DEBUG : # Re-direct stdout and stderr to log file
    log_file = path.join(user_application_data_directory , 'SARDM_error_log.txt')
    if path.exists(log_file) :
        sys.stdout = open(log_file, 'a')
        sys.stderr = open(log_file, 'a')
    else :
        sys.stdout = open(log_file, 'w')
        sys.stderr = open(log_file, 'w')

root = tk.Tk()
app = ApplicationGUI(application_name, user_application_data_directory, master=root)
app.master.title((application_longname + ' - ' + application_version))
app.mainloop()

if not DEBUG : # close log files
    sys.stdout.close()
    sys.stderr.close()

if root.children :
    root.destroy() # required for menu quit
else :
    0 # Window close already destroyed object

# END Main program
