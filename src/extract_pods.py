from kubernetes import client, config
from flask import Flask, render_template

app = Flask(__name__)

def get_kube_config():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        try:
            config.load_kube_config()
        except config.ConfigException:
            raise Exception("Could not configure kubernetes python client")
    v1 = client.CoreV1Api()
    return v1

def main():
    v1 = get_kube_config()
    pods = v1.list_pod_for_all_namespaces(watch=False)
    pods_details_list = []
    for pod in pods.items:
        status = get_pod_status(pod)
        dict = {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "ip": pod.status.pod_ip,
            "node": pod.spec.node_name,
            "status": status
        }
        pods_details_list.append(dict)
    return (pods_details_list)

def get_pod_status(pod):
    status = pod.status.phase
    try:
        for container_status in pod.status.container_statuses:
            if container_status.started is False or container_status.ready is False:
                waiting_state = container_status.state.waiting
                if waiting_state is not None:
                    status = waiting_state.reason
    finally:
        return status

@app.route('/')
def hello_world():
    return render_template('index.html', pods_list=main())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)