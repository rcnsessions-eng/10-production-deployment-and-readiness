import asyncio
import os
import sys
import uuid

import httpx


async def main() -> None:
    expected = int(sys.argv[1])
    issuer = os.environ["LEARNING_IDP_URL"]
    async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
        user = await client.post(
            issuer + "/protocol/openid-connect/token",
            data={
                "grant_type": "password",
                "client_id": "learning-client",
                "username": "learner-red-1",
                "password": os.environ["LEARNING_DEMO_PASSWORD"],
            },
        )
        workload = await client.post(
            issuer + "/protocol/openid-connect/token",
            data={
                "grant_type": "client_credentials",
                "client_id": "agent-adapter",
                "client_secret": os.environ["LEARNING_AGENT_SECRET"],
            },
        )
        assert user.status_code == workload.status_code == 200
        headers = {
            "Authorization": "Bearer " + user.json()["access_token"],
            "X-Workload-Authorization": "Bearer " + workload.json()["access_token"],
        }
        response = await client.post(
            os.environ["LEARNING_GATEWAY_URL"] + "/v1/delegated/tools/evidence.record",
            headers=headers,
            json={
                "args": {
                    "course_id": "course-red",
                    "kind": "content_read",
                    "idempotency_key": "readiness-" + uuid.uuid4().hex,
                }
            },
        )
        assert response.status_code == expected, "Unexpected protected write outcome"
        if expected == 503:
            assert "id" not in response.json(), "Denied write returned a receipt"
        else:
            assert response.json().get("id"), "Authorized write returned no receipt"
        print("Protected write outcome verified: " + str(expected))


if __name__ == "__main__":
    asyncio.run(main())
