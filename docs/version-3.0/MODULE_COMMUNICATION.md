# Module Communication Patterns (Version 3.0)

**Version:** 3.0.0  
**Status:** Planning Phase  
**Last Updated:** 2025-11-21

---

## 1. Overview

This document defines the communication patterns and contracts for inter-module communication in SoulSpot Bridge Version 3.0. These patterns ensure **loose coupling** while enabling modules to collaborate effectively.

### 1.1 Design Principles

**Key Principles:**
- **Loose Coupling**: Modules don't import each other's implementation
- **Explicit Contracts**: All communication happens through well-defined interfaces
- **Event-Driven**: Prefer async events over sync calls for cross-module actions
- **Typed Communication**: All messages are strongly typed
- **Error Handling**: Failures in one module don't cascade
- **Versioning**: Support for contract evolution

### 1.2 Communication Types

| Type | Use Case | Coupling | Performance | Example |
|------|----------|----------|-------------|---------|
| **Events** | Notifications, side effects | Loose | Async | Download completed → Metadata enrichment |
| **Direct Calls** | Query data, immediate response | Medium | Sync | Dashboard requests download stats |
| **Message Queue** | Long-running tasks | Loose | Async | Process entire playlist |
| **Shared Database** | Data persistence | Tight | Sync | Track references between modules |

---

## 2. Event Bus Architecture

### 2.1 Event Bus Design

The Event Bus is the primary mechanism for inter-module communication.

**Components:**
```
┌─────────────────────────────────────────────────────┐
│                   EVENT BUS                         │
│  ┌──────────────────────────────────────────────┐  │
│  │  Event Router                                │  │
│  │  - Receives events from publishers           │  │
│  │  - Routes to registered subscribers          │  │
│  │  - Handles delivery guarantees               │  │
│  └──────────────────────────────────────────────┘  │
│                         ↓↓↓                         │
│  ┌──────────────────────────────────────────────┐  │
│  │  Event Store (Optional)                      │  │
│  │  - Persists events for replay                │  │
│  │  - Enables event sourcing                    │  │
│  │  - Audit trail                               │  │
│  └──────────────────────────────────────────────┘  │
│                         ↓↓↓                         │
│  ┌──────────────────────────────────────────────┐  │
│  │  Schema Registry                             │  │
│  │  - Validates event schemas                   │  │
│  │  - Manages schema versions                   │  │
│  │  - Type safety                               │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 2.2 Event Bus Implementation

```python
# core/events/event_bus.py

from typing import Callable, Dict, List, Any, Awaitable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """
    Base event class.
    
    Hey future me, all events MUST extend this base class. This gives us
    standard fields for tracing, ordering, and debugging. The event_type
    is the routing key - make it clear and descriptive!
    """
    
    event_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return f"Event({self.event_type}, id={self.event_id})"

class EventBus:
    """
    Central event bus for module communication.
    
    Hey future me, this is the heart of module communication. Publishers call
    publish() and don't wait for response. Subscribers register handlers that
    run async. If a handler fails, we log it but don't break other handlers.
    This prevents cascading failures!
    
    IMPORTANT: Handlers run in PARALLEL, not sequentially! If order matters,
    use a queue or add sequence numbers to events.
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._event_store: List[Event] = []  # In-memory for now
        self._schema_registry: Dict[str, Any] = {}
    
    def subscribe(
        self,
        event_type: str,
        handler: Callable[[Event], Awaitable[None]],
    ) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Event type to subscribe to (e.g., "download.completed")
            handler: Async function to call when event occurs
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler to {event_type}")
    
    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event_type: Type of event
            data: Event data payload
            metadata: Optional metadata (source module, user, etc.)
        """
        # Create event
        event = Event(
            event_type=event_type,
            data=data,
            metadata=metadata or {},
        )
        
        # Store event (optional)
        self._event_store.append(event)
        
        # Get handlers
        handlers = self._handlers.get(event_type, [])
        
        if not handlers:
            logger.debug(f"No subscribers for {event_type}")
            return
        
        # Execute handlers in parallel
        logger.info(
            f"Publishing {event_type} to {len(handlers)} handlers"
        )
        
        tasks = []
        for handler in handlers:
            task = asyncio.create_task(
                self._execute_handler(handler, event)
            )
            tasks.append(task)
        
        # Wait for all handlers to complete
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_handler(
        self,
        handler: Callable,
        event: Event,
    ) -> None:
        """
        Execute a single event handler with error handling.
        
        Args:
            handler: Handler function
            event: Event to process
        """
        try:
            await handler(event)
        except Exception as e:
            logger.error(
                f"Handler {handler.__name__} failed for {event.event_type}: {e}",
                exc_info=True
            )
            # Don't re-raise - isolate failures
    
    def register_schema(
        self,
        event_type: str,
        schema: Dict[str, Any],
    ) -> None:
        """
        Register event schema for validation.
        
        Args:
            event_type: Event type
            schema: JSON schema for validation
        """
        self._schema_registry[event_type] = schema
        logger.info(f"Registered schema for {event_type}")
    
    def validate_event(self, event: Event) -> bool:
        """
        Validate event against registered schema.
        
        Args:
            event: Event to validate
            
        Returns:
            True if valid, False otherwise
        """
        schema = self._schema_registry.get(event.event_type)
        if not schema:
            logger.warning(f"No schema for {event.event_type}")
            return True  # Pass if no schema
        
        # TODO: Implement JSON schema validation
        return True
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Event]:
        """
        Get recent events from store.
        
        Args:
            event_type: Optional filter by type
            limit: Maximum events to return
            
        Returns:
            List of events
        """
        events = self._event_store
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Return most recent first
        return sorted(
            events,
            key=lambda e: e.timestamp,
            reverse=True
        )[:limit]

