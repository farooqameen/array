## Project Objective

The primary objective of this project is to develop a RAG chatbot capable of retrieving relevant information from diverse sources and generating coherent responses in real-time. Specifically, we aim to achieve the following goals: 

1. **Implementing a retrieval mechanism:** Explore and implement state-of-the-art techniques, such as the Llama3 model, for retrieving relevant data from knowledge bases. 

2. **Utilizing vector databases:** Investigate and integrate vector database solutions to efficiently store and retrieve semantically similar documents. 

3. **Cloud deployment:** Deploy the RAG chatbot system on the AWS cloud platform to ensure scalability, reliability, and ease of maintenance. 

4. **Building a user-friendly frontend:** Develop an intuitive and interactive frontend interface to facilitate seamless interaction with the chatbot.

------------
## How to Run

### Credentials:

- This project utilizes various API keys stored in a `.env` file. 
- When a particular API key is required during execution, it will automatically be fetched from `AWS Secrets Manager` and stored locally in `.env` (This is handled by `prototype/common/utils/validate_credentials` decorator)

**Hence, you must follow these steps during setup for the first time**

1. create a new folder called `.aws` inside `prototype`
2. create a new file called `config` inside `prototype/.aws` with the following content

```
[default]
region = me-south-1 
```
3. create a new file called `credentials` inside `prototype/.aws` with the following content

```
[default]
aws_access_key_id={get it from aws}
aws_secret_access_key={get it from aws}
aws_session_token={get it from aws}
```
**Note:** Those access keys have expiry times. Ensure that you are constantly updating them to avoid `invalid credentials` error.

**Note:** Do not add any extensions to the file names `config` and `credentials`.

**Side Note**  
- Any inclusion of new APIs requires the following:
  - updating the `CRED_ENV_MAP` dict in `prototype/common/utils`
  - updating the `Credential` enum
  - adding the key in `AWS Secrets Manager` inside `prod/chatbot/backend` and `dev/chatbot/backend` secrets as required with name `{api_key_name}`
  - decorate the function that uses the API with `@validate_credentials(creds=[...])`

### Building Docker Image

- This project must always be run & tested from inside a Docker image. It is also deployed as a Docker image. On Windows, it is recommended to use Git Bash to run the shell commands.

**Build commands**
  -   **local build:** this is for local usage & development (you will only need this)
      -   run `./build.sh local` 
  -   **dev build:**  This image is used for deployment by CICD
      -   run `./build.sh dev` (for deployment)
  -   **prod build:** This image is used for deployment by CICD
      -   run `./build.sh prod` (for deployment)
```
If ./build.sh is failing due to OS compatibility, follow its logic to build manually

All the different dockerfiles & dockerignore are in /dockerfiles folder

copy the desired build's dockerfile & .dockerignore to root dir & use command: docker build prototype:{tag}
```
------------
## Execution Options

### 1. Server: 
**run `docker run -d -p 8000:8000 prototype:local`**


