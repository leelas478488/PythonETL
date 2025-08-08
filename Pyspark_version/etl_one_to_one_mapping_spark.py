from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
import os
import platform

# 1. Initialize SparkSession with fix for Windows native I/O issue
builder = SparkSession.builder.appName("OneToOneETL")

# Apply Windows-specific configs
if platform.system().lower() == "windows":
    builder = builder \
        .config("spark.hadoop.hadoop.native.lib", "false") \
        .config("spark.hadoop.fs.file.impl.disable.cache", "true")

spark = builder.getOrCreate()

# 2. Define file paths
input_path = r"C:/Users/91888/PycharmProjects/PythonETL/data/input/employees.csv"
# IMPORTANT: For Spark CSV output, give a folder path, not a single file
output_path = r"C:/Users/91888/PycharmProjects/PythonETL/data/output/employees_transformed"

# 3. Check input file exists
if not os.path.exists(input_path):
    raise FileNotFoundError(f"Input file not found: {input_path}")

# 4. Create output directory if it doesn't exist (Spark will overwrite it anyway)
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# 5. Extract
df = spark.read.option("header", "true").option("inferSchema", "true").csv(input_path)

# 6. Transform — filter high salaries
df_filtered = df.filter(col("salary") > 70000)

# 7. Rename columns and add processed date
df_renamed = df_filtered \
    .withColumnRenamed("emp_id", "employee_id") \
    .withColumnRenamed("emp_name", "employee_name") \
    .withColumnRenamed("department", "dept_name") \
    .withColumnRenamed("salary", "monthly_salary") \
    .withColumn("processed_date", current_timestamp())

df_renamed.show()
# 8. Load — Spark will create multiple part-*.csv files inside the folder
#df_renamed.write.mode("overwrite").option("header", "true").csv(output_path)

# 9. Done
print("ETL completed. Transformed data written to folder:")
print(output_path)

# 10. Stop Spark session
spark.stop()
