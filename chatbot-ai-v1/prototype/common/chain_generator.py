from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_aws import ChatBedrock, ChatBedrockConverse
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
import json, os, boto3
from abc import ABC, abstractmethod
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import BedrockEmbeddings
from langchain_aws.chat_models.bedrock_converse import ChatBedrockConverse
import logging, re
from pydantic import BaseModel
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langsmith import traceable
from .utils import search_set, s3_csv_to_set, get_aws_session_w_region, create_history_aware_retriever
from .prompts import PROMPT_GENERATION, PROMPT_GENERATE_TITLE, PROMPT_MODIFY_QUESTION_W_HISTORY, DOCUMENT_TEMPLATE_BEDROCK, DOCUMENT_TEMPLATE_OPENAI, PROMPT_PROCESS_QUESTION

# choose import statement based on runtime (python vs. streamlit)

from .constants import BEDROCK_MODEL_IDS, BOTO_CONFIG
from .utils import Credential, validate_credential, store_env_var

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] {%(module)s::%(funcName)s} %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("Prototype")


if 'LANGCHAIN_TRACING_V2' in os.environ and os.environ.get('LANGCHAIN_TRACING_V2') == 'true':
    logger.info(f"LANGSMITH TRACING IS ENABLED")
    os.environ['LANGCHAIN_PROJECT'] = 'prototype'
    @validate_credential(creds=[Credential.LANGSMITH])
    def validate_langsmith_creds():
        pass
    validate_langsmith_creds()


class DocumentType(BaseModel):
    content: str
    metadata: dict


class OutputType(BaseModel):
    context: list[DocumentType]
    response: str


class ResultChunk:
    """
    Class to abstract result chunks from RAG chains.

    Attributes:
        response (dict): The response part of the result.
        context (list[Document]): The context part of the result.
    """

    def __init__(self, result: dict):
        self.response = None
        self.context = None
        if "response" in result:
            self.response = result["response"]
        if "context" in result:
            self.context = result["context"]

    def has_response(self) -> bool:
        """Check if the result chunk has a response."""
        return False if self.response is None else True

    def has_context(self) -> bool:
        """Check if the result chunk has context."""
        return False if self.context is None else True


class Citation:
    """
    Utility Class to transform & massage retrieved context [NOTE: a single retrieved context chunk is a citation]

    Attributes:
        page_content (str): The content of the cited page.
        metadata (dict): The metadata associated with the citation.
    """

    _session = None

    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata

    @staticmethod
    @validate_credential(creds=[Credential.AWS, Credential.DATASET_S3_BUCKET])
    def _fetch_s3_metadata(metadata: dict) -> None:
        """
        Fetch metadata from S3 and update the metadata dictionary.

        Args:
            metadata (dict): The metadata to update.
        """
        # check invariance (metadata is not null & uri exists)
        if not metadata:
            logger.warning(f"metadata is null")
            return
        if "location" not in metadata\
            or "s3Location" not in metadata["location"]\
            or "uri" not in metadata["location"]["s3Location"]:
            logger.warning(f"s3 uri cannot be found in metadata")
            return

        s3_uri = metadata["location"]["s3Location"]["uri"]
        try:
            if Citation._session is None:
                Citation._session = get_aws_session_w_region()

            s3_client = Citation._session.client("s3")

            match = re.search(r's3://([^/]+)/', s3_uri)
            bucket = "cbb-rulebook" if match is None else match.group(1)
            key = s3_uri.split(f"s3://{bucket}")[1][1:]
            custom_metadata = s3_client.get_object(
                Bucket=bucket, Key=f"{key}.metadata.json"
            )
            custom_metadata = json.loads(custom_metadata["Body"].read().decode("utf-8"))
        except Exception as err:
            logger.error(f"Failed to fetch metadata from s3 bucket [{metadata['location']['s3Location']['uri']}], no changes made.. continuing..")
            logger.error(f"{err}")
            return

        metadata["s3_uri"] = metadata["location"]["s3Location"]["uri"]
        del metadata["location"]
        metadata.update(custom_metadata["metadataAttributes"])
        return

    @staticmethod
    def extract_citations(result: ResultChunk, get_s3_meta: bool = None) -> list:
        """
        Extract citations from a result chunk.

        Args:
            result (ResultChunk): The result chunk to extract citations from.
            get_s3_meta (bool, optional): Flag to fetch S3 metadata. Defaults to None.

        Returns:
            list: List of Citation objects.
        """
        citations = []
        if result.has_context():
            result = result.context
        for doc in result:
            page_content, metadata = "", {}
            if hasattr(doc, "page_content"):
                page_content = doc.page_content
            else:
                logger.warning(f"missing page content in")
                logger.warning(f"{result}")

            if hasattr(doc, "metadata"):
                metadata = doc.metadata
                if 'location' in metadata and 's3Location' in metadata['location']:
                    Citation._fetch_s3_metadata(metadata)
            else:
                logger.warning(f"missing metadata in")
                logger.warning(f"{result}")

            citations.append(Citation(page_content=page_content, metadata=metadata))
        return citations

    @staticmethod
    def context_to_one_string(response) -> str:
        """
        Convert context to a single string.

        Args:
            response (dict): The response containing context.

        Returns:
            str: Combined context as a single string.
        """
        text = "".join([f"{doc.page_content}\n" for doc in response['context'] if hasattr(doc, "page_content")])
        return text

    @staticmethod
    def context_to_list_string(response) -> str:
        """
        Convert context to a list of strings.

        Args:
            response (dict): The response containing context.

        Returns:
            list: List of context strings.
        """
        text = [f"{doc.page_content}" for doc in response['context'] if hasattr(doc, "page_content")]
        return text


