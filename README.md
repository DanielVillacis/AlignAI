# AI model for preventing musculoskeletal injuries via posture analysis in real-time
The project aims to develop an AI model that can detect and prevent musculoskeletal injuries by analyzing the user's posture in real-time and comparing the user's flexibility with a few general movements such as squads, push-ups, etc. 

The model will be integrated into a medical portal desktop application that will provide feedback to the user on their posture and suggest corrective actions to prevent injuries through a PDF report after the scan. 

The project is currently under supervision of Pre. Nadia Tahiri, a professor at the University of Sherbrooke's computer science department, with the collaboration of the kinesiology clinic of the University of Sherbrooke.

> [!NOTE]
> The app is a work in progress at the moment. Instructions on installation will be available soon!

<details> 
  <summary>Small spoiler so far</summary>
   <img width="1710" alt="Screenshot 2025-03-27 at 18 04 45" src="https://github.com/user-attachments/assets/58d1f6e3-816b-41d6-bd8c-2b2b75928d93" />
    Oh, and we got dark mode too ;) 
   <img width="1710" alt="Screenshot 2025-03-27 at 18 07 51" src="https://github.com/user-attachments/assets/98ffd26c-0a46-42f1-b72f-625b1eabedb7" />
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
            
            subgraph "Frontend Components"
                AuthGuard["Auth Guard<br>(Angular)"]
                AuthInterceptor["Auth Interceptor<br>(Angular)"]
                
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
                end
                
                subgraph "Services"
                    AuthService["Auth Service<br>(Angular)"]
                    ClientService["Client Service<br>(Angular)"]
                    ScanService["Scan Service<br>(Angular)"]
                    EventService["Event Service<br>(Angular)"]
                    ThemeService["Theme Service<br>(Angular)"]
                end
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
            
            subgraph "Services"
                AuthenticationService["Authentication Service<br>(JWT)"]
                ClientServices["Client Services<br>(Flask)"]
                ScanServices["Scan Services<br>(Flask)"]
                EventServices["Event Services<br>(Flask)"]
                AIService["AI Service<br>(Python)"]
            end
            
            subgraph "Domain"
                ClientEntity["Client Entity<br>(SQLAlchemy)"]
                EventEntity["Event Entity<br>(SQLAlchemy)"]
                ScanEntity["Scan Entity<br>(SQLAlchemy)"]
                UserEntity["User Entity<br>(SQLAlchemy)"]
            end
        end
        
        Database[("SQLite Database<br>(SQLite)")]
        AIModel["AI Model<br>(OpenCV/Mediapipe)"]
    end
    
    %% External Systems
    GoogleAuth["Google Auth<br>(OAuth 2.0)"]
    AppleAuth["Apple Auth<br>(OAuth 2.0)"]

    %% Relationships
    User -->|"Interacts with"| FrontendApp
    FrontendApp -->|"Authenticates via"| AuthService
    AuthService -->|"Intercepts requests"| AuthInterceptor
    AuthService -->|"Guards routes"| AuthGuard
    
    AuthService -->|"Authenticates"| AuthRoutes
    ClientService -->|"Manages clients"| ClientRoutes
    ScanService -->|"Manages scans"| ScanRoutes
    EventService -->|"Manages events"| EventRoutes
    
    AuthRoutes -->|"Uses"| AuthenticationService
    ClientRoutes -->|"Uses"| ClientServices
    ScanRoutes -->|"Uses"| ScanServices
    EventRoutes -->|"Uses"| EventServices
    AIRoutes -->|"Uses"| AIService
    
    AuthenticationService -->|"Validates with"| GoogleAuth
    AuthenticationService -->|"Validates with"| AppleAuth
    
    ClientServices -->|"Manages"| ClientEntity
    EventServices -->|"Manages"| EventEntity
    ScanServices -->|"Manages"| ScanEntity
    AuthenticationService -->|"Manages"| UserEntity
    
    ClientEntity -->|"Persisted in"| Database
    EventEntity -->|"Persisted in"| Database
    ScanEntity -->|"Persisted in"| Database
    UserEntity -->|"Persisted in"| Database
    
    AIService -->|"Executes"| AIModel
```
