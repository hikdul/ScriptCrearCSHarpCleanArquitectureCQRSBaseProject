## User:
hola, quiero hacer programacion agentica y las pruebas las voy hacer en opencode.

me gustaria que generes una guia paso a paso para poder crear un ejemplo con el que entienda como hacerla y poder desarrollar algo como una web de citas.

el objetivo es usar programacion agentica y trabajar con tdp test driven promp. asi que en cierto modo me gustaria que basado en un archivo se generen las bases del codigo, los test, luego el codigo y por ultimo la validacion si todo esta bien que se indique y si no que se repita el loop maximo 3 repeticiones.

nota importante la idea es usar el modelo que propone c martin y manteniendo siempre el clean code

## system:
Sí. Y para lo que quieres hacer, no plantearía esto simplemente como “darle un prompt a OpenCode para que programe”. Lo interesante es construir un pequeño sistema de desarrollo agentico, donde el agente tenga un ciclo controlado:

Especificación → diseño → tests → implementación → validación → corrección → validación, con un máximo de 3 iteraciones.

Además, si cuando dices “el modelo que propone C. Martin” te refieres a Robert C. Martin (Uncle Bob), podemos basarnos fuertemente en Clean Code + SOLID + TDD + Clean Architecture, haciendo que esos principios sean reglas del agente y no simples recomendaciones.

OpenCode encaja bastante bien para esto porque permite definir AGENTS.md, agentes especializados, permisos y comandos personalizados.

1. Lo que vamos a construir

Te propongo que nuestro proyecto de aprendizaje sea algo pequeño pero suficientemente real:

Proyecto: Matchly

Una web sencilla de citas/encuentros.

El MVP tendrá:

Usuario
 ├── crear perfil
 ├── buscar perfiles
 ├── indicar "me gusta"
 └── generar Match cuando ambos se gustan

Pero no vamos a pedirle a la IA que construya todo esto de una vez.

Vamos a desarrollar una funcionalidad a la vez.

Por ejemplo:

"Como usuario quiero indicar que me gusta otro perfil para poder generar un match."

Y el agente deberá transformar eso en:

requirements.md
       ↓
architecture
       ↓
tests
       ↓
implementation
       ↓
validation
       ↓
PASS / FIX
       ↓
maximum 3 iterations
2. La diferencia importante: AI Coding vs Agentic Programming

Un enfoque tradicional con IA sería:

Humano
   ↓
"Créame un sistema de likes"
   ↓
LLM
   ↓
código

Eso es simplemente AI-assisted coding.

Lo que tú quieres es:

                 ┌──────────────────┐
                 │ specification.md │
                 └────────┬─────────┘
                          ↓
                 ┌──────────────────┐
                 │     Planner      │
                 └────────┬─────────┘
                          ↓
                 ┌──────────────────┐
                 │   Test Writer    │
                 └────────┬─────────┘
                          ↓
                 ┌──────────────────┐
                 │    Developer     │
                 └────────┬─────────┘
                          ↓
                 ┌──────────────────┐
                 │    Validator     │
                 └────────┬─────────┘
                          ↓
                     ¿PASS?
                    /      \
                  YES       NO
                   ↓         ↓
                DONE      Developer
                            ↓
                       max 3 loops

Eso ya se parece mucho más a programación agentica.

3. TDP: Test-Driven Prompting

Aquí haría una pequeña distinción.

TDD tradicional:

RED
 ↓
GREEN
 ↓
REFACTOR

Tú quieres llevar esa filosofía al trabajo con agentes:

PROMPT
 ↓
TEST
 ↓
IMPLEMENTATION
 ↓
VALIDATION
 ↓
FEEDBACK
 ↓
PROMPT/CORRECTION

Podemos llamarlo:

TDP — Test-Driven Prompting

La idea fundamental sería:

El agente no decide si terminó. Los tests y las reglas del proyecto deciden si terminó.

Eso es importantísimo.

No queremos:

"Creo que la implementación está correcta."

Queremos:

dotnet test

Passed: 18
Failed: 0

Architecture tests: PASS
Unit tests: PASS
Integration tests: PASS
Code quality checks: PASS

Entonces:

STATUS = COMPLETE
4. La arquitectura que utilizaría

Dado que ya trabajas bastante con .NET, yo usaría:

.NET 10
ASP.NET Core
PostgreSQL
Entity Framework Core
React + TypeScript
xUnit
FluentAssertions
NetArchTest

Y una arquitectura:

                 ┌──────────────────────┐
                 │      Web / API        │
                 │   ASP.NET + React     │
                 └──────────┬───────────┘
                            │
                            ↓
                 ┌──────────────────────┐
                 │     Application      │
                 │ Use Cases / Ports     │
                 └──────────┬───────────┘
                            │
                            ↓
                 ┌──────────────────────┐
                 │        Domain        │
                 │ Entities / Rules     │
                 └──────────────────────┘
                            ↑
                            │
                 ┌──────────────────────┐
                 │   Infrastructure     │
                 │ EF / PostgreSQL      │
                 └──────────────────────┘

Pero hay una regla fundamental:

Domain
  ↓
NO conoce Infrastructure

Y:

Application
  ↓
NO conoce EF Core

Por ejemplo:

Domain
 ├── User
 ├── Profile
 ├── Like
 └── Match

Application:

Application
 ├── Users
 ├── Likes
 │    └── LikeProfile
 └── Matches

Infrastructure:

Infrastructure
 ├── Persistence
 ├── Repositories
 └── EntityFramework
5. El repositorio será parte del agente

La estructura inicial podría ser:

matchly/
│
├── AGENTS.md
├── README.md
│
├── docs/
│   ├── requirements/
│   │   └── match-profile.md
│   │
│   ├── architecture/
│   │   └── architecture.md
│   │
│   └── decisions/
│
├── src/
│   ├── Matchly.Api/
│   ├── Matchly.Application/
│   ├── Matchly.Domain/
│   └── Matchly.Infrastructure/
│
├── tests/
│   ├── Matchly.Domain.Tests/
│   ├── Matchly.Application.Tests/
│   ├── Matchly.Infrastructure.Tests/
│   └── Matchly.Architecture.Tests/
│
└── .opencode/
    ├── agents/
    └── commands/

Esta estructura es deliberadamente importante.

El agente no debe inventar su propia arquitectura cada vez.

6. AGENTS.md será nuestro "contrato"

OpenCode utiliza AGENTS.md como instrucciones persistentes del proyecto. El propio /init puede generarlo y la documentación recomienda mantenerlo en Git.

Pero nosotros vamos a hacer uno mucho más estricto.

Conceptualmente:

# AGENTS.md

## Project

Matchly is a web application for dating profiles.

## Architecture

Use Clean Architecture.

Dependencies must point inward.

Domain must not depend on:
- Entity Framework
- ASP.NET
- Infrastructure
- external services

Application must not depend on:
- Entity Framework
- Infrastructure implementations

## Development methodology

Use TDD.

Always:

1. Understand requirement
2. Write tests
3. Run tests
4. Implement minimum code
5. Run tests
6. Refactor
7. Validate architecture

## Clean Code

Follow Robert C. Martin principles.

Prefer:
- small functions
- meaningful names
- single responsibility
- explicit dependencies
- low coupling
- high cohesion

Avoid:
- speculative abstractions
- premature optimization
- unnecessary interfaces
- duplicated logic
- god classes
- long methods

## Testing

Tests must exist before implementation.

Never modify a test simply because the implementation fails.

Only modify tests when the requirement itself changed.

## Agent behavior

Never implement multiple unrelated features.

Never skip tests.

Never declare success without executing validation.

Maximum correction iterations: 3.

Esto transforma a AGENTS.md en una especie de constitución del agente.

7. No empezaría con todo el sistema

Este punto es muy importante.

No le daríamos:

"Construye Matchly."

Le daríamos una especificación pequeña.

Por ejemplo:

docs/requirements/like-profile.md

# Like Profile

## Goal

Allow a user to like another user profile.

## Rules

1. A user cannot like themselves.
2. A user cannot like the same profile twice.
3. If user A likes user B and user B already likes user A,
   a Match must be created.
4. The operation must be atomic.
5. The operation must return whether a Match was created.

## Acceptance Criteria

Given user A and user B

When A likes B

Then A must have a Like relationship with B.

Given A already likes B

