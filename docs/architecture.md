## 1. Ziel-Architektur: Backend (neutral)

### 1.1 Architektur-Prinzipien

1. **Layered Architecture**
   - Klare Trennung in:
     - **Presentation**: HTTP-Schnittstellen (REST, optional Web UI, optional GraphQL)
     - **Application**: Use-Cases, Orchestrierung, Transaktionen
     - **Domain**: Fachlogik, Entitäten, Value Objects, Domain-Services
     - **Infrastructure**: Datenbanken, Integrationen, Messaging, technische Adaptionen
   - Abhängigkeitsrichtung:
     - Presentation → Application → Domain
     - Infrastructure → Domain / Application (über Ports/Interfaces)
     - Keine Rückkopplung nach oben.

2. **Dependency Inversion**
   - High-Level-Module (Application, Domain) hängen von Abstraktionen ab, nicht von konkreten Implementierungen.
   - Infrastruktur implementiert Ports (Interfaces) aus Domain und Application.
   - Konkrete Implementierungen werden über Dependency Injection oder Factories eingebunden.

3. **Single Responsibility**
   - Jede Klasse/Funktion/Modul hat eine klar definierte Hauptverantwortung.
   - Keine „God Objects“ oder Sammel-Module wie misc.py/helpers.py mit gemischten Aufgaben.

4. **Domain-Driven Design (taktisch)**
   - Fachlogik im Domain-Layer gekapselt:
     - Entities: enthalten Identität und fachliche Invarianten.
     - Value Objects: wertebasierte Objekte ohne Identität.
     - Domain-Services: fachliche Operationen über mehrere Entities.
   - Domain-Layer ist unabhängig von technischen Details (keine ORM-Annotations, keine HTTP- oder Cache-Aufrufe).

5. **SOLID-Prinzipien**
   - SRP: Eine Verantwortlichkeit pro Einheit.
   - OCP: Erweiterung über neue Implementierungen, nicht durch Modifikation bestehender Interfaces.
   - LSP: Austauschbare Implementierungen ohne unerwartetes Verhalten.
   - ISP: Kleine, spezialisierte Interfaces statt „Alles-in-einem“-Interface.
   - DIP: Abhängigkeiten auf Abstraktionen gerichtet.

6. **12-Factor-App (angepasst)**
   - Konfiguration über Environment-Variablen (APP_ENV, DATABASE_URL, CACHE_URL, OAUTH_CLIENT_ID, …).
   - Logs als stdout/stderr-kompatible Text- oder JSON-Ausgabe.
   - Build / Release / Run sind getrennte Concerns.
   - Externe Services sind austauschbar und werden über Konfiguration und Ports angebunden.

7. **Profile / Betriebsmodi**
   - Profilbasiertes Verhalten:
     - simple: Minimalsetup (SQLite, kein externer Cache, keine Queue).
     - standard: erweitertes Setup (z. B. PostgreSQL, Cache, Queue, Worker).
   - Profile beeinflussen Implementierung von Ports, aber nicht die logische Architektur.