# Global event bus instance
event_bus = EventBus()
```

### 2.3 Event Patterns

**1. Fire-and-Forget Pattern:**
```python
# Publisher doesn't wait for processing
await event_bus.publish(
    "download.completed",
    {
        "download_id": "dl-123",
        "file_path": "/music/track.mp3",
    }
)
# Continue immediately
```

**2. Fan-Out Pattern:**
```python
# One event, multiple handlers
@event_bus.subscribe("download.completed")
async def enrich_metadata(event: Event):
    await metadata_service.enrich(event.data["file_path"])

@event_bus.subscribe("download.completed")
async def import_to_library(event: Event):
    await library_service.import_file(event.data["file_path"])

@event_bus.subscribe("download.completed")
async def notify_user(event: Event):
    await notification_service.send(f"Downloaded {event.data['file_path']}")
```

**3. Event Chain Pattern:**
```python
# Events trigger other events
@event_bus.subscribe("download.completed")
async def on_download_completed(event: Event):
    # Enrich metadata
    metadata = await metadata_service.enrich(event.data["file_path"])
    
    # Publish next event
    await event_bus.publish(
        "metadata.enriched",
        {
            "file_path": event.data["file_path"],
            "metadata": metadata,
        }
    )

@event_bus.subscribe("metadata.enriched")
async def on_metadata_enriched(event: Event):
    # Import to library
    await library_service.import_file(
        event.data["file_path"],
        metadata=event.data["metadata"]
    )
    
    # Publish completion
    await event_bus.publish(
        "track.ready",
        {"file_path": event.data["file_path"]}
    )
```

---

## 3. Direct Module Calls

### 3.1 Module Registry

```python
# core/registry/module_registry.py

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ModuleRegistry:
    """
    Registry for module discovery and direct calls.
    
    Hey future me, this is for when you NEED a direct call instead of events.
    Use sparingly! Events are better for most cases. This is for queries where
    you need immediate response (e.g., "get current download count").
    """
    
    def __init__(self):
        self._modules: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}
    
    def register_module(self, name: str, module: Any) -> None:
        """
        Register a module.
        
        Args:
            name: Module name (e.g., "soulseek")
            module: Module instance
        """
        self._modules[name] = module
        logger.info(f"Registered module: {name}")
    
    def register_service(
        self,
        module_name: str,
        service_name: str,
        service: Any,
    ) -> None:
        """
        Register a service from a module.
        
        Args:
            module_name: Module name
            service_name: Service name
            service: Service instance
        """
        key = f"{module_name}.{service_name}"
        self._services[key] = service
        logger.info(f"Registered service: {key}")
    
    def get_module(self, name: str) -> Optional[Any]:
        """
        Get module by name.
        
        Args:
            name: Module name
            
        Returns:
            Module instance or None
        """
        return self._modules.get(name)
    
    def get_service(
        self,
        module_name: str,
        service_name: str,
    ) -> Optional[Any]:
        """
        Get service from module.
        
        Args:
            module_name: Module name
            service_name: Service name
            
        Returns:
            Service instance or None
        """
        key = f"{module_name}.{service_name}"
        return self._services.get(key)
    
    async def query(
        self,
        module: str,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Query a module operation.
        
        Args:
            module: Module name
            operation: Operation name
            params: Optional parameters
            
        Returns:
            Operation result
        """
        mod = self.get_module(module)
        if not mod:
            raise ValueError(f"Module {module} not found")
        
        # Get operation handler
        handler = getattr(mod, operation, None)
        if not handler:
            raise ValueError(
                f"Operation {operation} not found on {module}"
            )
        
        # Execute
        if params:
            return await handler(**params)
        else:
            return await handler()
    
    def list_modules(self) -> List[str]:
        """List all registered modules."""
        return list(self._modules.keys())
    
    def list_services(self) -> List[str]:
        """List all registered services."""
        return list(self._services.keys())

# Global registry
module_registry = ModuleRegistry()
```

### 3.2 Direct Call Pattern

```python
# Use module registry for queries
from core.registry import module_registry

# Example: Dashboard needs download statistics
class DashboardService:
    async def get_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        
        # Direct call to soulseek module
        downloads_service = module_registry.get_service(
            "soulseek", "downloads"
        )
        
        download_stats = await downloads_service.get_statistics()
        
        # Direct call to library module
        library_service = module_registry.get_service(
            "library", "library"
        )
        
        library_stats = await library_service.get_statistics()
        
        return {
            "downloads": download_stats,
            "library": library_stats,
        }
```

---

## 4. Module Router / Orchestrator

### 4.1 Overview

The Module Router acts as an **intelligent orchestrator** that coordinates communication between modules, handles module availability detection, and ensures graceful degradation when modules are missing.

**Key Responsibilities:**
- **Capability Discovery**: Identify which modules can handle specific operations
- **Request Routing**: Route requests to appropriate modules based on capabilities
- **Availability Monitoring**: Track which modules are active and healthy
- **Graceful Degradation**: Handle missing modules without crashing
- **Standalone Operation**: Allow modules to run independently

### 4.2 Module Router Design

```
┌─────────────────────────────────────────────────────────┐
│                   MODULE ROUTER                         │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Capability Registry                             │  │
│  │  - Tracks module capabilities                    │  │
│  │  - Maps operations to modules                    │  │
│  │  │  e.g., "download.track" → ["soulseek"]       │  │
│  │  │       "search.track" → ["spotify", "local"]  │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓↓↓                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Module Health Monitor                           │  │
│  │  - Periodic health checks                        │  │
│  │  - Module availability status                    │  │
│  │  - Automatic module discovery                    │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓↓↓                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Request Router                                  │  │
│  │  - Routes requests to capable modules            │  │
│  │  - Handles fallbacks for missing modules         │  │
│  │  - Logs warnings when modules unavailable        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 4.3 Module Router Implementation

```python
# core/router/module_router.py

from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class ModuleStatus(str, Enum):
    """Module availability status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

@dataclass
class ModuleCapability:
    """
    Module capability definition.
    
    Hey future me, capabilities define WHAT a module can do, not HOW.
    For example, "download.track" is a capability. Multiple modules might
    provide it (soulseek, youtube-dl, etc). The router picks the best one!
    """
    
    operation: str  # e.g., "download.track", "search.artist"
    module_name: str
    priority: int = 0  # Higher = preferred
    required_modules: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.operation} → {self.module_name} (priority: {self.priority})"

