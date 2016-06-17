# Python modules
from os import chdir, getcwd, listdir, mkdir, path
from subprocess import call
import string

# Python extension module NumPy (requires extension installation)
import numpy as np

# Tool library module
from MpFileExtractorAndGeneratorHelper import MpFileExtractorAndGeneratorHelper
from MpParameterBoundConstraintHelper import MpParameterBoundConstraintHelper

# Set test directory
test_directory = getcwd() # r'C:\afat32\Dropbox\GlobalEcologyGroup\ProjectCode\SensitivityAnalysisToolset\v0.3\Test'

## Test Configuration 1 (for simplified example)
class TestMetapopConfiguration1 :

    # Initialise with the test config
    def __init__(self) :

        # Configure parameter list in desired order
        self.parameters = ['single 1', 'single 2', 'single 3', 'single row 1', 'single row 2', 'single row 3',
                           'single column 1', 'single column 2', 'single column 3', 'single column 4',
                           'Matrix 1', 'Matrix 2']

        # Parameter mapping to test 1 (simplified example) MP file
        self.parameter_mapping = {}

        # Single value:
        self.parameter_mapping['single 1'] = { 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 4, 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['single 2'] = { 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 5, 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['single 3'] = { 'number_rows' : 1, 'number_columns' : 1, 'start_row' : 6, 'start_column' : 1, 'delimiter' : ',' }

        # Single row matrices:
        self. parameter_mapping['single row 1'] = { 'number_rows' : 1, 'number_columns' : 2, 'start_row' : 9, 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['single row 2'] = { 'number_rows' : 1, 'number_columns' : 3, 'start_row' : 10, 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['single row 3'] = { 'number_rows' : 1, 'number_columns' : 3, 'start_row' : 11, 'start_column' : 2, 'delimiter' : ' ' }

        # Single column matrices:
        self.parameter_mapping['single column 1'] = { 'number_rows' : 2, 'number_columns' : 1, 'start_row' : 14, 'start_column' : 1, 'delimiter' : ',' }
        self.parameter_mapping['single column 2'] = { 'number_rows' : 3, 'number_columns' : 1, 'start_row' : 14, 'start_column' : 2, 'delimiter' : ',' }
        self.parameter_mapping['single column 3'] = { 'number_rows' : 3, 'number_columns' : 1, 'start_row' : 14, 'start_column' : 4, 'delimiter' : ',' }
        self.parameter_mapping['single column 4'] = { 'number_rows' : 2, 'number_columns' : 1, 'start_row' : 17, 'start_column' : 2, 'delimiter' : ' ' }

        # Matrices:
        self.parameter_mapping['Matrix 1'] = { 'number_rows' : 3, 'number_columns' : 4, 'start_row' : 22, 'start_column' : 1, 'delimiter' : ' ' }
        self.parameter_mapping['Matrix 2'] = { 'number_rows' : 4, 'number_columns' : 3, 'start_row' : 28, 'start_column' : 2, 'delimiter' : ',' }

        # No Additional
        self.parameter_mapping['additional'] = {}

        # Output formats:
        self.data_frame_mp_file_heading = 'Modified MP file'
        self.data_frame_heading_lines = 3
        self.data_frame_field_width = 15
        self.data_frame_percent_width = self.data_frame_field_width - 1
        self.data_frame_field_width_substitution = 'FW'
        self.data_frame_notes_marker = ' *'
        self.parameter_output_format = {}
        self.parameter_output_format['single 1'] = { 'mp_format' : '%.1f' }
        self.parameter_output_format['single 2'] = { 'mp_format' : '%.1f' }
        self.parameter_output_format['single 3'] = { 'mp_format' : '%.2f' }
        self.parameter_output_format['single row 1'] = { 'mp_format' : '%.1f' }
        self.parameter_output_format['single row 2'] = { 'mp_format' : '%.1f' }
        self.parameter_output_format['single row 3'] = { 'mp_format' : '%.1f' }
        self.parameter_output_format['single column 1'] = { 'mp_format' : '%.1f' }
        self.parameter_output_format['single column 2'] = { 'mp_format' : '%.1f' }
        self.parameter_output_format['single column 3'] = { 'mp_format' : '%.1f' }
        self.parameter_output_format['single column 4'] = { 'mp_format' : '%.1f' }
        self.parameter_output_format['Matrix 1'] = { 'mp_format' : '%.1f', 'output_file_heading' : 'Matrix 1', 'output_file_format' : '%FW.3f', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Matrix 2'] = { 'mp_format' : '%.6f', 'output_file_heading' : 'Matrix 2', 'output_file_format' : '%FW.3f', 'output_file_percent_format' : '%FW.1f%%' }

        # Configure file generation numbering format
        self.file_generation_numbering_format = '_%04d' # generates numbering from _0001
        
        # Parameter constraints:
        self.parameter_constraints = {}
        self.parameter_constraints['Matrix 1'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 },
                                                  { 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1, 'from_row' : 2 }]
        self.parameter_constraints['Matrix 2'] = [{ 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_CELL_VALUES, 'lower' : 0, 'upper' : 1 },
                                                  { 'constraint_type' : MpParameterBoundConstraintHelper.LIMITED_COLUMN_SUMS, 'upper' : 1, 'from_row' : 2 }]

        # Configure how to express the data frame values for the parameters (default uses unique or percentage)
        self.parameter_data_frame = {}

        # Configure how to express the result input values for the parameters
        self.parameter_result_input = {}

# END TestMetapopConfiguration1

## Test Configuration 2 (for realistic example)
class TestMetapopConfiguration2 :

    # Initialise with the test config
    def __init__(self) :

        # Configure parameter list in desired order
        self.parameters = ['Initial Abundance', 'Rmax', 'Carrying Capacity', 'Allee Effect', 'Probability of a Catastrophe 1', 'Local Multiplier 1', 'Stage Multiplier 1',
                           'Probability of a Catastrophe 2', 'Local Multiplier 2', 'Stage Multiplier 2', 'Dispersal Matrix', 'Correlation Matrix', 'Fecundity Rates',
                           'Survival Rates', 'Environmental Variation']

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
        fecundity_rates_submatrix_mask = { 'partition' : 'diagonal_upper_right', 'rows' : 'first', 'include_diagonal' : True }
        self.parameter_mapping['alternatives']['Fecundity Rates']['OnlyFemale'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'whole_matrix' : fecundity_rates_submatrix_mask } }
        self.parameter_mapping['alternatives']['Fecundity Rates']['OnlyMale'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'whole_matrix' : fecundity_rates_submatrix_mask } }
        self.parameter_mapping['alternatives']['Fecundity Rates']['AllIndividuals'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'whole_matrix' : fecundity_rates_submatrix_mask } }
        self.parameter_mapping['alternatives']['Fecundity Rates']['TwoSexes'] = { 'option' : 'mating_system' }
        self.parameter_mapping['alternatives']['Fecundity Rates']['TwoSexes']['Monogamous'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'quadrants' : { 'divide_at' : 'female_stages', 'upper_left' : fecundity_rates_submatrix_mask, 'lower_left' : fecundity_rates_submatrix_mask } } }
        self.parameter_mapping['alternatives']['Fecundity Rates']['TwoSexes']['Polygynous'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'quadrants' : { 'divide_at' : 'female_stages', 'upper_left' : fecundity_rates_submatrix_mask, 'lower_left' : fecundity_rates_submatrix_mask } } }
        self.parameter_mapping['alternatives']['Fecundity Rates']['TwoSexes']['Polyandrous'] = { 'subset_of' : 'Stage Matrix', 'subset_mask' : { 'quadrants' : { 'divide_at' : 'female_stages', 'upper_right' : fecundity_rates_submatrix_mask, 'lower_right' : fecundity_rates_submatrix_mask } } }
        self.parameter_mapping['alternatives']['Survival Rates'] = {}
        self.parameter_mapping['alternatives']['Survival Rates']['option'] = 'sex_structure'
        survival_rates_submatrix_mask = { 'partition' : 'diagonal_lower_left', 'rows' : 'below_first', 'include_diagonal' : True }
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
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][False]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][True] = {}
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][True]['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][True]['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Local Multiplier 1']['postcondition'][True]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
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
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][False]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : ['Vital Rates'], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][True] = {}
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][True]['Local'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][True]['Correlated'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
        self.parameter_mapping['alternatives']['conditions']['Probability of a Catastrophe 2']['postcondition'][True]['Regional'] = { 'option' : 'catastrophe_affects', 'values' : [], 'match_any' : ['Abundances', 'Vital Rates', 'Carrying Capacities', 'Dispersal Rates'], 'match_none' : [], 'satisfied' : False }
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
        self.parameter_output_format['Rmax'] = { 'short_heading' : 'Rmax', 'mp_format' : '%.3f', 'output_file_heading' : 'Rmax', 'output_file_format' : '%FW.3f', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Carrying Capacity'] = { 'short_heading' : 'Capac', 'mp_format' : '%d', 'output_file_heading' : ['Carrying', 'Capacity', ''], 'output_file_format' : '%FWd', 'output_file_percent_format' : '%FWd%%' }
        self.parameter_output_format['Allee Effect'] = { 'short_heading' : 'Allee', 'mp_format' : '%d', 'output_file_heading' : ['Allee', 'Effect', ''], 'output_file_format' : '%FWd', 'output_file_percent_format' : '%FWd%%' }
        self.parameter_output_format['Probability of a Catastrophe 1'] = { 'short_heading' : 'ProbCat1', 'mp_format' : '%.5f', 'output_file_heading' : ['Probability', 'Catastrophe', '1'], 'output_file_format' : '%FW.5f', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Local Multiplier 1'] = { 'short_heading' : 'LocMult1', 'mp_format' : '%.3f', 'output_file_heading' : ['Local', 'Multiplier', '1'], 'output_file_format' : '%FW.3f', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Stage Multiplier 1'] = { 'short_heading' : 'StgMult1', 'mp_format' : '%.6f', 'output_file_heading' : ['Stage', 'Multipliers', '1'], 'output_file_format' : '%FW.3f', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Probability of a Catastrophe 2'] = { 'short_heading' : 'ProbCat2', 'mp_format' : '%.5f', 'output_file_heading' : ['Probability', 'Catastrophe', '2'], 'output_file_format' : '%FW.5f', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Local Multiplier 2'] = { 'short_heading' : 'LocMult2', 'mp_format' : '%.3f', 'output_file_heading' : ['Local', 'Multiplier', '2'], 'output_file_format' : '%FW.3f', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Stage Multiplier 2'] = { 'short_heading' : 'StgMult2', 'mp_format' : '%.6f', 'output_file_heading' : ['Stage', 'Multipliers', '2'], 'output_file_format' : '%FW.3f', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Dispersal Matrix'] = { 'short_heading' : 'Disp', 'mp_format' : '%.5f', 'output_file_heading' : ['Dispersal', 'Matrix', ''], 'output_file_format' : '%FW.3f', 'output_file_percent_format' : '%FW.1f%%' }
        self.parameter_output_format['Stage Matrix'] = { 'mp_format' : '%.9f' }
        self.parameter_output_format['Fecundity Rates'] = { 'short_heading' : 'Fecund', 'mp_format' : '%.9f', 'output_file_heading' : ['Fecundity', 'Rates', ''], 'output_file_format' : '%FW.5f', 'output_file_percent_format' : '%FW.3f%%' }
        self.parameter_output_format['Survival Rates'] = { 'short_heading' : { 'single' : 'Surv', 'multiple' : ['LowSurv', 'HiSurv'] }, 'mp_format' : '%.9f', 'output_file_heading' : ['Survival', 'Rates', ''], 'output_file_format' : '%FW.5f', 'output_file_percent_format' : '%FW.3f%%' }
        self.parameter_output_format['Environmental Variation'] = { 'short_heading' : 'EnvVar', 'mp_format' : '%.9f', 'output_file_heading' : ['Environmental', 'Variation', ''], 'output_file_format' : '%FW.5f', 'output_file_percent_format' : '%FW.3f%%' }
        self.parameter_output_format['Initial Abundance'] = { 'short_heading' : 'InitN', 'mp_format' : '%d', 'output_file_heading' : ['Initial', 'Abundance', ''], 'output_file_format' : '%FWd', 'output_file_percent_format' : '%FWd%%' }
        self.parameter_output_format['Correlation Matrix'] = { 'short_heading' : 'Corr', 'mp_format' : '%.5f', 'output_file_heading' : ['Correlation', 'Matrix', ''], 'output_file_format' : '%FW.3f', 'output_file_percent_format' : '%FW.1f%%' }

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
        self.parameter_result_input['Fecundity Rates'] = 'unique_or_percent' # was 'last_non_zero'
        self.parameter_result_input['Survival Rates'] = ['min_non_zero', 'max']
        self.parameter_result_input['Environmental Variation'] = 'percent_change'

        # Configure file generation numbering format
        self.file_generation_numbering_format = '_%04d' # generates numbering from _0001
        
        # Configure the local disk location of the RAMAS Metapop program
        self.metapop_exe_location = r'H:\La Trobe Lecturing\Collaborations\GlobalEcologyGroup-Lab\RAMAS-Metapop\Metapop.exe'

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
        self.result_output_format['Expected Minimum Abundance'] = { 'short_heading' : 'EMA', 'output_file_heading' : ['Expected', 'Minimum', 'Abundance'], 'output_file_format' : '%FW.1f' }
        self.result_output_format['Final number of occupied patches'] = { 'short_heading' : 'FinalOcc', 'output_file_heading' : ['Final number', 'of occupied', 'patches'], 'output_file_format' : '%FW.1f' }
        self.result_output_format['Final N for persistent runs'] = { 'short_heading' : 'FinalN', 'output_file_heading' : ['Final N for', 'persistent', 'runs'], 'output_file_format' : '%FW.2f' }
        self.result_output_format['Total extinction risk'] = { 'short_heading' : 'Ext', 'output_file_heading' : ['Total', 'extinction', 'risk'], 'output_file_format' : '%FW.4f' }
        self.result_output_format['Quasi extinction risk'] = { 'short_heading' : 'QuasiExt', 'output_file_heading' : ['Quasi', 'extinction', 'risk'], 'output_file_format' : '%FW.4f' }

        # Configure selection of result plots collected in the desired presentation order
        self.metapop_result_plots = ['Abundance', 'Patch Occupancy']

        # Configure result plot mapping to RAMAS Metapop result file components
        self.metapop_result_plot_mapping = {}
        self.metapop_result_plot_mapping['Abundance'] = { 'fields': ['Time', 'Average'], 'collect' : [{ 'result_file' : 'Abund.txt', 'component' : 'time' }, { 'result_file' : 'Abund.txt', 'component' : 'mean_n' }], 'value' : 'join_arrays(time,mean_n)' }
        self.metapop_result_plot_mapping['Patch Occupancy'] = { 'fields': ['Time', 'Average'], 'collect' : [{ 'result_file' : 'MetapopOcc.txt', 'component' : 'time' }, { 'result_file' : 'MetapopOcc.txt', 'component' : 'n_occ_patches' }], 'value' : 'join_arrays(time,n_occ_patches)' }

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
        self.result_plot_calculated_data['Abundance'] = common_calculations
        self.result_plot_calculated_data['Patch Occupancy'] = common_calculations

        # Configure result plot file and visualisation details
        self.result_plot_file_details = {}
        self.result_plot_file_details['Abundance'] = { 'filename' : 'Predicted_Abundance', 'fields' : common_fields }
        self.result_plot_file_details['Patch Occupancy'] = { 'filename' : 'Predicted_Metapopulation_Size', 'fields' : common_fields }
                                
# END TestMetapopConfiguration2

## Main program

# Create and configure the file helpers
config1 = TestMetapopConfiguration1()
config2 = TestMetapopConfiguration2()
mp_file_helper1 = MpFileExtractorAndGeneratorHelper(config1)
mp_file_helper2 = MpFileExtractorAndGeneratorHelper(config2)

# TEST 1: MP file extraction and generation. Check that:
# I)  Simplified example
#     a) The parameter values are correctly extracted from the baseline mp file
#     b) The template is correctly generated
#     c) The replacement values are substituted correctly into the modified mp file
#     d) The output formats are as per configuration

print 'TEST 1: MP file extraction and generation'

# I) Simplified example
print '\nI) Simplified example'

# Load baseline mp file
mp_file_path = test_directory + r'\test_1_baseline.mp'
mp_file_helper1.setOutputDirectory(test_directory)
mp_file_helper1.loadBaselineMpFile(mp_file_path)

# Extract baseline parameter values
baseline_parameter_values = mp_file_helper1.extractParametersFromMpFileContents()
print '\nExtracted parameters:'
for parameter in config1.parameters :
    print parameter, ' = '
    print baseline_parameter_values[parameter]

# Generate template (also write to file)
mp_file_helper1.createGenerationTemplate(config1.parameters, write_template='test_1_template_1.txt')
print '\nTemplate test_1_template_1.txt generated in Test directory\n'

# Multiply the baseline values by 10
modified_parameter_values = {}
for parameter in config1.parameters :
    modified_parameter_values[parameter] = 10*baseline_parameter_values[parameter]

# Test ouput directory
print 'Output directory: ', mp_file_helper1.output_directory
mp_file_helper1.output_directory['name'] = 'MpFilesTest'
mp_file_helper1.output_directory['path'] = test_directory + r'\MpFilesTest'

# Generate modified mp file
generated_mp_file_name = mp_file_helper1.generateModifiedMpFile(modified_parameter_values, 1)

# TEST 1: MP file extraction and generation. Check that:
# II) Realistic examples
#     a) Test resolution of dynamic MP parameter mapping configuration
#     b) The parameter values are correctly extracted from the baseline mp file
#     c) Matrices are generated from extracted function parameters where appropriate
#     d) The template is correctly generated including the modification of additional settings
#     e) The replacement values are substituted correctly into the modified mp file 
#     These examples test various combinations of alternative or conditional extraction strategies, including:
#     * Conditional inclusion of Rmax, Carrying Capacity and Allee Effect dependent on density dependence type,
#       which may be defined for each population or common to all
#     * The extraction of multiple matrices (or layers) for Fecundity Rates, Survival Rates and Environmental Variation
#     * The conditional extraction or function-based generation of matrices for Dispersal Matrix and Correlation Matrix
#     NEW for case studies:
#     * The conditional inclusion of Dispersal Matrix and Correlation Matrix when populations > 1
#     * The conditional inclusion of Probability of a Catastrophe, Local Multiplier, and Stage Multiplier (1 and 2)
#       dependent on catastrophe Extent (Local/Correlated/Regional) and Affects (Abundances/Vital Rates/Carrying Capacities/Dispersal Rates)
#     * The conditional extraction of Probability of a Catastrophe and Stage Multiplier (1 and 2) dependent on Extent and Affects
#     * The conditional extraction of the temporal trend and other filenames required, including: user defined functions (.DLL);
#       relative fecundity (.FCH); relative survival (.SCH); relative dispersal (.DCH); temporal trend in K (.KCH);
#       relative variability-fecundity (.VCH); relative variability-survival (.VCH); catastrophe probability (.PCH);
#       catastrophe local multiplier (.MCH); and map features (.MAP)
#     f) The temporal trend and other linked files are appropriately modified, indexed, and generated or copied into the generation directory.

# II) Realistic example
print '\nII) Realistic examples:'

# Example files
example_files = ['SandLizard_baseline_1.mp', 'SandLizard_baseline_1a.mp', 'SandLizard_baseline_2.mp', 'SandLizard_baseline_3.mp', 'SandLizard_baseline_4.mp',
                 r'TemporalTrendTest\SandLizard_temporal_trends-1.mp', r'TemporalTrendTest\SandLizard_temporal_trends-2.mp',
                 r'CaseStudies\Abalone\KI_Rubra_ModelV2.mp', r'CaseStudies\Abalone\KI_Rubra_ModelV2_males.mp', r'CaseStudies\Abalone\KI_Rubra_ModelV2_mixed.mp',
                 r'CaseStudies\GCB\KI_GBC.mp', r'CaseStudies\GCB\KI_GBC_Polygynous.mp', r'CaseStudies\GCB\KI_GBC_Polyandrous.mp',
                 r'CaseStudies\Abalone\KI_Rubra_ModelV2.mp', r'CaseStudies\GCB\KI_GBC.mp', r'CaseStudies\Orangutan\OrangSinglePop.mp',
                 r'CaseStudies\Turtle\TurtleMetapopNorthern.mp', r'CaseStudies\Turtle\TurtleMetapopSouthern.mp']
for index, example_file in enumerate(example_files) :

    # Load baseline mp file
    mp_file_path = test_directory + '\\' + example_file
    mp_file_helper2.loadBaselineMpFile(mp_file_path)

    if index == 0 : 
        # Resolve dynamic MP parameter mapping configuration
        print '\nParameter mapping configuration prior to resolution of dynamic mapping: '
        print mp_file_helper2.config.parameter_mapping
        mp_file_helper2.resolveDynamicMpParameterMappingConfiguration(mp_file_helper2.baseline_mp_file['lines'])
        print '\nParameter mapping configuration after resolution of dynamic mapping: '
        print mp_file_helper2.parameter_mapping
        correct_mapping = {'Environmental Variation': {'delimiter': ' ', 'start_row': 89, 'number_columns': 15, 'number_rows': 15, 'start_column': 1}, 'Local Multiplier': {'delimiter': ',', 'start_row': 45, 'number_columns': 1, 'number_rows': 8, 'start_column': 12}, 'Rmax': {'delimiter': ',', 'start_row': 45, 'number_columns': 1, 'number_rows': 8, 'start_column': 6}, 'Probability of a Catastrophe': {'delimiter': ',', 'start_row': 45, 'number_columns': 1, 'number_rows': 8, 'start_column': 13}, 'Dispersal Matrix': {'delimiter': ',', 'start_row': 56, 'number_columns': 8, 'number_rows': 8, 'start_column': 1}, 'Carrying Capacity': {'delimiter': ',', 'start_row': 45, 'number_columns': 1, 'number_rows': 8, 'start_column': 7}, 'Survival Rates': {'delimiter': ' ', 'start_row': 73, 'number_columns': 15, 'number_rows': 14, 'start_column': 1}, 'Fecundity Rates': {'delimiter': ' ', 'start_row': 72, 'number_columns': 15, 'number_rows': 1, 'start_column': 1}}
        print '\nShould be:'
        print correct_mapping

    # Extract baseline parameter values
    baseline_parameter_values = mp_file_helper2.extractParametersFromMpFileContents()
    print '\nExtracted parameters for ' + example_file + ':', baseline_parameter_values.keys()
    for parameter in ['Stage Multiplier 1', 'Stage Multiplier 2'] : #['Fecundity Rates', 'Survival Rates'] : #baseline_parameter_values.keys() :
        #print 'mapping:', mp_file_helper2.parameter_mapping[parameter]
        if baseline_parameter_values.has_key(parameter) :
            print parameter, ' = '
            print baseline_parameter_values[parameter]

    # Additional parameter values extracted (includes: 'population_coordinates')
    print '\nAdditional extracted parameters for ' + example_file + ':'
    for parameter in mp_file_helper2.additional_parameter_values.keys() :
        print parameter, ' = '
        print mp_file_helper2.additional_parameter_values[parameter]

    # Parameter file links
    files_linked_to_parameters = mp_file_helper2.loadFilesLinkedToParameters()
    print '\nParameter file links for ' + example_file + ':'
    for parameter in files_linked_to_parameters.keys() :
        print '*', parameter, ' = '
        for key, value in files_linked_to_parameters[parameter].items() :
            if key == 'file_contents' :
                for file_name, contents in value.items() :
                    print file_name, ':\n', contents.to_string(max_rows=5)
            else :
                print key, ':\n', value

    # Construct matrices defined as functions in MP file
    calculated_parameter_values = mp_file_helper2.constructFunctionDefinedMatrices()
    print '\nCalculated parameters for ' + example_file + ':'
    for parameter in calculated_parameter_values.keys() :
        print parameter, ' = '
        print calculated_parameter_values[parameter]

    # Reset file helper generation functionality
    mp_file_helper2.reset_sampling_generation()

    # Select all parameters but Local Multiplier 2 and Rmax
    selected_keys = baseline_parameter_values.keys()
    if selected_keys.count('Local Multiplier 2') :
        selected_keys.remove('Local Multiplier 2')
    if selected_keys.count('Rmax') :
        selected_keys.remove('Rmax')

    # Set output directory
    output_dir_path = path.join(test_directory, 'MpFilesTest', mp_file_helper2.getBaselineMpFileName().replace('.mp', ''))
    if not path.exists(output_dir_path) :
        mkdir(output_dir_path)
    mp_file_helper2.setOutputDirectory(output_dir_path)

    # Generate template (also write to file)
    if index == 0 : 
        mp_file_helper2.modifyAdditionalParameterValues({ 'Replications' : 1020, 'Duration' : 55 })
    mp_file_helper2.createGenerationTemplate(selected_keys, write_template='template.txt')
    print '\nTemplate template.txt generated in', output_dir_path, '\n'

    # Multiply the baseline values by 0.5
    modified_parameter_values = {}
    for parameter_key in baseline_parameter_values.keys() :
        modified_parameter_values[parameter_key] = 0.5*baseline_parameter_values[parameter_key]
    modified_parameter_values['Fecundity Rates'] = 0.1*baseline_parameter_values['Fecundity Rates']

    # Multiply any linked file contents by 0.5
    modified_linked_file_contents = {}
    for parameter_key, file_links in files_linked_to_parameters.items() :
        if parameter_key in selected_keys :
            modified_linked_file_contents[parameter_key] = {}
            for filename, contents in file_links['file_contents'].items() :
                modified_contents = 0.5*contents.get_values()
                if mp_file_helper2.config.parameter_data_types.has_key(parameter_key) :
                    if mp_file_helper2.config.parameter_data_types[parameter_key] == 'integer' :
                        modified_contents = modified_contents.round().astype(int) 
                modified_linked_file_contents[parameter_key][filename] = modified_contents

    # Generate modified mp file
    generated_mp_file_name = mp_file_helper2.generateModifiedMpFile(modified_parameter_values, 1)
    print generated_mp_file_name, 'generated in', output_dir_path, '\n'

    # Generate modified linked files
    generated_linked_file_names = mp_file_helper2.generateModifiedLinkedFiles(modified_linked_file_contents, 1)
    print 'linked files generated in', output_dir_path, '\n', generated_linked_file_names

    # Copy other linked files
    copied_linked_files = mp_file_helper2.copyUnmodifiedLinkedFiles()
    print 'Unmodified linked files copied to', output_dir_path, '\n', copied_linked_files

    print "Press any key to continue *************************************************************************************************************"
    test = raw_input()

# END TEST 1

# TEST 2: Data frame generation. Check that:
# a) Data frame headings and entries are correctly generated
# b) Entries are in the correct format and appropriately presented as a value or %
# c) Constraint violations are marked and noted

print '\nTEST 2: Data frame generation'

# Test parameters values and multipliers
mp_file_helper1.parameters_selected = ['Matrix 1', 'Matrix 2']
test_parameter_values1 = { 'Matrix 1' : np.array([[0.2, 0.2], [0.2, 0.2], [0.2, 0.2]]),
                          'Matrix 2' : np.array([[0.8, 0.6, 0.8], [0.8, 0.8, 0.8]]) }
multiplier1 = {'Matrix 1' : 1.1, 'Matrix 2' : 0.9}
test_parameter_values2 = { 'Matrix 1' : np.array([[1.6, 1.6], [1.6, 1.6], [1.6, 1.6]]),
                          'Matrix 2' : np.array([[2.4, 4.8, 2.4], [2.4, 2.4, 2.4]]) }
multiplier2 = {'Matrix 1' : 0.8, 'Matrix 2' : 1.2}
test_parameter_values3 = { 'Matrix 1' : np.array([[1.6, 1.6], [1.6, 1.6], [1.6, 1.6]]),
                          'Matrix 2' : np.array([[2.4, 4.8, 2.4], [2.4, 2.4, 2.4]]) }
multiplier3 = {'Matrix 1' : 0.8, 'Matrix 2' : 1.2}

# Generate data frame entries
data_frame_entry_details = mp_file_helper1.generateDataFrameEntry('dummy_filename_1.mp', test_parameter_values1, multiplier1)
print data_frame_entry_details
data_frame_entry_details = mp_file_helper1.generateDataFrameEntry('dummy_filename_2.mp', test_parameter_values2, multiplier2)
print data_frame_entry_details
data_frame_entry_details = mp_file_helper1.generateDataFrameEntry('dummy_filename_2b.mp', test_parameter_values2, multiplier2)
print data_frame_entry_details

# Generate data frame file
mp_file_helper1.generateDataFrameFile()

# END TEST 2

# TEST 3: Metapop batch generation. Check that:
# a) Batch entries are correctly generated
# b) The MP files are copied into 'originals' directory
# c) Batch file runs correctly (calls RAMAS Metapop) and generates numbered output files

print '\nTEST 3: Metapop batch generation'

# Generate MP batch entries
mp_file_helper2.generateMpBatchEntry('SandLizard_1_modified_0001.mp', 1)
mp_file_helper2.generateMpBatchEntry('SandLizard_1_modified_0002.mp', 2)
mp_file_helper2.generateMpBatchEntry('SandLizard_1_modified_0003.mp', 3)

# Generate MP batch file
mp_file_helper2.output_directory['name'] = 'BatchTest'
mp_file_helper2.output_directory['path'] = test_directory + r'\BatchTest'
mp_file_helper2.generateMpBatchFile(pause=True)

# Run batch file (calls RAMAS Metapop)
chdir(test_directory + r'\BatchTest')
call('mp_batch.bat')

# END TEST 3

# TEST 4: Save and load generation data. Check that:
# a) Complex data (containing dictionaries, lists, and numpy arrays) saves to file as a serialised object
# b) Complex data loads from file in its original form

print '\nTEST 4: Save and load generation data'

# Example complex data
test_parameter_values1 = { 'Matrix 1' : np.array([[0.2, 0.2], [0.2, 0.2], [0.2, 0.2]]),
                          'Matrix 2' : np.array([[0.8, 0.6, 0.8], [0.8, 0.8, 0.8]]) }
multiplier1 = {'Matrix 1' : 1.1, 'Matrix 2' : 0.9}
test_parameter_values2 = { 'Matrix 1' : np.array([[1.6, 1.6], [1.6, 1.6], [1.6, 1.6]]),
                          'Matrix 2' : np.array([[2.4, 4.8, 2.4], [2.4, 2.4, 2.4]]) }
multiplier2 = {'Matrix 1' : 0.8, 'Matrix 2' : 1.2}
example_data = [{ 'sample' : 1, 'values' : test_parameter_values1, 'multipliers' : multiplier1 }, { 'sample' : 2, 'values' : test_parameter_values2, 'multipliers' : multiplier2 }]
print 'Original example data: ', example_data

# Save data
mp_file_helper1.output_directory['path'] = test_directory + '\GenerationDataTest'
mp_file_helper1.saveGenerationData(example_data)

# Load data
mp_file_helper1.loadGenerationData(test_directory + '\GenerationDataTest')
print 'Loaded example data: ', mp_file_helper1.generation_data

# END TEST 4

## TEST 5: Load Metapop Results. Check that:
## a) Collects an ordered list of the required result files in their generic form
## b) Appropriate warning when generation_data.dat missing
## c) Appropriate warning when batch results missing
## d) Result extraction:
##    i)     Result components are correctly extracted from result files
##    ii)    Results are correctly calculated from result components
##    iii)   Results are correctly extracted from multi-run result files
## e) Appropriate warning when batch results incomplete
## f) No warning when successfully loaded results
## g) Handle division by zero if total extinction risk = 1 when calculating final N for persistent runs
## h) Handle case when the first threshold value > 0 in IntExtRisk result file (total extinction risk = 0)
## i) Handle other quasi-extinction risk extraction cases:
##    i)     Quasi-extinction threshold falls below minimum threshold value in IntExtRisk result file (quasi-ext-risk = 0)
##    ii)    Quasi-extinction threshold falls above maximum threshold value in IntExtRisk result file (quasi-ext-risk = 1)
##    iii)   Quasi-extinction threshold falls between threshold values in IntExtRisk result file (linear interpolate)

print '\nTEST 5: Load Metapop Results'

results_directory_path_no_generation_data = test_directory + '\MpLoadResultsTest\NoGenerationData'
results_directory_path_batch_not_run = test_directory + '\MpLoadResultsTest\BatchNotRun'
results_directory_path_batch_incomplete = test_directory + '\MpLoadResultsTest\BatchIncomplete'
results_directory_path_batch_complete = test_directory + '\MpLoadResultsTest\BatchComplete'
results_directory_path_results_extraction = test_directory + '\MpLoadResultsTest\ResultsExtraction'

print '\na) required result file keys = ', mp_file_helper2.listOrderedRequiredResultFileKeys()
print '\nb) generation_data.dat missing: details = ', mp_file_helper2.loadMpResults(results_directory_path_no_generation_data)
print '\nc) batch results missing: details = ', mp_file_helper2.loadMpResults(results_directory_path_batch_not_run)

# Result extraction:
#   Note that for most variables line numbers will be case specific:
#   Expected Minimum Abundance: L14 of IntExtRisk.txt (value = 128.4)
#   Final N of occupied patches: L66 (4th column) of MetapopOcc.txt (value = 7.8)
#   Total extinction risk: L17 (2nd column) of IntExtRisk.txt (value = 0.004) i.e., it is the value where the population threshold = 0 
#   Quasi extinction risk: To get this value you need to read the threshold level from line 12 of QuasiExt.txt (i.e. "Time to quasi-extinction (Threshold level = 80.0)"). This threshold is then applied to the file IntExtRisk.txt to calculate Quasi extinction risk i.e., at Line 97 the threshold is 80 returning a probability of 0.2230
#   Final N of persistent runs: First read mean final N from L66 of Abund.txt. Then use the formula: mean Final N/ (1-total extinction risk)

# Result components
mp_file_helper2.results_directory = mp_file_helper2.splitPath(results_directory_path_results_extraction)
result_files = ['Abund_0001.txt', 'QuasiExt_0001.txt', 'IntExtRisk_0001.txt', 'MetapopOcc_0001.txt']
mp_file_helper2.loadGenerationData(results_directory_path_results_extraction)
result_components = mp_file_helper2.extractResultComponents(1, result_files)
print '\nd) i) Results components = ', result_components

# Calculate results
results = mp_file_helper2.calculateResultsFromComponents(result_components)
print 'd) ii) Calculated results = ', results
print 'Correct values are:'
print '  Expected Minimum Abundance = 128.4'
print '  Final number of occupied patches = 7.8'
print '  Total extinction risk = 0.004'
print '  Quasi extinction risk = 0.223'
print '  Final N for persistent runs = 1023.24'

print 'd) iii) Results for multiple runs:'
incomplete_details = mp_file_helper2.loadMpResults(results_directory_path_batch_incomplete)
incomplete_loaded_results = dict(mp_file_helper2.loaded_results)
print 'Incomplete loaded results = ', mp_file_helper2.loaded_results

mp_file_helper2.loaded_results = {}
complete_details = mp_file_helper2.loadMpResults(results_directory_path_batch_complete)
complete_loaded_results = dict(mp_file_helper2.loaded_results)
print 'Complete loaded results = ', mp_file_helper2.loaded_results

print '\ne) batch results incomplete: details = ', incomplete_details
print '\nf) successfully loaded results: details = ', complete_details

print '\ng) Handle division by zero if total extinction risk = 1 when calculating final N for persistent runs'
mp_file_helper2.results_directory = mp_file_helper2.splitPath(results_directory_path_results_extraction)
result_files = ['Abund_0002.txt', 'QuasiExt_0002.txt', 'IntExtRisk_0002.txt', 'MetapopOcc_0002.txt']
result_components = mp_file_helper2.extractResultComponents(2, result_files)
print 'Results components: '
print '  IntExtRisk:initial_ext_risk =', result_components['IntExtRisk.txt']['initial_ext_risk']
print '  Abund:mean_final_n =', result_components['Abund.txt']['mean_final_n']
results = mp_file_helper2.calculateResultsFromComponents(result_components)
print 'Calculated results: '
print '  Total extinction risk =', results['Total extinction risk']
print '  Final N for persistent runs =', results['Final N for persistent runs']
print results

print '\nh) Handle cases when first threshold value > 0 in IntExtRisk result file (total extinction risk = 0)'
result_files = ['Abund_0003.txt', 'QuasiExt_0003.txt', 'IntExtRisk_0003.txt', 'MetapopOcc_0003.txt']
result_components = mp_file_helper2.extractResultComponents(3, result_files)
print 'Results components: '
print '  IntExtRisk:initial_threshold =', result_components['IntExtRisk.txt']['initial_threshold']
print '  IntExtRisk:initial_ext_risk =', result_components['IntExtRisk.txt']['initial_ext_risk']
results = mp_file_helper2.calculateResultsFromComponents(result_components)
print 'Calculated results:'
print '  Total extinction risk =', results['Total extinction risk']
print '  Final N for persistent runs =', results['Final N for persistent runs']
print '    should equal result component:', result_components['Abund.txt']['mean_final_n']

print '\ni) Handle other quasi-extinction risk extraction cases:'
mp_file_helper2.results_directory = mp_file_helper2.splitPath(results_directory_path_results_extraction)
mp_file_helper2.loadGenerationData(results_directory_path_results_extraction)

print '\ni) i) Quasi-extinction threshold falls below minimum threshold value in IntExtRisk result file (quasi-ext-risk = 0)'
result_files = ['Abund_0003.txt', 'QuasiExt_0003.txt', 'IntExtRisk_0003.txt', 'MetapopOcc_0003.txt']
result_components = mp_file_helper2.extractResultComponents(3, result_files)
print 'Results components: '
print '  QuasiExt:quasi_ext_threshold =', result_components['QuasiExt.txt']['quasi_ext_threshold']
print '  IntExtRisk:initial_threshold =', result_components['IntExtRisk.txt']['initial_threshold']
print '  IntExtRisk:thresholds_to_quasi ='
print result_components['IntExtRisk.txt']['thresholds_to_quasi']
print '  IntExtRisk:ext_risk_to_quasi ='
print result_components['IntExtRisk.txt']['ext_risk_to_quasi']
results = mp_file_helper2.calculateResultsFromComponents(result_components)
print 'Calculated result: Quasi extinction risk =', results['Quasi extinction risk']

print '\ni) ii) Quasi-extinction threshold falls above maximum threshold value in IntExtRisk result file (quasi-ext-risk = 1)'
result_files = ['Abund_0004.txt', 'QuasiExt_0004.txt', 'IntExtRisk_0004.txt', 'MetapopOcc_0004.txt']
result_components = mp_file_helper2.extractResultComponents(4, result_files)
print 'Results components: '
print '  QuasiExt:quasi_ext_threshold =', result_components['QuasiExt.txt']['quasi_ext_threshold']
print '  IntExtRisk:initial_threshold =', result_components['IntExtRisk.txt']['initial_threshold']
print '  IntExtRisk:thresholds_to_quasi ='
print result_components['IntExtRisk.txt']['thresholds_to_quasi']
print '  IntExtRisk:ext_risk_to_quasi ='
print result_components['IntExtRisk.txt']['ext_risk_to_quasi']
results = mp_file_helper2.calculateResultsFromComponents(result_components)
print 'Calculated result: Quasi extinction risk =', results['Quasi extinction risk']

print '\ni) iii) Quasi-extinction threshold falls between threshold values in IntExtRisk result file (linear interpolate)'
result_files = ['Abund_0005.txt', 'QuasiExt_0005.txt', 'IntExtRisk_0005.txt', 'MetapopOcc_0005.txt']
result_components = mp_file_helper2.extractResultComponents(5, result_files)
print 'Results components: '
print '  QuasiExt:quasi_ext_threshold =', result_components['QuasiExt.txt']['quasi_ext_threshold']
print '  IntExtRisk:initial_threshold =', result_components['IntExtRisk.txt']['initial_threshold']
print '  IntExtRisk:thresholds_to_quasi ='
print result_components['IntExtRisk.txt']['thresholds_to_quasi']
print '  IntExtRisk:ext_risk_to_quasi ='
print result_components['IntExtRisk.txt']['ext_risk_to_quasi']
results = mp_file_helper2.calculateResultsFromComponents(result_components)
print 'Calculated result: Quasi extinction risk =', results['Quasi extinction risk'], '(should be 0.6633)'

# END TEST 5

# TEST 6: Generate result input and output files. Check that:
# a) Complete batch and full results produces correct input and output files
# b) Incomplete batch and partial results produces correct input and output files

print '\nTEST 6: Generate result input and output files'

# Using complete loaded results from test 5
mp_file_helper2.results_directory = mp_file_helper2.splitPath(results_directory_path_batch_complete)
mp_file_helper2.loadGenerationData(results_directory_path_batch_complete)
mp_file_helper2.generateInputAndOutputFiles(mp_file_helper2.config.metapop_results)
print 'a) Complete result_inputs.txt and result_outputs.txt generated in ', mp_file_helper2.results_directory['path']

mp_file_helper2.results_directory = mp_file_helper2.splitPath(results_directory_path_batch_incomplete)
mp_file_helper2.loadGenerationData(results_directory_path_batch_incomplete)
mp_file_helper2.loaded_results = incomplete_loaded_results
results = ['Final N for persistent runs', 'Total extinction risk', 'Quasi extinction risk']
mp_file_helper2.generateInputAndOutputFiles(results)
print 'b) Incomplete result_inputs.txt and result_outputs.txt generated in ', mp_file_helper2.results_directory['path']

# END TEST 6

# TEST 7: Generate Result Summary (including regression model). Check that:
# a) Perfect separation error occurs with several input parameters when sample number is small
# b) Generalised Linear Models run correctly on other occasions

print '\nTEST 7: Generate Result Summary (including regression model)'

results_directory_regression_model = test_directory + '\MpLoadResultsTest\RegressionModel'

# Load results and generate result input and output files
mp_file_helper2.loadMpResults(results_directory_regression_model)
mp_file_helper2.generateInputAndOutputFiles(mp_file_helper2.config.metapop_results)

print 'a) Perfect separation error occurs with several input parameters when sample number is small'
try :
    mp_file_helper2.generateResultSummary(mp_file_helper2.config.metapop_results)
except Exception, e :
    print 'ERROR:', e
# PerfectSeparationError when sample too small

print 'b) Generalised Linear Models run correctly on other occasions'

# Reduce the number of input parameters
mp_file_helper2.generation_data['parameters']['selected'].pop(3)
mp_file_helper2.generation_data['parameters']['selected'].pop(3)
mp_file_helper2.generation_data['parameters']['selected'].pop(3)
mp_file_helper2.generation_data['parameters']['selected'].pop(3)
mp_file_helper2.generation_data['parameters']['selected'].pop(3)

# Generate results summary
try :
    mp_file_helper2.generateResultSummary(mp_file_helper2.config.metapop_results)
except Exception, e :
    print 'ERROR:', e
print 'result_summary.txt generated in ', mp_file_helper2.results_directory['path']

# END TEST 7

# TEST 8: Generate Result Plots Data (including files). Check that:
# a) Result plot data is extracted from result files
# b) Result plot data files are generated

print '\nTEST 8: Generate Result Plots Data (including files)'

result_plots_directory = test_directory + '\MpLoadResultsTest\ResultPlots'

print 'a) Result plot data is extracted from result files, and transformed:'
mp_file_helper2.loadMpResults(result_plots_directory)
print mp_file_helper2.loaded_result_plots
#Check:
result_files = [['Abund_0001.txt', 'MetapopOcc_0001.txt'], ['Abund_0002.txt', 'MetapopOcc_0002.txt'],['Abund_0003.txt', 'MetapopOcc_0003.txt'],['Abund_0004.txt', 'MetapopOcc_0004.txt'],['Abund_0005.txt', 'MetapopOcc_0005.txt'],
                ['Abund_0006.txt', 'MetapopOcc_0006.txt'], ['Abund_0007.txt', 'MetapopOcc_0007.txt'],['Abund_0008.txt', 'MetapopOcc_0008.txt'],['Abund_0009.txt', 'MetapopOcc_0009.txt'],['Abund_0010.txt', 'MetapopOcc_0010.txt']]
abundance = np.zeros((51, 10))
occupancy = np.zeros((51, 10))
for i in range(10) :
    result_components = mp_file_helper2.extractResultComponents(i+1, result_files[i])
    abundance[:,i] = result_components['Abund.txt']['mean_n'][:,0]
    occupancy[:,i] = result_components['MetapopOcc.txt']['n_occ_patches'][:,0]
mean_abundance = abundance.mean(1)
mean_stdev_abundance = abundance.mean(1) + abundance.std(1)
stdev_mean_abundance = abundance.mean(1) - abundance.std(1)
mean_stdev2_abundance = abundance.mean(1) + 2*abundance.std(1)
stdev2_mean_abundance = abundance.mean(1) - 2*abundance.std(1)
min_abundance = abundance.min(1)
max_abundance = abundance.max(1)
mean_occupancy = occupancy.mean(1)
mean_stdev_occupancy = occupancy.mean(1) + occupancy.std(1)
stdev_mean_occupancy = occupancy.mean(1) - occupancy.std(1)
mean_stdev2_occupancy = occupancy.mean(1) + 2*occupancy.std(1)
stdev2_mean_occupancy = occupancy.mean(1) - 2*occupancy.std(1)
min_occupancy = occupancy.min(1)
max_occupancy = occupancy.max(1)
print '  Checking Abundance:'
print '    Time correct = ', (mp_file_helper2.loaded_result_plots['Abundance']['Time'] == np.arange(51)).all()
print '    Minimum correct = ', (mp_file_helper2.loaded_result_plots['Abundance']['Minimum'] == min_abundance).all()
print '    Mean-2SD correct = ', (mp_file_helper2.loaded_result_plots['Abundance']['Mean-2SD'] == stdev2_mean_abundance).all()
print '    Mean-1SD correct = ', (mp_file_helper2.loaded_result_plots['Abundance']['Mean-1SD'] == stdev_mean_abundance).all()
print '    Mean correct = ', (mp_file_helper2.loaded_result_plots['Abundance']['Mean'] == mean_abundance).all()
print '    Mean+1SD correct = ', (mp_file_helper2.loaded_result_plots['Abundance']['Mean+1SD'] == mean_stdev_abundance).all()
print '    Mean+2SD correct = ', (mp_file_helper2.loaded_result_plots['Abundance']['Mean+2SD'] == mean_stdev2_abundance).all()
print '    Maximum correct = ', (mp_file_helper2.loaded_result_plots['Abundance']['Maximum'] == max_abundance).all()
print '  Checking Patch Occupancy:'
print '    Time correct = ', (mp_file_helper2.loaded_result_plots['Patch Occupancy']['Time'] == np.arange(51)).all()
print '    Minimum correct = ', (mp_file_helper2.loaded_result_plots['Patch Occupancy']['Minimum'] == min_occupancy).all()
print '    Mean-2SD correct = ', (mp_file_helper2.loaded_result_plots['Patch Occupancy']['Mean-2SD'] == stdev2_mean_occupancy).all()
print '    Mean-1SD correct = ', (mp_file_helper2.loaded_result_plots['Patch Occupancy']['Mean-1SD'] == stdev_mean_occupancy).all()
print '    Mean correct = ', (mp_file_helper2.loaded_result_plots['Patch Occupancy']['Mean'] == mean_occupancy).all()
print '    Mean+1SD correct = ', (mp_file_helper2.loaded_result_plots['Patch Occupancy']['Mean+1SD'] == mean_stdev_occupancy).all()
print '    Mean+2SD correct = ', (mp_file_helper2.loaded_result_plots['Patch Occupancy']['Mean+2SD'] == mean_stdev2_occupancy).all()
print '    Maximum correct = ', (mp_file_helper2.loaded_result_plots['Patch Occupancy']['Maximum'] == max_occupancy).all()

print 'b) Result plot data files are generated:'
mp_file_helper2.generateResultPlotFiles()
for result_file in listdir(mp_file_helper2.results_directory['path']) :
    if result_file.count('Predicted_') :
        print '  ', result_file, 'generated'

# END Main program



