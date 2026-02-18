$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition

if (-not (Test-Path "$SCRIPT_DIR\venv")) {
    py -m venv "$SCRIPT_DIR\venv"
}

& "$SCRIPT_DIR\venv\Scripts\Activate.ps1"

py -m pip install -r "$SCRIPT_DIR\requirements.txt"

function Dictionary-Cmd {
    py "$SCRIPT_DIR\dictionary_cmd.py" @args
}

function Dictionary {
    streamlit run "$SCRIPT_DIR\dictionary.py"
}