class ModuleRouter:
    """
    Intelligent module orchestrator for routing requests.
    
    Hey future me, this is THE central coordination point. When a user action
    requires multiple modules (search in Spotify, download via Soulseek, enrich
    with Metadata), this router coordinates the flow. If a module is missing,
    we log it clearly and either use a fallback or fail gracefully.
    
    IMPORTANT: This enables standalone module operation! A module can work alone
    even if other modules aren't available.
    """
    
    def __init__(self):
        self._capabilities: Dict[str, List[ModuleCapability]] = {}
        self._module_status: Dict[str, ModuleStatus] = {}
        self._health_checkers: Dict[str, Callable] = {}
        self._missing_module_warnings: Set[str] = set()
    
    def register_capability(
        self,
        operation: str,
        module_name: str,
        priority: int = 0,
        required_modules: Optional[List[str]] = None,
    ) -> None:
        """
        Register a module capability.
        
        Args:
            operation: Operation identifier (e.g., "download.track")
            module_name: Module providing this capability
            priority: Priority (higher = preferred)
            required_modules: Other modules this capability depends on
        """
        capability = ModuleCapability(
            operation=operation,
            module_name=module_name,
            priority=priority,
            required_modules=required_modules or [],
        )
        
        if operation not in self._capabilities:
            self._capabilities[operation] = []
        
        self._capabilities[operation].append(capability)
        
        # Sort by priority (descending)
        self._capabilities[operation].sort(
            key=lambda c: c.priority,
            reverse=True
        )
        
        logger.info(f"Registered capability: {capability}")
    
    def register_health_checker(
        self,
        module_name: str,
        health_checker: Callable,
    ) -> None:
        """
        Register module health check function.
        
        Args:
            module_name: Module name
            health_checker: Async function that returns True if healthy
        """
        self._health_checkers[module_name] = health_checker
        logger.info(f"Registered health checker for {module_name}")
    
    async def check_module_health(self, module_name: str) -> ModuleStatus:
        """
        Check if a module is healthy.
        
        Args:
            module_name: Module to check
            
        Returns:
            Module status
        """
        checker = self._health_checkers.get(module_name)
        if not checker:
            return ModuleStatus.UNKNOWN
        
        try:
            is_healthy = await checker()
            return ModuleStatus.ACTIVE if is_healthy else ModuleStatus.INACTIVE
        except Exception as e:
            logger.error(f"Health check failed for {module_name}: {e}")
            return ModuleStatus.DEGRADED
    
    async def update_module_status(self, module_name: str) -> None:
        """Update cached module status."""
        status = await self.check_module_health(module_name)
        self._module_status[module_name] = status
        
        if status != ModuleStatus.ACTIVE:
            logger.warning(
                f"Module {module_name} status: {status.value}"
            )
    
    async def monitor_all_modules(self) -> None:
        """
        Periodic health monitoring for all registered modules.
        
        Hey future me, run this in a background task! It updates status
        for all modules every minute or so. This lets the router know
        what's available without checking on every request.
        """
        tasks = []
        for module_name in self._health_checkers:
            task = self.update_module_status(module_name)
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_capable_modules(
        self,
        operation: str,
        only_active: bool = True,
    ) -> List[ModuleCapability]:
        """
        Get modules capable of handling an operation.
        
        Args:
            operation: Operation to find modules for
            only_active: Only return active modules
            
        Returns:
            List of capable modules (sorted by priority)
        """
        capabilities = self._capabilities.get(operation, [])
        
        if only_active:
            # Filter by module status
            capabilities = [
                cap for cap in capabilities
                if self._module_status.get(cap.module_name) == ModuleStatus.ACTIVE
            ]
        
        return capabilities
    
    async def route_request(
        self,
        operation: str,
        params: Dict[str, Any],
        fallback_allowed: bool = True,
    ) -> Any:
        """
        Route request to appropriate module.
        
        Args:
            operation: Operation to perform
            params: Operation parameters
            fallback_allowed: Allow fallback to lower priority modules
            
        Returns:
            Operation result
            
        Raises:
            ModuleNotAvailableError: No module can handle the operation
        """
        capabilities = self.get_capable_modules(operation, only_active=True)
        
        if not capabilities:
            # No active modules for this operation
            await self._handle_missing_capability(operation)
            raise ModuleNotAvailableError(
                f"No module available for operation: {operation}"
            )
        
        # Try modules in priority order
        for capability in capabilities:
            module_name = capability.module_name
            
            # Check if required modules are available
            if not await self._check_dependencies(capability):
                logger.warning(
                    f"{module_name} cannot perform {operation} - "
                    f"missing dependencies: {capability.required_modules}"
                )
                continue
            
            try:
                # Get module and execute operation
                result = await self._execute_on_module(
                    module_name,
                    operation,
                    params
                )
                
                logger.info(
                    f"✓ Routed {operation} to {module_name}"
                )
                return result
                
            except Exception as e:
                logger.error(
                    f"✗ {module_name} failed to handle {operation}: {e}"
                )
                
                if not fallback_allowed:
                    raise
                
                # Try next module (fallback)
                continue
        
        # All capable modules failed
        raise ModuleOperationError(
            f"All modules failed to handle operation: {operation}"
        )
    
    async def _check_dependencies(
        self, capability: ModuleCapability
    ) -> bool:
        """Check if all required modules are available."""
        for required_module in capability.required_modules:
            status = self._module_status.get(required_module)
            if status != ModuleStatus.ACTIVE:
                return False
        return True
    
    async def _execute_on_module(
        self,
        module_name: str,
        operation: str,
        params: Dict[str, Any],
    ) -> Any:
        """
        Execute operation on specific module.
        
        Hey future me, this uses the module registry to get the actual
        module and call the operation. The module must expose the operation
        as a method or through its API interface.
        """
        from core.registry import module_registry
        
        module = module_registry.get_module(module_name)
        if not module:
            raise ModuleNotFoundError(f"Module {module_name} not found")
        
        # Call operation on module
        # Modules should expose operations as methods
        handler = getattr(module, operation.replace(".", "_"), None)
        if not handler:
            raise OperationNotSupportedError(
                f"{module_name} doesn't support {operation}"
            )
        
        return await handler(**params)
    
    async def _handle_missing_capability(self, operation: str) -> None:
        """
        Handle missing capability with clear logging.
        
        Hey future me, this is where we warn the user! If a module is missing,
        we log it CLEARLY so it shows up in logs, Docker logs, and can be
        displayed in the UI. Only warn once per operation to avoid spam.
        """
        if operation in self._missing_module_warnings:
            return  # Already warned
        
        self._missing_module_warnings.add(operation)
        
        # Get all modules that could provide this capability
        all_capabilities = self._capabilities.get(operation, [])
        
        if all_capabilities:
            inactive_modules = [
                cap.module_name for cap in all_capabilities
                if self._module_status.get(cap.module_name) != ModuleStatus.ACTIVE
            ]
            
            logger.warning(
                f"⚠️  MISSING MODULE WARNING ⚠️\n"
                f"Operation '{operation}' requires one of these modules:\n"
                f"  {', '.join([cap.module_name for cap in all_capabilities])}\n"
                f"Inactive modules: {', '.join(inactive_modules)}\n"
                f"Please enable required modules to use this feature."
            )
        else:
            logger.warning(
                f"⚠️  MISSING CAPABILITY WARNING ⚠️\n"
                f"Operation '{operation}' is not supported by any module.\n"
                f"This feature may not be available."
            )
    
    def get_module_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of all module statuses.
        
        Returns:
            Dictionary with module status information
        """
        return {
            "modules": {
                module: status.value
                for module, status in self._module_status.items()
            },
            "capabilities": {
                operation: [cap.module_name for cap in caps]
                for operation, caps in self._capabilities.items()
            },
            "active_modules": [
                module for module, status in self._module_status.items()
                if status == ModuleStatus.ACTIVE
            ],
            "inactive_modules": [
                module for module, status in self._module_status.items()
                if status != ModuleStatus.ACTIVE
            ],
        }

# Exceptions
class ModuleNotAvailableError(Exception):
    """Raised when no module is available for an operation."""
    pass

class ModuleNotFoundError(Exception):
    """Raised when a specific module is not found."""
    pass

class ModuleOperationError(Exception):
    """Raised when all modules fail to handle an operation."""
    pass

class OperationNotSupportedError(Exception):
    """Raised when a module doesn't support an operation."""
    pass

