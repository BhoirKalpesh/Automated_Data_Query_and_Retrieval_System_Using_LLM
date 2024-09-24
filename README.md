# Automated Data Query and Retrieval System Using LLM

## Overview

This project is an Automated Data Query and Retrieval System that leverages Local Language Models (LLMs) to generate MongoDB queries based on user-defined conditions. The system can read data from CSV files, load it into MongoDB, and execute generated queries to retrieve results. 

## Approach

In this project, I explored two methods for generating MongoDB queries based on user-defined conditions:

1. **Local Language Model (LLM) Setup**: This method involves running a local LLM on my system. While this approach allows for flexibility and control over the model, it has been observed that it takes a considerable amount of time to run due to the limited processing power of my system.

2. **Hugging Face Model**: The second method utilizes a pre-trained model from Hugging Face. This approach leverages the cloud infrastructure of Hugging Face, allowing for faster query generation and execution compared to the local setup.

By comparing these two methods, I aim to identify the most efficient approach for the Automated Data Query and Retrieval System.

## Features

- Load CSV data into MongoDB.
- Generate MongoDB queries based on user input conditions.
- Execute generated queries and display results.
- Save generated queries and conditions to a text file.
- User-friendly interface built with Streamlit.

## Model Downloading

For local setup, you can use the quantized version of the model for better performance. Download the following model file:

- [Llama-2-7B GGUF (Quantized)](https://huggingface.co/TheBloke/Llama-2-7B-GGML/blob/main/llama-2-7b.ggmlv3.q8_0.bin)

Make sure to place the downloaded model file in the appropriate directory within your project to enable smooth integration with the system.


### Environment Setup

This project uses a Conda virtual environment. Follow these steps to set it up:

1. **Create a new Conda environment** (replace `your_env_name` with your preferred environment name):
   ```bash
   conda create -n your_env_name python=3.8
   conda activate your_env_name


2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt

3. **Start the Streamlit application**:
    ```bash
    streamlit run app.py
