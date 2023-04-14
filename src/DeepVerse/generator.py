# -*- coding: utf-8 -*-
"""
DeepMIMOv2 Python Implementation

Description: Main generator script

Authors: Umut Demirhan, Ahmed Alkhateeb
Date: 12/10/2021
"""

from DeepVerse.raytracing import read_raytracing
from DeepVerse.communication import generate_MIMO_channel
from DeepVerse.radar import generate_radar_signal
from DeepVerse.file_loaders import load_scenario_params
import DeepVerse.consts as c
import scipy.io as scio
import numpy as np
import os
from DeepVerse.utils import safe_print, structured_arr_to_dict


def generate_data(params):

    np.random.seed(1001)

    num_bs = len(params[c.PARAMSET_ACTIVE_BS])

    dataset = {
        'scene': [dict(ue=None, bs=[dict() for _ in num_bs]) for _ in range(len(c.PARAMSET_DYNAMIC))],
        'info': dict()
    }

    scenario_folder = os.path.join(
        params[c.PARAMSET_DATASET_FOLDER], params[c.PARAMSET_SCENARIO])
    dataset['info']['scenario_folder'] = scenario_folder
    
    
    data_map_path = os.path.join(scenario_folder, 'data_map.mat')
    full_data = scio.loadmat(data_map_path)['full_data']

    # Position
    position_data_path = os.path.abspath(os.path.join(
        scenario_folder, full_data['trajectory'].item()[0]))
    if params[c.PARAMSET_POSITION][c.PARAMSET_ACTIVE]:
        position_data = scio.loadmat(position_data_path, squeeze_me=True)
        dataset['info']['mobility'] = {'object_types': structured_arr_to_dict(
            position_data['object_info'])}
        
        scene_count = 0
        for scene in params[c.PARAMSET_DYNAMIC]:
            ue_data = structured_arr_to_dict(structured_arr_to_dict(
                position_data['scene'][scene])['objects'])
            
            dataset['scene'][scene_count]['ue'] = ue_data
            scene_count += 1
    
    # Camera
    if params[c.PARAMSET_CAMERA][c.PARAMSET_ACTIVE]:
        for scene in params[c.PARAMSET_DYNAMIC]:
            # Camera
            dataset['scene'][scene_count]['bs'][]
            for i in params[c.PARAMSET_CAMERA][c.PARAMSET_IDX]:
                pass
                # np.array(structured_arr_to_dict(full_data['bs1'][0])[0][0][0]['image'][0][0]['cam1'][0][0]['data'][0]).flatten()[4]
    
    # Lidar
    if params[c.PARAMSET_LIDAR][c.PARAMSET_ACTIVE]:
        pass

    # Radar
    if params[c.PARAMSET_RADAR][c.PARAMSET_ACTIVE]:
        pass

        params[c.PARAMSET_SCENARIO_FIL] = os.path.join(
            os.path.abspath(params[c.PARAMSET_DATASET_FOLDER]),
            params[c.PARAMSET_SCENARIO],
            'scene_' + str(scene),  # 'scene_i' folder
            params[c.PARAMSET_SCENARIO]
        )
        comm_dataset.append(generate_comm_data(params))
    # Comm
    if params[c.PARAMSET_COMM][c.PARAMSET_ACTIVE]:

        params[c.PARAMSET_SCENARIO_FIL] = os.path.join(
            os.path.abspath(params[c.PARAMSET_DATASET_FOLDER]),
            params[c.PARAMSET_SCENARIO],
            'scene_' + str(scene),  # 'scene_i' folder
            params[c.PARAMSET_SCENARIO]
        )
        radar_dataset.append(generate_radar_data(params))


