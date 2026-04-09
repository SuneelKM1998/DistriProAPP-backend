import azure.functions as func
from azure.data.tables import TableClient
import json
import os

# Create the Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="syncdata", methods=["GET", "POST"])
def syncdata(req: func.HttpRequest) -> func.HttpResponse:
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    
    # Check if Connection String exists to prevent 500 errors
    if not conn_str:
        return func.HttpResponse("Error: Storage Connection String missing in Azure Settings.", status_code=500)
        
    table_client = TableClient.from_connection_string(conn_str, table_name="ShowReports")

    # FETCH DATA
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
                    'slot': entity.get('Slot'),
                    'booked': int(entity.get('Booked', 0)),
                    'total': int(entity.get('Total', 0))
                })
            return func.HttpResponse(json.dumps(reports), mimetype="application/json")
        except Exception as e:
            return func.HttpResponse(f"Fetch Error: {str(e)}", status_code=500)

    # SAVE DATA
    elif req.method == "POST":
        try:
            data = req.get_json()
            # Creating a unique RowKey to prevent duplicates
            r_key = f"{data['theater']}_{data['screen']}_{data['time']}".replace(" ", "-")
            
            entity = {
                'PartitionKey': data['date'],
                'RowKey': r_key,
                'City': data['city'],
                'Movie': data['movie'],
                'Time': data['time'],
                'Slot': data['slot'],
                'Booked': int(data['booked']),
                'Total': int(data['total'])
            }
            table_client.upsert_entity(mode='merge', entity=entity)
            return func.HttpResponse(json.dumps({"status": "Success"}), mimetype="application/json")
        except Exception as e:
            return func.HttpResponse(f"Save Error: {str(e)}", status_code=500)
