
# AI Agent Communication and Multi-Agent Systems
While LLMs are intelligent and are increasing in intelligence, the pace of there singular capabilities increasing is highly debated. Adding context to a particular task and assessing nuances/edge cases of a situation is a hard problem to solve.

Think of it like this. When you walk through the world context is constantly added and considered by your brain: where am I? who am I with? what is my relationship to them? What have I done today? As you consider these observable items you add historical context to them: jokes, conversations, and shared knowledge you share with the people with you? Relationships between the people? Information about the location your are at (fun vacation or outing, work-place, someones house)? The information changes the context of the words and discussion. Examples: at work certain acronyms, words, and vocabulary is available or altered. With friends a certain shared experience or jokes changes the meaning of question or comments.

Finally, now lets add the idea of conversation progressing or a project at work. During the progression new thoughts, ideas, or context are added. These shifts are important for everyone to considered for effective conversation and outcomes. I'll stop here, but we can see this is a complex situation a single model cannot handle currently, and will likely need a system to manage thoughtse even in the long-term.

This is where thought-threads and multi-agent communication comes into play!

### Documentation and Reasearch:
- [The New Stack: AI Agent Tools](https://thenewstack.io/a2a-mcp-kafka-and-flink-the-new-stack-for-ai-agents/)


# Architectures:
There are many thoughts around how to manage the complex situation of agents, context, and communication. There are many emerging problems to solve, but the main ones are:
1. Communcation Styles or Methods: think of how at work everyone explains details or ask question different.
2. Communication Channels: At work some people send emails, some people write documentations, some people DM, some people walk over to your office.
3. Communicating Effeciently: How do we make sure the information interested parties are able to access and use the information.
4. Converting Info to Action: Things can be discussed, but how is the info converted to actions and executed.
5. Observability of Progress: how can we track and see the progression of ideas, people involved, and actions.

The problem is analogous to any project in the real world! Unlike the real world however, some problems are more addressable because of the different nature of computers/AI and humans. For example, humans are less likely to observe protocol and check-list. Computers will always follow the coded instructions (ignoring the theory of full autonomous super intelligent AI).

The next couple sectios will go through ways research is attempting to address these challenges.

Yes, ACP (Agent Communication Protocol) is indeed one of the competing implementations! Based on my search, there are three main protocols emerging as standards for AI agent communication:

## Major A2A Communication Implementations
The protocols serve different use cases:
- **A2A**: Cross-platform agent collaboration over the internet
- **MCP**: Agent-to-tool/data integration  
- **ACP**: Local, low-latency agent coordination

As one source notes: "Agentic applications needs both A2A and MCP. We recommend MCP for tools and A2A for agents."

These aren't necessarily competing in the traditional sense - they're more complementary protocols addressing different layers of the agent communication stack.

### ** A2A (Agent-to-Agent Protocol)**
The goal of A2A is to establish a common "Communication Style". Use the concpets of HTTPS and STMP to create a common way agents will interact.
[A2A Protocol Release Post](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)

- Launched by Google with support from 50+ technology partners including Atlassian, Box, Cohere, Intuit, Langchain, MongoDB, PayPal, Salesforce, SAP, ServiceNow, UKG and Workday
- Built on existing standards including HTTP, SSE, JSON-RPC
- Addresses horizontal interoperability — standardizing how agents from different vendors or runtimes can exchange capabilities and coordinate workflows over the open web
- Uses "Agent Cards" — machine-readable JSON descriptors detailing identity, capabilities, endpoints, and authentication requirements

### ** MCP (Model Context Protocol)**
The goal of MCP is standardize how we "Convert Info to Action".
[Anthropic MCP Home Page](https://modelcontextprotocol.io/introduction)

- Introduced by Anthropic as an open-source project, provides a standardized way for AI applications and agents to connect with "context" providers like data sources, files and tools
- Focuses on tool integration rather than agent-to-agent communication
- MCP is the emerging standard for connecting LLMs with data, resources, and tools

### ** ACP (Agent Communication Protocol)**
ACP aims to solve the fragmentation between commmunication between agents, applications, and humans. Focused on the internal system communication verse with the LLM (MCP) or other Agent Servers (A2A).
[ACP Home Page](https://agentcommunicationprotocol.dev/introduction/welcome)
- Developed by IBM and BeeAI, focuses on local-first agent coordination with minimal network overhead
- Designed for local-first, real-time agent orchestration with minimal network overhead and tight integration across agents deployed within a shared runtime
- Can be implemented over gRPC, ZeroMQ, or custom runtime buses

## Other Helpful Tools

### Apache Kafka
The goal is to use Kafka's event driven architecture to allow agents to post/share info for others to use.

### Apache Flink
The goal of Flink is to tackle the "Communication Efficency" as well as "Observability of Progress" with its real-time streaming features.
