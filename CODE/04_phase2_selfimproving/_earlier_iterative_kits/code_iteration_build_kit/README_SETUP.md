# Setup — self-improving non-iconicity detector (Claude Code, Agent Teams, Opus 4.8)

The kit is PRE-BUILT. All folders exist, the v5 pipeline is already in pipeline/,
and the four agents + loop are configured. You only add two things: your stories
and your answer key. You never write code.

## Already done for you
- pipeline/        ← the v5 detection code is ALREADY HERE (run.py, run_split.py, pipeline/*.py)
- stories/         ← created (has a placeholder; you add your 15 .txt files)
- groundtruth/     ← created (has a placeholder; you add your .sty files)
- predictions/     ← created, empty (filled automatically)
- iterations/      ← created, empty (filled automatically)
- .claude/         ← agents (improver/runner/scorer), the /loop command, settings, hooks
- CLAUDE.md, split.json, state.json, feedback.json ← all ready

## STEP 1 — Add your stories
Put your 15 story .txt files into  stories/  and delete the placeholder file there.
(File manager: drag them in. Terminal: cp /path/to/your/*.txt stories/ )

## STEP 2 — Add your answer key
Put your .sty ground-truth files into  groundtruth/  and delete the placeholder there.

## STEP 3 — Make split.json match your filenames
Open split.json. Make the names EXACTLY match your story filenames WITHOUT .txt.
Keep 10 in "dev" and 5 in "test". (Example: file 09_The_Witch.txt -> list "09_The_Witch".)

## STEP 4 — One-time git init for pipeline/ (lets the firewall hook check changes)
From the project root:
    cd pipeline && git init && git add -A && git commit -m "v5 baseline" && cd ..
(If git asks for name/email the first time:
    git config --global user.email "you@example.com"
    git config --global user.name  "Your Name"
 then re-run the commit.)

## STEP 5 — Install the one dependency (NLTK), once
    pip install -r pipeline/requirements.txt

## STEP 6 — Start Claude Code in the project folder
    claude
settings.json already enables Agent Teams. If Claude says teams are off, quit, run
    export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
(Windows PowerShell:  $env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 )
then start  claude  again.

## STEP 7 — Start the loop
In the Claude Code session, type:
    /loop
The lead agent runs improve -> run -> score -> checkpoint, prints one line per
iteration, and continues automatically until the stop rule fires
(plateau, 12 iterations, or thrashing).

## STEP 8 — If a usage limit stops it
Wait for your reset, start  claude  again, type  /loop  . It reads state.json and
continues from the next iteration. Nothing repeats. Check budget with  /usage .

## STEP 9 — Final test (you, once, by hand)
When it stops it names the best iteration. Then:
    cp -r iterations/iter_<best>/pipeline ./final_pipeline
    python final_pipeline/run_split.py --split test --stories stories --out test_predictions
Score test_predictions against groundtruth (the test stories), and compare dev-F1 vs
test-F1. That gap is your honesty check. The agents never touch the test split.

## What the improver is allowed to change
Any stage of pipeline/ — preprocessing (tokenization, sentence splitting, contraction
handling, POS), event extraction, or the rules — but ONE focused, general, incremental
change per iteration, logged in pipeline/CHANGELOG.md. It never rewrites from scratch
and never hard-codes story-specific text.

## The firewall (why this is not contamination)
- improver edits pipeline/ but CANNOT read groundtruth/   (tools + a hook enforce this)
- scorer reads groundtruth/ but CANNOT touch pipeline/, and emits only aggregate numbers
- a hook blocks any round where the scorer leaks specifics or the improver hard-codes a name
- the loop optimises on dev only; you test once on held-out test
No single agent ever holds both the code and the answers.
