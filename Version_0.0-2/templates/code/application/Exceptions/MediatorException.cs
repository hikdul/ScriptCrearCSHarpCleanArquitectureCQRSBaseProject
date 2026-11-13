namespace {{ProjectName}}.Application.Exceptions;

/// <summary>
/// Raised when a request cannot be dispatched to exactly one handler:
/// no handler is registered, or more than one matches.
/// </summary>
public class MediatorException : Exception
{
    public MediatorException(string message)
        : base(message) { }
}
