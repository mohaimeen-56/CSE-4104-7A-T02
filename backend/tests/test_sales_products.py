from datetime import date

def test_list_sales_pagination(client, viewer_headers):
    response = client.get('/api/sales?page=1&page_size=2', headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert len(data['data']) == 2
    assert data['pagination']['total'] == 3
    assert data['pagination']['total_pages'] == 2

def test_search_and_filter_sales(client, viewer_headers):
    response = client.get('/api/sales?category=Furniture', headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data['data']) == 1
    assert data['data'][0]['product']['category'] == 'Furniture'

    response_search = client.get('/api/sales?search=Laptop', headers=viewer_headers)
    assert response_search.status_code == 200
    assert len(response_search.json()['data']) == 1

def test_create_sale_rbac(client, viewer_headers, manager_headers):
    sale_payload = {
        'product_id': 1,
        'region_id': 1,
        'quantity': 3,
        'unit_price': 1200.0,
        'sale_date': '2026-09-05'
    }
    # Viewer cannot create sale
    res_viewer = client.post('/api/sales', json=sale_payload, headers=viewer_headers)
    assert res_viewer.status_code == 403

    # Manager can create sale
    res_manager = client.post('/api/sales', json=sale_payload, headers=manager_headers)
    assert res_manager.status_code == 201
    created = res_manager.json()['data']
    assert created['total_price'] == 3600.0

def test_update_sale(client, manager_headers):
    update_payload = {
        'quantity': 4,
        'unit_price': 1200.0
    }
    response = client.put('/api/sales/1', json=update_payload, headers=manager_headers)
    assert response.status_code == 200
    data = response.json()['data']
    assert data['quantity'] == 4
    assert data['total_price'] == 4800.0

def test_delete_sale_admin_only(client, manager_headers, admin_headers):
    # Manager cannot delete sale
    res_mgr = client.delete('/api/sales/1', headers=manager_headers)
    assert res_mgr.status_code == 403

    # Admin can delete sale
    res_adm = client.delete('/api/sales/1', headers=admin_headers)
    assert res_adm.status_code == 200
