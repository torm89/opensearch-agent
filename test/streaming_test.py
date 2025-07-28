import requests

if __name__ == '__main__':
    response = requests.post(
        'http://localhost:8080/invocations',
        stream=True,
        json={
            "input": {
                "question": "What is the capital of France?"
            }
        }
    )
    # response = requests.post(
    #     'http://localhost:3000/api/chat/edge',
    #     stream=True,
    #     json={
    #         "messages": ["What is the name of the first ship to circumnavigate the globe?"]
    #     }
    # )
    print(response.status_code)

    for chunk in response.iter_lines(decode_unicode=True):
        print(chunk)
