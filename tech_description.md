Absolutely. For a **capstone/project proposal form**, I would make it technical enough to demonstrate depth, but not so detailed that it reads like an implementation document.

### Project Title
**RepoPilot: An Evidence-Driven Multi-Agent AI Framework for Automated Software Quality Assurance and Repair**

### Technical Description

RepoPilot is an **agentic software engineering and quality-assurance system** designed to automatically analyze, test, diagnose, and improve software repositories, with a particular focus on applications generated or heavily modified using AI coding tools.

The system accepts an existing software repository as input and constructs a structured representation of the codebase using **repository analysis, static analysis, dependency graphs, semantic code search, and Retrieval-Augmented Generation (RAG)**. An **orchestrator agent** decomposes the overall QA task into specialized stages and coordinates multiple domain-specific agents.

The proposed pipeline includes specialized agents for **repository/code understanding, risk analysis, test planning, test generation, test execution, failure analysis, repair, and final review/reporting**. Agents operate within isolated context boundaries while accessing shared engineering tools such as code search, repository indexing, compilers, test runners, static analyzers, coverage tools, mutation-testing tools, and artifact generators.

Rather than relying solely on LLM-generated reasoning, RepoPilot uses **execution-based feedback as an external source of evidence**. Generated tests are executed against the actual application, and the resulting compiler errors, runtime failures, stack traces, coverage information, static-analysis findings, and mutation-testing results are fed back into the appropriate agent.

A critical component is the **failure-analysis stage**, which determines whether a failed test indicates:

1. an error in the generated test,
2. a defect in the application implementation, or
3. an environmental/configuration/dependency problem.

Based on this classification, the system can either revise the test or propose/implement a bounded repair to the software. Repairs are subsequently re-tested against the existing regression suite to reduce the possibility of introducing new defects.

The agents use **bounded self-iteration** rather than unrestricted autonomous loops. Each iteration must produce measurable evidence, such as successful compilation, passing tests, improved coverage, mutation score, or resolution of a previously identified defect. All intermediate results are represented as **structured artifacts** that are handed between agents rather than relying on conversational memory.

The final system produces an **evidence-backed software quality report** containing discovered risks, generated tests, execution results, detected defects, repair attempts, regression results, coverage/mutation metrics, and a trace of the actions performed by the agents.

### Core Architecture

```text
                    Software Repository
                           ³
                                               Repository Ingestion
                           ³
                                             Code Understanding Agent
                           ³
                  ÚÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄ¿
                               Code RAG          Dependency Graph
                  ³                 ³
                  ÀÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÙ
                                               Risk Analysis Agent
                           ³
                                               Test Planning Agent
                           ³
                                              Test Generation Agent
                           ³
                                               Execution Harness
                           ³
              ÚÄÄÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÄÄÄÄÄÄ¿
                        Test Results   Coverage   Static Analysis
              ³
                                Failure Analysis Agent
                           ³
                ÚÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÄÄÄÄ¿
                             Test Bug   Code Bug   Environment
                ³          ³
                          Test Repair   Repair Agent
                ³          ³
                ÀÄÄÄÄÂÄÄÄÄÄÙ
                                       Re-testing
                     ³
              ÚÄÄÄÄÄÄÁÄÄÄÄÄÄ¿
                        Regression     Mutation
            Tests         Testing
              ³             ³
              ÀÄÄÄÄÄÄÂÄÄÄÄÄÄÙ
                                      Review Agent
                     ³
                                  Evidence-Based Report
```

### AI / Technical Components

- **Multi-Agent Architecture** - specialized agents with clearly defined responsibilities.
- **LLMs** - reasoning, code understanding, planning, test generation, failure diagnosis, and repair.
- **Agent Orchestrator** - controls task decomposition, agent selection, execution order, and bounded iterations.
- **RAG for Code** - retrieves relevant source files, functions, classes, dependencies, documentation, tests, and previous artifacts instead of placing the entire repository into every context window.
- **Code Intelligence** - AST parsing, symbol resolution, dependency analysis, call graphs, and semantic code search.
- **Execution Harness** - isolated environment for compiling, executing, and testing generated changes.
- **Static Analysis** - detection of code smells, suspicious constructs, dependency problems, and potential vulnerabilities.
- **Automated Test Generation** - generation of unit/integration tests based on repository context and identified risks.
- **Failure Diagnosis** - classification of failures using execution traces, source context, test intent, and static analysis.
- **Automated Program Repair** - bounded attempts to modify defective implementation code or incorrect generated tests.
- **Mutation Testing** - evaluates whether generated tests can actually detect artificially introduced defects rather than relying only on code coverage.
- **Artifact-Based Agent Handover** - agents communicate through structured outputs such as test plans, defect reports, repair proposals, execution results, and validation reports.
- **Quality Gates** - agents cannot simply declare success; progression depends on measurable validation results.

### Key Research Aspect

The project investigates whether **a coordinated multi-agent architecture with repository-level context and execution-based feedback can provide more reliable automated QA and repair than simply prompting a general-purpose coding agent**.

A particularly important research problem is **failure attribution**: when an LLM-generated test fails, RepoPilot must determine whether the failure exposes an actual software defect or whether the generated test itself is incorrect.

### Expected Output

The final system will provide a developer-facing interface where a repository can be submitted for analysis and the system produces:

- Identified high-risk components
- Automatically generated test plans
- Generated unit/integration tests
- Test execution results
- Detected defects
- Failure classifications
- Proposed or automatically applied repairs
- Regression-test results
- Coverage and mutation-testing measurements
- Complete agent/action trace
- Final software quality report

### One-paragraph version for a small form

> **RepoPilot is an evidence-driven multi-agent AI framework for automated software quality assurance and repair. Given an existing software repository, the system uses an orchestrator and specialized LLM agents for code understanding, risk analysis, test planning, test generation, execution, failure analysis, repair, and review. Repository-level RAG, static analysis, dependency graphs, and semantic code search provide agents with relevant code context, while an isolated execution harness provides objective feedback through compilation, testing, coverage, static analysis, and mutation testing. When generated tests fail, a dedicated failure-analysis agent determines whether the problem originates from the test, the application, or the environment before initiating bounded repair and re-testing. Agents exchange structured artifacts rather than relying on unrestricted conversational memory. The project aims to investigate whether this controlled, multi-agent, evidence-driven approach can reliably identify and repair weaknesses in AI-generated or poorly tested software repositories.**
