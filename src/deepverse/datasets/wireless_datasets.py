
import os
import numpy as np
from tqdm import tqdm
from ..wireless.process_params import create_antennas, find_users_from_rows
from ..wireless.RayTracingLoader import RayTracingLoader

from ..wireless import consts as c
from ..wireless.Paths import Paths
from ..wireless.Channel import OFDMChannel, RadarChannel
from ..wireless.Waveform import FMCW

class RadarDataset:
    def __init__(self, params):
        self.params = params
        self._validate_parameters(self.params)
        self.data = self._generate_data(params[c.PARAMSET_DYNAMIC_SCENES])

    def _validate_parameters(self, params):
        
        params['user_rows'] = np.array([0]) # Dynamic scenarios
        params[c.PARAMSET_SCENARIO_PARAMS_PATH] = os.path.join(
                os.path.abspath(params[c.PARAMSET_DATASET_FOLDER]),
                params[c.PARAMSET_SCENARIO],
                'wireless',
                'params.mat'
        )
        params[c.PARAMSET_SCENARIO_PARAMS] = RayTracingLoader.load_scenario_params(params[c.PARAMSET_SCENARIO_PARAMS_PATH])
        
        if isinstance(params[c.PARAMSET_ACTIVE_BS], list):
            params[c.PARAMSET_ACTIVE_BS] = np.array(params[c.PARAMSET_ACTIVE_BS])
            
        # BS antenna format
        params['tx_ant_objs'] = create_antennas(ant_params=params[c.PARAMSET_ANT_TX], 
                                                n_ant=len(params[c.PARAMSET_ACTIVE_BS]))
            
        params['rx_ant_objs'] = create_antennas(ant_params=params[c.PARAMSET_ANT_RX], 
                                                n_ant=len(params[c.PARAMSET_ACTIVE_BS]))
        
        return params

    def _generate_data(self, scenes):
        dataset = []
        for i, scene_idx in enumerate(tqdm(scenes, desc="Processing Scenes", leave=False)):
            dataset.append(self._generate_scene_data(scene_idx=scene_idx))
            
        return dataset
    
    def _generate_scene_data(self, scene_idx):
        params = self.params.copy()
        
        # TODO: Move these to dataset object initialization
        carrier_freq = params[c.PARAMSET_SCENARIO_PARAMS][c.PARAMSET_SCENARIO_PARAMS_CF]
        waveform = FMCW(**params['FMCW'], f_0=carrier_freq)
        
        scene_folder = os.path.join(os.path.abspath(params[c.PARAMSET_DATASET_FOLDER]), 
                                    params[c.PARAMSET_SCENARIO],
                                    'wireless',
                                    'scene_' + str(scene_idx)
                                   )
        rt_loader = RayTracingLoader(scene_folder)
        num_active_bs = len(params[c.PARAMSET_ACTIVE_BS])
        dataset = []
        for i in range(num_active_bs):
            bs_indx = params[c.PARAMSET_ACTIVE_BS]
            
            raydata, _ = rt_loader.load_data(tx_idx=bs_indx[i]-1, rx_idx=bs_indx-1, user=False)
            bs_channels = []
            n_bs = len(raydata['paths'])
            for j in tqdm(range(n_bs), desc=f'Generating BS{bs_indx[i]} channels', leave=False):
                paths = Paths(raydata['paths'][j], carrier_freq, params['num_paths']).apply_antenna_parameters(TX_antenna=params['tx_ant_objs'][i], RX_antenna=params['rx_ant_objs'][j])
                    
                channel = RadarChannel(tx_antenna=params['tx_ant_objs'][i],
                                       rx_antenna=params['rx_ant_objs'][j],
                                       paths=paths, 
                                       carrier_freq=carrier_freq, 
                                       waveform=waveform, 
                                       params=params
                                      )
                channel.generate()
                bs_channels.append(channel)
            dataset.append(bs_channels)
        return dataset
    
    def get_sample(self, tx_bs_idx, rx_bs_idx, sample_idx):
        return self.data[sample_idx][tx_bs_idx][rx_bs_idx]


