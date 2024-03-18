# des-p2p-crypto-net

Discrete-event simulator for a P2P cryptocurrency network

Usage: python3 main.py [--num_nodes NODES] [--slowfrac SLOW] [--lowCPUfrac LOWCPU] [--txnDelay_meantime TXNDELAYMEAN] [--max_sim_time MAXSIMULATIONTIME]

NODES - Number of nodes  
SLOW - Fraction of nodes which are slow  
LOWCPU - Fraction of nodes which are low CPU  
TXNDELAYMEAN - Average inter arrival time between transactions  
MAXSIMULATIONTIME - Maximum duration of the simulation period.

## Output

All the tree information for each node will be created in the output folder.  
To change the avg block generation delay you have to change it in the line 71 of file node.py  

## Dependencies

This project depends on the following Python libraries:

- `numpy` (version 1.24.2)
- `networkx` (version 3.2.1)
- `matplotlib` (version 3.7.1)

You can install these dependencies using pip:

```bash
pip3 install numpy==1.24.2 networkx==3.2.1 matplotlib==3.7.1


```

## References

- create_chain function in node.py (ref: https://github.com/dufferzafar/crypto-simulation/blob/master/simulation.py)
- network generation in simulation.py (ref: chatgpt)
