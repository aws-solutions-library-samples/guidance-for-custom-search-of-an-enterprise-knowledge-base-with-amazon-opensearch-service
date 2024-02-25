FROM nvcr.io/nvidia/pytorch:23.10-py3

WORKDIR /workspace/
ENV PYTHONPATH /workspace/
COPY requirements.txt /workspace/
COPY . /workspace

RUN pip install --no-cache-dir -r /workspace/requirements.txt && \
    pip install bitsandbytes --upgrade
RUN pip install xformers==0.0.22.post4 --index-url https://download.pytorch.org/whl/cu118
RUN ls /workspace
# RUN pip uninstall -y flash-attn