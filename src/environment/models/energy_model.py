# TODO: fancy add to input
class EnergyModel:
    # TODO: fancy accurate packet size
    e_elec = 50
    power_amplifier_for_fs = 10
    power_amplifier_for_amp = 0.0013
    distance_threshold = 100
    packet_size = 1

    @staticmethod
    def calculate_consumed_energy(transition_distance, num_of_packets):
        k = num_of_packets * EnergyModel.packet_size
        distance = transition_distance
        if distance < EnergyModel.distance_threshold:
            e_t = k * (EnergyModel.e_elec + EnergyModel.power_amplifier_for_fs * (distance ** 2))
        else:
            e_t = k * (EnergyModel.e_elec + EnergyModel.power_amplifier_for_amp * (distance ** 4))
        e_r = k * EnergyModel.e_elec
        energy = e_t + e_r
        # TODO: fancy remove magic number
        energy /= 1e6
        return round(energy, 3)