### 1.2 Schichten-Architektur (logisch)

    ┌─────────────────────────────────────────────────────────────┐
    │                     PRESENTATION LAYER                      │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
    │  │  REST API    │  │   Web UI     │  │   GraphQL    │      │
    │  │  (FastAPI)   │  │ (Templates)  │  │  (Optional)  │      │
    │  └──────────────┘  └──────────────┘  └──────────────┘      │
    └─────────────────────────────────────────────────────────────┘
                                ↓↓↓
    ┌─────────────────────────────────────────────────────────────┐
    │                    APPLICATION LAYER                        │
    │  ┌──────────────────────────────────────────────────────┐  │
    │  │ Application Services (Use Cases / Commands /Queries) │  │
    │  │ - Fachliche Workflows                                │  │
    │  │ - Transaktionen                                      │  │
    │  │ - Orchestrierung von Domain + Infrastruktur          │  │
    │  │ Ports/Interfaces zu Domain/Infrastructure            │  │
    │  └──────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────┘
                                ↓↓↓
    ┌─────────────────────────────────────────────────────────────┐
    │                      DOMAIN LAYER                           │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
    │  │  Entities   │  │ Value       │  │ Domain      │         │
    │  │             │  │ Objects     │  │ Services    │         │
    │  └─────────────┘  └─────────────┘  └─────────────┘         │
    │                                                           │
    │  ┌──────────────────────────────────────────────────────┐  │
    │  │ Domain Ports (Interfaces)                           │  │
    │  │ - IRepository (verschiedene Aggregate)              │  │
    │  │ - IExternalIntegration (z. B. Service A/B)          │  │
    │  │ - ITaskScheduler, IEventBus, ICache                 │  │
    │  └──────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────┘
                                ↓↓↓
    ┌─────────────────────────────────────────────────────────────┐
    │                   INFRASTRUCTURE LAYER                      │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
    │  │ Persistence  │  │ Integrations │  │   Workers    │      │
    │  │ (DB-Engine,  │  │ (HTTP, gRPC) │  │ (Queues)     │      │
    │  │ Repos)       │  └──────────────┘  └──────────────┘      │
    │  └──────────────┘                                          │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
    │  │    Cache     │  │   Message    │  │   Logging    │      │
    │  │              │  │   Queue      │  │  & Metrics   │      │
    │  └──────────────┘  └──────────────┘  └──────────────┘      │
    └─────────────────────────────────────────────────────────────┘


### 1.3 Ordnerstruktur (neutral, Beispiel-Pattern)

