# Python modules
import pickle
import re
import string
from os import listdir, mkdir, path
from shutil import copyfile
from StringIO import StringIO
from time import time, localtime, strftime

# Python extension modules (requires extension installations)
import numpy as np
import pandas as pd
from patsy.builtins import *
import statsmodels.api as sm

# Tool library modules
from MpParameterBoundConstraintHelper import MpParameterBoundConstraintHelper
from PopulationMatrixGenerator import PopulationMatrixGenerator

# Global method to join numpy arrays (simplifies join defined in config)
def join_arrays(array1, array2) :
    return np.append(array1, array2, 1)

## MP (RAMAS Metapop) file extractor and generator helper
## * Extracts parameters from mp files into matrix structures via configured mappings
## * Creates a template of parameter placeholders for modified mp file generation
## * Generates modified mp files by substituting modified parameter values into the template
## * Generates a data frame file summarising the modified mp files
## * Generates a RAMAS Metapop batch file for running the modified mp files
## * Extracts results RAMAS Metapop result files
## * Generates a result summary for selected results
class MpFileExtractorAndGeneratorHelper :

    # Initialise with the Metapop config
    def __init__(self, mp_config) :

        self.config = mp_config

        # Maintain a copy of the parameter mapping from config
        self.parameter_mapping = self.copy_parameter_mapping()

        # Extracted parameters
        self.extracted_parameters = []

        # Parameter file links: { link_frame : [DataFrame], file_contents: {}, link_key, use_file_value : first/max }
        self.parameter_file_links = {}

        # Initialise parameters selected
        self.parameters_selected = []

        # Structure to store baseline file content and details
        self.baseline_mp_file = { 'path' : '', 'directory' : '', 'name' : '', 'lines' : [] }

        # Additional parameter values extracted from MP file
        self.additional_parameter_values = {}

        # Modified additional parameters to use when generating MP files
        self.modified_additional_parameter_values = {}

        # Additional parameters linked to baseline parameters (written to template)
        self.link_to_additional_parameters = {}

        # Data frame summarises generated MP files
        self.data_frame = []

        # RAMAS Metapop batch file for the generated MP files
        self.mp_batch = []

        # Create a MP parameter constraint helper
        self.mp_constraint_helper = MpParameterBoundConstraintHelper(self.config)

        # Compile a list of any parameter constraint violations marked with a * (for notes) in the data frame
        self.parameter_constraint_violations = {}

        # Initialise maximum MP file name width (for data frame formatting)
        self.maximum_mp_file_name_width = 0

        # Output template
        self.output_template = ''

        # Output directory
        self.output_directory = { 'name' : '', 'directory' : '', 'path' : '' }

        # Generation data: serialised to file for subsequent flexible cross-referencing with RAMAS Metapop outputs
        self.generation_data = {}

        # Results directory
        self.results_directory = { 'name' : '', 'directory' : '', 'path' : '' }

        # Loaded results from MP runs
        self.loaded_results = {}

        # Loaded result plots from MP runs
        self.loaded_result_plots = {}

    # Method resets stored helper variables associated with sampling file generation (not load)
    def reset_sampling_generation(self) :
        self.parameters_selected = []
        self.data_frame = []
        self.mp_batch = []
        self.parameter_constraint_violations = {}
        self.maximum_mp_file_name_width = 0
        self.modified_additional_parameter_values = {}
        self.output_template = ''
        self.output_directory = { 'name' : '', 'directory' : '', 'path' : '' }
    
    # Method resets stored helper variables associated with MP result loading
    def reset_result_load(self) :
        self.results_directory = { 'name' : '', 'directory' : '', 'path' : '' }
        self.loaded_results = {}
        self.loaded_result_plots = {}

    # Is the baseline MP file loaded?
    def isBaselineMpFileLoaded(self) :
        if self.baseline_mp_file['path'] :
            return True
        else :
            return False

    # Have MP results been loaded successfully?
    def mpResultsLoadedOk(self) :
        if self.loaded_results and self.loaded_result_plots:
            return True
        else :
            return False

    # Is the result plot data loaded
    def isResultPlotDataLoaded(self) :
        if self.loaded_result_plots :
            return True
        else :
            return False

    # Get the baseline MP file name
    def getBaselineMpFileName(self) :
        return self.baseline_mp_file['name']

    # Get the baseline MP file directory
    def getBaselineMpFileDirectory(self) :
        return self.baseline_mp_file['directory']

    # Get parameter file links
    def getParameterFileLinks(self) :
        return self.parameter_file_links

    # Get additional parameter value
    def getAdditionalParameterValue(self, key) :
        if self.additional_parameter_values.has_key(key) :
            return self.additional_parameter_values[key]
        else :
            return None

    # Get results plot data
    def getResultsPlotData(self) :
        return self.loaded_result_plots

    # Get the output directory for the current generation
    def getOutputDirectory(self) :
        return self.output_directory

    # Set the output directory for the current generation
    def setOutputDirectory(self, output_directory_path) :
        self.output_directory = self.splitPath(output_directory_path)

    # Modify additional parameter values when generating MP files (template)
    def modifyAdditionalParameterValues(self, modified_values) :
        for key, value in modified_values.items() :
            self.modified_additional_parameter_values[key] = value
    
    # Method loads baseline MP file 
    def loadBaselineMpFile(self, file_path) :

        # Split path into path, directory, and file name
        self.baseline_mp_file = self.splitPath(file_path)

        # Read file lines
        f = open(self.baseline_mp_file['path'])
        self.baseline_mp_file['lines'] = f.readlines()
        f.close()

    # Method splits path into a dictionary containing path, name (end), and (parent) directory
    def splitPath(self, full_path) :
        full_path = path.normpath(str(full_path))
        path_dictionary = { 'path' : full_path }
        split_path = path.split(full_path)
        path_dictionary['directory'] = split_path[0]
        path_dictionary['name'] = split_path[1]
        return path_dictionary

    # Method recursively creates a new directory path (eliminates duplicate existing subdirectories)
    def createDirectoryPath(self, dir_path) :
        root_dir_path = self.splitPath(dir_path)['directory']
        new_dir_name = self.splitPath(dir_path)['name']
        if not(path.exists(root_dir_path)) :
            root_dir_path = self.createDirectoryPath(root_dir_path)
        if new_dir_name == self.splitPath(root_dir_path)['name'] :
            return root_dir_path
        else :
            new_path = path.join(root_dir_path, new_dir_name)
            mkdir(new_path)
            return new_path
            
    # Create a copy of the parameter mapping from the config
    def copy_parameter_mapping(self) :
        return self.copy_dict_mapping(self.config.parameter_mapping)

    # Copy dictionary mapping (recursive)
    def copy_dict_mapping(self, dict_mapping) :
        mapping_copy = {}
        for key, item in dict_mapping.items() :
            if type(item) == dict :
                mapping_copy[key] = self.copy_dict_mapping(item)
            else :
                mapping_copy[key] = item
        return mapping_copy

    # Method extracts all configured parameters from a list of MP file contents
    def extractParametersFromMpFileContents(self) :

        # Resolve dynamic MP parameter mapping configuration
        if self.parameter_mapping.has_key('dynamic_variables') :
            self.resolveDynamicMpParameterMappingConfiguration(self.baseline_mp_file['lines'])

        # Copy parameter mapping from sectioned parameters to their subsets
        for parameter_key in self.config.parameters :
            if self.parameter_mapping[parameter_key].has_key('subset_of') :
                self.parameter_mapping[parameter_key].update(self.parameter_mapping[self.parameter_mapping[parameter_key]['subset_of']])

        # Copy values into a matrix for each parameter: 
        parameter_values = {}
        self.parameter_file_links = {}
        self.extracted_parameters = []
        for parameter_key in self.config.parameters :
            conditions_ok = True
            if self.parameter_mapping.has_key('conditions') :
                if self.parameter_mapping['conditions'].has_key(parameter_key) :
                    if not self.parameter_mapping['conditions'][parameter_key]['satisfied'] :
                        conditions_ok = False
            if conditions_ok :
                if self.parameter_mapping[parameter_key].has_key('layers') : # file links not implemented for layers
                    for layer_index in range(self.parameter_mapping[parameter_key]['layers']) :
                        if layer_index == 0 :
                            value_matrix = np.array([self.extractMatrixFromFileLines(self.baseline_mp_file['lines'], self.parameter_mapping[parameter_key])])
                        else :
                            next_layer_mapping = self.parameter_mapping[parameter_key].copy()
                            next_layer_mapping['start_row'] += next_layer_mapping['next_layer']*layer_index
                            next_layer_values = self.extractMatrixFromFileLines(self.baseline_mp_file['lines'], next_layer_mapping)
                            value_matrix = np.append(value_matrix, [next_layer_values], axis=0)
                else :
                    value_matrix = self.extractMatrixFromFileLines(self.baseline_mp_file['lines'], self.parameter_mapping[parameter_key])
                    if self.parameter_mapping[parameter_key].has_key('may_link_to_temporal_trend_files') :
                        if self.parameter_mapping[parameter_key]['may_link_to_temporal_trend_files'] :
                            link_frame = self.extractMatrixFromFileLines(self.baseline_mp_file['lines'], self.parameter_mapping[parameter_key], link_to_file=True)
                            if self.fileLinksExist(link_frame) :
                                self.parameter_file_links[parameter_key] = { 'file_contents' : {}, 'link_key' : parameter_key, 'link_frame' : link_frame, 'use_file_value' : '' }
                                if self.parameter_mapping[parameter_key].has_key('use_file_value') :
                                    self.parameter_file_links[parameter_key]['use_file_value'] = self.parameter_mapping[parameter_key]['use_file_value']
                if self.parameter_mapping[parameter_key].has_key('subset_of') and self.parameter_mapping[parameter_key].has_key('subset_mask') :
                    subset_mask = self.resolveSubsetMask(parameter_key, value_matrix)
                    value_matrix *= subset_mask
                if self.parameter_mapping[parameter_key].has_key('mask_values') :
                    value_mask = np.ones_like(value_matrix)
                    for mask_value in self.parameter_mapping[parameter_key]['mask_values'] :
                        value_mask *= (value_matrix == mask_value)
                if (value_matrix.flatten() != 0).max() : # has non-zero values including potential nan's from linked file names
                    if self.parameter_mapping[parameter_key].has_key('subset_of') and self.parameter_mapping[parameter_key].has_key('subset_mask') :
                        parameter_values[parameter_key] = np.ma.masked_array(value_matrix, mask=subset_mask*-1+1)
                    elif self.parameter_mapping[parameter_key].has_key('mask_values') :
                        parameter_values[parameter_key] = np.ma.masked_array(value_matrix, mask=value_mask)
                    else :
                        parameter_values[parameter_key] = value_matrix
                    self.extracted_parameters.append(parameter_key)

        # Extract any additional parameters that may be required
        self.additional_parameter_values = {}
        if self.parameter_mapping.has_key('additional') :
            for key, mapping in self.parameter_mapping['additional'].items() :

                # Extract
                link_to_trend_file = False
                if mapping.has_key('line') :
                    line_number = eval(str(mapping['line']))
                    line = self.baseline_mp_file['lines'][line_number-1]
                    self.additional_parameter_values[key] = eval(str(mapping['value']))
                elif mapping.has_key('value') :
                    self.additional_parameter_values[key] = mapping['value']
                else :
                    if mapping.has_key('may_link_to_temporal_trend_files') :
                        link_to_trend_file = mapping['may_link_to_temporal_trend_files']
                    value = self.extractMatrixFromFileLines(self.baseline_mp_file['lines'], mapping, link_to_file=link_to_trend_file)
                    if not link_to_trend_file :
                        if np.size(value) == 1 :
                            value = value.flatten().tolist().pop()
                    self.additional_parameter_values[key] = value

                # Link to parameters where required
                if mapping.has_key('link_to_parameter') :
                    self.link_to_additional_parameters[mapping['link_to_parameter']] = key
                    if link_to_trend_file and (mapping['link_to_parameter'] in self.extracted_parameters) :
                        if not self.parameter_file_links.has_key(mapping['link_to_parameter']) :
                            self.parameter_file_links[mapping['link_to_parameter']] = { 'link_frame' : self.additional_parameter_values[key], 'file_contents' : {}, 'link_key' : key, 'use_file_value' : '' }
                            if mapping.has_key('use_file_value') :
                                self.parameter_file_links[mapping['link_to_parameter']]['use_file_value'] = mapping['use_file_value']

        return parameter_values

    # Method resolves subset mask using parameter mapping
    def resolveSubsetMask(self, parameter_key, value_matrix) :
        mapping = self.parameter_mapping[parameter_key]#['subset_mask']
        subset_mask = np.zeros_like(value_matrix)
        if mapping['subset_mask'].has_key('whole_matrix') :
            subset_mask = self.resolveSubmatrixMask(subset_mask, mapping['subset_mask']['whole_matrix'])
        elif mapping['subset_mask'].has_key('quadrants') and mapping['subset_mask']['quadrants'].has_key('divide_at') :
            divider = mapping['subset_mask']['quadrants']['divide_at']
            if len(subset_mask.shape) == 3 :
                mask = subset_mask[0]
            else :
                mask = subset_mask
            if mapping['subset_mask']['quadrants'].has_key('upper_left') :
                mask[:divider,:divider] = self.resolveSubmatrixMask(mask[:divider,:divider], mapping['subset_mask']['quadrants']['upper_left'])
            if mapping['subset_mask']['quadrants'].has_key('lower_left') :
                mask[divider:,:divider] = self.resolveSubmatrixMask(mask[divider:,:divider], mapping['subset_mask']['quadrants']['lower_left'])
            if mapping['subset_mask']['quadrants'].has_key('upper_right') :
                mask[:divider,divider:] = self.resolveSubmatrixMask(mask[:divider,divider:], mapping['subset_mask']['quadrants']['upper_right'])
            if mapping['subset_mask']['quadrants'].has_key('lower_right') :
                mask[divider:,divider:] = self.resolveSubmatrixMask(mask[divider:,divider:], mapping['subset_mask']['quadrants']['lower_right'])
            if len(subset_mask.shape) == 3 :
               subset_mask[:] = mask
        return subset_mask

    # Method resolves a submatrix mask
    def resolveSubmatrixMask(self, submatrix, submatrix_mask_mapping) :

        # Zero 2D mask
        if len(submatrix.shape) == 3 : # layered
            mask = np.zeros_like(submatrix[0])
        else :
            mask = np.zeros_like(submatrix)
        row_mask = mask.copy()

        # Diagonal mask
        if submatrix_mask_mapping['include_diagonal'] :
            mask += np.eye(N=mask.shape[0], M=mask.shape[1], k=0)
        for i in np.arange(1, max(mask.shape)) :
            if submatrix_mask_mapping['partition'] is 'diagonal_upper_right' :
                mask += np.eye(N=mask.shape[0], M=mask.shape[1], k=i)
            elif submatrix_mask_mapping['partition'] is 'diagonal_lower_left' :
                mask += np.eye(N=mask.shape[0], M=mask.shape[1], k=-1*i)

        # Row inclusion mask
        if submatrix_mask_mapping['rows'] is 'first' :
            row_mask[0,:] = 1
        elif submatrix_mask_mapping['rows'] is 'all' :
            row_mask[:,:] = 1
        elif submatrix_mask_mapping['rows'] is 'below_first' :
            row_mask[1:,:] = 1

        # Combine masks and return (layered) mask
        mask *= row_mask
        submatrix_mask = np.zeros_like(submatrix)
        submatrix_mask[:] = mask
        return submatrix_mask

    # Method checks to see if file links exist
    def fileLinksExist(self, link_frame) :
        file_links_found = False
        for item in link_frame.get_values().flatten() :
            file_path = path.join(self.baseline_mp_file['directory'], str(item))
            if item and path.exists(file_path) :
                file_links_found = True
        return file_links_found

    # Method loads files linked to parameters
    def loadFilesLinkedToParameters(self) :
        for parameter_key, file_links in self.parameter_file_links.items() :
            for item in file_links['link_frame'].get_values().flatten() :
                file_path = path.join(self.baseline_mp_file['directory'], str(item))
                if item and path.exists(file_path) :
                    file_links['file_contents'][item] = pd.read_csv(file_path, header=None)
        return self.parameter_file_links

    # Method resolves dynamic MP parameter mapping configuration by extracting details from the MP file
    def resolveDynamicMpParameterMappingConfiguration(self, file_lines) :

        # Reset the copy of the parameter mapping
        self.parameter_mapping = self.copy_parameter_mapping()

        # Ignore comment lines if appropriate
        search_from_row = 1
        if self.parameter_mapping.has_key('search_for_dynamic_variables_from_row') :
            search_from_row = self.parameter_mapping['search_for_dynamic_variables_from_row']

        # Extract the dynamic variables from the file lines
        dynamic_variable_values = {}
        for name, dynamic_variable_map in self.parameter_mapping['dynamic_variables'].items() :

            # Extraction using regular expression patterns for line number or value extraction
            if dynamic_variable_map.has_key('pattern') :
                found = self.findPatternInFileLines(dynamic_variable_map['pattern'], file_lines, search_from_row)
                extract = dynamic_variable_map['value']
                if extract.find('line') >= 0 :
                    line = found['line']
                    dynamic_variable_values[name] = eval(extract)
                else : # formula containing match
                    match = found['match']
                    dynamic_variable_values[name] = eval(extract)

            # Extraction using matrix extraction (assumes single value 1x1 matrix)
            else :
                dynamic_variable_values[name] = int(self.extractMatrixFromFileLines(file_lines, dynamic_variable_map)[0,0])

        # Create the dynamic variables with their given values
        for name, value in dynamic_variable_values.items() :
            exec(name + ' = value')

        # Resolve options if any
        if self.parameter_mapping.has_key('options') :
            for parameter_key, options in self.parameter_mapping['options'].items() :
                for option_key, option in options.items() :
                    if option.has_key('value') :
                        line_number = eval(str(option['line']))
                        line = file_lines[line_number-1]
                        options[option_key] = eval(str(option['value']))
                    elif option.has_key('values') :
                        from_line = eval(str(option['from_line']))
                        lines = eval(str(option['lines']))
                        options[option_key] = []
                        for i in range(lines) :
                            line = file_lines[from_line-1+i]
                            options[option_key].append(eval(str(option['values'])))
                    elif option.has_key('value_list') :
                        line_number = eval(str(option['line']))
                        line = file_lines[line_number-1]
                        options[option_key] = eval(str(option['value_list']))

        # Resolve alternatives from options if any
        if self.parameter_mapping.has_key('alternatives') :
            for key, alternatives in self.parameter_mapping['alternatives'].items() :

                # Resolve and exchange alternative from options for parameters
                if self.parameter_mapping.has_key(key) and self.parameter_mapping[key].has_key('choose_alternative') :
                    chosen_option = self.parameter_mapping['options'][key].get(alternatives['option'])
                    if type(chosen_option) is list :
                        for option_value in chosen_option :
                            if alternatives.has_key(option_value) :
                                self.parameter_mapping[key] = alternatives[option_value]
                    else :
                        if alternatives[chosen_option].has_key('option') : # has nested options
                            nested_option = self.parameter_mapping['options'][key].get(alternatives[chosen_option]['option'])
                            self.parameter_mapping[key] = alternatives[chosen_option][nested_option]
                        else :
                            self.parameter_mapping[key] = alternatives[chosen_option]
                    if self.parameter_mapping[key].has_key('calculate_matrix') :
                        self.parameter_mapping[key]['calculate_matrix']['parameters'] = self.parameter_mapping['options'][key]

                # Resolve and exchange alternative from options for additional parameters
                elif self.parameter_mapping.has_key('additional') and self.parameter_mapping['additional'].has_key(key) and self.parameter_mapping['additional'][key].has_key('choose_alternative') :
                    chosen_option = self.parameter_mapping['options'][key].get(alternatives['option'])
                    if type(chosen_option) is list :
                        for option_value in chosen_option :
                            if alternatives.has_key(option_value) :
                                self.parameter_mapping['additional'][key] = alternatives[option_value]
                    else :
                        self.parameter_mapping['additional'][key] = alternatives[chosen_option]

                # Resolve and exchange alternative from options for parameter conditions
                elif key == 'conditions' :
                    for parameter_key, condition_alternatives in alternatives.items() :
                        if self.parameter_mapping['conditions'][parameter_key].has_key('choose_alternative') :
                            if condition_alternatives.has_key('precondition') and condition_alternatives.has_key('postcondition') :
                                precond_alt_key = self.parameter_mapping['options'][parameter_key].get(condition_alternatives['precondition']['option'])
                                precondition = condition_alternatives['precondition'][precond_alt_key]
                                if precondition.has_key('option') :
                                    precondition['values'] = self.parameter_mapping['options'][parameter_key][precondition['option']]
                                postcond_alt_key = self.parameter_mapping['options'][parameter_key].get(condition_alternatives['postcondition']['option'])
                                postconditions = { False : condition_alternatives['postcondition'][False][postcond_alt_key], True : condition_alternatives['postcondition'][True][postcond_alt_key] }
                                if postconditions[False].has_key('option') :
                                    postconditions[False]['values'] = self.parameter_mapping['options'][parameter_key][postconditions[False]['option']]
                                if postconditions[True].has_key('option') :
                                    postconditions[True]['values'] = self.parameter_mapping['options'][parameter_key][postconditions[False]['option']]
                                self.parameter_mapping['conditions'][parameter_key] = { 'precondition' : precondition, 'postconditions' : postconditions, 'satisfied' : False }
                            elif condition_alternatives.has_key('option') :
                                alt_key = self.parameter_mapping['options'][parameter_key].get(condition_alternatives['option'])
                                self.parameter_mapping['conditions'][parameter_key] = condition_alternatives[alt_key]
                                if self.parameter_mapping['conditions'][parameter_key].has_key('option') :
                                    option_key = self.parameter_mapping['conditions'][parameter_key].get('option')
                                    self.parameter_mapping['conditions'][parameter_key]['values'] = self.parameter_mapping['options'][parameter_key][option_key]

        # Resolve conditions if any
        if self.parameter_mapping.has_key('conditions') :
            for parameter_key, condition in self.parameter_mapping['conditions'].items() :
                if condition.has_key('line') :
                    if re.findall(condition['should_match'], file_lines[eval(condition['line'])-1]) :
                        condition['satisfied'] = True
                    else :
                        condition['satisfied'] = False
                elif condition.has_key('values') :
                    match_found = False
                    negation_found = False
                    for value in condition['values'] :
                        match_found = (match_found or (value in condition['match_any']))
                        if condition.has_key('match_none') :
                            negation_found = (negation_found or (value in condition['match_none']))
                    condition['satisfied'] = (match_found and not negation_found)
                elif condition.has_key('precondition') and condition.has_key('postconditions') :
                    precond_match_found = False
                    precond_negation_found = False
                    for precond_value in condition['precondition']['values'] :
                        precond_match_found = (precond_match_found or (precond_value in condition['precondition']['match_any']))
                        if condition['precondition'].has_key('match_none') :
                            precond_negation_found = (precond_negation_found or (precond_value in condition['precondition']['match_none']))
                    condition['precondition']['satisfied'] = (precond_match_found and not precond_negation_found)
                    postcondition = condition['postconditions'][condition['precondition']['satisfied']]
                    postcond_match_found = False
                    postcond_negation_found = False
                    for postcond_value in postcondition['values'] :
                        postcond_match_found = (postcond_match_found or (postcond_value in postcondition['match_any']))
                        if postcondition.has_key('match_none') :
                            postcond_negation_found = (postcond_negation_found or (postcond_value in postcondition['match_none']))
                    condition['satisfied'] = (postcond_match_found and not postcond_negation_found)
                elif condition.has_key('condition') :
                    condition['satisfied'] = eval(condition['condition'])

        # Include sectioned parameter mappings
        parameters = self.config.parameters[:] # copy
        for parameter_key in self.config.parameters :
            if self.parameter_mapping[parameter_key].has_key('subset_of') :
                sectioned_parameter = self.parameter_mapping[parameter_key]['subset_of']
                if sectioned_parameter not in parameters :
                    parameters.append(sectioned_parameter)

        # Insert the dynamic variable values into the parameter MP mapping configuration
        for parameter_key in parameters :
            for key, value in self.parameter_mapping[parameter_key].items() :
                if key in ['number_rows', 'number_columns', 'start_row', 'start_column', 'layers', 'next_layer'] and type(value) == str :
                    self.parameter_mapping[parameter_key][key] = eval(value)
                elif key is 'subset_mask' and value.has_key('quadrants') and value['quadrants'].has_key('divide_at') :
                    self.parameter_mapping[parameter_key]['subset_mask']['quadrants']['divide_at'] = eval(value['quadrants']['divide_at'])

        # Insert the dynamic variable values into any additional parameter MP mapping configuration
        if self.parameter_mapping.has_key('additional') :
            for parameter_key in self.parameter_mapping['additional'].keys() :
                if not self.parameter_mapping['additional'][parameter_key].has_key('line') :
                    for key, value in self.parameter_mapping['additional'][parameter_key].items() :
                        if key in ['number_rows', 'number_columns', 'start_row', 'start_column', 'value'] and type(value) == str :
                            self.parameter_mapping['additional'][parameter_key][key] = eval(value)

        # Insert the dynamic variable values into the omit_results_from_mp_template MP mapping configuration
        if self.parameter_mapping.has_key('omit_results_from_mp_template') :
            for key, value in self.parameter_mapping['omit_results_from_mp_template'].items() :
                if key in ['from_line', 'to_line'] and type(value) == str :
                    self.parameter_mapping['omit_results_from_mp_template'][key] = eval(value)

    # Method extracts a matrix of values from file lines given a specified mapping
    def extractMatrixFromFileLines(self, file_lines, mapping, link_to_file=False) :

        # Compile mapping specifications
        extraction = 'specified'
        delimiter = mapping['delimiter']
        from_row = mapping['start_row']
        if mapping.has_key('number_rows') and mapping.has_key('start_column') and mapping.has_key('number_columns') :
            extract = 'matrix'
            number_rows = mapping['number_rows']
            to_row = from_row + number_rows - 1
            from_column = mapping['start_column']
            number_columns = mapping['number_columns']
            to_column = from_column + number_columns - 1
        elif mapping.has_key('until_value_condition') and mapping.has_key('column') : # single column
            extraction = 'conditional'
            until_value_condition = mapping['until_value_condition']
            column = mapping['column']

        if mapping.has_key('under_diagonal_only') and extraction is 'specified' : # no link to file considered

            # Initialise as a zero matrix
            matrix = np.zeros(tuple([number_rows, number_columns]))

            # Extract the values below the main diagonal one row at a time
            for columns, row in enumerate(range(from_row, to_row)) :
                column_indexes = tuple(range(from_column-1, from_column+columns))
                value_array = np.genfromtxt(StringIO(file_lines[row]), delimiter=delimiter, usecols=column_indexes, autostrip=True)
                matrix[row-from_row+1, 0:columns+1] = value_array

            return matrix

        elif extraction is 'specified' :

            lines_string = string.join(file_lines[from_row-1:to_row], sep='')

            if link_to_file :
                if lines_string.strip() :
                    # Extract as a data frame
                    return pd.read_csv(StringIO(lines_string), header=None, delimiter=delimiter, na_filter=False, usecols=range(from_column-1, to_column))
                else :
                    return pd.DataFrame([])
            else :

                # Extract the values as a full matrix
                column_indexes = tuple(range(from_column-1, to_column))
                value_array = np.genfromtxt(StringIO(lines_string), delimiter=delimiter, usecols=column_indexes, autostrip=True)

                # Correctly shape the array to a matrix (necessary when single row or column)
                return np.reshape(value_array, (number_rows, number_columns))

        elif extraction is 'conditional' :

            # Iterate through file lines until condition satisfied or blank line
            line = file_lines[from_row-1]
            to_row = from_row
            if line.strip() :
                value = np.genfromtxt(StringIO(line), delimiter=delimiter, usecols=tuple(range(column-1, column)), autostrip=True)
            while line.strip() and len(file_lines) >= (to_row + 1) and not eval(str(value)+until_value_condition) :
                to_row += 1
                line = file_lines[to_row-1]
                if line.strip() :
                    value = np.genfromtxt(StringIO(line), delimiter=delimiter, usecols=tuple(range(column-1, column)), autostrip=True)

            # Return column down to row that satisfies condition or until blank line
            lines_string = string.join(file_lines[from_row-1:to_row], sep='')
            value_array = np.genfromtxt(StringIO(lines_string), delimiter=delimiter, usecols=tuple(range(column-1, column)), autostrip=True)

            # Correctly shape the array to a matrix (necessary when single row or column)
            return np.reshape(value_array, (to_row-from_row+1, 1))

    # Method constructs matrices defined as functions in MP file
    def constructFunctionDefinedMatrices(self) :

        calculated_parameter_values = {}

        # Collect any matrix calculation details from resolved mapping
        matrix_calculation_details = {}
        for parameter_key in self.extracted_parameters :
            if self.parameter_mapping[parameter_key].has_key('calculate_matrix') :
                matrix_calculation_details[parameter_key] = self.parameter_mapping[parameter_key]['calculate_matrix']

        # Calculate matrices from any details found
        if matrix_calculation_details :
            population_matrix_generator = PopulationMatrixGenerator(self.additional_parameter_values['population_coordinates']) 
            for parameter_key, details in matrix_calculation_details.items() :
                matrix_type = details.get('type')
                if matrix_type == 'population' :
                    calculated_parameter_values[parameter_key] = population_matrix_generator.calculateMatrix(details)

        return calculated_parameter_values

    # Method creates a generation template for a selection of parameters
    def createGenerationTemplate(self, parameter_list=[], write_template='') :

        # Set the selected parameter list
        self.parameters_selected = parameter_list

        # Create an output MP template
        template_lines = self.baseline_mp_file['lines'][:] # A copy

        # Omit result lines if required
        if self.parameter_mapping.has_key('omit_results_from_mp_template') and self.parameter_mapping['omit_results_from_mp_template']['omit'] :
            if type(self.parameter_mapping['omit_results_from_mp_template']['from_line']) is int and type(self.parameter_mapping['omit_results_from_mp_template']['to_line']) is int :
                if self.parameter_mapping['omit_results_from_mp_template']['from_line'] <= self.parameter_mapping['omit_results_from_mp_template']['to_line'] :
                    template_lines = self.baseline_mp_file['lines'][:self.parameter_mapping['omit_results_from_mp_template']['from_line']-1]
                    template_lines.append(self.baseline_mp_file['lines'][self.parameter_mapping['omit_results_from_mp_template']['to_line']])

        # Correct any file paths
        if self.parameter_mapping.has_key('additional') :
            for key, mapping in self.parameter_mapping['additional'].items() :
                if mapping.has_key('file_with_full_path') :
                    if self.additional_parameter_values[key] :
                        if not path.exists(self.additional_parameter_values[key]) :
                            local_path = path.join(self.baseline_mp_file['directory'], self.splitPath(self.additional_parameter_values[key])['name'])
                            if path.exists(local_path) :
                                self.modifyAdditionalParameterValues({ key : local_path })

        # Modify any additional parameter values (implemented for string and single integer values only)
        for key, value in self.modified_additional_parameter_values.items() :
            if self.parameter_mapping['additional'].has_key(key) :
                parameter_mapping = self.parameter_mapping['additional'][key]
                if parameter_mapping.has_key('start_row') :
                    template_lines[parameter_mapping['start_row']-1] = re.sub('\d+', str(value), template_lines[parameter_mapping['start_row']-1])
                elif parameter_mapping.has_key('line') :
                    template_lines[parameter_mapping['line']-1] = template_lines[parameter_mapping['line']-1].replace(str(self.additional_parameter_values[key]), str(value))

        # Ensure any existing $ characters are made safe for templating and remove new lines
        for index, line in enumerate(template_lines) :
            if '$' in line :
                template_lines[index] = template_lines[index].replace('$','$$')

        # Initialise template parameters
        template_parameters = self.parameters_selected[:] # A copy

        # Substitute the parent parameter when a parameter is a subset of another
        for parameter_key in self.parameters_selected :
            if self.parameter_mapping[parameter_key].has_key('subset_of') :
                template_parameters.remove(parameter_key)
                if not template_parameters.count(self.parameter_mapping[parameter_key]['subset_of']) :
                    template_parameters.append(self.parameter_mapping[parameter_key]['subset_of'])

        # Add linked additional parameters
        for parameter_key in self.parameters_selected :
            if self.link_to_additional_parameters.has_key(parameter_key) :
                template_parameters.append(self.link_to_additional_parameters[parameter_key])
     
        # Write MP template entries for each parameter 
        for parameter_key in template_parameters :

            # Get mapping for parameter
            if self.parameter_mapping['additional'].has_key(parameter_key) :
                mapping = self.parameter_mapping['additional'][parameter_key]
            else :
                mapping = self.parameter_mapping[parameter_key]

            # Determine number of layers
            if mapping.has_key('layers') :
                layers = mapping['layers']
            else :
                layers = 1

            # Build template entries for non-layered and layered parameters
            for layer_index in range(layers) :

                if mapping.has_key('layers') :
                    from_row = mapping['start_row'] + mapping['next_layer']*layer_index
                else :
                    from_row = mapping['start_row']
                number_rows = mapping['number_rows']
                to_row = from_row + number_rows - 1
                from_column = mapping['start_column']
                number_columns = mapping['number_columns']
                to_column = from_column + number_columns - 1
                delimiter = mapping['delimiter']

                # Pattern (regular expression) for line endings to preserve during template building
                regex_for_endings = '[ \t\r\f\v]+$|\s*#.*$'

                # Replace parameter row values with indexed template fields
                for index, row in enumerate(range(from_row-1, to_row)) :

                    # Preserve and remove line ending
                    line_ending = '\n'
                    ending_list = re.findall(regex_for_endings, template_lines[row])
                    if ending_list :
                       line_ending = ending_list.pop() + '\n'
                    template_lines[row] = string.replace(template_lines[row], line_ending, '')

                    # Add template field
                    if mapping.has_key('layers') :
                        template_key = string.replace(parameter_key,' ','_') + '_' + str(layer_index) + '_' + str(index)
                    else :
                        template_key = string.replace(parameter_key,' ','_') + '_' + str(index)
                    split_row = template_lines[row].split(delimiter)
                    if mapping.has_key('under_diagonal_only') :
                        if index :
                            split_row[from_column-1:from_column+index-1] = '$'
                            split_row[from_column-1] = '${' + template_key + '}'
                    else :
                        split_row[from_column-1:to_column] = '$'
                        split_row[from_column-1] = '${' + template_key + '}'
                    template_lines[row] = string.join(split_row,delimiter)

                    # Re-attach the line ending
                    template_lines[row] += line_ending

        # Join the lines of the output MP template
        self.output_template = string.join(template_lines, sep='')

        # For testing: Examine the MP template
        if write_template :
            f = open(self.output_directory['path'] + '\\' + write_template, 'w')
            f.write(self.output_template)
            f.close()

    # Method generates an MP file by substituting modified parameter values into the output template
    def generateModifiedMpFile(self, modified_parameter_values, file_number) :

        # Copy modified parameter values
        modified_parameter_values = self.copy_dict_mapping(modified_parameter_values)

        # Initialise template parameters
        template_parameters = self.parameters_selected[:] # A copy

        # Substitute the parent parameter when a parameter is a subset of another and merge modified values into parent
        for parameter_key in self.parameters_selected :
            if self.parameter_mapping[parameter_key].has_key('subset_of') :
                parent_key = self.parameter_mapping[parameter_key]['subset_of']
                template_parameters.remove(parameter_key)
                if not template_parameters.count(parent_key) :
                    template_parameters.append(parent_key)
                    modified_parameter_values[parent_key] = modified_parameter_values[parameter_key].data # assumed masked numpy array
                else :
                    modified_parameter_values[parent_key] += modified_parameter_values[parameter_key].data # assumed masked numpy array

        # Generate MP template substitution values for modified parameters
        template_substitution_values = {}
        for parameter_key in template_parameters :

            mapping = self.parameter_mapping[parameter_key]
            number_rows = mapping['number_rows']
            number_columns = mapping['number_columns']
            delimiter = mapping['delimiter']
            mp_format = self.config.parameter_output_format[parameter_key]['mp_format']

            # Determine number of layers
            if mapping.has_key('layers') :
                layers = mapping['layers']
            else :
                layers = 1

            # Build template substitution values for non-layered and layered parameters 
            for layer_index in range(layers) :

                # Single layer of modified parameter values
                if mapping.has_key('layers') :
                    single_layer_values = modified_parameter_values[parameter_key][layer_index, :]
                else :
                    single_layer_values = modified_parameter_values[parameter_key]

                # Generate a delimited string of modified values for each row or line
                for index in range(0, number_rows) :

                    # Extract the modified row values and convert them to a single row matrix
                    modified_value_matrix = np.array([])
                    if mapping.has_key('under_diagonal_only') :
                        if index :
                            modified_value_matrix = np.reshape(single_layer_values[index,0:index], (1, index))
                    else :
                        modified_value_matrix = np.reshape(single_layer_values[index,:], (1, number_columns))

                    # Generate the delimited modified value string for template substitution
                    if modified_value_matrix.size :

                        # Write modified matrix to string
                        string_buffer = StringIO()
                        np.savetxt(string_buffer, modified_value_matrix, fmt=mp_format, delimiter=delimiter, newline='')
                        substitution_string = string_buffer.getvalue()

                        # Substitute indexed linked file names (implemented as single column only)
                        if self.parameter_file_links.has_key(parameter_key) :
                            link_frame_entry = self.parameter_file_links[parameter_key]['link_frame'].iat[index, 0]
                            if self.parameter_file_links[parameter_key]['file_contents'].has_key(link_frame_entry) :
                                link_file_ext = string.split(link_frame_entry, '.').pop()
                                link_frame_entry = string.replace(link_frame_entry, ('.' + link_file_ext), (self.config.file_generation_numbering_format % file_number + '.' + link_file_ext))
                                if self.parameter_file_links[parameter_key]['link_key'] == parameter_key :
                                    substitution_string = link_frame_entry
                            if self.parameter_file_links[parameter_key]['link_key'] != parameter_key :
                                template_key = string.replace(self.parameter_file_links[parameter_key]['link_key'],' ','_') + '_' + str(index)
                                template_substitution_values[template_key] = link_frame_entry

                        # Set template substitutions for parameter
                        if mapping.has_key('layers') :
                            template_key = string.replace(parameter_key,' ','_') + '_' + str(layer_index) + '_' + str(index)
                        else :
                            template_key = string.replace(parameter_key,' ','_') + '_' + str(index)
                        template_substitution_values[template_key] = substitution_string

        # Substitute modified values into the output MP template
        template = string.Template(self.output_template)
        modified_mp_string = template.substitute(template_substitution_values)

        # Construct output file name from baseline file
        file_ext = string.split(self.baseline_mp_file['name'], '.').pop()
        modified_file_name = self.baseline_mp_file['name'].replace(('.' + file_ext), ('_modified' + self.config.file_generation_numbering_format % file_number + '.' + file_ext))
        #modified_file_name = string.split(self.baseline_mp_file['name'], '.')[0] + '_modified' + self.config.file_generation_numbering_format % file_number + '.mp'
        if string.find(modified_file_name, '_baseline') > -1 :
            modified_file_name = modified_file_name.replace('_baseline', '')

        # Write modified output file
        f = open(self.output_directory['path'] + '\\' + modified_file_name, 'w')
        f.write(modified_mp_string)
        f.close()

        # Set maximum MP file name width
        if self.maximum_mp_file_name_width < len(modified_file_name) :
            self.maximum_mp_file_name_width = len(modified_file_name)

        return modified_file_name

    # Method generates the modified linked files
    def generateModifiedLinkedFiles(self, modified_linked_file_contents, file_number) :
        filenames = []
        for parameter_key, file_links in modified_linked_file_contents.items() :
            if parameter_key in self.parameters_selected :
                for filename, contents in file_links.items() :
                    file_ext = string.split(filename, '.').pop()
                    filename = filename.replace(('.' + file_ext), (self.config.file_generation_numbering_format % file_number + '.' + file_ext))
                    output_file_path = path.join(self.output_directory['path'], filename)
                    if not self.config.parameter_data_types.has_key(parameter_key) : # float
                        pd.DataFrame(contents).to_csv(output_file_path, header=False, index=False, float_format=self.config.parameter_output_format[parameter_key]['mp_format'])
                    else : # assume integer
                        pd.DataFrame(contents).to_csv(output_file_path, header=False, index=False)
                    filenames.append(filename)
        return filenames

    # Method copies unmodified linked files to the output directory
    def copyUnmodifiedLinkedFiles(self) :
        
        filenames = []

        # Copy linked files for parameters that were not selected
        for parameter_key, file_links in self.parameter_file_links.items() :
            if parameter_key not in self.parameters_selected :
                for filename in file_links['file_contents'].keys() :
                    if path.exists(path.join(self.baseline_mp_file['directory'], filename)) :
                        copyfile(path.join(self.baseline_mp_file['directory'], filename), path.join(self.output_directory['path'], filename))
                        filenames.append(filename)

        # Copy other linked files from additional parameters
        for key, value_frame in self.additional_parameter_values.items() :
            if self.parameter_mapping['additional'][key].has_key('copy_files') :
                if self.parameter_mapping['additional'][key]['copy_files'] :
                    for item in value_frame.get_values().flatten() :
                        source_file_path = path.join(self.baseline_mp_file['directory'], str(item))
                        if item and path.exists(source_file_path) :
                            copyfile(source_file_path, path.join(self.output_directory['path'], item))
                            filenames.append(item)

        return filenames

    # Method generates a time-stamped directory within the current output directory
    def generateTimestampedOutputDirectory(self) :

        # Create directory name from date and time
        timestamped_dir_name = strftime("%d%b%Y_%I%M%p_%S", localtime()) + '.' + string.split('%.3f' % time(), '.')[1] + 's'

        # Create the directory within the current output directory
        new_ouput_path = self.createDirectoryPath(path.join(self.output_directory['path'], timestamped_dir_name))
        self.setOutputDirectory(new_ouput_path)

        # Add timestamped directory name to output directory structure
        self.output_directory['timestamped'] = timestamped_dir_name

        return self.output_directory

    # Method generates a data frame entry for the corresponding generated MP file
    def generateDataFrameEntry(self, mp_file_name, modified_parameter_values, multipliers) :

        # Generated MP file name
        file_heading = self.config.data_frame_mp_file_heading
        file_heading_width = max(self.maximum_mp_file_name_width, len(file_heading))
        padding = file_heading_width - len(mp_file_name)
        frame_line = mp_file_name + (('%' + str(padding) + 's') % '')

        # Data frame entry details for generation data collection
        entry_details = {}

        # Selected parameter values or percentage change (when multiple values)
        for parameter_key in self.parameters_selected :

            # Data field appendage default to space so marker for notes stands out
            data_field_appendage = ' ' * len(self.config.data_frame_notes_marker)

            # Extract data only from masked values
            if type(modified_parameter_values[parameter_key]) is np.ma.MaskedArray :
                modified_parameter_values[parameter_key] = modified_parameter_values[parameter_key].data

            # Determine if the parameter value(s) violate any constraints
            constraint_violations = self.mp_constraint_helper.checkParameterValuesAgainstConstraints(parameter_key, modified_parameter_values[parameter_key])
            if constraint_violations : # append violations to maintain a unique set
                if self.parameter_constraint_violations.has_key(parameter_key) :
                    for new_violation in constraint_violations :
                        contained_within_existing = False
                        for existing_violation in self.parameter_constraint_violations[parameter_key] :
                            if new_violation['constraint_type'] == existing_violation['constraint_type'] and new_violation['violation'] == existing_violation['violation'] :
                                contained_within_existing = True
                        if not(contained_within_existing) :
                            self.parameter_constraint_violations.has_key(parameter_key).append(new_violation)
                else :
                    self.parameter_constraint_violations[parameter_key] = constraint_violations
                data_field_appendage = self.config.data_frame_notes_marker

            # Add data frame entry details for parameter
            entry_details[parameter_key] = { 'constraint_violations' : constraint_violations }

            self.modified_parameter_values = modified_parameter_values # TEST

            # Determine if value sums are involved
            sum_values = False
            if self.config.parameter_data_frame.has_key(parameter_key) :
                sum_values = (self.config.parameter_data_frame[parameter_key] == 'sum_values')

            # Substitute any linked file values when not summed
            if self.parameter_file_links.has_key(parameter_key) and not sum_values :
                values = []
                for i, value in enumerate(modified_parameter_values[parameter_key]) :
                    link_frame_entry = self.parameter_file_links[parameter_key]['link_frame'].iat[i, 0]
                    if self.parameter_file_links[parameter_key]['file_contents'].has_key(link_frame_entry) :
                        file_contents = self.parameter_file_links[parameter_key]['file_contents'][link_frame_entry]
                        modified_file_values = file_contents.get_values()*multipliers[parameter_key]
                        values.extend(modified_file_values.flatten().tolist())
                    else :
                        values.extend(value.flatten().tolist())
                modified_parameter_values[parameter_key] = np.array(values)

            # Determine if multiple values are involved 
            unique_values = list(set(modified_parameter_values[parameter_key].flatten()))

            # Resolve and use value for data frame
            if len(unique_values) > 1 and not sum_values :
                # Use multiplier percentage data_frame_percent_format in data frame
                entry_details[parameter_key]['unique'] = False
                entry_details[parameter_key]['value'] = multipliers[parameter_key]*100
                output_format = self.config.parameter_output_format[parameter_key]['output_file_percent_format']
                field_width = self.config.data_frame_percent_width - len(data_field_appendage)
                output_format = output_format.replace(self.config.data_frame_field_width_substitution, str(field_width))
                frame_line += ((output_format % entry_details[parameter_key]['value']) + data_field_appendage)
            else :
                # Use unique parameter value or sum of values
                if sum_values :
                    unique_value = modified_parameter_values[parameter_key].flatten().sum()
                else :
                    unique_value = unique_values[0]
                entry_details[parameter_key]['unique'] = True
                entry_details[parameter_key]['value'] = unique_value
                output_format = self.config.parameter_output_format[parameter_key]['output_file_format']
                field_width = self.config.data_frame_field_width - len(data_field_appendage)
                output_format = output_format.replace(self.config.data_frame_field_width_substitution, str(field_width))
                frame_line += ((output_format % entry_details[parameter_key]['value']) + data_field_appendage)

            # Resolve and use value for results
            if self.config.parameter_result_input.has_key(parameter_key) and self.config.parameter_result_input[parameter_key] != 'unique_or_percent' :
                if type(self.config.parameter_result_input[parameter_key]) == list :
                    result_values = []
                    for result_input in self.config.parameter_result_input[parameter_key] :
                        if result_input == 'min_non_zero' :
                            min_non_zero = max(unique_values)
                            for unique_value in unique_values :
                                if unique_value > 0 and unique_value < min_non_zero :
                                    min_non_zero = unique_value
                            result_values.append(min_non_zero)
                        elif result_input == 'max' :
                            result_values.append(max(unique_values))
                    entry_details[parameter_key]['result_value'] = result_values
                else : # string
                    if self.config.parameter_result_input[parameter_key] == 'first_value' :
                        entry_details[parameter_key]['result_value'] = modified_parameter_values[parameter_key].flatten()[0]
                    elif self.config.parameter_result_input[parameter_key] == 'sum_values' :
                        entry_details[parameter_key]['result_value'] = modified_parameter_values[parameter_key].sum()
                    elif self.config.parameter_result_input[parameter_key] == 'percent_change' :
                        entry_details[parameter_key]['result_value'] = multipliers[parameter_key]*100
                    elif self.config.parameter_result_input[parameter_key] == 'last_non_zero' :
                        result_value = 0
                        for value in modified_parameter_values[parameter_key].flatten() :
                            if value > 0 :
                                result_value = value
                        entry_details[parameter_key]['result_value'] = result_value
            else : # default 'unique_or_percent'
                if len(unique_values) > 1 :
                    entry_details[parameter_key]['result_value'] = multipliers[parameter_key]*100
                else :
                    entry_details[parameter_key]['result_value'] = unique_values[0]

        # Add the frame line to the data frame
        self.data_frame.append(frame_line + '\n')

        # Return data frame entry details for generation data collection
        return entry_details        

    # Method generates a data frame file summarising the generated MP files
    def generateDataFrameFile(self) :

        # Insert column headings (given maximum file name width is now known)
        file_heading = self.config.data_frame_mp_file_heading
        file_heading_width = max(self.maximum_mp_file_name_width, len(file_heading))

        # Allow space for note markers to stand out
        field_appendage = ' ' * len(self.config.data_frame_notes_marker)

        # Multi-line headings (for data frame in v0.3)
        for index in range(self.config.data_frame_heading_lines) :

            line_number = index + 1

            # Run/sample heading
            if line_number == 1 :
                padding = file_heading_width - len(file_heading)
                heading_line = file_heading + (('%' + str(padding) + 's') % '')
            else :
                heading_line = (('%' + str(file_heading_width) + 's') % '')
        
            # Selected parameter headings
            for parameter_key in self.parameters_selected :
                parameter_heading = self.config.parameter_output_format[parameter_key]['output_file_heading']
                if type(parameter_heading) is str :
                    if line_number == 1 :
                        heading = parameter_heading
                    else :
                        heading = ''
                elif type(parameter_heading) is list :
                    heading = parameter_heading[index]
                field_width = self.config.data_frame_field_width - len(field_appendage)
                output_format = '%' + str(field_width) + 's'
                heading_line += ((output_format % heading) + field_appendage)
            
            # Add the heading line to front of the data frame
            self.data_frame.insert(index, heading_line + '\n')

        # Add parameter constraint violation notes if any
        if self.parameter_constraint_violations :
            notes = self.config.data_frame_notes_marker.strip() + ' Parameter values outside of constraints:\n'
            for parameter_key in self.parameters_selected :
                if self.parameter_constraint_violations.has_key(parameter_key) :
                    notes += ('  - ' + self.mp_constraint_helper.parameterConstraintViolationsToString(parameter_key, self.parameter_constraint_violations[parameter_key]) + '\n')
            self.data_frame.append('\n' + notes)

        # Write the data frame file
        f = open(self.output_directory['path'] + r'\data_frame.txt', 'w')
        f.writelines(self.data_frame)
        f.close()

    # Method generates a MP batch file entry for the corresponding generated MP file
    def generateMpBatchEntry(self, mp_file_name, file_number) :

        # Metapop execution line
        self.mp_batch.append(r'START /WAIT "R_SAM" "' + self.config.metapop_exe_location + r'" "' + mp_file_name + r'" /RUN=YES /TEX' + '\n')

        # Rename the Metapop result files
        for result_file in self.config.metapop_result_files :
            modified_file_name = string.split(result_file, '.')[0] + self.config.file_generation_numbering_format % file_number + '.' + string.split(result_file, '.')[1]
            self.mp_batch.append('RENAME ' + result_file + ' ' + modified_file_name + '\n')

    # Method generates the MP batch file. Also makes copies of the original generated MP files.
    def generateMpBatchFile(self, pause=False) :

        # Make a copy of the original MP files
        self.mp_batch.insert(0, 'MKDIR original\n')
        self.mp_batch.insert(1, 'COPY *.mp original\n')

        # Pause at the end of the batch
        if pause :
            self.mp_batch.append('PAUSE\n')
        
        # Write the data frame file
        f = open(self.output_directory['path'] + r'\mp_batch.bat', 'w')
        f.writelines(self.mp_batch)
        f.close()

    # Method saves data as a serialised object to a file
    def saveGenerationData(self, generation_data) :
        f = open(self.output_directory['path'] + r'\generation_data.dat', 'w')
        pickle.dump(generation_data, f)
        f.close()

    # Method checks for existing generation data file in output directory
    def outputDirectoryContainsGeneratedData(self) :
        return path.exists(path.join(self.output_directory['path'], 'generation_data.dat'))

    # Method checks if the output directory is empty
    def outputDirectoryIsEmpty(self) :
        if listdir(self.output_directory['path']) :
            return False
        else : # no contents
            return True

    # Method loads generation data from a file containing serialised object
    def loadGenerationData(self, directory_path) :
        f = open(directory_path + r'\generation_data.dat', 'r')
        self.generation_data = pickle.load(f)
        f.close()

    # Method loads MP results from specified directory. Returns warnings if results can't be loaded.
    def loadMpResults(self, results_directory_path) :

        self.reset_result_load()
        result_load_details = { 'result_sets_loaded' : 0, 'warnings' : [] }

        # Check that the directory contains file: generation_data.dat
        if listdir(results_directory_path).count('generation_data.dat') :

            # Load generation data
            self.loadGenerationData(results_directory_path)

            # Collect expected MP result file names corresponding to generated MP parameter samples and check that they are present in the results directory
            result_filenames = {}
            expected_result_sets = len(self.generation_data['samples'])
            numbering_format = self.generation_data['file_generation_numbering_format']
            for sample_details in self.generation_data['samples'] :

                # Construct an ordered (according to dependencies) list of required result files present for each sample/run
                result_filenames_present = []
                for result_file_key in self.listOrderedRequiredResultFileKeys() :
                    result_file_name = string.split(result_file_key, '.')[0] + numbering_format % sample_details['sample_number'] + '.' + string.split(result_file_key, '.')[1]
                    if listdir(results_directory_path).count(result_file_name) :
                        result_filenames_present.append(result_file_name)

                # Add list of required files for sample/run if complete
                if len(result_filenames_present) == len(self.listOrderedRequiredResultFileKeys()) :
                    result_filenames[sample_details['sample_number']] = result_filenames_present
            
            # Extract results from the result files for the samples/runs where all required files were present
            if result_filenames :

                # Set results directory
                self.results_directory = self.splitPath(results_directory_path)

                # Extract results from result files
                self.extractResults(result_filenames) 

                # Warn if some required result files were missing
                if len(result_filenames) < len(self.generation_data['samples']) :
                    result_load_details['warnings'].append('Directory only contains expected result files for ' + str(len(result_filenames)) + ' of ' + str(len(self.generation_data['samples'])) + ' runs')
                
                result_load_details['result_sets_loaded'] = len(result_filenames)
            else :
                result_load_details['warnings'].append('Directory does not contain the expected result files')
        else :
            result_load_details['warnings'].append('Directory is missing generation_data.dat')
        
        return result_load_details

    # Method collects an ordered list (according to dependencies) of the required result file keys (file names not appended with sample/run number)
    def listOrderedRequiredResultFileKeys(self) :
        ordered_file_keys = self.config.metapop_result_component_mapping.keys()
        for file_key, dependencies in self.config.metapop_result_file_dependencies.items() :
            for depends_on in dependencies['dependent_on'] :
                if ordered_file_keys.index(file_key) < ordered_file_keys.index(depends_on) :
                    ordered_file_keys.remove(depends_on)
                    ordered_file_keys.insert(ordered_file_keys.index(file_key), depends_on)
        return ordered_file_keys

    # Method extracts results from the listed result files
    def extractResults(self, result_filenames) :

        # Extract for each sample/run
        result_plots_data = {}
        for sample_number, result_files in result_filenames.items() :

            # Extract the result components
            result_components = self.extractResultComponents(sample_number, result_files)

            # Calculate results from result components
            self.loaded_results[sample_number] = self.calculateResultsFromComponents(result_components)

            # Calculate result plot lists from result components
            result_plots_data[sample_number] = self.calculateResultsFromComponents(result_components, plot_list=True)

        # Transform and calculate result plot data
        self.loaded_result_plots = self.transformAndCalculateResultPlotsData(result_plots_data)

    # Method extracts the result components from the result files 
    def extractResultComponents(self, sample_number, result_files) :

        # Read the files and extract the result components
        result_components = {}
        filename_appendage = self.generation_data['file_generation_numbering_format'] % sample_number
        for result_file in result_files :

            # Read file lines
            f = open(self.results_directory['path'] + '\\' + result_file)
            result_file_lines = f.readlines()
            f.close()

            # Extract the result components
            result_file_key = result_file.replace(filename_appendage, '')
            result_components[result_file_key] = {}
            component_mapping = self.copy_dict_mapping(self.config.metapop_result_component_mapping[result_file_key])
            for component_key in component_mapping['process_order'] :

                # Components using regular expression patterns for line number or value extraction
                if component_mapping[component_key].has_key('pattern') :
                    found = self.findPatternInFileLines(component_mapping[component_key]['pattern'], result_file_lines)
                    extract = component_mapping[component_key]['value']
                    if extract == 'line' :
                        result_components[result_file_key][component_key] = found['line']
                    else : # formula containing match
                        match = found['match']
                        result_components[result_file_key][component_key] = eval(extract)

                # Components dependent on other result components
                elif component_mapping[component_key].has_key('dependent_on') :
                    dependent_on_result = component_mapping[component_key]['dependent_on']['result_file']
                    dependent_on_component = component_mapping[component_key]['dependent_on']['component']
                    result_components[result_file_key][component_key] = result_components[dependent_on_result][dependent_on_component]

                # Components using matrix extraction
                else :
                    for key, value in result_components[result_file_key].items() :
                        exec(key + ' = value')
                    for key, value in component_mapping[component_key].items() :
                        if key in ['number_rows', 'number_columns', 'start_row', 'start_column'] and type(value) == str :
                            component_mapping[component_key][key] = eval(value)
                        elif key is 'until_value_condition' :
                            for other_key, other_value in result_components[result_file_key].items() :
                                if value.count(other_key) :
                                    component_mapping[component_key][key] = value.replace(other_key, str(other_value))
                    #try :
                    result_components[result_file_key][component_key] = self.extractMatrixFromFileLines(result_file_lines, component_mapping[component_key])
                    #except Exception, e :
                    #    result_components[result_file_key][component_key] = component_mapping[component_key]['default_value']
                 
        return result_components

    # Method calculates results, or result plot lists, from result components
    def calculateResultsFromComponents(self, result_components, plot_list=False) :
        results = {}
        if plot_list :
            result_mapping = self.config.metapop_result_plot_mapping
        else :
            result_mapping = self.config.metapop_result_mapping
        for result_key, mapping in result_mapping.items() :

            # Collect component values
            for component in mapping['collect'] :
                name = component['component']
                value = result_components[component['result_file']][component['component']]
                exec(name + ' = value')

            # Calculate result value
            value = mapping['value']
            if mapping.has_key('condition') :
                condition_satisfied = eval(mapping['condition'])
                if type(condition_satisfied) == np.ndarray :
                    condition_satisfied = condition_satisfied[0,0]
                if not condition_satisfied :
                    value = mapping['alt_value']
            linear_interpolate = self.linearInterpolate
            result = eval(value)

            # Unless plot list, extract matrix value (assumes 1 by 1 matrix)
            if not plot_list and type(result) == np.ndarray :
                result = result[0,0]

            results[result_key] = result

        return results

    # Method transforms and calculates result plots data
    def transformAndCalculateResultPlotsData(self, result_plots_data) :
        transformed_data = {}
        for sample_number, plots_data in result_plots_data.items() :
            for plot_key, plot_data in plots_data.items() :
                array_shape = list(plot_data.shape)
                array_shape.insert(0,1)
                if not transformed_data.has_key(plot_key) :
                    transformed_data[plot_key] = plot_data.reshape(array_shape)
                else :
                    transformed_data[plot_key] = np.append(transformed_data[plot_key], plot_data.reshape(array_shape), 0)
        calculated_data = {}
        for plot_key, plots_data in transformed_data.items() :
            calculated_data[plot_key] = {}
            for plot_field in self.config.result_plot_calculated_data[plot_key]['fields'] :
                if plot_field in self.config.result_plot_calculated_data[plot_key]['calculations'].keys() :
                    extracted_field = self.config.result_plot_calculated_data[plot_key]['calculations'][plot_field]['field']
                    extracted_index = self.config.metapop_result_plot_mapping[plot_key]['fields'].index(extracted_field)
                    calculation = self.config.result_plot_calculated_data[plot_key]['calculations'][plot_field]['calculate']
                    mean = plots_data[:,:,extracted_index].mean(0)
                    stdev = plots_data[:,:,extracted_index].std(0)
                    minimum = plots_data[:,:,extracted_index].min(0)
                    maximum = plots_data[:,:,extracted_index].max(0)
                    calculated_data[plot_key][plot_field] = eval(calculation)
                else : # use first column
                    extracted_index = self.config.metapop_result_plot_mapping[plot_key]['fields'].index(plot_field)
                    calculated_data[plot_key][plot_field] = plots_data[0,:,extracted_index]
        return calculated_data

    # Method performs a linear interpolation between the last 2 entries of the results if possible
    def linearInterpolate(self, target_threshold, thresholds_to_target, ext_risk_to_target) :
        thresholds_to_target = thresholds_to_target.flatten().tolist()
        ext_risk_to_target = ext_risk_to_target.flatten().tolist()
        size = len(thresholds_to_target)
        upper_threshold = thresholds_to_target.pop()
        upper_ext_risk = ext_risk_to_target.pop()
        if upper_threshold > target_threshold :
            if size > 1 :
                lower_threshold = thresholds_to_target.pop()
                lower_ext_risk = ext_risk_to_target.pop()
                if lower_threshold <= target_threshold and upper_threshold != lower_threshold :
                    return lower_ext_risk + (upper_ext_risk - lower_ext_risk)*(target_threshold - lower_threshold)/(upper_threshold - lower_threshold)
            else :
                return 0.0
        else :
            return upper_ext_risk

    # Method searches file lines for first occurrence of matching regular expression
    def findPatternInFileLines(self, find_pattern, file_lines, search_from_row=1) :
        found = { 'match' : None, 'line' : None }
        line = search_from_row
        search_file_lines = file_lines[(search_from_row-1):]
        for file_line in search_file_lines :
            if not(found['match']) :
                match = re.findall(find_pattern, file_line)
                if match :
                    found['match'] = match.pop()
                    found['line'] = line
            line += 1
        return found

    # Method generates the result input and output files for selected results
    def generateInputAndOutputFiles(self, selected_results) :

        result_input_lines = []
        result_output_lines = []

        # Extract details from loaded generation data
        numbering_format = self.generation_data['file_generation_numbering_format']
        modified_parameters = self.generation_data['parameters']['selected']

        # Insert column headings
        run_heading = self.config.result_summary_run_heading
        run_heading_width = max(len(numbering_format % 1), len(run_heading))
        output_format = '%' + str(self.config.result_summary_field_width) + 's'

        # Add short headings
        padding = run_heading_width - len(run_heading)
        input_heading_line = run_heading + (('%' + str(padding) + 's') % '')
        output_heading_line = run_heading + (('%' + str(padding) + 's') % '')
        for parameter_key in modified_parameters :
            if type(self.config.parameter_output_format[parameter_key]['short_heading']) is dict : # for (Low, Hi)
                input_heading_line += (output_format % self.config.parameter_output_format[parameter_key]['short_heading']['single'])
                #input_heading_line += (output_format % self.config.parameter_output_format[parameter_key]['short_heading']['multiple'][0])
                #input_heading_line += (output_format % self.config.parameter_output_format[parameter_key]['short_heading']['multiple'][1])
            else : # string
                input_heading_line += (output_format % self.config.parameter_output_format[parameter_key]['short_heading'])
        for result_key in selected_results :
            output_heading_line += (output_format % self.config.result_output_format[result_key]['short_heading'])
        result_input_lines.append(input_heading_line + '\n')
        result_output_lines.append(output_heading_line + '\n')

        # Generate lines for corresponding parameters and results
        for run_sample in self.generation_data['samples'] :

            run = (numbering_format % run_sample['sample_number']).replace('_', '')
            padding = run_heading_width - len(run)
            input_data_line = run + (('%' + str(padding) + 's') % '')
            output_data_line = run + (('%' + str(padding) + 's') % '')
            
            # Add parameter data via result values
            for parameter_key in modified_parameters :
                if type(self.config.parameter_result_input[parameter_key]) is list :
                    parameter_value = run_sample['data_frame_entry_details'][parameter_key]['value']
                    parameter_result_values = run_sample['data_frame_entry_details'][parameter_key]['result_value']
                    if run_sample['data_frame_entry_details'][parameter_key]['unique'] :
                        output_format = self.config.parameter_output_format[parameter_key]['output_file_format']
                        field_width = self.config.data_frame_field_width
                    else :
                        output_format = self.config.parameter_output_format[parameter_key]['output_file_percent_format']
                        field_width = self.config.data_frame_percent_width
                    output_format = output_format.replace(self.config.data_frame_field_width_substitution, str(field_width))
                    input_data_line += (output_format % parameter_value)
