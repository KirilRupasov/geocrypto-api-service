import os
import psycopg2
import json

def get_latest_trends(cur, search_term):
    query = """
        SELECT DISTINCT ON (country) id, country, search_term, score, trend_date
        FROM trends
        WHERE search_term = %s
        ORDER BY country, trend_date DESC
    """
    cur.execute(query, (search_term,))
    rows = cur.fetchall()
    return [
        {
            'id': row[0],
            'country': row[1],
            'search_term': row[2],
            'score': row[3],
            'trend_date': row[4].isoformat()
        }
        for row in rows
    ]

def get_trends_last24h(cur, search_term):
    query = """
        SELECT id, country, search_term, score, trend_date
        FROM trends
        WHERE search_term = %s AND trend_date >= (NOW() - INTERVAL '24 HOURS')
        ORDER BY trend_date DESC
    """
    cur.execute(query, (search_term,))
    rows = cur.fetchall()
    return [
        {
            'id': row[0],
            'country': row[1],
            'search_term': row[2],
            'score': row[3],
            'trend_date': row[4].isoformat()
        }
        for row in rows
    ]

def lambda_handler(event, context):
    params = event.get('queryStringParameters', {})
    search_term = params.get('search_term')
    path = event.get('path', '')
    if not search_term:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'search_term parameter is required'})
        }

    conn = psycopg2.connect(
        host=os.environ['PG_HOST'],
        database=os.environ['PG_DB'],
        user=os.environ['PG_USER'],
        password=os.environ['PG_PASSWORD'],
        port=os.environ.get('PG_PORT', 5432)
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

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
