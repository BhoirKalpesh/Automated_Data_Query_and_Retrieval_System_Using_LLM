# Automated Data Query and Retrieval System Using LLM

## Overview

This project is an Automated Data Query and Retrieval System that leverages Local Language Models (LLMs) to generate MongoDB queries based on user-defined conditions. The system can read data from CSV files, load it into MongoDB, and execute generated queries to retrieve results. 

## Features

- Load CSV data into MongoDB.
- Generate MongoDB queries based on user input conditions.
- Execute generated queries and display results.
- Save generated queries and conditions to a text file.
- User-friendly interface built with Streamlit.

## Requirements

### Environment Setup

This project uses a Conda virtual environment. Follow these steps to set it up:

1. **Create a new Conda environment** (replace `your_env_name` with your preferred environment name):
   ```bash
   conda create -n your_env_name python=3.8
   conda activate your_env_name


streamlit
pymongo
pandas
huggingface_hub
langchain
langchain-community

pip install -r requirements.txt

streamlit run app.py
