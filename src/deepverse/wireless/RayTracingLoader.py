import os
import glob
import numpy as np
import scipy.io
import re
import pandas as pd
from . import consts as c
from .utils import dbm2pow
from tqdm import tqdm

class RayTracingLoader:
    def __init__(self, directory):
        self.directory = directory
        self.data_tables = self._get_data_files(directory)

        # -- To validate the format --
        # TODO: To be written..
        self.num_ue = 0 if self.data_tables['rx'].empty else self.data_tables['rx']['rx_end'].max()
        self.num_bs = len(self.data_tables['tx'])
        self.num_files_per_bs = (self.data_tables['rx']['tx'] == 1).sum() # Pick number of BSs from the BS file
        
    def load_data(self, tx_idx, rx_idx=None, user=True):
        if rx_idx is None:
            rx_idx = np.arange(self.num_ue)
        ray_data, rx_locs, tx_loc = self._load_ray_data(bs_id=tx_idx, 
                                                        generation_idx=rx_idx, 
                                                        df=self.data_tables['rx' if user else 'tx'])
        
        path_list = []
        for user in tqdm(range(len(ray_data)), desc='Reading ray-tracing', leave=False):
            path_dict = raydata_matrix_to_dictionary(ray_data[user][0], num_max_paths=None, power_normalization_factor=30)
            path_list.append(path_dict)
            
        data = {c.OUT_LOC: [],
                c.OUT_DIST: [],
                c.OUT_PL: []}
        data[c.OUT_PATH] = path_list
        if len(rx_locs)>0:
            data[c.OUT_LOC] = rx_locs[:, :3]
            data[c.OUT_DIST] = rx_locs[:, 3]
            data[c.OUT_PL] = rx_locs[:, 4]
        return data, tx_loc
        
    def _load_ray_data(self, bs_id, generation_idx, df):
        """
        Loads ray-tracing data for user equipment (UE) from provided UE DataFrame.

        Parameters:
        - generation_idx (array-like): Indices of the users to be processed.
        - bs_id (int): Base station ID.
        - df (pd.DataFrame): DataFrame containing file paths.

        Returns:
        - tuple: A tuple containing ray_data, rx_locs, and tx_loc.
        """
        ray_data = []
        rx_locs = []

        # Filter ue_df for the specified base station
        filtered_df = df[df['tx'] == bs_id]

        # Filter further based on generation_idx
        filtered_df = filtered_df[
            filtered_df.apply(lambda row: np.any((generation_idx >= row['rx_start']) & (generation_idx <= row['rx_end'])), axis=1)
        ]
        
        ray_data = [] # May be converted to np.array
        # Process each row in the filtered UE DataFrame
        file_data = None
        for idx, row in filtered_df.iterrows():
            file_path = row['file_path']
            rx_start = row['rx_start']
            rx_end = row['rx_end']
            
            rx_in_file = generation_idx[(generation_idx >= rx_start) & (generation_idx <= rx_end)]
            file_data = scipy.io.loadmat(file_path)
            # TODO: somehow clean the next for loop
            for rx in rx_in_file:
                rx_data = file_data['channels'][0][rx-rx_start][0][0]
                ray_data.append(rx_data)
                rx_locs.append(file_data['rx_locs'][rx-rx_start])
        ray_data = np.array(ray_data)
        rx_locs = np.array(rx_locs)
        tx_loc = self._get_tx_location(file_data, bs_id) # Sth better here would be good

        return ray_data, rx_locs, tx_loc

    def _get_tx_location(self, file_data, bs_id):
            if file_data is not None and 'tx_loc' in file_data:
                tx_loc = file_data['tx_loc'].squeeze()
            # If tx location is not available in the data
            # pull it from the BS-BS file
            else:
                file = os.path.join(self.directory, 'BS%i_BS.mat'%(bs_id+1))
                file_data = scipy.io.loadmat(file)
                tx_loc = file_data['rx_locs'][bs_id][:3]
            return tx_loc

    def _get_data_files(self, directory):
        """
        Finds files in the specified directory, extracts numbers based on predefined regex patterns, and returns pandas DataFrames.

        Parameters:
        - directory (str): The directory to search for files.

        Returns:
        - dict of DataFrames: Dictionary with keys as 'bs' and 'ue' and values as DataFrames with extracted file paths and numbers.
        """
        def process_files(format, column_names):
            format_regex = format.replace('*', r'(\d+)')
            files = glob.glob(os.path.join(directory, format))
            data = return_numbers_from_filelist(files, format_regex)
            df = pd.DataFrame(data, columns=['file_path'] + column_names)
            return df

        # Define file format strings and regex patterns
        bs_df = process_files(format='BS*_BS.mat', column_names=['tx'])
        # To match the format of BS-UE dictionaries
        bs_df['tx'] = bs_df['tx'] - 1
        bs_df['rx_start'] = bs_df['tx'].min()
        bs_df['rx_end'] = bs_df['tx'].max()
        
        ue_df = process_files(format='BS*_UE_*-*.mat', column_names=['tx', 'rx_start', 'rx_end'])
        ue_df['tx'] = ue_df['tx'] - 1

        return {'tx': bs_df, 'rx': ue_df}

    @staticmethod
    def load_scenario_params(parameters_file_path):
        """
        Loads scenario parameters from a .mat file and returns them as a dictionary.

        Parameters:
        - parameters_file_path (str): The path to the .mat file containing scenario parameters.

        Returns:
        - dict: A dictionary with scenario parameters.
        
        The dictionary contains the following keys:
        - c.PARAMSET_SCENARIO_PARAMS_CF: Carrier frequency (float)
        - c.PARAMSET_SCENARIO_PARAMS_TX_POW: Transmission power (float)
        - c.PARAMSET_SCENARIO_PARAMS_NUM_BS: Number of base stations (int)
        - c.PARAMSET_SCENARIO_PARAMS_USER_GRIDS: User grids (int array)
        - c.PARAMSET_SCENARIO_PARAMS_DOPPLER_EN: Doppler enable flag (int)
        - c.PARAMSET_SCENARIO_PARAMS_POLAR_EN: Polarization enable flag (int)
        """
        try:
            data = scipy.io.loadmat(parameters_file_path)
            scenario_params = {
                c.PARAMSET_SCENARIO_PARAMS_CF: data[c.LOAD_FILE_SP_CF].astype(float).item(),
                c.PARAMSET_SCENARIO_PARAMS_TX_POW: data[c.LOAD_FILE_SP_TX_POW].astype(float).item(),
                c.PARAMSET_SCENARIO_PARAMS_NUM_BS: data[c.LOAD_FILE_SP_NUM_BS].astype(int).item(),
                c.PARAMSET_SCENARIO_PARAMS_USER_GRIDS: data[c.LOAD_FILE_SP_USER_GRIDS].astype(int),
                c.PARAMSET_SCENARIO_PARAMS_DOPPLER_EN: data[c.LOAD_FILE_SP_DOPPLER].astype(int).item(),
                c.PARAMSET_SCENARIO_PARAMS_POLAR_EN: data[c.LOAD_FILE_SP_POLAR].astype(int).item()
            }
            return scenario_params
        except KeyError as e:
            raise KeyError(f"Missing key in the scenario parameters mat file: {e}")
        except Exception as e:
            raise RuntimeError(f"An error occurred while loading scenario parameters: {e}")

