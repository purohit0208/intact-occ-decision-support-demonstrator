# Pre-Arrival OCC Decision Support for Aircraft Turnaround Coordination: A Human-in-the-Loop Architecture and Scenario-Based Evaluation

## Abstract

Aircraft turnaround coordination depends on maintenance, catering, passenger-assistance, gate, and bottleneck information that may become available before arrival but is often handled through fragmented workflows. This paper presents a human-in-the-loop Operations Control Center (OCC) decision-support architecture for pre-arrival aircraft turnaround coordination. The architecture integrates component-aware maintenance risk indicators, service-area inventory readiness, process-class bottleneck forecasting, passenger-assistance readiness logic, and a transparent rule-based fusion layer that converts heterogeneous signals into readiness scores, alert levels, and operator-facing action queues. The evaluation is deliberately framed as controlled synthetic scenario analysis rather than airline deployment validation. Existing module-level holdout results are combined with a deterministic scenario sweep of 1000 synthetic inbound cases across six operational regimes, monotonicity and sanity checks, and ablation and baseline comparisons. The scenario sweep produced mean readiness 47.396, median readiness 50.65, 370 Critical cases, 284 Priority cases, and 188 Routine cases. Ablations show that removing maintenance influence increased mean readiness by 13.65 points, while removing bottleneck influence increased mean readiness by 9.99 points, indicating that the fusion layer materially changes prioritization under controlled stress conditions. Two maintenance-related monotonicity checks did not strictly pass because small local readiness increases occurred at low malfunction levels before urgency thresholds changed; these failures are treated as limitations of the current model-fusion interaction rather than hidden. The work contributes a reproducible OCC decision-support architecture and scenario-evaluation package, while explicitly preserving the limitations that no airline operational data, OCC user study, deployment, certification, or measured operational savings are claimed.

**Keywords:** aircraft turnaround; Operations Control Center; decision support; scenario-based evaluation; predictive maintenance; inventory readiness; bottleneck forecasting; human-in-the-loop

## 1. Introduction

Aircraft turnaround operations are managed under tight time constraints and require coordination across maintenance, catering, cleaning, boarding, refueling, passenger assistance, gate management, and airline operations control. Information relevant to these processes can be available before arrival, but it is often distributed across separate operational or analytical views. The practical problem is therefore not only whether individual prediction models can be trained, but how heterogeneous pre-arrival signals can be converted into a form that supports OCC coordination before the aircraft reaches the stand.

This study is framed as an air transport operations contribution. The focus is pre-arrival decision support for turnaround coordination, not a generic intelligent-systems contribution. The architecture remains human-in-the-loop: it supports operator review through readiness scores, alert levels, provenance labels, and action queues, but it does not automate dispatch or claim certified operational control.

The work uses synthetic but operationally grounded data because no real airline, airport, or station-operation dataset is available in the current project package. That boundary is central to the paper. The evaluation therefore asks whether the architecture behaves coherently and differentiates operational regimes under controlled scenarios. It does not ask whether the system is validated for airline deployment.

## 2. Related Work

### 2.1 OCC Decision Support and Disruption Management

Airline Operations Control Centers coordinate time-critical decisions across aircraft, crews, gates, passengers, and downstream rotations. Classical OCC and disruption-management literature, including work by Clarke, Clausen, Hassan, and Su, shows that these decisions combine schedule recovery, resource coordination, and human judgment rather than a single optimization objective. Naturalistic and decision-support studies by Fogaca and Vink further motivate systems that preserve operator review instead of replacing OCC staff with automated control.

### 2.2 Turnaround Coordination and Ground Handling

Aircraft turnaround research treats the stand-side process as a tightly coupled operational system. Work on turnaround management, ground-handling automation, apron-resource planning, and delay propagation, including studies by Makhloof, Conde, Gok, Guimarans, Evler, and Wu, shows that local process delays can affect broader airline and airport performance. This paper builds on that perspective by focusing on pre-arrival coordination signals that can change preparation before the aircraft reaches the stand.

### 2.3 Aviation ML for Delay and Resource Prediction

Aviation machine-learning studies have addressed arrival-time prediction, delay classification, resource planning, and ground-operation forecasting. The cited studies by Basturk, Zoutendijk, Sahadevan, Okwir, Kicinger, and Wandelt support the view that predictive analytics can inform aviation operations. However, a collection of separate predictive tasks does not automatically create an OCC workflow. The contribution here is therefore not a new prediction algorithm; it is the operational integration of heterogeneous predictive and rule-based signals into one pre-arrival advisory process.

