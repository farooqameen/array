from enum import Enum, auto

from langsmith.evaluation import LangChainStringEvaluator
from common.utils import Credential, validate_credential
from langsmith.schemas import Example, Run
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from .deepeval_custom import (
    HallucinationMetricCustom, 
    FaithfulnessMetricCustom, 
    ContextualRelevancyMetricCustom, 
    ContextualRecallMetricCustom, 
    ContextualPrecisionMetricCustom,
    GEvalCustom,
    BiasMetricCustom,
    AnswerRelevancyMetricCustom
)
from .judge_models import get_judge_model, JudgeName
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] {%(module)s::%(funcName)s} %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Prototype")

class Evaluator(Enum):
    """
    Enum for various types of evaluators. [NOTE: makes evaluator keys deterministic rather than string-based]
    """
    doc_relevance = auto(),
    hallucination = auto(),
    noise_awareness = auto(),
    correctness = auto(),
    de_contextual_relevancy = auto(),
    de_contextual_recall = auto(),
    de_contextual_precision = auto(),
    de_hallucination = auto(),
    de_faithfulness = auto(),
    de_noise_awarness = auto(),
    de_correctness = auto(),
    de_answer_relevancy = auto(),
    de_bias = auto()


@validate_credential(creds=[Credential.OPENAI])
def setup_evaluators(judge_name:str, judge_config:dict) -> dict:
    """
    Sets up the evaluators using the specified judge model.

    Args:
        judge_model (str): The model to be used for evaluation, default is "gpt-4o".
    
    Returns:
        dict: A dictionary of evaluators keyed by their respective `Evaluator` enum.
    """

    # judge-model object for Langchain evaluators
    model_for_de_evaluators, model_for_langchain_evaluators = get_judge_model(
        judge_name= judge_name,
        judge_config= judge_config
    )
    logger.info(f"Evaluators model objects: {model_for_de_evaluators}, {model_for_langchain_evaluators}")
    available_evaluators = {}
    if model_for_langchain_evaluators:
        # Document Relevance Evaluator
        doc_relevance_evaluator = LangChainStringEvaluator("score_string",config={"llm":model_for_langchain_evaluators,
            "criteria":{
                    "relevance":"""The Assistant's answer is a set of documents retrieved from a vectorstore.
                    the input is a question used for retrieval. You will score whether the Assistant's answer (retrieved docs) 
                    are relevant to the input question. A score of [[1]] means that the Assistant's answer is not at all relevant
                    to the input question. A score of [[5]] means that the Assistant's answer contains some documents that are relevant
                    to the input question. 
                    A score of [[10]] means that all of the assistant's answer are relevant to the input question"""
            },
                "normalize_by":10
        }, prepare_data=lambda run, example:{  
            "prediction":  run.outputs['context'],
            "input": example.inputs['question']})
        

        # Hallucination Evaluator
        hallucination_evaluator = LangChainStringEvaluator("labeled_score_string",config={"llm":model_for_langchain_evaluators,
            "criteria":{
                "hallucination":"""Is the Assistant's answer fully supported by the Ground Truth documentation? A score
                of [[10]] means the Assistant's answer is not at all supported by the Ground Truth documentation.
                A score of [[5]] means that the Assistant's answer contains some information (e.g, a hallucination) that is
                not captured in the Ground Truth documentation. A score of [[1]] means that the Assistant's answer is fully
                based upon / supported by the Ground Truth documentation. This scoring is used to make sure the Assistant does not make stuff up or lie"""
            },
                "normalize_by":10
        }, prepare_data=lambda run, example:{
                "prediction": run.outputs['answer'],
                "reference": run.outputs['context'],
                "input": example.inputs['question']})
        

        # Noise Awareness Evaluator
        noise_awareness = LangChainStringEvaluator("labeled_score_string",config={"llm":model_for_langchain_evaluators,
            "criteria":{
                "awareness":"""The Assistant's is given an input question that cannot be answered correctly without
                getting more information from the User. The Ground truth provided is a number, either 0 or 1. A Ground truth of 1
                indicates that the input question cannot be answered without more information while a 0 indicates the question can be answered. 
                If the Ground truth is 1: 
                A score of [[10]] means the Assistant's answer includes asking the User to provide more context for the input question or it is a general summary of different possible answers while stating that the Assistant is unsure which is correct.
                A score of [[1]] means the Assistant's answer does not show awareness that it needs more context for the input question to answer it correctly
                If the Ground truth is 0, the score is always [[10]]"""
            },
                "normalize_by":10
        }, prepare_data=lambda run, example:{
                "prediction": run.outputs['answer'],
                "reference": example.outputs['noise'],
                "input": example.inputs['question']})


        # Correctness Evaluator
        correctness_evaluator = LangChainStringEvaluator("labeled_score_string", config={"llm": model_for_langchain_evaluators,
            "criteria":{
                "correctness":"""You are a teacher grading a quiz.
                You are given a question (input), the context the question is about (reference), and the student's answer (prediction). You are asked to score the student's answer as either CORRECT or INCORRECT, based on the context. 
                For a CORRECT answer, output [[10]]. If the answer is INCORRECT, output [[1]]. If the answer is PARTICALLY CORRECT, output a range between [[2]] to [[9]] where a higher number is more CORRECT.
                If the context of the question (reference) mentions that there are is not enough information to answer the question fully or it asks for more information, the student's answer (prediction) shoult contain that. 
                Otherwise, the student's answer (prediction) is INCORRECT, as the student cannot avoid answering the question by saying there is not enough information although the context (reference) suggests there is enough information.
                Write out in a step by step manner your reasoning to be sure that your conclusion is correct. Avoid simply stating the correct answer at the outset.

                Example Format:
                QUESTION: question here
                CONTEXT: context the question is about here
                STUDENT ANSWER: student's answer here
                EXPLANATION: step by step reasoning here
                GRADE: A score of[[10]] for CORRECT, or a score of [[1]] for INCORRECT here"""
            },
                "normalize_by":10
        }, prepare_data=lambda run, example:{
            "prediction": run.outputs['answer'],
            "reference": example.outputs['answer'],
            "input": example.inputs['question']})
        
        available_evaluators.update({
            Evaluator.doc_relevance: doc_relevance_evaluator,
            Evaluator.hallucination: hallucination_evaluator,
            Evaluator.noise_awareness: noise_awareness,
            Evaluator.correctness: correctness_evaluator
        })


    # DeepEval Contextual Relevancy Evaluator
    def de_contextual_relevancy_evaluator(run: Run, example: Example) -> dict:
        """
        DeepEval Contextual Relevancy Evaluator:
        Compares the retrieved Context to the input question
        Evaluates whether the text chunk size and top-K of your retriever is able to retrieve information without much irrelevancies

        Args:
            run (Run): Langsmith run object containing outputs from the model.
            example (Example): Langsmith example object containing inputs and outputs from the test dataset.

        Returns:
            dict: A dictionary with evaluation key and score.
        """
        test_case = LLMTestCase(
            input= example.inputs['question'],
            actual_output= run.outputs['answer'],
            retrieval_context= run.outputs['context'],
            context= run.outputs['context']
        )
        metric = ContextualRelevancyMetricCustom(include_reason=True, threshold=0.7, model= model_for_de_evaluators)
        metric.measure(test_case)
        return {"key" : "contextual_relevancy(DE)", "score": metric.score}


    # DeepEval Contextual Recall Evaluator
    def de_contextual_recall_evaluator(run: Run, example: Example) -> dict:
        """
        DeepEval Contextual Recall Evaluator:
        Compares the retrieved Context to the labeled Answer
        Evaluates whether the embedding model in your retriever is able to accurately capture and retrieve relevant information based on the context of the input

        Args:
            run (Run): Langsmith run object containing outputs from the model.
            example (Example): Langsmith example object containing inputs and outputs from the test dataset.

        Returns:
            dict: A dictionary with evaluation key and score.
        """
        test_case = LLMTestCase(
            input= example.inputs['question'],
            actual_output= run.outputs['answer'],
            expected_output= example.outputs['answer'],
            retrieval_context= run.outputs['context'],
            context= run.outputs['context']
        )
        metric = ContextualRecallMetricCustom(include_reason=True, threshold=0.7, model= model_for_de_evaluators)
        metric.measure(test_case)
        return {"key" : "contextual_recall(DE)", "score": metric.score}
        

    # DeepEval Contextual Precision Evaluator
    def de_contextual_precision_evaluator(run: Run, example: Example) -> dict:
        """
        DeepEval Contextual Precision Evaluator:
        Measures how many significant statements in Context were picked & included in Answer
        Evaluates whether the reranker in your retriever ranks more relevant nodes in your retrieval context higher than irrelevant ones

        Args:
            run (Run): Langsmith run object containing outputs from the model.
            example (Example): Langsmith example object containing inputs and outputs from the test dataset.

        Returns:
            dict: A dictionary with evaluation key and score.
        """
        test_case = LLMTestCase(
            input= example.inputs['question'],
            actual_output= run.outputs['answer'],
            expected_output= example.outputs['answer'],
            retrieval_context= run.outputs['context'],
            context= run.outputs['context']
        )
        metric = ContextualPrecisionMetricCustom(include_reason=True, threshold=0.7, model= model_for_de_evaluators)
        metric.measure(test_case)
        return {"key" : "contextual_precision(DE)", "score": metric.score}
        

    # DeepEval Hallucination Evaluator
    def de_hallucination_evaluator(run: Run, example: Example) -> dict:
        """
        DeepEval Hallucination Evaluator:
        Measures whether all significant statements in the Context are mentioned in the Answer. Does not detect only lies

        Args:
            run (Run): Langsmith run object containing outputs from the model.
            example (Example): Langsmith example object containing inputs and outputs from the test dataset.

        Returns:
            dict: A dictionary with evaluation key and score.
        """
        test_case = LLMTestCase(
            input=example.inputs['question'],
            actual_output=run.outputs['answer'],
            context=run.outputs['context']
        )
        metric = HallucinationMetricCustom(threshold=0.5, model= model_for_de_evaluators)
        metric.measure(test_case)
        return {"key" : "hallucination(DE)", "score": metric.score}
    

    # DeepEval Faithfulness Evaluator
    def de_faithfulness_evaluator(run: Run, example: Example) -> dict:
        """
        DeepEval Faithfulness Evaluator:
        Measures whether Answer contains any statements not provided by Context. Effectively measures lies

        Args:
            run (Run): Langsmith run object containing outputs from the model.
            example (Example): Langsmith example object containing inputs and outputs from the test dataset.

        Returns:
            dict: A dictionary with evaluation key and score.
        """
        test_case = LLMTestCase(
            input= example.inputs['question'],
            actual_output= run.outputs['answer'],
            retrieval_context= run.outputs['context'],
            context= run.outputs['context']
        )
        metric = FaithfulnessMetricCustom(include_reason=True, threshold=0.5, model=model_for_de_evaluators)
        metric.measure(test_case)
        return {"key" : "faithfulness(DE)", "score": metric.score}


    # DeepEval Noise Awareness Evaluator
    def de_noise_awarness_evaluator(run: Run, example: Example) -> dict:
        """
        DeepEval Noise Awareness Evaluator:
        Measures the Assistant's awareness of needing more context to answer the input question.

        Args:
            run (Run): Langsmith run object containing outputs from the model.
            example (Example): Langsmith example object containing inputs and outputs from the test dataset.

        Returns:
            dict: A dictionary with evaluation key and score.
        """
        test_case = LLMTestCase(
            input= example.inputs['question'],
            actual_output= run.outputs['answer'],
            expected_output= example.outputs['noise']
        )
        metric = GEvalCustom(threshold=0.5, name="noise_awareness", model= model_for_de_evaluators,
            evaluation_steps=[
                "check whether the facts in 'actual output' suggest there are not enough information to answer the 'input'",
                "Choose ONLY ONE from the following steps depending on what is the 'expected output'"
                "ONLY if 'expected output' is INSUFFICIENT, 'actual output' must suggest there are not enough information to answer the 'input'",
                "ONLY if 'expected output' is SUFFICIENT, 'actual output' must be able to answer the 'input' question without more information"
            ],
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT])
        metric.measure(test_case)
        return {"key" : "noise_awareness(DE)", "score": metric.score}
    

    # DeepEval Correctness Evaluator
    def de_correctness_evaluator(run: Run, example: Example) -> dict:
        """
        DeepEval Correctness Evaluator:
        Measures the correctness of the Assistant's answer based on the provided context.

        Args:
            run (Run): Langsmith run object containing outputs from the model.
            example (Example): Langsmith example object containing inputs and outputs from the test dataset.

        Returns:
            dict: A dictionary with evaluation key and score.
        """
        test_case = LLMTestCase(
            input= example.inputs['question'],
            actual_output= run.outputs['answer'],
            expected_output= example.outputs['answer']
        )
        metric = GEvalCustom(threshold=0.5, name="correctness", model= model_for_de_evaluators,
            evaluation_steps=[
                "1. Assess whether the 'actual output' conveys the same underlying logic as the 'expected output,' allowing for differences in wording and minor omissions.",
                "2. Check if both outputs directly address the question and remain relevant to the topic.",
                "3. Recognize that minor vagueness or omission of non-essential details does not affect overall logical equivalence."
            ],
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT])
        metric.measure(test_case)
        return {"key" : "correctness(DE)", "score": metric.score}

    # DeepEval Answer Relevancy Evaluator
    def de_answer_relevancy_evaluator(run: Run, example: Example) -> dict:
        """
        DeepEval Answer Relevancy Evaluator:
        Measures whether Answer is erelevant to question

        Args:
            run (Run): Langsmith run object containing outputs from the model.
            example (Example): Langsmith example object containing inputs and outputs from the test dataset.

        Returns:
            dict: A dictionary with evaluation key and score.
        """
        test_case = LLMTestCase(
            input= example.inputs['question'],
            actual_output= run.outputs['answer'],
            context= run.outputs['context']

            
        )
        metric = AnswerRelevancyMetricCustom(include_reason=True, threshold=0.5, model=model_for_de_evaluators)
        metric.measure(test_case)
        return {"key" : "answer_relevancy(DE)", "score": metric.score}
    
    # DeepEval bias Evaluator
    def de_bias_evaluator(run: Run, example: Example) -> dict:
        """
        DeepEval Bias Evaluator:
        Measures whether Answer is biased due to gender, georgraphy, politics, ethnic, etc...

        Args:
            run (Run): Langsmith run object containing outputs from the model.
            example (Example): Langsmith example object containing inputs and outputs from the test dataset.

        Returns:
            dict: A dictionary with evaluation key and score.
        """
        test_case = LLMTestCase(
            input= example.inputs['question'],
            actual_output= run.outputs['answer'],
            context= run.outputs['context']
            
        )
        metric = BiasMetricCustom(include_reason=True, threshold=0.5, model=model_for_de_evaluators)
        metric.measure(test_case)
        return {"key" : "Bias(DE)", "score": metric.score}
    
    available_evaluators.update({
        Evaluator.de_contextual_relevancy: de_contextual_relevancy_evaluator,
        Evaluator.de_contextual_recall: de_contextual_recall_evaluator,
        Evaluator.de_contextual_precision: de_contextual_precision_evaluator,
        Evaluator.de_hallucination: de_hallucination_evaluator,
        Evaluator.de_faithfulness: de_faithfulness_evaluator,
        Evaluator.de_noise_awarness: de_noise_awarness_evaluator,
        Evaluator.de_correctness: de_correctness_evaluator,
        Evaluator.de_answer_relevancy: de_answer_relevancy_evaluator,
        Evaluator.de_bias: de_bias_evaluator,
    })
    # return all evaluators 
    return available_evaluators
    
    

@validate_credential(creds=[Credential.OPENAI])
def activate_evaluators(requested_evaluators: list,
                        judge_name: str = JudgeName.OPENAI,
                        judge_config: dict = {"judge_model":"gpt-4o"}
                    ) -> list:
    """
    Generate a list of evaluators from config file

    Args:
        evaluators_config: The list of evaluators found in automated_test_config
        judge_model (str): The model to be used for evaluation, default is "gpt-4o".
    
    Returns:
        list: A list of evaluators
    """
    if requested_evaluators is None or len(requested_evaluators) == 0:
        logger.warning(f"no evaluators were found in config file")
        return []
    
    available_evaluators = setup_evaluators(
        judge_name = judge_name,
        judge_config= judge_config
    )

    # map evaluators to string-names
    available_evaluators = {key.name: value for key,value in available_evaluators.items()}
    # filter for the evaluators specified in config 
    active_evaluators = []
    for evaluator_name, evaluator_func in available_evaluators.items():
        if evaluator_name in requested_evaluators:
            active_evaluators.append(evaluator_func)
    
    if len(active_evaluators) != len(requested_evaluators):
        logger.warning(f"Some evaluators in config file were not activated")
    
    return active_evaluators
