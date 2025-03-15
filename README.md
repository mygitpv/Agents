# Order Tracking Lambda Function triggered by Bedrock Agent Action Group

## Overview
This AWS Lambda function integrates with Amazon Bedrock Agent to retrieve order tracking information from an Amazon Redshift database. It provides order status and tracking details based on a provided order ID.

## Features
- Queries Amazon Redshift using the Redshift Data API
- Handles asynchronous query execution with status polling
- Provides formatted responses for Amazon Bedrock Agent
- Includes comprehensive error handling
- Supports parameter validation

## Prerequisites
- AWS Account with appropriate permissions
- Amazon Redshift cluster
- Required AWS IAM roles and policies
- Python 3.x
- Required Python packages:
  - boto3
  - json

## Configuration
### Environment Variables
The following configuration values need to be set:
```python
CLUSTER_IDENTIFIER = 'cluster_name'    # Your Redshift cluster identifier
DATABASE = 'database_name'             # Your Redshift database name
DB_USER = 'user_name'                 # Your Redshift username
```

### Required IAM Permissions
The Lambda function requires the following AWS permissions:
- `redshift-data:ExecuteStatement`
- `redshift-data:DescribeStatement`
- `redshift-data:GetStatementResult`

## Usage
### Input Format
The Lambda function expects an event object with the following structure:
```json
{
  "parameters": [
    {
      "name": "order_id",
      "value": "your_order_id"
    }
  ],
  "actionGroup": "your_action_group",
  "function": "your_function_name",
  "messageVersion": "1.0"
}
```

### Output Format
The function returns a response in the following format:
```json
{
  "response": {
    "actionGroup": "your_action_group",
    "function": "your_function_name",
    "functionResponse": {
      "responseBody": {
        "TEXT": {
          "body": "Your order status is 'STATUS' and you can track your order here: TRACKING_ID"
        }
      }
    }
  },
  "messageVersion": "1.0"
}
```

## Error Handling
The function handles several types of errors:
- Missing or invalid order_id parameter
- Database query failures
- Connection issues
- No results found

## Database Schema
The function expects a Redshift table with the following structure:
```sql
temp_workspace.order_tracking_test (
    order_id varchar,
    order_status varchar,
    order_tracking_id varchar
)
```

## Deployment
1. Package the Lambda function with its dependencies
2. Deploy to AWS Lambda
3. Configure environment variables
4. Set appropriate timeout values (recommended: 30 seconds)
5. Configure memory allocation based on your needs

## Monitoring
The function includes logging statements that can be monitored through CloudWatch Logs:
- Query execution start
- Error messages
- Response payload

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

