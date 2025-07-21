# Kubernetes AKS Log Analyzer Utility

This is a Python-based CLI utility to analyze logs from Azure Kubernetes Service (AKS) pods. It allows environment-based selection (dev, test), filtering by log level, time period, and specific search terms, making it easier to analyze pod logs for debugging and monitoring.

## Features

* Automatically sets the correct Kubernetes context based on the environment
* Lists pods in a specified namespace and allows interactive selection
* Filters logs by:
   * Log level (error, warning, info, or all)
   * Time period (e.g., 5m, 1h, 24h)
   * Optional search term
* Provides a count of matched log lines

## Prerequisites
Ensure the following tools are installed and configured:

* Python 3.6+
* Azure CLI (az) logged in and configured
* kubectl installed and configured

## Project Structure
`.`

`├── k8s_log_analyzer.py      # Main utility script`

`└── README.md                # This file`

## Configuration
Supported environments are defined in the script:

    "dev": {
    
        "aks_name": "aks-dev", 
        "resource_group": "rg-dev", 
        "namespace": "ns-dev"
    },
    "test": {
        "aks_name": "aks-test", 
        "resource_group": "rg-test", 
        "namespace": "ns-test"
    }

You can add more environments as needed.

## Usage
Run the script:

`python k8s_log_analyzer.py`

The script will prompt you for:
1. **Environment**: dev or test
2. **Log Level**: error, warning, info, or all
3. **Time Period (optional)**: e.g., 5m, 1h, 2d (or leave blank)
4. **Search Term (optional)**: any keyword to further filter the logs

You'll then be presented with a list of pods. Choose one or more by index (e.g., 1,2,5) or type all to fetch from all pods.

## Example Output

`Enter the environment (dev, test): dev`

`Enter the log level to filter by (error, warning, info, all): error` 

`Enter the time period for logs (e.g., 5m, 1h, 48h): 1h`

`Enter a search term to filter logs: connection refused`


`Fetching logs for pod: mypod-123456`

`=============================================================================================`

`...filtered logs...`

`=============================================================================================`

`Total log entries for pod 'mypod-123456' with level 'error' and search term 'connection refused': 4`

## Error Handling
* Invalid environment name: prints a clear error and exits
* No pods found: exits gracefully
* Invalid pod indexes: notifies user and exits
* Any command failures (e.g., failed `az` or `kubectl` commands) will raise an error due to `check=True`

## Notes
* The script uses `subprocess.run()` to execute `az` and `kubectl` commands
* You may require `az login` or appropriate RBAC permissions to access the AKS cluster
* `kubectl logs` uses `--since` only if the `time_period` is specified

## Security Tip
Do not hardcode credentials or sensitive information in the script. Use environment variables or a secure key vault if future enhancements involve secrets.
