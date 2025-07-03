"""
deepeval_custom.py

EDIT THIS MODULE AT YOUR OWN RISK

Purpose:
    We rely on DeepEval evaluators to execute automated tests. 
    The DeepEval library has compatibility issues with Langsmith.

    This module overrides certain APIs from the DeepEval library in order to overcome numerious issues


Warning:
    These changes to the API are fragile. Any edits here must be made with caution
"""

from deepeval.metrics import (
    HallucinationMetric, 
    FaithfulnessMetric, 
    ContextualRelevancyMetric, 
    ContextualRecallMetric, 
    ContextualPrecisionMetric,
    GEval,
    AnswerRelevancyMetric,
    BiasMetric,
    SummarizationMetric
)

from typing import Union, List
from pydantic import BaseModel, Field
from enum import Enum
from deepeval.test_case import (
    LLMTestCase,
    LLMTestCaseParams,
    ConversationalTestCase,
)
from deepeval.utils import (
    get_or_create_event_loop,
    generate_uuid,
    prettify_list,
)
from deepeval.metrics.utils import (
    print_intermediate_steps,
    validate_conversational_test_case,
    check_llm_test_case_params,
)
required_params: List[LLMTestCaseParams] = [
    LLMTestCaseParams.INPUT,
    LLMTestCaseParams.ACTUAL_OUTPUT,
    LLMTestCaseParams.CONTEXT,
]

'''

'''
class GEvalResponse(BaseModel):
    score: float
    reason: str

class GEvalCustom(GEval):
    '''
    Overrides DeepEval GEval evaluator

    Used by:
        - de_noise_awarness_evaluator
        - de_correctness_evaluator
    '''
    def measure(
        self,
        test_case: Union[LLMTestCase, ConversationalTestCase],
    ) -> float:
        if isinstance(test_case, ConversationalTestCase):
            test_case = validate_conversational_test_case(test_case, self)
        check_llm_test_case_params(test_case, self.evaluation_params, self)

        self.evaluation_cost = 0 if self.using_native_model else None
        # with metric_progress_indicator(self):
        if self.async_mode:
            loop = get_or_create_event_loop()
            (
                self.evaluation_steps,
                self.score,
                self.reason,
                self.success,
            ) = loop.run_until_complete(self._measure_async(test_case))
        else:
            self.evaluation_steps: List[str] = (
                self._generate_evaluation_steps()
            )
            g_score, reason = self.evaluate(test_case)
            self.reason = reason
            self.score = float(g_score) / 10
            self.score = (
                0
                if self.strict_mode and self.score < self.threshold
                else self.score
            )
            self.success = self.score >= self.threshold
            if self.verbose_mode:
                print_intermediate_steps(
                    self.__name__,
                    steps=[
                        f"Evaluation Steps:\n{prettify_list(self.evaluation_steps)}\n",
                        f"Score: {self.score}\nReason: {self.reason}",
                    ],
                )
            return self.score


class HallucinationVerdict(BaseModel):
    verdict: str
    reason: str = Field(default=None)

class HallucinationMetricCustom(HallucinationMetric):
    '''
    Overrides DeepEval HallucinationMetric evaluator

    Used by:
        - de_hallucination_evaluator
    '''
    def measure(
        self,
        test_case: Union[LLMTestCase, ConversationalTestCase],
    ) -> float:
        if isinstance(test_case, ConversationalTestCase):
            test_case = validate_conversational_test_case(test_case, self)
        check_llm_test_case_params(test_case, required_params, self)

        self.evaluation_cost = 0 if self.using_native_model else None
        # with metric_progress_indicator(self):
        if self.async_mode:
            loop = get_or_create_event_loop()
            (self.verdicts, self.score, self.reason, self.success) = (
                loop.run_until_complete(self._measure_async(test_case))
            )
        else:
            self.verdicts: List[HallucinationVerdict] = (
                self._generate_verdicts(
                    test_case.actual_output, test_case.context
                )
            )
            self.score = self._calculate_score()
            self.reason = self._generate_reason()
            self.success = self.score <= self.threshold
            if self.verbose_mode:
                print_intermediate_steps(
                    self.__name__,
                    steps=[
                        f"Verdicts:\n{prettify_list(self.verdicts)}\n",
                        f"Score: {self.score}\nReason: {self.reason}",
                    ],
                )
            return self.score


class FaithfulnessVerdict(BaseModel):
    verdict: str
    reason: str = Field(default=None)

