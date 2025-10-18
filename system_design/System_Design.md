# System Design

## Learning Goals
- Design a system that handles high traffic with real-time updates.  
- Identify bottlenecks, scaling limits, and security boundaries.  
- Estimate costs for peak and moderate traffic.

---

## Situation

An investor asks you to take $1,000,000 (one million dollars) and deploy a website that hosts realtime stats for all events in the next Winter Olympics including leaderboards by different categories.  

Some quick research tells you you can expect about **360,000,000 requests per day** during **17 days** of the Olympic games.

---

## Deliverables

1. **System Design**  
   - Draw a diagram showing all components and how requests flow.  
   - Explain how your system handles traffic and scales.

2. **Bottlenecks & Scaling**  
   - Identify potential bottlenecks (e.g., real-time processing, database writes).  
   - Explain how your design addresses scaling constraints.

3. **Security**  
   - Identify security boundaries (e.g., admin endpoints, APIs).  
   - Explain how security is maintained (encryption, authentication, firewalls).

4. **Cost Estimation**  
   - Calculate costs for peak load (17 days) and half load (17 days).  
   - Include a table of technologies you'll use and associated costs, showing your calculations.
