# import azure.functions as func
# from azure.data.tables import TableClient
# import json
# import os

# app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# @app.route(route="syncdata", methods=["GET", "POST"])
# def syncdata(req: func.HttpRequest) -> func.HttpResponse:
#     conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    
#     if not conn_str:
#         return func.HttpResponse("Error: Storage Connection String missing.", status_code=500)
        
#     table_client = TableClient.from_connection_string(conn_str, table_name="ShowReports")

#     # --- FETCH DATA (GET) ---
#     if req.method == "GET":
#         try:
#             entities = table_client.list_entities()
#             reports = []
#             for entity in entities:
#                 reports.append({
#                     'date': entity.get('PartitionKey'),
#                     'theater': entity.get('RowKey', '').split('_')[0].replace("-", " "),
#                     'screen': entity.get('RowKey', '').split('_')[1] if '_' in entity.get('RowKey', '') else "Screen",
#                     'city': entity.get('City'),
#                     'movie': entity.get('Movie'),
#                     'time': entity.get('Time'),
#                     'slot': entity.get('Slot'),
#                     'booked': int(entity.get('Booked', 0)),
#                     'total': int(entity.get('Total', 0))
#                 })
#             return func.HttpResponse(json.dumps(reports), mimetype="application/json")
#         except Exception as e:
#             return func.HttpResponse(f"Error: {str(e)}", status_code=500)

#     # --- SAVE DATA (POST) ---
#     elif req.method == "POST":
#         try:
#             data = req.get_json()
#             r_key = f"{data['theater']}_{data['screen']}_{data['time']}".replace(" ", "-")
            
#             entity = {
#                 'PartitionKey': data['date'],
#                 'RowKey': r_key,
#                 'City': data['city'],
#                 'Movie': data['movie'],
#                 'Time': data['time'],
#                 'Slot': data['slot'],
#                 'Booked': int(data['booked']),
#                 'Total': int(data['total'])
#             }
#             table_client.upsert_entity(mode='merge', entity=entity)
#             return func.HttpResponse(json.dumps({"status": "Success"}), mimetype="application/json")

import azure.functions as func
from azure.data.tables import TableClient
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# --- ROUTE 1: MOVIE DATA ---
@app.route(route="syncdata", methods=["GET", "POST"])
def syncdata(req: func.HttpRequest) -> func.HttpResponse:
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        return func.HttpResponse("Error: Storage Connection String missing.", status_code=500)
    
    table_client = TableClient.from_connection_string(conn_str, table_name="ShowReports")

    if req.method == "GET":
        try:
            entities = table_client.list_entities()
            reports = []
            for entity in entities:
                reports.append({
                    'date': entity.get('PartitionKey'),
                    'theater': entity.get('RowKey', '').split('_')[0].replace("-", " "),
                    'screen': entity.get('RowKey', '').split('_')[1] if '_' in entity.get('RowKey', '') else "Screen",
                    'city': entity.get('City'),
                    'movie': entity.get('Movie'),
                    'time': entity.get('Time'),
                    'slot': entity.get('Slot', 'N/A'),
                    'booked': int(entity.get('Booked', 0)),
                    'total': int(entity.get('Total', 0))
                })
            return func.HttpResponse(json.dumps(reports), mimetype="application/json")
        except Exception as e:
            return func.HttpResponse(f"Error: {str(e)}", status_code=500)

    elif req.method == "POST":
        try:
            data = req.get_json()
            r_key = f"{data['theater']}_{data['screen']}_{data['time']}".replace(" ", "-")
            entity = {
                'PartitionKey': data['date'],
                'RowKey': r_key,
                'City': data.get('city', 'Unknown'),
                'Movie': data['movie'],
                'Time': data['time'],
                'Slot': data.get('slot', 'N/A'),
                'Booked': int(data['booked']),
                'Total': int(data['total'])
            }
            table_client.upsert_entity(mode='merge', entity=entity)
            return func.HttpResponse(json.dumps({"status": "Success"}), mimetype="application/json")
        except Exception as e:
            return func.HttpResponse(f"Error: {str(e)}", status_code=500)

# --- ROUTE 2: USER MANAGEMENT ---
@app.route(route="manageusers", methods=["GET", "POST", "DELETE"])
def manageusers(req: func.HttpRequest) -> func.HttpResponse:
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    table_client = TableClient.from_connection_string(conn_str, table_name="DistriUsers")

    if req.method == "GET":
        entities = table_client.list_entities()
        users = [{"name": e.get('PartitionKey'), "pass": e.get('Password'), "role": e.get('Role')} for e in entities]
        return func.HttpResponse(json.dumps(users), mimetype="application/json")

    elif req.method == "POST":
        data = req.get_json()
        entity = {
            'PartitionKey': data['name'],
            'RowKey': data['name'], # Simple unique key
            'Password': data['pass'],
            'Role': data['role']
        }
        table_client.upsert_entity(mode='merge', entity=entity)
        return func.HttpResponse(json.dumps({"status": "User Updated"}), mimetype="application/json")
#         except Exception as e:
#             return func.HttpResponse(f"Error: {str(e)}", status_code=500)