def generate_comm_data(params):
    num_active_bs = len(params[c.PARAMSET_ACTIVE_BS])
    dataset = [{c.DICT_UE_IDX: dict(), c.DICT_BS_IDX: dict(), c.OUT_LOC: None}
               for x in range(num_active_bs)]

    for i in range(num_active_bs):
        bs_indx = params[c.PARAMSET_ACTIVE_BS][i]

        safe_print('\nBasestation %i' % bs_indx)

        safe_print('\nUE-BS Channels')
        dataset[i][c.DICT_UE_IDX], dataset[i][c.OUT_LOC] = read_raytracing(
            bs_indx, params, user=True)
        dataset[i][c.DICT_UE_IDX][c.OUT_CHANNEL] = generate_MIMO_channel(dataset[i][c.DICT_UE_IDX][c.OUT_PATH],
                                                                         params,
                                                                         params[c.PARAMSET_ANT_BS][i],
                                                                         params[c.PARAMSET_ANT_UE])

        if params[c.PARAMSET_BS2BS]:
            safe_print('\nBS-BS Channels')

            dataset[i][c.DICT_BS_IDX], _ = read_raytracing(
                bs_indx, params, user=False)
            dataset[i][c.DICT_BS_IDX][c.OUT_CHANNEL] = generate_MIMO_channel_rx_ind(dataset[i][c.DICT_BS_IDX][c.OUT_PATH],
                                                                                    params,
                                                                                    params[c.PARAMSET_ANT_BS][i],
                                                                                    params[c.PARAMSET_ANT_BS])

            if not params[c.PARAMSET_ANT_BS_DIFF]:
                dataset[i][c.DICT_BS_IDX][c.OUT_CHANNEL] = np.stack(
                    dataset[i][c.DICT_BS_IDX][c.OUT_CHANNEL], axis=0)
    return dataset


def generate_radar_data(params):
    num_active_bs = len(params[c.PARAMSET_ACTIVE_BS])
    dataset = [{c.DICT_UE_IDX: dict(), c.DICT_BS_IDX: dict(), c.OUT_LOC: None}
               for x in range(num_active_bs)]

    for i in range(num_active_bs):
        bs_indx = params[c.PARAMSET_ACTIVE_BS][i]

        safe_print('\nBasestation %i' % bs_indx)

        safe_print('\nUE-BS Channels')
        dataset[i][c.DICT_UE_IDX], dataset[i][c.OUT_LOC] = read_raytracing(
            bs_indx, params, user=True)
        dataset[i][c.DICT_UE_IDX][c.OUT_CHANNEL] = generate_MIMO_channel(dataset[i][c.DICT_UE_IDX][c.OUT_PATH],
                                                                         params,
                                                                         params[c.PARAMSET_ANT_BS][i],
                                                                         params[c.PARAMSET_ANT_UE])

        if params[c.PARAMSET_BS2BS]:
            safe_print('\nBS-BS Channels')

            dataset[i][c.DICT_BS_IDX], _ = read_raytracing(
                bs_indx, params, user=False)
            dataset[i][c.DICT_BS_IDX][c.OUT_CHANNEL] = generate_MIMO_channel_rx_ind(dataset[i][c.DICT_BS_IDX][c.OUT_PATH],
                                                                                    params,
                                                                                    params[c.PARAMSET_ANT_BS][i],
                                                                                    params[c.PARAMSET_ANT_BS])

            if not params[c.PARAMSET_ANT_BS_DIFF]:
                dataset[i][c.DICT_BS_IDX][c.OUT_CHANNEL] = np.stack(
                    dataset[i][c.DICT_BS_IDX][c.OUT_CHANNEL], axis=0)
    return dataset


