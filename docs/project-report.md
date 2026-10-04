Performance Evaluation of FQ-CoDel with and without ECN using NeST
1. Introduction
Modern computer networks must handle increasing amounts of TCP traffic while maintaining good throughput, low delay, and low packet loss. When multiple TCP flows share a bottleneck link, packets can accumulate in router queues, resulting in increased queuing delay and packet loss.
Active Queue Management (AQM) mechanisms attempt to control this problem by managing packets before a queue becomes completely full. FQ-CoDel (FlowQueue Controlled Delay) is an AQM mechanism that combines flow-based queueing with the CoDel algorithm. It attempts to control queueing delay while maintaining fair sharing of the bottleneck among flows.
Explicit Congestion Notification (ECN) provides an alternative to indicating congestion. Instead of immediately dropping a packet when congestion is detected, a router can mark the packet with congestion information. An ECN-capable TCP sender can then react to the congestion signal by reducing its sending rate.
This project evaluates the behavior of FQ-CoDel with ECN disabled and enabled using the NeST network emulation framework on Linux. The experiments use TCP CUBIC as the congestion-control algorithm and compare the two configurations under different network conditions.
The study examines the effect of:
- Bottleneck bandwidth
- Propagation delay
- FQ-CoDel queue limit
- Number of concurrent CUBIC streams
- Mixed ECN-capable and non-ECN-capable traffic
The measurements include packet drops, ECN marks, queue length, TCP RTT, recorded sending rate, and per-flow throughput/fairness where applicable.
2. Problem Statement
When TCP traffic passes through a congested bottleneck, traditional congestion handling based primarily on packet drops can result in unnecessary packet loss and retransmissions.
ECN provides an alternative mechanism in which congestion can be communicated to an ECN-capable sender through packet marking rather than packet dropping.
The objective of this project is therefore to experimentally evaluate how FQ-CoDel behaves with ECN disabled and enabled, and to determine how the observed network metrics change under different controlled network conditions.
The project also investigates a mixed environment where ECN-capable and non-ECN-capable TCP flows share the same bottleneck.
3. Objectives
The main objectives of the project are:
1. To create a controlled bottleneck network using NeST.
2. To configure FQ-CoDel on the bottleneck link.
3. To use TCP CUBIC consistently for the experiments.
4. To compare FQ-CoDel with:
   - ECN disabled
   - ECN enabled
5. To study the effect of bottleneck bandwidth.
6. To study the effect of propagation delay.
7. To study the effect of FQ-CoDel queue size.
8. To study the effect of increasing traffic load using multiple concurrent CUBIC streams.
9. To evaluate mixed ECN-capable and non-ECN-capable traffic.
10. To collect and process network performance measurements.
11. To generate graphs for comparing the different configurations.
12. To identify experimentally observed advantages and differences associated with ECN marking versus packet dropping.
4. Technologies and Tools Used
Component	Technology
Operating System	Linux
Network Emulation	NeST v0.4.4
Programming Language	Python
Congestion Control	TCP CUBIC
Queue Discipline	FQ-CoDel
Database / Storage	CSV and JSON experiment results
Experiment Automation	Python scripts
Visualization	Python / Matplotlib
Network Configuration	Linux networking and NeST
Containerization	Not required for the final experiments


NeST was used to create network namespaces, nodes, routers, links, traffic flows, and measurements.
5. Background
5.1 TCP Congestion
TCP adjusts its sending rate according to the congestion state of the network.
When congestion occurs, the sender needs some indication that the network cannot currently handle the offered traffic rate.
A traditional mechanism is packet loss. When packets are dropped, TCP interprets the loss as a congestion signal and reduces its sending rate.
ECN provides another congestion signal by allowing congestion to be indicated through packet marking.
5.2 Explicit Congestion Notification
With ECN enabled, a congested queue can mark packets instead of dropping them.
The receiver communicates the congestion information back to the sender, allowing the sender to react to congestion.
Therefore, the two experimental configurations can be summarized as:
ECN OFF
Congestion
    ↓
FQ-CoDel detects congestion
    ↓
Packet is dropped
    ↓
TCP detects loss
    ↓
TCP reduces sending rate

