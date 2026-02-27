FROM pytorch/pytorch:2.2.2-cuda11.8-cudnn8-runtime

# Avoid interactive prompts during apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Install mede from pinned requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Installed as sitecustomize.py so CPython runs it on every interpreter startup
#! Update this path appropriately if base image is updated!
COPY utils/shm_fix.py /opt/conda/lib/python3.10/sitecustomize.py

# Install entrypoint script
RUN mkdir -p /scripts
COPY entrypoint.py /scripts/entrypoint.py

# Create mount points
RUN mkdir -p /input /output

# Configure entrypoint
RUN chmod a+x /scripts/entrypoint.py

# XNAT Container Service command auto-discovery
LABEL org.nrg.commands="[{\"name\":\"mede-deface\",\"label\":\"MEDE Deface\",\"description\":\"Remove facial features from head MRI/CT scans using MedNeXt neural network defacing\",\"version\":\"0.0.2\",\"schema-version\":\"1.0\",\"image\":\"maxwellthorpe/mede-deface:0.0.2\",\"type\":\"docker\",\"command-line\":\"python /scripts/entrypoint.py /input /output\",\"override-entrypoint\":true,\"mounts\":[{\"name\":\"in\",\"writable\":false,\"path\":\"/input/dicoms\"},{\"name\":\"out\",\"writable\":true,\"path\":\"/output\"}],\"environment-variables\":{\"NVIDIA_VISIBLE_DEVICES\":\"all\"},\"ports\":{},\"inputs\":[],\"outputs\":[{\"name\":\"defaced-dicoms\",\"description\":\"Defaced DICOM files\",\"required\":true,\"mount\":\"out\",\"glob\":\"**/*\"}],\"xnat\":[{\"name\":\"mede-deface-scan\",\"label\":\"MEDE Deface (Scan)\",\"description\":\"Deface a head MRI/CT scan using MedNeXt neural network\",\"contexts\":[\"xnat:imageScanData\"],\"external-inputs\":[{\"name\":\"scan\",\"description\":\"Input scan\",\"type\":\"Scan\",\"required\":true,\"load-children\":true}],\"derived-inputs\":[{\"name\":\"scan-dicoms\",\"description\":\"The DICOM resource on the scan\",\"type\":\"Resource\",\"matcher\":\"@.label == 'DICOM'\",\"required\":true,\"provides-files-for-command-mount\":\"in\",\"load-children\":true,\"derived-from-wrapper-input\":\"scan\",\"multiple\":false}],\"output-handlers\":[{\"name\":\"defaced-resource\",\"accepts-command-output\":\"defaced-dicoms\",\"as-a-child-of\":\"scan\",\"type\":\"Resource\",\"label\":\"DEFACED\"}]}],\"reserve-memory\":8192,\"limit-memory\":16384,\"container-labels\":{},\"generic-resources\":{},\"ulimits\":{},\"secrets\":[]}]"
