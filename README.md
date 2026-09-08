[README.md](https://github.com/user-attachments/files/31968305/README.md)
# Active Brownian Predator–Prey Simulation

Simulation code accompanying the manuscript **“Programmable active motion accelerates catalysis in self-propelled metal–organic framework microreactors.”**

## Overview

This repository contains the Python simulation code used to model a predator–prey system in which:

- prey undergo random Brownian-like motion with a fixed step size;
- predators undergo active Brownian motion;
- predator propulsion speed can be constant, exponentially decaying, or segmented/oscillatory;
- prey are removed when they enter the specified predation radius of a predator;
- predator trajectories, prey population, predator speed, and mean-squared displacement (MSD) are exported for downstream analysis.

The code is intended to accompany the research manuscript:

**Programmable active motion accelerates catalysis in self-propelled metal–organic framework microreactors**

and should be cited together with the associated publication once the article is published.

## Repository contents

```text
.
├── simulate_predator_prey.py
├── README.md
├── CITATION.cff
├── .zenodo.json
├── LICENSE
├── requirements.txt
├── .gitignore
├── CHANGELOG.md
└── ZENODO_METADATA_CHECKLIST.md
```

## Repository

GitHub repository: <https://github.com/farhagroupnu/active-motion-microreactor-simulation>

Repository owner: Farha Group at Northwestern University (`farhagroupnu`)

Maintainer: Zhihua Cheng (`JehuCheng`)

## Requirements

- Python 3.10 or newer
- NumPy
- OpenCV-Python
- Matplotlib
- Pillow

Install dependencies with:

```bash
python -m pip install -r requirements.txt
```

## Running the simulation

From the repository root:

```bash
python simulate_predator_prey.py
```

Results will be written to the `results/` directory.

## Main simulation parameters

The principal parameters are defined at the top of `simulate_predator_prey.py`.

| Parameter | Default value | Description |
|---|---:|---|
| `WIDTH` | 1000 | Simulation width |
| `HEIGHT` | 1000 | Simulation height |
| `N_PREY` | 20,000 | Initial prey population |
| `N_PRED` | 125 | Number of predators |
| `PREY_SPEED` | 250 | Prey displacement per step |
| `ACTIVE_DIFFUSION` | 0.1 | Predator translational diffusion coefficient |
| `ROTATIONAL_DIFFUSION` | 0.1 | Predator rotational diffusion coefficient |
| `PRED_SPEED_MODE` | 1 | Predator speed protocol |
| `PRED_SPEED_INIT` | 1.0 | Initial predator speed |
| `PRED_SPEED_FINAL` | 0.001 | Final speed for decay modes |
| `PRED_SPEED_SEGMENTS` | 5 | Number of segments in mode 3 |
| `STEPS` | 5000 | Number of simulation steps |
| `FRAME_INTERVAL` | 20 | Video frame interval |
| `VIDEO_FPS` | 25 | Output video frame rate |
| `RANDOM_SEED` | 42 | Random-number seed |
| `PREDATION_RADIUS` | 1.0 | Predation distance threshold |

### Predator speed modes

`PRED_SPEED_MODE` controls the predator propulsion protocol:

1. **Constant:** predator speed remains at `PRED_SPEED_INIT`.
2. **Exponential decay:** predator speed decays toward `PRED_SPEED_FINAL`.
3. **Segmented exponential decay:** the exponential decay restarts at the beginning of each segment, producing an oscillatory speed profile.

## Generated outputs

The script generates:

- `results/simulation.mp4` — simulation movie;
- `results/predator_trajectories.png` — predator trajectories;
- `results/prey_count.png` — prey population versus simulation step;
- `results/predator_trajectories.csv` — long-format predator coordinates;
- `results/predator_trajectories_wide.csv` — wide-format predator coordinates;
- `results/prey_count.csv` — prey population at each step;
- `results/predator_speed.csv` — predator speed history;
- `results/predator_msd.csv` — mean-squared displacement of predators.

The generated numerical outputs are deterministic for a fixed NumPy random seed, subject to differences caused by software/library versions.

## Reproducibility notes

The random-number seed is set by:

```python
RANDOM_SEED = 42
```

For a different stochastic realization, change this value before running the simulation.

The simulation uses an explicit Euler-style time-stepping scheme for the active Brownian motion.

## Important implementation note

The boundary condition in this implementation **relocates particles that leave the simulation domain to random positions inside the canvas**. This behavior is part of the supplied simulation model and should not be interpreted as periodic or reflecting boundary conditions.

## Citation

Please cite the associated research article and this software release when using the code.

**Software citation:**

Zenodo DOI: to be added after the first Zenodo release.

**Associated manuscript:**

Manuscript DOI: not yet available at the time of this software release.

A machine-readable citation record is provided in `CITATION.cff`.

## Authors and affiliations

Authors are listed in `CITATION.cff` and `.zenodo.json`.

Institutional affiliations and the available ORCID identifiers are included in the metadata files.

## License

This software is released under the MIT License. See `LICENSE`.

The copyright holder is Northwestern University.

## Version

Initial submission version: **v1.0.0**

Release version: v1.0.0; release date: 2026-09-08.


## Associated manuscript

**Programmable active motion accelerates catalysis in self-propelled metal–organic framework microreactors**

Authors: Zhihua Cheng, Duaa N. Ansari, Saptasree Bose, Palak Garg, Kent O. Kirlikovali, Omar K. Farha.

Affiliations:
1. Department of Chemistry, Northwestern University
2. International Institute for Nanotechnology, Northwestern University
3. Paula M. Trienens Institute for Sustainability and Energy, Northwestern University
4. Department of Chemical and Biological Engineering, Northwestern University

Corresponding author: Omar K. Farha (o-farha@northwestern.edu)

At the time this package was prepared, the manuscript DOI and Zenodo DOI had not yet been assigned.

## Funding and acknowledgements

The authors acknowledge financial support from the Defense Threat Reduction Agency (award number HDTRA12410014). D.N.A. is supported by the National Science Foundation Graduate Research Fellowship (NSF GRFP) under Grant No. DGE-2234667 and would like to acknowledge support from the Ryan Fellowship and the International Institute for Nanotechnology at Northwestern University.

This work made use of the IMSERC Crystallography, MS and NMR facilities at Northwestern University, which has received support from the Soft and Hybrid Nanotechnology Experimental (SHyNE) Resource (RRID:SCR_017874), and Northwestern University. This work also made use of the EPIC facility (RRID:SCR_026361) of Northwestern University’s NUANCE Center, which has received support from the IIN and Northwestern's MRSEC program (NSF DMR-2308691).

Confocal fluorescent microscopy was performed at the Biological Imaging Facility at Northwestern University (RRID:SCR_017767), graciously supported by the Chemistry for Life Processes Institute, the NU Office for Research, the Department of Molecular Biosciences and the Rice Foundation.

## Repository metadata status

- **Authors:** populated
- **ORCID:** populated for Zhihua Cheng and Omar K. Farha
- **Manuscript title:** populated
- **Manuscript DOI:** not yet available
- **GitHub repository URL:** populated
- **Zenodo DOI:** generated after release
- **Funding/grants and facilities:** populated
- **License copyright holder:** Northwestern University
