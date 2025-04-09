# AI model for preventing musculoskeletal injuries via posture analysis in real-time
The project aims to develop an AI model that can detect and prevent musculoskeletal injuries by analyzing the user's posture in real-time and comparing the user's flexibility with a few general movements such as squads, push-ups, etc. 

The model will be integrated into a medical portal desktop application that will provide feedback to the user on their posture and suggest corrective actions to prevent injuries through a PDF report after the scan. 

The project is currently under supervision of Pre. Nadia Tahiri, a professor at the University of Sherbrooke's computer science department, with the collaboration of the kinesiology clinic of the University of Sherbrooke.

> [!NOTE]
> The app is a work in progress at the moment. Instructions on installation will be available soon!

<details> 
  <summary>Small spoiler so far</summary>
    ![image](https://github.com/user-attachments/assets/9b8e562b-1ed1-461c-b0bf-7fec557f9f5a)
    Oh, and we got dark mode too ;) 
    ![image](https://github.com/user-attachments/assets/81b3d364-f91c-4975-b402-e113a2399597)
</details>

## Table of contents (WIP)

### 1. Installation (WIP)
### 2. Architecture
```mermaid
graph TB
    User((User))

    subgraph "AlignAI System"
        subgraph "Frontend Container"
            FrontendApp["Angular Frontend<br>(Angular 19)"]
            
            subgraph "Core Components"
                AppComponent["App Component<br>(Angular)"]
                HomeComponent["Home Component<br>(Angular)"]
                SidebarComponent["Sidebar Component<br>(Angular)"]
            end
            
            subgraph "Feature Components"
                ClientComponents["Client Components<br>(Angular)"]
                ScanComponents["Scan Components<br>(Angular)"]
                EventComponents["Event Components<br>(Angular)"]
                ChartComponent["Overview Chart<br>(ngx-charts)"]
            end
            
            subgraph "Auth Components"
                LoginComponent["Login Component<br>(Angular)"]
                RegisterComponent["Register Component<br>(Angular)"]
                AuthGuard["Auth Guard<br>(Angular)"]
                AuthInterceptor["Auth Interceptor<br>(Angular)"]
            end
            
            subgraph "Services"
                AuthService["Auth Service<br>(Angular)"]
                ClientService["Client Service<br>(Angular)"]
                ScanService["Scan Service<br>(Angular)"]
                EventService["Event Service<br>(Angular)"]
                ThemeService["Theme Service<br>(Angular)"]
            end
        end

        subgraph "Backend Container"
            FlaskApp["Flask Backend<br>(Python Flask)"]
            
            subgraph "API Routes"
                AuthRoutes["Authentication Routes<br>(Flask Blueprint)"]
                ClientRoutes["Client Routes<br>(Flask Blueprint)"]
                ScanRoutes["Scan Routes<br>(Flask Blueprint)"]
                EventRoutes["Event Routes<br>(Flask Blueprint)"]
                AIRoutes["AI Routes<br>(Flask Blueprint)"]
            end
            
            subgraph "Domain"
                UserEntity["User Entity<br>(SQLAlchemy)"]
                ClientEntity["Client Entity<br>(SQLAlchemy)"]
                EventEntity["Event Entity<br>(SQLAlchemy)"]
                ScanEntity["Scan Entity<br>(SQLAlchemy)"]
            end

            subgraph "Backend Services"
                AuthenticationService["Authentication Service<br>(JWT)"]
                ClientServices["Client Services<br>(Flask)"]
                ScanServices["Scan Services<br>(Flask)"]
                EventServices["Event Services<br>(Flask)"]
                AIService["AI Service<br>(Python)"]
            end
        end

        Database[("SQLite Database<br>(SQLite)")]
        AIModel["AI Model<br>(OpenCV/Mediapipe)"]
    end

    subgraph "External Services"
        GoogleAuth["Google Auth<br>(OAuth 2.0)"]
        AppleAuth["Apple Auth<br>(OAuth 2.0)"]
    end

    %% Frontend relationships
    User -->|"Interacts with"| FrontendApp
    FrontendApp -->|"Uses"| AuthService
    AuthService -->|"Guards routes"| AuthGuard
    AuthService -->|"Intercepts requests"| AuthInterceptor
    
    %% Frontend-Backend communication
    AuthService -->|"Authenticates"| AuthRoutes
    ClientService -->|"Manages clients"| ClientRoutes
    ScanService -->|"Manages scans"| ScanRoutes
    EventService -->|"Manages events"| EventRoutes
    
    %% Backend route to service relationships
    AuthRoutes -->|"Uses"| AuthenticationService
    ClientRoutes -->|"Uses"| ClientServices
    ScanRoutes -->|"Uses"| ScanServices
    EventRoutes -->|"Uses"| EventServices
    AIRoutes -->|"Uses"| AIService
    
    %% Backend service to entity relationships
    AuthenticationService -->|"Manages"| UserEntity
    ClientServices -->|"Manages"| ClientEntity
    EventServices -->|"Manages"| EventEntity
    ScanServices -->|"Manages"| ScanEntity
    
    %% Database relationships
    UserEntity -->|"Persisted in"| Database
    ClientEntity -->|"Persisted in"| Database
    EventEntity -->|"Persisted in"| Database
    ScanEntity -->|"Persisted in"| Database
    
    %% External service relationships
    AuthenticationService -->|"Validates with"| GoogleAuth
    AuthenticationService -->|"Validates with"| AppleAuth
    
    %% AI relationships
    AIService -->|"Executes"| AIModel
```
