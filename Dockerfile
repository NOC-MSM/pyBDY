FROM continuumio/miniconda3

WORKDIR /src/PyNEMO

COPY environment.yml /src/PyNEMO/

RUN conda install -c conda-forge gcc python=3.10 \
    && conda env update -n base -f environment.yml

COPY . /src/PyNEMO

RUN pip install --no-deps -e .
