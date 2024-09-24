import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
from huggingface_hub import InferenceClient
from langchain.prompts import PromptTemplate
import json
import os
import re

load_dotenv()

# Function to load CSV data into MongoDB
def read_csv(file):
    df = pd.read_csv(file)
    client = MongoClient('mongodb://localhost:27017/')
    db = client['my_database']
    collection = db['collection_1']
    data = df.to_dict(orient='records')
    collection.insert_many(data)
    st.success("Data loaded into MongoDB successfully!")

# Function to clean the generated query by keeping only the content between the first and last curly braces
def keep_first_last_curly(json_string):
    """
    This function retains only the content inside the first and last curly brackets of the provided JSON string.
    
    Args:
    json_string (str): Input JSON string which might have extra curly braces or content.

    Returns:
    str: Cleaned JSON string with only the first and last curly brackets content.
    """
    try:
        # Use regex to extract content between the first and last curly braces
        cleaned_json = re.search(r'\{(.*)\}', json_string, re.DOTALL).group(0)
        return cleaned_json
    except Exception as e:
        print(f"Error processing the JSON string: {e}")
        return None

# Function to fix improperly formatted MongoDB operators in JSON
def fix_query_format(query_condition):
    # Ensure all MongoDB operators like $gt, $gte are enclosed in double quotes
    cleaned_query = re.sub(r'(\$[a-zA-Z]+)', r'"\1"', query_condition)
    
    # Further clean double-quote escaping issues
    cleaned_query = cleaned_query.replace('""', '"')
    return cleaned_query

# Function to generate MongoDB query using Hugging Face InferenceClient
def get_llm_response(input_column, input_condition):
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    if not token:
        st.error("Hugging Face API token not found. Please set the 'HUGGINGFACEHUB_API_TOKEN' environment variable.")
        return None

    # Initialize the Hugging Face client
    client = InferenceClient("microsoft/Phi-3-mini-4k-instruct", token=token)

    # Define the prompt template for MongoDB query generation
    template = """

        You are a MongoDB query generator responsible for creating correct query conditions.

        Please follow these guidelines when generating the MongoDB query condition:
        1. Ensure that all MongoDB operators like $and, $or, $gt, $lt, $gte, $lte, $in are enclosed in double quotes.
        2. Dates must be in ISODate format (e.g., ISODate('YYYY-MM-DDTHH:MM:SSZ')).
        3. The query condition should be a valid JSON format that MongoDB can interpret directly.
        4. Do not include any additional comments, text, or explanations.
        5. Avoid including invalid or out-of-place fields like 'Sort' in the query condition itself.
        6. Only return the query condition inside curly brackets, with no extra text outside.

        Example schema for reference:
        - ProductID, ProductName, Category, Price, Rating, ReviewCount, Stock, Discount, Brand, LaunchDate.

        Your task:
        Generate a MongoDB query condition using the following inputs:
        - Column name: '{input_column}'
        - Condition: '{input_condition}'

        Ensure the output is valid JSON and follows MongoDB's syntax rules.


    """

    prompt = PromptTemplate(input_variables=["input_column", "input_condition"], template=template)

    try:
        # Format the prompt with input column and condition
        formatted_prompt = prompt.format(input_column=input_column, input_condition=input_condition)
        
        # Fetch the response from the model
        response = ""
        for message in client.chat_completion(
                messages=[{'role': 'user', 'content': formatted_prompt}],
                max_tokens=500,
                stream=True,
        ):
            response += message.choices[0].delta.content  # Collect the response parts

        # Clean the generated query using the function to keep only the first and last curly brackets
        cleaned_query = keep_first_last_curly(response.strip())
        
        # Fix MongoDB query format for operators
        fixed_query = fix_query_format(cleaned_query)
        
        return fixed_query
    except Exception as e:
        st.error(f"Error generating query: {e}")
        return None
    
def execute_query(query_condition):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['my_database']
    collection = db['collection_1']

    try:
        # Convert the condition string (in JSON format) to a Python dictionary
        query_dict = json.loads(query_condition)  
        
        # Execute the query to find matching documents
        result = collection.find(query_dict)
        
        # Convert the result to a list of documents
        result_list = list(result)
        
        # Convert the MongoDB ObjectId to string for compatibility
        for document in result_list:
            if '_id' in document:
                document['_id'] = str(document['_id'])
        
        # Create a DataFrame from the result list
        result_df = pd.DataFrame(result_list)
        
        return result_df

    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None


# Streamlit App
st.set_page_config(page_title="Query Generator", layout="centered")
st.header("CSV to MongoDB Query Generator")

# Upload CSV file
file = st.file_uploader("Upload a CSV file", type=['csv'])
if file:
    read_csv(file)

# Input for query generation
input_column = st.text_input('Enter the column name')
input_condition = st.text_input('Enter the condition')

# Button to generate and execute query
if st.button("Generate and Execute Query"):
    query_condition = get_llm_response(input_column, input_condition)
    if query_condition:
        st.success(f"Generated Query is : {query_condition}")
        # Save the generated query to a text file
        with open("Queries_generated.txt", "a") as file:
            file.write(f"Input Condition: {input_condition}\n")
            file.write(f"Generated Query: {query_condition}\n\n")

    else:
        st.warning("Failed to generate a query.")
        
        # Execute the query and get the result
    result = execute_query(query_condition)
    
    # Check if the DataFrame is empty
    if result is not None and not result.empty:
        st.write("Query Result:")
        result_df = pd.DataFrame(result)
        st.write(result_df)
        
        # Option to save as CSV
        if st.button("Save as CSV"):
            csv_data = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download CSV", data=csv_data, file_name="output.csv", mime='text/csv')
    else:
        st.warning("No results found.")
else:
    st.warning("Failed to generate a query.")
