import subprocess

# Environment-based configurations for AKS, Resource Group, and Namespace
env_configurations = {
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
}

def fetch_k8s_logs(env="dev", log_level="all", time_period=None):
    # Step 1: Fetch environment-specific configuration
    if env not in env_configurations:
        print(f"Error: Environment '{env}' is not configured.")
        return

    env_config = env_configurations[env]

    # Step 2: Get AKS credentials
    print(f"Getting credentials for AKS cluster: {env_config['aks_name']}")
    subprocess.run(
        ["az", "aks", "get-credentials", "--name", env_config["aks_name"],
         "--resource-group", env_config["resource_group"]],
        check=True
    )

    # Step 3: Set the namespace context
    print(f"Setting Kubernetes context to namespace: {env_config['namespace']}")
    subprocess.run(
        ["kubectl", "config", "set-context", "--current", "--namespace", env_config["namespace"]],
        check=True
    )

    # Step 4: Fetch and list all pod names in the specified namespace
    print(f"Fetching pod names in namespace: {env_config['namespace']}")
    pods = subprocess.run(
        ["kubectl", "get", "pods", "--namespace", env_config["namespace"], "-o", "jsonpath={.items[*].metadata.name}"],
        capture_output=True, text=True
    )
    pod_names = pods.stdout.split()  # Split the output into individual pod names
    if not pod_names:
        print("No pods found in the specified namespace.")
        return

    print("\nAvailable Pods:")
    for idx, name in enumerate(pod_names, 1):
        print(f"{idx}. {name}")

    # Step 5: Ask user to select pods by index
    selection = input("\nEnter the pod indexes (comma separated) you want logs for, or press Enter (or type 'all') to select all pods: ").strip().lower()
    if selection == "" or selection == "all":
        selected_pods = pod_names
    else:
        try:
            indices = [int(i.strip()) for i in selection.split(",") if i.strip().isdigit()]
            selected_pods = [pod_names[i - 1] for i in indices if 0 < i <= len(pod_names)]
            if not selected_pods:
                print("No valid indexes entered. Exiting.")
                return
        except Exception as e:
            print("Invalid input. Exiting.")
            return

    # Step 6: Loop through the selected pods and fetch their logs
    for pod in selected_pods:
        print("=============================================================================================")
        print(f"Fetching logs for pod: {pod}")
        print("=============================================================================================")
        
        # Set the time period conditionally (if none provided, fetch from the beginning)
        since_flag = f"--since={time_period}" if time_period else ""
        logs = subprocess.run(
            ["kubectl", "logs", pod, "--namespace", env_config["namespace"], since_flag],
            capture_output=True, text=True
        )

        if logs.stdout:
            # Filter logs based on the specified log level
            filtered_logs = filter_logs(logs.stdout, log_level)
            log_count = len(filtered_logs.splitlines())
            # Print the filtered logs first...
            print(filtered_logs)
            # ...then print the count at the end.
            print("=============================================================================================")
            print(f"Total log entries for pod '{pod}' with level '{log_level}': {log_count}")
            print("=============================================================================================")
        else:
            print(f"No logs found for pod '{pod}'")

def filter_logs(logs, log_level="all"):
    """Filter logs based on the given log level."""
    log_lines = logs.splitlines()
    filtered_lines = []
    for line in log_lines:
        if log_level == "all":
            filtered_lines.append(line)
        elif log_level == "error" and "error" in line.lower():
            filtered_lines.append(line)
        elif log_level == "warning" and "warning" in line.lower():
            filtered_lines.append(line)
        elif log_level == "info" and "info" in line.lower():
            filtered_lines.append(line)
    return "\n".join(filtered_lines)

# Example usage:
env = input("Enter the environment (dev, test): ").strip().lower()
log_level = input("Enter the log level to filter by (error, warning, info, all): ").strip().lower() or "all"
time_period = input("Enter the time period for logs (e.g., 5m, 1h, 48h, or leave blank for logs from the beginning): ").strip().lower()

fetch_k8s_logs(env, log_level, time_period)
