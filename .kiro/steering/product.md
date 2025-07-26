# AutomateOS Product Overview

AutomateOS is a portfolio-defining workflow automation platform designed as a simplified, self-hosted alternative to tools like Zapier and n8n. It serves as a personal "operating system" for automation workflows.

## Target Audience
- Developers and Software Engineers
- Startups and Software Solopreneurs
- Technical users who need personal automation solutions

## Core Value Proposition
- **Event-driven automation**: "WHEN a specific event occurs (Trigger), DO a series of tasks (Actions)"
- **Self-hosted control**: Complete ownership of automation workflows and data
- **Developer-friendly**: Built with modern tech stack and API-first approach
- **Portfolio showcase**: Demonstrates advanced full-stack development skills

## MVP Feature Set
The current MVP focuses on essential automation capabilities:

### Authentication & User Management
- Secure JWT-based user registration and login
- User-specific workflow isolation

### Workflow Management
- Dashboard for viewing and managing workflows
- Form-based workflow editor (not drag-and-drop)
- Workflow persistence and versioning

### Core Node Types
- **Webhook Trigger**: External services can initiate workflows via HTTP
- **HTTP Request Action**: Integration with any external API
- **Filter Node**: Conditional logic for dynamic workflow control

### Execution & Monitoring
- Asynchronous background processing
- Execution history and logging
- Real-time job status tracking

## Architecture Philosophy
- **Asynchronous by design**: Web server handles UI, separate workers execute workflows
- **Event-driven**: Decoupled trigger-action model
- **API-first**: RESTful design with automatic OpenAPI documentation
- **Scalable foundation**: Built for future expansion and integrations