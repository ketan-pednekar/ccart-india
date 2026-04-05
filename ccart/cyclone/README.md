# CCART Cyclone Module

***Historical + Synthetic Tropical Cyclone Modelling for India and Beyond***

*Synthetic cyclone engine for India — 1100+ tracks, three scenarios, full hazard → exposure → impact → calibration pipeline, district-level outputs.*

The **CCART Cyclone Module** provides a complete, modular, research‑grade framework for tropical cyclone hazard and impact modelling.
It supports both:

- **Historical cyclone reconstruction** using IBTrACS + CLIMADA
- **Synthetic cyclone simulation** using CCART’s scenario‑aware generator

The module is designed to be:

- scientifically honest
- fully modular
- country‑agnostic
- reproducible
- open‑source ready

It is the most mature hazard subsystem in CCART and sets the architectural standard for all future modules.

---

## 🌍 Architecture Overview

The cyclone module is composed of two parallel modelling pipelines:

**1. Historical Pipeline**

Reconstructs cyclone hazards from IBTrACS best‑track data.

**2. Synthetic Pipeline**

Generates fully synthetic, scenario‑aware cyclone events using:

- statistical analog selection
- physical perturbations
- structural variety
- CLIMADA‑safe constraints

Both pipelines feed into a shared impact, calibration, and HWE workflow.

---

## 🚀 Quick start

```python
from ccart.cyclone.synthetic.run_single_synthetic import run_single_synthetic

result = run_single_synthetic(
    run_dir="outputs/test_run",
    scenario="baseline",
    ...
)
```
---

## 📁 Folder Structure

```python
ccart/cyclone/
    ├── hazard.py                     # Historical hazard builder
    ├── synthetic/
    │     ├── synthetic_generator.py  # Synthetic cyclone engine
    │     ├── hazard_from_tracks.py   # Synthetic hazard builder
    │     ├── synthetic_exposure.py   # Districts + exposure preprocessing
    │     ├── synthetic_impact.py     # Hazard stats + raw impact
    │     ├── synthetic_calibration.py# DLNA + coastal calibration
    │     ├── synthetic_hwe.py        # HWE metrics
    │     ├── run_single_synthetic.py # End-to-end single-run pipeline
    │     └── run_batch.py            # Multi-scenario batch runner
    └── examples/
          └── run_synthetic_batch_example.py
```

---

## 🧱 Module Index (Subsystem READMEs)

Each subsystem has its own dedicated README with full documentation.

**1. Historical Hazard Module**

`ccart/cyclone/hazard.py`

Generates CLIMADA tropical cyclone hazards from IBTrACS tracks:

- corridor‑based centroid grid
- CLIMADA windfield generation
- intensity cleaning + validation
- district‑level hazard statistics

Used for historical reconstruction and validation.

**2. Synthetic Cyclone Generator**

`ccart/cyclone/synthetic/synthetic_generator.py`

The core synthetic engine:

- landfall filtering
- DBSCAN clustering
- weighted cluster selection (all archetypes represented)
- PCA‑based analog refinement
- genesis jitter
- track perturbation
- intensity, RMW, rainfall variety
- scenario logic
- CLIMADA‑safe constraints

Outputs a fully synthetic cyclone track.

**3. Synthetic Hazard Module**

`ccart/cyclone/synthetic/hazard_from_tracks.py`

Builds CLIMADA hazards from synthetic tracks:

- variable reshaping
- fallback logic
- negative intensity cleaning
- weak‑storm handling
- CSR matrix enforcement

Produces synthetic hazard footprints.

**4. Synthetic Exposure Module**

`ccart/cyclone/synthetic/synthetic_exposure.py`

Spatial preprocessing:

- district loading + normalization
- coastal distance computation
- inland masking
- exposure clipping to hazard footprint

Ensures spatial consistency.

**5. Synthetic Impact Module**

`ccart/cyclone/synthetic/synthetic_impact.py`

Core impact computation:

- district hazard statistics
- inland mask merging
- raw impact (exposure × vulnerability × hazard)
- district‑level aggregation

Feeds into calibration and HWE.

**6. Synthetic Calibration Module**

`ccart/cyclone/synthetic/synthetic_calibration.py`

DLNA‑style calibration:

- compute DLNA synthetic total
- coastal calibration
- inland zeroing
- unified calibrated loss table

Ensures realistic spatial distribution.

**7. Synthetic HWE Module**

`ccart/cyclone/synthetic/synthetic_hwe.py`

Distributional impact layer:

- align calibrated losses with wealth
- compute HWE metrics
- attach metrics to district geometries

Used for equity‑focused analysis.

**8. Single‑Run Orchestrator**

`ccart/cyclone/synthetic/run_single_synthetic.py`

End‑to‑end pipeline for one synthetic cyclone:

- generate track
- build hazard
- clip exposure
- compute hazard stats
- compute raw impact
- calibrate
- compute HWE
- save outputs + metadata

Forms the backbone of interactive runs.

**9. Batch Runner**

`ccart/cyclone/synthetic/run_batch.py`

Large‑scale ensemble engine:

- multi‑scenario execution
- resume‑safe looping
- clean folder structure
- scenario summaries
- master summary

Used for synthetic ensemble studies.

**10. Example Batch Script**

`examples/run_synthetic_batch_example.py`

Demonstrates how to call `run_batch()` with:

- districts
- coastline
- wealth
- exposures
- vulnerability curves
- cleaned historical tracks

A ready‑to‑run template for users.

---

## 🔄 Pipeline Summary

**Historical Pipeline**

```python
IBTrACS → build_hazard → district_hazard_stats → impact (optional)
```

**Synthetic Pipeline**

```python
synthetic_generator
    → synthetic_hazard
    → synthetic_exposure
    → synthetic_impact
    → synthetic_calibration
    → synthetic_hwe
    → outputs + metadata
```

**Batch Pipeline**

```python
run_batch → run_single_synthetic → scenario summaries → master summary
```
---

## 🧬 Design Philosophy

The cyclone module embodies CCART’s core principles:

- **Modularity** — each subsystem is independent and testable
- **Transparency** — no black‑box shortcuts
- **Reproducibility** — no hard‑coded paths; config‑driven
- **Scientific honesty** — explicit assumptions, clear logic
- **Teaching‑friendly** — readable, inspectable, extensible

It is built to support:

- research
- teaching
- open‑source collaboration
- institutional credibility

---

## 🎯 Summary

The CCART Cyclone Module is a complete, end‑to‑end framework for:

- historical cyclone reconstruction
- synthetic cyclone simulation
- hazard modelling
- impact modelling
- calibration
- HWE analysis
- ensemble generation

It is the most mature subsystem in CCART and the blueprint for all future hazard modules.