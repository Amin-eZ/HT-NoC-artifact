import math
import numpy as np


def FC_map(NOC_SIZE_X, NOC_SIZE_Y, Output_activation_Size):
    """
    Map an FC layer under OS dataflow.

    Returns:
        over_grid_iteration                : Number of full grid iterations.
        last_grid_usage_horizontal_latency : Number of columns of the last tile.
        last_grid_usage_vertical_latency   : Number of rows of the last tile.
    """
    grid_size = NOC_SIZE_X * NOC_SIZE_Y
    over_grid_iteration = Output_activation_Size // grid_size
    last_grid_iteration_size = Output_activation_Size % grid_size
    last_grid_iteration_full_row_number = last_grid_iteration_size // NOC_SIZE_X
    last_grid_iteration_row_number = np.ceil(last_grid_iteration_size / NOC_SIZE_X)

    if last_grid_iteration_full_row_number >= 1:
        last_grid_usage_horizontal_latency = NOC_SIZE_X
    else:
        last_grid_usage_horizontal_latency = last_grid_iteration_size % NOC_SIZE_X

    last_grid_usage_vertical_latency = last_grid_iteration_row_number

    return (
        over_grid_iteration,
        int(last_grid_usage_horizontal_latency),
        int(last_grid_usage_vertical_latency),
    )


def sum_collection_latency(
    NOC_SIZE_X, NOC_SIZE_Y, Input_activation_size, Output_activation_Size, Node_latency
):
    """Compute total latency for sum collection."""
    (
        over_grid_iteration,
        last_grid_usage_horizontal_latency,
        last_grid_usage_vertical_latency,
    ) = FC_map(NOC_SIZE_X, NOC_SIZE_Y, Output_activation_Size)

    add_last_pass_memory_latency = 0
    add_full_pass_memory_latency = 0

    if last_grid_usage_vertical_latency == 0:
        add_last_pass_memory_latency = 0
    else:
        add_last_pass_memory_latency = 1

    if over_grid_iteration == 0:
        add_full_pass_memory_latency = 0
    else:
        add_full_pass_memory_latency = 1

    sum_latency = (
        over_grid_iteration
        * (Node_latency * (NOC_SIZE_Y) + add_full_pass_memory_latency * 3)
        + last_grid_usage_vertical_latency * Node_latency
        + add_last_pass_memory_latency * 3
    )
    return int(sum_latency)


def FC_compute_latency(NOC_SIZE_X, NOC_SIZE_Y, Input_layer_size, Output_activation_Size):
    latency_one_pass = Input_layer_size
    (
        over_grid_iteration,
        last_grid_usage_horizontal_latency,
        last_grid_usage_vertical_latency,
    ) = FC_map(NOC_SIZE_X, NOC_SIZE_Y, Output_activation_Size)

    if last_grid_usage_vertical_latency == 0:
        num_passes = over_grid_iteration
    else:
        num_passes = over_grid_iteration + 1

    latency = num_passes * latency_one_pass
    return int(latency)


def num_weight_packets_per_node(Input_activation_size):
    total_num_packets = np.ceil(Input_activation_size / 4) + 1
    return int(total_num_packets)


def num_activation_packets_per_node(Input_activation_size):
    total_num_packets = np.ceil(Input_activation_size / 4) + 1
    return int(total_num_packets)


def activation_reuse_latency(Node_rank, Packet_number_per_node, Node_latency):
    """Data reuse activation latency: latency to reach Node_rank."""
    latency = Node_latency * Node_rank + Packet_number_per_node - 1
    return int(latency)


def activation_latency(
    NOC_SIZE_X, NOC_SIZE_Y, Input_activation_size, Output_activation_Size, Node_latency
):
    """Latency of input neuron propagation phase."""
    activation_packets_per_node = num_activation_packets_per_node(Input_activation_size)
    (
        over_grid_iteration,
        last_grid_usage_horizontal_latency,
        last_grid_usage_vertical_latency,
    ) = FC_map(NOC_SIZE_X, NOC_SIZE_Y, Output_activation_Size)

    if over_grid_iteration == 0:
        full_activation_latency = activation_reuse_latency(
            last_grid_usage_horizontal_latency, activation_packets_per_node, Node_latency
        )
    else:
        full_activation_latency = activation_reuse_latency(
            NOC_SIZE_X, activation_packets_per_node, Node_latency
        )
    return int(full_activation_latency)


def Weight_Latency_HT(Node_rank, Packet_number_per_node, Node_latency):
    """Latency under full HT mode."""
    latency = Packet_number_per_node * np.ceil(Node_rank / 4) + Node_latency * Node_rank - 1
    return int(latency)


def Weight_Latency_Normal(Node_rank, Packet_number_per_node, Node_latency):
    """Latency under Normal mode."""
    latency = Packet_number_per_node * Node_rank + Node_latency * Node_rank
    return int(latency)


def weight_latency_phase_HT_mode(
    NOC_SIZE_X, NOC_SIZE_Y, Input_activation_size, Output_activation_Size, Node_latency
):
    """Latency of the weight propagation phase under full HT mode."""
    weight_packets_per_node = num_weight_packets_per_node(Input_activation_size)
    (
        over_grid_iteration,
        last_grid_usage_horizontal_latency,
        last_grid_usage_vertical_latency,
    ) = FC_map(NOC_SIZE_X, NOC_SIZE_Y, Output_activation_Size)

    full_weight_latency_4_outputs = (
        over_grid_iteration
        * Weight_Latency_HT(NOC_SIZE_X, weight_packets_per_node, Node_latency)
        + Weight_Latency_HT(
            last_grid_usage_horizontal_latency, weight_packets_per_node, Node_latency
        )
    )
    return int(full_weight_latency_4_outputs)


def weight_latency_phase_Normal_mode(
    NOC_SIZE_X, NOC_SIZE_Y, Input_activation_size, Output_activation_Size, Node_latency
):
    """Latency of the weight propagation phase under Normal mode."""
    weight_packets_per_node = num_weight_packets_per_node(Input_activation_size)
    (
        over_grid_iteration,
        last_grid_usage_horizontal_latency,
        last_grid_usage_vertical_latency,
    ) = FC_map(NOC_SIZE_X, NOC_SIZE_Y, Output_activation_Size)

    full_weight_latency_1_output = (
        over_grid_iteration
        * Weight_Latency_Normal(NOC_SIZE_X, weight_packets_per_node, Node_latency)
        + Weight_Latency_Normal(
            last_grid_usage_horizontal_latency, weight_packets_per_node, Node_latency
        )
    )
    return int(full_weight_latency_1_output)


def FC_reconfiguration_latency(NOC_SIZE_X, NOC_SIZE_Y, Output_activation_Size):
    num_full_passes, num_columns_last_pass, vertical_latency_last_pass = FC_map(
        NOC_SIZE_X, NOC_SIZE_Y, Output_activation_Size
    )
    if num_full_passes != 0:
        reconfiguration_latency = NOC_SIZE_X
    else:
        reconfiguration_latency = num_columns_last_pass
    return int(2 * reconfiguration_latency)