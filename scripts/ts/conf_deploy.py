from dotenv import set_key
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
print(env_path)
set_key(str(env_path), 'DS_EXP_GEN_HYPOTHESIS_DESC', 'We are putting this solution online, so we aim to remove any unnecessary code without hurting the final results. For example, we will use the best hyperparameters or features already found in the stdout instead of searching for them again, remove code used only for analysis, and delete unused models.')
set_key(str(env_path), 'APP_TPL', 'app/ts/tpl/')
set_key(str(env_path), 'DS_ENABLE_MODEL_DUMP', "True")
