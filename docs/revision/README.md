# Revision notes

Short notes to revise the project before an interview. Read them in this order:

| File | What it is for |
|---|---|
| [01_project_story.md](01_project_story.md) | the 2-minute "tell me about your project" answer (English + French) |
| [02_services_cheatsheet.md](02_services_cheatsheet.md) | each Azure service: what it is, why it was used, where it is in the code |
| [03_interview_questions.md](03_interview_questions.md) | 40 questions with short answers |
| [04_commands_cheatsheet.md](04_commands_cheatsheet.md) | every command used, phase by phase |
| [05_problems_and_fixes.md](05_problems_and_fixes.md) | the real problems met and how they were fixed (the best interview stories) |
| [06_cost_story.md](06_cost_story.md) | how the cost was planned, tracked and kept near zero |
| [cv_lines.md](cv_lines.md) | CV bullets with real numbers (English + French) |
| [07_linkedin_and_portfolio.md](07_linkedin_and_portfolio.md) | a LinkedIn post and a portfolio project card |

The whole flow in one line:

**CSV data → `train.py` (laptop, then Azure ML) → model in the registry → Docker image in ACR → API on Container Apps → requests in Application Insights; GitHub Actions repeats the train-test-deploy part on every push.**
