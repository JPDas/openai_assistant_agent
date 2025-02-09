import sys
from openai import OpenAI

from loguru import logger

from dotenv import load_dotenv

logger.remove() #remove the old handler. Else, the old one will work along with the new one you've added below'
logger.add(sys.stderr, level="INFO") 

load_dotenv()

class Inference:
    def __init__(self, assistant_id, thread_id =None):

        self.assistant_id = assistant_id
        self.thread_id = thread_id

        self.openai = OpenAI()

        if not self.thread_id:

            thread = self.openai.beta.threads.create()
        
            logger.info(f"Thread is created {thread}")

            self.thread_id = thread.id

    def run_thread(self, query):

        # ==== Create a Message ====
        message = self.openai.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=query
        )

        # === Run our Assistant ===
        run = self.openai.beta.threads.runs.create_and_poll(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions="Please address the user as JP",
        )
        
        messages = list(self.openai.beta.threads.messages.list(thread_id=self.thread_id, run_id=run.id))

        message_content = messages[0].content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = self.openai.files.retrieve(file_citation.file_id)
                logger.info(f"cited file : {cited_file}")
                citations.append(f"[{index}] {cited_file.filename}")

        citations = "\n".join(citations)
        logger.info(f"Citations:: {citations}")

        if citations:
            final_response = message_content.value + "<br>" + "Sources: " + "<br>" + citations
        else:
            final_response = message_content.value

        # ==== Steps --- Logs ==
        run_steps = self.openai.beta.threads.runs.steps.list(thread_id=self.thread_id, run_id=run.id)
        logger.info(f"Steps---> {run_steps.data[0]}")

        return final_response

# if __name__ == "__main__":

      #query = "I need to solve the equation 3x + 11 = 14. Can you help me?"
      # query ="How Your RS A Token Works?"
#     # query = "How to contact the Banking Ombudsman?"
#     query = "How the Code relates to bank terms and conditions?"
#     inference = Inference("asst_b0e8Dh6T1MiyPV80jcOz6ka4", query, thread_id="thread_sF288yuX9gy8NR6s6nNO9Hdh")

#     inference.run_thread(query)