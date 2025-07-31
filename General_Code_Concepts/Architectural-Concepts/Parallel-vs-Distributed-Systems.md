# Parallel vs. Distributed Systems
## **Parallel computing** 
involves multiple processors or cores working together on the same machine to solve a single problem simultaneously. The processors typically share memory and resources, allowing them to communicate quickly through shared memory spaces. Think of it like having multiple workers in the same room collaborating on a project - they can easily share materials and coordinate their efforts.

## **Distributed computing** 
spreads the computational work across multiple separate machines connected by a network. Each machine has its own memory, storage, and processing power, and they communicate by passing messages over the network. This is more like having workers in different buildings or cities collaborating on a project - they need to send messages back and forth to coordinate.

### Key differences:

**Memory architecture**: Parallel systems usually share memory, while distributed systems have separate memory spaces for each node.

**Communication speed**: Parallel systems have fast, low-latency communication through shared memory. Distributed systems rely on network communication, which is slower and less reliable.

**Fault tolerance**: Distributed systems can continue operating if one machine fails. Parallel systems typically fail entirely if any component fails.

**Scalability**: Distributed systems can theoretically scale to thousands of machines across the globe. Parallel systems are limited by the number of processors you can fit in one machine.

**Complexity**: Distributed systems must handle network partitions, node failures, and data consistency across machines, making them more complex to design and debug.

Many modern systems combine both approaches - for example, a distributed system where each node runs parallel computations internally.
