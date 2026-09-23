
# Feature: Multi-Tenant Database Resolution and Unified Access Scope

**ID:** 001

**Status:** Draft

**Layer:** Cross-Layer (Domain, Application, Infrastructure)

**Type:** Business Behavior

---

## 1. Objective

Provide a robust multi-tenant architecture utilizing a database-per-tenant strategy for physical data isolation, combined with a unified access scoping mechanism (`UserScope`) that replaces redundant pivot tables and supports multi-company operations, role-based boundaries, and dynamic tenant switching via stateless context resolution.

The architecture must maintain a strict separation between:

* **Identity:** Who the authenticated user is.
* **Role:** What actions the user is allowed to perform.
* **UserScope:** Which organizational context or companies the user is allowed to access.
* **Current Tenant:** Which company the current HTTP request intends to operate on.
* **Tenant Resolution:** Which physical database corresponds to the requested company.
* **Tenant Data:** Operational data belonging exclusively to the resolved company.

The system must guarantee that tenant-specific business operations are executed exclusively against the physical database assigned to the resolved company.

---

## 2. Context

This feature establishes the core access control and tenant resolution model for the system.

It depends on ASP.NET Core Identity for user authentication and role management (`SuperAdmin`, `AdmoHoldingRRHH`, `Fiscal`, `Colaborador`).

It does not depend on specific business domain entities (e.g., employees, time-tracking records, or reports). It defines the boundary between the Central Catalog Context (managing users, holdings, companies, instances, and scopes) and the isolated Tenant Contexts (storing high-volume operational and reporting data).

Already in place: Basic ASP.NET Core Identity setup.

NOT part of this feature: Specific business feature implementations (e.g., payroll processing, shift management) operating inside individual tenant databases.

### Architectural Context

The system uses a **database-per-tenant** strategy.

Each `Company` represents a tenant and is associated with exactly one physical tenant database.

Conceptually:

```text
Company A → Database A
Company B → Database B
Company C → Database C
```

The `CompanyId` is therefore the canonical identifier used to resolve the tenant context.

`CompanyId` is **not** used as a tenant discriminator inside tenant databases. Since each tenant database belongs exclusively to one company, tenant entities do not require a `CompanyId` column for isolation purposes.

The Central Context is responsible for determining:

```text
User
  ↓
Authorization Scope
  ↓
Requested Company
  ↓
Tenant Metadata
  ↓
Database
```

The Tenant Context is responsible exclusively for accessing the operational data of the resolved company.

---

## 3. Business Rules

### BR-001 — Isolated Tenant Database Architecture

Every company must belong to a designated physical database instance and database name.

Operational tenant data must reside entirely within its isolated tenant database.

The relationship must conceptually follow:

```text
Company
   ↓
DbInstance
   ↓
DatabaseName
   ↓
TenantDbContext
```

Tenant-specific entities must not depend on a `CompanyId` discriminator to enforce isolation.

---

### BR-002 — Unified Access Scope Model

A user's access across holdings and companies must be represented via a unified `UserScope` model defined by a `ScopeType` (`Global`, `Holding`, or `Company`).

Specialized join/pivot tables per role or entity type are strictly prohibited.

The same `UserScope` mechanism must be used regardless of whether the user is a `SuperAdmin`, `AdmoHoldingRRHH`, `Fiscal`, `Colaborador`, or a future role.

The mechanism used to resolve the scope may differ according to the scope type, but the resulting authorization model must remain unified.

---

### BR-003 — Scope Resolution and Hierarchy

Access authorization to a requested company (`CompanyId`) must be granted if and only if:

* The user has `ScopeType.Global` and the user's role is authorized to operate globally, OR
* The user has `ScopeType.Holding` where the target company belongs to the specified `HoldingId`, and the user's role permits operation over that holding, OR
* The user has `ScopeType.Company` explicitly matching the target `CompanyId`, and the user's role permits operation over that company.

Attempting to access a company outside the user's resolved scope must result in a domain authorization error.

`UserScope` alone must not implicitly grant unrestricted functional permissions. Functional permissions remain determined by the user's Identity roles and, where applicable, future authorization policies.

---

### BR-004 — Separation Between Role and Scope

Role and scope represent independent authorization dimensions.

**Role determines:**

```text
What the user can do.
```

