from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
import os
spark._jsc.hadoopConfiguration().set("hadoop.check.native.io", "false")

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("OneToOneETL") \
    .getOrCreate()
spark.sparkContext._jvm.org.apache.hadoop.fs.FileSystem.get(
    spark._jsc.hadoopConfiguration()
).set(
    "spark.hadoop.io.native.lib.available", "false"
)

# Define file paths
input_path = "C:/Users/91888/PycharmProjects/PythonETL/data/input/employees.csv"
output_path = "C:/Users/91888/PycharmProjects/PythonETL/data/output/employees_transformed.csv"

# Check input file exists
if not os.path.exists(input_path):
    raise FileNotFoundError(f"Input file not found: {input_path}")

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# 1. Extract
df = spark.read.option("header", "true").option("inferSchema", "true").csv(input_path)

# 2. Transform
df_filtered = df.filter(col("salary") > 70000)

# Rename columns using withColumnRenamed
df_renamed = df_filtered \
    .withColumnRenamed("emp_id", "employee_id") \
    .withColumnRenamed("emp_name", "employee_name") \
    .withColumnRenamed("department", "dept_name") \
    .withColumnRenamed("salary", "monthly_salary") \
    .withColumn("processed_date", current_timestamp())

# 3. Load (append if file exists, else create)
if os.path.exists(output_path):
    df_renamed.write.mode("append").option("header", "false").csv(output_path)
    print(df_renamed)
    print(f"Appended to existing file: {output_path}")
else:
    df_renamed.write.mode("overwrite").option("header", "true").csv(output_path)
    print(df_renamed)
    print(f"Created new output file: {output_path}")

spark.stop()
