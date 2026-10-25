"""Sample PySpark ETL job: validates rows and reports rejected/clean counts."""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp

def run_etl():
    spark = SparkSession.builder.appName("self-healing-agent-sample-etl").getOrCreate()
    df = spark.createDataFrame([(1,"Asha",1200.0),(2,"Rohan",850.0),(3,None,500.0)],
                               ["customer_id","customer_name","amount"])
    invalid = df.filter(col("customer_id").isNull() | col("customer_name").isNull() | (col("amount") < 0))
    clean = (df.filter(col("customer_id").isNotNull() & col("customer_name").isNotNull() & (col("amount") >= 0))
             .withColumn("processed_at_utc", current_timestamp()))
    counts={"input_rows":df.count(),"rejected_rows":invalid.count(),"clean_rows":clean.count()}
    print(counts)
    clean.show(truncate=False)
    return counts

if __name__ == "__main__":
    run_etl()
