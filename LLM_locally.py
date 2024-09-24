import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from pymongo import MongoClient
import pandas as pd
import json
import re
# Function to load CSV data into MongoDB
def read_csv(file):
    df = pd.read_csv(file)
    client = MongoClient('mongodb://localhost:27017/')
    db = client['my_database']
    collection = db['collection_1']
    data = df.to_dict(orient='records')
    collection.insert_many(data)
    st.success("Data loaded into MongoDB successfully!")

# Function to generate MongoDB query using LLM
def get_llm_response(input_condition):
    template = """
        Generate a MongoDB query condition for the following user input:
        '{input_condition}' applied on the data stored in mongodb database.

        The query should use valid MongoDB syntax (find or aggregation pipeline) and should work with the following schema:
        
        - **ProductID**: Unique identifier for the product.
        - **ProductName**: Name of the product.
        - **Category**: Category of the product.
        - **Price**: Price of the product.
        - **Rating**: Rating of the product.
        - **ReviewCount**: Number of reviews for the product.
        - **Stock**: Quantity of the product in stock.
        - **Discount**: Discount applied to the product.
        - **Brand**: The brand of the product.
        - **LaunchDate**: Date the product was launched.

        The query should be in valid MongoDB syntax, and must use proper MongoDB operators like $and, $or, $gt, etc. 
        Only return the condition part of the query in JSON format, nothing else.

    """

    # Load the local LLaMA model
    llm = CTransformers(model='models\llama-2-7b.ggmlv3.q8_0.bin',
                        model_type='llama',
                        config={'max_new_tokens': 256, 'temperature': 0.01})

    prompt = PromptTemplate(input_variables=["input_condition"], template=template)

    try:
        response = llm.invoke(prompt.format(input_condition=input_condition))
        response = response.strip()  # Remove unnecessary spaces
        return response
    except Exception as e:
        st.error(f"Error generating query: {e}")
        return None

# Function to clean the generated query
def clean_query(query_condition):
    # Remove unwanted characters and ensure valid JSON
    clean_query = re.sub(r'[^a-zA-Z0-9:,"{}\[\]$.\- ]', '', query_condition)
    return clean_query

# Function to execute MongoDB query
def execute_query(query_condition):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['my_database']
    collection = db['collection_1']

    try:
        # Clean the query condition and convert it into a Python dictionary
        clean_condition = clean_query(query_condition)
        query_dict = json.loads(clean_condition)
        
        # Execute the query
        result = collection.find(query_dict)
        return list(result)
    except json.JSONDecodeError:
        st.error("Generated query is not a valid JSON.")
        return None
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None

# Function to save generated queries to a file
def save_query_to_file(input_condition, query_condition):
    try:
        with open("Queries_generated.txt", "a") as file:
            file.write(f"Condition: {input_condition}\n")
            file.write(f"Query generated by Model: {query_condition}\n\n")
    except Exception as e:
        st.error(f"Error saving query to file: {e}")

# Streamlit App
st.set_page_config(page_title="Query Generator", layout="centered")
st.header("CSV to MongoDB Query Generator")

# Upload CSV file
file = st.file_uploader("Upload a CSV file", type=['csv'])
if file:
    read_csv(file)

# Input for query generation
input_condition = st.text_input('Enter the condition')

# Button to generate and execute query
if st.button("Generate and Execute Query"):
    query_condition = get_llm_response(input_condition)
    if query_condition:
        st.success(f"Generated Query Condition: {query_condition}")
        
        # Save the query to a file
        save_query_to_file(input_condition, query_condition)
        
        # Execute the query
        result = execute_query(query_condition)
        
        if result:
            st.write("Query Result:")
            result_df = pd.DataFrame(result)
            st.write(result_df)
            
            # Option to save as CSV
            if st.button("Save as CSV"):
                csv_data = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="Download CSV", data=csv_data, file_name="output.csv", mime='text/csv')
    else:
        st.warning("Failed to generate a query.")