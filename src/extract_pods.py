from kubernetes import client, config
from flask import Flask, render_template

app = Flask(__name__)

def main():
    config.load_incluster_config()
    #config.load_kube_config()

    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces(watch=False)
    pods_details_list = []
    for pod in pods.items:
        dict = {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "ip": pod.status.pod_ip,
            "node": pod.spec.node_name,
            "status": pod.status.phase
        }
        pods_details_list.append(dict)
    return (pods_details_list)

@app.route('/')
def hello_world():
    return render_template('index.html', pods_list=main())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)