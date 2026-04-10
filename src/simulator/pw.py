import numpy as np

from .fc import FC_map


def PW_map(NOC_SIZE_X, NOC_SIZE_Y, ifmap_side):
    """Map a PW layer under IS dataflow."""
    ifmap_flat_size = ifmap_side * ifmap_side
    return FC_map(NOC_SIZE_X, NOC_SIZE_Y, ifmap_flat_size)


def PW_reconfiguration_latency(NOC_SIZE_X, NOC_SIZE_Y, ifmap_side):
    num_full_passes, num_columns_last_pass, vertical_latency_last_pass = PW_map(
        NOC_SIZE_X, NOC_SIZE_Y, ifmap_side
    )
    if num_full_passes != 0:
        reconfiguration_latency = NOC_SIZE_X
    else:
        reconfiguration_latency = num_columns_last_pass
    return int(2 * reconfiguration_latency)


def num_ifmap_packets_per_node(input_activation_size):
    return int(np.ceil(input_activation_size / 4) + 1)


def Ifmap_Latency_HT_mode(Node_rank, Packet_number_per_node, Node_latency):
    latency = Packet_number_per_node * np.ceil(Node_rank / 4) + Node_latency * Node_rank - 1
    return int(latency)


def Ifmap_Latency_Normal_mode(Node_rank, Packet_number_per_node, Node_latency):
    latency = Packet_number_per_node * Node_rank + Node_latency * Node_rank
    return int(latency)


def PW_ifmap_latency_HT_mode(NOC_SIZE_X, NOC_SIZE_Y, ifmap_side, ifmap_depth, alpha, Node_latency):
    ifmap_packet_per_node = num_ifmap_packets_per_node(ifmap_depth * alpha)
    over_grid_iteration, last_grid_usage_horizontal_latency, last_grid_usage_vertical_latency = PW_map(
        NOC_SIZE_X, NOC_SIZE_Y, ifmap_side
    )
    full_ifmap_latency_ht_mode = (
        over_grid_iteration * (ifmap_packet_per_node * np.ceil(NOC_SIZE_X / 4))
        + Ifmap_Latency_HT_mode(last_grid_usage_horizontal_latency, ifmap_packet_per_node, Node_latency)
    )
    return int(full_ifmap_latency_ht_mode)


def PW_ifmap_latency_Normal_mode(NOC_SIZE_X, NOC_SIZE_Y, ifmap_side, ifmap_depth, alpha, Node_latency):
    ifmap_packet_per_node = num_ifmap_packets_per_node(ifmap_depth * alpha)
    over_grid_iteration, last_grid_usage_horizontal_latency, last_grid_usage_vertical_latency = PW_map(
        NOC_SIZE_X, NOC_SIZE_Y, ifmap_side
    )
    ifmap_latency_normal_mode = (
        over_grid_iteration * (ifmap_packet_per_node * NOC_SIZE_X)
        + Ifmap_Latency_Normal_mode(last_grid_usage_horizontal_latency, ifmap_packet_per_node, Node_latency)
    )
    return int(ifmap_latency_normal_mode)


def PW_filter_latency(NOC_SIZE_X, NOC_SIZE_Y, ifmap_depth, number_filters, alpha, Node_latency):
    num_packets = num_ifmap_packets_per_node(ifmap_depth * number_filters * alpha * alpha)
    num_vertical_hops = NOC_SIZE_Y // 2
    num_horizontal_hops = NOC_SIZE_X
    num_total_hops = num_vertical_hops + num_horizontal_hops
    full_filter_latency = Node_latency * num_total_hops + num_packets
    return int(full_filter_latency)


def PW_parameter_breakdown(NOC_SIZE_X, NOC_SIZE_Y, ifmap_side_original, ifmap_depth, number_filters, alpha):
    num_full_passes, last_grid_usage_horizontal_latency, last_grid_usage_vertical_latency = PW_map(
        NOC_SIZE_X, NOC_SIZE_Y, ifmap_side_original
    )

    if last_grid_usage_horizontal_latency != 0 or last_grid_usage_vertical_latency != 0:
        is_last_pass = 1
    else:
        is_last_pass = 0

    total_passes = num_full_passes + is_last_pass

    num_ifmap_per_node = ifmap_depth * total_passes * alpha
    num_filter_per_node = number_filters * ifmap_depth * alpha * alpha

    total_param = num_ifmap_per_node + num_filter_per_node

    ifmap_per_node_ratio = 100 * num_ifmap_per_node / total_param
    filter_per_node_ratio = 100 * num_filter_per_node / total_param

    return (
        int(num_ifmap_per_node),
        int(num_filter_per_node),
        float(ifmap_per_node_ratio),
        float(filter_per_node_ratio),
    )