ECN ON
Congestion
    ↓
FQ-CoDel detects congestion
    ↓
Packet is ECN-marked
    ↓
TCP receives congestion indication
    ↓
TCP reduces sending rate

The purpose of the experiment is not to assume that one mechanism is always superior, but to measure how the network behaves under the tested conditions.
6. FQ-CoDel
FQ-CoDel combines two concepts:
Flow Queueing
Traffic is divided into separate queues according to flows. This helps prevent one flow from dominating the queue.
Controlled Delay
CoDel monitors queueing delay and attempts to control excessive delay by dropping or marking packets when persistent queueing occurs.
The important FQ-CoDel parameters used in this project are:
Parameter	Meaning
limit	Maximum number of packets that can be queued
flows	Number of flow-queue buckets
target	Target queueing delay
interval	CoDel control interval


The experiments used:
flows   = 2
target  = 5 ms
interval = 100 ms

while the queue limit was varied in the queue-size experiment.
7. TCP CUBIC
TCP CUBIC was used as the congestion-control algorithm for all experiments.
Keeping CUBIC fixed is important because the project is intended to study the effect of ECN and network conditions, rather than comparing different TCP congestion-control algorithms.
Therefore:
Congestion Control = CUBIC

was kept constant throughout the experiments.
8. Experimental Methodology
8.1 Network Topology
The main topology used in the experiments is:
       Endpoint                 Endpoint
          h1                       h2
           |                       |
           |                       |
        +-----+                 +-----+
        | r1  |=================| r2  |
        +-----+   Bottleneck    +-----+
                  Link

The link between r1 and r2 acts as the bottleneck.
The endpoint links have a higher capacity than the bottleneck so that congestion is primarily created at the bottleneck.
The default baseline configuration was:
Bottleneck bandwidth : 10 Mbps
Bottleneck delay     : 10 ms
Endpoint bandwidth   : 100 Mbps
Endpoint delay       : 1 ms
Queue limit          : 100 packets
FQ-CoDel flows       : 2
Target               : 5 ms
Interval             : 100 ms
Traffic duration     : 20 seconds
TCP algorithm        : CUBIC

9. Experimental Configurations
The project was divided into the following experiments.
9.1 Baseline
The baseline compares:
ECN OFF
ECN ON

under fixed network conditions.
The baseline experiment was repeated three times for each condition.
9.2 Bandwidth Sweep
The bottleneck bandwidth was varied over:
5 Mbps
10 Mbps
20 Mbps

while other parameters remained fixed.
Both ECN OFF and ECN ON were tested at every bandwidth.
9.3 Delay Sweep
The bottleneck propagation delay was varied over:
5 ms
10 ms
20 ms

Both ECN configurations were tested.
9.4 Queue-Size Sweep
The FQ-CoDel queue limit was varied over:
50 packets
100 packets
200 packets

Both ECN configurations were tested.
9.5 Traffic-Load Sweep
Traffic load was represented by the number of simultaneous TCP CUBIC streams:
1 stream
2 streams
4 streams

Both ECN configurations were tested.
This allows the behavior of ECN to be studied as the number of competing TCP flows increases.
9.6 Mixed Traffic
A separate mixed-traffic experiment was performed with:
ECN-capable TCP flow
+
Non-ECN TCP flow

sharing the same bottleneck.
Separate sender nodes were used because the Linux TCP ECN configuration is applied at the node level.
The purpose of this experiment was to observe how ECN-capable and non-ECN-capable flows share the bottleneck.
10. Metrics Collected
The following measurements were collected.
Metric	Description
Packet drops	Number of packets dropped by FQ-CoDel
ECN marks	Number of packets marked for congestion
Maximum queue length	Maximum observed queue occupancy
TCP RTT	Average TCP round-trip time
Recorded sending rate	Average sending rate recorded by the experiment
Per-flow throughput	Throughput of individual mixed-traffic flows
Per-flow RTT	RTT observed by individual mixed-traffic flows
Fairness	Relative fairness between mixed flows


