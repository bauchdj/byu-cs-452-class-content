# Reliable Systems

## Learning Goals
- Learn how to keep a system running when nodes fail.  
- Understand trade offs between consistency and availability.

## Situation

Your system is horizontally scaled with nodes arranged in a **ring using consistent hashing**.  
Load is managed with horizontal scaling, consistent hashing and a network load balancer.  

**Problem:** Roughly once every three months, a server may fail, causing downtime for reads and writes.  
**Goal:** Design a system that remains fully available, allowing reads and writes even when a single node goes down.

---

## Deliverables

### System Design

Design a system that allows a node to temporarily go down while still giving read and write access to your data with zero downtime. Draw pictures and explain how it works.

### Considerations

To help focus your design, consider:
- How might you replicate data across multiple nodes?  
- How will clients continue to access data if a node fails?  
- What consistency and availability trade offs should you consider?  
- How might your design affect read/write latency under node failure?  
- How should the system handle nodes rejoining after a failure?  
- How does your design scale as the system grows in nodes or data volume?
