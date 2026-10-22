# **Project: CPU-Z Modernization — Hardware Intelligence Dashboard** 

## **1. Mission** 

Act as an autonomous senior reverse engineer, Windows systems engineer, software architect, and UI/UX designer. 

Modernize CPU-Z into a visually polished, modern hardware-information application with an interactive, infographic-style dashboard while preserving the accuracy and usefulness of its hardware-identification capabilities. 

### **Core objectives** 

- Investigate the installed CPU-Z application and understand its functionality. 

- Use REA and Ghidra where appropriate to analyze relevant binary behavior. 

- Identify reliable and legitimate ways to retrieve hardware information. 

- Build a modern application with a clean, responsive interface. 

- Validate actual hardware readings against CPU-Z and other trustworthy sources. 

- Execute research, implementation, testing, debugging, and UI refinement autonomously. 

- Avoid requiring me to write code manually. 

Choose the most suitable models, tools, libraries, frameworks, and implementation strategy for each phase. Use your judgment to optimize accuracy, reliability, maintainability, and execution quality. 

Do not stop after generating code. Build, run, test, inspect, and improve the application. 

## **2. Target Discovery** 

Discover the installed CPU-Z executable from 

- C:\Program Files\CPUID\CPU-Z\ 

## **3. Hardware Data Discovery — REA and Ghidra First** 

Prioritize **REA and Ghidra** to investigate how CPU-Z retrieves, calculates, interprets, and displays hardware information. 

- Trace each field from its original input through the relevant functions and transformations to its displayed value. 

- Inspect decompiled code, disassembly, cross-references, data structures, constants, and register operations as applicable. 

- **Never assume or invent a field's formula, scaling factor, unit conversion, or interpretation.** Establish the method using reverse-engineering evidence. 

- Do not replace CPU-Z's detection logic with generic libraries before investigating the original implementation. 

- Use Windows APIs, WMI/CIM, vendor interfaces, and other libraries to corroborate findings or fill documented gaps. 

- Validate implemented fields against CPU-Z wherever practical. 

Document findings in research/data-access-strategy.md, including relevant functions and evidence, input sources, verified calculation methods, confidence levels, validation results, and implementation decisions. 

**For any field whose formula or detection method remains unknown, explicitly document it as Unknown — further REA/Ghidra investigation required, describe the missing evidence, and do not invent a replacement formula.** If an alternative method is necessary, document it separately and do not claim equivalence without validation. 

Create research/data-access-strategy.md documenting: 

- Candidate data sources and the information they provide. 

- Supported hardware and operating-system configurations. 

- Data freshness and accuracy limitations. 

- Required permissions, drivers, or dependencies. 

- Licensing and compatibility considerations. 

- The recommended implementation strategy and rationale. 

Prefer reliable, maintainable, documented data-access methods where practical. Use reverse engineering to investigate gaps that matter to the project. 

## **4. Reverse Engineering with REA and Ghidra** 

Use REA and Ghidra to investigate CPU-Z behavior where doing so adds meaningful value. 

Investigate relevant functionality, including: 

- CPU identification: vendor, family, model, stepping, and architecture. 

- Processor topology, core/thread counts, and cache hierarchy. 

- Processor features and instruction-set support. 

- Clock and frequency measurement methods. 

- Motherboard and chipset identification. 

- BIOS vendor, version, and date. 

- Memory type, capacity, channels, frequency, and timings. 

- SPD and memory-module information. 

- Graphics adapter identification and related information. 

#### ● Other useful hardware fields discovered in the installed version. 

For each investigation: 

1. Locate relevant functions, references, and dependencies. 

2. Inspect decompiled code and supporting structures. 

3. Trace the data source, transformations, units, and output fields. 

4. Record supporting evidence. 

5. Distinguish confirmed behavior from inference. 

6. Validate findings against actual system behavior or documented interfaces. 

7. Identify which findings are useful for the new implementation. 

Never invent function addresses, symbols, structure layouts, register meanings, or metric values. 

Treat undocumented internal structures as implementation details, not stable APIs. 

Do not bypass licensing, defeat protections, copy proprietary implementation code into the new application, or introduce unsafe undocumented hardware access. 

If a field cannot be understood or reproduced confidently, document the limitation and implement a safe alternative where possible. 

## **5. Persistent Evidence and Research** 

Create research/evidence-ledger.md. 

For every significant finding, record: 

- Finding ID and feature. 

- Relevant function, symbol, or address, if verified. 