- This will spin-up the FastAPI server used in deployment to serve the chatbot client
- This server will be running in a docker container & listening on localhost/port:8000
- The API endpoint documentation is found here [Chatbot API Endpoints Docs](https://arrayinnovation.sharepoint.com/:fl:/g/contentstorage/CSP_d2563bd2-2f3c-4a2c-828e-b99f429178ca/EV4kZryXltdOrvQYujdJsXEBZhg6MQudCvLoTxvyu-Dnfw?e=yEjRq0&nav=cz0lMkZjb250ZW50c3RvcmFnZSUyRkNTUF9kMjU2M2JkMi0yZjNjLTRhMmMtODI4ZS1iOTlmNDI5MTc4Y2EmZD1iJTIxMGp0VzBqd3ZMRXFDanJtZlFwRjR5bC1OTG1VcHR2bE9tVnZ3SGdVWlFoaHNTa0FSNWZGbVFMMEJFRVNMYy14SyZmPTAxNUg0SFBNMjZFUlRMWkY0VzI1SEs1NUFZWEkzVVRNTFImYz0lMkYmYT1Mb29wQXBwJnA9JTQwZmx1aWR4JTJGbG9vcC1wYWdlLWNvbnRhaW5lciZ4PSU3QiUyMnclMjIlM0ElMjJUMFJUVUh4aGNuSmhlV2x1Ym05MllYUnBiMjR1YzJoaGNtVndiMmx1ZEM1amIyMThZaUV3YW5SWE1HcDNka3hGY1VOcWNtMW1VWEJHTkhsc0xVNU1iVlZ3ZEhac1QyMVdkbmRJWjFWYVVXaG9jMU5yUVZJMVprWnRVVXd3UWtWRlUweGpMWGhMZkRBeE5VZzBTRkJOV1ZjMU5UVkJTazVWVkZFMVEwbEdWa0UzTTBwRlEwb3pNalklM0QlMjIlMkMlMjJpJTIyJTNBJTIyNjBiN2QzZTktMjc0Ni00ZWRkLWExMzQtZjFmMDRkYzBhNjdmJTIyJTdE)

#### Description:
- The server code is in `prototype/backend_server/app.py`
- Upon startup, it will load required environment variables & `Solution` instance
- The `Solution` instance is created using a `config json` whose path is hard-coded in the module




### 2. Test:
**run `docker run prototype:local test`**


- This will execute all the unit-tests found in `tests` directory




### 3. Manual Solution Execution:
**run `docker run prototype:local evaluate config/..._config_file.json`:**


**run w/ storing results locally `docker run -v C:\Users\User\ARRAY\{chat-bot-dir-in-host}:/home/appuser/app/src/prototype/data prototype:local evaluate config/..._config_file.json`**


#### Description:
- We utilize json files to describe Manual Executions. These json files are all saved in `config` directory
- Example `config json`

```
{
    "exe_simple_test": false,
    "exe_automated_test": false,
    "exe_streamlit_app": true,
    "chain_config":{
        "solution_class":"{class-name}",
        "args":{
            // arguments needed to instantiate the class (check chain_generator to figure out the args)
        }
    },
    "automated_test_config":{
        // all of below config must be provided
        "evaluators":["de_contextual_recall","de_faithfulness","de_noise_awarness","de_correctness"],
        "dataset_name":"cbb-test-dataset-v2",
        "per_q_repeat":1,
        "split_data":true,
        "splits": ["opinion"],
        "evaluator_model":"gpt-4o",
        "experiment_name": "{file-name}"
    }
}
```

- Manual solution Execution will load the `config json` and execute based on the parameters it contains
  - **chain_config**
    - `solution_class` : pick a solution class implemented in `prototype/common/chain_generator.py`
    - `args` : all the arguments required to instantiate an object of the chosen class
    - **This is very important as it defines the  `Solution` object during runtime. This `Solution` object is the RAG (chatbot) model used to generate responses. Without it, nothing works**

  - **execution path**
    - `exe_simple_test` : asks the chatbot model a simple question & prints out output in terminal
    - `exe_automated_test` : will execute automated Langsmith testing given the config provided in `automated_test_config`
    - `exe_streamlit_app` " DEPRECATED


------------
## Data
- The RAG (chatbot) Model utilizes a knoweldge base that is created via a separate data pipeline
- Documentation of the different datasets including Knowledge Base & Testing dataset is found here [DataGuide](https://arrayinnovation.sharepoint.com/:fl:/g/contentstorage/CSP_d2563bd2-2f3c-4a2c-828e-b99f429178ca/EfjmV3A4pXtKhroYetnsbowBHmyxm8LJTY4yhqW0oiSxHQ?e=shE3tJ&nav=cz0lMkZjb250ZW50c3RvcmFnZSUyRkNTUF9kMjU2M2JkMi0yZjNjLTRhMmMtODI4ZS1iOTlmNDI5MTc4Y2EmZD1iJTIxMGp0VzBqd3ZMRXFDanJtZlFwRjR5bC1OTG1VcHR2bE9tVnZ3SGdVWlFoaHNTa0FSNWZGbVFMMEJFRVNMYy14SyZmPTAxNUg0SFBNN1k0WkxYQU9GRlBORklOT1FZUExNNlkzVU0mYz0lMkYmYT1Mb29wQXBwJnA9JTQwZmx1aWR4JTJGbG9vcC1wYWdlLWNvbnRhaW5lciZ4PSU3QiUyMnclMjIlM0ElMjJUMFJUVUh4aGNuSmhlV2x1Ym05MllYUnBiMjR1YzJoaGNtVndiMmx1ZEM1amIyMThZaUV3YW5SWE1HcDNka3hGY1VOcWNtMW1VWEJHTkhsc0xVNU1iVlZ3ZEhac1QyMVdkbmRJWjFWYVVXaG9jMU5yUVZJMVprWnRVVXd3UWtWRlUweGpMWGhMZkRBeE5VZzBTRkJOV1ZjMU5UVkJTazVWVkZFMVEwbEdWa0UzTTBwRlEwb3pNalklM0QlMjIlMkMlMjJpJTIyJTNBJTIyNDAwOWI1ZDUtYzk2NC00YmMyLWFiMGUtMzcxOGNlNDUwYWRjJTIyJTdE)

------------
## Automated Testing
- We use a Jupyter notebook for automated chatbot performance testing. You can find the notebook at `prototype/langsmith_testing.ipynb`.
- The test dataset is uploaded, and the evaluation results are logged in Langsmith.

### Creating a Test Dataset

- The first part of the notebook helps create a test dataset from a question bank.
-  This is done by randomly sampling questions from different sections of the question bank to ensure variety.
-  You need to input:
    - Number of sections (windows) to sample from
    - Number of samples per section
    - Filepath to the question bank
- The final dataset size will be `num_windows * sample_size`.

### Running an Automated Test
- The second part of the notebook runs the automated test on the dataset.
- Set the experiment name, which will be used for saving the experiment in Langsmith and the configuration file.

### Start a test-run
- Use the pre-set login credentials for Langsmith:
  - `Email: ebrahim.alhaddad@array.world`
  - `Password: Array@2024Array@2024`
- Sample command:  `docker run -v C:\Users\ZaherAlmudhaweb\projects\chat-bot:/home/appuser/app/src/prototype/data prototype:local evaluate config/config_GPTPineconeSolution_Volume_1_rules_meta_curated_test_12_doc.json`. 
  - This command runs the Docker container, mounts a local directory into the container, and runs an evaluation process inside the container with a specific configuration file.
- You could then go to the Langsmith website and view the report generated for the given data-set name in the intended config file.
- Some common errors like `invalid credentials` are due to the keys expiring from AWS. Ensure you are always changing the keys.

## Detailed Wiki of the project is found here

### [Wiki](https://arrayinnovation.sharepoint.com/:fl:/g/contentstorage/CSP_d2563bd2-2f3c-4a2c-828e-b99f429178ca/EXF5O1_TYCFFmg6lu1ilQfwBtGS8SlYwcyggIaONZ0ofpQ?e=7bW3zY&nav=cz0lMkZjb250ZW50c3RvcmFnZSUyRkNTUF9kMjU2M2JkMi0yZjNjLTRhMmMtODI4ZS1iOTlmNDI5MTc4Y2EmZD1iJTIxMGp0VzBqd3ZMRXFDanJtZlFwRjR5bC1OTG1VcHR2bE9tVnZ3SGdVWlFoaHNTa0FSNWZGbVFMMEJFRVNMYy14SyZmPTAxNUg0SFBNM1JQRTVWN1UzQUVGQ1pVRFZGWE5NS0tRUDQmYz0lMkYmYT1Mb29wQXBwJnA9JTQwZmx1aWR4JTJGbG9vcC1wYWdlLWNvbnRhaW5lciZ4PSU3QiUyMnclMjIlM0ElMjJUMFJUVUh4aGNuSmhlV2x1Ym05MllYUnBiMjR1YzJoaGNtVndiMmx1ZEM1amIyMThZaUV3YW5SWE1HcDNka3hGY1VOcWNtMW1VWEJHTkhsc0xVNU1iVlZ3ZEhac1QyMVdkbmRJWjFWYVVXaG9jMU5yUVZJMVprWnRVVXd3UWtWRlUweGpMWGhMZkRBeE5VZzBTRkJOV1ZjMU5UVkJTazVWVkZFMVEwbEdWa0UzTTBwRlEwb3pNalklM0QlMjIlMkMlMjJpJTIyJTNBJTIyZWRlNzIyODYtZTNhMy00MDk3LTlkNTYtOGM4OTNjNTFiZTFmJTIyJTdE)
