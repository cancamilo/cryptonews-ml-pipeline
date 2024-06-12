import logging
import json
from db.qdrant import connection as client
from utils.data_formatter import DataFormatter
from utils.openai_helper import OpenAIHandler
from comet_ml import Artifact, Experiment
from settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DatasetGenerator:
    def __init__(
        self,
        api_communicator: OpenAIHandler,
        data_formatter: DataFormatter
    ):
        self.api_communicator = api_communicator
        self.data_formatter = data_formatter

    def generate_training_data(self, all_contents: list, batch_size: int = 1):
        response = []
        for i in range(0, len(all_contents), batch_size):
            batch = all_contents[i : i + batch_size]
            initial_prompt = self.data_formatter.format_prompt(batch, i)
            batch_result = self.api_communicator.request(initial_prompt)

            if len(batch_result) != len(batch):
                continue
            
            for j in range(0, len(batch_result)):
                batch_result[j]["content"] = batch[j]

            response += batch_result
                

        return response
    
    def fetch_all_cleaned_content(self, collection_name: str) -> list:
        all_cleaned_contents = []

        scroll_response = client.scroll(collection_name=collection_name, limit=10000)
        points = scroll_response[0]

        for point in points:
            cleaned_content = point.payload["cleaned_content"]
            # cleaned_content = point.payload
            if cleaned_content:
                all_cleaned_contents.append(cleaned_content)

        return all_cleaned_contents

        
    
    def push_to_comet(self, data: list, collection_name: str):
        try:
            logging.info(f"Starting to push data to Comet: {collection_name}")

            # Assuming the settings module has been properly configured with the required attributes
            experiment = Experiment(
                api_key=settings.COMET_API_KEY,
                project_name=settings.COMET_PROJECT,
                workspace=settings.COMET_WORKSPACE,
            )

            file_name = f"{collection_name}.json"
            logging.info(f"Writing data to file: {file_name}")

            with open(file_name, "w") as f:
                json.dump(data, f)

            logging.info("Data written to file successfully")

            artifact = Artifact(collection_name)
            artifact.add(file_name)
            logging.info(f"Artifact created and file added: {file_name}")

            experiment.log_artifact(artifact)
            experiment.end()
            logging.info("Data pushed to Comet successfully and experiment ended")

        except Exception as e:
            logging.error(f"Failed to push data to Comet: {e}", exc_info=True)
    
if __name__ == "__main__":
    collection_name = "cleaned_articles"
    openai_handler = OpenAIHandler()
    formatter = DataFormatter()
    generator = DatasetGenerator(openai_handler, formatter)
    all_contents = generator.fetch_all_cleaned_content(collection_name)
    training_data = generator.generate_training_data(all_contents[:10], 1)
    generator.push_to_comet(training_data, collection_name)


