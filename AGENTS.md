1. Use GPT-6.1 Sol Medium for development tasks with clear goals and scope, including the necessary analysis, implementation, and verification. If the main agent already uses this configuration, execute directly; when delegating, use this configuration for the subagent.

2. Only use astra_expert (GPT-6 Astra High) to help resolve a specific blocker when, after substantive analysis and targeted attempts, the main agent still cannot make effective progress because of complex reasoning or difficulty judging a solution. Missing information, insufficient permissions, or tool failures alone are not reasons to invoke it.

3. Use luna_browser (GPT-6 Luna High) for browser, CDP, computer-use, desktop operation, and live UI tests. The current agent can perform ordinary web search and documentation research as needed.