# Global router instance
module_router = ModuleRouter()
```

### 4.4 Usage Example: Search and Download Flow

```python
# Example: User searches for a song via Spotify, downloads via Soulseek

# 1. Register capabilities during module startup
# In Spotify module initialization:
module_router.register_capability(
    operation="search.track",
    module_name="spotify",
    priority=10,  # High priority for Spotify search
)

# In Soulseek module initialization:
module_router.register_capability(
    operation="download.track",
    module_name="soulseek",
    priority=10,
    required_modules=["spotify"],  # Needs Spotify for track info
)

# 2. Use the router to coordinate the flow
async def search_and_download_track(query: str):
    """
    Search for track and initiate download.
    
    Hey future me, this shows how the router coordinates modules.
    If Spotify is missing, search fails. If Soulseek is missing,
    download fails with a clear warning. Both failures are graceful!
    """
    
    try:
        # Step 1: Search via router
        search_results = await module_router.route_request(
            operation="search.track",
            params={"query": query, "limit": 10}
        )
        
        logger.info(f"✓ Found {len(search_results)} tracks")
        
        # Step 2: User selects a track (first result for example)
        selected_track = search_results[0]
        
        # Step 3: Download via router
        download = await module_router.route_request(
            operation="download.track",
            params={
                "track_id": selected_track["id"],
                "track_info": selected_track,
            }
        )
        
        logger.info(f"✓ Download initiated: {download['id']}")
        return download
        
    except ModuleNotAvailableError as e:
        logger.error(f"✗ Cannot complete operation: {e}")
        # This error message will show in logs and can be displayed in UI
        raise