When A likes B again

Then the operation must fail.

Given A likes B
And B already likes A

When A likes B

Then a Match must exist.

Esto es la fuente de verdad.

8. El primer agente: Planner

Nuestro primer agente no programa.

Su trabajo es analizar:

requirements
+
architecture
+
existing code

y producir:

implementation-plan.md

Por ejemplo:

# Implementation Plan

## Domain

Create:

Like
Match

## Application

Create:

LikeProfileCommand
LikeProfileHandler

## Infrastructure

Add persistence for Like.

## Tests

Domain:
- cannot like itself
- duplicate like

Application:
- creates like
- creates match
- does not create duplicate match

Architecture:
- Domain does not depend on Infrastructure

OpenCode soporta agentes especializados y agentes secundarios (subagents), así que podemos separar estos roles.

9. Segundo agente: Test Engineer

Este agente recibe:

requirements
+
implementation-plan

pero tiene una regla:

NO puede implementar producción.

Solamente:

tests/

Su trabajo:

RED

Por ejemplo:

[Fact]
public void User_cannot_like_itself()
{
    ...
}

Y después:

dotnet test

Debe producir:

Expected failure:
User cannot like itself.

Esto es exactamente lo que queremos.

10. Tercer agente: Developer

Ahora entra el agente que puede modificar producción.

Recibe:

requirements
implementation-plan
tests

Y la instrucción:

Implementa únicamente lo necesario para hacer pasar los tests. No modifiques los tests.

Su objetivo:

RED
 ↓
GREEN

No:

RED
 ↓
"Voy a refactorizar todo el proyecto"
11. Cuarto agente: Validator

Este es probablemente el agente más importante.

No debería confiar en la respuesta del Developer.

Ejecuta:

dotnet test
dotnet build
dotnet format --verify-no-changes

Y eventualmente:

architecture tests
integration tests
security checks

Produce algo estructurado:

VALIDATION RESULT

Tests: PASS
Build: PASS
Architecture: PASS
Formatting: PASS

STATUS: PASS

O:

VALIDATION RESULT

Tests: FAIL

Failures:
- LikeProfileHandlerTests.CreatesMatch

STATUS: FAIL

Suggested correction:
Match creation logic is missing.
12. Aquí aparece realmente el loop agentico

Ahora podemos implementar:

iteration = 0

while iteration < 3:

    planner()

    tests()

    developer()

    result = validator()

    if result == PASS:
        return SUCCESS

    developer(result)

    iteration += 1

return FAILED

Pero hay una mejora.

No queremos ejecutar siempre:

Planner
Test Writer
Developer

otra vez.

Después de un fallo:

Validator
     ↓
Developer
     ↓
Validator

Porque los tests ya existen.

Entonces:

                 REQUIREMENT
                      │
                      ▼
                  PLANNER
                      │
                      ▼
                 TEST WRITER
                      │
                      ▼
                   TESTS
                      │
                      ▼
                 DEVELOPER
                      │
                      ▼
                 VALIDATOR
                      │
             ┌────────┴────────┐
             │                 │
           PASS              FAIL
             │                 │
             ▼                 ▼
          FINISH          DEVELOPER
                               │
                               ▼
                          VALIDATOR
                               │
                         max 3 loops
13. OpenCode puede representar bastante bien este sistema

OpenCode permite crear comandos personalizados mediante archivos Markdown en:

.opencode/commands/

y esos comandos pueden seleccionar agentes, modelos, ejecutar comandos del shell e incluir archivos del proyecto.

Por ejemplo:

.opencode/
│
├── agents/
│   ├── planner.md
│   ├── test-engineer.md
│   ├── developer.md
│   └── validator.md
│
└── commands/
    ├── plan.md
    ├── tests.md
    ├── implement.md
    ├── validate.md
    └── feature.md
14. Comando /plan

Conceptualmente:

---
description: Analyze a feature and create an implementation plan
agent: planner
---

Read:

@AGENTS.md

and the requirement:

@docs/requirements/$ARGUMENTS.md

Analyze the existing codebase.

Do not modify production code.

Create:

docs/architecture/$ARGUMENTS-plan.md

The plan must contain:

- affected layers
- domain changes
- application changes
- infrastructure changes
- API changes
- required tests
- architectural risks

Do not implement anything.

Entonces:

/plan like-profile
15. Comando /tests
---
description: Create tests from a feature specification
agent: test-engineer
---

Read:

@AGENTS.md

@docs/requirements/$ARGUMENTS.md

@docs/architecture/$ARGUMENTS-plan.md

Create the required tests.

Rules:

- Do not modify production code.
- Tests must express business behavior.
- Follow TDD.
- Tests must initially fail for the correct reason.
- Do not weaken assertions.
- Do not modify existing tests unless required by a changed requirement.

Run the test suite.

Report:
- tests created
- expected failures
- unexpected failures
16. Comando /implement
---
description: Implement a feature using existing tests
agent: developer
---

Read:

@AGENTS.md

@docs/requirements/$ARGUMENTS.md

@docs/architecture/$ARGUMENTS-plan.md

Implement the feature.

Rules:

- Do not modify tests.
- Follow Clean Architecture.
- Follow Clean Code.
- Implement the minimum required behavior.
- Do not add speculative abstractions.
- Do not implement unrelated functionality.

Run tests after implementation.

If tests fail, diagnose the production code.

Do not declare success until tests pass.
17. Comando /validate

Aquí empieza algo interesante.

