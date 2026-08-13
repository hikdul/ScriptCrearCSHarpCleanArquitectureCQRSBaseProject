Feature: Profile Discovery

Objective
---------
A user can discover profiles that are eligible to be liked.

Rules
-----
- A user must not discover themselves.
- A user must not discover a profile they have already liked.
- A user must be able to discover an eligible profile.
- Existing matches must not be returned as available profiles.
- The behavior belongs to the Domain layer.
- No persistence is introduced.

Out of scope
------------
- Database queries
- Pagination
- Location filtering
- Recommendations
- Authentication
- HTTP
- Application layer
- Infrastructure
