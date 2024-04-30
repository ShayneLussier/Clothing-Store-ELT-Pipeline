import json
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

# -------------------- FUNCTIONS -------------------- #

def fetch_product_data(key='products/products.csv', bucket_name='data-pipeline-repo', **kwargs):
    s3_hook = S3Hook(aws_conn_id='aws_airflow')
    csv_file = s3_hook.get_key(key, bucket_name).get()['Body'].read().decode('utf-8') # Returns the file as a string

    data = csv_file.strip().split('\n')
    headers = data[0].split(',')

    result = []
    for row in data[1:]:
        values = row.split(',')
        row_dict = {}
        for header, value in zip(headers, values):
            if header == 'PrimaryColor' and (value.strip('"') == '' or value.strip('"') == 'NA'):
                row_dict[header] = 'NA'
            else:
                row_dict[header] = value.strip('"')
        result.append(row_dict)
    return result

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = [json.loads(line) for line in file if line.strip()]
    return json_data

def append_to_json(file_path, data):
    with open(file=file_path, mode='a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        f.write('\n')

def upload_to_s3(file_path="transactions.json", key='transactions/transactions.json', bucket_name='data-pipeline-repo', **kwargs):
    s3_hook = S3Hook(aws_conn_id='aws_airflow')
    
    # Upload the data to S3
    s3_hook.load_file(
        filename=file_path,
        key=key,
        bucket_name=bucket_name,
        replace=True
    )