from . import consts as c
from .Antenna import Antenna

import numpy as np
import copy

def create_antennas(ant_params, n_ant):
    """
    Create base station antennas based on the given parameters.

    Parameters:
    ----------
    n_active_BS : int
        Number of active base stations.
    ant_params : dict or list of dict
        Antenna parameters. Can be a single dictionary or a list of dictionaries
        where each dictionary contains parameters for one antenna.

    Returns:
    -------
    tx_ant : list of Antenna
        List of created Antenna objects for each active base station.
    """
    
    # Check the type of antenna parameters and create antennas accordingly
    if isinstance(ant_params, dict):
        # If antenna parameters are given as a single dictionary
        
        # Rotation Modes
        if ant_params['rotation'] is not None:
            if isinstance(ant_params['rotation'], list):
                ant_params['rotation'] = np.array(ant_params['rotation'])
            rotation_shape = ant_params['rotation'].shape
            rotation_shape_len = len(rotation_shape)

            if rotation_shape_len == 1 and rotation_shape[0] == 3:
                # If rotation is a single 3D vector, replicate it for each antenna
                antennas = [Antenna(**ant_params)] * n_ant
            elif rotation_shape_len == 2 and rotation_shape[0] == 3 and rotation_shape[1] == 2:
                # If rotation is a 3 x 2 matrix, generate random rotations within the given ranges
                rotations = np.random.uniform(ant_params['rotation'][:, 0],
                                              ant_params['rotation'][:, 1],
                                              (n_ant, 3))
                ant_params['rotation'] = None
                antenna = Antenna(**ant_params)
                antennas = []
                for i in range(n_ant):
                    ant_i = copy.copy(antenna)
                    ant_i.rotation = rotations[i]
                    antennas.append(ant_i)
                    
            elif rotation_shape[0] == n_ant:
                # If rotation is already defined for each antenna, ensure it's in array form
                rotations = ant_params['rotation']
                ant_params['rotation'] = None
                antenna = Antenna(**ant_params)
                antennas = []
                for i in range(n_ant):
                    ant_i = copy.copy(antenna)
                    ant_i.rotation = rotations[i]
                    antennas.append(ant_i)
            else:
                # Raise a TypeError if the rotation parameters are not in a supported format
                raise TypeError('The UE antenna rotation must either be a 3D vector for constant values or 3 x 2 matrix for random values')

        
    elif isinstance(ant_params, list):
        # If antenna parameters are given as a list, create an antenna for each set of parameters
        num_ant_params = len(ant_params)
        antennas = [Antenna(**ant_params[i]) for i in range(num_ant_params)]
        # If only one set of antenna parameters is provided, replicate it for each active BS
        if num_ant_params == 1 and n_ant > 1:
            ant = antennas * n_ant
        else:
            assert num_ant_params == n_ant, '# of BS antenna parameters is not equivalent to # of active BSs.'
    else:
        # Raise a TypeError if the antenna parameters are not in a supported format
        raise TypeError('Antenna type must be a dictionary or list of dictionaries')
    
    
    # Return the list of created antennas
    return antennas


# Generate the set of users to be activated
def find_users_from_rows(params):

    def rand_perm_per(vector, percentage):
        if percentage == 1: return vector
        num_of_subsampled = round(len(vector)*percentage)
        if num_of_subsampled < 1: num_of_subsampled = 1 
        subsampled = np.arange(len(vector))
        np.random.shuffle(subsampled)
        subsampled = vector[subsampled[:num_of_subsampled]]
        subsampled = np.sort(subsampled)
        return subsampled
    
    def get_user_ids(row, grids):
        row = row + 1
        row_prev_ids = np.sum((row > grids[:, 1])*(grids[:, 1] - grids[:, 0] + 1)*grids[:, 2])
        row_cur_ind = (grids[:, 1] >= row) * (row >= grids[:, 0])
        row_cur_start = row - grids[row_cur_ind, 0][0]
        users_in_row = grids[:, 2][row_cur_ind][0]

        row_curr_ids = row_cur_start * users_in_row
        user_ids = row_prev_ids + row_curr_ids + np.arange(users_in_row)
            
        return user_ids
    
    grids = params[c.PARAMSET_SCENARIO_PARAMS][c.PARAMSET_SCENARIO_PARAMS_USER_GRIDS]
    rows = params[c.PARAMSET_USER_ROWS]
    
    user_ids = np.array([], dtype=int)
    for row in rows:
        user_ids_row = get_user_ids(row, grids)
        user_ids_row = rand_perm_per(user_ids_row, params[c.PARAMSET_USER_SUBSAMP])
        user_ids = np.concatenate((user_ids, user_ids_row))
    
    return user_ids