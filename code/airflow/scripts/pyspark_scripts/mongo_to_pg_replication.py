import argparse

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import col, to_json

def process_nested_columns(df):
    """Конвертирует вложенные структуры в JSON строки"""
    for field in df.schema:
        if isinstance(field.dataType, (StructType, ArrayType, MapType)):
            df = df.withColumn(field.name, to_json(col(field.name)))
    return df

def replicate_collection(
    mongo_uri: str,
    pg_uri: str,
    pg_driver: str,
    collection: str,
    pg_table_name: str,
    schema: str = "stg"
) -> None:
    """
    Реплицирует данные из коллекции MongoDB в таблицу PostgreSQL с полной перезаписью.
    
    Args:
        mongo_uri (str): URI подключения к MongoDB
        pg_url (str): JDBC URL для PostgreSQL
        pg_driver (str): Класс драйвера PostgreSQL
        collection (str): Название коллекции MongoDB
        pg_table_name (str): Название таблицы в PG
        schema (str): Схема в PostgreSQL (stg)
    """
    
    spark = (
        SparkSession.builder
        .appName(f"MongoDB_to_PG_{collection}")
        .config("spark.mongodb.read.connection.uri", mongo_uri)
        .config("spark.sql.jsonGenerator.ignoreNullFields", "false")
        .getOrCreate()
    )

    try:       
        mongo_df = (
            spark.read
            .format("mongodb")
            .option("database", mongo_uri.split('/')[-1])
            .option("collection", collection)
            .load()
        )

        # Удаление системного _id
        mongo_df = mongo_df.drop("_id") if "_id" in mongo_df.columns else mongo_df
        
        # Обработка вложенных структур
        processed_df = process_nested_columns(mongo_df)

        # Запись в PostgreSQL
        (
            processed_df.write
            .format("jdbc")
            .option("driver", pg_driver)
            .option("url", pg_uri)
            .option("dbtable", f"{schema}.{pg_table_name}")
            .option("truncate", "true")
            .option("stringtype", "unspecified")
            .mode("overwrite")
            .save()
        )
            
    except Exception as e:
        spark.stop()
        raise RuntimeError(f"Error processing {collection}: {str(e)}")

    spark.stop()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mongo_uri", type=str, required=True)
    parser.add_argument("--pg_uri", type=str, required=True)
    parser.add_argument("--pg_driver", type=str, required=True)
    parser.add_argument("--collection", type=str, required=True)
    parser.add_argument("--pg_table_name", type=str, required=True)
    parser.add_argument("--schema", type=str, default="stg")
    
    args = parser.parse_args()
    
    try:
        replicate_collection(
            args.mongo_uri,
            args.pg_uri,
            args.pg_driver,
            args.collection,
            args.pg_table_name,
            args.schema
        )
    except Exception as e:
        print(f"Critical error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()