The project uses the measured sending rate as a recorded network metric. It should not be interpreted as an independently calculated aggregate throughput unless explicitly calculated from per-flow data.
11. Baseline Results
The baseline experiment was repeated three times for both configurations.
Baseline Packet Drops and ECN Marks
Condition	Drops – Run 1	Drops – Run 2	Drops – Run 3	ECN Marks – Run 1	ECN Marks – Run 2	ECN Marks – Run 3
ECN OFF	44	44	44	0	0	0
ECN ON	2	0	2	41	42	45


The baseline results show a clear difference in the way congestion was signaled.
With ECN disabled, the observed congestion signals were packet drops.
With ECN enabled, the experiments recorded substantially fewer packet drops while recording ECN marks.
The recorded sending rates remained around 9.6–9.7 Mbps in both configurations.
This indicates that under the baseline conditions, enabling ECN changed the congestion-signaling mechanism from predominantly dropping packets to predominantly marking packets.
12. Bandwidth Sweep Results
The bottleneck bandwidth was varied from 5 Mbps to 20 Mbps.
12.1 Numerical Results
Bandwidth	ECN	Drops	ECN Marks	Max Queue	Avg TCP RTT (ms)	Avg Recorded Sending Rate (Mbps)
5 Mbps	OFF	55	0	23	32.35	4.855
5 Mbps	ON	1	57	24	33.32	4.853
10 Mbps	OFF	43	0	36	29.76	9.663
10 Mbps	ON	0	42	33	29.84	9.623
20 Mbps	OFF	23	0	14	27.14	18.905
20 Mbps	ON	0	23	16	27.17	18.911


12.2 Observations
At 5 Mbps, ECN OFF recorded 55 packet drops, while ECN ON recorded only 1 drop and 57 ECN marks.
At 10 Mbps, ECN OFF recorded 43 drops, while ECN ON recorded no drops and 42 ECN marks.
At 20 Mbps, ECN OFF recorded 23 drops, while ECN ON recorded no drops and 23 ECN marks.
The recorded sending rates were close to the corresponding bottleneck capacities in both configurations.
The measured TCP RTT also remained relatively close between ECN OFF and ECN ON.
Therefore, in these measurements, enabling ECN substantially changed the congestion signal from packet drops to ECN marks without producing a large difference in the recorded sending rate.
13. Delay Sweep Results
The bottleneck delay was varied from 5 ms to 20 ms.
13.1 Numerical Results
Delay	ECN	Drops	ECN Marks	Max Queue	Avg TCP RTT (ms)	Avg Recorded Sending Rate (Mbps)
5 ms	OFF	73	0	18	20.95	9.741
5 ms	ON	0	76	21	21.22	9.753
10 ms	OFF	44	0	35	29.61	9.646
10 ms	ON	2	43	35	29.98	9.613
20 ms	OFF	38	0	44	49.71	9.648
20 ms	ON	2	29	43	49.51	9.688


13.2 Observations
Increasing the bottleneck delay resulted in a substantial increase in measured TCP RTT.
For example:
5 ms delay  → approximately 21 ms TCP RTT
10 ms delay → approximately 30 ms TCP RTT
20 ms delay → approximately 50 ms TCP RTT

This confirms that propagation delay is reflected in the overall TCP round-trip time.
For every tested delay, ECN ON recorded considerably fewer drops than ECN OFF.
At 5 ms:
ECN OFF → 73 drops
ECN ON  → 0 drops, 76 marks

At 20 ms:
ECN OFF → 38 drops
ECN ON  → 2 drops, 29 marks

The recorded sending rates were again relatively similar.
14. Queue-Size Sweep Results
The FQ-CoDel queue limit was varied over 50, 100, and 200 packets.
14.1 Numerical Results
Queue Limit	ECN	Drops	ECN Marks	Max Queue	Avg TCP RTT (ms)	Avg Recorded Sending Rate (Mbps)
50	OFF	43	0	36	29.59	9.610
50	ON	0	41	34	29.91	9.670
100	OFF	43	0	32	29.69	9.661
100	ON	0	42	36	29.80	9.635
200	OFF	44	0	36	29.50	9.671
200	ON	1	41	36	29.98	9.693


14.2 Observations
The queue limit itself did not produce a large change in the maximum observed queue length in these particular runs.
For ECN OFF, the number of drops remained around:
43–44 packets

