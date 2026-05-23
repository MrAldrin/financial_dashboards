import sys
import requests
import json
import os

def execute(url, token, code, session_id=None):
    base_url = url.rstrip('/')
    headers = {
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if not session_id:
        resp = requests.get(f"{base_url}/api/sessions", headers=headers)
        resp.raise_for_status()
        sessions = resp.json()
        if not sessions:
            print("No active sessions", file=sys.stderr)
            sys.exit(1)
        if len(sessions) > 1:
            print(f"Multiple sessions: {list(sessions.keys())}", file=sys.stderr)
            # Pick the first one for now or match by filename if possible
            session_id = list(sessions.keys())[0]
        else:
            session_id = list(sessions.keys())[0]
    
    headers["Marimo-Session-Id"] = session_id
    
    # Use stream=True to handle SSE if we wanted to stream stdout/stderr
    # But for a simple execution, we can just wait for the end or parse the stream
    with requests.post(f"{base_url}/api/kernel/execute", headers=headers, json={"code": code}, stream=True) as r:
        r.raise_for_status()
        current_event = None
        for line in r.iter_lines():
            if not line:
                continue
            line = line.decode('utf-8')
            if line.startswith('event:'):
                current_event = line[len('event: '):]
            elif line.startswith('data:'):
                payload = json.loads(line[len('data: '):])
                if current_event == 'stdout':
                    sys.stdout.write(payload.get('data', ''))
                    sys.stdout.flush()
                elif current_event == 'stderr':
                    sys.stderr.write(payload.get('data', ''))
                    sys.stderr.flush()
                elif current_event == 'done':
                    if not payload.get('success', True):
                        print(payload.get('error', {}).get('msg', 'Unknown error'), file=sys.stderr)
                        sys.exit(1)
                    output = payload.get('output', {}).get('data', '')
                    if output:
                        print(output)
                    return

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--token")
    parser.add_argument("--session")
    parser.add_argument("-c", "--code")
    args = parser.parse_args()
    
    code = args.code
    if not code:
        code = sys.stdin.read()
    
    execute(args.url, args.token or os.environ.get("MARIMO_TOKEN"), code, args.session)
