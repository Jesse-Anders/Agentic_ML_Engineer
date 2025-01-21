<h1><center>Capstone Journal</center></h1>

**January 13, 2025** - We started off the semester by compiling preliminary work that included 200 lines of a predominantly langchain / langraph code-generating agentic data preprocessor, 10+ pages of notes on the ARC (Abstraction and Reasoning Corpus) ADAS (Automated Design of Agentic Systems) codebase, and a local api-call-ready installation of Llama 3.3 70b housed on the Lambda Vector workstation and hosted via LM Studio.

**January 14** - Successfully transferred an ADAS virtual environment to Vector along with a copy of the ADAS codebase.

**January 15** - Finished the first round of notes on the ARC ADAS repository.

**January 16** - Met with Dr. Gogolin and discussed our project for around an hour and a half. Received the green light to fully pursue our ML_Engineer project.

**January 17** - Began work on the architecture code.

**January 18** - Worked on the architecture code probably 6 hours.

**January 19** - Continued work on the architecture code. Met with Jesse to do a code review and discuss potential future issues.

**January 20** - Finished creating the initial architecture. The system now automatically saves previous generations and uses a task loop to populate the pipeline_lib and pipeline.py files with new code. There still exists the some formidable flaws in the system, namely handling multi-parameter function calls once generated functions are written and dealing with mismatching import requirements between pipeline_lib, static_lib, and pipeline.py.