for all three queue limits.
For ECN ON, the number of drops remained close to zero:
0, 0, and 1 packet

while ECN marks remained around 41–42.
The average TCP RTT also remained close to 30 ms for all tested queue limits.
Therefore, under the tested traffic and duration, changing the configured queue limit from 50 to 200 packets did not produce a large change in the measured TCP RTT or recorded sending rate.
15. Traffic-Load Sweep Results
Traffic load was varied by increasing the number of concurrent CUBIC TCP streams.
The tested values were:
1 stream
2 streams
4 streams

15.1 Numerical Results
CUBIC Streams	ECN	Drops	ECN Marks	Max Queue	Avg TCP RTT (ms)	Avg Recorded Sending Rate (Mbps)
1	OFF	43	0	34	29.79	9.646
1	ON	0	42	33	29.82	9.626
2	OFF	110	0	44	34.27	5.109
2	ON	1	116	47	33.43	4.855
4	OFF	306	0	69	41.87	2.878
4	ON	1	346	66	44.69	3.060


15.2 Observations
Increasing the number of CUBIC streams increased congestion at the bottleneck.
For ECN OFF:
1 stream → 43 drops
2 streams → 110 drops
4 streams → 306 drops

Thus, the measured packet drops increased substantially as more TCP flows competed for the same bottleneck.
With ECN ON:
1 stream → 0 drops, 42 marks
2 streams → 1 drop, 116 marks
4 streams → 1 drop, 346 marks

The number of ECN marks increased significantly as traffic load increased.
The maximum queue length also increased with the number of streams:
1 stream → approximately 33–34 packets
2 streams → approximately 44–47 packets
4 streams → approximately 66–69 packets

The measured TCP RTT increased as the number of competing streams increased.
For example, under ECN OFF:
1 stream → 29.79 ms
2 streams → 34.27 ms
4 streams → 41.87 ms

This indicates increased congestion and queueing as traffic load increased.
16. Mixed ECN / Non-ECN Traffic
The mixed-traffic experiment used two simultaneous flows sharing the same bottleneck:
Flow 1 → ECN capable
Flow 2 → Non-ECN capable

Separate sender nodes were used so that the ECN configuration could be controlled independently for the two flows.
16.1 Per-Flow Throughput
The measured average sending rates were approximately:
Flow	Average Recorded Rate
ECN flow	≈ 5.6 Mbps
Non-ECN flow	≈ 4.6 Mbps


The values indicate that both flows obtained a substantial portion of the available bottleneck capacity.
The exact per-flow measurements should be interpreted as measurements from the experiment rather than as a universal fairness result.
16.2 Per-Flow RTT
The mixed-traffic experiment recorded approximately:
Non-ECN flow RTT ≈ 34.90 ms

The per-flow measurements were used to compare the behavior of the two flows.
16.3 Fairness
The measured Jain fairness value was approximately:
Jain fairness = 0.9911

The Jain fairness index is calculated as:
\[
J = \frac{(\sum x_i)^2}{n\sum x_i^2}
\]
where:
- \(x_i\) is the throughput of flow \(i\)
- \(n\) is the number of flows
A value close to 1 indicates that the measured throughputs are close to one another.
The observed value of approximately 0.9911 therefore indicates that the two flows had very similar measured throughput in this particular mixed-traffic experiment.
This result should not be generalized to all ECN/non-ECN combinations because only the tested mixed configuration was evaluated.
17. Summary of Experimental Results
The main measured results can be summarized as follows.
Experiment	Main Observation
Baseline	ECN ON produced marks with substantially fewer drops
Bandwidth	ECN ON consistently reduced observed drops and produced ECN marks
Delay	Increasing delay increased TCP RTT
Queue Size	Queue limit had relatively small effect on measured RTT and recorded sending rate in these runs
Traffic Load	More CUBIC streams increased congestion, drops, queue length and RTT
Mixed Traffic	ECN and non-ECN flows shared the bottleneck with high measured fairness in the tested scenario