OpenCode permite insertar la salida de comandos shell dentro del prompt mediante !...`.

Podríamos hacer:

---
description: Validate the current implementation
agent: validator
---

Read:

@AGENTS.md

Execute:

!`dotnet build`

!`dotnet test`

!`dotnet format --verify-no-changes`

Analyze the results.

Return exactly:

STATUS: PASS

or:

STATUS: FAIL

If FAIL, list:

1. failing test
2. error
3. likely cause
4. recommended correction

Do not modify code.
18. El /feature sería nuestro orquestador

Finalmente:

/feature like-profile

debería representar:

1. Read requirement
2. Plan
3. Create tests
4. Implement
5. Validate
6. If failed:
      fix
      validate
7. Maximum 3 iterations
8. Report final status

Aquí es donde empieza la verdadera programación agentica.

19. Pero hay una cuestión importante

Yo no pondría todo el control del loop dentro del LLM.

Es decir, evitaría:

LLM:

"Si falla, intenta nuevamente hasta tres veces."

Porque el LLM puede perfectamente:

Iteration 1
Iteration 2
Iteration 3
Iteration 4
Iteration 5
...

o simplemente decir:

"He corregido el problema."

sin haberlo validado correctamente.

El control de flujo debe estar fuera del modelo.

Idealmente:

Orchestrator
     │
     ├── Agent
     ├── Agent
     ├── Agent
     └── Validator

El orquestador es quien dice:

iteration = 1

y sabe que jamás debe superar:

3

Esto es una diferencia fundamental entre un chatbot con prompts y un sistema agentico controlado.

20. Estado de la ejecución

Yo también guardaría un estado.

Por ejemplo:

.agent/
└── runs/
    └── like-profile/
        ├── state.json
        ├── plan.md
        ├── test-result-1.txt
        ├── validation-1.txt
        ├── validation-2.txt
        └── final.md

state.json:

{
  "feature": "like-profile",
  "iteration": 2,
  "status": "failed",
  "phase": "validation",
  "startedAt": "2026-08-08T12:00:00Z"
}

Esto permite que el sistema sea observable.

21. Las reglas de Clean Code deben convertirse en tests

Esto es otra cosa que recomiendo muchísimo.

No solamente:

"Agent, write clean code."

Eso es demasiado subjetivo.

Mejor:

Clean Code
      ↓
Rules
      ↓
Automated validation

Por ejemplo:

Architecture Tests

validando:

Domain → no Infrastructure

Domain → no EF Core

Application → no Infrastructure implementation

Infrastructure → may depend on Application

API → may depend on Application

Y tests de calidad pueden comprobar ciertas reglas objetivas.

Así el agente no necesita "recordar" Clean Architecture.

El repositorio lo obliga.

22. La filosofía de Robert C. Martin

Yo establecería estas reglas:

Single Responsibility

Una clase no debe terminar haciendo:

UserService
 ├── authentication
 ├── database
 ├── email
 ├── matching
 ├── notifications
 └── logging

Queremos:

AuthenticateUser
CreateProfile
LikeProfile
CreateMatch
SendNotification
Dependency Inversion

En Application:

public interface ILikeRepository
{
    Task<bool> ExistsAsync(...);
    Task AddAsync(...);
}

Infrastructure implementa:

public class LikeRepository : ILikeRepository
{
}

No:

Application
    ↓
EF Core

sino:

Application
    ↑
Infrastructure
23. El agente también debe respetar "No premature abstraction"

Este es un punto que muchas veces los agentes hacen fatal.

Le dices:

"Crear Like."

Y termina creando:

IRepository<T>
GenericRepository<T>
BaseService<T>
BaseEntity
BaseHandler<TCommand>
BaseValidator<T>
DomainServiceFactory
...

Para una operación.

Eso va contra el espíritu de Clean Code.

Nuestro AGENTS.md debe decir:

Do not create abstractions until there is a concrete reason for them.

24. El proceso completo de una feature

Al final quiero que puedas pensar una feature así:

                     feature.md
                         │
                         ▼
                    REQUIREMENT
                         │
                         ▼
                       PLAN
                         │
                         ▼
                    TEST DESIGN
                         │
                         ▼
                       RED
                         │
                         ▼
                   IMPLEMENTATION
                         │
                         ▼
                      GREEN
                         │
                         ▼
                      REFACTOR
                         │
                         ▼
                     VALIDATION
                         │
                ┌────────┴────────┐
                │                 │
              PASS              FAIL
                │                 │
                ▼                 ▼
             COMPLETE          FIX #1
                                  │
                                  ▼
                              VALIDATE
                                  │
                            ┌─────┴─────┐
                            │           │
                           PASS       FAIL
                            │           │
                            ▼           ▼
                         COMPLETE     FIX #2
                                        │
                                        ▼
                                    VALIDATE
                                        │
                                  ┌─────┴─────┐
                                  │           │
                                 PASS       FAIL
                                  │           │
                                  ▼           ▼
                               COMPLETE    STOP
25. Y hay algo todavía mejor: separar agentes

No usaría un único agente para todo.

Tendríamos:

                 ┌─────────────┐
                 │   Planner   │
                 └──────┬──────┘
                        │
                        ▼
              ┌──────────────────┐
              │  Test Engineer   │
              └────────┬─────────┘
                       │
                       ▼
                 ┌───────────┐
                 │ Developer │
                 └─────┬─────┘
                       │
                       ▼
                 ┌───────────┐
                 │ Validator │
                 └─────┬─────┘
                       │
                 ┌─────┴─────┐
                 │           │
               PASS        FAIL
                 │           │
                 ▼           ▼
               DONE      Developer

OpenCode suporta precisamente agentes especializados y subagentes, además de permisos diferentes por agente.

Por ejemplo:

Agent	Puede leer	Puede escribir	Bash	Objetivo
Planner	✅	docs	❌	Diseño
Test Engineer	✅	tests	✅	TDD
Developer	✅	código	✅	Implementación
Validator	✅	❌	✅	Verificación
Reviewer	✅	❌	❌	Clean Code

Eso es mucho más seguro que darle todos los permisos a un único agente. OpenCode permite configurar read, edit, bash, task, etc., individualmente por agente.

26. Y agregaría un Code Reviewer

Después de que todo pase:

Validator
    ↓
PASS
    ↓
Code Reviewer

El reviewer no cambia código.

Evalúa:

SOLID
Clean Code
duplicación
nombres
complejidad
acoplamiento
arquitectura
tests

Por ejemplo:

CODE REVIEW

Architecture: PASS
SRP: PASS
DIP: PASS
Duplication: PASS

Issues:

[LOW]
LikeProfileHandler has unnecessary abstraction.

Recommendation:
Remove ILikeService because only one implementation exists.

STATUS: PASS WITH RECOMMENDATIONS
27. Una cosa que NO haría

No empezaría intentando construir:

Multi-agent autonomous software factory

desde el primer día.

Primero:

Fase 1
Requirement
 ↓
Test
 ↓
Code
 ↓
Validate
Fase 2
Requirement
 ↓
Planner
 ↓
Test Engineer
 ↓
Developer
 ↓
Validator
Fase 3
Planner
 ↓
Test Engineer
 ↓
Developer
 ↓
Validator
 ↓
Reviewer
Fase 4
                    Orchestrator
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
          Planner      Tests      Reviewer
             │           │           │
             └───────────┼───────────┘
                         ↓
                      Developer
                         ↓
                      Validator
                         │
                    PASS / FAIL
                         │
                    Retry ≤ 3
28. El primer ejercicio que te recomiendo

No empezaría creando login, perfiles, fotos, mensajes, etc.

Haría una única feature:

Like Profile

Porque contiene suficiente complejidad para demostrar agentic programming:

Business rules
    ↓
Domain
    ↓
Application
    ↓
Persistence
    ↓
Tests
    ↓
Validation
    ↓
Retry

Y además permite probar:

A → B = Like

A → A = invalid

A → B
B → A
   ↓
 Match

Es prácticamente una pequeña máquina de estados.

29. El objetivo final de nuestro experimento

Cuando terminemos la guía, quiero que puedas hacer esto:

cd matchly
opencode

y dentro:

/feature like-profile

Y que el sistema produzca algo parecido a:

╔══════════════════════════════════════╗
║       AGENTIC DEVELOPMENT RUN        ║
╚══════════════════════════════════════╝

Feature:
    like-profile

[1/3] Planning .............. PASS
[1/3] Test generation ...... PASS
[1/3] Implementation ....... PASS
[1/3] Validation ........... FAIL

Failure:
    Match is not created when
    reciprocal like exists.

[2/3] Correction ........... PASS
[2/3] Validation ........... PASS

[3/3] Code review .......... PASS

────────────────────────────────────────

RESULT: SUCCESS

Tests:       27 passed
Architecture: PASS
Build:        PASS
Format:       PASS
Code Review:  PASS

Iterations: 2/3

Eso ya sería un pipeline agentico de desarrollo, no simplemente "usar ChatGPT para programar".

30. Cómo te propongo que lo hagamos juntos

Yo lo dividiría en 8 pasos prácticos, y en cada uno te entregaría los archivos que tienes que crear:

Paso 1 — Crear el proyecto
Matchly
.NET 10
PostgreSQL
React
xUnit
Paso 2 — Crear Clean Architecture
Domain
Application
Infrastructure
API
Tests
Paso 3 — Crear las reglas de AGENTS.md

Aquí definimos exactamente qué puede y qué no puede hacer la IA.

Paso 4 — Crear TDP

Construimos:

requirements
 ↓
tests
 ↓
implementation
 ↓
validation
Paso 5 — Crear los agentes de OpenCode
planner
test-engineer
developer
validator
reviewer
Paso 6 — Crear los comandos
/plan
/tests
/implement
/validate
/review

OpenCode permite precisamente definir estos comandos como Markdown bajo .opencode/commands/, con agentes, modelos, argumentos, referencias de archivos y ejecución de comandos del proyecto.

Paso 7 — Crear el orchestrator

Aquí implementamos:

max_iterations = 3

y hacemos que el programa, no el LLM, controle el loop.

Paso 8 — Primera feature real
Like Profile

y dejamos que el sistema la construya completamente.

Una decisión que considero importante

Para este experimento yo usaría .NET 10 + PostgreSQL + React/TypeScript, porque coincide bastante con tu stack y permite que después podamos llevar exactamente la misma metodología a tu software real.

Y no intentaría hacer que OpenCode "sea inteligente" desde el comienzo. La inteligencia la vamos a conseguir mediante restricciones, contexto, tests, agentes especializados y feedback verificable.

La documentación actual de OpenCode además respalda justamente las piezas que necesitamos: AGENTS.md para las reglas persistentes, agentes especializados/subagentes, permisos diferenciados y comandos personalizados.

Mi recomendación es que el siguiente paso sea construir el proyecto desde cero, empezando por el README, la estructura Clean Architecture, AGENTS.md, opencode.json y la primera especificación like-profile.md. A partir de ahí podemos ir ejecutando el experimento realmente en OpenCode, en lugar de quedarnos solamente en teoría.

## User
bien son 8 pasos para empezar a trabajar.. ve mas a indicar cada paso 1 a 1 hasta que lleguemos al 8 diciendome esactamente que debo hacer.

empecemos con el paso 1

## system

Sí. Este error no viene de nuestro proyecto Matchly; viene del SDK de .NET que estás usando (10.0.110) y de la información de package pruning para Microsoft.AspNetCore.App.

Y como estamos construyendo una base para que posteriormente los agentes trabajen sobre ella, no quiero que simplemente pongamos AllowMissingPrunePackageData=true sin entenderlo.

Vamos a corregir el entorno primero.

1. Confirma qué SDK estás usando

Ejecuta:

dotnet --info

y también:

dotnet --list-sdks

En tu error ya vemos:

/usr/share/dotnet/sdk/10.0.110/

Así que probablemente tienes .NET 10 instalado, pero quiero comprobar si tienes varias versiones.

2. Comprueba si tienes global.json

Desde Matchly:

ls -la

Si existe:

global.json

muéstramelo:

cat global.json

Si no existe, no pasa nada.

3. Comprueba el .csproj de la API

Ejecuta:

cat src/Matchly.Api/Matchly.Api.csproj

Probablemente tendremos algo parecido a:

<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

</Project>

Eso está bien.

4. Primero intentemos la solución recomendada para nuestro proyecto

Como estamos utilizando .NET 10 y queremos cerrar correctamente el baseline del proyecto, podemos agregar explícitamente:

<AllowMissingPrunePackageData>true</AllowMissingPrunePackageData>

Pero solo al proyecto Web, no quiero empezar contaminando todos los proyectos con una propiedad que no necesitan.

Edita:

nvim src/Matchly.Api/Matchly.Api.csproj

y déjalo así:

<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>

    <AllowMissingPrunePackageData>true</AllowMissingPrunePackageData>
  </PropertyGroup>

</Project>

Guarda.

5. Limpia el restore anterior

Ahora:

dotnet clean

Después elimina los obj generados:

find . -type d -name obj -prune -exec rm -rf {} +

Y también bin:

find . -type d -name bin -prune -exec rm -rf {} +

Esto es importante porque el error ocurre durante restore.

6. Restore nuevamente

Ejecuta:

dotnet restore

Si termina correctamente:

Restore succeeded.

continúa con:

dotnet build
7. Después ejecuta los tests
dotnet test
8. Si sigue apareciendo NETSDK1226

Si vuelve a aparecer:

NETSDK1226
Prune Package data not found

no agregues todavía más configuraciones.

Pásame la salida completa de:

dotnet --info
dotnet --list-sdks
cat src/Matchly.Api/Matchly.Api.csproj

y:

find . -name "*.csproj" -print -exec sh -c 'echo "--- $1"; cat "$1"' _ {} \;

Con eso podemos determinar si el problema viene del SDK 10.0.110, de la instalación de .NET en Arch o de alguna configuración del proyecto.

Importante para nuestro experimento

No considero terminado el Paso 1 hasta conseguir:

dotnet restore    → PASS
dotnet build      → PASS
dotnet test       → PASS
git status        → limpio

Y no vamos a avanzar al Paso 2 todavía. Queremos que el estado inicial del repositorio sea completamente reproducible; eso será fundamental cuando posteriormente hagamos que el agente modifique el código y necesitemos saber si un fallo lo introdujo el agente o ya existía antes.

## User

Matchly main ❯ dotnet info
Could not execute because the specified command or file was not found.
Possible reasons for this include:

- You misspelled a built-in dotnet command.
- You intended to execute a .NET program, but dotnet-info does not exist.
- You intended to run a global tool, but a dotnet-prefixed executable with this name could not be found on the PATH.

Matchly main ✗ dotnet --info
.NET SDK:
Version:           10.0.110
Commit:            f7d90799ce
Workload version:  10.0.100-manifests.1641d827
MSBuild version:   18.0.11

Runtime Environment:
OS Name:     arch
OS Version:
OS Platform: Linux
RID:         arch-x64
Base Path:   /usr/share/dotnet/sdk/10.0.110/

.NET workloads installed:
There are no installed workloads to display.
Configured to use workload sets when installing new manifests.
No workload sets are installed. Run "dotnet workload restore" to install a workload set.

Host:
Version:      10.0.10
Architecture: x64
Commit:       f7d90799ce

.NET SDKs installed:
10.0.110 [/usr/share/dotnet/sdk]

.NET runtimes installed:
Microsoft.NETCore.App 9.0.18 [/usr/share/dotnet/shared/Microsoft.NETCore.App]
Microsoft.NETCore.App 10.0.10 [/usr/share/dotnet/shared/Microsoft.NETCore.App]

Other architectures found:
None

Environment variables:
Not set

global.json file:
Not found

Learn more:
[https://aka.ms/dotnet/info](https://aka.ms/dotnet/info)

Download .NET:
[https://aka.ms/dotnet/download](https://aka.ms/dotnet/download)

Matchly main ❯ dotnet --list-sdks
10.0.110 [/usr/share/dotnet/sdk]


# System

Perfecto. Con esa información ya queda bastante claro el problema.

Tienes una instalación muy reciente de .NET 10 en Arch Linux:

SDK:       10.0.110
Runtime:   10.0.10
OS:        Arch Linux

Y no tienes global.json, así que Matchly no está forzando una versión concreta del SDK.

El error:

NETSDK1226: Prune Package data not found
.NETCoreApp 10.0 Microsoft.AspNetCore.App

está ocurriendo durante restore, antes de compilar nuestro código.

Primero quiero que hagamos una corrección importante

En el mensaje anterior te indiqué poner AllowMissingPrunePackageData solamente en Matchly.Api. Para este caso, prefiero no hacerlo todavía.

Como estamos construyendo un proyecto que posteriormente será utilizado por agentes, quiero que el baseline esté limpio y que no ocultemos un problema del SDK mediante una propiedad de compatibilidad.

Haz esto ahora
1. Muéstrame los .csproj

Ejecuta:

find . -name "*.csproj" -print

y luego:

cat src/Matchly.Api/Matchly.Api.csproj

También:

cat src/Matchly.Domain/Matchly.Domain.csproj
cat src/Matchly.Application/Matchly.Application.csproj
cat src/Matchly.Infrastructure/Matchly.Infrastructure.csproj
2. Comprueba si Arch tiene instalado el paquete ASP.NET correspondiente

Ejecuta:

pacman -Qs aspnet

y:

pacman -Qs dotnet

Esto es particularmente importante porque tu SDK está buscando información de:

Microsoft.AspNetCore.App

y en Arch el SDK/runtime se gestiona mediante los paquetes de Arch.

3. Comprueba físicamente qué runtimes tienes

Ejecuta:

ls -la /usr/share/dotnet/shared/Microsoft.AspNetCore.App/

y:

ls -la /usr/share/dotnet/packs/
4. No ejecutes todavía dotnet workload restore

El mensaje:

No workload sets are installed.
Run "dotnet workload restore"

no es la causa de este problema.

No necesitamos workloads para una API ASP.NET Core normal.

Una observación importante

Tu instalación muestra:

Microsoft.NETCore.App 10.0.10

pero todavía no sabemos si tienes:

Microsoft.AspNetCore.App 10.0.x

instalado correctamente.

Por eso quiero ver específicamente:

ls /usr/share/dotnet/shared/Microsoft.AspNetCore.App/

Si ese directorio no existe, probablemente ya encontramos el problema.

Envíame estas cuatro salidas

Puedes ejecutar todo de una vez:

echo "=== CSPROJ ==="
find . -name "*.csproj" -print

echo "=== API ==="
cat src/Matchly.Api/Matchly.Api.csproj

echo "=== ASPNET RUNTIME ==="
ls -la /usr/share/dotnet/shared/Microsoft.AspNetCore.App/

echo "=== DOTNET PACKAGES ==="
pacman -Qs dotnet

Con eso te digo exactamente qué corregir en Arch, sin meter todavía configuraciones de workaround en Matchly.

Y una pequeña corrección: el comando correcto es dotnet --info, como hiciste después; dotnet info no existe.

## User


Matchly main ❯ find . -name "*.csproj" -print
./src/Matchly.Domain/Matchly.Domain.csproj
./src/Matchly.Application/Matchly.Application.csproj
./src/Matchly.Infrastructure/Matchly.Infrastructure.csproj
./src/Matchly.Api/Matchly.Api.csproj
./tests/Matchly.Domain.Tests/Matchly.Domain.Tests.csproj
./tests/Matchly.Application.Tests/Matchly.Application.Tests.csproj
./tests/Matchly.Infrastructure.Tests/Matchly.Infrastructure.Tests.csproj
./tests/Matchly.Architecture.Tests/Matchly.Architecture.Tests.csproj

Matchly main ❯ cat src/Matchly.Api/Matchly.Api.csproj
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="10.0.10" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\Matchly.Application\Matchly.Application.csproj" />
  </ItemGroup>

</Project>

Matchly main ❯ cat src/Matchly.Domain/Matchly.Domain.csproj
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

</Project>

Matchly main ❯ cat src/Matchly.Application/Matchly.Application.csproj
<Project Sdk="Microsoft.NET.Sdk">

  <ItemGroup>
    <ProjectReference Include="..\Matchly.Domain\Matchly.Domain.csproj" />
  </ItemGroup>

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

</Project>

Matchly main ❯ cat src/Matchly.Infrastructure/Matchly.Infrastructure.csproj
<Project Sdk="Microsoft.NET.Sdk">

  <ItemGroup>
    <ProjectReference Include="..\Matchly.Domain\Matchly.Domain.csproj" />
  </ItemGroup>

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

</Project>

para el pacman -Qs aspnet no muestra nada



## System

Perfecto, ya encontramos la causa. Tus .csproj están bien.

El dato clave es:

pacman -Qs aspnet
→ no muestra nada

y tu API usa:

<Project Sdk="Microsoft.NET.Sdk.Web">

Por lo tanto, te falta el runtime de ASP.NET Core 10 en Arch Linux.

Arch separa el runtime de .NET (dotnet-runtime) del runtime de ASP.NET Core (aspnet-runtime). La documentación de Arch indica que para construir aplicaciones ASP.NET Core se necesitan aspnet-runtime y aspnet-targeting-pack.

Además, actualmente Arch tiene disponibles las versiones 10.0.10.sdk110-1, que coinciden exactamente con tu SDK 10.0.110.

Haz esto
1. Actualiza el sistema

Primero:

sudo pacman -Syu

Si te pide reiniciar por alguna actualización importante, hazlo antes de continuar.

2. Instala ASP.NET Core 10

Ejecuta:

sudo pacman -S aspnet-runtime-10.0 aspnet-targeting-pack-10.0

No necesitas instalar otra versión de .NET.

Tu combinación debería quedar:

dotnet-sdk-10.0
dotnet-runtime-10.0
aspnet-runtime-10.0
aspnet-targeting-pack-10.0

Arch actualmente publica esos paquetes como parte de dotnet-core-10.0.

3. Comprueba que ahora existe ASP.NET

Ejecuta:

dotnet --list-runtimes

Queremos ver algo parecido a:

Microsoft.AspNetCore.App 10.0.10 [/usr/share/dotnet/shared/Microsoft.AspNetCore.App]
Microsoft.NETCore.App 10.0.10 [/usr/share/dotnet/shared/Microsoft.NETCore.App]

Y:

dotnet --list-sdks

debería mostrar:

10.0.110 [/usr/share/dotnet/sdk]
4. Comprueba el paquete

También:

pacman -Qs aspnet

Ahora debería aparecer algo como:

local/aspnet-runtime-10.0 10.0.10.sdk110-1
local/aspnet-targeting-pack-10.0 10.0.10.sdk110-1
5. Ahora limpia Matchly

Desde el directorio del proyecto:

find . -type d -name obj -prune -exec rm -rf {} +
find . -type d -name bin -prune -exec rm -rf {} +

Después:

dotnet restore

Luego:

dotnet build

Y finalmente:

dotnet test
No agregues AllowMissingPrunePackageData

Ahora que sabemos cuál era el problema, no pongas:

<AllowMissingPrunePackageData>true</AllowMissingPrunePackageData>

en nuestros proyectos.

Eso sería ocultar el problema del entorno. Para nuestro experimento agentico quiero que el proyecto empiece desde un estado correcto y reproducible.

El estado que buscamos

Después de instalar los paquetes, estos tres comandos deben funcionar:

dotnet restore
dotnet build
dotnet test

Y especialmente:

dotnet --list-runtimes

debe contener:

Microsoft.AspNetCore.App 10.0.10
Después de hacerlo

Pásame solamente la salida de:

dotnet --list-runtimes

y:

dotnet test

Si ambos están bien, cerramos oficialmente el Paso 1 y pasamos al Paso 2.


## user
paso 1 completo continuemos al paso 2


## system

Perfecto. Paso 1 queda cerrado. Ahora empezamos el Paso 2 y, nuevamente, no avanzaremos al 3 hasta dejarlo completamente terminado.

Paso 2 — Establecer Clean Architecture y las reglas arquitectónicas

En este paso todavía no vamos a crear agentes de OpenCode.

El objetivo es conseguir que el repositorio tenga una arquitectura que pueda ser verificada automáticamente.

La idea central es:

No queremos decirle al agente solamente "usa Clean Architecture". Queremos que el proyecto pueda detectar automáticamente cuándo el agente viola la arquitectura.

Al terminar este paso tendremos:

Matchly/
├── src/
│   ├── Matchly.Api/
│   ├── Matchly.Application/
│   ├── Matchly.Domain/
│   └── Matchly.Infrastructure/
│
├── tests/
│   ├── Matchly.Domain.Tests/
│   ├── Matchly.Application.Tests/
│   ├── Matchly.Infrastructure.Tests/
│   └── Matchly.Architecture.Tests/
│
└── docs/
    └── architecture/
        └── architecture.md

Y tendremos tests capaces de detectar dependencias incorrectas.

2.1. Primero definamos nuestra arquitectura

Para Matchly vamos a utilizar esta variante de Clean Architecture:

                         ┌─────────────────┐
                         │   Matchly.Api   │
                         │   HTTP / Web    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Application  │
                         │   Use Cases     │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     Domain      │
                         │ Business Rules  │
                         └─────────────────┘
                                  ▲
                                  │
                         ┌────────┴────────┐
                         │ Infrastructure  │
                         │ DB / EF / APIs  │
                         └─────────────────┘

Hay una sutileza importante:

Infrastructure implementará interfaces definidas en Application.

Por ejemplo:

Application
    │
    └── ILikeRepository
             ▲
             │ implements
             │
Infrastructure
    │
    └── LikeRepository

Así Application define qué necesita, pero no sabe cómo se almacena.

2.2. Nuestras reglas arquitectónicas

Vamos a establecer estas reglas:

Regla 1 — Domain es independiente
Domain

no puede depender de:

Application
Infrastructure
API
EF Core
ASP.NET Core
PostgreSQL
Regla 2 — Application depende solamente de Domain
Application
    ↓
Domain

No:

Application
    ↓
Infrastructure
Regla 3 — Infrastructure depende de Application
Infrastructure
    ↓
Application
    ↓
Domain

Infrastructure puede conocer Domain directamente si lo necesita.

Regla 4 — API depende de Application
API
 ↓
Application
 ↓
Domain

Por ahora API no tendrá una referencia directa a Infrastructure.

Esto nos obliga a pensar correctamente cómo vamos a conectar la infraestructura posteriormente.

Regla 5 — Domain no conoce frameworks

Queremos poder abrir:

src/Matchly.Domain

y encontrar código de negocio puro.

Nada de:

[ApiController]

ni:

[Table("users")]

ni:

DbContext

ni:

IHttpContextAccessor
2.3. Documentemos la arquitectura

Crea el directorio:

mkdir -p docs/architecture

Ahora:

nvim docs/architecture/architecture.md

Coloca:

# Matchly Architecture

## Overview

Matchly follows Clean Architecture principles inspired by
Robert C. Martin.

The system is divided into four main layers:

- Domain
- Application
- Infrastructure
- API

## Dependency Rule

Dependencies must point toward the Domain.

```text
API
 ↓
