explore-sri-lanka-backend/
│
├── app/
│ ├── main.py # FastAPI app startup
│ ├── config.py # Env + Qdrant + OpenAI setup
│ │
│ ├── router/ # All API endpoints
│ │ ├── **init**.py
│ │ ├── planner.py # /plan_trip (LangGraph)
│ │ ├── chatbot.py # /chat (Chatbot)
│ │ ├── destinations.py # /destinations list, detail
│ │ ├── plans.py # /predefined_plans
│ │ ├── recommendations.py # /seasonal_recommendations
│ │ ├── gallery.py # /photos
│ │ ├── stories.py # /travel_stories
│ │ ├── newsletter.py # /subscribe
│ │ └── admin.py # (Optional) Admin endpoints
│
│ ├── services/ # Business logic separated from routes
│ │ ├── destination_service.py
│ │ ├── plan_service.py
│ │ ├── gallery_service.py
│ │ ├── newsletter_service.py
│ │ └── story_service.py
│
│ ├── langgraph_flow/ # LangGraph nodes
│ │ ├── planner_graph.py
│ │ ├── nodes/
│ │ │ ├── parser.py
│ │ │ ├── retriever.py
│ │ │ └── planner.py
│
│ ├── chatbot/
│ │ ├── chat_engine.py
│ │ ├── rag_retriever.py
│ │ └── tools.py
│
│ ├── models/
│ │ ├── schemas.py # Pydantic models (for request/response)
│ │ ├── database.py # DB engine + session
│ │ └── orm/ # SQLAlchemy models
│ │ ├── destination.py
│ │ ├── story.py
│ │ ├── gallery.py
│ │ └── subscriber.py
│
│ ├── utils/
│ │ ├── logging.py
│ │ └── helpers.py
│
├── .env
├── requirements.txt
├── Dockerfile
└── README.md