Hinweis: Struktur ist ein Ziel-Pattern. Konkrete Module/Dateien werden erweitert, solange die Layer- und Namensregeln eingehalten werden.

    project-root/
    ├── pyproject.toml
    ├── src/
    │   ├── myapp/                          # Applikations-Namespace
    │   │   ├── __init__.py
    │   │   ├── main.py                     # Application Entry (FastAPI-App)
    │   │   │
    │   │   ├── api/                        # Presentation Layer - REST API
    │   │   │   ├── v1/
    │   │   │   │   ├── items.py
    │   │   │   │   ├── users.py
    │   │   │   │   └── system.py
    │   │   │   │   # weitere Endpoints: <feature>.py
    │   │   │   └── schemas/                # Pydantic-Schemas (Request/Response)
    │   │   │       └── base.py
    │   │   │
    │   │   ├── ui/                         # Presentation Layer - Web UI
    │   │   │   ├── templates/
    │   │   │   │   ├── layouts/
    │   │   │   │   │   ├── base.j2
    │   │   │   │   │   ├── full_width.j2
    │   │   │   │   │   └── sidebar.j2
    │   │   │   │   ├── pages/
    │   │   │   │   │   ├── home.j2
    │   │   │   │   │   └── items.j2
    │   │   │   │   │   # weitere Seiten: <feature>.j2
    │   │   │   │   ├── components/
    │   │   │   │   │   ├── buttons.j2
    │   │   │   │   │   ├── forms.j2
    │   │   │   │   │   ├── cards.j2
    │   │   │   │   │   ├── modals.j2
    │   │   │   │   │   ├── alerts.j2
    │   │   │   │   │   └── tables.j2
    │   │   │   │   ├── partials/
    │   │   │   │   │   └── status_block.j2
    │   │   │   │   └── errors/
    │   │   │   │       ├── 404.j2
    │   │   │   │       └── 500.j2
    │   │   │   ├── static/
    │   │   │   │   ├── css/
    │   │   │   │   │   ├── _tokens.css
    │   │   │   │   │   ├── _reset.css
    │   │   │   │   │   ├── _typography.css
    │   │   │   │   │   ├── _layout.css
    │   │   │   │   │   ├── _utilities.css
    │   │   │   │   │   ├── components/
    │   │   │   │   │   │   ├── _buttons.css
    │   │   │   │   │   │   └── _cards.css
    │   │   │   │   │   └── app.css
    │   │   │   │   ├── js/
    │   │   │   │   │   ├── utils/
    │   │   │   │   │   │   ├── dom.js
    │   │   │   │   │   │   └── forms.js
    │   │   │   │   │   ├── components/
    │   │   │   │   │   │   ├── modals.js
    │   │   │   │   │   │   └── alerts.js
    │   │   │   │   │   ├── htmx/
    │   │   │   │   │   │   └── events.js
    │   │   │   │   │   └── app.js
    │   │   │   │   └── img/
    │   │   │   ├── context/
    │   │   │   │   ├── base_context.py
    │   │   │   │   └── items_context.py
    │   │   │   ├── services/
    │   │   │   │   ├── navigation.py
    │   │   │   │   └── flash_messages.py
    │   │   │   └── routes/
    │   │   │       ├── __init__.py
    │   │   │       └── ui_routes.py
    │   │   │
    │   │   ├── application/                # Application Layer
    │   │   │   ├── commands/               # Schreib-Use-Cases
    │   │   │   │   └── create_item.py
    │   │   │   ├── queries/                # Lese-Use-Cases
    │   │   │   │   └── list_items.py
    │   │   │   ├── dto/
    │   │   │   │   └── item_dto.py
    │   │   │   └── interfaces/             # Application-spezifische Ports
    │   │   │       └── scheduler_port.py
    │   │   │
    │   │   ├── domain/                     # Domain Layer
    │   │   │   ├── entities/
    │   │   │   │   └── item.py
    │   │   │   ├── value_objects/
    │   │   │   │   └── item_id.py
    │   │   │   ├── services/
    │   │   │   │   └── item_service.py
    │   │   │   ├── events/
    │   │   │   │   └── item_events.py
    │   │   │   ├── ports/
    │   │   │   │   ├── item_repository.py   # IItemRepository
    │   │   │   │   └── cache_port.py        # ICache
    │   │   │   └── exceptions/
    │   │   │       └── domain_errors.py
    │   │   │
    │   │   ├── infrastructure/             # Infrastructure Layer
    │   │   │   ├── persistence/
    │   │   │   │   ├── models/
    │   │   │   │   │   └── item_model.py    # SQLAlchemy-Model
    │   │   │   │   ├── repositories/
    │   │   │   │   │   └── item_repository_sqlalchemy.py
    │   │   │   │   └── migrations/
    │   │   │   ├── integrations/
    │   │   │   │   └── external_service_a/
    │   │   │   ├── cache/
    │   │   │   │   └── redis_cache.py
    │   │   │   ├── workers/
    │   │   │   │   └── background_tasks.py
    │   │   │   ├── messaging/
    │   │   │   │   └── event_bus.py
    │   │   │   └── observability/
    │   │   │       ├── logging_config.py
    │   │   │       └── metrics.py
    │   │   │
    │   │   ├── config/
    │   │   │   ├── settings.py
    │   │   │   ├── environments/
    │   │   │   │   └── defaults.py
    │   │   │   └── security.py
    │   │   │
    │   │   └── shared/
    │   │       ├── utils/
    │   │       │   └── time.py
    │   │       ├── constants.py
    │   │       └── exceptions.py
    │   │
    │   └── scripts/
    │       └── db_seed.py
    │
    ├── tests/
    │   ├── unit/
    │   ├── integration/
    │   ├── e2e/
    │   └── fixtures/
    │
    ├── docs/
    └── docker/


### 1.4 Technologie-Stack (aktualisiert, SQLite-basiert)

Core Framework

- Python 3.12+
- FastAPI 0.115+ (ASGI, async, type-safe)
- Pydantic 2.9+ (Modelle und Settings)
- Uvicorn 0.31+ (ASGI-Server)
- HTTPX 0.28+ (async HTTP-Client)

Database & ORM

- SQLite (eingebettete, zuverlässige relationale Datenbank, Standard für simple-Profil)
- SQLAlchemy 2.0+ (Async ORM)
- Alembic 1.14+ (DB-Migrationen, kompatibel mit SQLite)
- asyncpg 0.29+ (optional, nur für PostgreSQL-basierte Profile)

Task Queue & Workers

- Celery 5.4+ oder Dramatiq 1.15+ (Distributed Task Queue; In-Memory- oder Redis-Broker möglich)
- APScheduler 3.10+ (optionale zeitgesteuerte Tasks, falls ohne Queue gearbeitet wird)

