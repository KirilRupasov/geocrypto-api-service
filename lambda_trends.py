import os
import psycopg2
import json
import boto3

def get_db_secret(secret_name, region_name):
    client = boto3.client('secretsmanager', region_name=region_name)
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

def get_latest_trends(cur, search_term):
    query = """
        SELECT DISTINCT ON (country) country, trend_score
        FROM trends
        WHERE search_term = %s
        ORDER BY country, trend_date DESC
    """
    cur.execute(query, (search_term,))
    rows = cur.fetchall()
    result = {row[0]: row[1] for row in rows}
    return result

def get_trends_last24h(cur, search_term):
    query = """
        SELECT country, trend_score, trend_date
        FROM trends
        WHERE search_term = %s AND trend_date >= (NOW() - INTERVAL '24 HOURS')
        ORDER BY trend_date DESC
    """
    cur.execute(query, (search_term,))
    rows = cur.fetchall()
    # Map results to dictionary
    result = {row[0]: row[1] for row in rows}
    return result

def lambda_handler(event, context):
    path_params = event.get('pathParameters', {})
    search_term = path_params.get('crypto')
    path = event.get('path', '')
    if not search_term:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'search_term parameter is required'})
        }

    secrets = get_db_secret('database', 'eu-west-2')
    conn = psycopg2.connect(
        host=secrets['DB_HOST'],
        database=secrets['DB_NAME'],
        user=secrets['DB_USER'],
        password=secrets['DB_PASSWORD'],
        port=secrets.get('DB_PORT', 5432),
        sslmode='require'
    )
    cur = conn.cursor()

    if path.endswith('/latest'):
        results = get_latest_trends(cur, search_term)
    elif path.endswith('/last24h'):
        results = get_trends_last24h(cur, search_term)
    else:
        cur.close()
        conn.close()
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Invalid endpoint'})
        }

    cur.close()
    conn.close()

    print("RESULTS:", json.dumps(results))

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps(results)
    }
