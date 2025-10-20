# Virtual Nodes in Consistent Hashing

## How Virtual Nodes Work

In consistent hashing with virtual nodes (vnodes):

1. **Each physical node is assigned multiple positions** on the hash ring (e.g., 100-200 vnodes per physical node)
2. **Each vnode is placed at a different point** on the ring by hashing the node identifier plus a vnode index
3. **Keys are mapped to the ring** by hashing the key and finding the next vnode in clockwise order

## Finding Consecutive Nodes

To determine the next consecutive nodes for replication:

1. **Hash the key** to find its position on the ring
2. **Walk clockwise** from that position to find the next N vnodes
3. **Map vnodes back to physical nodes** - multiple vnodes may belong to the same physical node
4. **Select unique physical nodes** until you have N distinct nodes for replication

## Example

```
Ring: [N1-V1, N2-V1, N1-V2, N3-V1, N2-V2, N1-V3, N3-V2, ...]

If key hashes to position between N1-V1 and N2-V1:
- Primary replica: N2-V1 (maps to physical node N2)
- Replica 2: N1-V2 (maps to physical node N1)
- Replica 3: N3-V1 (maps to physical node N3)
```

## Benefits

- **Better load distribution**: Vnodes smooth out the distribution of keys across nodes
- **Easier scaling**: Adding/removing nodes only affects vnodes on the ring, not the entire key space
- **Reduced hotspots**: Multiple vnodes per physical node reduce the chance of uneven key distribution
