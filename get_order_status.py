import json
import boto3
import time

def lambda_handler(event, context):
    print("Event received:", json.dumps(event, indent=2))
    
    # Extract parameters from the event
    parameters = event.get('parameters', [])
    
    def get_param_value(param_name):
        for param in parameters:
            if param.get('name') == param_name:
                return param.get('value', '')
        return ''
    
    # Get order_id
    order_id = get_param_value("order_id")

    # Validate the parameter
    if not order_id:
        raise ValueError("The order_id parameter must not be empty.")
    
    # Redshift connection details
    CLUSTER_IDENTIFIER = 'aws-proserve-insights-redshift-cluster-alpha'
    DATABASE = 'quasar'
    DB_USER = 'veepooja'  # Replace with your actual Redshift username
    
    # Initialize Redshift Data API client
    redshift_client = boto3.client('redshift-data')

    try:
        print("Executing Redshift query...")
        # Execute query
        response = redshift_client.execute_statement(
            ClusterIdentifier=CLUSTER_IDENTIFIER,
            Database=DATABASE,
            DbUser=DB_USER,
            Sql="""
                SELECT 
                    order_status,
                    order_tracking_id
                FROM temp_workspace.order_tracking_test
                WHERE order_id = :order_id
                LIMIT 1;
            """,
            Parameters=[{'name': 'order_id', 'value': order_id}]  # ✅ Include the 'name' field
        )

        # Get query execution ID
        query_id = response['Id']
        
        # Wait for query to complete
        while True:
            # Get query result status
            status_response = redshift_client.describe_statement(Id=query_id)
            status = status_response['Status']
            
            if status == 'FINISHED':
                # Get query results
                result = redshift_client.get_statement_result(Id=query_id)
                
                # Process the results
                records = result['Records']
                if records:
                    # Extract data from first record
                    order_status = records[0][0]['stringValue']
                    order_tracking_id = records[0][1]['stringValue']

                    # Response for Bedrock Agent
                    responseBody = {
                        "TEXT": {
                            "body": f"Your order status is '{order_status}' and you can track your order here: {order_tracking_id}."
                        }
                    }
                else:
                    responseBody = {
                        "TEXT": {
                            "body": f"No order information found for order ID {order_id}."
                        }
                    }
                break
            
            elif status in ['FAILED', 'ABORTED']:
                raise Exception(f"Query failed with status: {status}")
            
            # Wait before checking again
            time.sleep(0.5)
    
    except Exception as e:
        print(f"Error querying Redshift: {str(e)}")
        responseBody = {
            "TEXT": {
                "body": f"Error retrieving order information: {str(e)}"
            }
        }
    
    # Prepare the action response for Bedrock Agent
    action_response = {
        'actionGroup': event.get('actionGroup', ''),
        'function': event.get('function', ''),
        'functionResponse': {
            'responseBody': responseBody
        }
    }
    
    # Construct the full response
    lambda_response = {
        'response': action_response,
        'messageVersion': event.get('messageVersion', '1.0')
    }
    
    print("Response:", json.dumps(lambda_response, indent=2))
    return lambda_response