```

### 4.5 Module Health Checks

Each module must provide a health check function:

```python
# modules/soulseek/backend/__init__.py

async def health_check() -> bool:
    """
    Soulseek module health check.
    
    Returns:
        True if module is healthy and operational
    """
    try:
        # Check slskd connection
        from .infrastructure.integrations.slskd_client import slskd_client
        await slskd_client.ping()
        return True
    except Exception as e:
        logger.error(f"Soulseek health check failed: {e}")
        return False

# Register with router during module initialization
from core.router import module_router

module_router.register_health_checker("soulseek", health_check)
```

### 4.6 UI Integration - Missing Module Warnings

The UI should display module status and warnings:

```html
<!-- modules/dashboard/frontend/widgets/module_status.html -->
<div class="module-status-widget">
    <h3>System Modules</h3>
    
    <div hx-get="/api/modules/status"
         hx-trigger="load, every 30s"
         hx-swap="innerHTML">
        Loading module status...
    </div>
</div>

<!-- API returns this for each module -->
<div class="module-item" data-module="{{ module.name }}">
    <div class="module-header">
        <span class="module-name">{{ module.display_name }}</span>
        <span class="status-badge status-{{ module.status }}">
            {{ module.status }}
        </span>
    </div>
    
    {% if module.status != 'active' %}
    <div class="module-warning">
        ⚠️ {{ module.warning_message }}
    </div>
    {% endif %}
    
    {% if module.capabilities %}
    <div class="module-capabilities">
        <small>Provides: {{ module.capabilities|join(', ') }}</small>
    </div>
    {% endif %}
</div>
```

### 4.7 Logging Integration

Clear, structured logging for missing modules:

```python
# Configure structured logging
import logging
from pythonjsonlogger import jsonlogger

# Create logger with structured format
logger = logging.getLogger("soulspot.modules")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(name)s %(levelname)s %(message)s"
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# When module is missing, this creates structured log entry
logger.warning(
    "Module unavailable",
    extra={
        "module": "soulseek",
        "operation": "download.track",
        "status": "inactive",
        "impact": "Download functionality unavailable",
        "action": "Enable Soulseek module to use downloads",
    }
)
```

**Docker logs will show:**
```json
{
  "asctime": "2025-11-21 10:30:00",
  "name": "soulspot.modules",
  "levelname": "WARNING",
  "message": "Module unavailable",
  "module": "soulseek",
  "operation": "download.track",
  "status": "inactive",
  "impact": "Download functionality unavailable",
  "action": "Enable Soulseek module to use downloads"
}
```

### 4.8 Standalone Module Operation

Each module can run independently:

```python
# modules/soulseek/main.py (standalone entrypoint)

"""
Standalone Soulseek module.

Can run independently for development/testing.
Will warn about missing modules but remain functional for core operations.
"""

from fastapi import FastAPI
from .backend.api.routes import router
from .backend.config.settings import settings
from core.router import module_router

app = FastAPI(title="Soulseek Module (Standalone)")

