#! /bin/bash

help() {
    echo "$0: Get Started"
    echo "Usage: $0 -o option"
		echo "Liminal available options:          "
		echo "installation "
		echo "deployment"
}

if [[ "$#" -lt 2 ]]; then
	help
	exit
fi

# Arguments processing
while getopts ":o:" opt; do #installation, deployment
	case $opt in
	o)
	  option=$OPTARG
	  case $option in
	    installation)
	      ACTION="installation"
	    ;;
	    deployment)
	      ACTION="deployment"
	    ;;
	  esac
	esac
done

mount_efs() {
	local EFS_ID=$1
	local SSH_KEY=$2
	local USERNAME='admin'
	local HOST_IP=$3
	ssh -i ${SSH_KEY} ${USERNAME}@${HOST_IP} 'sudo bash -s' <<EOF
	EFS_ID=$EFS_ID
	echo "The EFS_ID is: ${EFS_ID}"

	echo 'Create /mnt/efs'
	mkdir /mnt/efs:wq

	echo 'Mount the /mnt/efs'
	sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport ${EFS_ID}:/ /mnt/efs

	echo 'Find the the mounted path of the Airflow'
	airflow_path=$(find /mnt/efs/ -name "liminal_home")

	echo 'Export the liminal home'
	export LIMINAL_HOME=${airflow_path}

	echo 'Append apache-liminal pacakge to the requirements file'
	echo "apache-liminal" >$LIMINAL_HOME/requirements.txt
EOF
}

restart_airflow_components() {
	echo 'Rollout restart Airflow components'
	kubectl rollout restart statefulset airflow-worker
	kubectl rollout restart deployment airflow-web
	kubectl rollout restart deployment airflow-scheduler
}

deploy_yaml() {
        echo "Deployment"
}

case $ACTION in
	installation)
                read -r -p "Please enter EFS ID: " EFS_ID
                read -r -p "Please enter ssh key path: " SSH_KEY
                read -r -p "Please enter host ip: " HOST_IP

                EFS_ID=${EFS_ID}
                SSH_KEY=${SSH_KEY}
                HOST_IP=${HOST_IP}
                mount_efs $EFS_ID $SSH_KEY $HOST_IP
                restart_airflow_components
		exit 0
	;;
	deployment)
                deploy_yaml
		exit 0
	;;
*)
  help
  exit
  ;;
esac