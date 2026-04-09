import azure.functions as func
from azure.data.tables import TableClient
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="SyncData", methods=["GET", "POST"])
def SyncData(req: func.HttpRequest) -> func.HttpResponse:
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    table_client = TableClient.from_connection_string(conn_str, table_name="ShowReports")

    # --- 1. FETCH DATA (GET) ---
    # This runs when you login or refresh the page
    if req.method == "GET":
        try:
            entities = table_client.list_entities()
            reports = []
            for entity in entities:
                reports.append({
                    "date": entity['PartitionKey'],
                    "theater": entity['RowKey'].split('_')[0].replace("_", " "),
                    "screen": entity['RowKey'].split('_')[1] if '_' in entity['RowKey'] else "Screen",
                    "time": entity.get('Time', ''),
                    "movie": entity.get('Movie', ''),
                    "city": entity.get('City', ''),
                    "booked": entity.get('Booked', 0),
                    "total": entity.get('Total', 0),
                    "slot": entity.get('Slot', '')
                })
            return func.HttpResponse(json.dumps(reports), mimetype="application/json", status_code=200)
        except Exception as e:
            return func.HttpResponse(f"Error fetching: {str(e)}", status_code=500)

    # --- 2. SAVE DATA (POST) ---
    # This runs when you click the "Sync" button
    elif req.method == "POST":
        try:
            req_body = req.get_json()
            
            # Create a unique ID for the show
            p_key = req_body.get('date')
            r_key = f"{req_body.get('theater')}_{req_body.get('screen')}_{req_body.get('time')}".replace(" ", "_")

            entity = {
                'PartitionKey': p_key,
                'RowKey': r_key,
                'City': req_body.get('city'),
                'Movie': req_body.get('movie'),
                'Time': req_body.get('time'),
                'Slot': req_body.get('slot'),
                'Booked': int(req_body.get('booked')),
                'Total': int(req_body.get('total'))
            }

            table_client.upsert_entity(mode='merge', entity=entity)
            return func.HttpResponse(json.dumps({"status": "Success"}), mimetype="application/json", status_code=200)
        except Exception as e:
            return func.HttpResponse(f"Error saving: {str(e)}", status_code=500)
