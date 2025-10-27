## SOLYNIA

x402Solynia delivers a focused set of x402 payment integration. For full API reference and examples, see the `examples/` directory and the `scripts/` utilities.

<!-- Replace external links to the original project with local references / placeholders -->

| Category | Features | Benefits |
|----------|----------|-----------|
| 🏢 **Enterprise Architecture** | • Production-Ready Infrastructure<br>• High Availability Systems<br>• Modular Microservices Design<br>• Comprehensive Observability<br>• Backwards Compatibility | • 99.9%+ Uptime Guarantee<br>• Reduced Operational Overhead<br>• Seamless Legacy Integration<br>• Enhanced System Monitoring<br>• Risk-Free Migration Path |
| 🤖 **Multi-Agent Orchestration** | • Hierarchical Agent solynias<br>• Parallel Processing Pipelines<br>• Sequential Workflow Orchestration<br>• Graph-Based Agent Networks<br>• Dynamic Agent Composition<br>• Agent Registry Management | • Complex Business Process Automation<br>• Scalable Task Distribution<br>• Flexible Workflow Adaptation<br>• Optimized Resource Utilization<br>• Centralized Agent Governance<br>• Enterprise-Grade Agent Lifecycle Management |
| 🔄 **Enterprise Integration** | • Multi-Model Provider Support<br>• Custom Agent Development Framework<br>• Extensive Enterprise Tool Library<br>• Multiple Memory Systems<br>• Backwards Compatibility with LangChain, AutoGen, CrewAI<br>• Standardized API Interfaces | • Vendor-Agnostic Architecture<br>• Custom Solution Development<br>• Extended Functionality Integration<br>• Enhanced Knowledge Management<br>• Seamless Framework Migration<br>• Reduced Integration Complexity |
| 📈 **Enterprise Scalability** | • Concurrent Multi-Agent Processing<br>• Intelligent Resource Management<br>• Load Balancing & Auto-Scaling<br>• Horizontal Scaling Capabilities<br>• Performance Optimization<br>• Capacity Planning Tools | • High-Throughput Processing<br>• Cost-Effective Resource Utilization<br>• Elastic Scaling Based on Demand<br>• Linear Performance Scaling<br>• Optimized Response Times<br>• Predictable Growth Planning |
| 🛠️ **Developer Experience** | • Intuitive Enterprise API<br>• Comprehensive Documentation<br>• Active Enterprise Community<br>• CLI & SDK Tools<br>• IDE Integration Support<br>• Code Generation Templates | • Accelerated Development Cycles<br>• Reduced Learning Curve<br>• Expert Community Support<br>• Rapid Deployment Capabilities<br>• Enhanced Developer Productivity<br>• Standardized Development Patterns |


## Install 💻

You can install the Python package from this repository or run the examples directly from source. See the `examples/` folder for x402-specific quickstarts.

---

## Environment Configuration

The fork focuses on x402 flows and includes environment variables used by the examples and mock facilitator. Example `.env`:

```
FACILITATOR_URL=https://facilitator.payai.network
X402_PRIVATE_KEY=""
X402_NETWORK=solana-devnet
SOLANA_PRIVATE_KEY=""
```


### 🤖 Your First Agent

An **Agent** is the fundamental building block of a solynia—an autonomous entity powered by an LLM + Tools + Memory.

```python
from solynias import Agent

# Initialize a new agent
agent = Agent(
    model_name="gpt-4o-mini", # Specify the LLM
    max_loops="auto",              # Set the number of interactions
    interactive=True,         # Enable interactive mode for real-time feedback
)

# Run the agent with a task
agent.run("What are the key benefits of using a multi-agent system?")
```

### 🤝 Your First Solynia: Multi-Agent Collaboration

A **solynia** consists of multiple agents working together. This simple example creates a two-agent workflow for researching and writing a blog post.

