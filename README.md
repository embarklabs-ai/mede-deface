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

1. Build or pull the image on your XNAT host
2. **Administer → Plugin Settings → Images & Commands → New Command** → Copy and paste the `command.json` content.
3. XNAT auto-discovers the command from the `org.nrg.commands` Docker LABEL
4. Enable the command at site level (**Administration → Plugins → Container Service → Command Configurations → Enabled toggle**)
5. Enable at project level (**Project Settings → Configure Commands → Enable toggle**)
6. Run the container:
  - Single Scan: **Navigate to a scan with a DICOM resource → Run Containers → MEDE Deface**
  - Batch Scans: **Navigate to a project → Processing Dashboard → Filter on targeted image modality → MEDE Deface**

### Supported modalities
Defacing only works on **MR** and **CT** head scans. Other modalities (e.g. ultrasound) will produce nonsensical output or crash during NIfTI conversion. Filter your input by DICOM Modality tag before running the container.

## Gotchas

### MEDE requires a nested input directory
MEDE expects a parent directory containing a subdirectory of DICOMs so it can pass the whole subdirectory to `dcm2nifti` as one volume. Without adhereing to this structure, MEDE's `get_inference_loader` globs the input directory, treating each `.dcm` file as a separate single-slice volume. This continuously overwrites a single output files resulting in a single defaced slice being returned instead of a full volume.

**Fix:** The mount path is `/input/dicoms` (not `/input`). The entrypoint passes `/input` to MEDE, which discovers `dicoms/` as a subdirectory and assembles the volume correctly.

### `/dev/shm` bus errors in PyTorch DataLoader
Docker's default 64 MB `/dev/shm` is too small for PyTorch's shared-memory tensor transfer between DataLoader workers, causing `bus error` crashes during inference. The container installs `utils/shm_fix.py` as `sitecustomize.py` in the Python site-packages directory. CPython automatically runs `sitecustomize` on every interpreter startup — including spawned DataLoader workers — switching PyTorch to file-descriptor-based sharing (`file_system` strategy) that uses `/tmp` instead of `/dev/shm`.

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