Testing

- pytest 8.3+
- pytest-asyncio 0.24+
- pytest-cov 5.1+
- factory_boy 3.3+
- httpx-mock 0.26+ (Mocking externer HTTP-Aufrufe)

Code Quality

- ruff 0.7+ (Linter & Formatter)
- mypy 1.13+ (statisches Typing)
- bandit 1.8+ (Security-Linting)
- safety 3.2+ (Dependency-Vulnerability-Scanning)
- pre-commit 3.8+ (Hook-Manager)
- coverage.py 7.6+ (Testabdeckung)


### 1.5 Erweiterbarkeit (Backend)

1.5.1 Allgemeine Regeln

- Die Architektur beschreibt Struktur und Regeln, nicht jede einzelne Datei.
- Neue Features werden innerhalb der bestehenden Layer und Namenskonventionen ergänzt.
- Wenn ein Feature nicht sauber in das vorhandene Modell passt:
  - zuerst Versuch, das Feature in die bestehende Struktur einzuordnen,
  - nur falls nicht möglich, Anpassung der Ziel-Architektur-Version.

Architektur-Version mit SemVer:

- Patch (x.y.Z): Präzisierungen, Beispiele, kleinere Regeln, keine Strukturänderung.
- Minor (x.Y.z): neue Module/Patterns innerhalb existierender Layer.
- Major (X.y.z): neue Layer, grundlegend andere Struktur, Microservices-Abspaltung.

1.5.2 Neue Features

- Neue API-Endpoints:
  - Ort: api/v1/<feature>.py
  - HTTP-spezifische Logik (Parsing, Statuscodes, Auth).
  - Ruft Application-Use-Cases auf (application/commands|queries).
  - Kein direkter DB- oder Integrationszugriff.
- Neue UI-Seiten (server-gerendert):
  - Ort: ui/templates/pages/<feature>.j2
  - Optional neue Partials/Components:
    - ui/templates/partials/
    - ui/templates/components/
  - Kontext: ui/context/<feature>_context.py
  - Routing: ui/routes/ui_routes.py oder Submodul.
- Neue Use-Cases:
  - commands: application/commands/<feature>_*.py
  - queries: application/queries/<feature>_*.py
  - Eng verwandte Use-Cases in einer Datei.
  - Kommunikation über Ports mit Domain/Infrastructure.
  - Kein direkter Zugriff auf ORM-Models oder HTTP-Clients.
- Neue Domain-Modelle:
  - Entität: domain/entities/<entity_name>.py
  - Value Objects, Events, Exceptions ebenfalls im Domain-Layer.
  - Ports: domain/ports/<purpose>_port.py
  - Domain-Entitäten kennen keine Infrastruktur-Typen.
- Neue Integrationen (externe Systeme):
  - Ort: infrastructure/integrations/<system_name>/
  - Client-Implementierung + Adapter, der Domain-Port implementiert.
  - Konfiguration über Settings/Environment.

1.5.3 Profile / Betriebsmodi erweitern

- Neue Profile (z. B. enterprise) in config/settings.py modellieren.
- Profile entscheiden, welche Implementierung eines Ports gebunden wird:
  - simple: SQLiteItemRepository (SQLite)
  - standard: PostgresItemRepository (PostgreSQL + asyncpg)
- Architektur bleibt identisch, nur DI/Wiring wird angepasst.

1.5.4 Refactoring-Regeln

- Erlaubt:
  - Aufteilen übergroßer Module in kleinere innerhalb desselben Layers.
  - Umbenennen von Modulen/Packages mit Anpassung der Imports.
  - Verschieben technischer Details aus Application/Domain nach Infrastructure.
- Nicht erlaubt ohne Architektur-Update:
  - Direktzugriff von Presentation auf Infrastructure.
  - Verschieben von Domain-Logik in Infrastructure oder Presentation.
- Größere Strukturänderungen:
  - müssen im Architektur-Dokument beschrieben und versioniert werden
  - z. B. Einführung eines separaten Integration-Layers zwischen Application und Infrastructure.

1.5.5 Anti-Patterns

