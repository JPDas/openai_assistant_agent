import sys
import time
import json
from openai import OpenAI

from loguru import logger

from dotenv import load_dotenv

from utility import get_current_temperature

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

        if run.status == "requires_action":
            
            required_actions = run.required_action.submit_tool_outputs.model_dump()
            logger.info(f"Require Actions:: {required_actions}")
            
            for action in required_actions["tool_calls"]:
                tools_outputs = []
                func_name = action["function"]["name"]
                print(func_name)

                arguments = action["function"]["arguments"]
                arguments = json.loads(arguments)
                print(arguments["location"])

                if func_name == "get_current_temperature":
                    final_string = get_current_temperature(arguments["location"], arguments["unit"])

                    tools_outputs.append({"tool_call_id": action["id"], "output": final_string})


                    run = self.openai.beta.threads.runs.submit_tool_outputs(thread_id=self.thread_id, run_id=run.id, tool_outputs=tools_outputs)

                    while run.status == "queued" or run.status == "in_progress":
                        run = self.openai.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run.id)

                        time.sleep(1)

                    break
        
        logger.info(f"Run status is {run.status}")
        if run.status == "completed":
            messages = list(self.openai.beta.threads.messages.list(thread_id=self.thread_id, run_id=run.id))

            logger.info(f"Messages::{messages}")

            if type(messages) == list and len(messages) > 0:
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
            else:
                final_response = messages

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