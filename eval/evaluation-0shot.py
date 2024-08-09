import argparse
import csv
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, LlamaForCausalLM, CodeLlamaTokenizer
from datasets import load_dataset
import time

data_cache = './llm_data_cache'

def add_result_to_csv(data_row, file_path):
    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(data_row)

def load_data(data_path):
    dataset = load_dataset("json", data_files = data_path, split = "train", cache_dir = data_cache)
    return dataset

def get_system_content(task_name):
    res = None
    if task_name == "wfsgen":
        res = "You are a software engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```. "
    elif task_name == "wfsbugfind":
        res = "You are a software engineer and help the user identify whether a GitHub Workflow has syntax errors or not. Output format should be: <Yes or No>| line number: <line num>. If the error is in the shell script, output the line number of the run key. If no syntax errors exist, line number is N/A. "
    elif task_name == "wfsvulfind":
        res = "You are a security engineer and help the user detect code injection vulnerabilities in the GitHub Workflow. If no vulnerabilities are detected, print No. Otherwise, print Yes followed by the line number of the run key(sink in the shell script) or the line number of the uses key(sink in the GitHub Action or Reusable Workflow), tainted variable, and the corresponding taint source. The output format should be: Yes | line number: <line number> | tainted variable: <tainted variable> | taint source: <taint source>. If vulnerabilities happen inside the GitHub Action or Reusable Workflow, both the tainted variable and the taint source are N/A. "
    elif task_name == "wfsbugfix":
        res = "You are a software engineer. Please help the user fix syntax errors in the GitHub Workflow. Output format should be: ```yaml <Workflow>```. If the input workflow contains line numbers, please remove them from the output. "
    elif task_name == "wfsvulfix":
        res = "You are a security engineer. Please help the user repair code injection vulnerabilities in the GitHub Workflow. Output format should be: ```yaml <Workflow>```. If the input workflow contains line numbers, please remove them from the output. "
    else:
        print("Error: task name is not valid.")
        exit()
    return res

def reformat_input(model_name, prompts, system_content):
    new_prompts = []
    if model_name == "starchat" or model_name == "starchat-finetuned":
        for prompt in prompts:
            new_prompt = f"<|system|>\n{system_content}<|end|>\n<|user|>\n{prompt}<|end|>\n<|assistant|>"
            new_prompts.append(new_prompt)
    else: # "codellama-instruct", "codellama-instruct-finetuned"
        for prompt in prompts:
            new_prompt = f"<s>[INST] <<SYS>>\n{system_content}\n<</SYS>>\n\n{prompt} [/INST]"
            new_prompts.append(new_prompt)
    return new_prompts

