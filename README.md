# double-selfish-attack

Simulation of Double Selfish Mining Attack on a Blockchain network

Usage: python3 main.py [-n NODES] [-txm TXNDELAYMEAN] [-mst MAXSIMULATIONTIME] [-a1hp HPA1] [-a2hp HPA2]

NODES - Number of nodes  
TXNDELAYMEAN - Average inter arrival time between transactions  
MAXSIMULATIONTIME - Maximum duration of the simulation period.
HPA1 - Hashing fraction of attacker1  
HPA2 - Hashing fraction of attacker2  

## Output

All the tree information for each node will be created in the output folder. 
Red node represents the attacker1 mined block, Blue node represents the attacker2 mined block and green node represents the honest miners mined block.   
To change the avg block generation delay you have to change it in the line 75 of file node.py  

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
