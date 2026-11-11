# Week 05: Generative AI, Prompt Engineering and Loop Engineering

Lab work for Week 05. Every example runs against a local model through Ollama (`qwen2.5:7b`). The running example throughout the week is a preliminary insurance-claim triage assistant that classifies a claim, summarises it and lists missing evidence, without ever approving or denying it.

The work is split into the same four phases as the slides. Each demo from the slides has its own folder. The slide decks are course material and are not included in this repository. If you have them, place `Phase 01.pptx` to `Phase 04.pptx` inside the matching phase folder.

## Folder structure

```
Week 05/
├── README.md
├── requirements.txt
├── Phase_01_GenAI_Foundations/
│   ├── 01_rules_vs_generation/
│   ├── 02_token_generation/
│   ├── 03_concise_vs_noisy_context/
│   ├── 04_temperature_experiment/
│   └── 05_plausibility_vs_evidence/
├── Phase_02_Prompt_Engineering/
│   ├── 01_vague_vs_structured_prompt/
│   ├── 02_prompt_template_and_evaluation/
│   ├── 03_zero_shot_sentiment/
│   ├── 04_zero_vs_few_shot/
│   ├── 05_conflicting_instructions/
│   ├── 06_relevant_vs_irrelevant_context/
│   ├── 07_single_vs_chained_prompts/
│   ├── 08_structured_output_validation/
│   └── 09_self_critique/
├── Phase_03_Loop_Engineering/
│   ├── 01_single_call_vs_loop/
│   ├── 02_state_machine/
│   ├── 03_validation_retry/
│   ├── 04_generate_critique_revise/
│   ├── 05_evaluator_optimizer/
│   ├── 06_plan_execute_observe/
│   ├── 07_termination_budgets/
│   ├── 08_retry_backoff/
│   └── 09_observability_logging/
└── Phase_04_Integration_and_Evaluation/
    └── claim_triage_app/
```

## Requirements

You need Python 3.10 or newer, Ollama, around 8 GB of free RAM for the 7B model and about 5 GB of disk space for the model download.

## Setup

### 1. Install Ollama

Download and install Ollama from https://ollama.com/download. On Windows and macOS the installer starts Ollama in the background. On Linux, start it with `ollama serve` in a separate terminal if it is not already running.

Check the installation:

```
ollama --version
```

### 2. Download the model

```
ollama pull qwen2.5:7b
```

The download is about 4.7 GB, so do this first.

### 3. Create a virtual environment and install the packages

Run these from the `Week 05` folder.

Windows (PowerShell):

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks the activation script, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and try again.

Windows (Command Prompt):