class Evaluator: 
    def __init__(self, model, device, num_sequences, num_new_token, top_p, task_name):
        self.model_name = model
        self.device = device
        self.num_sequences = num_sequences
        self.num_new_token = num_new_token
        self.topp = top_p
        self.task = task_name
        
        if self.model_name == "starchat":
            self.checkpoint = "HuggingFaceH4/starchat-beta"
            self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.padding_side = "left"
            self.model = AutoModelForCausalLM.from_pretrained(self.checkpoint, torch_dtype=torch.float16).to(self.device)
            self.batch_size = 3
        elif self.model_name == "codellama-instruct":
            self.checkpoint = "codellama/CodeLlama-7b-Instruct-hf"
            self.tokenizer = CodeLlamaTokenizer.from_pretrained(self.checkpoint)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.padding_side = "left"
            self.model = LlamaForCausalLM.from_pretrained(self.checkpoint, torch_dtype=torch.float16).to(self.device)
            self.batch_size = 3
        elif self.model_name == "starchat-finetuned":
            self.checkpoint = "finetuning_models/final_models/HuggingFaceH4/starchat-beta-merged"
            self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.padding_side = "left"
            self.model = AutoModelForCausalLM.from_pretrained(self.checkpoint, torch_dtype=torch.float16).to(self.device)
            self.batch_size = 3
        elif self.model_name == "codellama-instruct-finetuned":
            self.checkpoint = "finetuning_models/final_models/codellama/CodeLlama-7b-Instruct-hf-merged"
            self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.padding_side = "left"
            self.model = LlamaForCausalLM.from_pretrained(self.checkpoint, torch_dtype=torch.float16).to(self.device)
            self.batch_size = 3
        else:
            print("Error: model name is not valid.")
            exit()

        if self.task == "wfsgen":
            self.num_prompts = 5
        elif self.task == "wfsbugfind":
            self.num_prompts = 2
        elif self.task == "wfsvulfind" or self.task == "wfsbugfix" or self.task == "wfsvulfix":
            self.num_prompts = 3
        else:
            print("Error: task name is not valid.")
            exit()

        if self.task == "wfsvulfind" or self.task == "wfsvulfix":
            self.batch_size = 2

        print("==================================================")
        print("Evaluator is initialized successfully.")
        print(f"model_name: {self.model_name}")
        print(f"checkpoint: {self.checkpoint}")
        print(f"model: {self.model}")
        print(f"device: {self.device}")
        print(f"num_sequences: {self.num_sequences}")
        print(f"num_new_token: {self.num_new_token}")
        print(f"top_p: {self.topp}")
        print(f"batch_size: {self.batch_size}")
        print(f"task: {self.task}")
        print(f"num_prompts: {self.num_prompts}")
        print("==================================================")
    
    def call_model(self, prompts, temperature):
        inputs = self.tokenizer(prompts, return_tensors="pt", padding=True).to(self.device)
        outputs = self.model.generate(**inputs,
                                        do_sample=True,
                                        top_p=self.topp,
                                        temperature=temperature,
                                        max_new_tokens=self.num_new_token,
                                        num_return_sequences=self.num_sequences
                                    )
        result = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        reshape_result = [result[i : i + self.num_sequences] for i in range(0, len(result), self.num_sequences)]
        return reshape_result

    def generate_results(self, target_data_path, dataset, temperature, prompt_level):
        for i in range(len(dataset)//self.batch_size):
            prompts = dataset[i * self.batch_size : (i + 1) * self.batch_size]["prompt" + str(prompt_level)]
            ids = dataset[i * self.batch_size : (i + 1) * self.batch_size]["id"]
            system_content = get_system_content(self.task)
            inputs = reformat_input(self.model_name, prompts, system_content)
            results = self.call_model(inputs, temperature)
            if len(results) == self.batch_size:
                for j in range(self.batch_size):
                    _id = ids[j]
                    _input = inputs[j]
                    if len(results[j]) == self.num_sequences:
                        datarow = [_id.encode('utf-8'), _input.encode('utf-8')]
                        for text in results[j]:
                            datarow.append(text.encode('utf-8'))
                        add_result_to_csv(datarow, target_data_path)
                    else:
                        print(f"Error: _id = {_id},  the number of generated text is not equal to self.num_sequences. ")
            else:
                print(f"Error: the number of generation is not equal to the batch size. ")

    def evaluate(self, data_path, target_dir, specified_temperature, specified_prompt_level):
        dataset_name = data_path.split("/")[-1].rstrip(".json")
        dataset = load_data(data_path)

        if specified_temperature:
            temperatures = [specified_temperature]
        else:
            temperatures =  [0.1, 0.3, 0.5, 0.7, 0.9]
        if specified_prompt_level:
            prompt_levels = [specified_prompt_level]
        else:
            prompt_levels = [i for i in range(1, self.num_prompts + 1)]
        
        for temperature in temperatures:
            for prompt_level in prompt_levels:
                csv_file_name = f"{dataset_name}_{self.model_name}_0shot_{temperature}_prompt{prompt_level}.csv"
                header = ["_id", "prompt"]
                for i in range(self.num_sequences):
                    header.append(f"gen_text_{i+1}")
                target_data_path = target_dir + csv_file_name
                add_result_to_csv(header, target_data_path)
                print(f"{csv_file_name} begins ......")
                start_time = time.time()
                self.generate_results(target_data_path, dataset, temperature, prompt_level)
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"{csv_file_name} is finished and executed in {execution_time} seconds......")

if __name__ == '__main__':
    """
    python evaluation-0shot.py --model "starchat" \
                            --device "cuda" \
                            --num_sequences 5 \
                            --num_new_token 1024 \
                            --top_p 1.0 \
                            --task_name 'wfsgen' \
                            --data_path "data/wfsgen-eval-small.json" \
                            --target_dir "results/"
    """
       
    parser = argparse.ArgumentParser()
    # model
    parser.add_argument("--model", type=str, required=True, choices=["starchat", "starchat-finetuned", "codellama-instruct", "codellama-instruct-finetuned"], help="model name")
    parser.add_argument('--device', type=str, required=False, default="cuda", help="device name (e.g., cuda, cpu)")
    parser.add_argument('--num_sequences', type=int, required=False, default=5, help="number of sequences to generate")
    parser.add_argument('--num_new_token', type=int, required=False, default=1024, help="number of new tokens to generate")
    parser.add_argument('--top_p', type=float, required=False, default=1.0, help="top_p value")
    parser.add_argument('--task_name', type=str, required=True, default="wfsgen", choices=["wfsgen", "wfsbugfind", "wfsvulfind", "wfsbugfix", "wfsvulfix"], help="task name")
    # data
    parser.add_argument("--data_path", type=str, required=True, help="path to the dataset")
    parser.add_argument('--target_dir', type=str, required=True, help="path to the directory which stores the results")
    parser.add_argument('--specified_temperature', type=float, required=False, help="temperature value")
    parser.add_argument('--specified_prompt_level', type=int, required=False, help="prompt level")

    args = parser.parse_args()
    print(args)
    evaluator = Evaluator(args.model, args.device, args.num_sequences, args.num_new_token, args.top_p, args.task_name)
    evaluator.evaluate(args.data_path, args.target_dir, args.specified_temperature, args.specified_prompt_level)
