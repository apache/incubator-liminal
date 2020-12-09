#! /bin/bash

# Read namespace
read -r -p "Please enter a namespace: " namespace

function green() {
  printf "\e[32m"
  echo "$1"
  printf "\e[0m"
}

components=("web" "scheduler" "worker")
namespace=${namespace}
podNames=()
for component in ${components[@]}
do
        podNames+="$(kubectl get pod -n ${namespace} -l "app=airflow,component=${component}" --no-headers -o custom-columns=":metadata.name")\n"

done

echo -e "The following Airflow pods are:\n${podNames}"

IFS=$'\n'|''; set -f; podNames=( ${podNames} )
webPodName=$(echo -e ${podNames[${#podNames[@]} - 1]} | head -n 1)

for podName in `echo -e ${podNames[@]}`
do
        green "Installing liminal in pod: ${podName}"
        kubectl exec -it -n ${namespace} ${podName} -- bash -c 'pip install --user apache-liminal'
done

green "Deploying liminal"
kubectl exec -it $webPodName -n ${namespace} -- bash -c "find '/home/airflow/' -path  '*liminal/runners/airflow/dag/liminal_dags.py'| xargs -I {} cp -p {} /opt/airflow/dags/"
kubectl exec -it $webPodName -n ${namespace} -- bash -c "mkdir -p /opt/airflow/dags/pipelines/"
kubectl exec -it $webPodName -n ${namespace} -- bash -c "mkdir -p /opt/airflow/dags/pipelines/example-repository/"
kubectl cp liminal.yml ${namespace}/$webPodName:/opt/airflow/dags/pipelines/example-repository/