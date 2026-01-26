import requests
import time

def safe_get(
        url: str, session: requests.Session, 
        retries: int = 3, wait: int = 3) -> (requests.Response | None):
    """
    Safely perform an HTTP GET request with retries and exponential backoff.

    This function attempts to fetch the given URL using a provided
    requests.Session. Transient network errors (timeouts, connection errors)
    are retried with exponential backoff. Non-recoverable request errors
    cause the request to be skipped.

    Args:
        url (str): The URL to request.
        session (requests.Session): An active requests session to reuse
            connections and headers.
        retries (int): Number of retry attempts for transient errors.
        wait (int): Base wait time in seconds for exponential backoff.

    Returns:
        (requests.Response | None):
            The response object if the request succeeds, otherwise None
            if all retries fail or a non-recoverable error occurs.
    """

    for attempt in range(retries):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            time.sleep(wait * 2**attempt)

        except requests.exceptions.RequestException as e:
            return None

    return None