**UserScope determines:**

```text
Where the user can do it.
```

Therefore, the system must not treat the existence of a `UserScope` as sufficient functional authorization.

Examples:

```text
SuperAdmin
    + Global Scope
    → Global administrative access

AdmoHoldingRRHH
    + Holding Scope
    → Administrative operations over companies in that holding

Fiscal
    + Holding Scope
    → Fiscal operations over companies in that holding

Fiscal
    + Company Scope
    → Fiscal operations over explicitly assigned companies

Colaborador
    + Company Scope
    → Operational operations over explicitly assigned companies
```

The list of valid role/scope combinations must remain extensible as new roles are introduced.

---

### BR-005 — Dynamic Tenant Switching

The active tenant context must be resolved statelessly per HTTP request based on the provided company identifier (`X-Company-Id`).

Tenant context state must never be permanently mutated on the user record in the database during context switches.

The selected company belongs exclusively to the current request context.

The same authenticated user must therefore be able to operate concurrently against different companies from different sessions, browser tabs, or requests without changing persistent user state.

Example:

```text
Request A
X-Company-Id: Company-A
    ↓
Tenant A

Request B
X-Company-Id: Company-B
    ↓
Tenant B
```

---

### BR-006 — Tenant Resolution

Once the requested `CompanyId` has been authorized, the system must resolve the physical tenant database associated with that company.

The resolution process must conceptually follow:

```text
CompanyId
   ↓
Company
   ↓
DbInstance
   ↓
DatabaseName
   ↓
Connection
   ↓
TenantDbContext
```

The Tenant Context must not determine authorization itself.

Authorization must be completed before the Tenant Context is made available for tenant-specific operations.

---

### BR-007 — Tenant Database Isolation Invariant

Tenant-specific database contexts (`TenantDbContext`) must operate without knowledge of `CompanyId` foreign keys on their entities, as physical isolation at the database level guarantees single-tenant scope per database.

A `TenantDbContext` must never be configured against a database belonging to a company different from the company resolved for the current request.

Cross-tenant joins and distributed queries are outside the scope of this feature.

---

### BR-008 — Central Context and Tenant Context Separation

The architecture must maintain two strictly separated persistence contexts:

```text
CentralDbContext
        │
        ├── Identity
        ├── Roles
        ├── UserScope
        ├── Holding
        ├── Company
        └── DbInstance

TenantDbContext
        │
        ├── Operational entities
        ├── High-volume entities
        └── Reporting entities
```

`TenantDbContext` must not depend on `CentralDbContext` to execute ordinary tenant business operations.

The Central Context resolves the tenant before the Tenant Context is used.

---

### BR-009 — Tenant Resolution Cache

Tenant database metadata may be cached in memory or Redis to reduce repeated lookups against the Central Database.

The cache may accelerate resolution of:

```text
CompanyId
    ↓
DbInstance
    ↓
DatabaseName
```

but must not become the authoritative source for authorization.

Authorization decisions must be based on the authoritative Central Context or a cache with explicitly defined consistency guarantees.

Cache invalidation must occur when tenant database infrastructure metadata changes.

---

### BR-010 — Instance Capacity and Provisioning

A new tenant database must only be provisioned on a database instance (`DbInstance`) that is active and has available capacity:

```text
CurrentTenantsCount < MaxTenants
```

Attempting to provision on an exhausted or inactive instance must result in a domain capacity/infrastructure error.

The capacity validation must be concurrency-safe.

Concurrent provisioning operations must not be able to exceed the configured `MaxTenants` limit due to race conditions.

---

### BR-011 — Tenant Provisioning Lifecycle

Creating a company and provisioning its tenant database must be treated as a lifecycle operation with explicit states.

The system must be able to distinguish, at minimum, between:

```text
Company registered
Provisioning
Provisioned
Provisioning failed
```

A company must not be considered fully operational until its tenant database has been successfully created and the required initial schema has been applied.

Partial failures must not result in a company being incorrectly represented as fully provisioned.

---

### BR-012 — Tenant Database Migration Isolation

Tenant database migrations must execute independently for each tenant database.

A migration failure for one tenant must not prevent the migration process from continuing for unrelated tenant databases.

The migration worker must provide controlled concurrency and isolation of errors.

---

## 4. Acceptance Criteria

