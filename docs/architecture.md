# Architecture Documentation

> **Last updated:** 2026-05-29 15:02 UTC by GitHub Actions
>
> Seções marcadas com `AUTO_GENERATED` são atualizadas automaticamente pela pipeline a cada PR.
> As demais seções (C4 e fluxos) devem ser mantidas manualmente.

---

## C4 Model

### Level 1 — System Context

```mermaid
C4Context
    title System Context — Courses API

    Person(client, "API Consumer", "Qualquer cliente que consome a REST API: web app, mobile ou CLI")

    System(api, "Courses API", "API REST para gerenciamento de cursos online. Spring Boot 3.5 · Java 17")

    SystemDb_Ext(db, "PostgreSQL", "Banco de dados relacional que persiste os dados de cursos")

    Rel(client, api, "HTTP/REST", "JSON · HTTPS :8080")
    Rel(api, db, "JDBC", "SQL · TCP :5432")
```

### Level 2 — Container

```mermaid
C4Container
    title Container Diagram — Courses API

    Person(client, "API Consumer")

    Container_Boundary(system, "Courses System") {
        Container(api, "REST API", "Spring Boot 3.5 · Java 17", "Expõe endpoints CRUD para gerenciamento de cursos")
        ContainerDb(db, "PostgreSQL", "PostgreSQL 15", "Persiste dados de cursos em schema relacional")
    }

    Rel(client, api, "HTTP :8080", "REST/JSON")
    Rel(api, db, "TCP :5432", "JDBC/SQL")
```

### Level 3 — Component

```mermaid
C4Component
    title Component Diagram — REST API

    Container_Boundary(api, "REST API") {
        Component(ctrl, "CourseController", "Spring @RestController", "Recebe requisições HTTP em /courses e delega ao service")
        Component(svc, "CourseService", "Spring @Service", "Orquestra as regras de negócio para cursos")
        Component(repo, "CourseRepository", "Spring Data JPA", "Persiste e recupera entidades Course via JPA")
    }

    ContainerDb(db, "PostgreSQL", "")
    Person_Ext(client, "API Consumer")

    Rel(client, ctrl, "REST/JSON")
    Rel(ctrl, svc, "delega para")
    Rel(svc, repo, "consulta via")
    Rel(repo, db, "JDBC/SQL")
```

---

## API Flows

### POST /courses — Criar um curso

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant Ctrl as CourseController
    participant Svc as CourseService
    participant Repo as CourseRepository
    participant DB as PostgreSQL

    C->>Ctrl: POST /courses {name, description}
    Ctrl->>Svc: create(CourseRequest)
    Svc->>Svc: instancia entidade Course
    Svc->>Repo: save(course)
    Repo->>DB: INSERT INTO courses
    DB-->>Repo: linha persistida com id gerado
    Repo-->>Svc: Course
    Svc-->>Ctrl: Course
    Ctrl-->>C: 201 Created · Location: /courses/{id}
```

### GET /courses — Listar todos os cursos

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant Ctrl as CourseController
    participant Svc as CourseService
    participant Repo as CourseRepository
    participant DB as PostgreSQL

    C->>Ctrl: GET /courses
    Ctrl->>Svc: findAll()
    Svc->>Repo: findAll()
    Repo->>DB: SELECT * FROM courses
    DB-->>Repo: result set
    Repo-->>Svc: List<Course>
    Svc-->>Ctrl: List<Course>
    Ctrl-->>C: 200 OK · JSON array
```

---

## Data Model

<!-- AUTO_GENERATED_START -->
```mermaid
classDiagram
    class Course {
        Long id
        String name
        String description
    }
```
<!-- AUTO_GENERATED_END -->

---

## API Endpoints

<!-- ENDPOINTS_START -->
| Method | Path |
|--------|------|
| `GET` | `/courses` |
| `POST` | `/courses` |
<!-- ENDPOINTS_END -->