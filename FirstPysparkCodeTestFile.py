from pyspark.sql import SparkSession
import os
os.environ["PYSPARK_PYTHON"] = "C:/Users/91888/AppData/Local/Programs/Python/Python39/python.exe"  # Adjust this path!
os.environ["PYSPARK_DRIVER_PYTHON"] = "C:/Users/91888/AppData/Local/Programs/Python/Python39/python.exe"

# Create Spark session
spark = SparkSession.builder \
    .appName("LocalETLTest") \
    .getOrCreate()

# Create DataFrame from list
data = [("John", 28), ("Alice", 34), ("Bob", 45)]
df = spark.createDataFrame(data, ["name", "age"])

# Transform
df_filtered = df.filter(df.age > 30)

# Show result
df_filtered.show()

# Stop session
spark.stop()