class CommunicationDataset:
    def __init__(self, params):
        self.params = params
        self._validate_parameters(self.params)
        self.data = self._generate_data(params[c.PARAMSET_DYNAMIC_SCENES])
        
    def _validate_parameters(self, params):
        
        params['user_rows'] = np.array([0]) # Dynamic scenarios
        params[c.PARAMSET_SCENARIO_PARAMS_PATH] = os.path.join(
                os.path.abspath(params[c.PARAMSET_DATASET_FOLDER]),
                params[c.PARAMSET_SCENARIO],
                'wireless',
                'params.mat'
        )
        params[c.PARAMSET_SCENARIO_PARAMS] = RayTracingLoader.load_scenario_params(params[c.PARAMSET_SCENARIO_PARAMS_PATH])
        
        if isinstance(params[c.PARAMSET_ACTIVE_BS], list):
            params[c.PARAMSET_ACTIVE_BS] = np.array(params[c.PARAMSET_ACTIVE_BS])
            
        # BS antenna format
        params['tx_ant_objs'] = create_antennas(ant_params=params[c.PARAMSET_ANT_BS], 
                                                n_ant=len(params[c.PARAMSET_ACTIVE_BS]))
            
        # TODO: Fix number of active users..
        params[c.PARAMSET_ACTIVE_UE] = [0]
        params['rx_ant_objs'] = create_antennas(ant_params=params[c.PARAMSET_ANT_UE], 
                                                n_ant=len(params[c.PARAMSET_ACTIVE_UE]))
        
        return params
    

    
    def _generate_data(self, scenes):
        dataset = []
        for i, scene_idx in enumerate(tqdm(scenes, desc="Processing Scenes", leave=False)):
            dataset.append(self._generate_scene_data(scene_idx=scene_idx))
            
        return dataset
    
    
    def _generate_scene_data(self, scene_idx):
        params = self.params.copy()
        carrier_freq = params[c.PARAMSET_SCENARIO_PARAMS][c.PARAMSET_SCENARIO_PARAMS_CF]
        
        scene_folder = os.path.join(os.path.abspath(params[c.PARAMSET_DATASET_FOLDER]), 
                                    params[c.PARAMSET_SCENARIO],
                                    'wireless',
                                    'scene_' + str(scene_idx)
                                   )
        rt_loader = RayTracingLoader(scene_folder)
        num_active_bs = len(params[c.PARAMSET_ACTIVE_BS])
        dataset = []
        for i in range(num_active_bs):
            bs_data = {}
        
            bs_indx = params[c.PARAMSET_ACTIVE_BS]
            
            #%%
            # TODO: When adding the feature for static users, fix None for rx_idx
            # rx_idx=None to generate all users
            raydata, bs_data['bs_loc'] = rt_loader.load_data(tx_idx=bs_indx[i]-1, rx_idx=None, user=True)

            ue_channels = []
            n_ue = len(raydata['paths'])
            for j in tqdm(range(n_ue), desc=f'Generating BS{bs_indx[i]}-UE channels', leave=False):
                # TODO: Fix selecting a single antenna - antennas need to be defined for each dynamic object & static object
                paths = Paths(raydata['paths'][j], carrier_freq, params['num_paths']).apply_antenna_parameters(TX_antenna=params['tx_ant_objs'][i], RX_antenna=params['rx_ant_objs'][0])
                channel = OFDMChannel(tx_antenna=params['tx_ant_objs'][i], 
                                      rx_antenna=params['rx_ant_objs'][0], 
                                      paths=paths, 
                                      carrier_freq=carrier_freq, 
                                      bandwidth=params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_BW]* c.PARAMSET_OFDM_BW_MULT, 
                                      num_subcarriers=params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_SC_NUM],
                                      select_subcarriers=params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_SC_SAMP],
                                      rx_filter=None, #params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_LPF],
                                      params=params,
                                      doppler_shift=params['enable_Doppler']
                                     )
                channel.generate()
                ue_channels.append(channel)
            bs_data['ue'] = ue_channels
            bs_data['ue_loc'] = np.asarray(raydata['location']).reshape((-1, 3))
            
            #%%
            raydata, _ = rt_loader.load_data(tx_idx=bs_indx[i]-1, rx_idx=bs_indx-1, user=False)
            bs_channels = []
            n_bs = len(raydata['paths'])
            for j in tqdm(range(n_bs), desc=f'Generating BS{bs_indx[i]}-BS channels', leave=False):
                paths = Paths(raydata['paths'][j], carrier_freq, params['num_paths']).apply_antenna_parameters(TX_antenna=params['tx_ant_objs'][i], RX_antenna=params['tx_ant_objs'][j])
                channel = OFDMChannel(tx_antenna=params['tx_ant_objs'][i], 
                                      rx_antenna=params['tx_ant_objs'][j], 
                                      paths=paths, 
                                      carrier_freq=carrier_freq, 
                                      bandwidth=params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_BW]* c.PARAMSET_OFDM_BW_MULT, 
                                      num_subcarriers=params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_SC_NUM],
                                      select_subcarriers=params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_SC_SAMP],
                                      rx_filter=None, #params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_LPF],
                                      params=params,
                                      doppler_shift=params['enable_Doppler']
                                     )
                channel.generate()
                bs_channels.append(channel)
            bs_data['bs'] = bs_channels
            
        dataset.append(bs_data)
        return dataset
    
    def get_ue_channel(self, ue_idx, bs_idx, time_idx):
        return self.data[time_idx][bs_idx]['ue'][ue_idx]
    
    def get_bs_channel(self, tx_idx, rx_idx, time_idx):
        return self.data[time_idx][tx_idx]['bs'][rx_idx]
    
    def get_ue_location(self, ue_idx, bs_idx, time_idx):
        return self.data[time_idx][bs_idx]['ue_loc'][ue_idx]
    
    def get_bs_location(self, bs_idx, time_idx):
        return self.data[time_idx][bs_idx]['bs_loc']