- Evidence source and analysis method. 

- Data type, unit, scaling, and interpretation. 

- Detection mechanism and dependencies. 

- Confidence level: Confirmed, Strongly Inferred, Tentative, or Unknown. 

- Validation method and result. 

- Implications for the new application. 

- Remaining questions and follow-up work. 

Create research/coverage-matrix.md listing planned fields and their status: 

- Implemented and verified. 

- Implemented but not fully verified. 

- Partially supported. 

- Unsupported. 

- Blocked by permissions, hardware, or licensing. 

Keep reverse-engineering discoveries separate from actual application capabilities. Discovering a function does not prove that the new application can safely reproduce its behavior. 

## **6. Application Architecture** 

Build a maintainable application rather than forcing everything into one HTML file. 

Choose the framework and architecture based on the project's requirements and the available environment. 

A possible structure is: 

- backend/ — hardware detection, data providers, and API. 

- frontend/ — dashboard components, pages, and visualizations. 

- research/ — evidence ledger and analysis notes. 

- tests/ — automated and integration tests. 

- docs/ — architecture, setup, limitations, and troubleshooting. 

- scripts/ — startup, shutdown, and validation utilities. 

### **Backend requirements** 

Implement a normalized hardware-information layer that separates data acquisition from presentation. 

Represent each field with suitable metadata, such as: 

- Value. 

- Unit, when applicable. 

- Data source. 

- Availability status. 

- Timestamp or freshness information. 

- Optional confidence or explanatory notes. 

Expose stable interfaces for: 

- System overview. 

- CPU details. 

- Cache and processor topology. 

- Motherboard and BIOS. 

- Memory and SPD. 

- Graphics and other supported components. 

- Refresh status and diagnostic information. 

Use background polling only for genuinely dynamic fields. Avoid repeatedly rediscovering static specifications. 

Handle unsupported hardware, missing dependencies, access-denied errors, and unavailable data gracefully. 

Represent unavailable fields explicitly. Never substitute fabricated readings for missing values. 

Bind the backend to loopback by default and do not expose the API publicly without an explicit requirement and suitable security controls. 

## **7. Premium Infographic Dashboard** 

Design a visually distinctive hardware-information experience that is substantially more modern than the traditional CPU-Z interface. 

### **Visual direction** 

- Dark-first theme with deep navy and charcoal surfaces. 

- Restrained cyan, blue, and indigo accents. 

- Clear typography and strong information hierarchy. 

- Modern cards, subtle depth, and restrained glass effects. 

- Responsive layouts suitable for desktop and smaller screens. 

- Smooth, lightweight animations. 

- Consistent icons, spacing, borders, and chart styles. 

- Accessible contrast, keyboard navigation, and readable technical labels. 

Avoid excessive empty space, oversized decoration, unnecessary animations, and visual effects that interfere with technical readability. 

### **Dashboard overview** 

Create an informative system overview with: 

- Processor name and key specifications. 

- Core and thread counts. 

- Current clock information when reliably available. 

- Cache hierarchy. 

- Motherboard and BIOS summary. 

- Memory capacity, type, channel configuration, and supported timings. 

- Graphics adapter summary, where supported. 

- A compact hardware configuration overview. 

Use informative metric cards, concise labels, and clear visual grouping. Distinguish static specifications from live measurements. 

### **Dedicated sections** 

#### **CPU** 

- Processor identification and architecture. 

- Family, model, and stepping where available. 

- Core and thread topology. 

- Cache hierarchy. 

- Supported instruction sets and processor features. 

- Clock information, with clear units and measurement semantics. 

#### **Mainboard** 

- Manufacturer and model. 

- Chipset. 

- BIOS vendor, version, and date where available. 

#### **Memory** 

- Installed capacity. 

- Memory type. 

- Channel configuration. 

- Frequency and timings where supported. 

- Module-specific details and SPD information when obtainable through an appropriate source. 

#### **Graphics** 

- Adapter identity and vendor. 

- Graphics memory and driver version where available. 

- Other supported adapter information. 

#### **System** 

- Operating system and architecture. 

- Processor and memory summary. 

- Other useful machine-level information. 

Implement additional sections only where they provide meaningful, reliable information. 

### **Visualizations** 

Use visualizations to make technical data easier to understand: 

- Metric cards. 

- Specification tables. 

- Memory-capacity bars. 

- Processor topology diagrams. 

- Cache hierarchy diagrams. 