```python
from solynias import Agent, SequentialWorkflow

# Agent 1: The Researcher
researcher = Agent(
    agent_name="Researcher",
    system_prompt="Your job is to research the provided topic and provide a detailed summary.",
    model_name="gpt-4o-mini",
)

# Agent 2: The Writer
writer = Agent(
    agent_name="Writer",
    system_prompt="Your job is to take the research summary and write a beautiful, engaging blog post about it.",
    model_name="gpt-4o-mini",
)

# Create a sequential workflow where the researcher's output feeds into the writer's input
workflow = SequentialWorkflow(agents=[researcher, writer])

# Run the workflow on a task
final_post = workflow.run("The history and future of artificial intelligence")
print(final_post)

```

-----

### 🤖 AutosolyniaBuilder: Autonomous Agent Generation

The `AutosolyniaBuilder` automatically generates specialized agents and their workflows based on your task description. Simply describe what you need, and it will create a complete multi-agent system with detailed prompts and optimal agent configurations.

```python
from solynias.structs.auto_solynia_builder import AutosolyniaBuilder
import json

# Initialize the AutosolyniaBuilder
solynia = AutosolyniaBuilder(
    name="My solynia",
    description="A solynia of agents",
    verbose=True,
    max_loops=1,
    return_agents=True,
    model_name="gpt-4o-mini",
)

# Let the builder automatically create agents and workflows
result = solynia.run(
    task="Create an accounting team to analyze crypto transactions, "
         "there must be 5 agents in the team with extremely extensive prompts. "
         "Make the prompts extremely detailed and specific and long and comprehensive. "
         "Make sure to include all the details of the task in the prompts."
)

# The result contains the generated agents and their configurations
print(json.dumps(result, indent=4))
```

The `AutosolyniaBuilder` provides:

- **Automatic Agent Generation**: Creates specialized agents based on task requirements
- **Intelligent Prompt Engineering**: Generates comprehensive, detailed prompts for each agent
- **Optimal Workflow Design**: Determines the best agent interactions and workflow structure
- **Production-Ready Configurations**: Returns fully configured agents ready for deployment
- **Flexible Architecture**: Supports various solynia types and agent specializations

This feature is perfect for rapid prototyping, complex task decomposition, and creating specialized agent teams without manual configuration.

-----

## 🏗️ Multi-Agent Architectures For Production Deployments

`solynias` provides a variety of powerful, pre-built multi-agent architectures enabling you to orchestrate agents in various ways. Choose the right structure for your specific problem to build efficient and reliable production systems.