### AC-001 — Access Granted via Holding Scope

**Given** a user with an `AdmoHoldingRRHH` role and a `UserScope` of type `Holding` for Holding "H-1"

**When** the user requests access to active tenant company "C-1" which belongs to Holding "H-1"

**Then** access is authorized and the connection is resolved to the database of Company "C-1".

---

### AC-002 — Access Granted via Direct Company Scope

**Given** a user with a `Colaborador` role and two `UserScope` records of type `Company` for "C-1" and "C-2"

**When** the user switches active context by requesting access with header `X-Company-Id` set to "C-2"

**Then** access is authorized and the connection switches to the database of Company "C-2" without requiring re-authentication.

---

### AC-003 — Access Denied for Unauthorized Company

**Given** a user with a `Colaborador` role and a `UserScope` of type `Company` for "C-1"

**When** the user requests access to Company "C-3"

**Then** the operation is rejected with a domain authorization error.

**And** no `TenantDbContext` for Company "C-3" is made available to the request.

---

### AC-004 — Global Scope Overrides Specific Tenant Checks

**Given** a user with a `SuperAdmin` role and a `UserScope` of type `Global`

**When** the user requests access to any valid registered company "C-X"

**Then** access is authorized unconditionally with respect to company scope.

**And** the tenant connection is resolved to the database associated with Company "C-X".

Functional authorization for individual operations remains governed by the user's role and applicable authorization policies.

---

### AC-005 — Provisioning Database Rejects Full Instance

**Given** a database instance with `MaxTenants` set to 100 and `CurrentTenantsCount` set to 100

**When** an operation attempts to provision a new company on this instance

**Then** the operation is rejected with a domain capacity error.

---

### AC-006 — Concurrent Provisioning Cannot Exceed Capacity

**Given** a database instance with one remaining tenant slot

**When** two concurrent provisioning operations attempt to allocate that final slot

**Then** only one operation may successfully reserve/provision the available capacity.

**And** the other operation must fail with a capacity/concurrency error.

**And** the final tenant count must not exceed `MaxTenants`.

---

### AC-007 — Tenant Context Contains Only Tenant Data

**Given** a valid authorized request for Company "C-1"

**When** the application executes an operation through `TenantDbContext`

**Then** the context is connected exclusively to Company "C-1"'s database.

**And** tenant entities do not require `CompanyId` discriminator columns for isolation.

---

### AC-008 — Stateless Tenant Switching

**Given** a user authorized for Company "C-1" and Company "C-2"

**When** the user sends one request with `X-Company-Id: C-1` and another request with `X-Company-Id: C-2`

**Then** each request is resolved independently to its corresponding tenant database.

**And** no persistent `ActiveCompanyId` is modified on the user record.

---

### AC-009 — Unauthorized Tenant Does Not Resolve Infrastructure

**Given** a user who is not authorized to access Company "C-3"

**When** the user sends `X-Company-Id: C-3`

**Then** authorization fails.

**And** the system must not expose or use the tenant database connection for Company "C-3" for that request.

---

### AC-010 — Tenant Provisioning Failure Is Explicit

**Given** a new company whose tenant database creation or initial migration fails

**When** the provisioning operation completes

**Then** the company must not be represented as fully provisioned.

**And** the failure must be recorded using an explicit provisioning state.

**And** the failure of this tenant must not corrupt the provisioning state of unrelated tenants.

---

## 5. Constraints

The implementation must:

* Keep the core authorization and scope logic within the Domain layer.
* Keep the Domain layer independent from infrastructure frameworks and database providers.
* Isolate Central Catalog concerns (`CentralDbContext`) from Tenant-specific concerns (`TenantDbContext`).
* Ensure `TenantDbContext` entities do not include tenant discriminator columns (`CompanyId`).
* Resolve dynamic tenant connection strings in the Infrastructure layer via a scoped tenant context.
* Ensure tenant authorization occurs before exposing a tenant-specific `DbContext` to application operations.
* Keep the current tenant selection stateless and request-scoped.
* Never persist the active tenant selection to `ApplicationUser` during normal tenant switching.
* Treat `CompanyId` as the canonical tenant identifier.
* Keep `Role` and `UserScope` as separate authorization concepts.
* Prevent invalid or incompatible Role/Scope combinations from granting unintended access.
* Allow tenant database metadata to be cached without making cache state the authoritative source for authorization.
* Ensure tenant database provisioning is concurrency-safe.
* Ensure tenant migration failures are isolated per database.
* Follow the project rules defined in `AGENTS.md`.
* Follow the TDP workflow defined in `docs/workflows/tdp-feature-workflow.md`.

