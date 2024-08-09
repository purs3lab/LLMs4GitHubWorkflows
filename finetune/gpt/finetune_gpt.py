from openai import OpenAI
client = OpenAI()

client.files.create(
  file=open("./finetune-dataset-gpt.jsonl", "rb"),
  purpose="fine-tune"
)
"""
Reference: https://platform.openai.com/docs/api-reference/fine-tuning/create
Request:
curl https://api.openai.com/v1/fine_tuning/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "training_file": "YOUR_FILE_ID",
    "model": "gpt-3.5-turbo",
    "hyperparameters": {
      "n_epochs": 5
    }
  }'

Response:
{
  "object": "fine_tuning.job",
  "id": "ftjob-bfcF8bJ51AGAtMJwGqzSC70J",
  "model": "gpt-3.5-turbo-0613",
  "created_at": 1707085288,
  "finished_at": null,
  "fine_tuned_model": null,
  "organization_id": "YOUR_ORG_ID",
  "result_files": [],
  "status": "validating_files",
  "validation_file": null,
  "training_file": "YOUR_FILE_ID",
  "hyperparameters": {
    "n_epochs": 5,
    "batch_size": "auto",
    "learning_rate_multiplier": "auto"
  },
  "trained_tokens": null,
  "error": null
}
"""
