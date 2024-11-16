%% General Parameters
dv.basestations = [1]; % Basestations to be included

dv.dataset_folder = r'D:\\DeepVerse\\scenarios';
dv.scenario = 'Town01-Carla';

dv.scenes = [100:101]; % Scenes to be included
    
dv.comm.enable = true;
dv.radar.enable = true;

dv.camera = true;
dv.camera_id = [1:5];

dv.lidar = true;
dv.position = true;

%% Comm
dv.comm.bs_antenna.shape = [32, 1];
dv.comm.bs_antenna.rotation = [5, 10, 20];
dv.comm.bs_antenna.spacing = 0.5;
dv.comm.bs_antenna.FoV = [360, 180];

dv.comm.ue_antenna.shape = [1, 1];
dv.comm.ue_antenna.rotation = [0, 30, 0];
dv.comm.ue_antenna.spacing = 0.5;
dv.comm.ue_antenna.FoV = [360, 180];

dv.comm.OFDM.bandwidth = 0.05;
dv.comm.OFDM.subcarriers = 512;
dv.comm.OFDM.selected_subcarriers = [0, 1];

dv.comm.activate_RX_filter = 0;
dv.comm.generate_OFDM_channels = 1;
dv.comm.num_paths = 25;
dv.comm.enable_Doppler = 1;

%% Radar
dv.radar.tx_antenna.shape = [1, 1];
dv.radar.tx_antenna.rotation = [0, 0, -90];
dv.radar.tx_antenna.spacing = 0.5;
dv.radar.tx_antenna.FoV = [360, 180];

dv.radar.rx_antenna.shape = [32, 1];
dv.radar.rx_antenna.rotation = [0, 0, -90];
dv.radar.rx_antenna.spacing = 0.5;
dv.radar.rx_antenna.FoV = [360, 180];

dv.radar.FMCW.chirp_slope = 15e12;
dv.radar.FMCW.Fs = 4e6;
dv.radar.FMCW.n_samples_per_chirp = 512;
dv.radar.FMCW.n_chirps = 256;

dv.radar.num_paths = 5000;