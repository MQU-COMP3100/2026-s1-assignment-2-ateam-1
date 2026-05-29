# COMP3100/6105 Assignment 2  
# Adaptive Load-Aware DRF Hybrid Scheduler

## Requirements
- Python 3
- Linux environment / GitHub Codespaces

---

## Project Overview
This project implements a custom scheduling algorithm for the ds-sim distributed systems simulator.

The implemented scheduling algorithm is:

**Adaptive Load-Aware DRF Hybrid Scheduler**

The scheduler combines:
- DRF-inspired resource balancing
- Runtime-aware scheduling
- Load-aware server selection
- Best-fit resource allocation
- Queue-aware adaptive scheduling

The algorithm is designed to improve:
- Turnaround time
- Resource utilisation
- Scheduling efficiency

while maintaining reasonable execution cost.

---

## Repository Structure

- `client.py` → Main scheduling algorithm implementation
- `ds_test.py` → Official testing and benchmarking script
- `TestConfigs/` → Benchmark configuration files
- `PrelimConfigs/` → Preliminary correctness testing configurations
- `configs/sample-configs/` → Sample simulator configurations
- `results/` → Generated benchmark results

---

# Running the Project

## 1. Open the Repository
Open the GitHub repository using GitHub Codespaces.

---

## 2. Enable Executable Permissions
After opening the Codespace for the first time, run:

```bash
chmod +x ds-*
```

---

## 3. Run Full Benchmark Testing
Use the following command to run the scheduler against the benchmark configurations:

```bash
python3 ./ds_test.py "python3 client.py" -n -p 50000 -c TestConfigs
```

This compares the implemented scheduler against the baseline algorithms:
- ATL
- FF
- BF
- FC
- FAFC

---

## 4. Run a Specific Test Configuration

Example:

```bash
python3 ./ds_test.py "python3 client.py" -n -p 50000 -c TestConfigs/config040-short-high.xml
```

---

## Output
The testing script prints:
- Average turnaround time
- Resource utilisation
- Total rental cost
- Performance comparisons against baseline algorithms

---

## Notes
- The scheduler dynamically adapts scheduling decisions based on:
  - Job runtime
  - Queue load
  - Resource utilisation
  - Server state
  - Resource waste minimisation
  - Available CPU, memory, and disk resources
  - Current system workload conditions
  - Best-fit server selection principles
  - DRF-inspired resource balancing strategies

- The scheduler prioritises efficient resource allocation while attempting to maintain low turnaround times and balanced server utilisation.

- Scheduling decisions may vary depending on the workload characteristics and resource availability of the simulator environment.