### 2.4 Predictive Maintenance, Service Readiness, and Assistance

Predictive-maintenance studies by Dangut, Lee and Mitici, Zeng, Hakami, and Kabashkin motivate maintenance-risk indicators for aviation decision support. Adjacent work on food-service and demand forecasting, including Malefors and Rodrigues, is relevant to service-readiness reasoning, but it should not be interpreted as evidence for item-wise airline trolley-demand prediction in this paper. Passenger-assistance and accessibility work by Gotti and Lee motivates explicit assistance-readiness handling, while the implemented system treats assistance as rule-based readiness support rather than localization machine learning.

### 2.5 Human-in-the-Loop and Synthetic Scenario Evaluation

Human-in-the-loop AI and explainability work, including Mosqueira-Rey, Vaccaro, and Xie, supports transparent advisory systems where model outputs remain reviewable by human operators. Synthetic-data and scenario-evaluation studies by Ardebili, de Frutos, and Stefani provide a methodological basis for controlled evaluation when operational data are not available, but they do not remove the need for future airline data and user studies. This paper therefore uses synthetic scenarios to evaluate architecture behavior, not to claim field validity.

Across these streams, the open gap is the connection between module-level analytics and pre-arrival OCC coordination. Maintenance, inventory, bottleneck, and assistance-readiness signals are not treated as separate dashboards. They are fused into one operator-facing advisory workflow, with explicit labels distinguishing trained inference, rule-based readiness logic, and synthetic scenario simulation.

## 3. Contributions

This paper makes four bounded contributions:

- A pre-arrival OCC decision-support architecture for aircraft turnaround coordination.
- A modular integration of maintenance risk, inventory readiness, bottleneck forecasting, and passenger-assistance readiness signals.
- A transparent fusion/action layer that converts heterogeneous signals into readiness scores, alerts, and action queues for operator review.
- A scenario-based evaluation package with seeded cases, a 1000-case synthetic sweep, monotonic sanity checks, and ablation/baseline comparisons.

The contribution is architectural and operational. It is not a claim of a new AI algorithm, airline deployment, or field-validated performance.

## 4. System Architecture

The architecture has four layers. The input layer represents pre-arrival aircraft and turnaround state, including passenger load, arrival delay, gate congestion, malfunction count and severity, trolley availability, inventory shortage indicators, assistance requests, weather disturbance, and refueling requirement. The analytics layer contains trained local modules for maintenance, inventory, and bottleneck prediction. Passenger assistance is treated as rule-based readiness support, not localization machine learning. The fusion layer combines module outputs and scenario state into readiness, criticality, alerts, and action queues. The presentation layer exposes the result in an operator-facing OCC interface.

[[FIGURE:outputs/figures/figure_1_occ_architecture.png|Figure 1. Integrated OCC decision-support architecture for pre-arrival turnaround coordination.]]

[[FIGURE:outputs/figures/figure_2_module_to_fusion_workflow.png|Figure 2. Module-to-fusion workflow for pre-arrival OCC decision support.]]

## 5. Module Design and Evidence Boundary

The maintenance module is component-aware in its features and explanation logic, but the OCC interface summarizes the result at flight-scenario level. It should not be described as a certified component-wise aircraft-health dashboard. The inventory module supports service-area, trolley-level, and flight-level inventory-risk reasoning; it is not item-wise product demand prediction. The bottleneck module predicts process-class bottleneck probabilities across Maintenance, Catering, Cleaning, Boarding, and Refueling. Passenger assistance is rule-based readiness support.

[[TABLE:outputs/tables/manuscript_table_1_module_summary.csv|Table 1. Module-level model summary and evidence boundary.]]

## 6. Scenario-Sweep Design

The evaluation extends the five seeded demonstration cases with a deterministic scenario sweep. The sweep contains 1000 synthetic inbound cases generated under six regimes: low-risk routine, maintenance-heavy, inventory-heavy, congestion/delay-heavy, assistance-readiness, and composite multi-risk. A fixed random seed, 20260608, is used so that the inputs, outputs, and figures can be reproduced. Cases are assigned across the six regimes and then evaluated through the existing trained model inference and OCC fusion functions.

