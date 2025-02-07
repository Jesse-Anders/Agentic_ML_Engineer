
# generated_pipeline

# This file is intended to be a reusable data pipeline.

import pandas as pd, sys, os

from static_lib import *
from pipeline_lib import *

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from utils import set_current_column
from runtime_lib.static_agent_libs.agent1_static_lib import *
from runtime_lib.static_agent_libs.agent2_static_lib import *
from runtime_lib.static_agent_libs.agent3_static_lib import *
from runtime_lib.static_agent_libs.agent4_static_lib import *
from runtime_lib.static_agent_libs.agent5_static_lib import *
from runtime_lib.static_agent_libs.agent6_static_lib import *

# SYSTEM GENERATION START:

df = pd.read_csv("data_inputs/data.csv", index_col=None)

set_current_column("col6")
df = drop_column(df)