##                    for i, result_config in enumerate(self.config.parameter_result_input[parameter_key]) :
##                        if result_config == 'percent_change' :
##                            output_format = self.config.parameter_output_format[parameter_key]['output_file_percent_format']
##                            field_width = self.config.data_frame_percent_width
##                        else :
##                            output_format = self.config.parameter_output_format[parameter_key]['output_file_format']
##                            field_width = self.config.data_frame_field_width
##                        output_format = output_format.replace(self.config.data_frame_field_width_substitution, str(field_width))
##                        input_data_line += (output_format % parameter_result_values[i])
                else :
                    parameter_value = run_sample['data_frame_entry_details'][parameter_key]['value']
                    parameter_result_value = run_sample['data_frame_entry_details'][parameter_key]['result_value']
                    parameter_unique = run_sample['data_frame_entry_details'][parameter_key]['unique']
                    if self.config.parameter_result_input[parameter_key] == 'percent_change' or (self.config.parameter_result_input[parameter_key] == 'unique_or_percent' and not parameter_unique) :
                        parameter_result_value = parameter_value # revert any old versions of generation_data.dat with other configs
                        output_format = self.config.parameter_output_format[parameter_key]['output_file_percent_format']
                        field_width = self.config.data_frame_percent_width
                    else :
                        output_format = self.config.parameter_output_format[parameter_key]['output_file_format']
                        field_width = self.config.data_frame_field_width
                    output_format = output_format.replace(self.config.data_frame_field_width_substitution, str(field_width))
                    input_data_line += (output_format % parameter_result_value)
                    
            # Add result data
            for result_key in selected_results :
                field_width = self.config.result_summary_field_width
                if self.loaded_results.has_key(run_sample['sample_number']) :
                    result_value = self.loaded_results[run_sample['sample_number']][result_key]
                    output_format = self.config.result_output_format[result_key]['output_file_format']
                    output_format = output_format.replace(self.config.result_summary_field_width_substitution, str(field_width))
                else :
                    result_value = '-'
                    output_format = '%' + str(self.config.result_summary_field_width) + 's'
                output_data_line += (output_format % result_value)

            # Add the data line to the input and output files
            result_input_lines.append(input_data_line + '\n')
            result_output_lines.append(output_data_line + '\n')

        # Write the result inputs file
        f = open(path.join(self.results_directory['path'] ,'result_inputs.txt'), 'w')
        f.writelines(result_input_lines)
        f.close()

        # Write the result outputs file
        f = open(path.join(self.results_directory['path'] ,'result_outputs.txt'), 'w')
        f.writelines(result_output_lines)
        f.close()

    # Method generates the result summary for selected results
    def generateResultSummary(self, selected_results) :

        # Results input and output data structures
        self.results_input_data = {}
        self.results_input_keys = []
        self.glm_input_keys = []
        self.results_output_data = {}
        self.results_output_keys = []
        self.result_indexes = []

        # Add short headings as keys
        self.short_heading_key_map = {}
        for parameter_key in self.generation_data['parameters']['selected'] :
            if type(self.config.parameter_output_format[parameter_key]['short_heading']) is dict : # for (Low, Hi)
                self.short_heading_key_map[self.config.parameter_output_format[parameter_key]['short_heading']['single']] = parameter_key
                #self.short_heading_key_map[self.config.parameter_output_format[parameter_key]['short_heading']['multiple'][0]] = parameter_key + ' Min'
                #self.short_heading_key_map[self.config.parameter_output_format[parameter_key]['short_heading']['multiple'][1]] = parameter_key + ' Max'
                self.results_input_data[self.config.parameter_output_format[parameter_key]['short_heading']['single']] = []
                #self.results_input_data[self.config.parameter_output_format[parameter_key]['short_heading']['multiple'][0]] = []
                #self.results_input_data[self.config.parameter_output_format[parameter_key]['short_heading']['multiple'][1]] = []
                self.results_input_keys.append(self.config.parameter_output_format[parameter_key]['short_heading']['single'])
                #self.results_input_keys.append(self.config.parameter_output_format[parameter_key]['short_heading']['multiple'][0])
                #self.results_input_keys.append(self.config.parameter_output_format[parameter_key]['short_heading']['multiple'][1])
                self.glm_input_keys.append(self.config.parameter_output_format[parameter_key]['short_heading']['single'])
            else : # string
                self.short_heading_key_map[self.config.parameter_output_format[parameter_key]['short_heading']] = parameter_key
                self.results_input_data[self.config.parameter_output_format[parameter_key]['short_heading']] = []
                self.results_input_keys.append(self.config.parameter_output_format[parameter_key]['short_heading'])
                self.glm_input_keys.append(self.config.parameter_output_format[parameter_key]['short_heading'])
        for result_key in selected_results :
            self.short_heading_key_map[self.config.result_output_format[result_key]['short_heading']] = result_key
            self.results_output_data[self.config.result_output_format[result_key]['short_heading']] = []
            self.results_output_keys.append(self.config.result_output_format[result_key]['short_heading'])

        # Write the input and output parameter keys to a file
        keys = { 'Key' : ['', 'Inputs:'], 'Parameter' : ['', ''] }
        for key in self.results_input_keys :
            keys['Key'].append(key)
            keys['Parameter'].append(self.short_heading_key_map[key])
        keys['Key'].append('')
        keys['Parameter'].append('')
        keys['Key'].append('Outputs:')
        keys['Parameter'].append('')
        for key in self.results_output_keys :
            keys['Key'].append(key)
            keys['Parameter'].append(self.short_heading_key_map[key])
        f = open(path.join(self.results_directory['path'] ,'keys.txt'), 'w')
        f.write(pd.DataFrame(keys).to_string(index=False))
        f.close()

        # Add data for parameters and results
        for run_sample in self.generation_data['samples'] :

            self.result_indexes.append(run_sample['sample_number'])
            
            # Add parameter data via result values
            for parameter_key in self.generation_data['parameters']['selected'] :
                parameter_value = run_sample['data_frame_entry_details'][parameter_key]['value']
                parameter_result_value = run_sample['data_frame_entry_details'][parameter_key]['result_value']
                parameter_unique = run_sample['data_frame_entry_details'][parameter_key]['unique']
                if type(parameter_result_value) is list and type(self.config.parameter_output_format[parameter_key]['short_heading']) is dict:
                    self.results_input_data[self.config.parameter_output_format[parameter_key]['short_heading']['single']].append(parameter_value)
                    #for i, value in enumerate(parameter_result_value) :
                    #    self.results_input_data[self.config.parameter_output_format[parameter_key]['short_heading']['multiple'][i]].append(parameter_result_value[i])
                else : # single value
                    if self.config.parameter_result_input[parameter_key] == 'percent_change' or (self.config.parameter_result_input[parameter_key] == 'unique_or_percent' and not parameter_unique) :
                        parameter_result_value = parameter_value # revert any old versions of generation_data.dat with other configs
                    self.results_input_data[self.config.parameter_output_format[parameter_key]['short_heading']].append(parameter_result_value)
                    
            # Add result data
            for result_key in selected_results :
                if self.loaded_results.has_key(run_sample['sample_number']) :
                    result_value = self.loaded_results[run_sample['sample_number']][result_key]
                else :
                    result_value = np.nan
                self.results_output_data[self.config.result_output_format[result_key]['short_heading']].append(result_value)

        # Prepare parameters for GLM model (and write them to CSV files)
        result_inputs = pd.DataFrame(self.results_input_data, index=self.result_indexes)
        result_outputs = pd.DataFrame(self.results_output_data, index=self.result_indexes)
        result_inputs[self.results_input_keys].to_csv(path.join(self.results_directory['path'] ,'result_inputs.csv'), index_label='Run')
        result_outputs[self.results_output_keys].to_csv(path.join(self.results_directory['path'] ,'result_outputs.csv'), index_label='Run')
        data_independ = result_inputs[self.glm_input_keys]
        data_independ = sm.add_constant(data_independ, prepend=False) # Required
        
        # Run GLM models
        glm_ok_for_results = []
        exceptions = {}
        if self.results_output_keys.count('EMA') :
            try :
                self.results_ema = sm.GLM(result_outputs['EMA'], data_independ, family=sm.families.Gaussian(sm.families.links.log)).fit()
                glm_ok_for_results.append('EMA')
            except Exception, ema_e :
                exceptions['EMA'] = 'Error generating GLM for EMA: ' + str(ema_e)
        if self.results_output_keys.count('FinalN') :
            try :
                self.results_final_n = sm.GLM(result_outputs['FinalN'], data_independ, family=sm.families.Gaussian(sm.families.links.log)).fit()
                glm_ok_for_results.append('FinalN')
            except Exception, final_n_e :
                exceptions['FinalN'] = 'Error generating GLM for FinalN: ' + str(final_n_e)
        if self.results_output_keys.count('Ext') :
            try :
                self.results_ext = sm.GLM(result_outputs['Ext'], data_independ, family=sm.families.Binomial(sm.families.links.logit)).fit()
                glm_ok_for_results.append('Ext')
            except Exception, ext_e :
                exceptions['Ext'] = 'Error generating GLM for Ext: ' + str(ext_e)
            
        # Write model details to the results file
        f = open(path.join(self.results_directory['path'] ,'result_summary.txt'), 'w')
        f.write('GLM model summaries for EMA, FinalN, and Ext.\n')
        f.write('See \'keys.txt\' for full input and output parameter names.\n\n')
        if self.results_output_keys.count('EMA') :
            if not exceptions.has_key('EMA') :
                f.write(self.results_ema.summary().as_text())
                std_coeffs = self.generateOrderedStandardisedRegressionCoefficients(self.results_ema)
                f.write('\nStandardised Regression Coefficients:\n')
                f.write(std_coeffs.to_string())
            else :
                f.write(exceptions['EMA'])
            f.write('\n\n')
        if self.results_output_keys.count('FinalN') :
            if not exceptions.has_key('FinalN') :
                f.write(self.results_final_n.summary().as_text())
                std_coeffs = self.generateOrderedStandardisedRegressionCoefficients(self.results_final_n)
                f.write('\nStandardised Regression Coefficients:\n')
                f.write(std_coeffs.to_string())
            else :
                f.write(exceptions['FinalN'])
            f.write('\n\n')
        if self.results_output_keys.count('Ext') :
            if not exceptions.has_key('Ext') :
                f.write(self.results_ext.summary().as_text())
                std_coeffs = self.generateOrderedStandardisedRegressionCoefficients(self.results_ext)
                f.write('\nStandardised Regression Coefficients:\n')
                f.write(std_coeffs.to_string())
            else :
                f.write(exceptions['Ext'])
        f.close()

        # Pass exceptions to main program
        if exceptions :
            exception_message = ''
            for key in self.results_output_keys :
                if exceptions.has_key(key) :
                    exception_message += ('\n' + exceptions[key])
            if glm_ok_for_results :
                exception_message += '\nGLM generated successfully for:'
                for key in glm_ok_for_results :
                    exception_message += ('\n    ' + self.short_heading_key_map[key])
            raise Exception(exception_message)

    # Method generates ordered standardised regression coefficients from GLM results
    def generateOrderedStandardisedRegressionCoefficients(self, glm_results) :
        coeffs = glm_results.params.copy().drop('const')
        stderrs = glm_results.bse.copy().drop('const')
        std_coeffs = (coeffs/stderrs)/sum(abs(coeffs/stderrs))
        abs_std_coeffs = std_coeffs.abs()
        abs_std_coeffs.sort(ascending=False) #.sort_values(inplace=True, ascending=False)
        return std_coeffs[abs_std_coeffs.keys()]

    # Method generates the result plot files
    def generateResultPlotFiles(self) :
        for result_plot_key, loaded_result_plot in self.loaded_result_plots.items() :
            result_plot_dataframe = pd.DataFrame(loaded_result_plot)
            base_filename = path.join(self.results_directory['path'], self.config.result_plot_file_details[result_plot_key]['filename'])
            fields = self.config.result_plot_file_details[result_plot_key]['fields']
            result_plot_dataframe.to_csv(base_filename+'.csv', cols=fields, index=False)
            self.result_plot_dataframe = result_plot_dataframe
            f = open(base_filename+'.txt', 'w')
            f.write(result_plot_dataframe.to_string(columns=fields, index=False))
            f.close()

# END MpFileExtractorAndGenerator