The generator varies arrival delay, gate congestion, malfunction count, malfunction severity, trolley availability, inventory shortage, passenger load, assistance readiness, weather disturbance, and refueling requirement. Low-risk routine cases use low delay, low congestion, few or no malfunctions, adequate trolley availability, and confirmed or absent assistance requests. Maintenance-heavy cases stress malfunction count and severity. Inventory-heavy cases stress trolley availability and shortage indicators. Congestion/delay-heavy cases stress arrival delay and gate congestion. Assistance-readiness cases vary assistance request status and confirmation. Composite multi-risk cases combine multiple stressors.

For each generated inbound case, the evaluation records readiness score, alert level, dominant bottleneck, module-level risks, action-queue size, priority-action counts, and top action categories. The sweep is a controlled architecture-behavior evaluation. It does not replace the seeded demonstration cases and does not create observational airline evidence.

[[TABLE:outputs/tables/manuscript_table_2_scenario_sweep_summary.csv|Table 2. Overall scenario-sweep summary.]]

[[FIGURE:outputs/figures/scenario_sweep_readiness_distribution.png|Figure 3. Readiness distribution across the controlled synthetic scenario sweep.]]

[[FIGURE:outputs/figures/scenario_sweep_alert_distribution.png|Figure 4. Alert-level distribution across the controlled synthetic scenario sweep.]]

## 7. Regime-Level Results

The generated regimes produced differentiated system behavior. The low-risk routine regime had mean readiness 82.34, while the maintenance-heavy regime had mean readiness 26.17, the inventory-heavy regime had mean readiness 54.62, and the composite multi-risk regime had mean readiness 8.77. These values should be interpreted as designed scenario-response behavior, not as observed airline probabilities.

[[TABLE:outputs/tables/manuscript_table_3_regime_summary.csv|Table 3. Regime-level summary of synthetic scenario responses.]]

[[FIGURE:outputs/figures/regime_readiness_boxplot.png|Figure 5. Readiness by synthetic operational regime.]]

## 8. Monotonicity and Sanity Checks

The monotonic checks test whether the system behaves coherently when one stressor changes while other inputs are held constant. Six of eight checks passed. Inventory shortage, trolley availability, arrival delay, gate congestion, assistance readiness, and composite-versus-low-risk checks behaved in the expected direction. The malfunction-severity and malfunction-count checks did not strictly pass because readiness increased slightly at low malfunction values before the maintenance urgency threshold changed. In both cases, maintenance failure probability still increased with the stressor, but the fused readiness score was not perfectly monotonic.

These failures are not positive evidence. They show that the current model-fusion interaction is not strictly monotonic under every stressor sweep and would need additional monotonic post-model guards, calibrated fusion constraints, or expert-reviewed thresholds before any deployment-oriented study. The present paper reports the failure as a limitation rather than converting the system into unsupported field evidence.

[[TABLE:outputs/tables/manuscript_table_4_monotonicity_summary.csv|Table 4. Monotonicity and sanity-check summary.]]

[[FIGURE:outputs/figures/sensitivity_curves.png|Figure 6. Sensitivity curves for one-factor system-behavior checks.]]

## 9. Ablation and Baseline Results

The ablation study compares the full fusion system against configurations in which maintenance, inventory, bottleneck, or assistance influence is neutralized. The objective is not to prove real operational superiority. The objective is to show whether each signal family changes the behavior of the integrated action logic under controlled synthetic scenarios.

The full configuration uses maintenance, inventory, bottleneck, assistance, and fusion logic together. The no-maintenance ablation neutralizes maintenance influence in the fusion layer. The no-inventory ablation neutralizes inventory-shortage influence. The no-bottleneck ablation replaces process-class bottleneck evidence with a neutral bottleneck state. The no-assistance ablation removes assistance-readiness influence. Each configuration is evaluated on the same generated scenario inputs so differences reflect fusion behavior rather than different scenario samples.

[[TABLE:outputs/tables/manuscript_table_5_ablation_summary.csv|Table 5. Ablation summary relative to the full integrated system.]]

[[FIGURE:outputs/figures/ablation_readiness_delta.png|Figure 7. Mean readiness change when signal families are removed from fusion.]]

