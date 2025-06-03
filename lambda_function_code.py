import json 
import csv
import io
import boto3 # AWS SDK for Python. Available in Lambda by default.
from datetime import datetime
from collections import defaultdict

# Initialize S3 client once here, so Lambda can reuse it if the container is warm
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}") # Good for debugging to see what triggered Lambda

    # --- 1. Get and Validate Date from Event ---
    try:
        processing_date_str = event['date']
        # Quick check to see if the date string looks like YYYY-MM-DD
        datetime.strptime(processing_date_str, '%Y-%m-%d')
    except (KeyError, ValueError) as e:
        print(f"Error: Missing or invalid 'date' in event: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "Missing or invalid 'date' in event. Expected YYYY-MM-DD format."})
        }

    # --- 2. Construct S3 File Paths ---
    try:
        date_obj = datetime.strptime(processing_date_str, '%Y-%m-%d')
        year = str(date_obj.year)
        month = f"{date_obj.month:02d}"
        day = f"{date_obj.day:02d}"   
    except ValueError: 
        print(f"Error: Invalid date format '{processing_date_str}'") # Should have been caught earlier
        return {'statusCode': 400, 'body': json.dumps({'error': "Invalid date format."})}

    # !!! REPLACE 'YOUR_BUCKET_NAME' with your actual S3 bucket name !!!
    bucket_name = 'lonelys-fintech-assignemnt' 

    # Input file: s3://YOUR_BUCKET_NAME/2024/05/15/trades.csv
    input_s3_key = f"{year}/{month}/{day}/trades.csv"

    # Output file: s3://YOUR_BUCKET_NAME/2024/05/15/analysis_2024-05-15.csv
    output_s3_key = f"{year}/{month}/{day}/analysis_{processing_date_str}.csv"

    print(f"Input S3 key: s3://{bucket_name}/{input_s3_key}")
    print(f"Output S3 key: s3://{bucket_name}/{output_s3_key}")

    # --- 3. Read trades.csv from S3 ---
    trade_records = []
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=input_s3_key)
        # The file content comes as a stream, so read it and decode from bytes to string
        csv_content = response['Body'].read().decode('utf-8')
                
        # Use io.StringIO to make the string content behave like a file for csv.DictReader
        csvfile = io.StringIO(csv_content)
        reader = csv.DictReader(csvfile)
        for row in reader:
            trade_records.append(row)
        
        if not trade_records:
            print(f"No records found in {input_s3_key} or file is empty.") # If file is empty, analysis will be empty, which is fine.
            pass

    except s3_client.exceptions.NoSuchKey:
        print(f"Error: Input file not found at s3://{bucket_name}/{input_s3_key}")
        return {
            'statusCode': 404,
            'body': json.dumps({'error': f"Input file not found: {input_s3_key}"})
        }
    except Exception as e:
        print(f"Error reading from S3: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Error reading input S3 file: {str(e)}"})
        }

    # --- 4. Process Data: Calculate Volume and Average Price ---
    # Using defaultdict to easily sum up values for each stock ticker
    # {'TICKER': {'total_volume': X, 'sum_price_x_quantity': Y, 'count_trades_for_avg_price': Z}}
    stock_analysis = defaultdict(lambda: {'total_volume': 0, 'sum_price_x_quantity': 0.0, 'count_trades_for_avg_price': 0})

    for record in trade_records:
        try:
            ticker = record['ticker']
            price = float(record['price'])
            quantity = int(record['quantity'])

            stock_analysis[ticker]['total_volume'] += quantity
            # For weighted average price: sum of (price * quantity)
            stock_analysis[ticker]['sum_price_x_quantity'] += price * quantity
            # Denominator for weighted average: sum of quantities
            stock_analysis[ticker]['count_trades_for_avg_price'] += quantity

        except (ValueError, KeyError) as e:
            # If a row in the CSV is messed up (e.g., price isn't a number), skip it
            print(f"Skipping malformed record: {record}. Error: {e}")
            continue 
    
    # --- 5. Prepare Analysis Results for CSV Output ---
    analysis_output_data = [] 
    analysis_output_data.append(['ticker', 'total_volume', 'average_price'])
    

    for ticker, data in stock_analysis.items():
        average_price = 0
        if data['count_trades_for_avg_price'] > 0: # Avoid division by zero if no trades for a ticker
            average_price = data['sum_price_x_quantity'] / data['count_trades_for_avg_price']
        
        analysis_output_data.append([
            ticker,
            data['total_volume'],
            f"{average_price:.2f}" # Format price to 2 decimal places, e.g., "150.75"
        ])
    
    print(f"Analysis results: {analysis_output_data}")
    
    # --- 6. Write Analysis Results back to S3 ---
    try:
        # Create the CSV content in memory as a string
        output_csvfile = io.StringIO()
        writer = csv.writer(output_csvfile)
        writer.writerows(analysis_output_data)
        
        # S3 needs bytes, so convert the string to bytes (UTF-8 encoded)
        output_csv_content_bytes = output_csvfile.getvalue().encode('utf-8')
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=output_s3_key,
            Body=output_csv_content_bytes,
            ContentType='text/csv'
        )
        print(f"Successfully wrote analysis to s3://{bucket_name}/{output_s3_key}")

    except Exception as e:
        print(f"Error writing to S3: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Error writing output S3 file: {str(e)}"})
        }

    # --- 7. Return Success Response ---
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f"Trade analysis complete for {processing_date_str}. Output at s3://{bucket_name}/{output_s3_key}",
            'input_file': input_s3_key,
            'output_file': output_s3_key,
            'records_processed': len(trade_records),
            'analysis_summary_count': len(analysis_output_data) -1 
        })
    }