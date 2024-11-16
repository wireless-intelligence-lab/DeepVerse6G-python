import numpy as np

def construct_radar_signal(tx_ant_size, tx_rotation, tx_FoV, tx_ant_spacing, rx_ant_size, rx_rotation, rx_FoV, rx_ant_spacing, path_params, params):
    # Initialization
    Fs = params['Fs']
    Ts = 1 / Fs
    T_PRI = params['T_PRI']
    N_chirp = params['N_chirp']
    N_samples = params['N_samples']
    num_paths = path_params['num_paths']
    F0_active = params['carrier_freq']

    # TX antenna parameters for a UPA structure
    M_TX_ind = antenna_channel_map(1, tx_ant_size[0], tx_ant_size[1], 0)
    M_TX = np.prod(tx_ant_size)
    kd_TX = 2 * np.pi * tx_ant_spacing

    # RX antenna parameters for a UPA structure
    M_RX_ind = antenna_channel_map(1, rx_ant_size[0], rx_ant_size[1], 0)
    M_RX = np.prod(rx_ant_size)
    kd_RX = 2 * np.pi * rx_ant_spacing

    # Handle case with no paths
    if num_paths == 0:
        return np.zeros((M_RX, M_TX, N_samples, N_chirp), dtype=np.complex128)

    # Compute DoD and DoA angles based on panel orientations
    DoD_theta, DoD_phi, DoA_theta, DoA_phi = antenna_rotation(tx_rotation, path_params['DoD_theta'], path_params['DoD_phi'], rx_rotation, path_params['DoA_theta'], path_params['DoA_phi'])

    # TX and RX Array Responses
    array_response_TX = compute_array_response(M_TX_ind, kd_TX, DoD_theta, DoD_phi)
    array_response_RX = compute_array_response(M_RX_ind, kd_RX, DoA_theta, DoA_phi)

    # Normalized delays and power adjustments
    delay_normalized = normalize_delays(path_params['ToA'], Ts, N_samples)
    power = adjust_power(path_params['power'], delay_normalized, N_samples)

    # Filter paths outside of FoV
    path_FoV_filter = filter_paths_FoV(DoD_theta, DoD_phi, tx_FoV, DoA_theta, DoA_phi, rx_FoV)
    power[~path_FoV_filter] = 0

    # LoS status computation
    channel_LoS_status = compute_LoS_status(path_params['LoS_status'], path_FoV_filter)

    # Compute IF signal
    IF_signal = compute_IF_signal(array_response_TX, array_response_RX, delay_normalized, power, path_params, params, T_PRI, N_chirp, N_samples, F0_active, M_RX, M_TX)
    
    return IF_signal

def antenna_channel_map(dummy1, num_rows, num_cols, dummy2):
    # Dummy implementation to match MATLAB function signature
    return np.arange(num_rows * num_cols).reshape((num_rows, num_cols))

def antenna_rotation(tx_rotation, DoD_theta, DoD_phi, rx_rotation, DoA_theta, DoA_phi):
    # Dummy implementation for antenna rotation
    # Real implementation should rotate DoD and DoA angles based on the given rotations
    return DoD_theta, DoD_phi, DoA_theta, DoA_phi

def compute_array_response(M_ind, kd, theta, phi):
    # Compute array response
    gamma = 1j * kd * np.array([np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)),
                                np.sin(np.deg2rad(theta)) * np.sin(np.deg2rad(phi)),
                                np.cos(np.deg2rad(theta))])
    return np.exp(M_ind @ gamma)

def normalize_delays(ToA, Ts, N_samples):
    # Normalize delays
    delay_normalized = ToA / Ts
    delay_normalized[delay_normalized > (N_samples - 1)] = (N_samples - 1)
    return delay_normalized

def adjust_power(power, delay_normalized, N_samples):
    # Adjust power based on normalized delays
    power[delay_normalized > (N_samples - 1)] = 0
    return power

def filter_paths_FoV(DoD_theta, DoD_phi, tx_FoV, DoA_theta, DoA_phi, rx_FoV):
    # Filter paths based on Field of View (FoV)
    FoV_TX = antenna_FoV(DoD_theta, DoD_phi, tx_FoV)
    FoV_RX = antenna_FoV(DoA_theta, DoA_phi, rx_FoV)
    return FoV_TX & FoV_RX

def antenna_FoV(theta, phi, FoV):
    # Dummy implementation for antenna FoV filtering
    # Real implementation should check if the angles are within the FoV
    return np.ones_like(theta, dtype=bool)

def compute_LoS_status(LoS_status, path_FoV_filter):
    # Compute Line-of-Sight (LoS) status
    if np.sum(path_FoV_filter) > 0:
        return np.sum(LoS_status & path_FoV_filter) > 0
    else:
        return -1

