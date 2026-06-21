testing commands

python tests\eval_tool.py run --config app\config.yaml --questions tests\gita_eval_questions.txt --output tests\phase1_eval.json --label phase1
python tests\eval_tool.py run --config app\config.yaml --questions tests\gita_eval_questions.txt --output tests\phase2_eval.json --label phase2
python tests\eval_tool.py compare --a tests\phase1_eval.json --b tests\phase2_eval.json --output tests\phase1_vs_phase2.md