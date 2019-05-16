from abc import ABC, abstractmethod
from ..utils import open_close_wallet


class BaseWallet(ABC):
    masterSecretIDRecordType = "masterSecretID"

    def __init__(self, wallet_config, wallet_credentials):
        pass

    @open_close_wallet
    @abstractmethod
    async def listDIDs(self, wallet_handle=None):
        pass

    @open_close_wallet
    @abstractmethod
    async def listPairwiseDIDs(self, wallet_handle=None):
        pass

    @open_close_wallet
    @abstractmethod
    async def getPairwiseInfo(self, their_did, wallet_handle=None):
        pass

    @open_close_wallet
    @abstractmethod
    async def store_did_and_create_pairwise(self, didkey, name, wallet_handle=None):
        pass

    @open_close_wallet
    @abstractmethod
    async def didfromseed(self, seed, wallet_handle=None):
        pass

    @open_close_wallet
    @abstractmethod
    async def verkeyfromseed(self, seed, wallet_handle=None):
        pass

    @open_close_wallet
    @abstractmethod
    async def get_wallet_records(self, record_type, query_json, wallet_handle=None):
        pass

    @abstractmethod
    async def create_pairwise_DID(
        self, wallet_handle, destination_did, destinationName
    ):
        pass

    @abstractmethod
    async def getwalletdid(self, wallet_handle):
        pass

    @abstractmethod
    async def getwalletverkey(self, wallet_handle):
        pass

    @abstractmethod
    async def get_master_secret_id(self, wallet_handle):
        pass

    @abstractmethod
    async def _get_wallet_records(self, wallet_handle, record_type, query_json):
        pass

    @abstractmethod
    async def store_wallet_record(
        self, wallet_handle, record_type, record_value, record_tags=None
    ):
        pass

    @abstractmethod
    async def storeDID(self, wallet_handle, didkey, verkey, name):
        pass

    # @open_close_wallet
    # async def storeDID(self, didkey, name, verkey="", wallet_handle=None):
    #     try:
    #         idjson = json.dumps({"did": didkey})
    #         metadata = json.dumps({"Name": name})
    #         await did.store_their_did(wallet_handle, idjson)
    #         await did.set_did_metadata(wallet_handle, didkey, metadata)
    #     except IndyError:
    #         log.exception("Error occured while storing DID")
    #     except Exception:
    #         log.exception("Error occured while storing DID")

    @abstractmethod
    async def _generate_DID(self, wallet_handle, seed=None, name=None):
        pass

    @abstractmethod
    async def _create_master_secret(self, wallet_handle):
        pass
