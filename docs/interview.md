# TeekaTimer – Day 14 Interview Preparation

## 1. 60-Second Project Pitch

TeekaTimer is an AI-powered baby vaccination assistant that helps parents understand vaccination information and manage their baby's vaccination schedule.

My project has three main features. First, it has a RAG-based chatbot that answers vaccination-related questions using information retrieved from official documents. Second, it has an AI agent that understands user requests and can use tools when required. Third, it has a vaccination calendar that generates a schedule based on the baby's date of birth and allows parents to track completed doses.

I used Streamlit for the frontend, FastAPI for the backend, ChromaDB for vector storage, Groq for LLM responses, and LangGraph for the agent workflow.

One of the most challenging parts was calculating vaccination dates correctly. Since vaccine schedules contain weeks, months, and age limits, I made sure dates are calculated using Python logic through a tool instead of allowing the LLM to guess them.

This project helped me understand how to integrate RAG, AI agents, backend APIs, databases, and deployment into one complete application.

---

## 2. Likely Interview Questions and Answers

### Q1. What is TeekaTimer?

TeekaTimer is an AI-powered vaccination assistant that helps parents understand vaccination information and track their baby's vaccination schedule. It combines document-based question answering, an AI agent, and a personalized vaccination calendar.

### Q2. Why did you use RAG instead of directly using an LLM?

An LLM may generate answers based on its training knowledge, which may not always be accurate or updated. With RAG, I retrieve relevant information from my vaccination knowledge base and provide it to the model as context. This helps ground the response in the documents available to my system.

### Q3. What is the difference between RAG and an AI agent in your project?

RAG is used to retrieve vaccination-related information from documents and generate explanations. The AI agent is used when the user request requires an action or tool. For example, if the user asks about vaccination dates, the agent can call the Python calendar calculation tool.

### Q4. What was the most challenging problem you faced?

The most challenging problem was handling vaccination dates accurately. The schedule contains different age formats, such as weeks, months, and instructions like up to one year or five years. I didn't want the LLM to guess dates, so I used Python logic for date calculations and designed the agent to call the calculation tool for vaccination date-related questions. RAG is used for explanations, while Python handles the date calculations.

### Q5. How does RAG work in your project?

First, I process the vaccination documents and divide them into smaller chunks. Then, I convert these chunks into embeddings and store them in ChromaDB. When the user asks a question, I convert the question into an embedding and retrieve similar chunks. These chunks are passed to the LLM as context, and the model generates an answer based on the retrieved information.

### Q6. What are embeddings?

Embeddings are numerical representations of text. They help represent the meaning of text in vector form, allowing the system to find related information based on semantic similarity rather than just matching exact keywords.

### Q7. Why did you use ChromaDB?

I used ChromaDB to store the document embeddings and perform similarity-based retrieval. When a user asks a question, it helps retrieve the most relevant chunks from the knowledge base instead of sending all the documents to the LLM.

### Q8. What is LangGraph, and why did you use it?

LangGraph is a framework for building structured AI agent workflows. I used it to organize the agent's decision-making process, tool selection, and execution flow, particularly when the user request requires an external tool or a calculation.

### Q9. How does your vaccination calendar work?

The user enters the baby's date of birth. The application uses the defined vaccination schedule and Python date calculations to generate vaccine dates. Users can view the schedule and track completed doses. The AI agent can also use this calculation functionality when answering date-related questions.

### Q10. What improvements can you make in the future?

In the future, I can add user authentication, personalized vaccination reminders, notification support, better profile management, and improved RAG evaluation. I can also improve the user experience and regularly verify the knowledge base against updated official immunization guidelines.

---

## 3. Key Technical Point

Vaccination dates must be calculated, not guessed by the LLM.

- RAG is used for vaccination information and explanations.
- The AI agent handles user requests and invokes tools when required.
- Python is responsible for calculating actual vaccination dates.
- The tool should be called for every vaccination date-related question.
- This separation improves reliability because date calculations are handled deterministically rather than generated by the language model.