# Register routes
app.include_router(router)

# Register capabilities
module_router.register_capability(
    operation="download.track",
    module_name="soulseek",
    priority=10,
    required_modules=[],  # Can work alone for basic downloads
)

# Start health monitoring
@app.on_event("startup")
async def startup():
    """Start module health monitoring."""
    import asyncio
    
    # Check for optional module dependencies
    await module_router.monitor_all_modules()
    
    # Log module status
    status = module_router.get_module_status_summary()
    logger.info(f"Soulseek module started (standalone mode)")
    logger.info(f"Active modules: {status['active_modules']}")
    
    if status['inactive_modules']:
        logger.warning(
            f"⚠️  Some modules are inactive: {status['inactive_modules']}\n"
            f"Enhanced features may be limited."
        )
    
    # Start periodic health monitoring
    asyncio.create_task(periodic_health_check())

async def periodic_health_check():
    """Periodic health check task."""
    while True:
        await asyncio.sleep(60)  # Every minute
        await module_router.monitor_all_modules()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### 4.9 Benefits of Module Router Approach

**✅ Standalone Capability:**
- Modules can run independently for development/testing
- Core functionality works even without other modules
- Clear warnings when optional features unavailable

**✅ Clear Error Messaging:**
- Structured logs show exactly what's missing
- UI displays module status and warnings
- Docker logs contain actionable information

**✅ Flexible Integration:**
- Multiple modules can provide same capability
- Priority-based routing for preferred modules
- Automatic fallback to alternative modules

**✅ Graceful Degradation:**
- System continues to function with partial module set
- Features degrade gracefully when modules unavailable
- No cascading failures

**✅ Dynamic Discovery:**
- Automatic module discovery via health checks
- Runtime capability registration
- Hot-swappable modules (restart individual modules)

---

## 5. Event Schemas

### 4.1 Schema Definition

```yaml
# modules/soulseek/contracts/events.yaml

events:
  download.started:
    version: "1.0.0"
    description: "Triggered when a download starts"
    producer: "soulseek"
    consumers: ["dashboard", "notifications"]
    
    schema:
      type: object
      required:
        - download_id
        - track_id
        - filename
        - timestamp
      properties:
        download_id:
          type: string
          description: "Unique download identifier"
          example: "dl-123"
        
        track_id:
          type: string
          description: "Track identifier"
          example: "track-456"
        
        filename:
          type: string
          description: "Filename being downloaded"
          example: "Artist - Song.mp3"
        
        timestamp:
          type: string
          format: date-time
          description: "When download started"
    
    examples:
      - download_id: "dl-123"
        track_id: "track-456"
        filename: "The Beatles - Here Comes The Sun.mp3"
        timestamp: "2025-11-21T10:00:00Z"
  
  download.completed:
    version: "1.0.0"
    description: "Triggered when download completes successfully"
    producer: "soulseek"
    consumers: ["metadata", "library", "dashboard", "notifications"]
    
    schema:
      type: object
      required:
        - download_id
        - track_id
        - file_path
        - file_size
        - timestamp
      properties:
        download_id:
          type: string
        
        track_id:
          type: string
        
        file_path:
          type: string
          description: "Path to downloaded file"
          example: "/mnt/downloads/track.mp3"
        
        file_size:
          type: integer
          description: "File size in bytes"
          minimum: 0
        
        duration_seconds:
          type: number
          description: "Download duration"
        
        timestamp:
          type: string
          format: date-time
```

### 4.2 Schema Versioning

**Version Format:** `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (remove field, change type)
- **MINOR**: Backwards-compatible additions (new field)
- **PATCH**: Documentation or validation changes

**Example Evolution:**
```yaml
# Version 1.0.0
download.completed:
  schema:
    download_id: string
    file_path: string

# Version 1.1.0 (added field, backwards compatible)
download.completed:
  schema:
    download_id: string
    file_path: string
    file_size: integer  # NEW

# Version 2.0.0 (changed field type, breaking)
download.completed:
  schema:
    download_id: string
    file_path: string
    file_size: integer
    download_time: integer  # CHANGED from duration_seconds (string)
```

---

## 6. Cross-Module Data Contracts

### 5.1 Shared Data Types

```python
# core/contracts/types.py

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class TrackReference:
    """
    Shared reference to a track across modules.
    
    Hey future me, this is the COMMON format for track references.
    All modules use this when passing track info between each other.
    Keep it minimal - just the IDs and basic metadata. Each module
    has its own detailed entity.
    """
    
    # Identity
    track_id: str                    # Our internal ID
    spotify_id: Optional[str] = None  # Spotify ID
    musicbrainz_id: Optional[str] = None  # MusicBrainz ID
    
    # Basic metadata
    title: str
    artist: str
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime

@dataclass
class FileReference:
    """Shared reference to a file."""
    
    file_id: str
    path: str
    size_bytes: int
    format: str  # mp3, flac, etc.
    checksum: Optional[str] = None
```

### 5.2 Data Transformation

```python
# Each module transforms to/from shared format

