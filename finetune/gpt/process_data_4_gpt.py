from datasets import load_dataset
import json
import tiktoken

"""
{
    "messages": [
                    {
                        "role": "system", 
                        "content": "Marv is a factual chatbot that is also sarcastic."
                    }, 
                    {
                        "role": "user", 
                        "content": "What's the capital of France?"
                    }, 
                    {
                        "role": "assistant", 
                        "content": "Paris, as if everyone doesn't know that already."
                    }
                ]
}
"""

def data_format(dataset):
    res = []
    for data in dataset:
        instr = data["Instruction"]
        inp = data["Input"]
        out = data["Output"]
        
        res.append(
            {
                "messages": [
                                {
                                    "role": "system", 
                                    "content": instr
                                }, 
                                {
                                    "role": "user", 
                                    "content": inp
                                }, 
                                {
                                    "role": "assistant", 
                                    "content": out
                                }
                            ]
            }
        )

    return res
    
def main():
    dataset = load_dataset(
            "json",
            data_files = "./data/finetuning-dataset.json",
            split="train",
            use_auth_token=True,
        )
    data = data_format(dataset)
    jsonl_file_path = './data/finetune-dataset-gpt.jsonl'

    with open(jsonl_file_path, 'w') as jsonl_file:
        for item in data:
            json_line = json.dumps(item)
            jsonl_file.write(json_line + '\n')

if __name__ == "__main__":
    main()