class AbstractSolution(ABC):
    """
    Abstract base class for solution implementations.
    """

    @abstractmethod
    def _init_chain():
        '''
        Follow convention in the GPTSolution constructor - this gets called inside it after prior setup
        Three things must be setup
            1- self._model
            2- self._vectorstore
            3- self._search_kwargs 
        '''
        pass

    def __init__(self,
                 list_context:bool = True,
                 has_filter:bool=None,
                 s3_rules_file_key:str=None
                 ):
        # Define member variables without initializing them
        self._has_filter = has_filter
        self._s3_rules_file_key = s3_rules_file_key
        self.list_context = list_context
        self._model = None
        self._search_kwargs = None
        self._filter_initialized = None
        self._filter_values = None
        self._vectorstore = None
        self._search_type = None
        

        if self._has_filter:
            if self._s3_rules_file_key:
                try:
                    self._filter_values = s3_csv_to_set(s3_key=self._s3_rules_file_key)

                except Exception as e:
                    self._has_filter = False
                    logger.error(f"Failed to retrieve filter values from S3. AWS connection error: {e}")
            else: 
                self._has_filter = False
                missing_info = [
                    ("S3 URI", self._s3_rules_file_key),

                ]
                missing_params = ", ".join([name for name, value in missing_info if not value])
                logger.error(f"Missing information for the filter: {missing_params}. Disabling filter.")

    @traceable(name="get_title_chain")
    def get_chain_title(self):
        title_w_history_template = ChatPromptTemplate.from_messages(
            [
                ("system", PROMPT_GENERATE_TITLE),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        chain = title_w_history_template | self._model | StrOutputParser()
        return chain
    
    
    def extract_and_filter_rule_codes(self, question: str) -> dict | None:
        """
        Extract and filter rule codes from user input.

        This function identifies patterns in the format 'XX-XX.XX.XXX' (where X can be a letter or digit),
        converts them to uppercase, and filters them against predefined values.

        Parameters:
        - question (str): The user's input question containing potential rule codes.

        Returns:
        - dict: The updated search_kwargs dictionary.
        """
        search_kwargs = self._search_kwargs.copy()
        
        if not self._has_filter and self._filter_initialized:
            logger.error("Filter initialization or AWS connection issue detected. Proceeding without filtering, which may affect the accuracy of the response.")
        
        if not self._has_filter:
            return search_kwargs
        
        rule_code_pattern = r'\b[A-Za-z]{2}-[A-Za-z0-9]{1,2}(?:\.[A-Za-z0-9]{1,2}){0,2}[A-Za-z]?\b'
        matches = re.findall(rule_code_pattern, question)
        
        if matches:
            filtered_matches = [match.upper() for match in matches if search_set(value_set=self._filter_values, search_value=match)]
            if filtered_matches:
                search_kwargs["filter"] = {"rules": {"$in": filtered_matches}}
    
        return search_kwargs
    
    
    @traceable(name="get_chain_with_history")
    def get_chain_with_history(self, question=""):
        # prompt used to request an LLM to adjust the question given the chat history
       
        # template to combine the prompt with fetched chat history
        modify_question_w_history_template = ChatPromptTemplate.from_messages(
            [
                ("system", PROMPT_MODIFY_QUESTION_W_HISTORY),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        search_kwargs = self.extract_and_filter_rule_codes(question=question)

        # modified retriever that adjusts question with chat history. 
        # Produces a retriever object
        # prompt | llm | StrOutputParser() | retriever
        temp_dict = {'type': self._search_type if self._search_type else 'similarity', 'kwargs':search_kwargs}
        history_aware_retriever = create_history_aware_retriever(
            self._model,
            self.make_retriever(self._vectorstore, **temp_dict),
            modify_question_w_history_template
        )

        # History aware retriever will produce context passed in generation_prompt
        # Main template used for generation
        generation_template = ChatPromptTemplate.from_messages(
            [
                ("system", PROMPT_GENERATION),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        # generation chain 
        # (combine retriever with generation_template)
        temp_dict = {'document_prompt': DOCUMENT_TEMPLATE_BEDROCK if self._vectorstore.__class__ is AmazonKnowledgeBasesRetriever else DOCUMENT_TEMPLATE_OPENAI}
        question_answer_chain = create_stuff_documents_chain(
            self._model, 
            generation_template, 
            **temp_dict)
        
        # combine history aware retriever with generation chain
        return create_retrieval_chain(history_aware_retriever, question_answer_chain)
    

    def process_question(self, question):
        """
        Process a user's question by extracting rule codes and adjusting search filters accordingly.

        This method extracts rule codes from the provided question, adjusts the search filters 
        based on the extracted rules, and constructs a retrieval and response generation chain.

        Parameters:
        - question (str): The user's input question.

        Returns:
        - chain: A chain object that can be used to retrieve and generate responses based on the user's question.
        """
        # Create a copy of the search_kwargs to avoid mutating the instance variable
        search_kwargs = self.extract_and_filter_rule_codes(question=question)

        

        process_question_template = ChatPromptTemplate.from_template(PROMPT_PROCESS_QUESTION)
        # Construct and execute the retrieval and response generation chain
        temp_dict = {'type': self._search_type if self._search_type else 'similarity', 'kwargs':search_kwargs}
        return (
            RunnableParallel(
                {
                    "context": self.make_retriever(self._vectorstore, **temp_dict),
                    "question": RunnablePassthrough(),
                }
            )
            .assign(response=process_question_template | self._model | StrOutputParser())
            .with_types(output_type=OutputType)
            .pick(["response", "context"])
        )


    def _test(
        self, inputs: dict, ans_key: str = "answer", cnt_key: str = "context"
    ) -> dict:
        """
        Test the solution with given inputs.

        Args:
            inputs (dict): The inputs for testing.
            ans_key (str): The key for the answer in the output dictionary.
            cnt_key (str): The key for the context in the output dictionary.

        Returns:
            dict: The result containing the answer and context.
        """
        self.chain = self.process_question(inputs["question"])
        
        response = self.chain.invoke(inputs["question"])
        return {
            ans_key: response["response"],
            cnt_key: (
                Citation.context_to_one_string(response)
                if not self.list_context
                else Citation.context_to_list_string(response)
            ),
        }


    def _invoke(self, prompt) -> ResultChunk:
        """
        Invoke the solution with a given prompt.

        Args:
            prompt: The prompt to process.

        Returns:
            ResultChunk: The result of the invocation.
        """
        self.chain = self.process_question(prompt)
        result = self.chain.invoke(prompt)
        return ResultChunk(result)


    def stream(self, prompt) -> ResultChunk:
        """
        Stream the solution with a given prompt.

        Args:
            prompt: The prompt to process.

        Returns:
            ResultChunk: The result of the stream.
        """
        self.chain = self.process_question(prompt)
        result = self.chain.stream(prompt)
        return ResultChunk(result)
    

    @traceable
    def test(
            self,
            inputs: dict,
            ans_key: str = "answer",
            cnt_key: str = "context",
    ) -> dict:
        """
        Wrapper function to implement try-catch for test
        """
        try:
            return self._test(inputs, ans_key, cnt_key)
        except Exception as e:
            logger.error(f"An error occurred within the chain.")
            logger.error(e)


    @traceable
    def invoke(self, prompt) -> ResultChunk:
        """
        Wrapper for invoke to implement try/catch
        """
        try:
            return self._invoke(prompt)
        except Exception as e:
            logger.error(f"An error occurred within the chain.")
            logger.error(e)
    
    def _parse_context(self, token) -> dict:
        """
        Parser function to return unified response.

        Args:
            token: The token to process.

        Returns:
            dict: The unified response dictionary.
        """
        return token

    @traceable
    def parse_context(self, token) -> dict:
        """
        Wrapper for parse to implement try/catch 
        """
        try:
            return self._parse_context(token)
        except Exception as e:
            logger.error(f"An error occurred within the chain.")
            logger.error(e)

    def _make_retriever(self, vectorstore, type, kwargs):
        """
        Turn a vectorspace into a retriever object.

        Args:
            vectorstore: Vectorstore object to turn into a retriever.
            type: Search type to be performed.
            kwargs: Keyword arguments to pass to the search function.
        Returns:
            A retriever object.
        """
        return vectorstore.as_retriever(search_type=type, search_kwargs=kwargs)

    @traceable
    def make_retriever(self, vectorstore, type, kwargs):
        """
        Wrapper for parse to implement try/catch 
        """
        try:
            return self._make_retriever(vectorstore, type, kwargs)
        except Exception as e:
            logger.error(f"An error occurred trying to make a retriever.")
            logger.error(e)

def generate_chain(chain_config: dict) -> AbstractSolution:
    """
    Generate a solution chain based on the given configuration.

    Args:
        chain_config (dict): {solution_class:'', args:{}} the args dictionary must match solution's constructor arguments

    Returns:
        AbstractSolution: An instance of the appropriate solution class.
    """
    subclasses = AbstractSolution.__subclasses__()
    solutions = {subclass.__name__: subclass for subclass in subclasses}

    solution_class = ""
    try:
        solution_class = chain_config["solution_class"]
    except Exception as err:
        logger.error(f"'solution_class' cannot be found in config file...")
        return None

    if solution_class in solutions:
        try:
            chain = solutions[solution_class](**chain_config["args"])
        except Exception as err:
            logger.error(f"Failed to instantiate solution object {solution_class}, likely due to invalid configs.")
            logger.error(f"{err}")
            return None
        return chain

    logger.error(f"{solution_class} is not implmeneted...")
    return None


class GPTPineconeSolution(AbstractSolution):
    """
    Implementation of the AbstractSolution for GPT Pinecone.

    Attributes:
        list_context (bool): Flag to list context as strings.
        _pinecone_index_name (str): Name of the Pinecone index.
        _embed_model (str): Model for embeddings.
        _gen_model (str): Model for generation.
        _search_type (str): Type of search (e.g., similarity, mmr).
        _search_k (int): Number of top results to retrieve.
        _search_lambda (float): Lambda parameter for MMR search.
        _search_fetch_k (int): Number of results to fetch initially.
        chain (RunnableParallel): The processing chain.
        _pinecone_key: The API key for the Pineconne vector database
    """

    def __init__(
        self,
        list_context: bool = True,
        pinecone_index_name: str = "rulebook-large",
        embed_model: str = "text-embedding-3-large",
        gen_model: str = "gpt-4o",
        search_type: str = "similarity",
        search_k: int = 4,
        search_fetch_k: int = 20,
        search_lambda: float = 0.5,
        pinecone_key: str = None,
        has_filter: bool = False,
        s3_rules_file_key: str = None,
    ):
        super().__init__(has_filter = has_filter,
                         s3_rules_file_key=s3_rules_file_key,
                         list_context=list_context
            )
        self._pinecone_index_name = pinecone_index_name
        self._embed_model = embed_model
        self._gen_model = gen_model
        self._search_type = search_type
        self._search_k = search_k
        self._search_lambda = search_lambda
        self._search_fetch_k = search_fetch_k
        self._pinecone_key = pinecone_key
        self._filter_initialized = has_filter

        self._init_chain()
        

    @validate_credential(creds=[Credential.OPENAI, Credential.DATASET_S3_BUCKET])
    def _init_chain(self):
        """Initialize the processing chain."""
        if self._pinecone_key:
            store_env_var("PINECONE_API_KEY", self._pinecone_key)

        try:
            self._embeddings = OpenAIEmbeddings(model=self._embed_model)
        except Exception as e:
            logger.error(f"failed to setup OpenAI embedding mode: {e}")

        try:
            self._vectorstore = PineconeVectorStore(
                index_name=self._pinecone_index_name, embedding=self._embeddings
            )
        except Exception as e:
            logger.error(f"failed to setup pinecone vector store: {e}")

        try:
            self._model = ChatOpenAI(model=self._gen_model, temperature=0)
        except Exception as e:
            logger.error(f"failed to setup OpenAI generation model: {e}")

        # search kwargs creation based on base type
        self._search_kwargs = {}
        if self._search_type == "mmr":
            self._search_kwargs = {
                "k": self._search_k,
                "fetch_k": self._search_fetch_k,
                "lambda_mult": self._search_lambda,
            }
        elif self._search_type == "similarity":
            self._search_kwargs = {"k": self._search_k}

class BedrockSolution(AbstractSolution):
    """
    Implementation of the AbstractSolution for Bedrock.

    Attributes:
        list_context (bool): Flag to list context as strings.
        _embed_model (str): Model for embeddings.
        _gen_model (str): Model for generation.
        _search_type (str): Type of search (e.g., similarity, mmr).
        _search_k (int): Number of top results to retrieve.
        _search_lambda (float): Lambda parameter for MMR search.
        _search_fetch_k (int): Number of results to fetch initially.
        _temperature (float): Specifies the temperature for the generation model.
        _knowledge_base_id (str): ID of KnowledgeBase used.
        chain (RunnableParallel): The processing chain.
    """
    @validate_credential(creds=[Credential.AWS])
    def __init__(
        self,
        list_context: bool = True,
        embed_model: str = "Embed Multilingual",
        gen_model: str = "Llama 3.1 405b Instruct",
        search_type: str = "SEMANTIC",
        search_k: int = 4,
        temperature: float = 0.0,
        has_filter: bool = False,
        s3_rules_file_key: str = None,
        knowledge_base_id="9URSIQVMYB",
        region_name="us-west-2",
        endpoint_url="https://bedrock-runtime.us-west-2.amazonaws.com",
    ):
        super().__init__(has_filter = has_filter,
                         s3_rules_file_key=s3_rules_file_key,
                         list_context=list_context
            )

        
        self._embed_model = embed_model
        self._gen_model = gen_model
        self._search_type = search_type
        self._search_k = search_k
        self._temperature = temperature
        self._filter_initialized = has_filter
        self._knowledge_base_id = knowledge_base_id
        self._region_name = region_name
        self._endpoint_url = endpoint_url
        self._search_kwargs = {}
        self._init_chain()
        

    @validate_credential(creds=[Credential.DATASET_S3_BUCKET])
    def _init_chain(self):
        """Initialize the processing chain."""

        self._bedrock_session = boto3.session.Session(region_name=self._region_name)
        bedrock_client = self._bedrock_session.client(
            service_name="bedrock-runtime",
            config=BOTO_CONFIG
        )
        bedrock_retrieval_client = self._bedrock_session.client(
            service_name="bedrock-agent-runtime",
            config=BOTO_CONFIG
        )

        try:
            self._embeddings = BedrockEmbeddings(
                model_id=BEDROCK_MODEL_IDS[self._embed_model], 
                client=bedrock_client
            )
        except Exception as e:
            logger.error(f"failed to setup Bedrock embedding model: {e}")

        try:
            self._vectorstore = AmazonKnowledgeBasesRetriever(
                knowledge_base_id=self._knowledge_base_id,
                retrieval_config={"vectorSearchConfiguration": {"numberOfResults": self._search_k, "overrideSearchType": self._search_type}},
                client=bedrock_retrieval_client
            )
        
        except Exception as e:
            logger.error(f"failed to setup amazon knowledge base retreiver: {e}")

        try:
            self._model = ChatBedrockConverse(
                client=bedrock_client,
                model_id=BEDROCK_MODEL_IDS[self._gen_model],
                temperature=self._temperature,
                endpoint_url=self._endpoint_url,
                max_tokens=2048
            )
        except Exception as e:
            logger.error(f"failed to setup Bedrock generation model: {e}")
    
    def _parse_context(self, token) -> dict:
        """
        Parser function to return unified response.

        Args:
            token: The token to process.

        Returns:
            dict: The unified response dictionary.
        """
        return {
            "context":
            [
                {
                    "metadata": {
                        "link":context_i.metadata['source_metadata']['link'], 
                        "name":context_i.metadata['source_metadata']['name'], 
                        "path":context_i.metadata['source_metadata']['path'], 
                        "rules":context_i.metadata['source_metadata']['rules']
                    },
                    "type":context_i.type
                }
                
            for context_i in token['context']
            ]
        }
    
    def _make_retriever(self, retriever, *args):
        """
        Returns retriever.

        Args:
            retriever: Retriever to be returned.
            *args: Additional arguments used in the superclass but ignored in this method.
        """
        return retriever

class BedrockPineconeSolution(AbstractSolution):
    """
    Implementation of the AbstractSolution for Bedrock Pinecone.

    Attributes:
        list_context (bool): Flag to list context as strings.
        _pinecone_index_name (str): Name of the Pinecone index.
        _embed_model (str): Model for embeddings.
        _gen_model (str): Model for generation.
        _search_type (str): Type of search (e.g., similarity, mmr).
        _search_k (int): Number of top results to retrieve.
        _search_lambda (float): Lambda parameter for MMR search.
        _search_fetch_k (int): Number of results to fetch initially.
        _region_name (str): Bedrock region
        _endpoint_url (str): Bedrock endpoint url
        _temperature (float): Specifies the temperature for the generation model.
        chain (RunnableParallel): The processing chain.
    """

    def __init__(
        self,
        list_context: bool = True,
        pinecone_index_name: str = "2024-10-27-10-15-35",
        embed_model: str = "Embed Multilingual",
        gen_model: str = "Llama 3.1 405b Instruct",
        search_type: str = "mmr",
        search_k: int = 8,
        search_lambda: float = 0.25,
        search_fetch_k: int = 20,
        region_name: str = "us-west-2",
        endpoint_url: str = "https://bedrock-runtime.us-west-2.amazonaws.com",
        temperature: float = 0.0,
        has_filter: bool = True,
        s3_rules_file_key: str = None,
    ):
        super().__init__(has_filter = has_filter,
                         s3_rules_file_key=s3_rules_file_key,
                         list_context=list_context
            )
        self._pinecone_index_name = pinecone_index_name
        self._embed_model = embed_model
        self._gen_model = gen_model
        self._search_type = search_type
        self._search_k = search_k
        self._search_lambda = search_lambda
        self._search_fetch_k = search_fetch_k
        self._region_name = region_name
        self._endpoint_url = endpoint_url
        self._temperature = temperature
        self._filter_initialized = has_filter

        self._init_chain()
        
    @validate_credential(creds=[Credential.PINECONE_COHERE])
    def _init_chain(self):
        """Initialize the processing chain."""
        self._bedrock_session = boto3.session.Session(region_name=self._region_name)
        bedrock_client = self._bedrock_session.client(
            service_name="bedrock-runtime",
            config=BOTO_CONFIG
        )

        try:
            self._embeddings = BedrockEmbeddings(
                model_id=BEDROCK_MODEL_IDS[self._embed_model], 
                client=bedrock_client
            )
        except Exception as e:
            logger.error(f"failed to setup Bedrock embedding model: {e}")

        try:
            self._vectorstore = PineconeVectorStore(
                index_name=self._pinecone_index_name, embedding=self._embeddings, pinecone_api_key=os.environ.get('PINECONE_COHERE_EMBED_KEY')
            )
        except Exception as e:
            logger.error(f"failed to setup pinecone vector store: {e}")

        try:
            self._model = ChatBedrockConverse(
                client=bedrock_client,
                model_id=BEDROCK_MODEL_IDS[self._gen_model],
                temperature=self._temperature,
                endpoint_url=self._endpoint_url,
                max_tokens=2048
            )
        except Exception as e:
            logger.error(f"failed to setup Bedrock generation model: {e}")

        # search kwargs creation based on base type
        self._search_kwargs = {}
        if self._search_type == "mmr":
            self._search_kwargs = {
                "k": self._search_k,
                "fetch_k": self._search_fetch_k,
                "lambda_mult": self._search_lambda,
            }
        elif self._search_type == "similarity":
            self._search_kwargs = {"k": self._search_k}
    
    def _parse_context(self, token) -> dict:

        """
        Parser function to return unified response.

        Args:
            token: The token to process.

        Returns:
            dict: The unified response dictionary.
        """
        return {
            "context":
            [
                {
                    "metadata": {
                        "link":document.metadata['link'], 
                        "name":document.metadata['name'], 
                        "path":document.metadata['path'], 
                        "rules":document.metadata['rules']
                    },
                    "type":"Document"
                }
                
            for document in token['context']
            ]
        }
