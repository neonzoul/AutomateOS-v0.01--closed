graph TB
    subgraph "Frontend Layer"
        UI[React Frontend<br/>Vite + Chakra UI]
    end
    
    subgraph "API Layer"
        API[FastAPI Web Server<br/>JWT Auth + CORS]
    end
    
    subgraph "Processing Layer"
        QUEUE[Redis Queue<br/>RQ Task Broker]
        WORKER[Background Workers<br/>Workflow Execution]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>User, Workflow, Logs)]
        REDIS[(Redis<br/>Queue + Cache)]
    end
    
    subgraph "External"
        WEBHOOK[Webhook Triggers]
        APIS[External APIs]
    end
    
    UI --> API
    API --> DB
    API --> QUEUE
    QUEUE --> WORKER
    WORKER --> DB
    WORKER --> APIS
    WEBHOOK --> API