The baseline comparison contrasts the full system with static delay/gate, maintenance-only, inventory-only, and bottleneck-only baselines. The static delay/gate baseline uses only arrival delay and gate congestion. The single-signal baselines expose one module family at a time. The full system produces more cross-domain action differentiation than the single-signal baselines, but this should be read as scenario-behavior differentiation rather than field performance superiority.

[[TABLE:outputs/tables/manuscript_table_6_baseline_comparison.csv|Table 6. Baseline comparison for controlled synthetic behavior differentiation.]]

## 10. Operator Interface

The interface remains a supporting artifact, not the main evidence source. It shows how readiness, alerts, provenance, bottleneck state, and action queues can be presented for operator review. Only one representative screenshot is retained in the main paper to avoid making the manuscript look like a software demo report.

[[FIGURE:outputs/figures/figure_6_representative_gui_dashboard.png|Figure 8. Representative OCC dashboard view showing fused pre-arrival summaries.]]

## 11. Discussion

The results support the architectural claim that heterogeneous pre-arrival signals can be fused into differentiated OCC advisory outputs. Maintenance-heavy, inventory-heavy, congestion-heavy, assistance-readiness, routine, and composite scenarios lead to distinct readiness states, alert distributions, bottleneck profiles, and action categories. This is the appropriate contribution level for the current evidence base.

For air transport management readers, the practical implication is not that the demonstrator is ready for airline use. The implication is that pre-arrival information can be structured into a transparent workflow that helps reason about cross-domain turnaround readiness before arrival. A maintenance issue can change stand-side preparation, an inventory issue can affect catering and boarding readiness, and an unconfirmed assistance request can reduce coordination margin even when other modules are nominal.

## 12. Limitations and Threats to Validity

The main limitation is synthetic data. The scenario sweep is controlled and reproducible, but it is not observational airline evidence. The system has not been evaluated on real airline, airport, or station-operation data. No OCC user study has been conducted. No airline deployment, certification, safety assurance, operational savings, or return-on-investment claim is made.

The readiness thresholds are heuristic. The fusion layer is transparent but rule-based rather than learned from OCC decisions. The maintenance and inventory modules are trained on synthetic labels. The bottleneck model predicts process classes, not full turnaround duration. Passenger assistance is readiness logic, not localization ML. The failed maintenance monotonicity checks further show that the current trained-module plus fusion behavior would need additional hardening before any practical deployment study.

## 13. Conclusion

This paper presents a pre-arrival OCC decision-support architecture for aircraft turnaround coordination and evaluates it through controlled synthetic scenarios. The results show that heterogeneous pre-arrival maintenance, inventory, bottleneck, and assistance-readiness signals can be fused into differentiated advisory outputs while preserving a transparent human-in-the-loop workflow. The study also shows the limits of the present evidence base: controlled scenario behavior is useful for architecture evaluation, but it is not a substitute for airline data, expert review, OCC user evaluation, or deployment-oriented validation.

## Data, Code, and Artifact Availability

The demonstrator source code, scenario-evaluation scripts, generated tables, and generated figures used in this study are available at https://github.com/purohit0208/intact-occ-decision-support-demonstrator. No airline operational dataset is included.

## Declaration of Generative AI and AI-Assisted Technologies

During manuscript preparation, OpenAI Codex was used to support document structuring, local script generation, and formatting. The authors are responsible for reviewing, verifying, and approving the final manuscript content before submission.

## References

Ardebili, A.A., Ficarella, A., Longo, A., Khalil, A., Khalil, S., 2023. Hybrid turbo-shaft engine digital twinning for autonomous aircraft via AI and synthetic data generation. Aerospace 10, 683. https://doi.org/10.3390/aerospace10080683

Basturk, O., Cetek, C., 2021. Prediction of aircraft estimated time of arrival using machine learning methods. The Aeronautical Journal 125, 1245-1259. https://doi.org/10.1017/aer.2021.13

Clarke, M.D.D., 1998. Irregular airline operations: a review of the state-of-the-practice in airline operations control centers. Journal of Air Transport Management 4, 67-76. https://doi.org/10.1016/S0969-6997(98)00012-X

Clausen, J., Larsen, A., Larsen, J., Rezanova, N.J., 2010. Disruption management in the airline industry - Concepts, models and methods. Computers & Operations Research 37, 809-821. https://doi.org/10.1016/j.cor.2009.03.027