18. Overall Observations
Across the experiments, a consistent difference was observed between the two congestion-signaling mechanisms.
With ECN disabled, congestion was primarily reflected through packet drops.
With ECN enabled, FQ-CoDel was able to use ECN marking for ECN-capable traffic, resulting in substantially fewer observed packet drops in the tested configurations.
For example, the baseline measurements showed:
ECN OFF → 44 drops
ECN ON  → approximately 0–2 drops

while ECN ON simultaneously recorded approximately 41–45 ECN marks.
A similar pattern appeared in the bandwidth, delay, queue-size, and traffic-load experiments.
However, the recorded sending rates were generally similar between ECN OFF and ECN ON for the single-flow experiments. Therefore, the primary difference observed in this project was the way congestion was signaled, rather than a large increase in the measured sending rate.
19. Effect of Increasing Traffic Load
The traffic-load experiment produced one of the clearest trends.
As the number of CUBIC streams increased:
1 → 2 → 4 streams

the bottleneck became increasingly congested.
Under ECN OFF:
43 → 110 → 306 drops

were observed.
Under ECN ON:
42 → 116 → 346 ECN marks

were observed, while packet drops remained close to zero.
The maximum queue length also increased considerably.
This demonstrates that increasing the number of simultaneous TCP flows creates greater contention at the bottleneck.
20. Realistic Network Scenario Interpretation
The experiments were designed as controlled parameter studies rather than exact replicas of individual commercial networks.
However, the tested configurations can be interpreted in terms of representative network conditions.
Lower-bandwidth access link
The 5 Mbps bottleneck represents a constrained link where congestion can develop relatively easily when the sender attempts to transmit near the available capacity.
Moderate-bandwidth network
The 10 Mbps configuration represents the baseline controlled bottleneck used throughout the majority of the experiments.
Higher-bandwidth bottleneck
The 20 Mbps configuration provides a less constrained bottleneck and allows the behavior of ECN to be observed under a higher-capacity link.
Higher-latency path
The 20 ms bottleneck delay represents a longer-delay network path compared with the 5 ms and 10 ms configurations.
Such parameter values can be used to represent different classes of access or wide-area conditions, but the experiments should not be described as actual measurements of a specific LAN, WAN, ISP, or real-world network.
The project emulates representative network characteristics rather than reproducing a particular physical network.
21. Why Two Routers Were Used
The two-router topology was used to create a clear bottleneck link:
h1 → r1 → r2 → h2
          ↑
       bottleneck

The r1-r2 link was configured with the controlled bandwidth and delay.
This makes it possible to isolate the effect of the bottleneck while keeping the endpoint links at a higher capacity.
The additional plots generated by NeST are not simply because the topology contains two routers.
NeST collects several categories of measurements such as:
- queue/qdisc statistics
- TCP statistics
- ping/RTT statistics
- traffic statistics
Additionally, the traffic-load experiment contains multiple CUBIC streams, which can result in additional per-flow measurements and plots.
22. Implementation Architecture
The project was implemented as modular Python code.
The major components are:
src/
├── config.py
├── qdisc.py
├── traffic.py
├── metrics.py
├── experiment.py
├── results.py
└── topologies/
    └── bottleneck.py

The experiment execution scripts are located in:
run/
├── run_one.py
└── run_sweep.py

The configuration files are stored under:
configs/
├── baseline.json
├── bandwidth.json
├── delay.json
├── queue_size.json
└── traffic_load.json

The generated results are organized into:
results/
├── raw/
└── processed/

The graphs are stored in:
analysis/
└── plots/

23. Experiment Automation
The experiments were automated using configuration files.
Instead of manually changing source code for every experiment, a sweep configuration specifies the parameter and its values.
For example, the bandwidth experiment uses:
5 Mbps
10 Mbps
20 Mbps

The experiment runner automatically executes:
5 Mbps  + ECN OFF
5 Mbps  + ECN ON

10 Mbps + ECN OFF
10 Mbps + ECN ON

20 Mbps + ECN OFF
20 Mbps + ECN ON

The same approach was used for delay, queue size, and traffic load.
This reduces manual configuration errors and ensures that the same experimental procedure is applied across the parameter values.
24. Result Organization
The raw NeST results are stored separately from the processed CSV results.
The processed results contain parameters such as:
experiment group
parameter
parameter value
condition
packet statistics
queue statistics
TCP RTT
sending rate

