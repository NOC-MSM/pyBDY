FROM continuumio/miniconda3

WORKDIR /src/pyBDY

COPY environment.yml /src/pyBDY/

RUN conda install -c conda-forge gcc python=3.9 \
    && conda env update -n base -f environment.yml

COPY . /src/pyBDY

RUN pip install --no-deps -e .