### Layer Breakdown

* **Domain Layer:** Defines `UserScope`, `ScopeType`, `Holding`, `Company`, `DbInstance`, provisioning states/invariants, and domain rules for authorization and capacity.
* **Application Layer:** Contains handlers/services for evaluating scopes, resolving authorized company access, provisioning new tenant databases, managing tenant lifecycle operations, and requesting context switches.
* **Infrastructure Layer:** Implements `CentralDbContext`, `TenantDbContext`, tenant resolution middleware/handlers, connection string resolution, connection string caching, database provisioning, and database migration routines.
* **API Layer:** Handles authentication, authorization policies, `X-Company-Id` request context, and exposes the application use cases through HTTP endpoints.

---

## 6. Out of Scope

List behavior that is explicitly excluded:

* Implementing business-specific operational entities inside the tenant database (e.g., employee contracts, attendance logs).
* Implementing frontend UI selectors or component representations for switching companies.
* Cross-database joins or distributed queries across multiple tenant databases.
* Automated DevOps infrastructure orchestration outside the application framework (e.g., Kubernetes or Terraform scripts).
* Persisting the currently selected company as mutable state on the user record.
* Implementing business-specific reporting logic.
* Implementing centralized reporting across multiple tenant databases.
* Defining a specific secret-management provider for database credentials.
* Implementing infrastructure orchestration beyond the tenant database provisioning and migration behavior defined by this feature.

---

## 7. Expected Behavior

```text
The system evaluates incoming tenant requests by authenticating the user and validating the user's assigned scopes against the requested target company.

The requested company is provided by the client through the X-Company-Id HTTP header.

The system first determines whether the authenticated user is functionally authorized by Identity role and whether the requested company falls within the user's resolved UserScope.

If the requested company is outside the user's authorized scope, the request fails before tenant-specific infrastructure is exposed.

If access is authorized, the system resolves the requested CompanyId through the Central Catalog:

CompanyId
    ↓
Company
    ↓
DbInstance
    ↓
DatabaseName
    ↓
Connection
    ↓
TenantDbContext

The TenantDbContext is created with a scoped lifetime for the current HTTP request and operates exclusively against the physical database assigned to the requested company.

Tenant-specific entities do not contain CompanyId discriminator columns because physical database isolation guarantees that the database belongs to a single company.

Tenant switching is stateless. The selected company exists only as part of the current request context and is not persisted as mutable state on the user.

A user may therefore operate against different authorized companies from different requests, sessions, or browser tabs without requiring re-authentication.

Tenant database metadata may be cached for performance, but authorization remains governed by the Central Catalog and its defined consistency rules.

When a new company is provisioned, the system selects an active DbInstance with available capacity, creates the physical database, applies the initial tenant schema, and only then considers the tenant fully provisioned.

Tenant database migrations are executed independently through an isolated worker process with controlled concurrency and failure isolation.

The resulting architecture guarantees physical tenant isolation, unified access control, stateless tenant switching, and scalable database-per-company infrastructure.
```

---

## 8. Validation

The feature is complete only when:

1. All acceptance criteria are represented by automated tests.
2. The tests pass.
3. The complete solution builds successfully.
4. The complete test suite passes.
5. Architecture tests pass.
6. No unrelated files are modified.
7. Tests verify that unauthorized users cannot resolve or obtain access to a tenant database.
8. Tests verify that tenant switching does not mutate persistent user state.
9. Tests verify that each authorized `CompanyId` resolves to its correct tenant database.
10. Tests verify that tenant entities do not require `CompanyId` discriminator columns.
11. Tests verify that concurrent tenant provisioning cannot exceed `DbInstance.MaxTenants`.
12. Tests verify that tenant provisioning failures result in an explicit non-ready provisioning state.
13. Tests verify that a migration failure for one tenant does not prevent independent tenant migrations from being processed.
14. Tests verify the expected compatibility between Identity roles and supported `UserScope` types.

