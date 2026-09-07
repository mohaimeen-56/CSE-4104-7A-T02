def test_analytics_summary_kpis(client, viewer_headers):
    response = client.get('/api/analytics/summary', headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()['data']
    assert data['total_orders'] == 3
    assert data['total_revenue'] == 2675.0

def test_analytics_overview(client, viewer_headers):
    response = client.get('/api/analytics/overview', headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()['data']
    assert 'kpis' in data
    assert 'revenue_trend' in data
    assert 'sales_by_category' in data
    assert 'sales_by_region' in data

def test_ai_insights_generation(client, viewer_headers):
    payload = {'period': 'all_time'}
    response = client.post('/api/ai/insights', json=payload, headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()['data']
    assert 'summary_text' in data
    assert len(data['summary_text']) > 10
    assert 'recommendations' in data

def test_ai_revenue_forecast(client, viewer_headers):
    response = client.get('/api/ai/forecast', headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()['data']
    assert 'predicted_revenue' in data
    assert 'historical_months' in data
    assert 'status' in data

def test_ai_anomaly_detection(client, viewer_headers):
    response = client.get('/api/ai/anomalies', headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()['data']
    assert isinstance(data, list)

def test_ai_chatbot_conversation_greeting(client, viewer_headers):
    payload = {'message': 'Hello, who are you?'}
    response = client.post('/api/ai/chat', json=payload, headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()['data']
    assert data['route'] == 'conversation'
    assert 'SalesIQ' in data['ai_response']

def test_ai_chatbot_conversation_definition(client, viewer_headers):
    payload = {'message': 'What is AOV?'}
    response = client.post('/api/ai/chat', json=payload, headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()['data']
    assert data['route'] == 'conversation'
    assert 'Average Order Value' in data['ai_response']

def test_ai_chatbot_analytics_query(client, viewer_headers):
    payload = {'message': 'Show me sales performance for this month'}
    response = client.post('/api/ai/chat', json=payload, headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()['data']
    assert data['route'] == 'analytics'
