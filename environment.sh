SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -e "{$SCRIPT_DIR}/venv" ]]; then
    python3 -m venv "${SCRIPT_DIR}/venv"
fi

source "${SCRIPT_DIR}/venv/bin/activate"

pip install -r "${SCRIPT_DIR}/requirements.txt"

alias dictionary_cmd="python3 ${SCRIPT_DIR}/dictionary_cmd.py"
alias dictionary="streamlit run ${SCRIPT_DIR}/dictionary.py"
