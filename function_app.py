import azure.functions as func
from azure.data.tables import TableClient
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="SyncData")
def SyncData(req: func.HttpRequest) -> func.HttpResponse:
    # Use an Environment Variable for security (we will set this in Azure later)
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    
    try:
        req_body = req.get_json()
        table_client = TableClient.from_connection_string(conn_str, table_name="ShowReports")

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
        return func.HttpResponse(json.dumps({"status": "Success"}), status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