def validate_params(params):

    # Load scenario files to calculate users
    if 'dyn' in params[c.PARAMSET_SCENARIO]:
        params[c.PARAMSET_SCENARIO_FIL] = os.path.join(
            os.path.abspath(params[c.PARAMSET_DATASET_FOLDER]),
            params[c.PARAMSET_SCENARIO],
            # 'scene_i' folder
            'scene_' + str(params[c.PARAMSET_DYNAMIC]
                           [c.PARAMSET_DYNAMIC_FIRST]-1),
            params[c.PARAMSET_SCENARIO]
        )
    else:
        params[c.PARAMSET_SCENARIO_FIL] = os.path.join(
            os.path.abspath(params[c.PARAMSET_DATASET_FOLDER]),
            params[c.PARAMSET_SCENARIO],
            params[c.PARAMSET_SCENARIO]
        )

    params[c.PARAMSET_SCENARIO_PARAMS] = load_scenario_params(
        params[c.PARAMSET_SCENARIO_FIL])

    # Active user IDs and related parameter
    assert params[c.PARAMSET_USER_SUBSAMP] > 0 and params[
        c.PARAMSET_USER_SUBSAMP] <= 1, 'The subsampling parameter \'%s\' needs to be in (0, 1]' % c.PARAMSET_USER_SUBSAMP
    assert params[c.PARAMSET_USER_ROW_SUBSAMP] > 0 and params[
        c.PARAMSET_USER_ROW_SUBSAMP] <= 1, 'The subsampling parameter \'%s\' needs to be in (0, 1]' % c.PARAMSET_USER_ROW_SUBSAMP
    params[c.PARAMSET_ACTIVE_UE] = find_users_from_rows(params)

    # BS antenna format
    params[c.PARAMSET_ANT_BS_DIFF] = True
    # Replicate BS Antenna for each active BS in a list
    if type(params[c.PARAMSET_ANT_BS]) is dict:
        ant = params[c.PARAMSET_ANT_BS]
        params[c.PARAMSET_ANT_BS] = []
        for i in range(len(params[c.PARAMSET_ACTIVE_BS])):
            params[c.PARAMSET_ANT_BS].append(ant)
    else:
        if len(params[c.PARAMSET_ACTIVE_BS]) == 1:
            params[c.PARAMSET_ANT_BS_DIFF] = False

    # BS Antenna Rotation
    for i in range(len(params[c.PARAMSET_ACTIVE_BS])):
        if c.PARAMSET_ANT_ROTATION in params[c.PARAMSET_ANT_BS][i].keys() and params[c.PARAMSET_ANT_BS][i][c.PARAMSET_ANT_ROTATION] is not None:
            rotation_shape = params[c.PARAMSET_ANT_BS][i][c.PARAMSET_ANT_ROTATION].shape
            assert (len(rotation_shape) ==
                    1 and rotation_shape[0] == 3), 'The BS antenna rotation must be a 3D vector'

        else:
            params[c.PARAMSET_ANT_BS][i][c.PARAMSET_ANT_ROTATION] = None

    # UE Antenna Rotation
    if c.PARAMSET_ANT_ROTATION in params[c.PARAMSET_ANT_UE].keys() and params[c.PARAMSET_ANT_UE][c.PARAMSET_ANT_ROTATION] is not None:
        rotation_shape = params[c.PARAMSET_ANT_UE][c.PARAMSET_ANT_ROTATION].shape
        assert (len(rotation_shape) == 1 and rotation_shape[0] == 3) or \
            (len(rotation_shape) == 2 and rotation_shape[0] == 3 and rotation_shape[1] == 2) or \
            (rotation_shape[0] == len(params[c.PARAMSET_ACTIVE_UE])
             ), 'The UE antenna rotation must either be a 3D vector for constant values or 3 x 2 matrix for random values'

        if len(rotation_shape) == 1 and rotation_shape[0] == 3:
            rotation = np.zeros((len(params[c.PARAMSET_ACTIVE_UE]), 3))
            rotation[:] = params[c.PARAMSET_ANT_UE][c.PARAMSET_ANT_ROTATION]
            params[c.PARAMSET_ANT_UE][c.PARAMSET_ANT_ROTATION] = rotation
        elif (len(rotation_shape) == 2 and rotation_shape[0] == 3 and rotation_shape[1] == 2):
            params[c.PARAMSET_ANT_UE][c.PARAMSET_ANT_ROTATION] = np.random.uniform(
                params[c.PARAMSET_ANT_UE][c.PARAMSET_ANT_ROTATION][:, 0],
                params[c.PARAMSET_ANT_UE][c.PARAMSET_ANT_ROTATION][:, 1],
                (len(params[c.PARAMSET_ACTIVE_UE]), 3))
    else:
        params[c.PARAMSET_ANT_UE][c.PARAMSET_ANT_ROTATION] = np.array(
            [None] * len(params[c.PARAMSET_ACTIVE_UE]))  # List of None

    # BS Antenna Radiation Pattern
    for i in range(len(params[c.PARAMSET_ACTIVE_BS])):
        if c.PARAMSET_ANT_RAD_PAT in params[c.PARAMSET_ANT_BS][i].keys():
            assert params[c.PARAMSET_ANT_BS][i][c.PARAMSET_ANT_RAD_PAT] in c.PARAMSET_ANT_RAD_PAT_VALS, 'The antenna radiation pattern for BS-%i must have one of the following values: [%s]' % (
                i, c.PARAMSET_ANT_RAD_PAT_VALS.join(', '))
        else:
            params[c.PARAMSET_ANT_BS][i][c.PARAMSET_ANT_RAD_PAT] = c.PARAMSET_ANT_RAD_PAT_VALS[0]

    # UE Antenna Radiation Pattern
    if c.PARAMSET_ANT_RAD_PAT in params[c.PARAMSET_ANT_UE].keys():
        assert params[c.PARAMSET_ANT_UE][c.PARAMSET_ANT_RAD_PAT] in c.PARAMSET_ANT_RAD_PAT_VALS, 'The antenna radiation pattern for UEs must have one of the following values: [%s]' % (
            c.PARAMSET_ANT_RAD_PAT_VALS.join(', '))
    else:
        params[c.PARAMSET_ANT_UE][c.PARAMSET_ANT_RAD_PAT] = c.PARAMSET_ANT_RAD_PAT_VALS[0]

    return params


