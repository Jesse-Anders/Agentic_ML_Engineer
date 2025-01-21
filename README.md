# Agentic ML Engineer
An agentic system that generates a data pipeline for AI models

## Running
```cmd
pip install -r requirements.txt
```

The system defaults to using gpt-4o-mini, which requires your OPENAI_API_KEY to be retrievable in your system's environment variables. To run the system with default arguments:
```cmd
python .\main.py
```

To specify system arguments:
```cmd
python .\main.py --llm_platform=lm-studio --data_input_path=data_inputs/titanic.csv --target_var=Survived
```
