namespace {{PROJECT_NAME}}.Domain;

/// <summary>
/// The one way a new entity identifier is produced.
/// <para>
/// Every identifier is a UUID version 7 (RFC 9562): the leading bits carry a
/// millisecond timestamp, so identifiers created later sort after identifiers
/// created earlier. That ordering is useful for keys and audit trails, and it is
/// the rule this repository follows for every entity. Non-entity values — a JWT
/// <c>jti</c>, a test fixture id — are not covered by it and may use
/// <see cref="Guid.NewGuid"/>.
/// </para>
/// </summary>
public static class EntityId
{
	/// <summary>Creates a new UUID version 7 identifier.</summary>
	public static Guid New() => Guid.CreateVersion7();
}
