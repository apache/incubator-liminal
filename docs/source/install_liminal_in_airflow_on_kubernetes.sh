#! /bin/bash

help() {
    echo "$0: Get Started"
    echo "Usage: $0 -o option"
		echo "Liminal available options:          "
		echo "clone"
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
	    clone)
	      ACTION="clone"
	    ;;
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
	EFS_ID=$1
	echo "The EFS_ID is: ${EFS_ID}"

	echo "Create /mnt/efs"
	mkdir /mnt/efs

	echo "Mount the /mnt/efs"
	sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport ${EFS_ID}:/ /mnt/efs
}

install_liminal() {
	echo "Installing liminal on Airflow components"
	docker ps | grep k8s_airflow | awk '{print $1}' | xargs -I {} docker exec {} bash -c 'pip install apache-liminal'

	echo "Installing liminal locally"
	pip install apache-liminal
}

deploy_yaml() {
	echo 'Find the the mounted path of the Airflow'
	airflow_path=$(find /mnt/efs/ -name "liminal_home")
	echo "The mounted Airflow path is: $airflow_path"

	echo 'Export the liminal home'
	export LIMINAL_HOME=${airflow_path}

	liminal deploy --path "incubator-liminal/examples/liminal-getting-started"

	echo "Restarting Airflow components"
	docker ps | grep k8s_airflow | awk '{print $1}' | xargs -I {} docker restart {}
}

clone() {
	echo 'Cloning incubator-liminal'
	git clone https://github.com/apache/incubator-liminal.git
}

case $ACTION in
	clone)
                clone
		exit 0
	;;
	installation)
                read -r -p "Please enter EFS ID: " EFS_ID
                mount_efs $EFS_ID
                install_liminal
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