def return_numbers_from_filelist(file_list, pattern_str):
    """
    Processes a list of file paths, extracts matches based on a predefined regex pattern, and returns a dictionary
    with paths as keys and tuples of numbers as values.

    Parameters:
    - file_list (list): List of file paths to process.
    - pattern_str (str): Regular expression pattern as a string for extracting numbers from filenames.

    Returns:
    - list: A list where [(file1_path, file1_number1, file1_number2, ...), ...].
    """
    pattern = re.compile(pattern_str)
    results = []
    for file_path in file_list:
        filename = os.path.basename(file_path)
        numbers = extract_matches_from_filename(filename, pattern)
        if numbers:
            results.append((file_path,) + numbers)
        else:
            raise ValueError(f'Regex pattern string and provided {filename} in the file_list list do not match!')
    return results
    
def extract_matches_from_filename(filename, pattern):
    """
    Extracts numeric values from a given filename based on a pre-compiled regular expression pattern. This function
    is optimized for repeated use by utilizing a regex pattern object that has been compiled in advance, ensuring 
    efficiency when the function is invoked multiple times with the same regex pattern.

    Parameters:
    - filename (str): The filename from which numbers will be extracted. The expected filename format should
                      match the structure defined by the regex pattern.
    - pattern (re.Pattern): A pre-compiled regular expression pattern used for extracting numeric groups from the filename.

    Returns:
    - tuple: A tuple containing the extracted numbers as integers, if matches are found, otherwise None.
             This is useful for parsing structured filenames where specific numeric values represent meaningful data,
             such as session identifiers, dates, or sequence numbers.
    """
    
    # Perform the search using the provided pre-compiled regex pattern on the filename
    match = pattern.search(filename)
    if match:
        # Convert all captured numeric groups to integers and return them as a tuple
        # This allows for direct use of the extracted numbers, assuming all groups in the regex are integers
        return tuple(int(num) for num in match.groups())
    # Return None if no matching groups are found
    return None

def raydata_matrix_to_dictionary(path_params, num_max_paths=None, power_normalization_factor=30):
    """
    Splits path parameters into a dictionary of variables.

    Parameters:
    - path_params (np.array): 2D array of path parameters with shape (num_features, num_paths).
                              The expected features are: phase, toa, rx_pow, doa_phi, doa_theta,
                              dod_phi, dod_theta, los, (optional) dop_vel, dop_acc.
    - num_max_paths (int): Maximum number of paths to process.
    - power_normalization_factor (float): Factor to normalize the power (default is 30).

    Returns:
    - dict: A dictionary with path parameters.
    
    """
    if num_max_paths is not None:
        num_max_paths = min(num_max_paths, path_params.shape[1])
        path_params = path_params[:, :num_max_paths]

    user_data = {
        c.OUT_PATH_PHASE: path_params[0],
        c.OUT_PATH_TOA: path_params[1],
        c.OUT_PATH_RX_POW: dbm2pow(path_params[2] + power_normalization_factor),
        c.OUT_PATH_DOA_PHI: path_params[3],
        c.OUT_PATH_DOA_THETA: path_params[4],
        c.OUT_PATH_DOD_PHI: path_params[5],
        c.OUT_PATH_DOD_THETA: path_params[6],
        c.OUT_PATH_LOS: path_params[7]
    }

    doppler_available = path_params.shape[0] > 8

    if doppler_available:
        user_data[c.OUT_PATH_DOP_VEL] = path_params[8]
        user_data[c.OUT_PATH_DOP_ACC] = path_params[9]
    else:
        user_data[c.OUT_PATH_DOP_VEL] = None
        user_data[c.OUT_PATH_DOP_ACC] = None

    return user_data

if __name__ == '__main__':
    x = RayTracingLoader(r'C:\Users\Umt\Documents\GitHub\DeepMIMO-python\raytracing_scenarios\city_4_phoenix')
    
    print('x')