# Copilot Studio Labs

Start with **Lab 00 - ILT Setup**. It creates the environment and solution required for the remaining labs.

| # | Lab | Topic it supports | Time | Needs |
|---|---|---|---|---|
| 00 | [ILT Setup](lab00-ILT-setup.md) | Power Platform environment, Dataverse, Copilot Studio, and solutions | 25 min | Internet |
| 01 | [Create Agents](lab01-create-agents.md) | Agent creation, instructions, knowledge sources, and publishing | 55 min | Copilot Studio access and the environment created in Lab 00 |
| 02 | [Manage Topics](lab02-manage-topics.md) | Topics, nodes, variables, structured conversations, and topic routing | 45 min | Agent created in Lab 01 |
| 03 | [Manage Knowledge](lab03-manage-knowledge.md) | Dataverse tables, file and website knowledge sources, generative orchestration, and generative answers | 60 min | Agent created in Lab 01 and Dataverse environment from Lab 00 |

## How the labs connect

```text
Lab 00  Create a Power Platform environment and solution
        -> Prepare the workspace for agent development

Lab 01  Create and configure agents
        -> Define agent behavior, add basic knowledge, and publish

Lab 02  Create and manage topics
        -> Build structured conversations using nodes, variables, and topic routing

Lab 03  Manage knowledge in agents
        -> Add Dataverse, file, and website knowledge sources
        -> Configure generative AI and test grounded responses
```