Application
 ↓
Domain

Infrastructure
 ↓
Application
 ↓
Domain

Infrastructure implements abstractions defined by the Application layer.

Domain

The Domain layer contains:

Entities
Value Objects
Domain Rules
Domain Services
Domain Exceptions

The Domain layer must not depend on:

ASP.NET Core
Entity Framework Core
Infrastructure
API
PostgreSQL
External services
Application

The Application layer contains:

Use Cases
Commands
Queries
Application Services
Interfaces required by use cases
DTOs

Application may depend on Domain.

Application must not depend on Infrastructure implementations.

Infrastructure

Infrastructure contains implementation details:

Entity Framework Core
PostgreSQL
Repositories
External services
Persistence

Infrastructure depends on Application and Domain.

API

API contains:

HTTP endpoints
Request/response models
Dependency injection composition
Authentication configuration

API depends on Application.

Dependency Inversion

Application defines abstractions required by the business use cases.

Infrastructure implements those abstractions.

Example:

Application

ILikeRepository
      ▲
      │
      │ implementation
      │
Infrastructure

LikeRepository
Architectural Rules
Domain cannot depend on Application.
Domain cannot depend on Infrastructure.
Domain cannot depend on API.
Domain cannot depend on external frameworks.
Application cannot depend on Infrastructure.
Application cannot depend on API.
Infrastructure can depend on Application.
API can depend on Application.
API must not contain business rules.
Infrastructure must not contain business rules.
Goal

