import json
import boto3
import time

def lambda_handler(event, context):
    """
    AWS Lambda handler function to process order tracking requests.
    Queries Redshift for order status and tracking information.
    
    Args:
        event (dict): Lambda event containing request parameters
        context (object): Lambda context object
    
    Returns:
        dict: Formatted response for Bedrock Agent
    """
    
    # Extract parameters from the event object
    parameters = event.get('parameters', [])
    
    def get_param_value(param_name):
        """
        Helper function to extract parameter value by name
        
        Args:
            param_name (str): Name of the parameter to find
            
        Returns:
            str: Parameter value if found, empty string otherwise
        """
        for param in parameters:
            if param.get('name') == param_name:
                return param.get('value', '')
        return ''
    
    # Get order_id from parameters
    order_id = get_param_value("order_id")

    # Validate order_id parameter
    if not order_id:
        raise ValueError("The order_id parameter must not be empty.")
    
    # Redshift connection configuration
    CLUSTER_IDENTIFIER = 'cluster_name'
    DATABASE = 'database_name'
    DB_USER = 'user_name'  # Replace with your actual Redshift username
    
    # Initialize AWS Redshift Data API client
    redshift_client = boto3.client('redshift-data')

    try:
        print("Executing Redshift query...")
        # Execute SQL query using Redshift Data API
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
            Parameters=[{'name': 'order_id', 'value': order_id}]
        )

        # Get the query execution ID
        query_id = response['Id']
        
        # Poll for query completion
        while True:
            # Check query execution status
            status_response = redshift_client.describe_statement(Id=query_id)
            status = status_response['Status']
            
            if status == 'FINISHED':
                # Retrieve and process query results
                result = redshift_client.get_statement_result(Id=query_id)
                records = result['Records']
                
                if records:
                    # Extract order status and tracking ID from first record
                    order_status = records[0][0]['stringValue']
                    order_tracking_id = records[0][1]['stringValue']

                    # Format success response
                    responseBody = {
                        "TEXT": {
                            "body": f"Your order status is '{order_status}' and you can track your order here: {order_tracking_id}."
                        }
                    }
                else:
                    # Format response for no results found
                    responseBody = {
                        "TEXT": {
                            "body": f"No order information found for order ID {order_id}."
                        }
                    }
                break
            
            elif status in ['FAILED', 'ABORTED']:
                raise Exception(f"Query failed with status: {status}")
            
            # Wait before next status check
            time.sleep(0.5)
    
    except Exception as e:
        # Handle and log any errors
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
    
    # Construct the final Lambda response
    lambda_response = {
        'response': action_response,
        'messageVersion': event.get('messageVersion', '1.0')
    }
    
    # Log the response and return
    print("Response:", json.dumps(lambda_response, indent=2))
    return lambda_response
