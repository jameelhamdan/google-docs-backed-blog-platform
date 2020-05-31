import uuid


def generate_uuid(repeat=1):
    final_uuid = ''
    for i in range(0, repeat):
        final_uuid += uuid.uuid4().hex

    return final_uuid