This makes the results suitable for subsequent plotting and analysis.
The project therefore follows the general workflow:
Configuration
      ↓
Network Creation
      ↓
FQ-CoDel Configuration
      ↓
TCP CUBIC Traffic
      ↓
NeST Experiment
      ↓
Raw Measurements
      ↓
Metric Extraction
      ↓
CSV Results
      ↓
Graphs
      ↓
Analysis

25. Limitations
The results have several important limitations.
25.1 Number of Repetitions
The baseline experiment was repeated three times for each condition.
However, the:
- bandwidth sweep
- delay sweep
- queue-size sweep
- traffic-load sweep
shown above use one run per condition.
Therefore, the sweep results should be interpreted as measured observations for the tested runs rather than statistically generalized results.
A larger number of repetitions would be required for stronger statistical conclusions.
25.2 Controlled Emulation
The experiments were performed using NeST in a controlled Linux environment.
Therefore, the results represent the behavior of the configured emulated network and should not be interpreted as direct measurements of a real production network.
25.3 Limited Parameter Range
Only a limited set of values was tested.
For example:
Bandwidth: 5, 10, 20 Mbps
Delay:     5, 10, 20 ms
Queue:     50, 100, 200 packets
Streams:   1, 2, 4

Other values may produce different results.
25.4 CUBIC Only
All experiments use TCP CUBIC.
Therefore, the conclusions cannot automatically be extended to other congestion-control algorithms such as Reno, BBR, or other TCP variants.
25.5 Limited Mixed-Traffic Study
The mixed experiment evaluates a representative combination of:
1 ECN flow
+
1 non-ECN flow

It does not exhaustively evaluate every possible ratio of ECN-capable to non-ECN-capable flows.
25.6 Recorded Sending Rate
The reported sending-rate metric is the rate recorded by the experiment.
It should not be described as an independently calculated aggregate throughput unless such a calculation is explicitly performed from per-flow measurements.
For the traffic-load experiment, the reduction in recorded sending rate with increasing numbers of streams therefore needs to be interpreted according to the metric collected by the experiment.
25.7 No Statistical Significance Testing
The project does not currently perform statistical hypothesis testing, confidence-interval calculation, or significance testing.
Therefore, differences between configurations should be presented as observed experimental differences, rather than statistically proven differences.
26. Scope of the Project
The project focuses on experimentally evaluating:
FQ-CoDel
      +
ECN OFF vs ECN ON
      +
TCP CUBIC
      +
Controlled network conditions

The project does not attempt to:
- implement FQ-CoDel from scratch
- implement TCP CUBIC from scratch
- implement ECN from scratch
- reproduce a particular ISP network
- compare all TCP congestion-control algorithms
- perform a large-scale statistical study
Instead, Linux and NeST provide the actual networking mechanisms, while the project focuses on controlled experimentation, measurement, comparison, and analysis.
27. Conclusion
This project experimentally evaluated FQ-CoDel with and without ECN using the NeST network emulation framework.
A controlled bottleneck topology was created using two routers, with FQ-CoDel configured on the bottleneck link. TCP CUBIC was used consistently across the experiments.
The study evaluated:
- bottleneck bandwidth
- propagation delay
- queue size
- traffic load
- mixed ECN/non-ECN traffic
The measured results showed a consistent distinction between ECN-disabled and ECN-enabled operation.
With ECN disabled, congestion was primarily represented by packet drops. With ECN enabled, congestion was predominantly represented by ECN marks, and the number of observed packet drops was substantially lower in the tested configurations.
The bandwidth experiments showed this behavior across 5, 10, and 20 Mbps bottlenecks.
The delay experiments showed that increasing propagation delay increased TCP RTT.
The queue-size experiments showed relatively small changes in RTT and recorded sending rate for the tested queue limits.
The traffic-load experiment showed that increasing the number of concurrent CUBIC streams increased congestion, queue occupancy, RTT, and packet drops when ECN was disabled. With ECN enabled, the congestion signal appeared primarily as ECN marks while packet drops remained close to zero in the tested runs.
The mixed-traffic experiment showed that ECN-capable and non-ECN-capable flows were able to share the bottleneck with a measured Jain fairness value of approximately 0.9911 for the tested configuration.
Overall, the experiments demonstrate that ECN changes the congestion-signaling behavior of FQ-CoDel from predominantly packet dropping toward packet marking for ECN-capable traffic. The measured results also show that network conditions such as bandwidth, delay, queue size, and traffic load influence the observed behavior.
These conclusions are limited to the configurations and runs performed in this project and should not be generalized beyond the tested scenarios without additional experimentation.
28. Future Scope
Several extensions can be performed in future work.
28.1 More Repetitions
Each sweep condition can be repeated multiple times to obtain:
- mean values
- standard deviation
- confidence intervals
- more statistically reliable comparisons
28.2 Larger Parameter Ranges
More bandwidth, delay, queue-size, and traffic-load values can be tested to obtain more detailed performance curves.
28.3 More Mixed-Traffic Ratios
The mixed experiment can be extended to combinations such as:
1 ECN + 1 non-ECN
2 ECN + 1 non-ECN
1 ECN + 2 non-ECN
2 ECN + 2 non-ECN