- Clock indicators where actual measurements are available. 

- Memory-module comparison layouts. 

- Explanatory tooltips for technical terminology. 

#### ● Copy and export actions. 

Do not add meaningless charts to static specifications. Do not invent utilization, temperature, voltage, frequency, or other hardware readings. 

### **Interaction** 

Implement: 

- Navigation between hardware sections. 

- Search across hardware fields. 

- Copy-to-clipboard actions. 

- Export to JSON and CSV. 

- Refresh controls where appropriate. 

- Loading, empty, unsupported, and error states. 

- Optional light theme. 

- Responsive layouts and accessible interactions. 

Make the interface feel like a cohesive, production-quality hardware intelligence product rather than a collection of disconnected cards. 

## **8. Autonomous Implementation Workflow** 

After the initial discovery and research, continue through implementation without waiting for unnecessary approvals. 

Work in verifiable phases: 

1. Inspect the environment and identify the target executable. 

2. Evaluate reliable data-access methods. 

3. Investigate relevant CPU-Z functionality. 

4. Establish the project structure and architecture. 

5. Implement the hardware data providers. 

6. Validate provider output against trustworthy sources. 

7. Define and test normalized interfaces. 

8. Build the dashboard layout and navigation. 

9. Implement individual hardware sections. 

10. Integrate the frontend and backend. 

11. Add search, copy, export, and refresh functionality. 

12. Run automated tests. 

13. Launch the application locally. 

14. Inspect the actual UI using available browser or computer-use tools. 

15. Test important workflows and responsive layouts. 

16. Fix defects and visual inconsistencies. 

17. Repeat validation until the completion criteria are met. 

Do not stop after producing source files. Start the application and verify that it runs. 

If browser automation is unavailable, use the strongest available alternative and explicitly document any missing visual validation. 

## **9. Testing and Hardware Accuracy** 

Create tests for: 

- Hardware provider output and error handling. 

- API response schemas. 

- Missing and unsupported fields. 

- Units, conversions, and normalization. 

- Static versus dynamic data handling. 

- JSON and CSV exports. 

- Loading and failure states. 

- Search, navigation, copy, and refresh. 

- Application startup and shutdown. 

- Local API security. 

Compare readings with CPU-Z running on the same machine whenever practical. 

For discrepancies: 

1. Identify the affected field. 

2. Determine whether the cause is timing, permissions, a different measurement source, a provider limitation, or an implementation defect. 

3. Fix the issue where feasible. 

4. Record unresolved differences in the coverage matrix. 

Do not claim perfect equivalence when the underlying measurement methods differ. Explain meaningful differences and limitations. 

## **10. Persistent Project State** 

Maintain these files throughout implementation: 

- PROJECT_STATUS.md — current phase, completed work, blockers, and next steps. 

- research/evidence-ledger.md — reverse-engineering evidence. 

- research/coverage-matrix.md — field-level support and validation. 

- research/data-access-strategy.md — selected data sources and rationale. 

- docs/decisions.md — architectural and implementation decisions. 

- docs/test-results.md — test results, failures, and outstanding issues. 

Update these files at the end of each substantial phase. 

Ensure another agent session can resume the project from the saved state without repeating completed research unnecessarily. 

## **11. Deliverables** 

Produce: 

1. A runnable, modern CPU-Z-inspired hardware dashboard. 

2. Complete backend and frontend source code. 

3. Evidence ledger and research notes. 

4. Data-access strategy. 

5. Hardware feature coverage matrix. 

6. Architecture and setup documentation. 

7. Automated tests and test results. 

8. Local launch and shutdown scripts. 

9. Troubleshooting documentation. 

10. A final report describing implemented features, verified accuracy, unsupported fields, known limitations, and remaining work. 

## **12. Definition of Done** 

The project is complete only when: 

- The application starts locally using documented instructions. 

- The interface is polished, responsive, and functional. 

- Implemented fields are backed by actual data providers. 

- Important hardware sections work on the available test machine. 

- Unsupported fields are clearly identified instead of fabricated. 

- The original CPU-Z executable remains unchanged. 

- Tests pass, or remaining failures are explicitly documented. 

- The evidence ledger and coverage matrix accurately reflect verified capabilities. 

- The project can be resumed and maintained without repeating completed research. 

Begin with environment discovery and data-access evaluation. Then proceed autonomously through research, implementation, testing, and visual refinement. Choose the most suitable tools and models for the work, and make evidence-based decisions throughout the project. 

