import requests


def request_plan(domain, instance):
    data = {'domain': domain,
            'problem': instance}

    resp = requests.post('http://solver.planning.domains/solve',
                         verify=False, json=data).json()

    return resp
