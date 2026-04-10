from .conv import(
    CONV_send_filter_latency,
    CONV_send_ifmap_latency_HT,
    CONV_send_ifmap_latency_Normal,
    CONV_parameter_breakdown,
    CONV_reconfiguration_latency
)

def DW_send_filter_latency(Kernel_side, ifmap_depth, num_pixels_per_packet, node_latency, NOC_SIZE_X):
    latency = CONV_send_filter_latency(
        Kernel_side, 1, ifmap_depth, num_pixels_per_packet, node_latency, NOC_SIZE_X
    )
    return latency


def DW_send_ifmap_latency_HT(Kernel_side, ifmap_side, ifmap_depth, num_pixels_per_packet, node_latency, NOC_SIZE_X, NOC_SIZE_Y):
    total_latency = CONV_send_ifmap_latency_HT(
        Kernel_side, ifmap_side, ifmap_depth, num_pixels_per_packet, node_latency, NOC_SIZE_X, NOC_SIZE_Y
    )
    return total_latency


def DW_send_ifmap_latency_Normal(Kernel_side, ifmap_side, ifmap_depth, num_pixels_per_packet, node_latency, NOC_SIZE_X, NOC_SIZE_Y):
    total_latency = CONV_send_ifmap_latency_Normal(
        Kernel_side, ifmap_side, ifmap_depth, num_pixels_per_packet, node_latency, NOC_SIZE_X, NOC_SIZE_Y
    )
    return total_latency


def DW_parameter_breakdown(Kernel_side, ifmap_side, ifmap_side_original, ifmap_depth, NOC_SIZE_X, NOC_SIZE_Y):
    num_ifmap_per_node, num_filter_per_node, ifmap_per_node_ratio, filter_per_node_ratio = CONV_parameter_breakdown(
        Kernel_side, 1, ifmap_side, ifmap_side_original, ifmap_depth, NOC_SIZE_X, NOC_SIZE_Y
    )
    return num_ifmap_per_node, num_filter_per_node, ifmap_per_node_ratio, filter_per_node_ratio


def DW_reconfiguration_latency(Kernel_side, ifmap_side, NOC_SIZE_X, NOC_SIZE_Y):
    latency_reconfiguration = CONV_reconfiguration_latency(
        Kernel_side, ifmap_side, NOC_SIZE_X, NOC_SIZE_Y
    )
    return latency_reconfiguration