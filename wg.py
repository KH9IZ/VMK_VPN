"""Creating wireguard configuration."""

import logging
from ipaddress import IPv4Address, ip_network
import os.path
from random import choice
import subprocess

logger = logging.getLogger("WireGuard")

used_ips: set[IPv4Address] = {
    IPv4Address('10.0.0.1'),
    IPv4Address('10.0.0.2')
}

def get_peer_config(user_id):
    """
    Return user config by user_id.

    :param user_id: unique identifuer of user
    :return: path to user config
    :rtype: str
    """
    wgc = WireGuardConfig(str(user_id))
    if not wgc.exists():
        wgc.create()
    return wgc


class WireGuardConfig:
    """Manage config files."""

    __client_publickey: str
    __client_name: str
    __selected_ip: IPv4Address

    MASK_BITS: int = 24
    SERVER_ADRESS: str = '45.142.215.232'
    HOSTS_NET: str = '10.0.0.0'
    DNS_SERVER: str = '8.8.8.8'
    SERVER_PORT: int = 51820
    CONFIGS_PATH: str = '/etc/wireguard/clients'
    SERVER_PUBLIC_KEY_PATH: str = '/etc/wireguard/server/server.key.pub'

    def __init__(self, client_name: str):
        """Select unused ip and init inner fields."""
        self.__client_name = client_name
        if self.exists():
            self.__parse_config()
            return
        available_ips = set(ip_network(self.HOSTS_NET + '/' + str(self.MASK_BITS)).hosts()) - used_ips
        if len(available_ips) > 0:
            self.__selected_ip = choice(tuple(available_ips))
        else:
            self.__selected_ip = None

    def exists(self) -> bool:
        """Check that user config file exists."""
        return os.path.isfile(self.get())

    def get(self) -> str:
        """Return path to config file."""
        return self.CONFIGS_PATH + '/' + self.__client_name + '.conf'

    def address(self) -> IPv4Address:
        """Return selected address."""
        return self.__selected_ip

    def get_publickey(self) -> str:
        """Return created user public key."""
        return self.__client_publickey

    def create(self):
        """Create new config file for user.

        Return tuple where first value is the proccess success,
        but the second is the error message.
        """
        if self.__selected_ip is None:
            raise ValueError("No available ip for client!")
        try:
            privkey, pubkey = self.__generate_keys()
            logger.info(f"{privkey=} , {pubkey=}")
            with open(self.SERVER_PUBLIC_KEY_PATH, 'r') as serv_pubkey_file:
                self.__fill_out_config(privkey, serv_pubkey_file.read())
            self.__add_client_key_to_server(pubkey)
            used_ips.add(self.address())
        except subprocess.CalledProcessError as exs:
            raise ValueError("Cannot create user config.") from exs

    def __fill_out_config(self, client_private: str, server_public: str):
        """Fill config file for client."""
        with open(self.get(), 'w', encoding='utf-8') as config:
            config.write(f"""[Interface]
PrivateKey = {client_private}
Address = {format(self.__selected_ip)}
DNS = {self.DNS_SERVER}

[Peer]
PublicKey = {server_public}
Endpoint = {self.SERVER_ADRESS}:{self.SERVER_PORT}
AllowedIPs = 0.0.0.0/0 """)

    def  __parse_config(self):
        with open(self.get(), 'r') as cfg:
            for line in cfg:
                if line.startswith("Address"):
                    self.__selected_ip = IPv4Address(line.rpartition('=')[-1].strip())
                    return

    def __generate_keys(self) -> tuple[str]:
        """Run bash scripts to generate keys."""
        privkey_proc = subprocess.run(["wg", "genkey"], capture_output=True, check=True)
        privkey = privkey_proc.stdout.strip()
        pubkey_proc = subprocess.run(["wg", "pubkey"], input=privkey,
                                     capture_output=True, check=True)
        pubkey = pubkey_proc.stdout.strip()
        return privkey.decode(), pubkey.decode()

    def __add_client_key_to_server(self, client_public: str):
        """Add clients public key and IP address to the server."""
        err, msg = subprocess.getstatusoutput(f"sudo wg set wg0 peer {client_public}"
                                              f"allowed-ips {format(self.__selected_ip)}")
        if err:
            raise ValueError("Can not add client ip to server!" + msg)
        else:
            logger.info("Added user public key to server: %s %s", self.__client_name, client_public)

    @staticmethod
    def remove(client_public: str):
        """Remove client public key from the server."""
        err, msg = subprocess.getstatusoutput(f"sudo wg set wg0 peer {client_public} remove")
        if err:
            raise ValueError("Can not remove client from server!" + msg)
        else:
            logger.info("Remove user public key from server: %s", client_public)