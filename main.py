from simulator import Simulator
import argparse

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Process simulation parameters.')

    # Adding arguments
    parser.add_argument('--num_nodes', type=int, required=True, help='Number of nodes')
    parser.add_argument('--lowCPUfrac', type=float, required=True, help='Fraction of nodes with low CPU')
    parser.add_argument('--txnDelay_meantime', type=float, required=True, help='Mean time for transaction delay')
    parser.add_argument('--max_sim_time', type=float, required=True, help='Maximum simulation time')
    parser.add_argument('--attacker1_hp', type=float, required=True, help='hashing power of attacker1')
    parser.add_argument('--attacker2_hp', type=float, required=True, help='hashing power of attacker2')

    # Parsing arguments
    args = parser.parse_args()

    # Accessing the arguments
    num_nodes = args.num_nodes
    lowCPUfrac = args.lowCPUfrac
    txnDelay_meantime = args.txnDelay_meantime
    max_sim_time = args.max_sim_time
    attacker1_hp = args.attacker1_hp
    attacker2_hp = args.attacker2_hp

    if(num_nodes <= 2):
        print("num nodes must be at least 3")
        exit(1)
        
    sim = Simulator(num_nodes, 0.5 ,lowCPUfrac,txnDelay_meantime, max_sim_time, attacker1_hp, attacker2_hp)

    sim.run()

