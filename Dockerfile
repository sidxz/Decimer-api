# Base image with Miniconda
FROM continuumio/miniconda3:latest

# Set environment variables
ENV ENV_NAME=Decimer-api
ENV CONDA_DIR=/opt/conda/envs/$ENV_NAME
ENV PATH=$CONDA_DIR/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libhdf5-dev \
    libhdf5-serial-dev \
    libblas-dev \
    liblapack-dev \
    gfortran \
    build-essential \
    python3-magic \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy environment.yml for Conda environment setup
COPY environment.yml /app/environment.yml

# Install the Conda environment
RUN conda env create -f environment.yml && \
    conda clean -a && \
    echo "source activate $ENV_NAME" > ~/.bashrc

# Activate Conda environment and install any pip dependencies
RUN /bin/bash -c "source ~/.bashrc && conda activate $ENV_NAME"

# Copy the project code
COPY . /app

# Expose the FastAPI app port
EXPOSE 8500

# Command to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8500"]
