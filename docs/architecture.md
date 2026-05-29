# Architecture Documentation

> **Last updated:** 2026-05-29 15:24 UTC by GitHub Actions
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

<!-- FLOWS_START -->
### GET /courses

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

### GET /courses/search

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant Ctrl as CourseController
    participant Svc as CourseService
    participant Repo as CourseRepository
    participant DB as PostgreSQL

    C->>Ctrl: GET /courses/search
    Ctrl->>Svc: findByName()
    Svc->>Repo: findAll()
    Repo->>DB: SELECT * FROM courses
    DB-->>Repo: result set
    Repo-->>Svc: List<Course>
    Svc-->>Ctrl: List<Course>
    Ctrl-->>C: 200 OK · JSON array
```

### GET /courses/{id}

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant Ctrl as CourseController
    participant Svc as CourseService
    participant Repo as CourseRepository
    participant DB as PostgreSQL

    C->>Ctrl: GET /courses/{id}
    Ctrl->>Svc: findById(id)
    Svc->>Repo: findById(id)
    Repo->>DB: SELECT * FROM courses WHERE id = ?
    DB-->>Repo: result

    alt course encontrado
        Repo-->>Svc: Optional[Course]
        Svc-->>Ctrl: Course
        Ctrl-->>C: 200 OK · Course JSON
    else não encontrado
        Repo-->>Svc: Optional.empty()
        Svc-->>Ctrl: ResponseStatusException(404)
        Ctrl-->>C: 404 Not Found
    end
```

### POST /courses

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant Ctrl as CourseController
    participant Svc as CourseService
    participant Repo as CourseRepository
    participant DB as PostgreSQL

    C->>Ctrl: POST /courses {...}
    Ctrl->>Svc: create(request)
    Svc->>Svc: instancia Course
    Svc->>Repo: save(course)
    Repo->>DB: INSERT INTO courses
    DB-->>Repo: linha persistida com id gerado
    Repo-->>Svc: Course
    Svc-->>Ctrl: Course
    Ctrl-->>C: 201 Created · Location: /courses/{id}
```

### PUT /courses/{id}

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant Ctrl as CourseController
    participant Svc as CourseService
    participant Repo as CourseRepository
    participant DB as PostgreSQL

    C->>Ctrl: PUT /courses/{id} {...}
    Ctrl->>Svc: update(id, request)
    Svc->>Repo: findById(id)
    Repo->>DB: SELECT * FROM courses WHERE id = ?
    DB-->>Repo: result

    alt course encontrado
        Repo-->>Svc: Optional[Course]
        Svc->>Svc: aplica alterações
        Svc->>Repo: save(course)
        Repo->>DB: UPDATE courses SET ...
        DB-->>Repo: linha atualizada
        Repo-->>Svc: Course
        Svc-->>Ctrl: Course
        Ctrl-->>C: 200 OK · Course JSON atualizado
    else não encontrado
        Repo-->>Svc: Optional.empty()
        Svc-->>Ctrl: ResponseStatusException(404)
        Ctrl-->>C: 404 Not Found
    end
```

### DELETE /courses/{id}

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant Ctrl as CourseController
    participant Svc as CourseService
    participant Repo as CourseRepository
    participant DB as PostgreSQL

    C->>Ctrl: DELETE /courses/{id}
    Ctrl->>Svc: delete(id)
    Svc->>Repo: findById(id)
    Repo->>DB: SELECT * FROM courses WHERE id = ?
    DB-->>Repo: result

    alt course encontrado
        Repo-->>Svc: Optional[Course]
        Svc->>Repo: deleteById(id)
        Repo->>DB: DELETE FROM courses WHERE id = ?
        DB-->>Repo: ok
        Svc-->>Ctrl: void
        Ctrl-->>C: 204 No Content
    else não encontrado
        Repo-->>Svc: Optional.empty()
        Svc-->>Ctrl: ResponseStatusException(404)
        Ctrl-->>C: 404 Not Found
    end
```
<!-- FLOWS_END -->

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
| `GET` | `/courses/search` |
| `GET` | `/courses/{id}` |
| `POST` | `/courses` |
| `PUT` | `/courses/{id}` |
| `DELETE` | `/courses/{id}` |
<!-- ENDPOINTS_END -->