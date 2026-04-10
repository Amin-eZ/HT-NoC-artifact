from .fc import (
    FC_compute_latency,
    FC_reconfiguration_latency,
    activation_latency,
    sum_collection_latency,
    weight_latency_phase_Normal_mode,
    weight_latency_phase_HT_mode,
)


def FC_phase_breakdown_normal(NOC_SIZE_X, NOC_SIZE_Y, Input_size, Output_size, Node_latency):
    """
    FC layer phase breakdown for the baseline NoC (Normal mode only).
    """
    weight_lat = weight_latency_phase_Normal_mode(
        NOC_SIZE_X, NOC_SIZE_Y, Input_size, Output_size, Node_latency
    )
    activation_lat = activation_latency(
        NOC_SIZE_X, NOC_SIZE_Y, Input_size, Output_size, Node_latency
    )
    compute_lat = FC_compute_latency(
        NOC_SIZE_X, NOC_SIZE_Y, Input_size, Output_size
    )
    sum_lat = sum_collection_latency(
        NOC_SIZE_X, NOC_SIZE_Y, Input_size, Output_size, Node_latency
    )

    total = weight_lat + activation_lat + compute_lat + sum_lat

    return {
        "weight": int(weight_lat),
        "activation": int(activation_lat),
        "compute": int(compute_lat),
        "sum_collection": int(sum_lat),
        "reconfiguration": 0,
        "total": int(total),
    }


def FC_phase_breakdown_ht(NOC_SIZE_X, NOC_SIZE_Y, Input_size, Output_size, Node_latency):
    """
    FC layer phase breakdown for HT-NoC.
    """
    weight_lat = weight_latency_phase_HT_mode(
        NOC_SIZE_X, NOC_SIZE_Y, Input_size, Output_size, Node_latency
    )
    activation_lat = activation_latency(
        NOC_SIZE_X, NOC_SIZE_Y, Input_size, Output_size, Node_latency
    )
    compute_lat = FC_compute_latency(
        NOC_SIZE_X, NOC_SIZE_Y, Input_size, Output_size
    )
    sum_lat = sum_collection_latency(
        NOC_SIZE_X, NOC_SIZE_Y, Input_size, Output_size, Node_latency
    )
    reconfig_lat = FC_reconfiguration_latency(
        NOC_SIZE_X, NOC_SIZE_Y, Output_size
    )

    total = weight_lat + activation_lat + compute_lat + sum_lat + reconfig_lat

    return {
        "weight": int(weight_lat),
        "activation": int(activation_lat),
        "compute": int(compute_lat),
        "sum_collection": int(sum_lat),
        "reconfiguration": int(reconfig_lat),
        "total": int(total),
    }


def FFN_phase_breakdown_normal(
    NOC_SIZE_X,
    NOC_SIZE_Y,
    FC1_Input_size,
    FC1_Output_size,
    FC2_Input_size,
    FC2_Output_size,
    Node_latency,
):
    """
    FFN breakdown for baseline NoC.
    """
    fc1 = FC_phase_breakdown_normal(
        NOC_SIZE_X, NOC_SIZE_Y, FC1_Input_size, FC1_Output_size, Node_latency
    )
    fc2 = FC_phase_breakdown_normal(
        NOC_SIZE_X, NOC_SIZE_Y, FC2_Input_size, FC2_Output_size, Node_latency
    )

    ffn_total = {
        "weight": fc1["weight"] + fc2["weight"],
        "activation": fc1["activation"] + fc2["activation"],
        "compute": fc1["compute"] + fc2["compute"],
        "sum_collection": fc1["sum_collection"] + fc2["sum_collection"],
        "reconfiguration": 0,
        "total": fc1["total"] + fc2["total"],
    }

    return {
        "fc1": fc1,
        "fc2": fc2,
        "ffn_total": ffn_total,
    }


def FFN_phase_breakdown_ht(
    NOC_SIZE_X,
    NOC_SIZE_Y,
    FC1_Input_size,
    FC1_Output_size,
    FC2_Input_size,
    FC2_Output_size,
    Node_latency,
):
    """
    FFN breakdown for HT-NoC.
    """
    fc1 = FC_phase_breakdown_ht(
        NOC_SIZE_X, NOC_SIZE_Y, FC1_Input_size, FC1_Output_size, Node_latency
    )
    fc2 = FC_phase_breakdown_ht(
        NOC_SIZE_X, NOC_SIZE_Y, FC2_Input_size, FC2_Output_size, Node_latency
    )

    ffn_total = {
        "weight": fc1["weight"] + fc2["weight"],
        "activation": fc1["activation"] + fc2["activation"],
        "compute": fc1["compute"] + fc2["compute"],
        "sum_collection": fc1["sum_collection"] + fc2["sum_collection"],
        "reconfiguration": fc1["reconfiguration"] + fc2["reconfiguration"],
        "total": fc1["total"] + fc2["total"],
    }

    return {
        "fc1": fc1,
        "fc2": fc2,
        "ffn_total": ffn_total,
    }


def FFN_speedup(
    NOC_SIZE_X,
    NOC_SIZE_Y,
    FC1_Input_size,
    FC1_Output_size,
    FC2_Input_size,
    FC2_Output_size,
    Node_latency,
):
    baseline = FFN_phase_breakdown_normal(
        NOC_SIZE_X,
        NOC_SIZE_Y,
        FC1_Input_size,
        FC1_Output_size,
        FC2_Input_size,
        FC2_Output_size,
        Node_latency,
    )

    ht = FFN_phase_breakdown_ht(
        NOC_SIZE_X,
        NOC_SIZE_Y,
        FC1_Input_size,
        FC1_Output_size,
        FC2_Input_size,
        FC2_Output_size,
        Node_latency,
    )

    baseline_total = baseline["ffn_total"]["total"]
    ht_total = ht["ffn_total"]["total"]
    speedup = baseline_total / ht_total

    return {
        "baseline_total": baseline_total,
        "ht_total": ht_total,
        "speedup": speedup,
    }