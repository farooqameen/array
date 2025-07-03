from langchain_community.chat_models import BedrockChat
from langchain_aws.chat_models.bedrock_converse import ChatBedrockConverse
from deepeval.models.base_model import DeepEvalBaseLLM
from enum import Enum
from langchain_openai import ChatOpenAI
import logging, boto3
from common.constants import BEDROCK_MODEL_IDS, BOTO_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] {%(module)s::%(funcName)s} %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Prototype")

class JudgeName(Enum):
    OPENAI = "openai"
    BEDROCK = "bedrock"

class DeepEvalPluginBedrock(DeepEvalBaseLLM):
    def __init__(
        self,
        model
    ):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        res = chat_model.invoke(prompt).content
        logger.info(f"GENERATE: {res}")
        return res if res else r"{}"

    async def a_generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        res = await chat_model.ainvoke(prompt)
        logger.info(f"GENERATE: {res.content}")
        return res.content if res and res.content else r"{}"

    def get_model_name(self):
        return "Custom Bedrock Model"
    
def get_judge_model(
        judge_name:str,
        judge_config:dict
        ):
    logger.info(f"Evaluators config: {judge_name} , {judge_config}")
    if not judge_name:
        logger.error(f"no judge name provided, cannot generate a judge model")
        return None, None

    model_for_de_evaluators = None
    model_for_langchain_evaluators = None
    if judge_name == JudgeName.OPENAI.value:
        judge_model = judge_config.get("judge_model")
        judge_kwargs = judge_config.get("judge_kwargs")
        if judge_kwargs:
            logger.warning(f"judge_kwargs cannot be passed to langchain evaluators, only deepeval will inherit those values")
        if not judge_model:
            logger.error("No judge model was specified for OPENAI") 
        else:
            model_for_de_evaluators = judge_model
            model_for_langchain_evaluators = ChatOpenAI(model=judge_model, **judge_kwargs)

    elif judge_name == JudgeName.BEDROCK.value:
        judge_model_id = judge_config.get("judge_model_id")
        judge_kwargs = judge_config.get("judge_kwargs")
        if judge_kwargs:
            logger.warning(f"judge_kwargs cannot be passed to langchain evaluators, only deepeval will inherit those values")
        if not judge_model_id:
            logger.error("No judge model id was specified for BEDROCK") 
        else:
            bedrock_session = boto3.session.Session(region_name="us-west-2")

            bedrock_client = bedrock_session.client(
                service_name="bedrock-runtime",
                config=BOTO_CONFIG
            )

            model_for_langchain_evaluators = ChatBedrockConverse(
                client=bedrock_client,
                model_id=BEDROCK_MODEL_IDS[judge_model_id],
                **judge_kwargs
                #temperature=0.0
            )
            model_for_de_evaluators = DeepEvalPluginBedrock(model=model_for_langchain_evaluators)


    return model_for_de_evaluators, model_for_langchain_evaluators
    

    