Architecture violations must be detected automatically through tests.


Guarda.

---

# 2.4. Ahora vamos a crear el primer Architecture Test

Este será uno de los elementos **más importantes de todo nuestro experimento agentico**.

El agente posteriormente podrá modificar código, pero no podrá escapar de estas reglas.

Vamos a utilizar **NetArchTest**.

Desde la raíz del proyecto:

```bash id="a4n0q4"
dotnet add tests/Matchly.Architecture.Tests/Matchly.Architecture.Tests.csproj package NetArchTest.Rules

Ahora necesitamos darle acceso a los assemblies de nuestro proyecto.

Ejecuta:

dotnet add tests/Matchly.Architecture.Tests/Matchly.Architecture.Tests.csproj reference src/Matchly.Domain/Matchly.Domain.csproj
dotnet add tests/Matchly.Architecture.Tests/Matchly.Architecture.Tests.csproj reference src/Matchly.Application/Matchly.Application.csproj
dotnet add tests/Matchly.Architecture.Tests/Matchly.Architecture.Tests.csproj reference src/Matchly.Infrastructure/Matchly.Infrastructure.csproj
dotnet add tests/Matchly.Architecture.Tests/Matchly.Architecture.Tests.csproj reference src/Matchly.Api/Matchly.Api.csproj
2.5. Crea ArchitectureTests.cs

Elimina el test de ejemplo:

rm tests/Matchly.Architecture.Tests/UnitTest1.cs

Ahora:

nvim tests/Matchly.Architecture.Tests/ArchitectureTests.cs

Coloca:

using NetArchTest.Rules;

namespace Matchly.Architecture.Tests;

public class ArchitectureTests
{
    private const string DomainNamespace = "Matchly.Domain";
    private const string ApplicationNamespace = "Matchly.Application";
    private const string InfrastructureNamespace = "Matchly.Infrastructure";
    private const string ApiNamespace = "Matchly.Api";

    [Fact]
    public void Domain_Should_Not_Depend_On_Application()
    {
        var result = Types
            .InAssembly(typeof(Matchly.Domain.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(ApplicationNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Domain_Should_Not_Depend_On_Infrastructure()
    {
        var result = Types
            .InAssembly(typeof(Matchly.Domain.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(InfrastructureNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Domain_Should_Not_Depend_On_Api()
    {
        var result = Types
            .InAssembly(typeof(Matchly.Domain.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(ApiNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Application_Should_Not_Depend_On_Infrastructure()
    {
        var result = Types
            .InAssembly(typeof(Matchly.Application.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(InfrastructureNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Application_Should_Not_Depend_On_Api()
    {
        var result = Types
            .InAssembly(typeof(Matchly.Application.AssemblyMarker).Assembly)
            .ShouldNot()
            .HaveDependencyOn(ApiNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful);
    }
}

Pero todavía nos falta una cosa.

2.6. Necesitamos Assembly Markers

Los proyectos están vacíos y necesitamos una forma limpia de obtener sus assemblies.

En Domain crea:

nvim src/Matchly.Domain/AssemblyMarker.cs

Contenido:

namespace Matchly.Domain;

public sealed class AssemblyMarker
{
}

Application:

nvim src/Matchly.Application/AssemblyMarker.cs
namespace Matchly.Application;

public sealed class AssemblyMarker
{
}

Infrastructure:

nvim src/Matchly.Infrastructure/AssemblyMarker.cs
namespace Matchly.Infrastructure;

public sealed class AssemblyMarker
{
}

API:

No necesitamos marker porque el test anterior solamente está utilizando los assemblies de Domain/Application.

2.7. Hay una decisión de Clean Code aquí

Podríamos hacer esto:

public static class AssemblyReference
{
}

Pero prefiero:

public sealed class AssemblyMarker
{
}

porque:

no tiene estado;
no tiene comportamiento;
es explícito;
no introduce abstracciones;
solamente identifica el assembly.

Es una pieza técnica pequeña y con una responsabilidad única.

2.8. Ejecuta los tests

Ahora:

dotnet test

Deberías obtener:

Passed!

Con nuestros cinco architecture tests:

Domain_Should_Not_Depend_On_Application
Domain_Should_Not_Depend_On_Infrastructure
Domain_Should_Not_Depend_On_Api
Application_Should_Not_Depend_On_Infrastructure
Application_Should_Not_Depend_On_Api
2.9. Hagamos una prueba importante

Quiero que comprobemos que nuestros tests realmente pueden detectar una violación.

No solamente que pasan.

Temporalmente agrega esta referencia:

dotnet add src/Matchly.Domain/Matchly.Domain.csproj reference src/Matchly.Infrastructure/Matchly.Infrastructure.csproj

Ahora:

dotnet test

Debe fallar.

Si falla, perfecto.

Eso significa:

Architecture violation
        ↓
Architecture Test
        ↓
FAIL

Eso es exactamente lo que necesitamos para nuestro futuro agente.

2.10. Ahora revierte esa violación

No queremos dejarla.

Ejecuta:

dotnet remove src/Matchly.Domain/Matchly.Domain.csproj reference src/Matchly.Infrastructure/Matchly.Infrastructure.csproj

Después:

dotnet test

Debe volver a:

PASS
2.11. Comprobemos la arquitectura real

Ejecuta:

dotnet list src/Matchly.Domain/Matchly.Domain.csproj reference

Debe indicar que no tiene referencias.

Luego:

dotnet list src/Matchly.Application/Matchly.Application.csproj reference

Debe mostrar:

Matchly.Domain

Infrastructure:

dotnet list src/Matchly.Infrastructure/Matchly.Infrastructure.csproj reference

Debe mostrar:

Matchly.Domain
Matchly.Application

API:

dotnet list src/Matchly.Api/Matchly.Api.csproj reference

Debe mostrar:

Matchly.Application
2.12. El resultado final del Paso 2

Queremos llegar a esto:

                     API
                      │
                      ▼
                Application
                      │
                      ▼
                   Domain
                      
                Infrastructure
                      │
                      ▼
                Application
                      │
                      ▼
                   Domain

Y además:

Architecture Tests
        │
        ├── Domain isolation
        ├── Application isolation
        ├── Infrastructure boundaries
        └── API boundaries
2.13. Finalmente haz commit

Cuando todo esté verde:

dotnet build
dotnet test

Después:

git status

Y:

git add .
git commit -m "test: enforce clean architecture boundaries"

Comprueba:

git log --oneline -2

Deberías tener:

xxxxxxx test: enforce clean architecture boundaries
xxxxxxx chore: initialize Matchly project
🚦 No avances todavía al Paso 3

El Paso 2 está terminado únicamente cuando:

✅ dotnet build
✅ dotnet test
✅ Domain no depende de Application
✅ Domain no depende de Infrastructure
✅ Domain no depende de API
✅ Application no depende de Infrastructure
✅ Application no depende de API
✅ Architecture test falla si introducimos una dependencia incorrecta
✅ La dependencia incorrecta fue eliminada
✅ Git commit creado

Cuando llegues a ese punto, dime:

"Paso 2 terminado"

y empezaremos el Paso 3 — crear AGENTS.md y el contrato de comportamiento del agente, donde vamos a convertir TDD + Clean Code + SOLID + Clean Architecture + TDP en las instrucciones permanentes que OpenCode deberá seguir.
```