def compute_IF_signal(array_response_TX, array_response_RX, delay_normalized, power, path_params, params, T_PRI, N_chirp, N_samples, F0_active, M_RX, M_TX):
    # Compute the IF signal

    ang_conv = np.pi / 180
    Ts = 1 / params['Fs']
    IF_sampling_mat = np.zeros((N_samples, path_params['num_paths']))
    for ll in range(path_params['num_paths']):
        IF_sampling_mat[int(np.ceil(delay_normalized[ll])):N_samples, ll] = 1
    time_fast = Ts * np.arange(N_samples)

    if params['comp_speed'] in [5, 4, 3]:
        time_slow = time_fast[:, None, None] + (np.arange(N_chirp) * T_PRI).reshape((1, 1, -1))
        Tau_rt = compute_Tau_rt(delay_normalized, time_slow, path_params)
        Extra_phase = np.exp(1j * path_params['phase'] * ang_conv)
        Phase_terms = compute_Phase_terms(F0_active, params, Tau_rt, time_fast)
        IF_mat = np.sqrt(power) * np.conj(Extra_phase) * Phase_terms * IF_sampling_mat

        IF_signal = calculate_IF_signal(params, array_response_RX, array_response_TX, IF_mat, M_RX, M_TX, N_samples, N_chirp, path_params)
    else:
        IF_signal = compute_IF_signal_methods_1_2(params, array_response_RX, array_response_TX, path_params, delay_normalized, power, time_fast, F0_active, ang_conv, N_samples, N_chirp, T_PRI, M_RX, M_TX, IF_sampling_mat)
    
    return IF_signal

def compute_Tau_rt(delay_normalized, time_slow, path_params):
    # Compute Tau_rt for Doppler effects
    Tau3_rt = (path_params['Doppler_acc'] * (time_slow ** 2)) / (2 * 3e8)
    Tau2_rt = (path_params['Doppler_vel'] * time_slow) / 3e8
    return delay_normalized[:, None, None] * Ts + Tau2_rt + Tau3_rt

def compute_Phase_terms(F0_active, params, Tau_rt, time_fast):
    # Compute phase terms for the IF signal
    return np.exp(1j * 2 * np.pi * (F0_active * Tau_rt - 0.5 * params['S'] * (Tau_rt ** 2) + params['S'] * time_fast[:, None, None] * Tau_rt))

def calculate_IF_signal(params, array_response_RX, array_response_TX, IF_mat, M_RX, M_TX, N_samples, N_chirp, path_params):
    # Calculate the IF signal based on computation speed
    if params['comp_speed'] == 5:
        IF_signal = np.sum(array_response_RX[:, None, None, :, None] * array_response_TX[None, :, None, :, None] * IF_mat[None, None, :, :, :], axis=3)
        IF_signal = IF_signal.reshape((M_RX, M_TX, N_samples, N_chirp))
    elif params['comp_speed'] == 4:
        IF_signal = np.zeros((M_RX, M_TX, N_samples, N_chirp), dtype=np.complex128)
        for ll in range(N_chirp):
            IF_signal[:, :, :, ll] = np.sum(array_response_RX[:, None, None, :] * array_response_TX[None, :, None, :] * IF_mat[:, :, ll, None, :], axis=3)
    else:
        IF_signal = np.zeros((M_RX, M_TX, N_samples, N_chirp), dtype=np.complex128)
        for aa in range(N_samples):
            for ll in range(N_chirp):
                IF_signal[:, :, aa, ll] = np.sum(array_response_RX[:, None, :] * array_response_TX[None, :, :] * IF_mat[aa, :, ll, None, :], axis=2)
    return IF_signal

def compute_IF_signal_methods_1_2(params, array_response_RX, array_response_TX, path_params, delay_normalized, power, time_fast, F0_active, ang_conv, N_samples, N_chirp, T_PRI, M_RX, M_TX, IF_sampling_mat):
    # Compute IF signal for methods 1 and 2
    IF_signal = np.zeros((M_RX, M_TX, N_samples, N_chirp), dtype=np.complex128)
    for ll in range(N_chirp):
        time_slow = time_fast + (ll * T_PRI)
        Tau_rt = compute_Tau_rt(delay_normalized, time_slow, path_params)
        Extra_phase = np.exp(1j * path_params['phase'] * ang_conv)
        Phase_terms = compute_Phase_terms(F0_active, params, Tau_rt, time_fast)
        IF_mat = np.sqrt(power) * np.conj(Extra_phase) * Phase_terms * IF_sampling_mat

        if params['comp_speed'] == 2:
            IF_signal[:, :, :, ll] = np.sum(array_response_RX[:, None, None, :] * array_response_TX[None, :, None, :] * IF_mat[:, :, None, :], axis=3)
        else:
            for aa in range(N_samples):
                IF_signal[:, :, aa, ll] = np.sum(array_response_RX[:, None, :] * array_response_TX[None, :, :] * IF_mat[aa, :, None, :], axis=2)
    return IF_signal
