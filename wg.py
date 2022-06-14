def get_peer_config(user_id):
    try:
        f = open(str(user_id) + '.conf', 'rb')
        return f
    except:    
        return None