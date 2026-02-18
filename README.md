# Polish Dictionary
<img width="659" height="475" alt="image" src="https://github.com/user-attachments/assets/d6e2db45-8e98-44aa-a8c3-70352957eb41" />

Polish Dictionary is a Streamlit application that allows users to search
Polish words using regular expressions within more than 160 000 words.

The dictionary source file is built from Wiktionary data. Since the
Polish Wiktionary contains fewer Polish entries than those available
through English Wiktionary translations, the final output file is
created by merging both sources.

Due to inconsistent and incomplete syllabification data in Wiktionary,
the application uses a heuristic approach to estimate syllable counts.
This heuristic is not fully accurate and requires improvement.

------------------------------------------------------------------------

## Environment Setup

From the root of the repository:

-   **Windows**

    ``` powershell
    . ./environment.ps1
    ```

-   **Linux**

    ``` bash
    source environment.sh
    ```

------------------------------------------------------------------------

## Building the Dictionary (Optional)

This step can be skipped because the repository already contains a
prebuilt `dictionary.json` file.

If you need to rebuild the dictionary:

1.  Source the environment (see above).

2.  Run:

    ``` bash
    ./dictionary_cmd.py make
    ```

The process of fetching, parsing, and building `dictionary.json` takes
approximately 15-20 minutes.

------------------------------------------------------------------------

## Using the Dictionary

Ensure the environment is sourced before running any commands.

### 1. Command Line Interface

By default, the argument parser searches within three word types:

-   `rzeczownik` (noun)
-   `czasownik` (verb)
-   `przymiotnik` (adjective)

Example usage:

Search all words matching a regular expression:

``` bash
Dictionary-Cmd search -r "*[u|ó]l"
```
<img width="315" height="308" alt="image" src="https://github.com/user-attachments/assets/49bbc647-9a26-4e92-bf61-d89219940ecb" />


Search only verbs (`cz` = czasownik):

``` bash
Dictionary-Cmd search -r "*[u|ó]l" -t cz
```
<img width="369" height="461" alt="image" src="https://github.com/user-attachments/assets/dbc208b1-f58f-44fd-a828-56789c01de3e" />


Search verbs with length between 3 and 4 characters:

``` bash
Dictionary-Cmd search -r "*[u|ó]l" -t cz -3 -M 4
```
<img width="379" height="236" alt="image" src="https://github.com/user-attachments/assets/1151ddee-78e9-48d7-999b-35f3f10938a3" />


------------------------------------------------------------------------

### 2. Web Interface

The dictionary also supports a Streamlit web interface.

To launch it, run:

``` bash
streamlit run Dictionary
```
<img width="599" height="449" alt="image" src="https://github.com/user-attachments/assets/c3861235-a36c-4b5b-88c5-8aa1b5745e62" />


Then open the displayed local URL in your browser.

------------------------------------------------------------------------

## Known Issues

The application is not deployed to Streamlit Cloud due to the following
unresolved problems:

-   Inaccurate syllable counting (heuristic-based and imperfect)
-   Presence of words not found in standard Polish dictionaries
-   Duplicate words due to case sensitivity
-   Limited word type coverage (currently only three types supported)

------------------------------------------------------------------------

## Planned Improvements

-   Replace heuristic syllable counting with a more reliable method
-   Validate entries against an authoritative Polish dictionary
-   Normalize case handling to prevent duplication
-   Expand support for additional word types
