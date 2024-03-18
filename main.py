from simulator import Simulator
import argparse

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Process simulation parameters.')

    # Adding arguments
    parser.add_argument('--num_nodes', type=int, required=True, help='Number of nodes')
    parser.add_argument('--slowfrac', type=float, required=True, help='Fraction of nodes that are slow')
    parser.add_argument('--lowCPUfrac', type=float, required=True, help='Fraction of nodes with low CPU')
    parser.add_argument('--txnDelay_meantime', type=float, required=True, help='Mean time for transaction delay')
    parser.add_argument('--max_sim_time', type=float, required=True, help='Maximum simulation time')

    # Parsing arguments
    args = parser.parse_args()

    # Accessing the arguments
    num_nodes = args.num_nodes
    slowfrac = args.slowfrac
    lowCPUfrac = args.lowCPUfrac
    txnDelay_meantime = args.txnDelay_meantime
    max_sim_time = args.max_sim_time

    sim = Simulator(num_nodes,slowfrac,lowCPUfrac,txnDelay_meantime, max_sim_time)

    sim.run()