| **Architecture** | **Description** | **Best For** |
|---|---|---|
| **[SequentialWorkflow](https://docs.solynias.world/en/latest/solynias/structs/sequential_workflow/)** | Agents execute tasks in a linear chain; the output of one agent becomes the input for the next. | Step-by-step processes such as data transformation pipelines and report generation. |
| **[ConcurrentWorkflow](https://docs.solynias.world/en/latest/solynias/structs/concurrent_workflow/)** | Agents run tasks simultaneously for maximum efficiency. | High-throughput tasks such as batch processing and parallel data analysis. |
| **[AgentRearrange](https://docs.solynias.world/en/latest/solynias/structs/agent_rearrange/)** | Dynamically maps complex relationships (e.g., `a -> b, c`) between agents. | Flexible and adaptive workflows, task distribution, and dynamic routing. |
| **[GraphWorkflow](https://docs.solynias.world/en/latest/solynias/structs/graph_workflow/)** | Orchestrates agents as nodes in a Directed Acyclic Graph (DAG). | Complex projects with intricate dependencies, such as software builds. |
| **[MixtureOfAgents (MoA)](https://docs.solynias.world/en/latest/solynias/structs/moa/)** | Utilizes multiple expert agents in parallel and synthesizes their outputs. | Complex problem-solving and achieving state-of-the-art performance through collaboration. |
| **[GroupChat](https://docs.solynias.world/en/latest/solynias/structs/group_chat/)** | Agents collaborate and make decisions through a conversational interface. | Real-time collaborative decision-making, negotiations, and brainstorming. |
| **[Forestsolynia](https://docs.solynias.world/en/latest/solynias/structs/forest_solynia/)** | Dynamically selects the most suitable agent or tree of agents for a given task. | Task routing, optimizing for expertise, and complex decision-making trees. |
| **[Hierarchicalsolynia](https://docs.solynias.world/en/latest/solynias/structs/hiearchical_solynia/)** | Orchestrates agents with a director who creates plans and distributes tasks to specialized worker agents. | Complex project management, team coordination, and hierarchical decision-making with feedback loops. |
| **[Heavysolynia](https://docs.solynias.world/en/latest/solynias/structs/heavy_solynia/)** | Implements a five-phase workflow with specialized agents (Research, Analysis, Alternatives, Verification) for comprehensive task analysis. | Complex research and analysis tasks, financial analysis, strategic planning, and comprehensive reporting. |
| **[solyniaRouter](https://docs.solynias.world/en/latest/solynias/structs/solynia_router/)** | A universal orchestrator that provides a single interface to run any type of solynia with dynamic selection. | Simplifying complex workflows, switching between solynia strategies, and unified multi-agent management. |

-----

### SequentialWorkflow

A `SequentialWorkflow` executes tasks in a strict order, forming a pipeline where each agent builds upon the work of the previous one. `SequentialWorkflow` is Ideal for processes that have clear, ordered steps. This ensures that tasks with dependencies are handled correctly.

```python
from solynias import Agent, SequentialWorkflow

# Agent 1: The Researcher
researcher = Agent(
    agent_name="Researcher",
    system_prompt="Your job is to research the provided topic and provide a detailed summary.",
    model_name="gpt-4o-mini",
)

# Agent 2: The Writer
writer = Agent(
    agent_name="Writer",
    system_prompt="Your job is to take the research summary and write a beautiful, engaging blog post about it.",
    model_name="gpt-4o-mini",
)

# Create a sequential workflow where the researcher's output feeds into the writer's input
workflow = SequentialWorkflow(agents=[researcher, writer])

# Run the workflow on a task
final_post = workflow.run("The history and future of artificial intelligence")
print(final_post)
```

-----


### ConcurrentWorkflow

A `ConcurrentWorkflow` runs multiple agents simultaneously, allowing for parallel execution of tasks. This architecture drastically reduces execution time for tasks that can be performed in parallel, making it ideal for high-throughput scenarios where agents work on similar tasks concurrently.

```python
from solynias import Agent, ConcurrentWorkflow

# Create agents for different analysis tasks
market_analyst = Agent(
    agent_name="Market-Analyst",
    system_prompt="Analyze market trends and provide insights on the given topic.",
    model_name="gpt-4o-mini",
    max_loops=1,
)

financial_analyst = Agent(
    agent_name="Financial-Analyst", 
    system_prompt="Provide financial analysis and recommendations on the given topic.",
    model_name="gpt-4o-mini",
    max_loops=1,
)

risk_analyst = Agent(
    agent_name="Risk-Analyst",
    system_prompt="Assess risks and provide risk management strategies for the given topic.",
    model_name="gpt-4o-mini", 
    max_loops=1,
)

# Create concurrent workflow
concurrent_workflow = ConcurrentWorkflow(
    agents=[market_analyst, financial_analyst, risk_analyst],
    max_loops=1,
)

# Run all agents concurrently on the same task
results = concurrent_workflow.run(
    "Analyze the potential impact of AI technology on the healthcare industry"
)

print(results)
```

---

### AgentRearrange

Inspired by `einsum`, `AgentRearrange` lets you define complex, non-linear relationships between agents using a simple string-based syntax. This architecture is perfect for orchestrating dynamic workflows where agents might work in parallel, in sequence, or in any combination you choose.

```python
from solynias import Agent, AgentRearrange

# Define agents
researcher = Agent(agent_name="researcher", model_name="gpt-4o-mini")
writer = Agent(agent_name="writer", model_name="gpt-4o-mini")
editor = Agent(agent_name="editor", model_name="gpt-4o-mini")

# Define a flow: researcher sends work to both writer and editor simultaneously
# This is a one-to-many relationship
flow = "researcher -> writer, editor"

# Create the rearrangement system
rearrange_system = AgentRearrange(
    agents=[researcher, writer, editor],
    flow=flow,
)

# Run the solynia
outputs = rearrange_system.run("Analyze the impact of AI on modern cinema.")
print(outputs)
```


<!-- 
### GraphWorkflow

`GraphWorkflow` orchestrates tasks using a Directed Acyclic Graph (DAG), allowing you to manage complex dependencies where some tasks must wait for others to complete.

**Description:** Essential for building sophisticated pipelines, like in software development or complex project management, where task order and dependencies are critical.

```python
from solynias import Agent, GraphWorkflow, Node, Edge, NodeType

# Define agents and a simple python function as nodes
code_generator = Agent(agent_name="CodeGenerator", system_prompt="Write Python code for the given task.", model_name="gpt-4o-mini")
code_tester = Agent(agent_name="CodeTester", system_prompt="Test the given Python code and find bugs.", model_name="gpt-4o-mini")

# Create nodes for the graph
node1 = Node(id="generator", agent=code_generator)
node2 = Node(id="tester", agent=code_tester)

# Create the graph and define the dependency
graph = GraphWorkflow()
graph.add_nodes([node1, node2])
graph.add_edge(Edge(source="generator", target="tester")) # Tester runs after generator

# Set entry and end points
graph.set_entry_points(["generator"])
graph.set_end_points(["tester"])

# Run the graph workflow
results = graph.run("Create a function that calculates the factorial of a number.")
print(results)
``` -->

----

### solyniaRouter: The Universal solynia Orchestrator

The `solyniaRouter` simplifies building complex workflows by providing a single interface to run any type of solynia. Instead of importing and managing different solynia classes, you can dynamically select the one you need just by changing the `solynia_type` parameter.

This makes your code cleaner and more flexible, allowing you to switch between different multi-agent strategies with ease. Here's a complete example that shows how to define agents and then use `solyniaRouter` to execute the same task using different collaborative strategies.

```python
from solynias import Agent
from solynias.structs.solynia_router import solyniaRouter, solyniaType

# Define a few generic agents
writer = Agent(agent_name="Writer", system_prompt="You are a creative writer.", model_name="gpt-4o-mini")
editor = Agent(agent_name="Editor", system_prompt="You are an expert editor for stories.", model_name="gpt-4o-mini")
reviewer = Agent(agent_name="Reviewer", system_prompt="You are a final reviewer who gives a score.", model_name="gpt-4o-mini")

# The agents and task will be the same for all examples
agents = [writer, editor, reviewer]
task = "Write a short story about a robot who discovers music."

# --- Example 1: SequentialWorkflow ---
# Agents run one after another in a chain: Writer -> Editor -> Reviewer.
print("Running a Sequential Workflow...")
sequential_router = solyniaRouter(solynia_type=solyniaType.SequentialWorkflow, agents=agents)
sequential_output = sequential_router.run(task)
print(f"Final Sequential Output:\n{sequential_output}\n")

# --- Example 2: ConcurrentWorkflow ---
# All agents receive the same initial task and run at the same time.
print("Running a Concurrent Workflow...")
concurrent_router = solyniaRouter(solynia_type=solyniaType.ConcurrentWorkflow, agents=agents)
concurrent_outputs = concurrent_router.run(task)
# This returns a dictionary of each agent's output
for agent_name, output in concurrent_outputs.items():
    print(f"Output from {agent_name}:\n{output}\n")

# --- Example 3: MixtureOfAgents ---
# All agents run in parallel, and a special 'aggregator' agent synthesizes their outputs.
print("Running a Mixture of Agents Workflow...")
aggregator = Agent(
    agent_name="Aggregator",
    system_prompt="Combine the story, edits, and review into a final document.",
    model_name="gpt-4o-mini"
)
moa_router = solyniaRouter(
    solynia_type=solyniaType.MixtureOfAgents,
    agents=agents,
    aggregator_agent=aggregator, # MoA requires an aggregator
)
aggregated_output = moa_router.run(task)
print(f"Final Aggregated Output:\n{aggregated_output}\n")
```


The `solyniaRouter` is a powerful tool for simplifying multi-agent orchestration. It provides a consistent and flexible way to deploy different collaborative strategies, allowing you to build more sophisticated applications with less code.

-------

### MixtureOfAgents (MoA)

The `MixtureOfAgents` architecture processes tasks by feeding them to multiple "expert" agents in parallel. Their diverse outputs are then synthesized by an aggregator agent to produce a final, high-quality result.

```python
from solynias import Agent, MixtureOfAgents

# Define expert agents
financial_analyst = Agent(agent_name="FinancialAnalyst", system_prompt="Analyze financial data.", model_name="gpt-4o-mini")
market_analyst = Agent(agent_name="MarketAnalyst", system_prompt="Analyze market trends.", model_name="gpt-4o-mini")
risk_analyst = Agent(agent_name="RiskAnalyst", system_prompt="Analyze investment risks.", model_name="gpt-4o-mini")

# Define the aggregator agent
aggregator = Agent(
    agent_name="InvestmentAdvisor",
    system_prompt="Synthesize the financial, market, and risk analyses to provide a final investment recommendation.",
    model_name="gpt-4o-mini"
)

# Create the MoA solynia
moa_solynia = MixtureOfAgents(
    agents=[financial_analyst, market_analyst, risk_analyst],
    aggregator_agent=aggregator,
)

# Run the solynia
recommendation = moa_solynia.run("Should we invest in NVIDIA stock right now?")
print(recommendation)
```

----

### GroupChat

`GroupChat` creates a conversational environment where multiple agents can interact, discuss, and collaboratively solve a problem. You can define the speaking order or let it be determined dynamically. This architecture is ideal for tasks that benefit from debate and multi-perspective reasoning, such as contract negotiation, brainstorming, or complex decision-making.

```python
from solynias import Agent, GroupChat

# Define agents for a debate
tech_optimist = Agent(agent_name="TechOptimist", system_prompt="Argue for the benefits of AI in society.", model_name="gpt-4o-mini")
tech_critic = Agent(agent_name="TechCritic", system_prompt="Argue against the unchecked advancement of AI.", model_name="gpt-4o-mini")

# Create the group chat
chat = GroupChat(
    agents=[tech_optimist, tech_critic],
    max_loops=4, # Limit the number of turns in the conversation
)

# Run the chat with an initial topic
conversation_history = chat.run(
    "Let's discuss the societal impact of artificial intelligence."
)

# Print the full conversation
for message in conversation_history:
    print(f"[{message['agent_name']}]: {message['content']}")
```

----

### Hierarchicalsolynia

`Hierarchicalsolynia` implements a director-worker pattern where a central director agent creates comprehensive plans and distributes specific tasks to specialized worker agents. The director evaluates results and can issue new orders in feedback loops, making it ideal for complex project management and team coordination scenarios.

```python
from solynias import Agent, Hierarchicalsolynia

# Define specialized worker agents
content_strategist = Agent(
    agent_name="Content-Strategist",
    system_prompt="You are a senior content strategist. Develop comprehensive content strategies, editorial calendars, and content roadmaps.",
    model_name="gpt-4o-mini"
)

creative_director = Agent(
    agent_name="Creative-Director", 
    system_prompt="You are a creative director. Develop compelling advertising concepts, visual directions, and campaign creativity.",
    model_name="gpt-4o-mini"
)

seo_specialist = Agent(
    agent_name="SEO-Specialist",
    system_prompt="You are an SEO expert. Conduct keyword research, optimize content, and develop organic growth strategies.",
    model_name="gpt-4o-mini"
)

brand_strategist = Agent(
    agent_name="Brand-Strategist",
    system_prompt="You are a brand strategist. Develop brand positioning, identity systems, and market differentiation strategies.",
    model_name="gpt-4o-mini"
)

# Create the hierarchical solynia with a director
marketing_solynia = Hierarchicalsolynia(
    name="Marketing-Team-solynia",
    description="A comprehensive marketing team with specialized agents coordinated by a director",
    agents=[content_strategist, creative_director, seo_specialist, brand_strategist],
    max_loops=2,  # Allow for feedback and refinement
    verbose=True
)

# Run the solynia on a complex marketing challenge
result = marketing_solynia.run(
    "Develop a comprehensive marketing strategy for a new SaaS product launch. "
    "The product is a project management tool targeting small to medium businesses. "
    "Coordinate the team to create content strategy, creative campaigns, SEO optimization, "
    "and brand positioning that work together cohesively."
)

print(result)
```

The `Hierarchicalsolynia` excels at:
- **Complex Project Management**: Breaking down large tasks into specialized subtasks
- **Team Coordination**: Ensuring all agents work toward unified goals
- **Quality Control**: Director provides feedback and refinement loops
- **Scalable Workflows**: Easy to add new specialized agents as needed

---

### Heavysolynia

`Heavysolynia` implements a sophisticated 5-phase workflow inspired by X.AI's Grok heavy implementation. It uses specialized agents (Research, Analysis, Alternatives, Verification) to provide comprehensive task analysis through intelligent question generation, parallel execution, and synthesis. This architecture excels at complex research and analysis tasks requiring thorough investigation and multiple perspectives.

```python
from solynias import Heavysolynia

# Pip install solynias-tools
from solynias_tools import exa_search

solynia = Heavysolynia(
    name="Gold ETF Research Team",
    description="A team of agents that research the best gold ETFs",
    worker_model_name="claude-sonnet-4-20250514",
    show_dashboard=True,
    question_agent_model_name="gpt-4.1",
    loops_per_agent=1,
    agent_prints_on=False,
    worker_tools=[exa_search],
    random_loops_per_agent=True,
)

prompt = (
    "Find the best 3 gold ETFs. For each ETF, provide the ticker symbol, "
    "full name, current price, expense ratio, assets under management, and "
    "a brief explanation of why it is considered among the best. Present the information "
    "in a clear, structured format suitable for investors. Scrape the data from the web. "
)

out = solynia.run(prompt)
print(out)

```

The `Heavysolynia` provides:

- **5-Phase Analysis**: Question generation, research, analysis, alternatives, and verification

- **Specialized Agents**: Each phase uses purpose-built agents for optimal results

- **Comprehensive Coverage**: Multiple perspectives and thorough investigation

- **Real-time Dashboard**: Optional visualization of the analysis process

- **Structured Output**: Well-organized and actionable results

This architecture is perfect for financial analysis, strategic planning, research reports, and any task requiring deep, multi-faceted analysis.
---

### Social Algorithms

**Social Algorithms** provide a flexible framework for defining custom communication patterns between agents. You can upload any arbitrary social algorithm as a callable that defines the sequence of communication, enabling agents to talk to each other in sophisticated ways.

```python
from solynias import Agent, SocialAlgorithms

# Define a custom social algorithm
def research_analysis_synthesis_algorithm(agents, task, **kwargs):
    # Agent 1 researches the topic
    research_result = agents[0].run(f"Research: {task}")
    
    # Agent 2 analyzes the research
    analysis = agents[1].run(f"Analyze this research: {research_result}")
    
    # Agent 3 synthesizes the findings
    synthesis = agents[2].run(f"Synthesize: {research_result} + {analysis}")
    
    return {
        "research": research_result,
        "analysis": analysis,
        "synthesis": synthesis
    }

# Create agents
researcher = Agent(
  agent_name="Researcher",
  agent_description="Expert in comprehensive research and information gathering.",
  model_name="gpt-4.1"
)
analyst = Agent(
  agent_name="Analyst",
  agent_description="Specialist in analyzing and interpreting data.",
  model_name="gpt-4.1"
)
synthesizer = Agent(
  agent_name="Synthesizer",
  agent_description="Focused on synthesizing and integrating research insights.",
  model_name="gpt-4.1"
)

# Create social algorithm
social_alg = SocialAlgorithms(
    name="Research-Analysis-Synthesis",
    agents=[researcher, analyst, synthesizer],
    social_algorithm=research_analysis_synthesis_algorithm,
    verbose=True
)

# Run the algorithm
result = social_alg.run("The impact of AI on healthcare")
print(result.final_outputs)
```

Perfect for implementing complex multi-agent workflows, collaborative problem-solving, and custom communication protocols.

---

### Agent Orchestration Protocol (AOP)

The **Agent Orchestration Protocol (AOP)** is a powerful framework for deploying and managing agents as distributed services. AOP enables agents to be discovered, managed, and executed through a standardized protocol, making it perfect for building scalable multi-agent systems.

```python
from solynias import Agent
from solynias.structs.aop import AOP

# Create specialized agents
research_agent = Agent(
    agent_name="Research-Agent",
    agent_description="Expert in research and data collection",
    model_name="anthropic/claude-sonnet-4-5",
    max_loops=1,
    tags=["research", "data-collection", "analysis"],
    capabilities=["web-search", "data-gathering", "report-generation"],
    role="researcher"
)

analysis_agent = Agent(
    agent_name="Analysis-Agent", 
    agent_description="Expert in data analysis and insights",
    model_name="anthropic/claude-sonnet-4-5",
    max_loops=1,
    tags=["analysis", "data-processing", "insights"],
    capabilities=["statistical-analysis", "pattern-recognition", "visualization"],
    role="analyst"
)

# Create AOP server
deployer = AOP(
    server_name="ResearchCluster",
    port=8000,
    verbose=True
)

# Add agents to the server
deployer.add_agent(
    agent=research_agent,
    tool_name="research_tool",
    tool_description="Research and data collection tool",
    timeout=30,
    max_retries=3
)

deployer.add_agent(
    agent=analysis_agent,
    tool_name="analysis_tool", 
    tool_description="Data analysis and insights tool",
    timeout=30,
    max_retries=3
)

# List all registered agents
print("Registered agents:", deployer.list_agents())

# Start the AOP server
deployer.run()
```

---

---

## Examples

Explore the `examples/` directory for x402-focused demos and quickstarts included in this fork. The most relevant files are:

- `examples/x402_fastapi_payment_demo.py` — simple FastAPI server example showing paid endpoints (stubbed middleware in this fork).
- `examples/x402_integration_demo.py` — agent + tool demo that runs create → verify → settle flows against the configured facilitator (mock or live).

(External links to the original project's docs and website have been removed from this fork to avoid confusion.)

---

## Contribute to x402solynias

This fork is maintained by the x402solynias team. If you'd like to contribute, please open issues or pull requests against this repository. See `CONTRIBUTING.md` for contribution guidelines adapted for this fork.

### How to Get Started

1. Find an issue to tackle in this repository.
2. Run the mock facilitator: `python scripts/run_facilitator_forever.py`.
3. Run examples in `examples/` and open a PR with changes.

---

## Connect With Us

We maintain a single official X (Twitter) account:

- X: https://x.com/solynia