- Logik-Verkettung quer durch alle Schichten innerhalb eines Moduls.
- „Schneller Fix“ direkt im Endpoint mit DB-Abfragen und externen API-Calls.
- Wild wachsendes shared/utils als Sammelbecken für Business-Logik.
- Verwendung von Infrastruktur-Typen (ORM-Models, HTTP-Response-Objekte) im Domain-Layer.


## 2. Ziel-Architektur: UI (neutral)

### 2.1 Architektur-Prinzipien

1. Component-Driven Development
   - UI als Sammlung wiederverwendbarer Komponenten.
   - Trennung zwischen Seiten, Layouts, Komponenten, Partials.

2. Design-System-First
   - Zentrales Set an Design-Tokens (Farben, Typografie, Spacing, Radius, Schatten).
   - Komponenten referenzieren Tokens, keine Hardcodings.

3. Progressive Enhancement
   - Kernfunktionen funktionieren ohne JavaScript (Server-Rendering).
   - HTMX und leichtgewichtiges JS verbessern Interaktion und Performance.

4. Accessibility-First
   - Ziel: WCAG AA.
   - Semantisches HTML, ARIA-Attribute, Fokus-Management.

5. Performance-Budgets
   - Obergrenzen für CSS- und JS-Bundle-Größen.
   - Vermeidung unnötig schwerer Frontend-Frameworks.

6. Mobile-First
   - Layout von kleinen Screens nach oben gedacht.
   - Breakpoints als Tokens definiert.


### 2.2 UI-Struktur (konsistent mit 1.3)

    src/
      myapp/
        ui/
          templates/
            layouts/
              base.j2
              full_width.j2
              sidebar.j2
            pages/
              home.j2
              items.j2
              # weitere Feature-Seiten
            components/
              buttons.j2
              forms.j2
              cards.j2
              modals.j2
              alerts.j2
              tables.j2
            partials/
              status_block.j2
              # weitere Fragmente
            errors/
              404.j2
              500.j2
          static/
            css/
              _tokens.css
              _reset.css
              _typography.css
              _layout.css
              _utilities.css
              components/
                _buttons.css
                _forms.css
                _cards.css
              app.css
            js/
              utils/
                dom.js
                forms.js
              components/
                modals.js
                alerts.js
              htmx/
                events.js
              app.js
            img/
              # Logos, Icons, Illustrationen
          context/
            base_context.py
            items_context.py
          services/
            navigation.py
            flash_messages.py
          routes/
            __init__.py
            ui_routes.py


### 2.3 Design-System & CSS

Design-Tokens (in static/css/_tokens.css):

    :root {
      /* Colors - Primary */
      --color-primary-500: #0ea5e9;

      /* Spacing (4px-Grid) */
      --spacing-1: 0.25rem;  /* 4px */
      --spacing-2: 0.5rem;   /* 8px */
      --spacing-3: 0.75rem;  /* 12px */
      --spacing-4: 1rem;     /* 16px */

      /* Typography */
      --font-size-base: 1rem;
      --font-size-sm: 0.875rem;
      --font-size-lg: 1.125rem;
      --font-weight-normal: 400;
      --font-weight-semibold: 600;
      --line-height-normal: 1.5;

      /* Border-Radius */
      --radius-sm: 0.125rem;
      --radius-md: 0.25rem;
      --radius-lg: 0.5rem;

      /* Shadows */
      --shadow-sm: 0 1px 2px rgb(0 0 0 / 0.05);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }

CSS-Struktur:

- _tokens.css: Tokens
- _reset.css: Reset/Normalize
- _typography.css: Grundtypografie
- _layout.css: Layout / Grids / Container
- _utilities.css: Hilfsklassen (Spacing, Flex, Text)
- components/_*.css: komponentenspezifische Styles
- app.css: zentraler Entry-Point

