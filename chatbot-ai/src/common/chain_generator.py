import boto3
from abc import ABC, abstractmethod
from opensearchpy import OpenSearch
from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_aws import  ChatBedrockConverse
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain_core.documents import Document
from langchain.vectorstores import OpenSearchVectorSearch
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from langchain_community.embeddings import BedrockEmbeddings
from langchain_aws.chat_models.bedrock_converse import ChatBedrockConverse
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from src.common.utils import  get_aws_session_w_region, create_history_aware_retriever
from src.common.prompts import (
    PROMPT_GENERATION, 
    PROMPT_GENERATE_TITLE, 
    PROMPT_MODIFY_QUESTION_W_HISTORY,
    DOCUMENT_TEMPLATE_BEDROCK,
    DOCUMENT_TEMPLATE_OPENAI
)
from src.common.constants import BEDROCK_MODEL_IDS, BOTO_CONFIG
from src.logs import logger
from src.settings import settings

class AbstractSolution(ABC):
    """
    Abstract base class for solution implementations.

    Provides a template for creating solution chains with common 
    methods for handling chat history and retrievers.
    """

    @abstractmethod
    def _init_services(self) -> None:
        '''
        initialize any services needed for solution
        '''
        pass

    def __init__(self):
        self._model = None
        self._search_kwargs = None
        self.vectorstore = None

    def get_title_chain(self, _session_id:str, user_id:str) -> RunnableWithMessageHistory:
        """
        Create a chain for generating conversation titles.

        Args:
            _session_id (str): Unique identifier for the conversation session.
            user_id (str): Identifier for the user.

        Returns:
            RunnableWithMessageHistory: A chain for generating conversation titles 
            with message history support.
        """
        title_w_history_template = ChatPromptTemplate.from_messages(
            [
                ("system", PROMPT_GENERATE_TITLE),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        chain = title_w_history_template | self._model | StrOutputParser()
        boto3_session = boto3.Session(region_name=settings.default_aws_region)
        return RunnableWithMessageHistory(
            chain,
            lambda session_id: DynamoDBChatMessageHistory(
                boto3_session=boto3_session,
                table_name=settings.chat_history_db_name, 
                session_id=_session_id,
                history_size= settings.history_size,
                key={"SessionId":_session_id, "UserId":user_id}
            ),
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def get_history_aware_chain(self, 
                                user_id:str, 
                                volume_display_name:list[str]=None,
                                subvolume_display_name:list[str]=None,
                                category_display_name:list[str]=None,
                                module_display_name:list[str]=None,
                                chapter_display_name:list[str]=None,
                                section_display_name:list[str]=None,
                                ) -> RunnableWithMessageHistory:
        """
        Create a history-aware retrieval chain.

        Args:
            user_id (str): Identifier for the user.
            volume_display_name (list, optional): Volume display names to filter.
            subvolume_display_name (list, optional): Subvolume display names to filter.
            category_display_name (list, optional): Category display names to filter.
            module_display_name (list, optional): Module display names to filter.
            chapter_display_name (list, optional): Chapter display names to filter.
            section_display_name (list, optional): Section display names to filter.

        Returns:
            RunnableWithMessageHistory: A chain that generates responses 
            based on conversation history and context.
        """
        # template to combine the prompt with fetched chat history
        modify_question_w_history_template = ChatPromptTemplate.from_messages(
            [
                ("system", PROMPT_MODIFY_QUESTION_W_HISTORY),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        request_search_kwargs = self._search_kwargs.copy()
        request_search_kwargs["filters"] = {}
        if volume_display_name:
            request_search_kwargs["filters"]["volume_display_name"] = volume_display_name
        if subvolume_display_name:
            request_search_kwargs["filters"]["subvolume_display_name"] = subvolume_display_name
        if category_display_name:
            request_search_kwargs["filters"]["category_display_name"] = category_display_name
        if module_display_name:
            request_search_kwargs["filters"]["module_display_name"] = module_display_name
        if chapter_display_name:
            request_search_kwargs["filters"]["chapter_display_name"] = chapter_display_name
        if section_display_name:
            request_search_kwargs["filters"]["section_display_name"] = section_display_name

        history_aware_retriever = create_history_aware_retriever(
            self._model,
            self.make_retriever(request_search_kwargs),
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
        temp_dict = {'document_prompt': DOCUMENT_TEMPLATE_BEDROCK if self.vectorstore.__class__ is AmazonKnowledgeBasesRetriever else DOCUMENT_TEMPLATE_OPENAI}
        question_answer_chain = create_stuff_documents_chain(
            self._model, 
            generation_template, 
            **temp_dict)
        
        # combine history aware retriever with generation chain
        history_aware_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        return RunnableWithMessageHistory(
            history_aware_chain,
            lambda session_id: DynamoDBChatMessageHistory(
                boto3_session=get_aws_session_w_region(settings.default_aws_region),
                table_name=settings.chat_history_db_name, 
                session_id=session_id,
                history_size= settings.history_size,
                key={"SessionId":session_id, "UserId":user_id}
            ),
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
    
    @abstractmethod
    def _parse_context(self, token:dict) -> dict:
        """
        Parser function to return unified response.

        Args:
            token (dict): The token to process.

        Returns:
            dict: The unified response dictionary.
        """
        pass

    def parse_context(self, token:dict) -> dict:
        """
        Wrapper method for parsing context with error handling.

        Args:
            token (dict): Token to be parsed.

        Returns:
            dict: Parsed context information or empty dict if parsing fails.
        """
        try:
            return self._parse_context(token)
        except Exception as e:
            logger.error(f"An error occurred while parsing context the chain. {e}")

    @abstractmethod
    def make_retriever(self, kwargs) ->  Any:
        """
        Abstract method to create a retriever from a vector store.

        Args:
            kwargs (dict): Keyword arguments for configuring the retriever.

        Returns:
            Any: A retriever object configured based on the input arguments.
        """
        pass


def generate_chain(chain_config: dict) -> AbstractSolution:
    """
    Generate a solution chain based on the given configuration.

    Args:
        chain_config (dict): Configuration for creating the solution chain.
            Expected format: {
                'solution_class': str, 
                'args': dict
            }

    Returns:
        Optional[AbstractSolution]: An instance of the specified solution class, 
        or None if creation fails.

    Raises:
        ValueError: If the solution class cannot be found or instantiated.
    """
    subclasses = AbstractSolution.__subclasses__()
    solutions = {subclass.__name__: subclass for subclass in subclasses}

    solution_class = ""
    try:
        solution_class = chain_config["solution_class"]
    except Exception as err:
        logger.error(f"'solution_class' cannot be found in config file...")
        raise

    if solution_class in solutions:
        try:
            chain = solutions[solution_class](**chain_config["args"])
        except Exception as err:
            logger.error(f"Failed to instantiate solution object {solution_class}, likely due to invalid configs.")
            logger.error(f"{err}")
            raise
        return chain

    logger.error(f"{solution_class} is not implmeneted...")
    return None

class BedrockOpensearchSolution(AbstractSolution):
    """
    Implementation of the AbstractSolution for Bedrock Pinecone.

    Attributes:
        _embed_model (str): Model for embeddings.
        _gen_model (str): Model for generation.
        _search_fetch_k (int): Number of results to fetch initially.
        _region_name (str): Bedrock region
        _endpoint_url (str): Bedrock endpoint url
        _temperature (float): Specifies the temperature for the generation model.
        chain (RunnableParallel): The processing chain.
    """

    def __init__(
        self,
        embed_model: str = "Embed Multilingual",
        gen_model: str = "Llama 3.1 405b Instruct",
        search_fetch_k: int = 20,
        max_retrieval_docs: int = 10,
        region_name: str = "us-west-2",
        endpoint_url: str = "https://bedrock-runtime.us-west-2.amazonaws.com",
        temperature: float = 0.0,
        vector_field_name: str = "embedding",
        content_field: str = ""
    ):
        super().__init__()
        self._embed_model = embed_model
        self._gen_model = gen_model
        self._search_fetch_k = search_fetch_k
        self._region_name = region_name
        self._endpoint_url = endpoint_url
        self._temperature = temperature
        self._vector_field_name = vector_field_name
        self._max_retrieval_docs = max_retrieval_docs
        self._content_field = content_field
        self._init_services()
        
    def _init_services(self) -> None:
        """
        Initialize AWS Bedrock and OpenSearch services for the solution.

        This method sets up:
        1. AWS Bedrock embedding model
        2. AWS Bedrock generation model
        3. OpenSearch client and vector store

        The method uses the following instance attributes:
        - self._region_name: AWS region for Bedrock services
        - self._embed_model: Embedding model identifier
        - self._gen_model: Generation model identifier
        - self._temperature: Model generation temperature
        - self._endpoint_url: Bedrock endpoint URL

        Side Effects:
        - Sets self._embeddings with BedrockEmbeddings
        - Sets self._model with ChatBedrockConverse
        - Sets self._opensearch_client with OpenSearch client
        - Sets self._vectorstore with OpenSearchVectorSearch
        - Sets self._search_kwargs with retrieval parameters

        Logs errors if any service initialization fails, 
        but does not raise exceptions to allow partial initialization.
        """
        aws_session =get_aws_session_w_region(region_name=self._region_name)
        bedrock_client = aws_session.client(
            service_name="bedrock-runtime",
            config=BOTO_CONFIG
        )
        try:
            self._embeddings = BedrockEmbeddings(
                model_id=BEDROCK_MODEL_IDS[self._embed_model], 
                client=bedrock_client
            )
            _ = self._embeddings.embed_query("test_text")
        except Exception as e:
            logger.error(f"failed to setup Bedrock embedding model: {e}")

        try:
            self._model = ChatBedrockConverse(
                client=bedrock_client,
                model_id=BEDROCK_MODEL_IDS[self._gen_model],
                temperature=self._temperature,
                endpoint_url=self._endpoint_url,
                max_tokens=2048
            )
            _ = self._model.invoke("test")
        except Exception as e:
            logger.error(f"failed to setup Bedrock generation model: {e}")
            
        try:
            self._opensearch_client = OpenSearch(
                hosts=[settings.opensearch_endpoint],
                http_auth=(settings.opensearch_user, settings.opensearch_password),
                use_ssl=True,
                verify_certs=True
            )
            # Custom OpenSearch Vector Store
            self._vectorstore = OpenSearchVectorSearch(
                opensearch_client=self._opensearch_client,
                opensearch_url=settings.opensearch_endpoint,
                index_name=settings.opensearch_index,
                embedding_function=self._embeddings.embed_query
            )
        except Exception as e:
            logger.error(f"failed to setup OpenSearch vector store: {e}")

        # Configurable search parameters
        self._search_kwargs = {
            "max_retrieval_docs":self._max_retrieval_docs,
            "k": self._search_fetch_k,
        }

         
    def make_retriever(self, search_kwargs) -> callable:
        """
        Create a custom retriever for OpenSearch vector search.

        This method generates a retriever function that performs 
        semantic search on OpenSearch using k-nearest neighbors (KNN) 
        with optional filtering capabilities.

        Args:
            search_kwargs (dict): Configuration for search parameters, including:
                - 'filters' (optional): Dictionary of display name filters
                - 'max_retrieval_docs' (optional): Maximum number of documents to retrieve
                - 'k' (optional): Number of nearest neighbors to search

        Returns:
            callable: A custom search function that:
            - Embeds the query using Bedrock embeddings
            - Performs KNN search on OpenSearch
            - Applies optional filters
            - Transforms results into LangChain Document format

        Key Search Behaviors:
        - Uses vector embedding for semantic search
        - Supports multi-field filtering on display names
        - Retrieves document content and metadata
        """
        def custom_search(query: str, **kwa):
            # Extract filter from kwargs if exists
            logger.info(f"SEARCH KWA{search_kwargs}")
            filter_dict = search_kwargs.get('filters', None)

            # Construct OpenSearch vector search query
            knn_query = {
                "size": search_kwargs.get('max_retrieval_docs', 10),
                "query": {
                    "knn": {
                        self._vector_field_name:{
                            "vector": self._embeddings.embed_query(query),
                            "k": search_kwargs.get('k', 10)
                        }
                    }
                }
            }
            if filter_dict:
                knn_query["query"]["knn"][self._vector_field_name]["filter"] = {
                    "bool": {
                        "must": [
                            {
                                "terms":{
                                    f"display_names.{field_name}.keyword":filter_value
                                }
                            } for field_name, filter_value in filter_dict.items()
                        ]
                    }
                }

            # Execute search
            results = self._opensearch_client.search(
                index=settings.opensearch_index, 
                body=knn_query
            )

            # Transform results to match LangChain Document format
            try:
                documents = [
                    Document(
                        page_content=hit['_source']["contents"]["md"],
                        metadata={
                            "link": hit["_source"]["html_link"],
                            "internal_rule_code":hit["_source"]["internal_rule_code"]
                        }                    
                    ) for hit in results['hits']['hits']
                ]
            except Exception as e:
                logger.info(f"{e}")
            return documents
        
        return custom_search

    def _parse_context(self, token:dict) -> dict:
        """
        Parse and transform context from retrieval results.

        Converts retrieved documents into a standardized context format 
        for further processing or response generation.

        Args:
            token (dict): Retrieved context containing document information, 
                        expected to have a 'context' key with a list of documents.

        Returns:
            dict: A structured representation of context metadata, including:
            - 'context': List of document metadata with:
                * 'metadata': Document-specific information
                * 'type': Constant "Document" identifier
        """
        return {
            "context":
            [
                {
                    "metadata": {
                        "link":document.metadata['link'], 
                        "internal_rule_code":document.metadata["internal_rule_code"]
                    },
                    "type":"Document"
                }
                
            for document in token['context']
            ]
        }
