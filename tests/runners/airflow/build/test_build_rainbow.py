import unittest
from unittest import TestCase

import docker
from rainbow.build import build_rainbows


class TestBuildRainbow(TestCase):

    def test_build_rainbow(self):
        docker_client = docker.client.from_env()
        image_names = ['rainbow_image', 'rainbow_image2']

        for image_name in image_names:
            if len(docker_client.images.list(image_name)) > 0:
                docker_client.images.remove(image=image_name)

        build_rainbows.build_rainbows('tests/runners/airflow/rainbow')

        for image_name in image_names:
            docker_client.images.get(name=image_name)

        docker_client.close()


if __name__ == '__main__':
    unittest.main()
