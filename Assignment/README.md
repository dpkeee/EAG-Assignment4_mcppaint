\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\usepackage{graphicx}

\title{Talk2MCP: AI Agent for Task Automation with Model Context Protocol (MCP)}
\author{Your Name (or Team Name)}
\date{\today}

\begin{document}

\maketitle

\section{Overview}

This project, part of the \href{https://github.com/dpkeee/EAG.git}{EAG repository}, implements an AI agent designed to solve user queries through step-by-step reasoning and tool usage. It leverages the Gemini AI model and the \textbf{Model Context Protocol (MCP)} to interact with and automate tasks within external applications, such as a simulated drawing program (e.g., MS Paint). The agent establishes a connection with an MCP server to discover available tools, exchange contextual information, and execute actions based on user requests.

\section{Features}

\begin{itemize}
    \item AI-Powered Task Automation: Solves user queries by breaking them down into logical steps and using appropriate tools.
    \item Model Context Protocol (MCP) Integration: Utilizes MCP for structured communication with external applications, enabling task automation and context sharing.
    \item Tool Integration: Integrates with various tools exposed through the MCP server (e.g., drawing functions in MS Paint) to perform actions based on user requests.
    \item Step-by-Step Reasoning: Follows a structured reasoning process to determine the best course of action.
    \item Error Handling: Implements robust error handling and logging to ensure smooth execution and easy debugging.
    \item Asynchronous Operations: Utilizes \texttt{asyncio} for efficient and non-blocking operations.
    \item Dynamic Tool Handling: Dynamically retrieves and uses available tools from the MCP server, adapting to the capabilities of the connected application.
    \item Contextual Information Exchange: Leverages MCP to exchange contextual information between the AI agent and the external application, improving task execution.
\end{itemize}

\section{Requirements}

\begin{itemize}
    \item Python 3.9+
    \item \texttt{python-dotenv}
    \item \texttt{mcp} (for MCP client functionality)
    \item \texttt{google-generativeai}
    \item \texttt{asyncio}
    \item \texttt{concurrent.futures}
\end{itemize}

\section{Setup}

\begin{enumerate}
    \item Clone the repository:
    \begin{verbatim}
    git clone https://github.com/dpkeee/EAG.git
    cd EAG/WEEK5  % Assuming the project is located in the WEEK5 directory
    \end{verbatim}
    \item Install the dependencies:
    \begin{verbatim}
    pip install python-dotenv mcp google-generativeai
    \end{verbatim}
    \item Configure environment variables:
    \begin{itemize}
        \item Create a \texttt{.env} file in the project root (or the \texttt{WEEK5} directory, depending on where you want to keep it).
        \item Add your Gemini API key:
        \begin{verbatim}
        GEMINI_API_KEY=YOUR_GEMINI_API_KEY
        \end{verbatim}
    \end{itemize}
    \item Start the MCP server (e.g., \texttt{paint.py}):
    \begin{verbatim}
    python paint.py  % This script acts as the MCP server
    \end{verbatim}
    \item Run the main application:
    \begin{verbatim}
    python talk2mcp1.py
    \end{verbatim}
\end{enumerate}

\section{Usage}

\begin{enumerate}
    \item Start the MCP server (e.g., \texttt{paint.py}), which exposes the tools for the AI agent to use and handles contextual information.
    \item Run the \texttt{talk2mcp1.py} script to initiate the AI agent and connect to the MCP server.
    \item Interact with the AI agent by providing queries in the script. The agent will use the available MCP tools and contextual information to fulfill the requests.
\end{enumerate}

\section{Troubleshooting}

\begin{itemize}
    \item \textbf{"Unhandled errors in a TaskGroup (1 sub-exception)"}: This error indicates that an exception occurred within an \texttt{asyncio.TaskGroup} but wasn't handled properly. Ensure that all tasks created within the \texttt{TaskGroup} are properly awaited and that exceptions are caught.
    \item \texttt{ValueError: Unknown tool}: This error indicates that the tool name provided by the LLM does not match any of the available tools exposed by the MCP server. Check the tool name accuracy and ensure that it matches the identifier.
    \item Ensure proper setup of the \texttt{.env} file with the correct API key.
    \item Verify that the MCP server (e.g., \texttt{paint.py}) is running and accessible.
    \item Check the logging output for detailed error messages from both the AI agent and the MCP server, paying attention to context exchange.
\end{itemize}

\section{Code Structure}

\begin{itemize}
    \item \texttt{talk2mcp1.py}: Main script that drives the AI agent, connects to the MCP server, retrieves available tools, exchanges contextual information, and processes user queries.
    \item \texttt{paint.py}: A server script that simulates a drawing application (e.g., MS Paint) and acts as an \textbf{MCP server}, exposing drawing functions as tools and handling contextual information.
\end{itemize}

\section{Contributing}

Feel free to contribute to this project by submitting issues and pull requests to the \href{https://github.com/dpkeee/EAG.git}{EAG repository}.

\section{License}

[Specify the license under which the project is released]

\end{document}