Conde, J., Munoz-Arcentales, A., Romero, M., Rojo, J., Salvachua, J., Huecas, G., Alonso, A., 2022. Applying digital twins for the management of information in turnaround event operations in commercial airports. Advanced Engineering Informatics 54, 101723. https://doi.org/10.1016/j.aei.2022.101723

Dangut, M.D., Jennions, I.K., King, S., Skaf, Z., 2022. Application of deep reinforcement learning for extremely rare failure prediction in aircraft maintenance. Mechanical Systems and Signal Processing 171, 108873. https://doi.org/10.1016/j.ymssp.2022.108873

Dangut, M.D., Jennions, I.K., King, S., Skaf, Z., 2023. A rare failure detection model for aircraft predictive maintenance using a deep hybrid learning approach. Neural Computing and Applications 35, 2991-3009. https://doi.org/10.1007/s00521-022-07167-8

de Frutos Carro, M.A., Villalonga, C.C., Cruz, A.B., 2024. Validating synthetic data for perception in autonomous airport navigation tasks. Aerospace 11, 383. https://doi.org/10.3390/aerospace11050383

Evler, J., Asadi, E., Preis, H., Fricke, H., 2021a. Airline ground operations: Optimal schedule recovery with uncertain arrival times. Journal of Air Transport Management 92, 102021. https://doi.org/10.1016/j.jairtraman.2021.102021

Evler, J., Asadi, E., Preis, H., Fricke, H., 2021b. Airline ground operations: Schedule recovery optimization approach with constrained resources. Transportation Research Part C: Emerging Technologies 128, 103129. https://doi.org/10.1016/j.trc.2021.103129

Evler, J., Lindner, M., Fricke, H., Schultz, M., 2022. Integration of turnaround and aircraft recovery to mitigate delay propagation in airline networks. Computers & Operations Research 138, 105602. https://doi.org/10.1016/j.cor.2021.105602

Fogaca, L.B., Henriqson, E., Carim Junior, G., Lando, F., 2022. Airline disruption management: A naturalistic decision-making perspective in an operational control centre. Journal of Cognitive Engineering and Decision Making 16, 3-28. https://doi.org/10.1177/15553434211061024

Gok, Y.S., Padron, S., Tomasella, M., Guimarans, D., Ozturk, C., 2023. Constraint-based robust planning and scheduling of airport apron operations through simheuristics. Annals of Operations Research 320, 795-830. https://doi.org/10.1007/s10479-022-04547-0

Gotti, D., Morales, E., Routhier, F., Riendeau, J., Hadj Hassen, A., 2024. Dehumanizing air travel: a scoping review on accessibility and inclusion of people with disabilities in international airports. Frontiers in Rehabilitation Sciences 5, 1305191. https://doi.org/10.3389/fresc.2024.1305191

Guimarans, D., Padron, S., 2022. A stochastic approach for planning airport ground support resources. International Transactions in Operational Research 29, 3316-3345. https://doi.org/10.1111/itor.13104

Hakami, A., 2024. Strategies for overcoming data scarcity, imbalance, and feature selection challenges in machine learning models for predictive maintenance. Scientific Reports 14, 9645. https://doi.org/10.1038/s41598-024-59958-9

Hassan, L.K., Santos, B.F., Vink, J., 2021. Airline disruption management: A literature review and practical challenges. Computers & Operations Research 127, 105137. https://doi.org/10.1016/j.cor.2020.105137

Jiang, Y., Tran, T.H., Williams, L., 2023. Machine learning and mixed reality for smart aviation: Applications and challenges. Journal of Air Transport Management 111, 102437. https://doi.org/10.1016/j.jairtraman.2023.102437

Kabashkin, I., Shoshin, L., 2024. Artificial Intelligence of Things as new paradigm in aviation health monitoring systems. Future Internet 16, 276. https://doi.org/10.3390/fi16080276

Kicinger, R., Krozel, J., Chen, J.T., Schelling, S., 2025. Machine learning of multimodal influences on airport pushback delays. Journal of Aerospace Information Systems 22, 750-761. https://doi.org/10.2514/1.I011546

Lee, C.D., Rafferty, E., Oliver, C., Cooper, R., Candiotti, J., Deepak, N., Cooper, R.A., 2025. Accessible commercial airline travel for mobility device users: A focus group study with veterans. Transportation Research Record: Journal of the Transportation Research Board 2679, 542-553. https://doi.org/10.1177/03611981241295704

