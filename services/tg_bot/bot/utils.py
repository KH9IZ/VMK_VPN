def generate_share_link(uuid: str, host: str):
    return (
        f'vless://{uuid}@{host}:443?' 
        'encryption=none&'
        'type=tcp&'
        'security=reality&'
        'flow=xtls-rprx-vision&'
        'headerType=none&'
        'fp=chrome&'
        'sni=localhost&'
        'pbk=qQ0UFS_alnlT-l74Rtz4LPvI9UpkbFJ8TrMSNYmi9RQ&'
        'sid=6893e38f461f8aa6'
        '#ChaussVPN'
    )