class FaithfulnessMetricCustom(FaithfulnessMetric):
    '''
    Overrides DeepEval FaithfulnessMetric evaluator

    Used by:
        - de_faithfulness_evaluator
    '''
    def measure(
        self,
        test_case: Union[LLMTestCase, ConversationalTestCase],
    ) -> float:
        if isinstance(test_case, ConversationalTestCase):
            test_case = validate_conversational_test_case(test_case, self)
        check_llm_test_case_params(test_case, required_params, self)

        self.evaluation_cost = 0 if self.using_native_model else None
        # with metric_progress_indicator(self):
        if self.async_mode:
            loop = get_or_create_event_loop()
            (
                self.truths,
                self.claims,
                self.verdicts,
                self.score,
                self.reason,
                self.success,
            ) = loop.run_until_complete(self._measure_async(test_case))
        else:
            self.truths: List[str] = self._generate_truths(
                test_case.retrieval_context
            )
            self.claims: List[str] = self._generate_claims(
                test_case.actual_output
            )
            self.verdicts: List[FaithfulnessVerdict] = (
                self._generate_verdicts()
            )
            self.score = self._calculate_score()
            self.reason = self._generate_reason()
            self.success = self.score >= self.threshold
            if self.verbose_mode:
                print_intermediate_steps(
                    self.__name__,
                    steps=[
                        f"Truths:\n{prettify_list(self.truths)}\n",
                        f"Claims:\n{prettify_list(self.claims)}\n",
                        f"Verdicts:\n{prettify_list(self.verdicts)}\n",
                        f"Score: {self.score}\nReason: {self.reason}",
                    ],
                )
            return self.score


class ContextualRelevancyVerdict(BaseModel):
    verdict: str
    reason: str = Field(default=None)

class ContextualRelevancyMetricCustom(ContextualRelevancyMetric):
    '''
    Overrides DeepEval ContextualRelevancyMetric evaluator

    Used by:
        - de_contextual_relevancy_evaluator
    '''
    def measure(
        self,
        test_case: Union[LLMTestCase, ConversationalTestCase],
    ) -> float:
        if isinstance(test_case, ConversationalTestCase):
            test_case = validate_conversational_test_case(test_case, self)
        check_llm_test_case_params(test_case, required_params, self)

        self.evaluation_cost = 0 if self.using_native_model else None
        # with metric_progress_indicator(self):
        if self.async_mode:
            loop = get_or_create_event_loop()
            (self.verdicts, self.score, self.reason, self.success) = (
                loop.run_until_complete(self._measure_async(test_case))
            )
        else:
            self.verdicts: List[ContextualRelevancyVerdict] = (
                self._generate_verdicts(
                    test_case.input, test_case.retrieval_context
                )
            )
            self.score = self._calculate_score()
            self.reason = self._generate_reason(test_case.input)
            self.success = self.score >= self.threshold
            if self.verbose_mode:
                print_intermediate_steps(
                    self.__name__,
                    steps=[
                        f"Verdicts:\n{prettify_list(self.verdicts)}\n",
                        f"Score: {self.score}\nReason: {self.reason}",
                    ],
                )
            return self.score


class ContextualRecallVerdict(BaseModel):
    verdict: str
    reason: str = Field(default=None)

class ContextualRecallMetricCustom(ContextualRecallMetric):
    '''
    Overrides DeepEval ContextualRecallMetric evaluator

    Used by:
        - de_contextual_recall_evaluator
    '''
    def measure(
        self,
        test_case: Union[LLMTestCase, ConversationalTestCase],
    ) -> float:
        if isinstance(test_case, ConversationalTestCase):
            test_case = validate_conversational_test_case(test_case, self)
        check_llm_test_case_params(test_case, required_params, self)
        self.evaluation_cost = 0 if self.using_native_model else None

        # with metric_progress_indicator(self):
        if self.async_mode:
            loop = get_or_create_event_loop()
            (self.verdicts, self.score, self.reason, self.success) = (
                loop.run_until_complete(self._measure_async(test_case))
            )
        else:
            self.verdicts: List[ContextualRecallVerdict] = (
                self._generate_verdicts(
                    test_case.expected_output, test_case.retrieval_context
                )
            )
            self.score = self._calculate_score()
            self.reason = self._generate_reason(test_case.input)
            self.success = self.score >= self.threshold
            if self.verbose_mode:
                print_intermediate_steps(
                    self.__name__,
                    steps=[
                        f"Verdicts:\n{prettify_list(self.verdicts)}\n",
                        f"Score: {self.score}\nReason: {self.reason}",
                    ],
                )
            return self.score


