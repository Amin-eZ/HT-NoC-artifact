import numpy as np


def CONV_map(Kernel_side, ifmap_side, NOC_SIZE_X, NOC_SIZE_Y):
    num_full_passes, num_last_pass_full_columns, num_remnant_Y_columns = 0, 0, 0

    if NOC_SIZE_Y >= Kernel_side:
        ofmap_size = ifmap_side - Kernel_side + 1
        virtual_configuration_X_size = Kernel_side
        virtual_configuration_Y_size = ofmap_size
        num_virtual_columns_per_pass = NOC_SIZE_X * (NOC_SIZE_Y // Kernel_side)

        num_full_passes = virtual_configuration_Y_size // num_virtual_columns_per_pass
        num_last_pass_full_columns = (virtual_configuration_Y_size % num_virtual_columns_per_pass) // NOC_SIZE_X
        num_remnant_Y_columns = ((virtual_configuration_Y_size % num_virtual_columns_per_pass) % NOC_SIZE_X)

    return int(num_full_passes), int(num_last_pass_full_columns), int(num_remnant_Y_columns)


def CONV_send_filter_latency(Kernel_side, kernel_number, ifmap_depth, num_pixels_per_packet, node_latency, NOC_SIZE_X):
    """
    Latency of filter propagation.
    """
    number_payload_packets = np.ceil((Kernel_side * kernel_number * ifmap_depth) / num_pixels_per_packet)
    latency = (node_latency * NOC_SIZE_X) + number_payload_packets + 1
    return int(latency + 1)  # +1 for configuration packet


def CONV_send_ifmap_latency_to_X_HT(ifmap_side, num_pixels_per_packet, node_latency, NOC_SIZE_X):
    number_of_packets = 1 + np.ceil(ifmap_side / num_pixels_per_packet)

    if NOC_SIZE_X == 1:
        latency_to_X = node_latency + number_of_packets
    elif NOC_SIZE_X == 2:
        latency_to_X = 3 * node_latency + number_of_packets
    elif NOC_SIZE_X == 3:
        latency_to_X = 5 * node_latency + number_of_packets
    elif NOC_SIZE_X == 4:
        latency_to_X = 7 * node_latency + number_of_packets
    elif NOC_SIZE_X == 5:
        latency_to_X = 7 * node_latency + 2 * number_of_packets
    else:
        latency_to_X = 8 * node_latency + number_of_packets * (1 + NOC_SIZE_X // 5)

    return int(latency_to_X + 1)  # +1 for configuration packet


def CONV_send_ifmap_latency_HT(Kernel_side, ifmap_side, ifmap_depth, num_pixels_per_packet, node_latency, NOC_SIZE_X, NOC_SIZE_Y):
    num_full_passes, num_last_pass_full_columns, num_remnant_Y_columns = CONV_map(
        Kernel_side, ifmap_side, NOC_SIZE_X, NOC_SIZE_Y
    )

    one_pass_latency = CONV_send_ifmap_latency_to_X_HT(
        ifmap_side, num_pixels_per_packet, node_latency, NOC_SIZE_X
    )

    if num_last_pass_full_columns == 0:
        last_pass_max_column_number = num_remnant_Y_columns
    else:
        last_pass_max_column_number = NOC_SIZE_X

    last_channel_last_pass_latency = CONV_send_ifmap_latency_to_X_HT(
        ifmap_side, num_pixels_per_packet, node_latency, last_pass_max_column_number
    )

    number_ifmap_payload_packets = np.ceil(ifmap_side / num_pixels_per_packet)
    read_from_memory_one_full_pass_one_channel_latency = np.ceil(NOC_SIZE_X / 5) * (1 + number_ifmap_payload_packets)
    read_from_memory_all_full_passes_one_channel_latency = read_from_memory_one_full_pass_one_channel_latency * num_full_passes

    read_from_memory_all_full_passes_full_channel_latency = read_from_memory_all_full_passes_one_channel_latency * ifmap_depth
    read_from_memory_last_pass_one_channel_latency = np.ceil(last_pass_max_column_number / 5) * (1 + number_ifmap_payload_packets)
    read_from_memory_last_pass_all_minus_1_channel_latency = read_from_memory_last_pass_one_channel_latency * (ifmap_depth - 1)
    read_from_memory_last_pass_last_channel_latency = CONV_send_ifmap_latency_to_X_HT(
        ifmap_side, num_pixels_per_packet, node_latency, last_pass_max_column_number
    )

    last_pass_total_latency = read_from_memory_last_pass_all_minus_1_channel_latency + read_from_memory_last_pass_last_channel_latency
    total_latency = read_from_memory_all_full_passes_full_channel_latency + last_pass_total_latency

    return int(total_latency)


def CONV_send_ifmap_latency_to_X_Normal(ifmap_side, num_pixels_per_packet, node_latency, NOC_SIZE_X):
    number_of_packets = 1 + np.ceil(ifmap_side / num_pixels_per_packet)

    if NOC_SIZE_X == 1:
        latency_to_X = node_latency + number_of_packets
    elif NOC_SIZE_X == 2:
        latency_to_X = 3 * node_latency + number_of_packets
    else:
        latency_to_X = 5 * node_latency + number_of_packets * (1 + NOC_SIZE_X // 2)

    return int(latency_to_X + 1)  # +1 for configuration packet


def CONV_send_ifmap_latency_Normal(Kernel_side, ifmap_side, ifmap_depth, num_pixels_per_packet, node_latency, NOC_SIZE_X, NOC_SIZE_Y):
    num_full_passes, num_last_pass_full_columns, num_remnant_Y_columns = CONV_map(
        Kernel_side, ifmap_side, NOC_SIZE_X, NOC_SIZE_Y
    )

    one_pass_latency = CONV_send_ifmap_latency_to_X_Normal(
        ifmap_side, num_pixels_per_packet, node_latency, NOC_SIZE_X
    )

    if num_last_pass_full_columns == 0:
        last_pass_max_column_number = num_remnant_Y_columns
    else:
        last_pass_max_column_number = NOC_SIZE_X

    last_channel_last_pass_latency = CONV_send_ifmap_latency_to_X_HT(
        ifmap_side, num_pixels_per_packet, node_latency, last_pass_max_column_number
    )

    if NOC_SIZE_X % 2 == 0:
        n_add = 1
    else:
        n_add = 0

    if last_pass_max_column_number % 2 == 0:
        nlpmcn = 1
    else:
        nlpmcn = 0

    number_ifmap_payload_packets = np.ceil(ifmap_side / num_pixels_per_packet)
    read_from_memory_one_full_pass_one_channel_latency = np.ceil((NOC_SIZE_X + n_add) / 2) * (1 + number_ifmap_payload_packets)
    read_from_memory_all_full_passes_one_channel_latency = read_from_memory_one_full_pass_one_channel_latency * num_full_passes

    read_from_memory_all_full_passes_full_channel_latency = read_from_memory_all_full_passes_one_channel_latency * ifmap_depth
    read_from_memory_last_pass_one_channel_latency = np.ceil((last_pass_max_column_number + nlpmcn) / 2) * (1 + number_ifmap_payload_packets)
    read_from_memory_last_pass_all_minus_1_channel_latency = read_from_memory_last_pass_one_channel_latency * (ifmap_depth - 1)
    read_from_memory_last_pass_last_channel_latency = CONV_send_ifmap_latency_to_X_HT(
        ifmap_side, num_pixels_per_packet, node_latency, last_pass_max_column_number
    )

    last_pass_total_latency = read_from_memory_last_pass_all_minus_1_channel_latency + read_from_memory_last_pass_last_channel_latency
    total_latency = read_from_memory_all_full_passes_full_channel_latency + last_pass_total_latency

    return int(total_latency)


def CONV_parameter_breakdown(Kernel_side, Kernel_number, ifmap_side, ifmap_side_original, ifmap_depth, NOC_SIZE_X, NOC_SIZE_Y):
    num_full_passes, num_last_pass_full_columns, num_remnant_Y_columns = CONV_map(
        Kernel_side, ifmap_side, NOC_SIZE_X, NOC_SIZE_Y
    )

    if num_last_pass_full_columns != 0 or num_remnant_Y_columns != 0:
        is_last_pass = 1
    else:
        is_last_pass = 0

    total_passes = num_full_passes + is_last_pass

    num_ifmap_per_node = ifmap_side_original * ifmap_depth * total_passes
    num_filter_per_node = Kernel_side * ifmap_depth * Kernel_number

    total_param = num_ifmap_per_node + num_filter_per_node

    ifmap_per_node_ratio = 100 * num_ifmap_per_node / total_param
    filter_per_node_ratio = 100 * num_filter_per_node / total_param

    return (
        int(num_ifmap_per_node),
        int(num_filter_per_node),
        float(ifmap_per_node_ratio),
        float(filter_per_node_ratio),
    )


def CONV_reconfiguration_latency(Kernel_side, ifmap_side, NOC_SIZE_X, NOC_SIZE_Y):
    num_full_tiles, num_last_pass_full_columns, num_remnant_Y_columns = CONV_map(Kernel_side, ifmap_side, NOC_SIZE_X, NOC_SIZE_Y)
    
    if num_full_tiles != 0 :
        reconfiguration_latency = NOC_SIZE_X
    
    else :
        if num_last_pass_full_columns != 0:
            reconfiguration_latency = NOC_SIZE_X
        else:
            reconfiguration_latency = num_remnant_Y_columns

    return 2 * reconfiguration_latency