## User

tengo esta salida de consola:



```
Matchly main  ? ❯ dotnet list src/Matchly.Domain/Matchly.Domain.csproj reference
There are no Project to Project references in project src/Matchly.Domain/Matchly.Domain.csproj.

Matchly main  ? ❯ dotnet list src/Matchly.Application/Matchly.Application.csproj reference
Project reference(s)
--------------------
../Matchly.Domain/Matchly.Domain.csproj

Matchly main  ? ❯ dotnet list src/Matchly.Infrastructure/Matchly.Infrastructure.csproj reference
Project reference(s)
--------------------
../Matchly.Domain/Matchly.Domain.csproj

Matchly main  ? ❯ dotnet list src/Matchly.Api/Matchly.Api.csproj reference
Project reference(s)
--------------------
../Matchly.Application/Matchly.Application.csproj
```

## System

Sí, y aquí hay una diferencia importante respecto de lo que esperábamos.

Tu salida muestra:

Domain
  └── ninguna dependencia

Application
  └── Domain

Infrastructure
  └── Domain

API
  └── Application

Pero Infrastructure no está referenciando Application.

Actualmente tienes:

API
 ↓
Application
 ↓
Domain

Infrastructure
 ↓
Domain

Y yo había definido para nuestro experimento:

API
 ↓
