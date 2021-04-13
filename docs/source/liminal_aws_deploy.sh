#! /bin/bash

help() {
    echo "$0: Get Started"
    echo "Usage: $0 -o option"
		echo "Liminal available options:          "
		echo "install"
		echo "build "
		echo "deploy"
}

if [[ "$#" -lt 2 ]]; then
	help
	exit
fi

# Arguments processing
while getopts ":o:" opt; do #install, build, deploy
	case $opt in
	o)
	  option=$OPTARG
	  case $option in
	    install)
	      ACTION="install"
	    ;;
	    build)
	      ACTION="build"
	    ;;
	    deploy)
	      ACTION="deploy"
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
	DEPLOY_PATH=$1
	echo "The DEPLOY_PATH is: ${DEPLOY_PATH}"
	echo 'Export the liminal home'
	export LIMINAL_HOME=$(find /mnt/efs/ -name "liminal_home")

	liminal deploy --path "${DEPLOY_PATH}"

	echo "Restarting Airflow components"
	docker ps | grep k8s_airflow | awk '{print $1}' | xargs -I {} docker restart {}
}

build() {
	BUILD_PATH=$1
	echo "The BUILD_PATH is: ${BUILD_PATH}"

	liminal build --path "${BUILD_PATH}"
}

case $ACTION in
	install)
                read -r -p "Please enter the EFS ID: " EFS_ID
                mount_efs $EFS_ID
                install_liminal
		exit 0
	;;
	build)
				read -r -p "Please enter the path to the liminal project: " BUILD_PATH
                build $BUILD_PATH
		exit 0
	;;
	deploy)
				read -r -p "Please enter the liminal yaml path: " DEPLOY_PATH
                deploy_yaml $DEPLOY_PATH
		exit 0
	;;
*)
  help
  exit
  ;;
esac