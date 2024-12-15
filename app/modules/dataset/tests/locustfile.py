from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing
import secrets


class DatasetBehavior(TaskSet):
    def on_start(self):
        self.dataset()

    @task
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()


class DatasetPublishBehavior(TaskSet):
    @task
    def publish_dataset(self):
        # Genera un número aleatorio seguro para la publicación del dataset
        dataset_id = secrets.randbelow(100) + 1  # Genera un número entre 1 y 100
        response = self.client.post(f"/dataset/{dataset_id}/publish")

        if response.status_code == 200:
            print(f"Dataset {dataset_id} publicado con éxito")
        elif response.status_code == 400:
            print(f"Dataset {dataset_id} ya estaba publicado o tuvo un error: {response.json()}")
        else:
            print(f"Error en la publicación del dataset {dataset_id}: {response.status_code}")