# Generate the set of users to be activated
def find_users_from_rows(params):

    def rand_perm_per(vector, percentage):
        if percentage == 1:
            return vector
        num_of_subsampled = round(len(vector)*percentage)
        if num_of_subsampled < 1:
            num_of_subsampled = 1
        subsampled = np.arange(len(vector))
        np.random.shuffle(subsampled)
        subsampled = vector[subsampled[:num_of_subsampled]]
        subsampled = np.sort(subsampled)
        return subsampled

    def get_user_ids(row, grids):
        row_prev_ids = np.sum(
            (row > grids[:, 1])*(grids[:, 1] - grids[:, 0] + 1)*grids[:, 2])
        row_cur_ind = (grids[:, 1] >= row) * (row >= grids[:, 0])
        row_cur_start = row - grids[row_cur_ind, 0][0]
        users_in_row = grids[:, 2][row_cur_ind][0]

        # column-oriented grid
        if grids.shape[1] == 4 and grids[row_cur_ind, 3][0]:
            users_in_col = (grids[:, 1]-grids[:, 0]+1)[row_cur_ind][0]
            user_ids = row_prev_ids + row_cur_start + \
                np.arange(0, users_in_col*users_in_row, users_in_col)
        # row-oriented grid
        else:
            row_curr_ids = row_cur_start * users_in_row
            user_ids = row_prev_ids + row_curr_ids + np.arange(users_in_row)

        return user_ids

    grids = params[c.PARAMSET_SCENARIO_PARAMS][c.PARAMSET_SCENARIO_PARAMS_USER_GRIDS]
    rows = np.arange(params[c.PARAMSET_USER_ROW_FIRST],
                     params[c.PARAMSET_USER_ROW_LAST]+1)
    active_rows = rand_perm_per(rows, params[c.PARAMSET_USER_ROW_SUBSAMP])

    user_ids = np.array([], dtype=int)
    for row in active_rows:
        user_ids_row = get_user_ids(row, grids)
        user_ids_row = rand_perm_per(
            user_ids_row, params[c.PARAMSET_USER_SUBSAMP])
        user_ids = np.concatenate((user_ids, user_ids_row))

    return user_ids
