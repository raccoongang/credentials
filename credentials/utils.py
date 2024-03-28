def keypath(payload, keys_path):
    keys = keys_path.split('.')
    current = payload

    def traverse(current, keys):
        if not keys:
            return current
        key = keys[0]
        if isinstance(current, dict) and key in current:
            return traverse(current[key], keys[1:])
        else:
            return None
    
    return traverse(current, keys)