Lee, J., Mitici, M., 2023. Deep reinforcement learning for predictive aircraft maintenance using probabilistic Remaining-Useful-Life prognostics. Reliability Engineering & System Safety 230, 108908. https://doi.org/10.1016/j.ress.2022.108908

Makhloof, M.A.A., Waheed, M.E., Badawi, U.A.E.R., 2014. Real-time aircraft turnaround operations manager. Production Planning & Control 25, 2-25. https://doi.org/10.1080/09537287.2012.655800

Malefors, C., Secondi, L., Marchetti, S., Eriksson, M., 2022. Food waste reduction and economic savings in times of crisis: The potential of machine learning methods to plan guest attendance in Swedish public catering during the Covid-19 pandemic. Socio-Economic Planning Sciences 82, 101041. https://doi.org/10.1016/j.seps.2021.101041

Mosqueira-Rey, E., Hernandez-Pereira, E., Alonso-Rios, D., Bobes-Bascaran, J., Fernandez-Leal, A., 2023. Human-in-the-loop machine learning: a state of the art. Artificial Intelligence Review 56, 3005-3054. https://doi.org/10.1007/s10462-022-10246-w

Okwir, S., Amouzgar, K., Ng, A.H.C., 2025. Exploring prediction accuracy for optimal taxi times in airport operations using various machine learning models. Journal of Air Transport Management 122, 102684. https://doi.org/10.1016/j.jairtraman.2024.102684

Rodrigues, M., Migueis, V., Freitas, S., Machado, T., 2024. Machine learning models for short-term demand forecasting in food catering services: A solution to reduce food waste. Journal of Cleaner Production 435, 140265. https://doi.org/10.1016/j.jclepro.2023.140265

Sahadevan, D., Al Ali, H., Notman, D., Mukandavire, Z., 2023. Optimising airport ground resource allocation for multiple aircraft using machine learning-based arrival time prediction. Aerospace 10, 509. https://doi.org/10.3390/aerospace10060509

Stefani, T., Christensen, J.M., Girija, A.A., Gupta, S., Durak, U., Koster, F., Kruger, T., Hallerbach, S., 2025. Automated scenario generation from Operational Design Domain model for testing AI-based systems in aviation. CEAS Aeronautical Journal 16, 197-212. https://doi.org/10.1007/s13272-024-00772-4

Su, Y., Xie, K., Wang, H., Liang, Z., Chaovalitwongse, W.A., Pardalos, P.M., 2021. Airline disruption management: A review of models and solution methods. Engineering 7, 435-447. https://doi.org/10.1016/j.eng.2020.08.021

Vaccaro, M., Almaatouq, A., Malone, T., 2024. When combinations of humans and AI are useful: A systematic review and meta-analysis. Nature Human Behaviour 8, 2293-2303. https://doi.org/10.1038/s41562-024-02024-1

Vink, J., Santos, B.F., Verhagen, W.J.C., Medeiros, I., Filho, R., 2020. Dynamic aircraft recovery problem - An operational decision support framework. Computers & Operations Research 117, 104892. https://doi.org/10.1016/j.cor.2020.104892

Wandelt, S., Chen, X., Sun, X., 2025. Flight delay prediction: A dissecting review of recent studies using machine learning. IEEE Transactions on Intelligent Transportation Systems 26, 4283-4297. https://doi.org/10.1109/TITS.2025.3528536

Wu, Y., Zhou, J., Xia, Y., Zhang, X., Cao, Z., Zhang, J., 2023. Neural airport ground handling. IEEE Transactions on Intelligent Transportation Systems 24, 15652-15666. https://doi.org/10.1109/TITS.2023.3253552

Xie, Y., Pongsakornsathien, N., Gardi, A., Sabatini, R., 2021. Explanation of machine-learning solutions in air-traffic management. Aerospace 8, 224. https://doi.org/10.3390/aerospace8080224

Zeng, J., Liang, Z., 2023. A dynamic predictive maintenance approach using probabilistic deep learning for a fleet of multi-component systems. Reliability Engineering & System Safety 238, 109456. https://doi.org/10.1016/j.ress.2023.109456

Zoutendijk, M., Mitici, M., 2021. Probabilistic flight delay predictions using machine learning and applications to the flight-to-gate assignment problem. Aerospace 8, 152. https://doi.org/10.3390/aerospace8060152