Beispiel Button-Styles (static/css/components/_buttons.css):

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: var(--spacing-2) var(--spacing-4);
      font-size: var(--font-size-base);
      font-weight: var(--font-weight-semibold);
      border-radius: var(--radius-md);
      border: none;
      cursor: pointer;
      box-shadow: var(--shadow-sm);
      transition: transform 150ms ease, box-shadow 150ms ease, background-color 150ms ease;
    }

    .btn-primary {
      background-color: var(--color-primary-500);
      color: white;
    }

    .btn-primary:hover {
      box-shadow: var(--shadow-md);
      transform: translateY(-1px);
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      box-shadow: none;
      transform: none;
    }


### 2.4 Komponenten (Jinja-Macros)

Buttons-Komponente (ui/templates/components/buttons.j2):

    {% macro button(
      text,
      variant="primary",
      size="md",
      type="button",
      disabled=False,
      aria_label=None
    ) %}
      <button
        type="{{ type }}"
        class="btn btn-{{ variant }} btn-{{ size }}"
        {% if disabled %}disabled{% endif %}
        {% if aria_label %}aria-label="{{ aria_label }}"{% endif %}
      >
        {{ text }}
      </button>
    {% endmacro %}

Verwendung (ui/templates/pages/home.j2):

    {% import "components/buttons.j2" as buttons %}

    <section class="hero">
      <h1>Example App</h1>
      {{ buttons.button("Aktion ausführen", variant="primary", type="submit") }}
    </section>


### 2.5 HTMX-Patterns

Fragment-Loading-Pattern (ui/templates/partials/status_block.j2):

    <section id="status-block"
             hx-get="/ui/status/fragment"
             hx-trigger="load, every 30s"
             hx-swap="outerHTML">
      <p>Lädt Status...</p>
    </section>

Form-Submit-Pattern:

    <form
      hx-post="/ui/items/create"
      hx-target="#items-list"
      hx-swap="innerHTML"
    >
      <!-- Form-Felder -->
      <button class="btn btn-primary" type="submit">
        Speichern
      </button>
    </form>


### 2.6 Accessibility-Ansatz

Modal-Beispiel mit ARIA:

    <div class="modal"
         role="dialog"
         aria-modal="true"
         aria-labelledby="modal-title"
         aria-describedby="modal-description">
      <div class="modal-content">
        <h2 id="modal-title">Bestätigung</h2>
        <p id="modal-description">Bist du sicher, dass du fortfahren möchtest?</p>
        <button class="btn btn-secondary" type="button" aria-label="Modal schließen">
          ×
        </button>
      </div>
    </div>

Anforderungen:

- Fokus beim Öffnen ins Modal setzen.
- Fokus beim Schließen zurück zum auslösenden Element.
- Escape schließt Modal.
- Tab-Reihenfolge vollständig und logisch.


### 2.7 Erweiterbarkeit (UI)

2.7.1 Neue Seiten

- Ort: ui/templates/pages/<feature>.j2
- Layout: nutzt ein Layout aus ui/templates/layouts/.
- Kontext: ui/context/<feature>_context.py
- Routing: zusätzlicher Pfad in ui/routes/ui_routes.py.

2.7.2 Neue UI-Komponenten

- Ort: ui/templates/components/<component_name>.j2
- Regeln:
  - Macro pro Komponente oder eng verwandte Varianten.
  - Parameter für Text, Variante, Größe, A11y.
- Styling:
  - static/css/components/_<component_name>.css
  - Nutzung der Design-Tokens.

2.7.3 Neue Partials / HTMX-Fragmente

- Ort: ui/templates/partials/<feature>_<fragment>.j2
- Routing: dedizierte Endpoints wie /ui/<feature>/fragment.
- Inhalt: nur der benötigte Ausschnitt (kein komplettes Layout).

2.7.4 Erweiterung des Design-Systems

- Neue Tokens in _tokens.css ergänzen.
- Eindeutige, semantische Namen (z. B. --color-accent-500).
- Änderungen an bestehenden Tokens als potenziell „breaking“ betrachten und versionieren.

2.7.5 UI-Anti-Patterns

- Inline-Styles statt zentralem CSS.
- Harte Farb-/Spacingwerte ohne Tokens.
- Komponenten, die Business-Logik, Layout und Fetching mischen.
- Einsatz schwerer Frontend-Frameworks zusätzlich zu Server-Rendering/HTMX ohne klaren Nutzen.