Application
 ↓
Domain

Infrastructure
 ↓
Application
 ↓
Domain
¿Es un error?

No necesariamente. De hecho, para Clean Architecture esto puede ser perfectamente válido dependiendo de cómo diseñemos Infrastructure.

Pero para el modelo que vamos a utilizar con TDD/TDP, quiero que Infrastructure implemente las abstracciones que definiremos en Application.

Por ejemplo, posteriormente tendremos:

Application
└── Abstractions
    └── ILikeRepository

y:

Infrastructure
└── Persistence
    └── LikeRepository : ILikeRepository

Por tanto:

Infrastructure
      │
      └──────► Application

es necesario.

Haz solamente este cambio

Ejecuta:

dotnet add src/Matchly.Infrastructure/Matchly.Infrastructure.csproj \
  reference src/Matchly.Application/Matchly.Application.csproj

Después comprueba:

dotnet list src/Matchly.Infrastructure/Matchly.Infrastructure.csproj reference

Ahora debería aparecer:

Project reference(s)
--------------------
../Matchly.Domain/Matchly.Domain.csproj
../Matchly.Application/Matchly.Application.csproj

El orden puede variar; no importa.

Después ejecuta
dotnet build

y:

dotnet test

Ambos deberían pasar.

Luego comprueba nuevamente:

dotnet list src/Matchly.Domain/Matchly.Domain.csproj reference
dotnet list src/Matchly.Application/Matchly.Application.csproj reference
dotnet list src/Matchly.Infrastructure/Matchly.Infrastructure.csproj reference
dotnet list src/Matchly.Api/Matchly.Api.csproj reference

La estructura final que queremos en este paso es:

                    Matchly.Api
                         │
                         ▼
                Matchly.Application
                         │
                         ▼
                   Matchly.Domain
                         ▲
                         │
              Matchly.Infrastructure

Esto además nos deja preparada la arquitectura para el siguiente paso.

Una cosa importante

No agregues ninguna referencia más.

En particular, NO hagas:

Domain → Application
Domain → Infrastructure
Domain → API
Application → Infrastructure
Application → API
API → Infrastructure

La única que falta ahora es:

Infrastructure → Application

Después de agregarla y verificar build + test, dime "continúa" y cerramos formalmente el Paso 2 antes de entrar al Paso 3.

## user

bien, ahora hagamos el paso 3

## system

Perfecto. Paso 3: crear el contrato del agente con AGENTS.md.

Este paso es especialmente importante porque aquí dejamos de definir solamente la arquitectura del software y empezamos a definir cómo debe comportarse el agente cuando trabaje sobre el repositorio.

Todavía no vamos a crear agentes especializados ni el loop de 3 iteraciones. Eso vendrá después.

Paso 3 — Crear AGENTS.md
Objetivo

Al terminar este paso tendremos:

matchly/
├── AGENTS.md                  ← contrato del agente
├── README.md
├── docs/
│   └── architecture/
│       └── architecture.md
├── src/
└── tests/

AGENTS.md será nuestra fuente de reglas para OpenCode.

La idea es que posteriormente cualquier agente que trabaje en Matchly tenga que respetar:

Clean Architecture
        +
Clean Code
        +
SOLID
        +
TDD
        +
TDP
        +
Testing
        +
Git discipline
3.1. Antes de crear el archivo

Quiero que entendamos una cosa.

No vamos a escribir un AGENTS.md gigantesco lleno de:

"Eres un excelente programador senior..."

Eso suele aportar poco.

Vamos a escribir reglas operacionales.

Por ejemplo:

❌ Mala regla:

Write high quality code.

✅ Buena regla:

Production code must not be considered complete until the
test suite passes.

❌ Mala regla:

Use Clean Architecture.

✅ Buena regla:

Domain must not reference Application, Infrastructure or API.

Esto es muy importante para nuestro enfoque TDP.

3.2. Crear AGENTS.md

Desde la raíz de Matchly:

nvim AGENTS.md

Coloca exactamente lo siguiente:

# Matchly Agent Contract

## 1. Project

Matchly is an experimental web application used to study:

- Agentic Programming
- Test-Driven Development
- Test-Driven Prompting
- Clean Code
- SOLID
- Clean Architecture

The project is developed incrementally through small, independently
validated features.

---

# 2. Core Development Principles

The following principles are mandatory:

1. Correctness over speed.
2. Simplicity over unnecessary abstraction.
3. Explicit behavior over implicit behavior.
4. Tests are executable specifications.
5. Production code must satisfy the tests.
6. Architectural rules must be automatically verifiable.
7. Do not implement functionality that is not required.
8. Do not modify unrelated code.
9. Do not weaken tests to make an implementation pass.
10. Do not declare success without executing validation.

---

# 3. Clean Architecture

Matchly follows Clean Architecture principles.

The architecture is:

