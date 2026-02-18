# Polish Dictionary
<img width="440" height="419" alt="image" src="https://github.com/user-attachments/assets/f3607807-e15f-40d4-b9b8-1ff99c9e140c" />


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
<img width="281" height="350" alt="image" src="https://github.com/user-attachments/assets/274f06a3-a62c-47f7-b34e-4d9bab1deb29" />

Search only verbs (`cz` = czasownik):

``` bash
Dictionary-Cmd search -r "*[u|ó]l" -t cz
```
<img width="224" height="400" alt="image" src="https://github.com/user-attachments/assets/c85055ca-41e8-4209-90e9-42a2a654b836" />

Search verbs with length between 3 and 4 characters:

``` bash
Dictionary-Cmd search -r "*[u|ó]l" -t cz -m 3 -M 4
```
<img width="245" height="160" alt="image" src="https://github.com/user-attachments/assets/c712dbc6-4538-47c9-b4d8-5e26346a7df4" />

------------------------------------------------------------------------

### 2. Web Interface

The dictionary also supports a Streamlit web interface.

To launch it, run:

``` bash
streamlit run Dictionary
```
<img width="365" height="430" alt="image" src="https://github.com/user-attachments/assets/e3d185c4-980b-4a94-89bc-87048c330d46" />

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