This would allow the interaction between ECN-capable and non-ECN-capable flows to be studied in greater detail.
28.4 Other Congestion-Control Algorithms
Future experiments could compare CUBIC with other TCP congestion-control algorithms.
However, this would constitute a separate experimental dimension and was intentionally kept outside the current project scope.
28.5 Additional Network Conditions
The experiment framework can be extended to include additional network conditions such as:
- higher latency
- lower bandwidth
- asymmetric links
- different endpoint delays
- larger numbers of competing flows
28.6 Statistical Analysis
The collected CSV results can be extended with statistical analysis to determine whether observed differences are consistent across repeated runs.
29. References
1. NeST – Network Stack Tester, official project documentation and source repository.
2. RFC 8290 – The Flow Queue CoDel Packet Scheduler, Internet Engineering Task Force.
3. RFC 3168 – The Addition of Explicit Congestion Notification (ECN) to IP, Internet Engineering Task Force.
4. Linux Traffic Control (tc) documentation, Linux networking documentation.
5. Linux TCP documentation, Linux kernel networking documentation.
6. TCP CUBIC, RFC 8312, Internet Engineering Task Force.
30. Project Directory Structure
The final project is organized approximately as follows:
OSNT_Project/
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── qdisc.py
│   ├── traffic.py
│   ├── metrics.py
│   ├── experiment.py
│   └── topologies/
│       ├── __init__.py
│       └── bottleneck.py
│
├── configs/
│   ├── baseline.json
│   ├── bandwidth.json
│   ├── delay.json
│   ├── queue_size.json
│   └── traffic_load.json
│
├── run/
│   ├── __init__.py
│   ├── run_one.py
│   └── run_sweep.py
│
├── results/
│   ├── raw/
│   │   ├── baseline/
│   │   ├── bandwidth/
│   │   ├── delay/
│   │   ├── queue_size/
│   │   └── traffic_load/
│   │
│   └── processed/
│       ├── baseline.csv
│       ├── bandwidth.csv
│       ├── delay.csv
│       ├── queue_size.csv
│       └── traffic_load.csv
│
├── analysis/
│   ├── plots/
│   └── plot_results.py
│
└── docs/
    └── project-report.md

31. Final Experimental Summary
The complete experimental workflow can be summarized as:
                  FQ-CoDel Bottleneck
                         │
              ┌──────────┴──────────┐
              │                     │
           ECN OFF                ECN ON
              │                     │
        Packet Drops          ECN Marking
              │                     │
              └──────────┬──────────┘
                         │
                   TCP CUBIC
                         │
              Performance Metrics
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Bandwidth          Delay         Queue Size
        │                │                │
        └────────────────┼────────────────┘
                         │
                  Traffic Load
                         │
                  Mixed Traffic
                         │
              Results + Graphs
                         │
                  Observations

The project therefore provides a controlled experimental evaluation of how FQ-CoDel behaves with and without ECN under different network conditions, while also examining the interaction between ECN-capable and non-ECN-capable TCP traffic.