# MEDE Deface — XNAT Container Service

Defacing-only container for XNAT, powered by the [MEDE](https://github.com/TIO-IKIM/medical_image_deidentification) toolkit's MedNeXt neural network.

## Scope

**Only defacing (`-de`) is enabled.** No other MEDE features are accessible.

## GPU / CPU Support

The container auto-detects hardware:
- **GPU**: Fast inference (seconds to minutes per volume).
    - XNAT command.json automatically flags for GPU availability.
- **CPU**: Slower but functional fallback.

PyTorch detects CUDA availability automatically.

## Build

```bash
docker build -t maxwellthorpe/mede-deface:0.0.2 .
```

Estimated image size: ~8–10 GB (vs 16.8 GB for `morrempe/mede`).

## Container Input

Mounts images from DICOM resource to `/input/dicoms` (not `/input` directly — see [Gotchas](#gotchas)):

## XNAT Deployment
Run the container form the scan context:
  - Single Scan: **Navigate to a scan with a DICOM resource → Run Containers → MEDE Deface**
  - Batch Scans: **Navigate to a project → Processing Dashboard → Filter on targeted image modality → MEDE Deface**

### Supported modalities
Defacing only works on **MR** and **CT** head scans. Other modalities (e.g. ultrasound) are not supported. 


### Memory requirements
The XNAT command reserves 8 GB and limits at 16 GB (`command.json`). CPU inference on a full 3D volume typically uses 8–12 GB RAM. XNAT admins should ensure the Docker host has at least 16 GB available for the container.


## How It Works

1. User selects a scan, or designates a batch run in XNAT
2. Container mounts the scan's DICOM resource at `/input/dicoms`
3. Entrypoint passes `/input` to MEDE, which discovers `dicoms/` as a subdirectory
4. MedNeXt generates a binary defacing mask via neural net inference
5. Mask is multiplied with the original image zeroing out facial features
6. Defaced DICOMs are written to `/output`
7. XNAT stores the output as a `DEFACED` resource on the source scan


## References

- [MEDE on PyPI](https://pypi.org/project/mede/)
- [MEDE on GitHub](https://github.com/TIO-IKIM/medical_image_deidentification)
- Rempe et al., European Radiology, 2025
