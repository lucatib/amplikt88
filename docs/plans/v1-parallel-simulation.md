# V1 parallel simulation plan

Requested experiment: connect the unused ECC83 section of V1 in parallel with the active section in simulation. Keep the production schematic/PCB and release tag 1.2 unchanged.

1. Export the current schematic as a baseline SPICE netlist and record provenance.
2. Add an isolated study script and tests for nonuniform-sample harmonic measurement and variant construction.
3. Compare baseline, direct parallel connection, and rebiased parallel operation. The scaled case halves R3/R4/R22 and scales R9/C6 to retain the approximate feedback fraction and time constant. Keep the output stage and deliberate inter-anode compensation unchanged. Document rail/loading shifts rather than silently matching them away.
4. Run DC, AC, voltage-injection loop estimates, equal-power transient THD and capacitive-load square waves. Check transient duration/timestep convergence at representative operating points. Report the voltage-injection validity assumption, model limitations and any unconverged metric.
5. Save reproducible inputs/results and a concise comparison, verify tests and document links, then commit/push as Codex on main.
