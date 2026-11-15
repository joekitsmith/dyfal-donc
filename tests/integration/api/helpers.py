from fastapi.testclient import TestClient

from tests.integration.api.conftest import ORIGIN
from tests.support.authenticator import SoftwareAuthenticator


def start_guest(client: TestClient) -> dict[str, object]:
    response = client.post("/auth/guest")
    assert response.status_code == 200
    body: dict[str, object] = response.json()
    return body


def register_passkey_response(
    client: TestClient, authenticator: SoftwareAuthenticator, label: str | None = None
) -> dict[str, object]:
    """Add a passkey to whoever the browser is signed in as, and return everything the server said."""
    options = client.post("/auth/passkeys/registration/options")
    assert options.status_code == 200
    credential = authenticator.register(options.json(), ORIGIN)
    body: dict[str, object] = {"credential": credential}
    if label is not None:
        body["label"] = label

    response = client.post("/auth/passkeys/registration/verify", json=body)
    assert response.status_code == 201, response.text
    result: dict[str, object] = response.json()
    return result


def register_passkey(
    client: TestClient, authenticator: SoftwareAuthenticator, label: str | None = None
) -> dict[str, object]:
    """Add a passkey, and return it."""
    passkey = register_passkey_response(client, authenticator, label)["passkey"]
    assert isinstance(passkey, dict)
    return passkey


def recovery_codes_after_saving(
    client: TestClient, authenticator: SoftwareAuthenticator
) -> list[str]:
    """Start as a guest and add the first passkey, which is when the recovery codes are shown."""
    start_guest(client)
    codes = register_passkey_response(client, authenticator)["recovery_codes"]
    assert isinstance(codes, list)
    return [str(code) for code in codes]


def sign_in(
    client: TestClient, authenticator: SoftwareAuthenticator
) -> dict[str, object]:
    options = client.post("/auth/passkeys/authentication/options")
    assert options.status_code == 200
    credential = authenticator.sign_in(options.json(), ORIGIN)

    response = client.post(
        "/auth/passkeys/authentication/verify", json={"credential": credential}
    )
    assert response.status_code == 200, response.text
    body: dict[str, object] = response.json()
    return body


def offer(client: TestClient) -> dict[str, object]:
    response = client.post("/me/next")
    assert response.status_code == 200
    body: dict[str, object] = response.json()
    return body


def answer(
    client: TestClient, selection_id: object, outcome: str = "got_it"
) -> dict[str, object]:
    response = client.post(
        "/me/outcomes", json={"selection_id": selection_id, "outcome": outcome}
    )
    assert response.status_code == 200
    body: dict[str, object] = response.json()
    return body


def progress(client: TestClient) -> dict[str, float]:
    response = client.get("/me/progress")
    assert response.status_code == 200
    body: dict[str, float] = response.json()
    return body
