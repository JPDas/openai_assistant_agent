import sys
import os
from openai import OpenAI

from dotenv import load_dotenv
from contextlib import ExitStack
from loguru import logger

from utility import weather_tool, get_current_temperature

logger.remove() #remove the old handler. Else, the old one will work along with the new one you've added below'
logger.add(sys.stderr, level="INFO") 


load_dotenv()

class Ingestion:
    def __init__(self, data_path, assistant_id = None, vector_store_id = None) -> None:
        self.data_path = data_path
        self.assistant_id = assistant_id
        self.vector_store_id = vector_store_id
        self.openai = OpenAI()

        if not self.assistant_id:

            assistant = self.openai.beta.assistants.create(
                            name="Policy Assistant",
                            instructions= """ You are a helpful assistant that answers questions about the policies and instructions in your files. The policies and instructions are from a variety of documents. 
                                            You will answer questions from the user about the policies and instructions. All you will do is answer questions about the policies and instructions in the files and provide related information.
                                            If the user asks you a question that is not related to the policies and instructions in the files, you should let them know that you can only answer questions about the policies and instructions.
                                        """,
                            model="gpt-4o-mini",
                            tools=[{"type": "file_search"}],
                            temperature=0.0,
                            top_p=0.5
                        )
            
            logger.info(f"Assistant created::{assistant}")
            self.assistant_id = assistant.id

        if not self.vector_store_id:
            # Create a vector store caled "Financial Statements"
            vector_store = self.openai.beta.vector_stores.create(name="Policy Assistant")

            logger.info(f"Vector store::{vector_store}")
            self.vector_store_id = vector_store.id
            logger.info(f"Vector store id::{self.vector_store_id}")

    def retrieve_files_from_assistant(self):

        files = self.openai.files.list()

        # files = self.openai.beta.vector_stores.files.list(self.vector_store_id)

        files = files.to_dict()

        data = files.get("data", [])

        print(data)
        file_list = [ file.get("filename", "") for file in data]
        logger.info(f"Retrieve files from Vector store::{file_list}")

        return file_list

    def upload_files_to_vector_store(self, present_files):

        # Ready the files for upload to the vector store.
        files = os.listdir(self.data_path)

        file_paths = [os.path.join(self.data_path, file) for file in files if file not in present_files] 

        logger.info(f"File paths are {file_paths}")

        # Using ExitStack to manage multiple context managers and ensure they are properly closed.
        with ExitStack() as stack:

            if file_paths:
                # Open each file in binary read mode and add the file stream to the list
                file_streams = [stack.enter_context(open(path, "rb")) for path in file_paths]

                # Use the upload and poll helper method to upload the files, add them to the vector store,
                # and poll the status of the file batch for completion.
                file_batch = self.openai.beta.vector_stores.file_batches.upload_and_poll(
                    vector_store_id=self.vector_store_id, files=file_streams
                )
        
                # Print the status and the file counts of the batch to see the results
                logger.info(f"File batch status {file_batch.status}")
                logger.info(f"File batch counts {file_batch.file_counts}")
    

    def update_assistant(self):

        assistant = self.openai.beta.assistants.update(
                        assistant_id=self.assistant_id,
                        instructions="""You are a helpful assistant that answers questions about the policies and instructions in your files. The policies and instructions are from a variety of documents. 
                            You will answer questions from the user about the policies and instructions. All you will do is answer questions about the policies and instructions in the files and provide related information.
                            When asked a math question, write and run code to answer the question.
                            when asked the temperature or weather of the location, provide the temperature of the city or state.
                            """,
                        tools=[{"type": "file_search"}, {"type": "code_interpreter"}, weather_tool],
                        tool_resources={"file_search": {"vector_store_ids": [self.vector_store_id]}},
                    )
        
        logger.info(f"Updated assistant:: {assistant}")


    def run(self):

        present_files = self.retrieve_files_from_assistant()
        self.upload_files_to_vector_store(present_files)

        self.update_assistant()

        logger.info("File ingested successfully")

# if __name__ == "__main__":

#     ingestion = Ingestion("ingested_data", assistant_id="asst_b0e8Dh6T1MiyPV80jcOz6ka4", vector_store_id="vs_67a4e54f13888191b44c151bef18c84f")

#     ingestion.run()