# In Soulseek module
class Download:
    def to_track_reference(self) -> TrackReference:
        """Convert download to track reference."""
        return TrackReference(
            track_id=self.track_id,
            title=self.track_title,
            artist=self.track_artist,
            created_at=self.queued_at,
            updated_at=self.updated_at,
        )

# In Metadata module
class Track:
    @classmethod
    def from_track_reference(
        cls, ref: TrackReference
    ) -> "Track":
        """Create track from reference."""
        return cls(
            id=ref.track_id,
            spotify_id=ref.spotify_id,
            title=ref.title,
            artist=ref.artist,
            album=ref.album,
        )
```

---

## 7. Error Handling

### 6.1 Error Propagation

**Events:**
```python
# Events don't propagate errors - they're fire-and-forget
await event_bus.publish("download.completed", data)
# Even if handlers fail, this returns immediately

# For critical errors, publish error event
await event_bus.publish(
    "download.failed",
    {
        "download_id": "dl-123",
        "error": str(error),
        "can_retry": True,
    }
)
```

**Direct Calls:**
```python
# Direct calls propagate errors normally
try:
    stats = await module_registry.query(
        "soulseek",
        "get_statistics"
    )
except ModuleNotFoundError:
    # Handle missing module
    stats = {"error": "Soulseek module unavailable"}
except Exception as e:
    # Handle other errors
    logger.error(f"Failed to get stats: {e}")
    stats = {"error": str(e)}
```

### 6.2 Retry Strategies

```python
# core/patterns/retry.py

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> Any:
    """
    Retry function with exponential backoff.
    
    Hey future me, use this for transient failures (network errors, timeouts).
    NOT for logical errors (validation failures). The backoff prevents
    hammering a struggling service. Delay doubles each time: 1s, 2s, 4s, etc.
    """
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise  # Last attempt, give up
            
            delay = base_delay * (2 ** attempt)
            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. "
                f"Retrying in {delay}s..."
            )
            await asyncio.sleep(delay)
```

---

## 8. Testing Module Communication

### 7.1 Test Event Bus

```python
# tests/helpers/test_event_bus.py

class TestEventBus:
    """Test event bus for unit tests."""
    
    def __init__(self):
        self._published_events: List[Event] = []
        self._handlers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to events."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish event (stores for inspection)."""
        event = Event(
            event_type=event_type,
            data=data,
            metadata=metadata or {},
        )
        self._published_events.append(event)
    
    def get_published_events(
        self, event_type: Optional[str] = None
    ) -> List[Event]:
        """Get published events for assertions."""
        if event_type:
            return [
                e for e in self._published_events
                if e.event_type == event_type
            ]
        return self._published_events
    
    def clear(self) -> None:
        """Clear all events."""
        self._published_events.clear()

# Use in tests
async def test_download_completion_publishes_event():
    # Arrange
    test_bus = TestEventBus()
    service = DownloadService(repo, slskd, test_bus)
    
    # Act
    await service.complete_download("dl-123", Path("/music/track.mp3"))
    
    # Assert
    events = test_bus.get_published_events("download.completed")
    assert len(events) == 1
    assert events[0].data["download_id"] == "dl-123"
```

### 7.2 Testing Cross-Module Integration

```python
# tests/integration/test_download_to_library_flow.py

@pytest.mark.integration
async def test_download_triggers_library_import(
    soulseek_module,
    library_module,
    event_bus,
):
    """Test that completed download triggers library import."""
    
    # Set up library module to listen for events
    imports_received = []
    
    @event_bus.subscribe("download.completed")
    async def on_download_completed(event: Event):
        file_path = event.data["file_path"]
        await library_module.import_file(file_path)
        imports_received.append(file_path)
    
    # Complete a download
    await soulseek_module.complete_download(
        "dl-123",
        Path("/music/test.mp3")
    )
    
    # Give event time to propagate
    await asyncio.sleep(0.1)
    
    # Verify library received import
    assert len(imports_received) == 1
    assert imports_received[0] == Path("/music/test.mp3")
```

---

## 9. Best Practices

### 8.1 DO

✅ **Use events for notifications and side effects**
```python
# Good: Loosely coupled
await event_bus.publish("download.completed", {...})

# Handler in metadata module
@event_bus.subscribe("download.completed")
async def enrich_metadata(event):
    await metadata_service.enrich(event.data["file_path"])
```

✅ **Use direct calls for queries**
```python
# Good: Immediate response needed
stats = await module_registry.query("soulseek", "get_statistics")
```

✅ **Version your event schemas**
```yaml
# Good: Explicit versioning
download.completed:
  version: "1.1.0"
  schema: ...
```

✅ **Handle errors gracefully**
```python
# Good: Isolate failures
try:
    await event_handler(event)
except Exception as e:
    logger.error(f"Handler failed: {e}")
    # Don't re-raise - protect other handlers
```

### 8.2 DON'T

❌ **Don't import from other modules' internals**
```python
# Bad: Tight coupling
from modules.metadata.backend.services import MetadataService