```
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

Linux or macOS:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Check that the model responds

```
ollama run qwen2.5:7b "Reply with one word: hello"
```

The first request is slow because the model is loaded into memory. Later requests are faster.

## Running the code

Always `cd` into a step folder before running its script. Some scripts read a prompt file next to them, and some write their results into the current folder.

After each demo, answer the questions on the "Answer These" slide that follows that demonstration in the phase deck.

### Phase 01: Generative AI Foundations

| Folder | Command | Slide demonstration |
|---|---|---|
| `01_rules_vs_generation` | `python demo.py` | Compare rules with generation |
| `02_token_generation` | `python token_generation.py` | Observe token-by-token generation (`Prompts.txt`) |
| `03_concise_vs_noisy_context` | `python demo_2.py` | Compare concise and noisy context (`Prompts_2.txt`). Run it three times as the slide asks |
| `04_temperature_experiment` | `python demo_3.py` | Temperature experiment |
| `05_plausibility_vs_evidence` | `python plausibility_check.py` | Separate plausibility from evidence (`Prompt_3.txt`) |

Example:

```
cd Phase_01_GenAI_Foundations/01_rules_vs_generation
python demo.py
```

### Phase 02: Prompt Engineering

| Folder | Command | Slide demonstration |
|---|---|---|
| `01_vague_vs_structured_prompt` | `python compare_prompts.py` | Improve a vague prompt (`Prompt.txt`) |
| `02_prompt_template_and_evaluation` | see below | Build a prompt from components |
| `03_zero_shot_sentiment` | `python zero_shot_sentiment.py` | Classification without examples (`Text.txt`) |
| `04_zero_vs_few_shot` | `python demo_6.py` | Zero-shot versus few-shot |
| `05_conflicting_instructions` | `python instruction_hierarchy.py` | Conflicting instructions (`Prompts_2.txt`) |
| `06_relevant_vs_irrelevant_context` | `python demo_7.py` | Relevant versus irrelevant context |
| `07_single_vs_chained_prompts` | `python demo_8.py` | Single prompt vs. chained prompts |
| `08_structured_output_validation` | `python structured_output.py` | Structured output and schema validation |
| `09_self_critique` | `python self_critique.py` | Reflection and self-critique (`Prompt_3.txt`) |

`02_prompt_template_and_evaluation` has several scripts that build on each other, so run them in this order:

```
cd Phase_02_Prompt_Engineering/02_prompt_template_and_evaluation
python demo.py
python demo_2.py
python demo_3.py
python demo_5.py
python evaluate_results.py
```

`demo.py` and `demo_2.py` only print the prompt templates and do not call the model. `demo_3.py` sends the `demo_2.py` template to the model. The slide calls the dataset file `demo_4.py`, but it is saved as `claims_dataset.py` because `demo_5.py` imports it by that name. `demo_5.py` runs the original and the enhanced prompt on every claim and writes `results.jsonl`. `evaluate_results.py` reads that file and prints the metrics from the slide (classification accuracy, missing-information recall, valid-output rate and mean latency). The unsupported-claim rate has to be counted by hand, so the script also writes `manual_review.csv` with empty columns for that.

### Phase 03: Loop Engineering

| Folder | Command | Slide topic |
|---|---|---|
| `01_single_call_vs_loop` | `python demo.py` | One call vs. a bounded loop |
| `02_state_machine` | `python demo_2.py` | Explicit loop state |
| `03_validation_retry` | `python demo_3.py` | Validation-retry loops |
| `04_generate_critique_revise` | `python demo_4.py` | Generate-critique-revise loops |
| `05_evaluator_optimizer` | `python demo_5.py` | Evaluator-optimizer loops |
| `06_plan_execute_observe` | `python demo_6.py` | Plan-execute-observe loops and ReAct |
| `07_termination_budgets` | `python demo_7.py` | Termination, budgets and infinite-loop prevention |
| `08_retry_backoff` | `python demo_8.py` | Retry, backoff and error classification (does not need Ollama) |
| `09_observability_logging` | `python demo_9.py` | Loop observability and evaluation |

### Phase 04: Integration and Evaluation

`claim_triage_app` puts everything from the earlier phases into one application, using the layers from the architecture slide.

| File | Layer |
|---|---|
| `input_layer.py` | Input layer: receives and validates the claim text |
| `prompt_layer.py` | Prompt layer: instructions, category definitions, few-shot examples and constraints |
| `llm_client.py` | LLM client: Ollama request and response handling |
| `schemas.py` | Pydantic models for the triage result and the final outcome |
| `validation.py` | Validation layer: JSON parsing, schema validation and business rules |
| `triage.py` | Control layer: bounded retry, time budget and termination reasons |
| `main.py` | Application output: prints a validated result or a controlled error |
| `evaluate.py` | Runs every claim in `sample_claims.json` and reports metrics |
| `config.py` | Model name, retry limits and input limits |

Triage a single claim:

```
cd Phase_04_Integration_and_Evaluation/claim_triage_app
python main.py "My car was hit in a parking lot and the other driver left."
```

You can also pass a file with `python main.py -f claim.txt`, or run `python main.py` with no arguments and type the claim.

Run the evaluation:

```
python evaluate.py
```

This prints one line per claim and a summary (status as expected, classification accuracy, valid-output rate, missing-information recall, human-review rate, mean attempts, mean latency, token usage and termination reasons). The full details are saved to `evaluation_report.json`. The sample set includes a prompt-injection claim and an empty claim, so the input check and the instruction rules are also tested.

`triage.py` exposes `triage_claim()` and a `TOOL_SPEC` description, so the same component can be used as a tool by an agent later.

## Files created when the scripts run

| Script | Output file |
|---|---|
| `Phase_01.../05_plausibility_vs_evidence/plausibility_check.py` | `model_output.txt` |
| `Phase_02.../02_prompt_template_and_evaluation/demo_5.py` | `results.jsonl` |
| `Phase_02.../02_prompt_template_and_evaluation/evaluate_results.py` | `manual_review.csv` |
| `Phase_02.../06_relevant_vs_irrelevant_context/demo_7.py` | `context_results.csv` |
| `Phase_02.../07_single_vs_chained_prompts/demo_8.py` | `chaining_results.txt` |
| `Phase_03.../09_observability_logging/demo_9.py` | `demo24_events.jsonl` |
| `Phase_04.../claim_triage_app/evaluate.py` | `evaluation_report.json` |

## Troubleshooting

**`ConnectionError` or "Failed to connect to Ollama"**: Ollama is not running. Open the Ollama app, or run `ollama serve` in another terminal.

**"model 'qwen2.5:7b' not found"**: run `ollama pull qwen2.5:7b`.

**`ModuleNotFoundError: No module named 'ollama'`**: the virtual environment is not active, or the packages were not installed. Activate `.venv` and run `pip install -r requirements.txt` again.

**`UnicodeEncodeError` on Windows when saving output to a file**: set UTF-8 mode before running. In PowerShell use `$env:PYTHONUTF8=1`, in Command Prompt use `set PYTHONUTF8=1`.

**Responses are very slow or the machine runs out of memory**: the 7B model needs around 8 GB of RAM. A smaller model such as `qwen2.5:3b` also works. Pull it with Ollama, then change `MODEL` at the top of each script. For Phase 04 you can set the `OLLAMA_MODEL` environment variable instead of editing the code.

**Results change between runs**: this is expected for scripts that do not set the temperature to 0. Several slides ask you to run the same experiment more than once and compare.