```text
API
 ↓
Application
 ↓
Domain

Infrastructure
 ↓
Application
 ↓
Domain

Dependencies must point toward the Domain.

Domain

Domain contains business rules and business concepts.

Domain must NOT depend on:

Application
Infrastructure
API
ASP.NET Core
Entity Framework Core
PostgreSQL
HTTP
external services

Domain code must remain framework independent.

Application

Application contains:

Use Cases
Commands
Queries
Application Services
DTOs
Interfaces required by use cases

Application may depend on:

Domain

Application must NOT depend on:

Infrastructure implementations
API
ASP.NET Core
Entity Framework Core

Application defines abstractions required by the use cases.

Infrastructure

Infrastructure contains implementation details.

Examples:

Entity Framework Core
PostgreSQL
Repository implementations
External services
Persistence
File systems

Infrastructure may depend on:

Application
Domain

Infrastructure implements abstractions defined by Application.

Infrastructure must not contain business rules that belong to Domain.

API

API contains:

HTTP endpoints
Request models
Response models
Dependency injection composition
Authentication configuration
HTTP-specific concerns

API may depend on:

Application

API must not contain business rules.

4. Dependency Rules

The following dependencies are forbidden:

Domain → Application
Domain → Infrastructure
Domain → API

Application → Infrastructure
Application → API

Domain → ASP.NET Core
Domain → Entity Framework Core
Domain → PostgreSQL

Architecture tests must detect violations of these rules.

Never bypass an architecture test by weakening or removing the test.

5. Clean Code

Follow Clean Code principles inspired by Robert C. Martin.

Naming

Names must communicate intent.

Prefer:

CreateUser
LikeProfile
CreateMatch
FindProfile

Avoid:

DoIt
Process
Manager
Helper
Handler2
Data
Info

unless the name is genuinely appropriate.

Functions

Functions should:

have one clear responsibility
be small
have meaningful names
avoid unnecessary parameters
avoid hidden side effects

Avoid large methods containing multiple responsibilities.

Classes

Classes should have a focused responsibility.

Avoid:

God classes
large service classes
classes with unrelated responsibilities
unnecessary inheritance
Abstractions

Do not create abstractions speculatively.

Do not create:

IRepository<T>
BaseService<T>
BaseHandler<T>
GenericManager<T>

without a concrete requirement.

Prefer the simplest design that satisfies the current requirement.

6. SOLID

Apply SOLID principles when they improve the design.

Single Responsibility

A class should have one clear reason to change.

Open/Closed

Prefer designs that can evolve without modifying stable business rules.

Do not introduce abstractions solely to satisfy this principle.

Liskov Substitution

Implementations must honor the contract of their abstractions.

Interface Segregation

Prefer focused interfaces over large interfaces.

Dependency Inversion

High-level application logic must depend on abstractions rather than infrastructure implementations.

7. Test-Driven Development

Development follows TDD.

The default cycle is:

RED
 ↓
GREEN
 ↓
REFACTOR
RED

Create a test describing required behavior.

Run the test.

The test should fail because the required behavior does not exist.

GREEN

Implement the minimum production code necessary to make the test pass.

Do not implement speculative functionality.

REFACTOR

Improve the implementation while preserving behavior.

After refactoring, tests must remain green.

8. Test-Driven Prompting

Features are developed from explicit requirements.

The development flow is:

Requirement
 ↓
Test Specification
 ↓
Tests
 ↓
Implementation
 ↓
Validation

The requirement is the source of truth.

Tests represent executable acceptance criteria.

Implementation must satisfy the tests and the requirement.

9. Tests Are Specifications

Tests must verify behavior.

Prefer:

User_cannot_like_themselves
Duplicate_like_is_rejected
Reciprocal_likes_create_match

Avoid tests that only verify implementation details.

Do not write tests such as:

Repository_method_X_was_called

unless the interaction itself is part of the required behavior.

10. Test Integrity

Tests must not be weakened to make production code pass.

Never:

remove an assertion because it fails
make an assertion less strict
skip a failing test
delete a test without a requirement change
change expected behavior merely to match the implementation

If production code fails a valid test:

Fix production code.

If the requirement changed:

Update the requirement.
Update the affected tests.
Then update production code.
11. Validation

Never declare a feature complete based only on code inspection.

At minimum, validate:

dotnet build
dotnet test

When applicable also run:

dotnet format --verify-no-changes

Architecture tests must pass.

A feature is complete only when validation succeeds.

12. Scope Control

Work on one feature at a time.

Do not:

refactor unrelated code
rename unrelated classes
modify unrelated tests
introduce unrelated dependencies
implement future requirements

If a discovered problem is outside the current feature:

Document it.
Do not silently expand the scope.
Continue with the current requirement if possible.
13. Database

The application uses PostgreSQL.

Persistence belongs to Infrastructure.

Domain entities must not depend on Entity Framework Core attributes.

Avoid leaking persistence concerns into the Domain model.

14. Error Handling

Errors must represent meaningful business or application conditions.

Do not use exceptions as normal control flow.

Do not catch exceptions unless the code can meaningfully handle them.

Do not silently swallow exceptions.

15. Logging

Logging belongs to infrastructure/application boundaries.

Do not add logging everywhere by default.

Log meaningful operational information.

Never log:

passwords
authentication tokens
secrets
sensitive personal data
16. Security

Never hardcode:

passwords
API keys
database credentials
tokens
secrets

Do not commit secrets to Git.

Validate external input at application boundaries.

17. Dependencies

Do not add a NuGet package unless it provides concrete value for the current requirement.

Before adding a dependency:

Determine whether the framework already provides the functionality.
Determine whether the requirement genuinely needs the dependency.
Keep the dependency limited to the appropriate layer.
18. Git Discipline

Changes must be focused.

Do not modify files unrelated to the current feature.

Do not rewrite Git history unless explicitly requested.

Do not commit generated artifacts.

Commit messages should describe the change.

Examples:

feat: add profile matching
test: add reciprocal like tests
refactor: simplify match creation
fix: prevent duplicate likes
19. Agent Behavior

The agent must reason about the existing code before modifying it.

Before implementing:

Read the requirement.
Inspect the relevant code.
Identify affected layers.
Identify existing tests.
Identify architectural constraints.

Do not immediately start writing code.

20. Completion Criteria

Never report:

Done

only because implementation was written.

A feature is complete only when:

Requirement satisfied
        AND
Tests pass
        AND
Build passes
        AND
Architecture rules pass
        AND
No unrelated changes were introduced
21. When Tests Fail

When tests fail:

Read the failure.
Identify the failing behavior.
Determine whether the problem is in production code.
Fix the production code.
Run the tests again.

Do not modify tests simply to make them pass.

22. When Architecture Tests Fail

Architecture violations are blocking failures.

Do not bypass them.

Do not:

remove the architecture test
weaken the rule
add exclusions without justification
move code to another namespace to hide the violation

Fix the dependency direction.

23. Implementation Philosophy

Prefer:

Simple
Explicit
Testable
Small
Focused
Maintainable

Avoid:

Clever
Generic
Speculative
Over-engineered
Highly coupled

The simplest correct implementation is preferred.

24. Agent Output

When reporting work, provide:

What was changed.
What tests were added or modified.
What validation was executed.
Validation results.
Any remaining issues.

Never claim that a command passed if it was not actually executed.


Guarda el archivo.

---

# 3.3. Ahora vamos a leerlo como lo haría el agente

Ejecuta:

```bash
cat AGENTS.md
```

No necesitamos modificarlo todavía.

3.4. Haz una comprobación importante

Quiero que Git nos muestre exactamente qué hemos agregado:

git status

Deberías tener algo parecido a:

Untracked files:
    AGENTS.md
3.5. Ejecuta nuevamente la validación

Aunque solamente hemos agregado documentación, ejecutemos:

dotnet build

y:

dotnet test

Los dos tienen que continuar pasando.

3.6. Ahora revisemos una cosa que será fundamental para TDP

Tenemos tres niveles de reglas:

                  AGENTS.md
                      │
              "qué debe hacer"
                      │
                      ▼
             Architecture Tests
                      │
              "qué está prohibido"
                      │
                      ▼
                Unit Tests
                      │
               "qué debe funcionar"

Esto es exactamente la estructura que queremos para nuestro sistema agentico.

AGENTS.md

Le dice al agente:

No hagas esto.

Architecture Tests

Le dicen automáticamente:

Has violado una regla.

Unit/Integration Tests

Le dicen:

El comportamiento no funciona.

Por eso más adelante nuestro Validator podrá tomar decisiones basándose en evidencia real.

3.7. Pero todavía falta una pieza

Hay algo que deliberadamente NO hemos puesto todavía:

"maximum 3 iterations"

No lo pondremos aquí como mecanismo de control.

¿Por qué?

Porque AGENTS.md describe cómo debe trabajar el agente, pero no debe ser responsable de controlar el flujo de ejecución.

El límite:

iteration <= 3

lo implementaremos en el orquestador del paso 7.

Así tendremos:

AGENTS.md
     │
     │ reglas
     ▼
Agents
     │
     ▼
Orchestrator
     │
     │ max 3
     ▼
Validator

Esto será mucho más robusto.

3.8. Haz el commit

Si:

dotnet build
dotnet test

están correctos:

git add AGENTS.md
git commit -m "docs: define agent development contract"

Después:

git log --oneline -3

Deberías tener:

xxxxxxx docs: define agent development contract
xxxxxxx test: enforce clean architecture boundaries
xxxxxxx chore: initialize Matchly project
✅ Criterios para cerrar el Paso 3

No pasamos al Paso 4 hasta que tengas:

✅ AGENTS.md creado
✅ Clean Architecture definida
✅ Clean Code definido
✅ SOLID definido
✅ TDD definido
✅ TDP definido
✅ Reglas de integridad de tests
✅ Reglas de validación
✅ Reglas de Git
✅ Reglas de seguridad
✅ dotnet build PASS
✅ dotnet test PASS
✅ commit realizado

Y algo importante: no ejecutes OpenCode todavía para modificar el proyecto. En el siguiente paso vamos a preparar el entorno de TDP de forma controlada.

Cuando hayas terminado, dime:

"Paso 3 terminado"

y pasaremos al Paso 4 — crear nuestra primera especificación TDP y convertirla en tests antes de escribir una sola línea de código de producción.


## user


paso 3 terminado


... Continuar desde aca


