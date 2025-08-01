# ENTROPYMAX 2.0

*A modernised version of the EntropyMax application for geological and geophysical analysis and data processing, with built‑in interactive visualisation that reduces or eliminates the need to move results into spreadsheets or other external software for plotting and mapping.*

---

## Table of Contents

* [Project Overview](#project-overview)
* [Roadmap](#roadmap)
* [Project Structure](#project-structure)
* [Development Status](#development-status)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)

## Project Overview

**ENTROPYMAX 2.0** is a ground‑up rewrite of the original EntropyMax that preserves its legacy geological and geophysical analysis core while **enhancing with a rigorously maintainable and extensible architecture**. Embedded, interactive visualisation is an intended requirement—every analytical routine should render maps, charts and cross‑plots directly inside the application, reducing or eliminating the time spent exporting data to spreadsheets or other external tools for refining, plotting, and mapping. **By design, the system aims to transfer as much cognitive load as possible from the user to the computer—automating repetitive analysis so geoscientists can concentrate on high‑value interpretation.** **Operating under a tight semester timeline, we are doubling‑down on clean‑code conventions, modular interfaces and comprehensive automated tests to ensure that future developers can add features or refine algorithms swiftly and safely—without wrestling with technical debt or fresh legacy complexity.**

## Roadmap

Project work is organised into three sprints aligned with UWA Semester 2 2025.

| Sprint | Date window | Focus                                                            | Intended outcomes                                                                                                                                                            |
| ------ | ----------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**  | Jul → Aug   | Legacy audit, architecture planning & visualisation requirements | · Select technology stack (including plotting/visualisation libraries)· Define module boundaries and data‑flow for on‑screen plots· Complete migration repository and documentation. Establish roles and CI/CD.     |
| **2**  | Aug → Sep   | Core algorithms **& visualisation prototype**                    | · Port first analytical module· Prototype in‑app plotting pipeline (e.g., interactive maps, scatter/line charts)· Establish automated test harness· Draft public API         |
| **3**  | Sep → Oct   | **User experience & advanced visualisation**                     | · Deliver fully integrated visualisation dashboard with export‑free workflow· Add sample datasets and tutorials showcasing plotting features· Finalise developer & user docs |

## Project Structure

```
ENTROPYMAX2.0/
├── legacy/                # Original VB6 application (read‑only)
├── src/                   # Modern rewrite (language & frameworks TBD)
├── tests/                 # Automated tests (framework TBD)
├── docs/                  # Design docs & user guides
└── examples/              # Sample datasets and walkthroughs
```

*Directory layout and tooling will evolve once the technology stack is finalised.*

## Development Status

The project is currently in **Sprint 1 – planning phase**. No concrete installation or build steps exist yet.

## Contributing

We welcome feedback, bug reports and feature ideas via **GitHub Issues** or **Discussions** from interested external parties. Please note that **pull requests will not be considered** until the assessed component of UWA’s CITS3002 unit concludes (late October 2025) to preserve academic integrity *and our sanity*.

## License

MIT (provisional) — subject to final approval.

## Contact

[CITS3002 Group 31](https://github.com/cits3002-group-31/ENTROPYMAX2.0)
