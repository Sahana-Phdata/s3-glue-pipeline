import sys
import re
import boto3
import pandas as pd
from io import BytesIO
from awsglue.utils import getResolvedOptions


def main():
    # Get parameters passed by the Glue job
    args = getResolvedOptions(
        sys.argv,
        ["INPUT_BUCKET", "OUTPUT_BUCKET"]
    )

    input_bucket = args["INPUT_BUCKET"]
    output_bucket = args["OUTPUT_BUCKET"]

    input_key = "input/movies.csv"
    output_key = "output/movies_transformed.csv"

    s3 = boto3.client("s3")

    # Read input CSV from S3
    response = s3.get_object(
        Bucket=input_bucket,
        Key=input_key
    )

    df = pd.read_csv(
        BytesIO(response["Body"].read())
    )

    # Validate required columns
    required_columns = [
        "movieId",
        "title",
        "genres"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Validate movieId
    df["movieId"] = pd.to_numeric(
        df["movieId"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["movieId"]
    )

    df["movieId"] = df["movieId"].astype(int)

    # Clean title
    df["title"] = (
        df["title"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Extract year from title
    df["year"] = df["title"].str.extract(
        r"\((\d{4})\)"
    )

    # Remove year from title
    # and convert title to uppercase
    df["title"] = (
        df["title"]
        .str.replace(
            r"\s*\(\d{4}\)\s*$",
            "",
            regex=True
        )
        .str.strip()
        .str.upper()
    )

    # Clean genres
    df["genres"] = (
        df["genres"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Select final columns
    df = df[
        [
            "movieId",
            "title",
            "year",
            "genres"
        ]
    ]

    # Rename movieId
    df = df.rename(
        columns={
            "movieId": "movie_id"
        }
    )

    # Convert DataFrame to CSV
    csv_data = df.to_csv(
        index=False
    )

    # Write transformed data
    # to the separate output bucket
    s3.put_object(
        Bucket=output_bucket,
        Key=output_key,
        Body=csv_data.encode("utf-8"),
        ContentType="text/csv"
    )

    print(
        "Transformation completed successfully."
    )

    print(
        f"Input: s3://{input_bucket}/{input_key}"
    )

    print(
        f"Output: s3://{output_bucket}/{output_key}"
    )


if __name__ == "__main__":
    main()