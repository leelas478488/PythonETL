from openai import OpenAI
import os

# How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
# Alternatively in a Databricks notebook you can use this:
# DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

client = OpenAI(
    api_key=DATABRICKS_TOKEN,
    base_url="https://dbc-03a0e5bf-091a.cloud.databricks.com/serving-endpoints"
)

response = client.chat.completions.create(
    model="databricks-gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "You will be provided with a document and asked to summarize it.\n\nSummarize the following document:\n\nWith origins in academia and the open source community, Databricks was founded in 2013 by the original creators of Apache Spark™, Delta Lake and MLflow. As the world's first and only lakehouse platform in the cloud, Databricks combines the best of data warehouses and data lakes to offer an open and unified platform for data and AI.\n\nToday, more than 9,000 organizations worldwide — including ABN AMRO, Condé Nast, Regeneron and Shell — rely on Databricks to enable massive-scale data engineering, collaborative data science, full-lifecycle machine learning and business analytics.\n\nHeadquartered in San Francisco, with offices around the world and hundreds of global partners, including Microsoft, Amazon, Tableau, Informatica, Capgemini and Booz Allen Hamilton, Databricks is on a mission to simplify and democratize data and AI, helping data teams solve the world's toughest problems."
        }
    ]
)

print(response.choices[0].message.content)