class ContextualPrecisionVerdict(BaseModel):
    verdict: str
    reason: str

class ContextualPrecisionMetricCustom(ContextualPrecisionMetric):
    '''
    Overrides DeepEval ContextualPrecisionMetric evaluator

    Used by:
        - de_contextual_precision_evaluator
    '''
    def measure(
        self,
        test_case: Union[LLMTestCase, ConversationalTestCase],
    ) -> float:
        if isinstance(test_case, ConversationalTestCase):
            test_case = validate_conversational_test_case(test_case, self)
        check_llm_test_case_params(test_case, required_params, self)

        self.evaluation_cost = 0 if self.using_native_model else None
        # with metric_progress_indicator(self):
        if self.async_mode:
            loop = get_or_create_event_loop()
            (self.verdicts, self.score, self.reason, self.success) = (
                loop.run_until_complete(self._measure_async(test_case))
            )
        else:
            self.verdicts: List[ContextualPrecisionVerdict] = (
                self._generate_verdicts(
                    test_case.input,
                    test_case.expected_output,
                    test_case.retrieval_context,
                )
            )
            self.score = self._calculate_score()
            self.reason = self._generate_reason(test_case.input)
            self.success = self.score >= self.threshold
            if self.verbose_mode:
                print_intermediate_steps(
                    self.__name__,
                    steps=[
                        f"Verdicts:\n{prettify_list(self.verdicts)}\n",
                        f"Score: {self.score}\nReason: {self.reason}",
                    ],
                )
            return self.score


class AnswerRelvancyVerdict(BaseModel):
    verdict: str
    reason: str = Field(default=None)

class AnswerRelevancyMetricCustom(AnswerRelevancyMetric):
    def measure(
        self, test_case: Union[LLMTestCase, ConversationalTestCase]
    ) -> float:
        if isinstance(test_case, ConversationalTestCase):
            test_case = validate_conversational_test_case(test_case, self)
        check_llm_test_case_params(test_case, required_params, self)

        self.evaluation_cost = 0 if self.using_native_model else None
        #with metric_progress_indicator(self):
        if self.async_mode:
            loop = get_or_create_event_loop()
            (
                self.statements,
                self.verdicts,
                self.score,
                self.reason,
                self.success,
            ) = loop.run_until_complete(self._measure_async(test_case))
        else:
            self.statements: List[str] = self._generate_statements(
                test_case.actual_output
            )
            self.verdicts: List[AnswerRelvancyVerdict] = (
                self._generate_verdicts(test_case.input)
            )
            self.score = self._calculate_score()
            self.reason = self._generate_reason(test_case.input)
            self.success = self.score >= self.threshold
            if self.verbose_mode:
                print_intermediate_steps(
                    self.__name__,
                    steps=[
                        f"Statements:\n{prettify_list(self.statements)}\n",
                        f"Verdicts:\n{prettify_list(self.verdicts)}\n",
                        f"Score: {self.score}\nReason: {self.reason}",
                    ],
                )
            return self.score
        
class BiasVerdict(BaseModel):
    verdict: str
    reason: str = Field(default=None)

class BiasMetricCustom(BiasMetric):
    def measure(
        self,
        test_case: Union[LLMTestCase, ConversationalTestCase],
    ) -> float:
        if isinstance(test_case, ConversationalTestCase):
            test_case = validate_conversational_test_case(test_case, self)
        check_llm_test_case_params(test_case, required_params, self)

        self.evaluation_cost = 0 if self.using_native_model else None
        #with metric_progress_indicator(self):
        if self.async_mode:
            loop = get_or_create_event_loop()
            (
                self.opinions,
                self.verdicts,
                self.score,
                self.reason,
                self.success,
            ) = loop.run_until_complete(self._measure_async(test_case))
        else:
            self.opinions: List[str] = self._generate_opinions(
                test_case.actual_output
            )
            self.verdicts: List[BiasVerdict] = self._generate_verdicts()
            self.score = self._calculate_score()
            self.reason = self._generate_reason()
            self.success = self.score <= self.threshold
            if self.verbose_mode:
                print_intermediate_steps(
                    self.__name__,
                    steps=[
                        f"Opinions:\n{prettify_list(self.opinions)}\n",
                        f"Verdicts:\n{prettify_list(self.verdicts)}\n",
                        f"Score: {self.score}\nReason: {self.reason}",
                    ],
                )
            return self.score