# Good: Use registry
metadata_service = module_registry.get_service("metadata", "metadata")
```

❌ **Don't use events for queries**
```python
# Bad: Events are async, can't wait for response
await event_bus.publish("get.statistics", {...})
result = ???  # Can't get result

# Good: Use direct call
result = await module_registry.query("soulseek", "get_statistics")
```

❌ **Don't break event contracts**
```python
# Bad: Remove required field (breaking change)
# Version 1.0.0
{"download_id": "...", "file_path": "..."}

# Version 1.1.0
{"download_id": "..."}  # BREAKING!

# Good: Add optional field
# Version 1.1.0
{"download_id": "...", "file_path": "...", "file_size": 123}
```

❌ **Don't create circular dependencies**
```python
# Bad: A depends on B, B depends on A
# Module A
@event_bus.subscribe("b.event")
async def on_b_event():
    await event_bus.publish("a.event", ...)

# Module B
@event_bus.subscribe("a.event")
async def on_a_event():
    await event_bus.publish("b.event", ...)  # Infinite loop!
```

---

## 10. Performance Considerations

### 9.1 Event Bus Optimization

**Batching:**
```python
# Instead of many small events
for item in items:
    await event_bus.publish("item.processed", {"id": item.id})

# Batch into single event
await event_bus.publish(
    "items.processed",
    {"ids": [item.id for item in items]}
)
```

**Async Processing:**
```python
# Events are already async, but for heavy processing:
@event_bus.subscribe("download.completed")
async def heavy_processing(event: Event):
    # Offload to background worker
    await job_queue.enqueue(
        "process_download",
        download_id=event.data["download_id"]
    )
```

### 9.2 Caching

```python
# Cache frequently accessed cross-module data
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_track_metadata(track_id: str) -> Dict:
    """Get cached track metadata."""
    return module_registry.query(
        "metadata",
        "get_track",
        {"track_id": track_id}
    )
```

---

## 11. Monitoring and Observability

### 10.1 Event Metrics

```python
# Track event metrics
class EventMetrics:
    def __init__(self):
        self.events_published = Counter()
        self.events_processed = Counter()
        self.event_latency = Histogram()
    
    async def publish(self, event_type: str, data: dict):
        """Publish with metrics."""
        start = time.time()
        
        await event_bus.publish(event_type, data)
        
        self.events_published.inc(labels={"type": event_type})
        self.event_latency.observe(
            time.time() - start,
            labels={"type": event_type}
        )
```

### 10.2 Event Tracing

```python
# Add correlation IDs for tracing
await event_bus.publish(
    "download.completed",
    {
        "download_id": "dl-123",
        "file_path": "/music/track.mp3",
    },
    metadata={
        "correlation_id": request_id,
        "source_module": "soulseek",
        "trace_id": trace_id,
    }
)

# Propagate through event chain
@event_bus.subscribe("download.completed")
async def on_download_completed(event: Event):
    correlation_id = event.metadata.get("correlation_id")
    
    # Process and publish next event
    await event_bus.publish(
        "metadata.enriched",
        {...},
        metadata={
            "correlation_id": correlation_id,  # Propagate
            "source_module": "metadata",
        }
    )
```

---

## 12. Migration from Current Architecture

### 11.1 Current State

**Current direct imports:**
```python
# Old way (tightly coupled)
from soulspot.infrastructure.integrations.slskd_client import SlskdClient
from soulspot.application.services.download_service import DownloadService

service = DownloadService(SlskdClient())
```

### 11.2 Migration Steps

**Step 1: Add Event Bus**
```python
# Add event bus to existing code
from core.events import event_bus

class DownloadService:
    async def complete_download(self, download_id):
        # ... existing logic ...
        
        # Add event publishing
        await event_bus.publish(
            "download.completed",
            {"download_id": download_id}
        )
```

**Step 2: Add Event Handlers**
```python
# Other modules subscribe
from core.events import event_bus

@event_bus.subscribe("download.completed")
async def on_download_completed(event):
    await metadata_service.enrich(event.data["file_path"])
```

**Step 3: Remove Direct Coupling**
```python
# Remove direct service calls
# Before:
await metadata_service.enrich(file_path)

# After:
await event_bus.publish(
    "download.completed",
    {"file_path": file_path}
)
```

---

## 13. Summary

Module communication in Version 3.0 follows these principles:

1. **Events First**: Use events for most inter-module communication
2. **Explicit Contracts**: All communication through well-defined interfaces
3. **Loose Coupling**: Modules don't depend on each other's implementation
4. **Type Safety**: Strongly typed messages and schemas
5. **Error Isolation**: Failures don't cascade across modules
6. **Observable**: Full tracing and metrics for debugging

This architecture enables:
- Independent module development
- Easy testing in isolation
- Clear system behavior
- Maintainable codebase
- Scalable architecture

---

**Related Documents:**
- [Roadmap](./ROADMAP.md)
- [Architecture](./ARCHITECTURE.md)
- [Module Specification](./MODULE_SPECIFICATION.md)
- [Soulseek Module](./SOULSEEK_MODULE.md)

**Status:** ✅ Complete - Planning Phase
