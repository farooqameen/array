from langsmith import Client
from langsmith.evaluation import evaluate
import time, logging, os, argparse
from .evaluators import activate_evaluators
from common.utils import Credential, validate_credential, load_config
from common.constants import LANGSMITH_SPLIT_TIME_BUFF
from common.chain_generator import Citation, generate_chain, AbstractSolution


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] {%(module)s::%(funcName)s} %(message)s",
    handlers=[
        #logging.FileHandler("crawler_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Prototype")


@validate_credential(creds=[Credential.LANGSMITH])
def run_test(solution: AbstractSolution, 
             automated_test_config: dict = None,
             dataset_name: str = None,
             split_data: bool = None, 
             per_q_repeat: int = None,
             split_time_buff: int = None,
             experiment_name: str = None,
             splits: list[str] = None,
             evaluators: list = None,
             judge_name: str = None,
             judge_config: str = None):
    """
    Execute Langsmith evaluation on the given solution with specified configurations.

    Args:
        solution (AbstractSolution): The solution to be tested.
        automated_test_config (dict): the dict containing automated test configuration
        dataset_name (str): The name of the langmsith dataset to use. [NOTE: must be already uploaded to Langsmith]
        split_data (bool): Whether to split the data for testing. [True: validate splits] [False: validate entire dataset]
        splits (list[str]): The data splits to use if splitting data. [NOTE: must be provided if split_data = True]
        per_q_repeat (int): Number of repetitions per question.
        split_time_buff (int): Buffer time between splits.
        experiment_name (str): The name of the experiment.
    """
    if not split_time_buff:
        split_time_buff = LANGSMITH_SPLIT_TIME_BUFF
        
    if automated_test_config is not None:
        if "evaluators" not in automated_test_config\
            or "dataset_name" not in automated_test_config\
            or "per_q_repeat" not in automated_test_config\
            or "split_data" not in automated_test_config\
            or "splits" not in automated_test_config\
            or "judge_name" not in automated_test_config\
            or "judge_config" not in automated_test_config\
            or "experiment_name" not in automated_test_config\
            or "max_concurrancy" not in automated_test_config:
                logger.error("Some automated test config are missing. Exiting...")
                return

        dataset_name = automated_test_config["dataset_name"]
        per_q_repeat = automated_test_config["per_q_repeat"]
        split_data = automated_test_config["split_data"]
        splits = automated_test_config["splits"]
        judge_name = automated_test_config["judge_name"]
        judge_config = automated_test_config["judge_config"]
        experiment_name = automated_test_config["experiment_name"]
        evaluators = automated_test_config["evaluators"]
        max_concurrancy = automated_test_config["max_concurrancy"]
        
        if "split_time_buff" in automated_test_config:
            split_time_buff = automated_test_config["split_time_buff"]

    if split_data and (not splits or len(splits) == 0):
        logger.error(f"Instructed to evaluate splits separately, but no split names were provided. Exiting...")
        return
    
    try:
        langsmith_client = Client()
    except Exception as err:
        logger.error(f"langsmith client instantiation failed.. exiting.. {err}")
        return
    
    evaluators = activate_evaluators(requested_evaluators= evaluators, 
                                     judge_name=judge_name,
                                     judge_config=judge_config
                )

    experiment_results = None
    try:
        if not split_data:
            experiment_results = evaluate(
                solution.test,
                data=dataset_name,
                evaluators= evaluators,
                experiment_prefix=f"{experiment_name}",
                metadata={"data": f"{dataset_name}: Base"},
                num_repetitions=per_q_repeat,
                max_concurrency=max_concurrancy)
        else:
            for split in splits:
                experiment_results = evaluate(
                    solution.test,
                    data=langsmith_client.list_examples(dataset_name=dataset_name, splits=[split]),
                    evaluators= evaluators,
                    experiment_prefix=f"{experiment_name}",
                    metadata={"data": f"{dataset_name}: {split}"},
                    num_repetitions=per_q_repeat,
                    max_concurrency=max_concurrancy)
                time.sleep(split_time_buff)
    except Exception as err:
        logger.error(f"langsmith evaluation failed: {err}")
        return None

    # parse langsmith results
    logger.info(f"Parsing evaluation results")
    extracted_data = []
    for row in experiment_results:
        try:
            extracted_row = {
                    "inputs_question": row['run'].inputs['inputs']['question'],
                    "output_answer": row['run'].outputs['answer'],
                    "label_answer": row['example'].outputs['answer']
                }
            extracted_row.update({result.key: result.score for result in row['evaluation_results']['results']})
            extracted_data.append(extracted_row)
        except Exception as e:
            logger.error(f"failed to extract evaluation result row: {e}")
            continue
    logger.info(f"finished parsing evaluation results")
    return extracted_data


def _store_test_result_pkl(
                        results, 
                        output_path:str = os.path.join(os.path.dirname(__file__), '..', "data", "test-result.pkl")
                    ):
    """utility to store automated evaluation results as a pickle file"""
    try:
        import pickle
        logger.info(f"Dumping evaluation results in {output_path}")
        with open(output_path, 'wb') as file:
            pickle.dump(results, file)
        logger.info(f"Finished dumping results in {output_path}")
    except Exception as e:
        logger.error(f"Failed to store test results as pickle file: {e}")


def _store_test_result_csv(
                        results, 
                        output_path:str = os.path.join(os.path.dirname(__file__), '..', "data", "test-result.csv")
                    ):
    """utility to store automated evaluation results as a csv file"""
    try:
        import pandas as pd
        
        # Initialize the DataFrame with the desired columns
        data = pd.DataFrame(columns=['id','input_question', 'output_answer', 'label_answer', 'contextual_recall', 'faithfulness', 'correctness'])
    
        # Loop through each row in raw_data and concatenate it to 'data'
        logger.info(f"Creating evaluation results dataframe")
        for row in results:
            # Create a new DataFrame for each row and concatenate it with 'data'
            data = pd.concat([data, pd.DataFrame({
                                                'input_question': [row['inputs_question']],
                                                'output_answer': [row['output_answer']],
                                                'label_answer': [row['label_answer']],
                                                'contextual_recall': [row['contextual_recall(DE)']],
                                                'faithfulness': [row['faithfulness(DE)']],
                                                'correctness': [row['correctness(DE)']]

                                                })],
                            ignore_index=True)
        logger.info(f"Dumping evaluation results in {output_path}")
        data.to_csv(output_path)
        logger.info(f"Finished dumping results in {output_path}")
    except Exception as e:
        logger.error(f"Failed to store test results as csv file: {e}")


def main():
    """
    Main function to execute the testing pipeline based on configuration.

    This function performs the following steps:
    1- load configuration file using environment variable
    2- generates a chain using the configuration file
    3- determine which test-type to execute, simple-cmd or langchain automated test
    4- execute the test using generated chain
    """

    # Create the argument parser
    parser = argparse.ArgumentParser(description='Prototype')
    # Add the config argument
    parser.add_argument("-c", "--config", action='store', help="Input Config File (Required)", required=True)
    # To skip prompting the user to input keys manually. For use inside Dockerfile
    parser.add_argument("-s", "--skip", action='store_true', help="use in-package .aws folder")
    # Parse the command-line arguments
    args = parser.parse_args()

    # Initialize execution flags
    chain_config, test_config = load_config(args.config)
    
    if not chain_config:
        logger.error("chain_config does not exist in config file. Aborting...")
        return
    
    if not test_config:
        logger.error("automated_test_config does not exist in config file. Aborting...")
        return
    
    # generate chain from config file
    solution = generate_chain(chain_config)

    # execute simple cmd test 
    if test_config['exe_simple_test']:
        # ask chain a simple question
        result = solution.invoke("how many volumes are there in the cbb rulebook?")
        # print response
        print(result.response)
        citations = Citation.extract_citations(result)
        # print citations
        for citation in citations:
            print(f"Page Content: {citation.page_content}")
            print("Source:", citation.metadata)
            print()

    # execute langchain automated test
    elif test_config['exe_automated_test']:
        # exit if test-config not available
        if "automated_test_config" not in test_config:
            logger.error("No automated test config found. exiting...")
            return
        automated_test_config = test_config["automated_test_config"]
                
        # execute automated test
        result = run_test(solution= solution, 
                 automated_test_config= automated_test_config)
        
        # store results locally
        if result:
            os.makedirs(os.path.join(os.path.dirname(__file__), '..', "data"), exist_ok=True)
            _store_test_result_pkl(result)
            _store_test_result_csv(result)

if __name__ == "__main__":
    main()